#!/usr/bin/env python3
# 跨平台。把工作台里的文件【软链接】进某分类的 raw/——"活来源"：原文只维护一份，
# 改动由 pending 检测并提议重新 ingest。
# 用法：python3 scripts/link_raw.py <分类> <文件或文件夹>...
#   文件 → 链接该文件；文件夹 → 链接其下一层普通文件（不递归，隐藏文件跳过）
# Windows 注意：创建符号链接需要「开发者模式」（设置 → 系统 → 开发者选项）或管理员
# 权限；不想开的话用 --copy 改为复制模式（快照，不跟踪原文变更）。
import os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

args = [a for a in sys.argv[1:] if a != "--copy"]
copy_mode = "--copy" in sys.argv
if len(args) < 2:
    print("用法: python3 scripts/link_raw.py <分类> <文件或文件夹>... [--copy]"); sys.exit(1)
cat, paths = args[0], args[1:]
dest = os.path.join("kb", cat, "raw")
if not os.path.isdir(dest):
    print(f"✗ 分类不存在: {cat}（先 python3 scripts/new_kb.py {cat}）"); sys.exit(1)

def link_one(src):
    src = os.path.abspath(src)
    base = os.path.basename(src)
    tgt = os.path.join(dest, f"linked-{base}")
    if os.path.lexists(tgt):
        try:
            if os.readlink(tgt) == src:
                print(f"  = 已存在同链接: {base}"); return
        except OSError: pass
        print(f"  ✗ 冲突跳过（{tgt} 已存在且指向别处）"); return
    if copy_mode:
        import shutil; shutil.copy2(src, tgt)
        print(f"  ✓ 复制 linked-{base}（快照模式）"); return
    try:
        os.symlink(src, tgt)
        print(f"  ✓ linked-{base} → {src}")
    except OSError as e:
        print(f"  ✗ 建链失败（{e}）")
        if os.name == "nt":
            print("    Windows：请开启「开发者模式」后重试，或加 --copy 用复制模式。")

for p in paths:
    if os.path.isfile(p):
        link_one(p)
    elif os.path.isdir(p):
        print(f"[目录] {p}（链接其下一层文件）:")
        for f in sorted(os.listdir(p)):
            fp = os.path.join(p, f)
            if os.path.isfile(fp) and not f.startswith("."):
                link_one(fp)
    else:
        print(f"  ✗ 不存在: {p}")
print(f"\n之后：/ingest {cat} 正常处理；你改动原文后，开工提醒会标「🔁 来源已更新」。")
