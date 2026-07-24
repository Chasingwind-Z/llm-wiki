# AGENTS.md / CLAUDE.md — 知识库行为规范

> `CLAUDE.md` 的内容是一行 `@AGENTS.md`，两者天然一致。改规则只改这一份。

## 这是什么

单人使用的个人知识库：用户把原始材料（论文、笔记、文章、转录、截图）放进来，
agent 把它蒸馏成带可信度标注的互链知识页。按主题分成多个分类库（见「多分类结构」）。
目标不是团队知识库或发表用系统，是「攒起来能查、能问、能对比的笔记网络」。
任何 agent（Claude Code、Codex，或其他）在这个仓库里工作前必须先完整读完这份文件。

**被问到本库覆盖领域的知识问题时，先查对应分类的 `wiki/`（从 `index.md` 进入）再作答**，
并按 query 规则记录引用。没有这个动作 wiki 就是死重：长期案例实证，这一行入口触发
是整个系统最关键的组件。

## 多分类结构

一个仓库装**多个分类知识库**，每个分类是 `kb/<分类>/` 下一棵独立的 raw+wiki 子树，
**共享**顶层这一份 schema 与 `scripts/`。新建分类用 `python3 scripts/new_kb.py <名字>`，
不必另开仓库。

```
<repo>/
├── AGENTS.md / CLAUDE.md   # 共享 schema（后者为 symlink）
├── scripts/                # 共享工具（按分类跑）
├── .claude/commands/       # /ingest、/lint（接分类参数）、/distill
├── capture/                # 采集缓冲层：chat（网页AI对话）/ clips（网页剪藏）/ drafts（会话蒸馏草稿）
├── output/                 # 交付层：拿知识产出的成品（PPT大纲/周报/文案）；不进 wiki、不进 lint
├── archive/                # 档案层：sessions-index.md（CLI会话索引，脚本生成）等；不进 wiki、不进 lint
└── kb/
    └── <分类>/             # 一个分类 = 一个独立知识库
        ├── raw/            # 原始来源，只读，永不编辑；子目录随意，每文件顶部写明来源+日期
        └── wiki/           # 唯一可被 agent 持续改写的部分
            ├── index.md    # 页面目录（>150 篇后不再是主检索手段，但仍维护）
            ├── log.md      # 追加式时间线：`## [YYYY-MM-DD] ingest | 来源 | 新建/更新页面`
            ├── entities/   # 人物、论文、方法、工具等实体页
            ├── concepts/   # 抽象概念/理论页
            └── synthesis/  # 跨来源的综合判断、对比、结论页
```

**分类间彼此隔离**：各有自己的 `raw/wiki/log/index`，`health.py` 的扩展阈值**按分类独立计**
（不同主题不累加、不互相误触发）。ingest / query / lint 都**针对某个分类**执行。

**Obsidian**：把 `kb/<分类>/` 作为一个 vault 打开——页面里的 `[[X]]` 与 `sources` 路径
都相对该分类根解析，无需改写。（想跨分类连也行：把整个 repo 作为一个 vault，但注意各分类
`index/log` 同名会有歧义，建议还是**每分类一个 vault**。）

## capture 缓冲层与 archive 档案层

**所有入口先落 `capture/`，由用户挑选后才进 `kb/<分类>/raw/`**——agent 可以在挑选时建议
归属分类，但不许自建新分类。`capture/` 里的东西不算知识库内容：不 lint、不链接、不引用。
ingest 开始前若 capture 有积压，agent **先提议分拣**（入库→建议分类 / 建议删除+理由），
用户一次确认后代为移动/删除——挑选的劳动归 agent，判断归用户。

- `capture/chat/`：网页 AI 对话（浏览器扩展导出 / MCP 写入 / 手动粘贴）
- `capture/clips/`：Obsidian Web Clipper 剪藏落点
- `capture/drafts/`：`/distill` 产出的会话蒸馏草稿（`status: draft`，进 wiki 必须经 ingest 复核）

`archive/` 是档案层（如 `sessions-index.md`，由 `python3 scripts/sessions_index.py` 生成的
CLI 会话索引）：只做定位用，agent 不得把档案层内容当知识引用进 wiki 页。

## output 交付层（顶层 `output/`，按需创建）

知识拿去用之后产出的成品：组会 PPT 大纲、周报、博客/小红书文案、面试答题稿等。
**与 wiki 是两种东西，不许互相污染**：wiki 是面向未来的自己、长期有效、过时走
supersession；output 面向特定受众和场合、一次性、发完即存档。同一个知识在两边
写法不同（wiki 写完整推导与前提，交付物按听众裁剪），把交付物版本回填进 wiki
属于知识退化。

- 文件头三行记来源与用途：
  ```yaml
  ---
  date: YYYY-MM-DD
  用途: 组会 20 分钟汇报 / 小红书图文 / 周报
  sources: ["[[页名A]]", "[[页名B]]"]   # 用到的 wiki 页，写页名即可（跨分类通用）
  ---
  ```
- **不参与 lint / health / 断链检查**：它不是知识层，缺 frontmatter 字段、
  没有 typed link 都正常，agent 不要按 wiki 纪律去规范它。
- **freshness.py 会读它**：被交付物用过的页 = 最强使用信号（比 query 引用更重，
  说明真拿去产出了东西），自动计入静默天数并在看板标 📤。所以 `sources` 值得认真填。
- 产出过程中若形成了**新的知识性判断**（不是措辞裁剪，是真的想明白了什么），
  按 query 的答案落盘规则问一句要不要存成 synthesis 页——回填的是判断，不是文案。
- 迭代版本直接在同一文件里改或另存 v2，git 记录足够，不需要额外机制。

**活来源（raw 里的软链接）**：`python3 scripts/link_raw.py <分类> <文件/文件夹>` 可把
工作台（如 `~/Learning/...`）的文件软链接进 raw/（命名 `linked-<原名>`），原文只维护
一份。pending.py 会检测「原文在上次 ingest 之后被改过」并标 🔁 提议**重新 ingest**
（surgical 更新相关 wiki 页；结论被推翻走 supersession）。纪律不变：**raw 只读对
软链接同样生效——agent 绝不许穿过链接修改工作台原文**；链接是绝对路径仅本机有效，
换机器悬空属预期。

**多模态来源（图片 / PDF / 笔记内嵌图）**：agent 原生能读图，ingest 时**必须用上**——
- 来源本身是图片，或笔记里引用了本地图片（含指向工作台/系统目录的绝对路径）、
  或 PDF 含图表：**逐图查看**，把图中的实质信息（公式与结论、架构图的组件关系、
  表格数据、曲线趋势）蒸馏进相应 wiki 页，行内溯源写 `[source: <来源>, 图N/页N]`。
- epistemic 定级：图中直接可读的数据/公式 = `fact`；对图的解读/推断 = `verified_inference`。
- 图片文件**不复制进 wiki**（wiki 是文字蒸馏层，图留在原处被引用）。
- 纯装饰图、无法辨识的图跳过，并在 `log.md` 注明「跳过图N：原因」——跳过要留痕，不许静默。
- 单批图超过 20 张时分批处理，防止上下文爆炸。

**Codex 注意**：Claude Code 有 SessionStart hook 自动跑 `pending.py`；Codex 没有 hook，
**开工先手动跑 `python3 scripts/pending.py`** 看有无待 ingest 文件。
另外 Codex 更新已有页面时必须 **surgical update**：只改必要段落，不整页重写；
若发现自己的 diff 超出了本次来源涉及的范围，停下说明原因（多工具横评实证
Codex 有整页重写倾向，此约束防止无关内容被顺手改掉）。

## 三个操作（+ 一个可选操作 review）

- **ingest**：处理 `raw/` 里的新内容，更新 `wiki/`
- **query**：基于 `wiki/`（不是 `raw/`）回答问题，附带链接到具体页面；
  **回答后在该分类 `log.md` 追加 `## [日期] query | 引用: [[A]], [[B]]`**
  （列出实际用到的页面——这是冷度监控的「访问强化」数据源，漏记会让页面显得比实际冷）。
  **答案落盘**：若回答做了真正的跨页综合（对比/取舍/新结论，而非单页复述），
  主动问一句「这个分析要不要存成 synthesis 页？」——用户同意才写，且必须满足
  synthesis 页全部纪律（写为什么 + 行内溯源，sources 可含 wiki 页）；单页能答的
  不提议，不为落盘而落盘
- **lint**：检查断链、孤儿页、frontmatter 缺失、潜在矛盾；**并跑 `python3 scripts/health.py`**
  监控规模指标，跨扩展阈值时按下节「扩展触发条件与监控职责」flag 建议；
  **再跑 `python3 scripts/freshness.py`** 生成冷度看板，把「冷藏候选」列给用户裁决
  （归档 / 合并 / 确认仍有用），**绝不自动处置**；
  另做**溯源抽查**：随机抽 3 条标为 `fact` 的关键主张，回 raw 原文核对确实存在——
  防 agent 高估自己的确定性（标错的降级为 verified_inference 并报告）；
  另做**缺口盘点**：对比 raw/ 来源与 `log.md` 的 ingest 记录，列出「进了 raw 但从未
  蒸馏的来源」「明显该有而没有的页」「悬而未决的开放问题」，**覆盖式更新** `index.md`
  的「缺口」小节（无缺口则移除该小节）——缺口是知识库的 known unknowns，
  后续 ingest/query 有机填补；
  完成后在该分类 `log.md` 追加 `## [日期] lint | 摘要` 一行（pending.py 靠它提醒
  「距上次 lint 已 N 次 ingest」）
- **review**（可选，按分类启用——备考/面试类分类才需要）：间隔重复复习，把知识
  背进脑子。`python3 scripts/review.py <分类> enroll` 启用；排期全由脚本管
  （新→7天→30天→90天→毕业；答错回起点 2 天后再来，状态存 `wiki/.review.json`）；
  已启用的分类，每次 ingest commit 后自动重跑 enroll 补录新页；
  agent 只负责出主动回忆题和判卷，**pass/fail 必须基于用户真实作答，不许代答**；
  复习中发现页面有错/过时，不改页面，提醒走 supersession/lint。
  这是「正版遗忘曲线」的用途（训练人脑），与冷度看板（监控注意力）互不混淆。

## 每个 wiki 页面必须有的 frontmatter

```yaml
---
type: entity | concept | synthesis
epistemic_status: fact | verified_inference | hypothesis | speculation
sources: ["[[raw/xxx]]", "..."]
last_confirmed: YYYY-MM-DD
supersedes: null 或 "[[旧页面]]"
superseded_by: null 或 "[[新页面]]"
# ↓ 两个可选字段，需要才写
review_after: YYYY-MM-DD        # 时间敏感页（版本号/行情/岗位类）到期 health.py 提醒复核
lifecycle: stub-intentional     # 故意的占位 stub——孤儿检查豁免，防 lint 误报刷屏
---
```

`review_after` 不是衰减：到期只**提醒**复核，由用户裁决 confirm（刷新 `last_confirmed`）
或 supersede，绝不自动降权。`lifecycle: stub-intentional` 的页面必须真是故意的占位
（如只记引用关系的 stub），不许用它逃避补链接。

不使用数值置信度（不写 `confidence: 0.85` 这种）。可信度靠 `sources` 里列出的
来源数量和 `last_confirmed` 的日期体现，自己从这两点判断，不要求 agent 编一个
数字出来。

`epistemic_status` 的含义：
- `fact`：来源里明确陈述的事实。
- `verified_inference`：从来源推出、且能追溯到具体依据的推断。
- `hypothesis`：有一定依据但未证实的猜想。
- `speculation`：agent 的猜测——**绝不能在下次读取时被当成既定事实**。

## 链接规则

用 Obsidian wikilink，并在链接后用花括号标注关系类型，例如：
`[[GEPA]] {supports}`
`[[AWM]] {contradicts}`
`[[DGM]] {extends}`
关系词库（可按需增加，先用这几个）：`supports / contradicts / extends /
supersedes / same_problem_as / builds_on`

## 跨库互联：只读指针，不共写

分类间的**运维隔离不变**（ingest/lint/阈值/爆炸半径各算各的）。知识层互联用只读指针：

- 页面 frontmatter 可选字段 **`see_also_kb: ["<分类>/<页名>", ...]`**（单行列表），
  正文相关处配一句人话：（另见 <分类> 库「页名」，从什么角度）。**不用 `[[wikilink]]` 跨库**
  ——分库 vault 里点不动，且会污染断链检查。
- **只读铁律**：在 A 库工作时，对其他库**永远只读**——不写、不改、不建页、不动对方的
  链接和 index。想在对方库沉淀内容 = 对那个库单独走一次正常 ingest。
- **query 可以跟指针**去对方库取材，但引用时必须标明「来自 <分类> 库」，不混淆出处域。
- `health.py` 校验指针指向的页真实存在，失效指针按断链对待。
- **密度信号**：指向同一个库的指针 ≥5 个 → 说明分界线可能画错了，lint 时 flag
  「考虑合库或挪页」，是否动由用户决定——指针密度是分类合理性的测量仪。

## 矛盾处理：不自动判定，当研究问题记录

发现两个页面/两个来源冲突时，不要自动选“更新的那个赢”，而是：
1. 两边各自的证据都保留、都写清楚
2. 加一段“这两者可能在什么条件下都成立”的开放问题
3. 在 `log.md` 里标记为待人工复核，不要自己下结论

## 过时处理：supersession，不做衰减

没有“forgetting curve”、没有自动降权。一个页面被新证据推翻时：
1. 旧页面整页保留，顶部加一行“⚠️ 已被 [[新页面]] 取代，原因见下方”
2. 新页面 frontmatter 里 `supersedes` 指回旧页面；旧页面 `superseded_by` 指向新页面
3. 旧的不删除、不隐藏——历史判断本身有价值，尤其是“当时为什么这么想”

**冷度监控（遗忘曲线的去毒实现）**：`scripts/freshness.py` 自动测量每页的
静默天数（距最近被 query 引用或被更新）、未确认天数、反链数，分四层
（活跃/正常/变冷/冷藏候选）输出终端摘要 + `archive/freshness.html` 看板。
**系统只测量、排序、提醒；归档/合并/确认由用户决定。**
**分类活跃度门控**：只有用户持续在用某分类时（近 90 天 ≥5 次 query/ingest），
「这页一直没被用到」才是有效信号；分类整体休眠（90 天 0 次）→ 冷度判定自动暂停，
低活跃（1–4 次）→ 候选只列 TOP5 并标注参考价值有限。**整个分类没在用 ≠ 里面的
知识失效**，回归使用后判定自动恢复。用户裁决「归档」时：
把页面移到 `kb/<分类>/wiki/_archive/`、`index.md` 条目挪到「已归档」小节、
页面顶部加一行“🗄 已冷藏归档（日期），原因”。`_archive/` 不参与 lint/health/
冷度统计，但**检索时不排除**——冷不等于错。

## 页面生命周期维护：merge / archive / verify

三个判断型维护操作（Claude Code 有同名 slash 命令；Codex 直接说「merge X 和 Y」等）：

- **merge**（lint 发现重复/同概念页后）：① 提出方案——保留哪页（内容更全者）、
  从被并页移入哪些独有内容（保留各自 sources 与 epistemic_status）、**全库有哪些
  入链要改写**指向保留页；②用户确认后执行：被并页整页保留，顶部标
  「🔀 已并入 [[保留页]]（日期）」+ `superseded_by`，保留页 `supersedes` 列出被并页，
  改写入链，更新 index；③ 单独 commit：`merge(<分类>): A,B → C`。
- **archive**（冷度看板出「冷藏候选」后）：逐个让用户三选一——**归档**（按
  「过时处理」节的归档动作）/ **合并**（走 merge）/ **确认仍有用**（刷新
  `last_confirmed`）。批量执行，单独 commit：`archive(<分类>): 归档 n / 确认 m`。
- **verify <页>**（`review_after` 到期或用户点名时）：重读该页全部 sources 原文，
  逐条核对关键主张，报告「支持 / 存疑 / 已过时」；用户裁决后：全部成立 → 刷新
  `last_confirmed`（时间敏感页顺延 `review_after`）；有被推翻 → 走 supersession。
  **默认只对照 raw 来源**；需要查外部最新信息时必须先问用户，不得自行联网。

## synthesis 类页面必须记录“为什么”，不只是结论

凡是下判断、做对比、下结论的页面（`synthesis/` 下的），必须包含：
- 比较了哪些选项/来源
- 排除了哪些，为什么排除
- 这个结论成立的前提条件是什么
只写结论、不写推理过程的 synthesis 页面视为不合格，ingest 时要重写。

**防循环自证**：以 wiki 页为主要 sources 的衍生页（query 落盘的综合、跨页对比），
`epistemic_status` 至高标 `verified_inference`、永不标 `fact`；后续任何页面引用
衍生页时，同样不得把它当一手事实——一手性只属于 raw。

另外，synthesis 页的**关键主张必须带行内溯源**：`[source: raw-slug, 位置]`
（位置=页码/小节名/时间戳）。frontmatter 的 `sources` 只到页面级，锚不住
「这句结论到底出自哪」；entities/concepts 页鼓励但不强制。

## 什么时候新建页面 vs 更新已有页面

**建任何新页前，查重是强制步骤**（同类项目实证：600+ 页库的头号病灶就是
同一概念因换了个名字被建了 4~8 个页，且中英文混杂重复）：

1. 用**中英文双语**关键词查现有页面——包括同义词、缩写、中译名/英文原名
   （grep `wiki/` 全文 + 看 `index.md`）。
2. 在 `log.md` 的 ingest 记录里写明「查重：查了哪些词 → 命中/未命中」。
3. **命中同概念页（哪怕页名不同）→ 更新它，不新建**。确有新角度时也先更新
   并加 typed link，等该角度攒够独立内容再考虑拆页。
4. 依然拿不准就记入 `log.md` 待复核；攒够 10~20 次 ingest 后回看，把重复出现的
   判断模式固化进本节。

**procedural 知识不建 wiki 页**：「怎么做某事」（命令、操作步骤、配置流程）的归宿
是 `scripts/`、skill 或本文件的规则，不是知识页。wiki 只收「是什么 / 为什么 /
怎么判断」。

## 明确不做的事（不要自己加，除非我明确要求）

- 不写数值 confidence score
- 不做定时/事件驱动的自动 ingest（每次 ingest 必须是我在场时明确触发的一次性操作）
- 不搭向量数据库 / BM25 混合检索 / 图数据库后端（**暂缓，非永久禁止**；触发条件与监控
  职责见下节「扩展触发条件与监控职责」）
- 不做多 agent 协作、权限分层（单人用）
- 不引入遗忘曲线 / 数值衰减 / 自动降权
- 每次 ingest 处理的原始文件数量不要超过合理审查范围（单次建议不超过 10 个），
  处理完必须停下来等我确认，不要连续处理多批不给我复核的机会

## 扩展触发条件与监控职责（什么时候该上更重的机制）

上一节里被「暂缓」的检索层 / 图后端是**暂缓，不是永久禁止**。为避免「该上时没上、不该上时乱上」，
把判断标准写死在这里，并规定**监控职责**：

> **每次 `lint` 必须跑 `python3 scripts/health.py`**，把它输出的指标与下列阈值比对。
> 一旦跨线，就在 lint 结果里**明确 flag 一条建议**、并追加一行到 `log.md`（`## [日期] 扩展信号 | …`），
> 但**绝不自动实现**——上不上、上哪种，由用户决定。监控 = 提醒，不 = 动手。

### 分级触发（从轻到重，逐级评估，不要跳级）

1. **BM25 / 关键词全文索引**（最先考虑，最轻）。触发（满足任一）：
   - content 页数 **> 100**（观察线）；**> 150**（认真评估线，v2 自承 100–200 才需要）；
   - `query` 时靠 `index.md` + grep 出现漏检（「以为没有相关页、其实有」）累计 **≥ 2 次**并已记入 `log.md`；
   - 同义/近义术语造成概念孤岛（同一概念因措辞不同没连上）反复出现。
   - 落地首选**零重构**方案：Obsidian Omnisearch 插件，或一个 ripgrep + 轻量索引脚本。

2. **向量 / 语义检索 → 混合（BM25 + 向量）**。触发：已上 BM25，但主要漏检变成
   「语义相近、字面不同」（BM25 命中不了）。落地：在现有 markdown 上**叠一层向量索引**，不改目录结构。

3. **图数据库后端**（门槛最高，个人库多半永远到不了）。触发（需**同时**满足）：
   content 页数 **> 300–500**，且确实要跑图算法（关系最短路径、社区发现、按 relation 类型
   程序化查子图），而 Obsidian graph view + Dataview 已扛不住。
   - 注意：绝大多数「按 `{relation}` 查边」的需求 **Dataview 就能满足**，先穷尽 Dataview 再谈图库。

### 永久弃用——监控时若自己「想加」，先停下反问

数值置信度、遗忘曲线 / 衰减、自动 / 定时摄入、多 agent、Router/Planner：**不设触发条件、永不引入**。
若某次工作中觉得「加上会更好」，这通常意味着**某条 schema 纪律没做到位**（如 `epistemic_status`
没标准、synthesis 没写「为什么」、supersession 没及时标）——应去**补纪律**，而不是加机制。
「知道 v2 有更先进的做法」不是把它加回来的理由。

## Git

每次 ingest 完成后单独 commit 一次，commit message 格式：
`ingest: 处理了 <来源摘要>，影响页面 <n> 个`。
这样效果不好可以直接 `git revert` 那一次，不用去 wiki 里手动排查。
