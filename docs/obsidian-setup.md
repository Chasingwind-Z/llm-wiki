# Obsidian 配置指南（手动步骤）

这份文档只收**必须你自己点鼠标的步骤**。仓库里的脚本能装插件、写配置文件，但
Obsidian 的信任提示、浏览器扩展的设置面板、账号登录这些在 GUI 里，agent 代劳不了。

不用 Obsidian 也能用这套知识库（它只依赖文件系统和 git）。以下全部可选。

---

## 一、打开哪个 vault：先想清楚这一步

这是最容易配错、且错了以后到处出怪事的地方。**vault 就是 Obsidian 眼里的"根目录"**，
`[[wikilink]]` 和搜索都相对它解析。

两种开法，按你有几个分类库选：

| 开法 | 做法 | 适合 |
|---|---|---|
| **每分类一个 vault**（推荐） | Open folder as vault → 选 `kb/<分类>/` | 日常读写。页面里的 `[[X]]` 与 `sources` 路径都相对该分类根，无需改写 |
| **整个仓库一个 vault** | Open folder as vault → 选仓库根 | 想跨分类看全局图谱，或要让 Web Clipper 写 `capture/` |

**两种可以同时存在**——Obsidian 允许 vault 嵌套（`kb/llm` 在仓库根 vault 里面）。
好处是想看哪层看哪层，代价见第三节的坑。

注意整个仓库当 vault 时，各分类的 `index.md` / `log.md` 同名，`[[index]]` 会有歧义。
所以日常仍建议按分类开。

**首次打开某个 vault 时 Obsidian 会弹信任提示**（Trust author and enable plugins），
必须点它，否则脚本装好的插件不会加载。每个 vault 各弹一次。

---

## 二、插件：脚本装、你启用

```bash
python3 scripts/setup_obsidian.py
```

它给每个 `kb/<分类>/` vault 装好 Claudian 和 Dataview，并把图谱按
entities / concepts / synthesis 配成三色。装完你要做的：

1. 打开 vault，点 Trust；
2. 设置 → 第三方插件，确认两个插件是启用状态；
3. **Claudian 要单独登录**——它调用你本机的 Claude Code / Codex，第一次用会让你登录
   或授权。如果侧边栏显示未登录且面板里点不动，去终端登录一次再回来（Claudian 复用
   CLI 的登录态，不是独立账号）。

两个 Dataview 查询可以直接贴进任意页面用：

````markdown
```dataview
table review_after where review_after <= date(today)
```
````

````markdown
```dataview
list where epistemic_status = "hypothesis" or epistemic_status = "speculation"
```
````

前者列出到期该复核的页，后者列出还停留在猜想级的结论。

---

## 三、Web Clipper：三个必填项和一个必踩的坑

[Obsidian Web Clipper](https://obsidian.md/clipper) 是浏览器扩展，网页一键剪成
Markdown。它通过 `obsidian://` 协议写进**某个已注册的 vault**，所以配置的关键是
**说清楚写哪个 vault、写到哪个子目录**。

### 配置步骤

1. 浏览器工具栏点 Web Clipper 图标 → 右上角齿轮进设置（或右键扩展图标 →「选项」）；
2. 左侧选 **Templates** → 点你在用的模板（默认叫 `Default`）；
3. 改两个字段：
   - **Vault**：填仓库根 vault 的名字（Obsidian 里登记的那个名字，注意大小写）
   - **Path / Note location**：填 `capture/clips`
4. 设置自动保存，关掉即可。

### ⚠️ 坑：vault 留空 = 写进"上次打开的 vault"

如果你按第一节开了多个嵌套 vault（仓库根 + 各个分类），而 Vault 字段留空，
Clipper 会写进**你最后打开的那个 vault**——通常是某个 `kb/<分类>/`，于是剪藏文件
落进了知识库分类里，而不是 `capture/clips`。文件不会丢，但会出现在不该出现的地方，
下次 lint 时才发现。

**所以 Vault 字段必须显式填写。** 这是嵌套 vault 唯一的实质代价。

另外注意 **Path 是相对 vault 根的**，填 `capture/clips`，不要填
`C:\kb\capture\clips` 或 `/home/you/kb/capture/clips` 这样的绝对路径，会失败。

### 验证

随便剪一篇，然后：

```bash
ls -la capture/clips/
```

出现 `.md` 文件就对了。

### 已知限制：图片仍是远程链接

Clipper 只下正文，图片留的是原站链接（`![](https://...)`）。对图解类文章
（架构图、公式推导图）意味着：**原站一改链接就失效，离线也打不开**。

处理办法二选一：
- 剪完手动把关键图另存到 `capture/clips/<同名>.assets/`；
- 或者干脆不剪，直接把原文另存为 PDF 丢进 `raw/`。

如果这篇材料的价值主要在图上，第二种更稳。

---

## 四、手机上看（可选）

装 **Remotely Save** 或 **Obsidian Git**，同步到 iCloud / WebDAV / 你自己的 git 远端。

建议**手机端只读**：移动场景适合翻和想，不适合做 ingest 这种需要复核的事。真要在
外面采集，用微信 ClawBot 那条链路（见 README「移动采集」一节），它会落进
`capture/`，等你回电脑再分拣。

---

## 五、配完自查

- [ ] 每个要用的 vault 都点过 Trust
- [ ] 图谱有三种颜色（蓝=实体、绿=概念、橙=判断）
- [ ] Dataview 查询能跑出结果（不是显示原始代码块）
- [ ] Clipper 的 Vault 字段**非空**，Path 是相对路径
- [ ] 剪一篇测试，文件确实出现在 `capture/clips/`

哪一步卡住，可以把现象贴给 Claude Code——它读不了你的 GUI，但能查配置文件
（`.obsidian/` 下的 json）确认插件是否真的装上、图谱分组是否写入。
