---
description: Merge duplicate/same-concept wiki pages with supersession and link rewrite
argument-hint: <分类> <页A> <页B> [...]（或留空=从最近 lint 报告里挑重复页）
---
按 `AGENTS.md`「页面生命周期维护」的 merge 协议合并 **`$ARGUMENTS`** 指定的页面
（未指定则先看该分类最近的 lint 报告/log 里标记的重复页，列出让我选）。

1. **先出方案、不动手**：
   - 保留哪一页（内容更全/命名更规范者），理由一句话；
   - 被并页有哪些**独有内容**要移入（逐条列出，标注各自的 source 与 epistemic_status）；
   - `grep` 全分类统计：哪些页面的入链需要改写指向保留页（列文件名清单）；
   - index.md 怎么改。
2. 我确认后执行：移内容（surgical，不整页重写保留页）→ 被并页顶部加
   「🔀 已并入 [[保留页]]（日期）」+ frontmatter `superseded_by` → 保留页
   `supersedes` 列出被并页 → 改写全部入链 → 更新 index → `log.md` 记一行。
3. 自检：跑 `python3 scripts/health.py <分类>` 确认无断链后，单独 commit：
   `merge(<分类>): A,B → C`。
4. 若该分类启用了复习：被并页在 `.review.json` 里的条目告诉我怎么处理（通常删除，
   保留页照常）。
