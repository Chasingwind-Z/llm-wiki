#!/usr/bin/env python3
# 跨平台。各分类知识库健康 & 扩展信号自查（阈值按每个分类独立计）。lint 时必跑。
# 只报告、只建议，不改任何东西。
# 用法：python3 scripts/health.py [分类]   （Windows: python；不给分类=逐个都查）
import os, re, sys, glob, datetime
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def norm(p): return p.replace("\\", "/")

def check_one(cat):
    root = f"kb/{cat}/wiki"
    print(f"════════ 分类：{cat} ════════")
    pages = {}
    for f in glob.glob(f"{root}/**/*.md", recursive=True):
        f = norm(f)
        base = os.path.splitext(os.path.basename(f))[0]
        if base in ("index", "log") or "/_archive/" in f:
            continue
        txt = open(f, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---", txt, re.S)
        fm = m.group(1) if m else ""
        def g(k, fm=fm):
            mm = re.search(rf"^{k}:\s*(.+)$", fm, re.M)
            return mm.group(1).strip().strip('"') if mm else ""
        sa = []
        raw_sa = g("see_also_kb")
        if raw_sa:
            sa = [s.strip().strip('"\'') for s in raw_sa.strip("[]").split(",") if s.strip()]
        pages[base.lower()] = (f, g("type"), g("epistemic_status"), g("last_confirmed"),
                               g("lifecycle"), g("review_after"), sa)
    n = len(pages)
    by_type = Counter(v[1] for v in pages.values())
    targets, broken = set(), []
    for f in glob.glob(f"{root}/**/*.md", recursive=True):
        f = norm(f)
        if "/_archive/" in f: continue
        for lk in re.findall(r"\[\[([^\]]+)\]\]", open(f, encoding="utf-8").read()):
            t = lk.split("|")[0].strip()
            if t.startswith("raw/"): continue
            targets.add(t.lower())
            if t.lower() not in pages: broken.append((os.path.basename(f), t))
    orphans = [p for p in pages if p not in targets and pages[p][4] != "stub-intentional"]
    exempt = sum(1 for p in pages if p not in targets and pages[p][4] == "stub-intentional")
    today = datetime.date.today()
    stale, review_due = [], []
    for name, (f, t, e, lc, lfc, ra, _sa) in pages.items():
        try:
            if (today - datetime.date.fromisoformat(lc)).days > 180: stale.append(f)
        except ValueError: pass
        try:
            if ra and datetime.date.fromisoformat(ra) <= today: review_due.append(f)
        except ValueError: pass
    bd = ", ".join(f"{k or '?'}={v}" for k, v in sorted(by_type.items()))
    print(f"  content 页数 : {n}   ({bd})")
    ex = f"（另 {exempt} 个 stub-intentional 已豁免）" if exempt else ""
    print(f"  孤儿页 {len(orphans)}{ex} / 断链 {len(broken)} / last_confirmed>180天 {len(stale)}")
    if broken: print(f"    断链: {broken}")
    if orphans: print(f"    孤儿: {orphans}")
    if review_due:
        print(f"  ⏰ review_after 已到期 {len(review_due)}（人工复核后 confirm 或 supersede，不自动处理）:")
        for f in review_due: print(f"    - {f}")
    # 跨库只读指针：校验目标存在 + 密度信号（见 AGENTS.md「跨库互联」）
    xkb, xkb_broken = Counter(), []
    for name, rec in pages.items():
        for ref in rec[6]:
            tc, _, tp = ref.partition("/")
            xkb[tc] += 1
            if not glob.glob(f"kb/{tc}/wiki/**/{tp}.md", recursive=True):
                xkb_broken.append((name, ref))
    if xkb:
        print("  跨库指针: " + ", ".join(f"→{k} {v}个" for k, v in sorted(xkb.items())))
        if xkb_broken: print(f"    ✗ 失效指针 {len(xkb_broken)}: {xkb_broken}")
        for k, v in xkb.items():
            if v >= 5:
                print(f"  ⚠ 指向 {k} 的指针已达 {v} 个——分界线可能画错，lint 时 flag「考虑合库/挪页」，由用户决定。")
    try:
        loglines = sum(1 for _ in open(f"{root}/log.md", encoding="utf-8"))
        if loglines > 500:
            print(f"  ⚠ log.md 已 {loglines} 行（>500 观察线）：建议把更早条目搬到 log-archive.md（不删除）。")
    except OSError: pass
    sig = []
    if n > 150: sig.append(f"⚠ 页数 {n}>150（认真评估线）：建议评估上 BM25/全文索引（先零重构：Omnisearch 或 ripgrep）。")
    elif n > 100: sig.append(f"· 页数 {n}>100（观察线）：留意 query 是否漏检；暂不用动。")
    if n > 300: sig.append(f"⚠ 页数 {n}>300：若在跑图算法且 Dataview 扛不住，才评估图数据库。")
    if sig:
        for s in sig: print("  " + s)
        print("  → 跨线：请在 lint 结果 flag 这条并追加到本分类 log.md；是否实施由用户决定。")
    else:
        print("  ✓ 未跨任何扩展阈值，检索保持 index.md + wikilink + 搜索即可。")

cats = [sys.argv[1]] if len(sys.argv) > 1 else sorted(
    os.path.basename(d.rstrip("/\\")) for d in glob.glob("kb/*/"))
for c in cats:
    check_one(c)
print("\n提醒：数值置信度/衰减/自动摄入/多agent/router 为永久弃用，任何页数都不触发。")
