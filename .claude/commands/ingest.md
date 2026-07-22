---
description: Ingest a category's new raw/ sources into its wiki, stopping for review before commit
argument-hint: <分类>（如 ai-agents；留空则先列出所有分类的待处理项）
---
> 分类留空且 `kb/` 下只有一个分类时，默认就是它，不必追问。

按 `AGENTS.md` 的 ingest 规则处理 **`$ARGUMENTS` 分类**（`kb/$ARGUMENTS/`）里尚未 ingest 的新来源。
人在环里、先复核后提交。

0. **capture 分拣**（若 `capture/` 下有积压文件）：逐个快速浏览，给出分拣提议——
   「值得入库 → 建议分类」或「建议删除（理由）」，我**一次确认**后：入库的移到
   `kb/<分类>/raw/`（agent 只能选现有分类），删除的删掉。然后再进入正常流程。
1. 先跑 `python3 scripts/pending.py $ARGUMENTS` 列出待处理文件（为空则停下告诉我；未指定分类则先展示所有分类的待处理项，问我做哪个）。
   对标 🔁 的「来源已更新」文件：重读原文全文，**surgical 更新**它当初影响的 wiki 页
   （对照 log.md 找到哪些页），结论被推翻的走 supersession；log 记一行 re-ingest。
2. 单次不超过 10 个文件。对每个待处理来源，按 `AGENTS.md` 在 `kb/$ARGUMENTS/wiki/` 下：
   - **建新页前先查重（强制）**：中英双语关键词（含同义词/缩写/译名）grep 现有页面；
     命中同概念页就更新它、不新建；查重过程记入 `log.md`；
   - **更新已有页面时 surgical update**：只改本次来源涉及的段落，不整页重写；
   - 生成/更新页面，frontmatter 必填六字段齐全（时间敏感页可加 `review_after`）、**不写数值置信度**；
   - `epistemic_status` 取值准确（论文原文=fact，归纳=verified_inference，我的猜测单独标 hypothesis/speculation）；
   - typed link（`[[X]] {relation}`）；过时用 supersession 不做衰减；
   - synthesis 页必须写“为什么”（比较/排除/前提），关键主张带行内溯源 `[source: raw-slug, 位置]`；
     矛盾当研究问题记录，不自动判定；
   - procedural 内容（怎么做某事）不建 wiki 页，指给 scripts/skill/AGENTS.md；
   - **来源含图片/PDF 图表时逐图查看并蒸馏**（按 AGENTS.md「多模态来源」节：
     实质信息入页 + `[source: 来源, 图N]` 溯源；跳过的图在 log 留痕；>20 张分批）。
3. 更新该分类的 `index.md` 和 `log.md`（含“新建 vs 更新”的判断依据与查重记录）。
4. **停下**，把本批产出与自检汇总给我复核——**先不要 commit**。
5. 我确认后再单独 commit：`ingest($ARGUMENTS): 处理了 <来源摘要>，影响页面 <n> 个`；
   commit 后 `git push`（有远端且可达时；失败不阻塞，提醒我即可）。
6. 若该分类已启用复习（存在 `kb/$ARGUMENTS/wiki/.review.json`），commit 后跑
   `python3 scripts/review.py $ARGUMENTS enroll` 把新页自动补进复习册。
