#!/usr/bin/env python3
# 桌面右键/「发送到」的入库选择器（跨平台，console 交互）。
# Windows：由 setup_quick_action_win.py 装进「发送到」菜单后右键调用。
# 也可手动跑：python3 scripts/quick_store.py <文件或文件夹>...
# 流程：选分类（动态列出 kb/ 下全部 + capture 兜底）→ 选方式（软链=活来源 / 复制=快照）→ 落库。
import os, sys, glob, shutil, subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

files = [f for f in sys.argv[1:] if os.path.exists(f)]
if not files:
    print("用法: python3 scripts/quick_store.py <文件或文件夹>...")
    sys.exit(1)

cats = sorted(os.path.basename(d.rstrip("/\\")) for d in glob.glob("kb/*/"))
if not cats:
    print("还没有任何分类库，先跑: python3 scripts/new_kb.py <名字>")
    sys.exit(1)

print(f"待存入 {len(files)} 项：" + "、".join(os.path.basename(f) for f in files[:5])
      + ("…" if len(files) > 5 else ""))
for i, c in enumerate(cats, 1):
    print(f"  [{i}] {c}")
print("  [0] capture（还没想好，稍后分拣）")
try:
    choice = input("存入哪个知识库？输入编号: ").strip()
except (EOFError, KeyboardInterrupt):
    sys.exit(0)

if choice == "0":
    dest = os.path.join("capture")
    os.makedirs(dest, exist_ok=True)  # capture 按需创建
    for f in files:
        (shutil.copytree if os.path.isdir(f) else shutil.copy2)(
            f, os.path.join(dest, os.path.basename(f)))
    print(f"✓ {len(files)} 项已复制进 capture/（下次开工会提醒分拣）")
    sys.exit(0)

try:
    cat = cats[int(choice) - 1]
except (ValueError, IndexError):
    print("无效编号"); sys.exit(1)

mode = input("方式：[l] 软链接（活来源，改原文会提醒同步） / [c] 复制（快照）: ").strip().lower()
if mode == "l":
    r = subprocess.run([sys.executable, os.path.join("scripts", "link_raw.py"), cat] + files)
    sys.exit(r.returncode)
else:
    dest = os.path.join("kb", cat, "raw")
    for f in files:
        (shutil.copytree if os.path.isdir(f) else shutil.copy2)(
            f, os.path.join(dest, os.path.basename(f)))
    print(f"✓ {len(files)} 项已复制进 kb/{cat}/raw/（下次开工会提醒 ingest）")
