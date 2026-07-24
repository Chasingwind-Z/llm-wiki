#!/usr/bin/env python3
# 跨平台。冷度看板（遗忘曲线的去毒实现：系统测量+排序+提醒，"遗忘"动作由人做）。
# 每页三信号自动采集：静默天数（距最近被 query 引用或 git 改动）、未确认天数、反链数。
# 分层：🔥活跃<30d ｜ 🌤正常30–90d ｜ 🧊变冷90–180d ｜ ❄️冷藏候选>180d
# 分类活跃度门控：近90天 query/ingest ≥5 正常｜1–4 低活跃（候选只列TOP5）｜0 休眠（判定暂停）
# 输出：终端摘要 + archive/freshness.html。用法：python3 scripts/freshness.py [分类]
import os, re, sys, glob, html, datetime, subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

today = datetime.date.today()
def days_since(s):
    try: return (today - datetime.date.fromisoformat(s)).days
    except (ValueError, TypeError): return None
def tier(d): return 0 if d < 30 else 1 if d < 90 else 2 if d < 180 else 3
def norm(p): return p.replace("\\", "/")

TIERS = [("🔥 活跃", "#2e9e44"), ("🌤 正常", "#8bb32e"), ("🧊 变冷", "#d99a1b"), ("❄️ 冷藏候选", "#3b7bd4")]
cats = [sys.argv[1]] if len(sys.argv) > 1 else sorted(
    os.path.basename(d.rstrip("/\\")) for d in glob.glob("kb/*/"))
all_sections = []

# output/ 交付物里被用过的页 = 最强使用信号（比 query 引用更重：真拿去产出了东西）
used_in_output = {}
for f in glob.glob("output/**/*.md", recursive=True):
    try: txt = open(f, encoding="utf-8").read()
    except OSError: continue
    m = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", txt, re.M)
    d = m.group(1) if m else datetime.date.fromtimestamp(os.path.getmtime(f)).isoformat()
    for lk in re.findall(r"\[\[([^\]|]+)", txt):
        k = lk.strip().lower()
        if not k.startswith("raw/") and used_in_output.get(k, "") < d:
            used_in_output[k] = d

for cat in cats:
    root, logf = f"kb/{cat}/wiki", f"kb/{cat}/wiki/log.md"
    # git：每文件最近一次改动日期（一次调用全拿）
    touched, cur = {}, None
    try:
        out = subprocess.run(["git", "log", "--format=@%as", "--name-only", "--", root],
                             capture_output=True, text=True, check=True, encoding="utf-8").stdout
        for line in out.splitlines():
            if line.startswith("@"): cur = line[1:]
            elif line.strip() and line not in touched: touched[line] = cur
    except Exception: pass
    # log.md：每页最近被 query 引用日期 + 分类活跃度
    cited, activity_90d = {}, 0
    try:
        for line in open(logf, encoding="utf-8"):
            m = re.match(r"^## \[(\d{4}-\d{2}-\d{2})\] (query|ingest)\b", line)
            if not m: continue
            d = m.group(1); ds = days_since(d)
            if ds is not None and ds <= 90: activity_90d += 1
            if m.group(2) == "query":
                for lk in re.findall(r"\[\[([^\]|]+)", line):
                    k = lk.strip().lower()
                    if cited.get(k, "") < d: cited[k] = d
    except OSError: pass
    # 页面与反链
    pages, inbound = {}, {}
    files = [norm(f) for f in glob.glob(f"{root}/**/*.md", recursive=True)
             if os.path.splitext(os.path.basename(f))[0] not in ("index", "log")
             and "/_archive/" not in norm(f)]
    for f in files:
        txt = open(f, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---", txt, re.S); fm = m.group(1) if m else ""
        def g(k, fm=fm):
            mm = re.search(rf"^{k}:\s*(.+)$", fm, re.M)
            return mm.group(1).strip().strip('"') if mm else ""
        base = os.path.splitext(os.path.basename(f))[0]
        pages[base.lower()] = dict(file=f, name=base, status=g("epistemic_status"),
            last_confirmed=g("last_confirmed"), lifecycle=g("lifecycle"),
            superseded=bool(g("superseded_by") and g("superseded_by") != "null"))
        for lk in re.findall(r"\[\[([^\]|]+)", txt):
            t = lk.strip().lower()
            if not t.startswith("raw/"): inbound[t] = inbound.get(t, 0) + 1
    rows = []
    for key, p in pages.items():
        sig = []
        d = days_since(cited.get(key))
        if d is not None: sig.append(d)
        d = days_since(touched.get(p["file"]))
        if d is not None: sig.append(d)
        d = days_since(used_in_output.get(key))
        if d is not None: sig.append(d)
        if not sig:
            sig.append((today - datetime.date.fromtimestamp(os.path.getmtime(p["file"]))).days)
        silent = min(sig)
        un = days_since(p["last_confirmed"])
        rows.append(dict(**p, silent=silent, unconfirmed=un if un is not None else -1,
                         inbound=inbound.get(key, 0), tier=tier(silent),
                         shipped=key in used_in_output))
    candidates = sorted([r for r in rows if r["tier"] == 3 and not r["superseded"]
                         and r["lifecycle"] != "stub-intentional"],
                        key=lambda r: (-r["silent"], r["inbound"]))
    counts = [sum(1 for r in rows if r["tier"] == t) for t in range(4)]
    if activity_90d == 0:
        mode_note = "🛌 分类休眠（近 90 天无 query/ingest）——冷度判定暂停，回归使用后自动恢复"
        candidates = []
    elif activity_90d < 5:
        mode_note = f"🌗 分类低活跃（近 90 天仅 {activity_90d} 次使用）——冷度参考价值有限，候选仅列 TOP5"
        candidates = candidates[:5]
    else:
        mode_note = ""
    print(f"════════ 分类：{cat}（{len(rows)} 页）════════")
    print("  " + " ｜ ".join(f"{TIERS[t][0]} {counts[t]}" for t in range(4)))
    shipped_n = sum(1 for r in rows if r["shipped"])
    if shipped_n: print(f"  📤 其中 {shipped_n} 页被 output/ 的交付物用过（最强使用信号）")
    if mode_note: print("  " + mode_note)
    if candidates:
        print(f"  ❄️ 冷藏候选 TOP{min(10, len(candidates))}（处置由用户决定：归档 / 合并 / 确认仍有用）：")
        for r in candidates[:10]:
            un = f"{r['unconfirmed']}天" if r["unconfirmed"] >= 0 else "?"
            print(f"    - {r['name']}  静默{r['silent']}天 / 未确认{un} / {r['inbound']}反链 / {r['status'] or '?'}")
    elif "休眠" not in mode_note:
        print("  ✓ 暂无冷藏候选")
    all_sections.append((cat, rows, candidates, counts, mode_note))

os.makedirs("archive", exist_ok=True)
parts = [f"""<!doctype html><meta charset="utf-8"><title>知识库冷度看板</title><style>
body{{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;max-width:880px;margin:2em auto;padding:0 1em;color:#222}}
h2{{border-bottom:2px solid #eee;padding-bottom:.3em}} .bar{{display:flex;height:26px;border-radius:6px;overflow:hidden;margin:.6em 0 1em}}
.bar div{{color:#fff;font-size:12px;line-height:26px;text-align:center;min-width:2px}}
table{{border-collapse:collapse;width:100%;font-size:14px}} td,th{{border-bottom:1px solid #eee;padding:6px 8px;text-align:left}}
.note{{color:#777;font-size:13px}} .tag{{font-size:12px;padding:1px 6px;border-radius:4px;background:#eef}} </style>
<h1>知识库冷度看板</h1>
<p class="note">生成于 {today}｜重新生成：<code>python3 scripts/freshness.py</code>｜
静默 = 距最近被引用/被更新的天数。看板只<b>测量与排序</b>，归档/合并/确认由用户决定——检索永远不会因为页面冷而跳过它。</p>"""]
for cat, rows, candidates, counts, mode_note in all_sections:
    n = max(len(rows), 1)
    parts.append(f"<h2>{html.escape(cat)}（{len(rows)} 页）</h2>")
    if mode_note: parts.append(f"<p class='note'>{html.escape(mode_note)}</p>")
    parts.append("<div class='bar'>")
    for t in range(4):
        if counts[t]:
            parts.append(f"<div style='background:{TIERS[t][1]};width:{counts[t]/n*100:.1f}%' title='{TIERS[t][0]}'>{TIERS[t][0]} {counts[t]}</div>")
    parts.append("</div>")
    if candidates:
        parts.append("<table><tr><th>❄️ 冷藏候选</th><th>静默</th><th>未确认</th><th>反链</th><th>epistemic</th></tr>")
        for r in candidates[:15]:
            un = f"{r['unconfirmed']}天" if r["unconfirmed"] >= 0 else "?"
            parts.append(f"<tr><td>{html.escape(r['name'])}</td><td>{r['silent']}天</td><td>{un}</td>"
                         f"<td>{r['inbound']}</td><td><span class='tag'>{html.escape(r['status'] or '?')}</span></td></tr>")
        parts.append("</table>")
    elif "休眠" not in mode_note:
        parts.append("<p class='note'>✓ 暂无冷藏候选</p>")
open("archive/freshness.html", "w", encoding="utf-8").write("".join(parts))
print("\n✓ 看板已写入 archive/freshness.html（浏览器打开即可）")
