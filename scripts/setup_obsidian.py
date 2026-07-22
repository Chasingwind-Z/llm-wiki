#!/usr/bin/env python3
# 跨平台。给每个 kb/<分类>/ vault 配好 Obsidian 体验（幂等可重跑）：
#   1. 安装/更新 Claudian（Claude Code + Codex 嵌入侧边栏）
#   2. 安装/更新 Dataview（按 epistemic_status / last_confirmed 做表格筛查）
#   3. 图谱默认按 entities/concepts/synthesis 三色分组（已有 graph.json 则不动）
# 用法：python3 scripts/setup_obsidian.py   （走系统代理环境变量）
import os, sys, json, glob, shutil, tempfile, urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "llm-wiki-setup"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def fetch_plugin(repo, name, tmp):
    tag = fetch_json(f"https://api.github.com/repos/{repo}/releases/latest")["tag_name"]
    d = os.path.join(tmp, name); os.makedirs(d, exist_ok=True)
    for f in ("main.js", "manifest.json", "styles.css"):
        url = f"https://github.com/{repo}/releases/download/{tag}/{f}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "llm-wiki-setup"})
            with urllib.request.urlopen(req, timeout=60) as r, open(os.path.join(d, f), "wb") as out:
                shutil.copyfileobj(r, out)
        except Exception:
            pass  # 个别插件无 styles.css
    return tag

tmp = tempfile.mkdtemp()
print("下载插件最新 release...")
v1 = fetch_plugin("YishenTu/claudian", "claudian", tmp)
v2 = fetch_plugin("blacksmithgu/obsidian-dataview", "dataview", tmp)
print(f"  claudian {v1} / dataview {v2}")

for d in sorted(glob.glob("kb/*/")):
    cat = os.path.basename(d.rstrip("/\\"))
    ob = os.path.join(d, ".obsidian")
    for p in ("claudian", "dataview"):
        pd = os.path.join(ob, "plugins", p); os.makedirs(pd, exist_ok=True)
        for f in os.listdir(os.path.join(tmp, p)):
            shutil.copy2(os.path.join(tmp, p, f), pd)
    cfg = os.path.join(ob, "community-plugins.json")
    try: plugins = json.load(open(cfg))
    except Exception: plugins = []
    for p in ("claudian", "dataview"):
        if p not in plugins: plugins.append(p)
    json.dump(plugins, open(cfg, "w"))
    gp = os.path.join(ob, "graph.json")
    if not os.path.exists(gp):
        json.dump({"colorGroups": [
            {"query": "path:entities",  "color": {"a": 1, "rgb": 5016565}},
            {"query": "path:concepts",  "color": {"a": 1, "rgb": 3055172}},
            {"query": "path:synthesis", "color": {"a": 1, "rgb": 14260763}},
        ]}, open(gp, "w"))
    print(f"  ✓ kb/{cat}")
shutil.rmtree(tmp, ignore_errors=True)

print("""
首次在 Obsidian 里打开某个 kb/<分类>/ 时（File → Open folder as vault）：
  1. 弹出信任提示 → 选 Trust / 启用社区插件（一次性，Obsidian 安全机制绕不开）；
  2. 若 Claudian 提示找不到 CLI，在其设置里填 claude / codex 的完整路径
     （macOS 常见 ~/.local/bin/…；Windows 用 where claude 查）。""")
