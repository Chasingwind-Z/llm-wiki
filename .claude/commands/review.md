---
description: Spaced-repetition review of a category's wiki pages (active recall quiz)
argument-hint: <分类>（如 ai-infra）
---
> 分类留空且 `kb/` 下只有一个分类时，默认就是它，不必追问。

对 **`$ARGUMENTS` 分类**做一轮间隔重复复习（把知识背进脑子，面试/备考用）。
排期由脚本管，你只负责出题和判卷；**pass/fail 必须基于用户的真实回答，不许代答**。

1. 跑 `python3 scripts/review.py $ARGUMENTS due`。未启用则告知启用命令后停下；无到期页则报告下次到期时间（`status`）。
2. 对每个到期页（单次 ≤10 个）：
   - **先不展示页面内容**，读该页后出 1–2 个主动回忆题（问核心机制/判断依据/对比取舍，
     不问"是什么"这种复述题；synthesis 页优先问"为什么这么定、排除了什么"）；
   - 等用户作答，对照页面内容给反馈：答对了哪些、漏了哪些、错了哪些；
   - 据实记录：答出核心 → `python3 scripts/review.py $ARGUMENTS pass <页名>`；
     答不出/答错要点 → `... fail <页名>`。模糊时问用户自评，宁 fail 勿 pass。
3. 结束后跑 `python3 scripts/review.py $ARGUMENTS status` 汇报：本轮 pass/fail、各阶段分布、下次到期。
4. 复习中若发现页面内容本身有错/过时，**不改页面**，记下来提醒用户走 supersession/lint 流程。
