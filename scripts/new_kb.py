#!/usr/bin/env python3
# 跨平台。新建一个分类知识库骨架：kb/<分类>/{raw,wiki}。共享顶层 AGENTS.md 与 scripts/。
# 用法：python3 scripts/new_kb.py <分类名>   （Windows: python）
import os, re, sys, glob, shutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

name = sys.argv[1] if len(sys.argv) > 1 else ""
if not name:
    print("用法: python3 scripts/new_kb.py <分类名>（如 papers）"); sys.exit(1)
d = os.path.join("kb", name)
if os.path.exists(d):
    print(f"已存在: {d}"); sys.exit(1)

for sub in ("raw/papers", "raw/notes", "raw/misc", "wiki/entities", "wiki/concepts", "wiki/synthesis"):
    p = os.path.join(d, *sub.split("/"))
    os.makedirs(p)
    open(os.path.join(p, ".gitkeep"), "w").close()

open(os.path.join(d, "wiki", "index.md"), "w", encoding="utf-8").write(f"""# {name} — Wiki 索引

> 本库范围：<建库后用一句话写清核心目标与边界——ingest 归类和查重的锚>
> 页面目录：人读 + agent 导航用。每次 ingest 新建/重命名页面后更新这里。

## Entities（`entities/`）

_（暂无。）_

## Concepts（`concepts/`）

_（暂无。）_

## Synthesis（`synthesis/`）

_（暂无。必须写“为什么”。）_
""")
open(os.path.join(d, "wiki", "log.md"), "w", encoding="utf-8").write(f"""# {name} — Ingest 时间线

> 追加式。每次 ingest：`## [YYYY-MM-DD] ingest | 来源文件 | 新建/更新页面`。
> 扩展信号（health 跨阈值）也记这里：`## [YYYY-MM-DD] 扩展信号 | 指标 | 建议`。

_（尚无 ingest 记录。分类骨架初始化于此。）_
""")
open(os.path.join(d, "raw", "README.md"), "w", encoding="utf-8").write(f"""# {name}/raw — 原始来源（只读）

**永不编辑。** agent 只读。每个文件顶部写明来源与日期。
子目录：`papers/` 论文、`notes/` 笔记、`misc/` 未分类。
""")

# HOME 导航台（vault 根，wiki/ 之外不进统计；从已有分类复制模板）
homes = sorted(glob.glob("kb/*/HOME.md"))
if homes:
    t = open(homes[0], encoding="utf-8").read()
    t = re.sub(r"^# .* 导航台", f"# {name} 导航台", t, count=1, flags=re.M)
    open(os.path.join(d, "HOME.md"), "w", encoding="utf-8").write(t)

# Obsidian 配置：从已有分类 vault 复制（免重新下载）
copied = False
for src in sorted(glob.glob("kb/*/.obsidian")):
    if os.path.isdir(os.path.join(src, "plugins")) and not src.startswith(d.replace("\\", "/")):
        shutil.copytree(src, os.path.join(d, ".obsidian"))
        copied = True
        break

print(f"✓ 已创建分类知识库: {d}")
print(f"  用法：把来源丢进 {d}/raw/，然后  /ingest {name}  或  python3 scripts/pending.py {name}")
print(f"  Obsidian：把 {d}/ 作为一个 vault 打开（wikilink 与 source 路径在分类内解析）。")
if copied:
    print("  ✓ Obsidian 插件配置已从现有分类复制（Claudian/Dataview/图谱配色即开即用）。")
else:
    print("  插件未配：跑 python3 scripts/setup_obsidian.py 一键装 Claudian + Dataview。")
print(f"  备考/面试类分类可启用复习：python3 scripts/review.py {name} enroll")
