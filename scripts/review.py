#!/usr/bin/env python3
# 跨平台。间隔重复复习（正版遗忘曲线用途：把知识背进脑子，面试/备考场景）。
# 按分类可选启用；状态存 kb/<分类>/wiki/.review.json（脚本独管，agent 只读结果）。
# 间隔阶梯：新页 due 立即 → pass +7天 → +30天 → +90天 → 毕业；fail → 回起点 +2天。
# 用法（Windows 把 python3 换成 python）：
#   python3 scripts/review.py                       # 各已启用分类的到期数（pending 用）
#   python3 scripts/review.py <分类> enroll         # 启用/补录该分类全部内容页（幂等）
#   python3 scripts/review.py <分类> due            # 列出到期页
#   python3 scripts/review.py <分类> pass|fail <页名>
#   python3 scripts/review.py <分类> status         # 阶段分布
import os, re, sys, glob, json, datetime
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

INTERVALS = [7, 30, 90]
STAGE_NAMES = ["新", "7天档", "30天档", "90天档", "🎓已毕业"]
today = datetime.date.today()
iso = today.isoformat()

def state_path(c): return f"kb/{c}/wiki/.review.json"
def load(c):
    try: return json.load(open(state_path(c), encoding="utf-8"))
    except Exception: return {}
def save(c, st):
    json.dump(st, open(state_path(c), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

args = sys.argv[1:]
if not args:  # 摘要模式：给 pending.py 用
    for sp in glob.glob("kb/*/wiki/.review.json"):
        c = sp.replace("\\", "/").split("/")[1]
        st = json.load(open(sp, encoding="utf-8"))
        due = [k for k, v in st.items() if v.get("due") and v["due"] <= iso]
        if due: print(f"📚 [{c}] {len(due)} 页到期待复习 → /review {c}")
    sys.exit(0)

cat = args[0]; cmd = args[1] if len(args) > 1 else ""; page = args[2] if len(args) > 2 else ""

if cmd == "enroll":
    st = load(cat); added = 0
    for f in glob.glob(f"kb/{cat}/wiki/**/*.md", recursive=True):
        f = f.replace("\\", "/")
        base = os.path.splitext(os.path.basename(f))[0]
        if base in ("index", "log") or "/_archive/" in f: continue
        txt = open(f, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---", txt, re.S)
        if m and re.search(r"^lifecycle:\s*stub-intentional", m.group(1), re.M): continue
        if base not in st:
            st[base] = {"stage": 0, "due": iso, "last": None}; added += 1
    save(cat, st)
    print(f"✓ [{cat}] 已启用复习：共 {len(st)} 页在册（本次新录 {added}）。新页 ingest 后自动补录。")

elif cmd == "due":
    st = load(cat)
    if not st: print(f"[{cat}] 未启用复习。启用：python3 scripts/review.py {cat} enroll"); sys.exit(0)
    due = sorted(((k, v) for k, v in st.items() if v.get("due") and v["due"] <= iso),
                 key=lambda kv: kv[1]["due"])
    if not due: print(f"[{cat}] ✓ 今天没有到期页。"); sys.exit(0)
    print(f"[{cat}] 到期 {len(due)} 页（单次复习建议 ≤10）：")
    for k, v in due[:10]:
        print(f"  - {k}（{STAGE_NAMES[v['stage']]}，到期 {v['due']}）")
    if len(due) > 10: print(f"  …另有 {len(due)-10} 页，下次再来")

elif cmd in ("pass", "fail"):
    st = load(cat)
    if page not in st: print(f"✗ [{cat}] 无此在册页：{page}"); sys.exit(1)
    v = st[page]
    if cmd == "pass":
        if v["stage"] >= 4:
            print(f"  {page} 已毕业，无需记录。")
        else:
            v["last"] = iso
            if v["stage"] >= 3:
                v["stage"], v["due"] = 4, None
                print(f"  🎓 {page} 毕业！（不再排期；内容被 supersede 时另行处理）")
            else:
                v["due"] = (today + datetime.timedelta(days=INTERVALS[v["stage"]])).isoformat()
                v["stage"] += 1
                print(f"  ✓ {page} → {STAGE_NAMES[v['stage']]}，下次 {v['due']}")
    else:
        v["stage"] = 0
        v["due"] = (today + datetime.timedelta(days=2)).isoformat()
        v["last"] = iso
        print(f"  ↩ {page} 回到起点，{v['due']} 再来")
    save(cat, st)

elif cmd == "status":
    st = load(cat)
    if not st: print(f"[{cat}] 未启用复习。"); sys.exit(0)
    c = Counter(min(v["stage"], 4) for v in st.values())
    print(f"[{cat}] 在册 {len(st)} 页：" + " ｜ ".join(f"{STAGE_NAMES[s]} {c.get(s,0)}" for s in range(5)))
    due = sum(1 for v in st.values() if v.get("due") and v["due"] <= iso)
    print(f"  今日到期：{due}")

else:
    print("用法见文件头注释"); sys.exit(1)
