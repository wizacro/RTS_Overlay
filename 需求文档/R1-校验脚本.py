# -*- coding: utf-8 -*-
"""R1 校验脚本：说明文档中文化后的自动化检查。
用法：python R1-校验脚本.py
检查项对应需求文档 R1 第 6 节清单 V2-V6（V1 由 git status 人工确认，V7/V8 为通读检查）。
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILES = ["Readme.md", "Changelog.md"]

old_text = {}
new_text = {}
for f in FILES:
    raw = subprocess.run(["git", "show", f"HEAD:{f}"], cwd=REPO, capture_output=True).stdout
    old_text[f] = raw.decode("utf-8")
    new_text[f] = (REPO / f).read_bytes().decode("utf-8")

problems = []


def gh_anchor(title: str) -> str:
    """近似 GitHub 的标题锚点算法：小写、去掉标点（保留字母/数字/下划线/连字符/空格）、空格转连字符。"""
    s = title.strip().lower()
    kept = [ch for ch in s if ch.isalnum() or ch in "_- "]
    return "".join(kept).replace(" ", "-")


def headings(text: str):
    hs = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            hs.append(m.group(2).strip())
            continue
        # Setext 样式标题：下一行是 === 或 --- 且上一行非空非列表
        if re.match(r"^(=+|-+)\s*$", line) and i > 0:
            prev = lines[i - 1]
            if prev.strip() and not prev.lstrip().startswith(("#", "-", "*", "+")) \
               and not re.match(r"^\s*\d+\.", prev) and not prev.startswith(("\t", "    ")):
                hs.append(prev.strip())
    return hs


def imgs(text: str):
    return sorted(re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text))


def ext_urls(text: str):
    # 链接目标里的 URL + 裸文本 URL；剥掉句尾英文句号（属标点，非 URL 一部分）
    urls = set(re.findall(r"\]\((https?://[^)\s]+)", text))
    urls |= {u.rstrip(".") for u in re.findall(r"(?<!\()(https?://[^\s)\]<>，。．（）“”‘’]+)", text)}
    return urls


def internal_links(text: str):
    return re.findall(r"\]\(#([^)\s]+)\)", text)


for f in FILES:
    old, new = old_text[f], new_text[f]
    print(f"===== {f} =====")

    # V2 标题结构
    ho, hn = headings(old), headings(new)
    print(f"V2 标题数量: 原文 {len(ho)} / 译文 {len(hn)}")
    if len(ho) != len(hn):
        problems.append(f"{f}: 标题数量不一致 {len(ho)} vs {len(hn)}")

    # V3 图片路径
    io, im = imgs(old), imgs(new)
    if io != im:
        problems.append(f"{f}: 图片路径不一致")
        print("V3 图片路径: 不一致 ->", set(io) ^ set(im))
    else:
        print(f"V3 图片路径: 一致（{len(io)} 张）")
    missing_imgs = [p for p in im if not (REPO / p.lstrip("/")).exists()]
    if missing_imgs:
        problems.append(f"{f}: 图片文件不存在 {missing_imgs}")

    # V4 外部 URL 与相对链接
    uo, un = ext_urls(old), ext_urls(new)
    lost = uo - un
    if lost:
        problems.append(f"{f}: 丢失的外部 URL: {lost}")
    print(f"V4 外部 URL: 原文 {len(uo)} 个 / 译文 {len(un)} 个，丢失 {len(lost)} 个")
    rel_targets = set(re.findall(r"\]\((?!https?://|#|mailto:)([^)\s]+)", new))
    bad_rel = []
    for t in rel_targets:
        path = t.split("#")[0].lstrip("/")
        if path and not (REPO / path).exists():
            bad_rel.append(t)
    if bad_rel:
        problems.append(f"{f}: 相对链接目标不存在 {bad_rel}")
    print(f"V4 相对链接目标检查: {len(rel_targets)} 个，失效 {len(bad_rel)} 个")

    # V5 内部锚点（仅 Readme 有 TOC；Changelog 原文无内部锚点）
    anchors = {gh_anchor(h) for h in headings(new)}
    ilinks = internal_links(new)
    if f == "Readme.md":
        ilinks_old = internal_links(old)
        print(f"V5 内部锚点链接: 原文 {len(ilinks_old)} 个 / 译文 {len(ilinks)} 个")
        if len(ilinks) != len(ilinks_old):
            problems.append(f"{f}: 内部锚点链接数量变化 {len(ilinks_old)} -> {len(ilinks)}")
        bad = [a for a in ilinks if a not in anchors]
        if bad:
            problems.append(f"{f}: 无法解析的锚点 {bad}")
        print(f"V5 锚点解析: {'全部有效' if not bad else '失效 ' + str(bad)}")

    # V6 编码与行尾
    raw = (REPO / f).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        problems.append(f"{f}: 存在 UTF-8 BOM")
    crlf_ok = b"\r\n" in raw and re.search(rb"(?<!\r)\n", raw) is None
    print(f"V6 编码: UTF-8 无 BOM={'是' if not raw.startswith(b'\xef\xbb\xbf') else '否'}，全部 CRLF={'是' if crlf_ok else '否'}")
    if not crlf_ok:
        problems.append(f"{f}: 行尾存在 LF（应为 CRLF）")

print()
if problems:
    print("!! 发现问题:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("全部自动检查通过 ✅")
