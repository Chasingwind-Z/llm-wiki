#!/usr/bin/env python3
# 跨平台。生成 archive/sessions-index.md —— Claude Code + Codex 本地会话索引（零 LLM）。
# 数据源：~/.claude/projects/*/*.jsonl、~/.codex/sessions/**/rollout-*.jsonl
# 用法：python3 scripts/sessions_index.py   （随时重跑，全量覆盖生成）
import json, os, re, sys, glob, datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

HOME = os.path.expanduser("~")
rows = []

def clean(s, limit=70):
    s = re.sub(r"\s+", " ", (s or "")).replace("|", "/").strip()
    return (s[:limit] + "…") if len(s) > limit else s

# ---- Claude Code ----
for f in glob.glob(os.path.join(HOME, ".claude", "projects", "*", "*.jsonl")):
    proj = os.path.basename(os.path.dirname(f))
    proj_disp = proj.replace("-", "/") if proj.startswith("-") else proj
    summary, first_user, ts = None, None, None
    try:
        with open(f, errors="replace", encoding="utf-8") as fh:
            for line in fh:
                if len(line) > 200_000: continue
                try: d = json.loads(line)
                except Exception: continue
                if ts is None and d.get("timestamp"): ts = d["timestamp"][:10]
                if d.get("type") == "summary" and d.get("summary"): summary = d["summary"]
                if first_user is None and d.get("type") == "user":
                    c = (d.get("message") or {}).get("content")
                    if isinstance(c, str) and c.strip(): first_user = c
                    elif isinstance(c, list):
                        for part in c:
                            if isinstance(part, dict) and part.get("type") == "text" and part.get("text", "").strip():
                                first_user = part["text"]; break
    except OSError: continue
    if ts is None:
        ts = datetime.date.fromtimestamp(os.path.getmtime(f)).isoformat()
    title = summary or first_user
    if not title: continue
    if title.strip().lower().startswith("reply with exactly"): continue  # warmup 噪音
    rows.append((ts, "claude", clean(proj_disp, 40), clean(title), f.replace(HOME, "~")))

# ---- Codex ----
for f in glob.glob(os.path.join(HOME, ".codex", "sessions", "*", "*", "*", "rollout-*.jsonl")):
    cwd, first_user, ts = None, None, None
    try:
        with open(f, errors="replace", encoding="utf-8") as fh:
            for line in fh:
                if len(line) > 200_000: continue
                try: d = json.loads(line)
                except Exception: continue
                if ts is None and d.get("timestamp"): ts = str(d["timestamp"])[:10]
                p = d.get("payload") or {}
                if cwd is None and d.get("type") == "session_meta": cwd = p.get("cwd")
                if first_user is None:
                    if p.get("type") == "user_message" and p.get("message"): first_user = p["message"]
                    elif p.get("role") == "user":
                        c = p.get("content")
                        if isinstance(c, list):
                            for part in c:
                                if isinstance(part, dict) and part.get("text", "").strip():
                                    first_user = part["text"]; break
                if cwd and first_user: break
    except OSError: continue
    if ts is None:
        m = re.search(r"rollout-(\d{4}-\d{2}-\d{2})", f)
        ts = m.group(1) if m else "????-??-??"
    if not first_user: continue
    rows.append((ts, "codex", clean((cwd or "?").replace(HOME, "~"), 40),
                 clean(first_user), f.replace(HOME, "~")))

rows.sort(key=lambda r: r[0], reverse=True)
out = ["# 会话索引（自动生成，勿手改）", "",
       f"> `python3 scripts/sessions_index.py` 重新生成。共 {len(rows)} 条。",
       "> 档案层：只做定位，不是知识页。要用某次会话的内容时，让 agent 去读对应转录路径。", "",
       "| 日期 | 工具 | 项目 | 标题 / 首条消息 | 转录 |", "|---|---|---|---|---|"]
for ts, tool, proj, title, path in rows:
    out.append(f"| {ts} | {tool} | `{proj}` | {title} | `{path}` |")
os.makedirs("archive", exist_ok=True)
open(os.path.join("archive", "sessions-index.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
nc = sum(1 for r in rows if r[1] == "claude")
print(f"✓ archive/sessions-index.md — {len(rows)} 条（claude {nc} / codex {len(rows)-nc}）")
