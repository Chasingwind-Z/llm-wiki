---
description: Re-verify a page's claims against its raw sources, refresh last_confirmed
argument-hint: <分类> <页名>（或 <分类> --due = 处理该分类全部 review_after 到期页）
---
> 分类留空且 `kb/` 下只有一个分类时，默认就是它，不必追问。

按 `AGENTS.md`「页面生命周期维护」的 verify 协议核实 **`$ARGUMENTS`**。
`--due` 时先用 `python3 scripts/health.py <分类>` 拿到期清单，逐页处理（单次 ≤5 页）。

1. 读目标页，找出它的**关键主张**（结论、数字、状态类陈述——不用逐句）。
2. 重读 frontmatter `sources` 列的全部 raw 原文，逐条核对，输出三态报告：
   - ✅ **支持**：原文依据仍在（引用位置）；
   - ⚠️ **存疑**：原文没有直接依据 / 当时是推断（对照 epistemic_status 是否标对）；
   - ❌ **已过时**：有理由认为现实已变（说明理由）。
   **默认只对照 raw 来源，不联网**；确需查外部最新信息（版本号/行情类）先问我，
   我同意后才查，且查到的东西按新来源走 capture，不直接改页。
3. 按我的裁决执行：全部成立 → `last_confirmed` 刷新为今天（有 `review_after` 的
   按其时间敏感度顺延一个合理周期并说明）；有被推翻 → 提出 supersession 方案
   （新页/改写）待我确认。
4. `log.md` 记一行 `## [日期] verify | <页名> | 结论`；改动单独 commit。
