#!/usr/bin/env python3
"""Normalize Markdown exported from WPS collaborative documents."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

HEADING_RE = re.compile(
    r"^(?P<indent>[ \t]*)(?:(?P<number>\d+)\.\s+)?"
    r"(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$"
)
LIST_ITEM_RE = re.compile(r"^\s*(?:[-+*]|\d+\.)\s+")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|(?:\s*:?-{3,}:?\s*\|)+\s*$")
IMAGE_RE = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\("
    r"(?P<url><[^>]+>|[^)\s]+)"
    r"(?:\s+(?P<title>[\"'][^\"']*[\"']))?\)"
)
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
CONTENT_TYPE_EXTENSIONS = {
    "image/avif": ".avif",
    "image/gif": ".gif",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/svg+xml": ".svg",
    "image/webp": ".webp",
}


@dataclass
class CleanStats:
    promoted_headings: int = 0
    converted_image_tables: int = 0
    dropped_images: int = 0
    downloaded_images: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean Markdown exported from WPS collaborative documents."
    )
    parser.add_argument("source", type=Path, help="WPS-exported Markdown file")
    parser.add_argument("-o", "--output", type=Path, help="output file; omit to print")
    parser.add_argument(
        "--force", action="store_true", help="replace an existing output file"
    )
    title_group = parser.add_mutually_exclusive_group()
    title_group.add_argument("--title", help="H1 to add when the export has no H1")
    title_group.add_argument(
        "--no-title", action="store_true", help="do not add a missing H1"
    )
    parser.add_argument(
        "--strip-heading-numbers",
        action="store_true",
        help="remove ordered-list numbers wrapped around WPS headings",
    )
    image_group = parser.add_mutually_exclusive_group()
    image_group.add_argument(
        "--keep-images",
        action="store_true",
        help="keep remote image links instead of removing images",
    )
    image_group.add_argument(
        "--download-images",
        type=Path,
        metavar="DIR",
        help="download remote images and rewrite them to paths under DIR",
    )
    return parser.parse_args()


def strip_indent(line: str, width: int) -> str:
    """Remove at most width columns of WPS container indentation."""
    removed = 0
    index = 0
    while index < len(line) and removed < width and line[index] in " \t":
        removed += 4 if line[index] == "\t" else 1
        index += 1
    return line[index:]


def unwrap_heading_title(title: str) -> str:
    title = title.strip()
    if len(title) >= 4 and title.startswith("**") and title.endswith("**"):
        return title[2:-2].strip()
    return title


def promote_headings(
    lines: list[str], stats: CleanStats, strip_heading_numbers: bool
) -> list[str]:
    """Promote WPS headings out of their synthetic ordered-list containers."""
    result: list[str] = []
    base_indent = 0
    fence_marker: str | None = None

    for line in lines:
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)[0]
            fence_marker = None if fence_marker == marker else marker
            result.append(strip_indent(line, base_indent).rstrip())
            continue

        if fence_marker:
            result.append(strip_indent(line, base_indent).rstrip())
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            number = heading_match.group("number")
            indent = heading_match.group("indent").expandtabs(4)
            marks = heading_match.group("marks")
            title = unwrap_heading_title(heading_match.group("title"))
            if number and not strip_heading_numbers:
                title = f"{number}. {title}"
            base_indent = len(indent) + (3 if number else 0)
            result.append(f"{marks} {title}")
            if number or indent:
                stats.promoted_headings += 1
            continue

        result.append(strip_indent(line, base_indent).rstrip())

    return result


def is_image_only_table_row(line: str) -> tuple[bool, list[str]]:
    images = [match.group(0) for match in IMAGE_RE.finditer(line)]
    if not images or not line.lstrip().startswith("|"):
        return False, []
    residue = IMAGE_RE.sub("", line)
    residue = re.sub(r"<br\s*/?>", "", residue, flags=re.IGNORECASE)
    residue = residue.replace("|", "").strip()
    return not residue, images


def normalize_image_tables(lines: list[str], stats: CleanStats) -> list[str]:
    result: list[str] = []
    skip_separator = False

    for line in lines:
        if skip_separator and TABLE_SEPARATOR_RE.match(line):
            skip_separator = False
            continue
        skip_separator = False

        is_image_row, images = is_image_only_table_row(line)
        if is_image_row:
            result.extend(images)
            stats.converted_image_tables += 1
            skip_separator = True
            continue
        result.append(line)

    return result


def remove_standalone_images(lines: list[str], stats: CleanStats) -> list[str]:
    result: list[str] = []
    for line in lines:
        residue = IMAGE_RE.sub("", line).strip()
        if IMAGE_RE.search(line) and not residue:
            stats.dropped_images += len(list(IMAGE_RE.finditer(line)))
            continue
        result.append(line)
    return result


def normalize_spacing(lines: list[str]) -> list[str]:
    compact: list[str] = []
    for index, line in enumerate(lines):
        if line:
            compact.append(line)
            continue

        previous = compact[-1] if compact else ""
        next_line = next((item for item in lines[index + 1 :] if item), "")
        if not previous or not next_line:
            continue
        if LIST_ITEM_RE.match(previous) and LIST_ITEM_RE.match(next_line):
            continue
        if compact[-1] != "":
            compact.append("")

    result: list[str] = []
    for line in compact:
        is_heading = bool(re.match(r"^#{1,6}\s+", line))
        if is_heading and result and result[-1] != "":
            result.append("")
        result.append(line)
        if is_heading:
            result.append("")

    deduplicated: list[str] = []
    for line in result:
        if line == "" and (not deduplicated or deduplicated[-1] == ""):
            continue
        deduplicated.append(line)
    while deduplicated and deduplicated[-1] == "":
        deduplicated.pop()
    return deduplicated


def has_h1(lines: list[str]) -> bool:
    return any(re.match(r"^#\s+\S", line) for line in lines)


def infer_title(source: Path) -> str:
    title = source.stem
    for suffix in (".clean", "-clean", "_clean"):
        if title.lower().endswith(suffix):
            title = title[: -len(suffix)]
            break
    return title.strip()


def add_missing_title(
    lines: list[str], source: Path, title: str | None, no_title: bool
) -> list[str]:
    if no_title or has_h1(lines):
        return lines
    heading = title.strip() if title else infer_title(source)
    return [f"# {heading}", "", *lines] if heading else lines


def image_extension(url: str, content_type: str | None) -> str:
    normalized_type = (content_type or "").split(";", 1)[0].lower()
    if normalized_type in CONTENT_TYPE_EXTENSIONS:
        return CONTENT_TYPE_EXTENSIONS[normalized_type]
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix if re.fullmatch(r"\.[a-z0-9]{2,5}", suffix) else ".bin"


def download_image(url: str, directory: Path) -> tuple[Path, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read()
        extension = image_extension(url, response.headers.get("Content-Type"))
    digest = hashlib.sha256(payload).hexdigest()[:12]
    destination = directory / f"wps-{digest}{extension}"
    return destination, payload


def localize_images(text: str, output: Path, image_dir: Path, stats: CleanStats) -> str:
    destination_dir = (
        image_dir if image_dir.is_absolute() else output.parent / image_dir
    )
    destination_dir.mkdir(parents=True, exist_ok=True)
    cache: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        raw_url = match.group("url")
        url = raw_url[1:-1] if raw_url.startswith("<") else raw_url
        if not url.startswith(("http://", "https://")):
            return match.group(0)
        if url in cache:
            local_url = cache[url]
        else:
            try:
                destination, payload = download_image(url, destination_dir)
                if not destination.exists():
                    destination.write_bytes(payload)
                local_url = Path(os.path.relpath(destination, output.parent)).as_posix()
                cache[url] = local_url
                stats.downloaded_images += 1
            except (OSError, urllib.error.URLError) as error:
                print(f"warning: could not download {url}: {error}", file=sys.stderr)
                return match.group(0)
        title = f" {match.group('title')}" if match.group("title") else ""
        return f"![{match.group('alt')}]({local_url}{title})"

    return IMAGE_RE.sub(replace, text)


def clean_markdown(
    source_text: str,
    source: Path,
    title: str | None,
    no_title: bool,
    drop_images: bool,
    strip_heading_numbers: bool,
) -> tuple[str, CleanStats]:
    stats = CleanStats()
    lines = source_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = promote_headings(lines, stats, strip_heading_numbers)
    lines = normalize_image_tables(lines, stats)
    if drop_images:
        lines = remove_standalone_images(lines, stats)
    lines = normalize_spacing(lines)
    lines = add_missing_title(lines, source, title, no_title)
    return "\n".join(lines).rstrip() + "\n", stats


def write_output(text: str, output: Path, force: bool) -> None:
    if output.exists() and not force:
        raise FileExistsError(
            f"output already exists: {output}; use --force to replace it"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        source_text = args.source.read_text(encoding="utf-8-sig")
    except OSError as error:
        print(f"error: could not read {args.source}: {error}", file=sys.stderr)
        return 2

    if args.download_images and not args.output:
        print("error: --download-images requires --output", file=sys.stderr)
        return 2

    cleaned, stats = clean_markdown(
        source_text,
        args.source,
        args.title,
        args.no_title,
        not args.keep_images and not args.download_images,
        args.strip_heading_numbers,
    )
    if args.download_images:
        cleaned = localize_images(cleaned, args.output, args.download_images, stats)

    if args.output:
        try:
            write_output(cleaned, args.output, args.force)
        except OSError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(cleaned)

    print(
        "cleaned: "
        f"{stats.promoted_headings} headings, "
        f"{stats.converted_image_tables} image tables, "
        f"{stats.dropped_images} images dropped, "
        f"{stats.downloaded_images} images downloaded",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
