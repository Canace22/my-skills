#!/usr/bin/env python3
"""Find self-made skills in local AI agents and copy them into this repository."""

from __future__ import annotations

import argparse
import codecs
import difflib
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

HOME = Path.home()

# Agent id -> skill roots. Roots that do not exist are skipped silently.
SOURCES: dict[str, list[Path]] = {
    "claude": [HOME / ".claude/skills"],
    "codex": [HOME / ".codex/skills"],
    "cursor": [HOME / ".cursor/skills"],
    "hermes": [HOME / ".hermes/skills"],
    "agents": [HOME / ".agents/skills"],
    "gemini": [HOME / ".gemini/skills"],
    "opencode": [HOME / ".config/opencode/skills", HOME / ".config/opencode/skill"],
    "openclaw": [HOME / ".openclaw/skills"],
    "copilot": [HOME / ".copilot/skills"],
    "codebuddy": [HOME / ".codebuddy/skills"],
    "trae": [HOME / ".trae/skills"],
    "windsurf": [HOME / ".codeium/windsurf/skills"],
}
# claude.ai skills synced into Claude Code; only source "plugin" is user-uploaded.
CLAUDE_SYNCED = HOME / ".claude/skills/synced"

JUNK_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".idea", ".vscode",
}
JUNK_FILES = {".DS_Store", "Thumbs.db"}
JUNK_SUFFIXES = {".pyc", ".pyo"}
LICENSE_NAMES = {"LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE"}
ALLOWED_FRONTMATTER = {"name", "description"}
MAX_DEPTH = 4
# Per-repo record of which local copy each skill was synced from, so a copy that was
# imported and then cleaned up in the repo does not keep showing as changed.
RECORD_FILE = Path("sync-local-skills/synced.json")
LARGE_FILE = 1024 * 1024

SECRET_PATTERNS = [
    ("OpenAI/Anthropic style key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("credential assignment", re.compile(
        r"(?i)\b(api[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*['\"][A-Za-z0-9_\-/+=.]{12,}['\"]")),
    ("env-style credential", re.compile(
        r"^\s*(export\s+)?[A-Z0-9_]*(KEY|SECRET|TOKEN|PASSWORD)\s*=\s*[^\s$'\"{(][^\s]{11,}")),
    ("email address", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
]
LOCAL_PATH_RE = re.compile(r"(/Users/[^/\s]+|/home/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+|~/(Desktop|Documents|Downloads)\b)")


@dataclass
class Copy:
    agent: str
    path: Path
    real: Path
    name: str
    description: str
    files: dict[str, str]
    mtime: float
    third_party: str = ""
    linked: bool = False

    @property
    def digest(self) -> str:
        h = hashlib.sha256()
        for rel, sha in sorted(self.files.items()):
            h.update(f"{rel}\0{sha}\n".encode())
        return h.hexdigest()


@dataclass
class Group:
    name: str
    copies: list[Copy] = field(default_factory=list)
    status: str = ""


def short(path: Path) -> str:
    text = str(path)
    home = str(HOME)
    return "~" + text[len(home):] if text.startswith(home) else text


def day(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else "-"


def is_junk(rel: Path) -> bool:
    if any(part in JUNK_DIRS for part in rel.parts[:-1]):
        return True
    return rel.name in JUNK_FILES or rel.suffix in JUNK_SUFFIXES


def list_files(root: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=True):
        dirnames[:] = sorted(d for d in dirnames if d not in JUNK_DIRS)
        for fname in sorted(filenames):
            full = Path(dirpath) / fname
            rel = full.relative_to(root)
            if not is_junk(rel) and full.is_file():
                found[rel.as_posix()] = full
    return found


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    meta: dict[str, str] = {}
    key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            meta[key] = "" if value in {">", "|", ">-", "|-"} else value.strip("'\"")
        elif key and line.startswith((" ", "\t")):
            meta[key] = (meta[key] + " " + line.strip()).strip()
    return meta


def read_meta(skill_dir: Path) -> dict[str, str]:
    try:
        return parse_frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return {}


def skill_name(skill_dir: Path, meta: dict[str, str]) -> str:
    name = meta.get("name", "")
    return name if re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) else skill_dir.name


def find_skill_dirs(root: Path, skip: set[str]) -> list[Path]:
    """Directories containing SKILL.md, without descending into a skill."""
    result: list[Path] = []

    def walk(directory: Path, depth: int) -> None:
        if (directory / "SKILL.md").is_file() and directory != root:
            result.append(directory)
            return
        if depth >= MAX_DEPTH:
            return
        try:
            children = sorted(directory.iterdir())
        except OSError:
            return
        for child in children:
            if child.name.startswith(".") or child.name in JUNK_DIRS or child.name in skip:
                continue
            if child.is_dir():
                walk(child, depth + 1)

    walk(root, 0)
    return result


def hermes_skip(root: Path) -> tuple[set[str], set[Path]]:
    """Names shipped with Hermes (bundled or optional) and paths installed from its hub."""
    names: set[str] = set()
    paths: set[Path] = set()
    for shipped in ("skills", "optional-skills"):
        shipped_root = root.parent / "hermes-agent" / shipped
        if shipped_root.is_dir():
            names.update(d.name for d in find_skill_dirs(shipped_root, set()))
    manifest = root / ".bundled_manifest"
    if manifest.is_file():
        for line in manifest.read_text(encoding="utf-8", errors="ignore").splitlines():
            if ":" in line:
                names.add(line.split(":", 1)[0].strip())
    lock = root / ".hub/lock.json"
    if lock.is_file():
        try:
            installed = json.loads(lock.read_text(encoding="utf-8")).get("installed", {})
        except (OSError, json.JSONDecodeError):
            installed = {}
        for entry_name, entry in installed.items():
            names.add(entry_name)
            if entry.get("install_path"):
                paths.add((root / entry["install_path"]).resolve())
    return names, paths


def claude_synced_dirs() -> tuple[list[Path], int]:
    keep: list[Path] = []
    skipped = 0
    if not CLAUDE_SYNCED.is_dir():
        return keep, skipped
    for bucket in sorted(CLAUDE_SYNCED.iterdir()):
        manifest = bucket / "manifest.json"
        if not manifest.is_file():
            continue
        try:
            entries = json.loads(manifest.read_text(encoding="utf-8")).get("skills", [])
        except (OSError, json.JSONDecodeError):
            continue
        for entry in entries:
            directory = bucket / entry.get("name", "")
            if not (directory / "SKILL.md").is_file():
                continue
            if entry.get("source") == "plugin":
                keep.append(directory)
            else:
                skipped += 1
    return keep, skipped


def make_copy(agent: str, path: Path, repo: Path) -> Copy:
    real = path.resolve()
    meta = read_meta(real)
    files = list_files(real)
    hashes = {rel: sha_file(full) for rel, full in files.items()}
    mtime = max((full.stat().st_mtime for full in files.values()), default=0.0)
    license_file = next((n for n in LICENSE_NAMES if (real / n).is_file()), "")
    if not license_file and meta.get("license"):
        license_file = "license in frontmatter"
    return Copy(
        agent=agent,
        path=path,
        real=real,
        name=skill_name(real, meta),
        description=meta.get("description", ""),
        files=hashes,
        mtime=mtime,
        third_party=f"has {license_file}" if license_file else "",
        linked=real == repo or repo in real.parents,
    )


def scan(repo: Path, extra: list[tuple[str, Path]]) -> tuple[list[Copy], dict[str, int], list[str]]:
    copies: list[Copy] = []
    skipped: dict[str, int] = {}
    broken: list[str] = []
    sources = [(agent, root) for agent, roots in SOURCES.items() for root in roots]
    sources += extra
    for agent, root in sources:
        if not root.is_dir():
            continue
        skip_names: set[str] = set()
        skip_paths: set[Path] = set()
        if agent == "hermes":
            skip_names, skip_paths = hermes_skip(root)
        skip_dirs = {"synced"} if agent == "claude" else set()
        broken += [f"{agent} {short(link)} -> {os.readlink(link)}"
                   for link in sorted(root.iterdir()) if link.is_symlink() and not link.exists()]
        for directory in find_skill_dirs(root, skip_dirs):
            real = directory.resolve()
            if agent == "hermes":
                name = skill_name(real, read_meta(real))
                if name in skip_names or directory.name in skip_names or real in skip_paths:
                    skipped[agent] = skipped.get(agent, 0) + 1
                    continue
            copies.append(make_copy(agent, directory, repo))
    synced, official = claude_synced_dirs()
    if official:
        skipped["claude.ai"] = official
    copies += [make_copy("claude.ai", d, repo) for d in synced]
    return copies, skipped, broken


def load_record(repo: Path) -> dict[str, list[dict[str, str]]]:
    try:
        return json.loads((repo / RECORD_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_record(repo: Path, record: dict[str, list[dict[str, str]]]) -> None:
    path = repo / RECORD_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def record_path(copy: Copy) -> str:
    """Display path for the record; hides the claude.ai account bucket id since the record is committed."""
    if CLAUDE_SYNCED in copy.path.parents:
        return short(CLAUDE_SYNCED / "<account>" / copy.path.name)
    return short(copy.path)


def remember(record: dict[str, list[dict[str, str]]], name: str, copy: Copy) -> None:
    """Record copy as synced, replacing any earlier entry for the same location."""
    entries = [e for e in record.get(name, []) if e.get("path") != record_path(copy)]
    entries.append({
        "agent": copy.agent,
        "path": record_path(copy),
        "digest": copy.digest,
        "date": datetime.now().strftime("%Y-%m-%d"),
    })
    record[name] = sorted(entries, key=lambda e: e["path"])


def recorded(record: dict[str, list[dict[str, str]]], copy: Copy) -> dict[str, str] | None:
    return next((e for e in record.get(copy.name, []) if e.get("digest") == copy.digest), None)


def repo_skill(repo: Path, name: str) -> Path | None:
    candidate = repo / name
    return candidate if (candidate / "SKILL.md").is_file() else None


def repo_hashes(repo_dir: Path) -> dict[str, str]:
    return {rel: sha_file(full) for rel, full in list_files(repo_dir).items()}


def copy_status(copy: Copy, repo: Path, record: dict[str, list[dict[str, str]]]) -> str:
    if copy.linked:
        return "linked"
    target = repo_skill(repo, copy.name)
    if target is None:
        return "new"
    existing = repo_hashes(target)
    if all(existing.get(rel) == sha for rel, sha in copy.files.items()):
        return "same"
    return "recorded" if recorded(record, copy) else "changed"


def build_groups(copies: list[Copy], repo: Path, record: dict[str, list[dict[str, str]]]) -> list[Group]:
    groups: dict[str, Group] = {}
    seen: set[tuple[str, Path]] = set()
    for copy in copies:
        key = (copy.agent, copy.real)
        if key in seen:
            continue
        seen.add(key)
        groups.setdefault(copy.name, Group(copy.name)).copies.append(copy)
    for group in groups.values():
        statuses = {copy_status(c, repo, record) for c in group.copies}
        if "new" in statuses:
            group.status = "new"
        elif "changed" in statuses:
            group.status = "changed"
        else:
            group.status = "synced"
        group.copies.sort(key=lambda c: c.mtime, reverse=True)
    return sorted(groups.values(), key=lambda g: g.name)


def describe_copies(group: Group, repo: Path, record: dict[str, list[dict[str, str]]]) -> list[str]:
    lines: list[str] = []
    variants: dict[str, list[Copy]] = {}
    for copy in group.copies:
        variants.setdefault(copy.digest, []).append(copy)
    target = repo_skill(repo, group.name)
    repo_mtime = max((p.stat().st_mtime for p in list_files(target).values()), default=0) if target else 0
    for label, same in zip("ABCDEFGHIJ", variants.values()):
        first = same[0]
        status = copy_status(first, repo, record)
        where = ", ".join(f"{c.agent} {short(c.path)}" for c in same)
        notes = [{"linked": "symlink into this repo", "same": "same as repo"}.get(status, "")]
        if status == "changed":
            if record.get(group.name):
                last = max(e["date"] for e in record[group.name])
                notes[0] = f"edited locally since last sync on {last}"
            elif repo_mtime:
                notes[0] = "newer than repo" if first.mtime > repo_mtime else "older than repo"
        if first.third_party:
            notes.append(f"{first.third_party}, maybe third-party")
        note = "; ".join(n for n in notes if n)
        lines.append(f"    [{label}] {day(first.mtime)}  {len(first.files)} files  {where}"
                     + (f"  ({note})" if note else ""))
    return lines


def print_report(groups: list[Group], skipped: dict[str, int], broken: list[str],
                 repo: Path, record: dict[str, list[dict[str, str]]], show_all: bool) -> None:
    sections = [
        ("new", "NEW - not in the repo yet"),
        ("changed", "CHANGED - in the repo, but a local copy differs"),
    ]
    print(f"Repo: {short(repo)}\n")
    for status, title in sections:
        chosen = [g for g in groups if g.status == status]
        own = [g for g in chosen if show_all or not all(c.third_party for c in g.copies)]
        maybe = [g for g in chosen if g not in own]
        print(f"{title}: {len(chosen)}")
        for group in own:
            desc = group.copies[0].description
            print(f"  {group.name}" + (f" - {desc[:90]}" if desc else ""))
            for line in describe_copies(group, repo, record):
                print(line)
        if maybe:
            names = ", ".join(g.name for g in maybe)
            print(f"  (hidden, every copy declares a license so likely installed from elsewhere: {names};"
                  " use --all to show)")
        print()
    synced = [g.name for g in groups if g.status == "synced"]
    print(f"IN SYNC (same as repo, linked, or unchanged since last sync): {len(synced)}"
          + (f" - {', '.join(synced)}" if synced else ""))
    if skipped:
        parts = ", ".join(f"{agent} {count}" for agent, count in sorted(skipped.items()))
        print(f"SKIPPED built-in / official / store-installed: {parts}")
    if broken:
        print("BROKEN LINKS (target is gone; ask the user where the skill went):")
        for line in broken:
            print(f"  {line}")


def pick_copy(group: Group, choice: str | None) -> Copy:
    candidates = [c for c in group.copies if not c.linked] or group.copies
    if choice:
        path = Path(choice).expanduser()
        matched = [c for c in candidates if c.agent == choice or c.path == path or c.real == path.resolve()]
        if not matched:
            options = ", ".join(sorted({c.agent for c in candidates}))
            raise SystemExit(f"{group.name}: no copy from {choice!r}. Available: {options}")
        candidates = matched
    if len({c.digest for c in candidates}) > 1:
        lines = "\n".join(f"  --from {c.agent}  ({short(c.path)}, {day(c.mtime)})" for c in candidates)
        raise SystemExit(f"{group.name}: local copies differ; pick one with --from (agent or path):\n{lines}")
    return candidates[0]


def find_group(groups: list[Group], name: str) -> Group:
    for group in groups:
        if group.name == name:
            return group
    raise SystemExit(f"{name}: not found in any local agent. Run `scan` to see names.")


def import_skill(group: Group, copy: Copy, repo: Path, overwrite: bool, dry_run: bool) -> Path:
    target = repo / group.name
    if target.exists() and not overwrite:
        raise SystemExit(f"{group.name}: {short(target)} already exists. "
                         "Review with `diff`, then re-run with --overwrite.")
    if copy.linked:
        raise SystemExit(f"{group.name}: {short(copy.path)} already points into this repo.")
    source_files = list_files(copy.real)
    existing = set(list_files(target)) if target.exists() else set()
    added = sorted(set(source_files) - existing)
    updated = sorted(rel for rel in set(source_files) & existing
                     if sha_file(source_files[rel]) != sha_file(target / rel))
    kept = sorted(existing - set(source_files))
    verb = "Would import" if dry_run else "Imported"
    print(f"{verb} {group.name} from {copy.agent} {short(copy.path)} -> {short(target)}")
    print(f"  added {len(added)}, updated {len(updated)}, unchanged "
          f"{len(source_files) - len(added) - len(updated)}")
    for rel in added:
        print(f"  + {rel}")
    for rel in updated:
        print(f"  ~ {rel}")
    if kept:
        print("  Only in repo (left untouched; delete by hand if obsolete):")
        for rel in kept:
            print(f"    {rel}")
    if not dry_run:
        for rel in added + updated:
            destination = target / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_files[rel], destination)
    return target


def is_text(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return False
    if b"\0" in chunk:
        return False
    try:
        # Incremental decode so a multibyte character cut at the chunk edge is fine.
        codecs.getincrementaldecoder("utf-8")().decode(chunk, final=False)
    except UnicodeDecodeError:
        return False
    return True


def check_skill(skill_dir: Path) -> int:
    problems: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        problems.append("SKILL.md is missing")
    else:
        meta = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="ignore"))
        if not meta:
            problems.append("SKILL.md has no frontmatter")
        if meta.get("name") != skill_dir.name:
            problems.append(f"frontmatter name {meta.get('name')!r} != directory {skill_dir.name!r}")
        if not meta.get("description"):
            problems.append("frontmatter description is empty")
        extra = sorted(set(meta) - ALLOWED_FRONTMATTER)
        if extra:
            problems.append(f"extra frontmatter keys (repo allows only name, description): {', '.join(extra)}")
    for dirpath, dirnames, filenames in os.walk(skill_dir):
        for d in dirnames:
            if d in JUNK_DIRS:
                problems.append(f"junk directory: {Path(dirpath, d).relative_to(skill_dir)}")
        dirnames[:] = [d for d in dirnames if d not in JUNK_DIRS]
        for fname in filenames:
            full = Path(dirpath, fname)
            rel = full.relative_to(skill_dir)
            if is_junk(rel):
                problems.append(f"junk file: {rel}")
                continue
            if full.stat().st_size > LARGE_FILE:
                problems.append(f"large file ({full.stat().st_size // 1024} KB): {rel}")
            if not is_text(full):
                continue
            for lineno, line in enumerate(full.read_text(encoding="utf-8").splitlines(), 1):
                for label, pattern in SECRET_PATTERNS:
                    match = pattern.search(line)
                    if match:
                        masked = line.replace(match.group(0), match.group(0)[:6] + "***")
                        problems.append(f"possible {label}: {rel}:{lineno}: {masked.strip()[:120]}")
                if LOCAL_PATH_RE.search(line):
                    problems.append(f"machine-specific path: {rel}:{lineno}: {line.strip()[:120]}")
    print(f"check {skill_dir.name}: " + ("OK" if not problems else f"{len(problems)} issue(s)"))
    for problem in problems:
        print(f"  - {problem}")
    return len(problems)


def show_diff(group: Group, copy: Copy, repo: Path, max_lines: int) -> None:
    target = repo_skill(repo, group.name)
    if target is None:
        print(f"{group.name}: not in the repo yet; nothing to compare.")
        return
    left = list_files(target)
    right = list_files(copy.real)
    print(f"--- repo  {short(target)}\n+++ local {copy.agent} {short(copy.path)}")
    for rel in sorted(set(right) - set(left)):
        print(f"only in local: {rel}")
    for rel in sorted(set(left) - set(right)):
        print(f"only in repo: {rel}")
    printed = 0
    for rel in sorted(set(left) & set(right)):
        if sha_file(left[rel]) == sha_file(right[rel]):
            continue
        if not (is_text(left[rel]) and is_text(right[rel])):
            print(f"binary differs: {rel}")
            continue
        diff = difflib.unified_diff(
            left[rel].read_text(encoding="utf-8").splitlines(),
            right[rel].read_text(encoding="utf-8").splitlines(),
            f"repo/{rel}", f"local/{rel}", lineterm="",
        )
        for line in diff:
            if printed >= max_lines:
                print(f"... truncated at {max_lines} lines (use --max-lines)")
                return
            print(line)
            printed += 1


def default_repo() -> Path | None:
    here = Path(__file__).resolve().parents[2]
    if (here / "AGENTS.md").is_file() and (here / "README.md").is_file():
        return here
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, help="skills repository (default: the repo this script lives in)")
    parser.add_argument("--source", action="append", default=[], metavar="AGENT=PATH",
                        help="extra skill root to scan, e.g. work=~/work/proj/.claude/skills")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="list local skills and how they compare with the repo")
    p_scan.add_argument("--all", action="store_true", help="also show skills that look third-party")
    p_scan.add_argument("--json", action="store_true", help="machine-readable output")

    p_diff = sub.add_parser("diff", help="show how a local copy differs from the repo")
    p_diff.add_argument("name")
    p_diff.add_argument("--from", dest="choice", help="agent id or path of the copy to compare")
    p_diff.add_argument("--max-lines", type=int, default=400)

    p_import = sub.add_parser("import", help="copy local skills into the repo")
    p_import.add_argument("names", nargs="+")
    p_import.add_argument("--from", dest="choice", help="agent id or path, when local copies differ")
    p_import.add_argument("--overwrite", action="store_true", help="update a skill already in the repo")
    p_import.add_argument("--dry-run", action="store_true")

    p_mark = sub.add_parser("mark", help="record a local copy as synced without copying it "
                            "(after merging by hand, or to stop listing a copy you chose to skip)")
    p_mark.add_argument("names", nargs="+")
    p_mark.add_argument("--from", dest="choice", help="agent id or path, when local copies differ")

    p_check = sub.add_parser("check", help="lint repo skills for repo conventions and leaked secrets")
    p_check.add_argument("names", nargs="+")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = (args.repo.expanduser() if args.repo else default_repo())
    if repo is None:
        raise SystemExit("Cannot locate the skills repo; pass --repo /path/to/my-skills.")
    repo = repo.resolve()

    if args.command == "check":
        return 1 if sum(check_skill(repo / name) for name in args.names) else 0

    extra: list[tuple[str, Path]] = []
    for item in args.source:
        agent, sep, path = item.partition("=")
        if not sep:
            raise SystemExit(f"--source expects AGENT=PATH, got {item!r}")
        extra.append((agent, Path(path).expanduser()))
    copies, skipped, broken = scan(repo, extra)
    record = load_record(repo)
    groups = build_groups(copies, repo, record)

    if args.command == "scan":
        if args.json:
            data = [{
                "name": g.name,
                "status": g.status,
                "copies": [{
                    "agent": c.agent, "path": str(c.path), "real": str(c.real),
                    "status": copy_status(c, repo, record), "modified": day(c.mtime),
                    "files": len(c.files), "third_party": c.third_party,
                    "digest": c.digest[:12], "description": c.description,
                } for c in g.copies],
            } for g in groups]
            print(json.dumps({"repo": str(repo), "skills": data, "skipped": skipped, "broken": broken},
                             ensure_ascii=False, indent=2))
        else:
            print_report(groups, skipped, broken, repo, record, args.all)
        return 0

    if args.command == "diff":
        group = find_group(groups, args.name)
        show_diff(group, pick_copy(group, args.choice), repo, args.max_lines)
        return 0

    if args.command == "mark":
        for name in args.names:
            group = find_group(groups, name)
            if repo_skill(repo, name) is None:
                raise SystemExit(f"{name}: not in the repo; use `import` instead.")
            copy = pick_copy(group, args.choice)
            remember(record, name, copy)
            print(f"Marked {name}: {copy.agent} {short(copy.path)} counts as synced")
        save_record(repo, record)
        return 0

    issues = 0
    for name in args.names:
        group = find_group(groups, name)
        copy = pick_copy(group, args.choice)
        target = import_skill(group, copy, repo, args.overwrite, args.dry_run)
        if not args.dry_run:
            remember(record, name, copy)
            save_record(repo, record)
            issues += check_skill(target)
        print()
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
