#!/usr/bin/env python3
# 跨平台（macOS/Windows/Linux）。列出各分类 kb/<分类>/raw 里尚未 ingest 的来源
# （basename 未出现在该分类 wiki/log.md），检测活来源变更、lint 欠账、复习到期、capture 积压。
# 用法：python3 scripts/pending.py [分类]   （Windows: python）
import os, re, sys, glob, datetime, subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

HAS_PENDING = False
LINT_DUE = []

def scan_one(cat):
    global HAS_PENDING
    root, logf = f"kb/{cat}", f"kb/{cat}/wiki/log.md"
    try:
        log = open(logf, encoding="utf-8").read()
    except OSError:
        log = ""
    pending, changed = [], []
    for base_dir, _dirs, files in os.walk(os.path.join(root, "raw"), followlinks=True):
        for name in files:
            if name in ("README.md", ".gitkeep") or name.startswith("."):
                continue
            f = os.path.join(base_dir, name)
            if name not in log:
                pending.append(f)
            else:
                # 已 ingest 过的活来源（link_raw 的软链接等）：原文在上次 ingest 后被改过？
                dates = sorted(re.findall(r"\[(\d{4}-\d{2}-\d{2})\]",
                                          "\n".join(l for l in log.splitlines() if name in l)))
                try:
                    mtime = datetime.date.fromtimestamp(os.path.getmtime(f)).isoformat()
                except OSError:
                    continue
                if dates and mtime > dates[-1]:
                    changed.append(f)
    if not pending and not changed:
        print(f"[{cat}] ✓ 无待 ingest")
    if pending:
        HAS_PENDING = True
        print(f"[{cat}] 待 ingest（{len(pending)}）：")
        for f in pending: print(f"    - {f}")
    if changed:
        HAS_PENDING = True
        print(f"[{cat}] 🔁 来源已更新、建议重新 ingest 同步 wiki（{len(changed)}）：")
        for f in changed: print(f"    - {f}")
    # 距上次 lint 的 ingest 次数
    n = 0
    for line in log.splitlines():
        if re.match(r"^## \[.*\] lint", line): n = 0
        elif re.match(r"^## \[.*\] ingest", line): n += 1
    if n >= 10:
        LINT_DUE.append(f"  ⏰ [{cat}] 距上次 lint 已 {n} 次 ingest → 建议本次先跑 /lint {cat}")

cats = [sys.argv[1]] if len(sys.argv) > 1 else sorted(
    os.path.basename(d.rstrip("/\\")) for d in glob.glob("kb/*/"))
for c in cats:
    scan_one(c)

if LINT_DUE:
    print()
    for l in LINT_DUE: print(l)

# 复习到期提醒（仅已 enroll 的分类）
try:
    out = subprocess.run([sys.executable, os.path.join("scripts", "review.py")],
                         capture_output=True, text=True, timeout=30).stdout.strip()
    if out: print("\n" + out)
except Exception:
    pass

# capture 积压
capture_n = sum(1 for _d, _s, fs in os.walk("capture") for f in fs
              if f not in (".gitkeep", "README.md"))
if capture_n:
    print(f"\n📥 capture 积压 {capture_n} 条待挑选（/ingest 时 agent 会先提议分拣）")

if HAS_PENDING:
    print("""
【给 agent 的指令】存在待 ingest 文件时，在回应用户第一条消息之后主动做一次 ingest 提议：
  1. 列出上面的待处理文件；
  2. 快速浏览每个文件，各给一行 plan（预计新建/更新哪些 wiki 页、归属哪个分类的判断）；
  3. 问一句「现在 ingest 吗？」——用户同意后才按 AGENTS.md 流程执行（产出后仍停下等复核）。
  未经同意不得直接 ingest；用户明显在忙别的事时提一句即可，不要反复催。""")
else:
    print("\n触发：Claude Code 里  /ingest <分类> ；或对 Codex 说「ingest <分类> 的新东西」。")
