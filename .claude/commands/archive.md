---
description: Batch-execute cold-candidate verdicts (archive / merge / confirm)
argument-hint: <分类>
---
> 分类留空且 `kb/` 下只有一个分类时，默认就是它，不必追问。

按 `AGENTS.md`「页面生命周期维护」的 archive 协议处理 **`$ARGUMENTS` 分类**的冷藏候选。

1. 跑 `python3 scripts/freshness.py $ARGUMENTS` 拿冷藏候选清单；为空则报告后停下。
2. 把候选整理成一张表（页名 / 静默天数 / 未确认天数 / 反链 / epistemic_status +
   一句内容摘要），让我对每页三选一：**归档 / 合并 / 确认仍有用**（可整批说）。
3. 按裁决执行：
   - **归档**：移到 `kb/$ARGUMENTS/wiki/_archive/`，页面顶部加
     「🗄 已冷藏归档（日期），原因」，index 条目挪到「已归档」小节（无此节则建）；
   - **合并**：走 `/merge` 协议（先出方案再确认）；
   - **确认**：`last_confirmed` 刷新为今天。
4. 跑 `python3 scripts/health.py $ARGUMENTS` 自检无断链（指向已归档页的链接保留有效——
   `_archive/` 只是不进统计，不是删除）；单独 commit：
   `archive($ARGUMENTS): 归档 n / 合并 m / 确认 k`。
