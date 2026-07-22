---
type: synthesis
epistemic_status: verified_inference
sources: ["[[raw/2026-07-01-为什么要编译知识.md]]", "[[知识编译]]"]
last_confirmed: 2026-07-01
supersedes: null
superseded_by: null
---
# 编译还是 RAG（synthesis 页示范：必须写推理过程）

**结论**：个人学习/研究笔记选编译；海量异构文档、只读不维护的场景选 RAG。

**比较了什么**：编译（本范式）与查询时检索（RAG）两条路线。

**为什么排除 RAG**：个人库材料量小（百页级）、查询反复命中同一批知识，
编译的一次性成本很快摊平 [source: 2026-07-01-为什么要编译知识, 第2段]；
且个人场景需要「答案可追溯、错误可体检」，RAG 的片段拼接做不到。

**前提条件**：库规模在检索天花板内（约 150 页）；用户愿意为每批入库花几分钟
复核。前提破坏时结论要重审：库爆长就得给编译层叠检索（见 AGENTS.md 扩展阈值）。

注意本页 epistemic_status 至高是 verified_inference：它引用了 wiki 页做依据，
按防循环自证规则永不标 fact。
