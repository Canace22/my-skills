#!/usr/bin/env python3
"""清洗 LLM 生成的 HTML：剥 ```html 代码块围栏，截取 <!DOCTYPE / <html ...> 到 </html>。

用法：python3 clean_output.py <raw输入> <输出>

打印起止片段便于人工校验；若不以 <!DOCTYPE/<html 开头、不以 </html> 结尾，
说明原始输出不是完整 HTML，应重跑该次生成而不是留半截文件。
"""
import re
import sys


def clean(raw: str) -> str:
    # 1. 剥 ```html / ```xml / ``` 围栏（取第一个围栏块）
    m = re.search(r"```(?:html|xml)?\s*(.*?)```", raw, re.S | re.I)
    if m:
        raw = m.group(1)
    # 2. 从 <!DOCTYPE 或 <html 开始，到 </html> 结束
    i = raw.find("<!DOCTYPE")
    if i == -1:
        i = raw.find("<html")
    if i == -1:
        i = 0
    j = raw.rfind("</html>")
    if j == -1:
        j = len(raw)
    else:
        j += len("</html>")
    return raw[i:j].strip()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    out = clean(open(src, encoding="utf-8", errors="ignore").read())
    open(dst, "w", encoding="utf-8").write(out)
    print(f"{src} -> {dst}: {len(out)} chars")
    print(f"  starts: {out[:40]!r}")
    print(f"  ends:   {out[-40:]!r}")
    if not (out.startswith("<!DOCTYPE") or out.startswith("<html")):
        print("  WARNING: 不以 <!DOCTYPE/<html 开头，输出可能不是完整 HTML，考虑重跑")
