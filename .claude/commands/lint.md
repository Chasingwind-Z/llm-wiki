---
description: Lint a category's wiki (links, frontmatter, contradictions) + growth-signal monitoring
argument-hint: <分类>（留空=所有分类）
---
> 分类留空且 `kb/` 下只有一个分类时，默认就是它，不必追问。

按 `AGENTS.md` 的 lint 规则体检 **`$ARGUMENTS`**（留空则所有分类），并履行「扩展触发条件与监控职责」。只报告、不改动。

1. 跑 `python3 scripts/health.py $ARGUMENTS`，读规模指标与扩展信号结论
   （孤儿豁免 `lifecycle: stub-intentional`、`review_after` 到期、log.md 行数已由脚本覆盖）。
   再跑 `python3 scripts/freshness.py $ARGUMENTS` 生成冷度看板；若有「❄️ 冷藏候选」，
   在报告里列出并请用户裁决（归档 / 合并 / 确认仍有用），**不自动处置**。
2. 另查（脚本没覆盖的）：
   - frontmatter 必填六字段齐全、有无误写数值置信度；
   - `epistemic_status` 有无被滥用（speculation/hypothesis 当 fact）；
   - `lifecycle: stub-intentional` 有无被滥用（内容明显已超出 stub 还挂着豁免）；
   - synthesis 页是否真写了“为什么”（比较/排除/前提）、关键主张有无行内溯源 `[source: ...]`；
   - 有无 procedural 页混进 wiki（操作手册式内容，该转 scripts/skill）；
   - **溯源抽查**：随机抽 3 条 `fact` 主张回 raw 原文核对（标错的降级并报告）；
   - **缺口盘点**：对比 raw/ 与 log.md 的 ingest 记录，列出未蒸馏来源、明显该有
     而没有的页、开放问题，覆盖式更新该分类 `index.md` 的「缺口」小节（无则移除）；
   - 有无被推翻却没做 supersession 标注的旧页；
   - 潜在跨来源矛盾（列出，**不自动判定**，标为待人工复核）。
3. **结构性问题可直接修**（仅限确定性操作：`index.md` 缺条目回填、条目排序、
   「缺口」小节覆盖更新、review_after 到期后经我确认的 `last_confirmed` 刷新）；
   **语义问题一律只报告**。
4. **若 health.py 报出跨阈值的扩展信号**：flag 那条建议，并追加一行到该分类的 `wiki/log.md`
   （`## [日期] 扩展信号 | 指标 | 建议`）。**是否实施由用户决定，不要自动上任何机制。**
5. 在该分类 `wiki/log.md` 追加一行 `## [日期] lint | <一句话结果摘要>`
   （pending.py 靠它计算「距上次 lint 的 ingest 次数」提醒）。
6. 汇总成简短体检报告给我；除结构性修复、扩展信号行、lint 记录行外不改其它内容、不 commit。
