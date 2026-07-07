# 优化日志

本文档记录用户在开发讨论中提出、但不一定立即进入 MVP 主线的优化项。优化项应尽量保持原始问题语义，并标注当前处理状态，避免后续遗忘或误解。

## 状态说明

- `待处理`：已记录，尚未进入开发。
- `进行中`：已经开始实现或验证。
- `已完成`：已经实现并验证。
- `延后`：暂不处理，等待 MVP 主线完成或依赖条件成熟。

## 优化项

### 2026-06-29 Asia/Shanghai - 前端页面层级模块定向箭头可以优化

状态：已完成

来源：用户在当前 Codex 线程中提出。

原始问题：

- 前端页面层级模块定向箭头可以优化。

当前处理意见：

- 已在 MVP 主线中先实现 Animator 风格暗色网格画布。
- 已将数据流边改为可点击 SVG 箭头。
- 点击箭头后，详情面板展示次级对比页面，分为“上级方法输出”和“下级方法输入”两部分。
- 本轮进一步修复了前端模块乱码，保证箭头、节点和详情组件可继续维护。
- 本轮已为层级流边增加状态化箭头头部、点击选中态、键盘选择热区、并行边 lane 偏移和反向 / 同列边回环路径。
- 后续 UI 细节阶段仍可继续优化整体层级布局、节点拥挤和边标签，但本条“定向箭头可优化”的 MVP 要求已完成。

### 2026-06-29 Asia/Shanghai - 监视窗口输入/输出快照展开状态需要固化

状态：已完成
来源：用户在当前 Codex 线程中提出。
原始问题：
- 监视窗口的输入/输出快照的内容未能固化，展开后短时间内自动折叠。

当前处理意见：
- 已确认根因是监视窗口每 3 秒实时刷新时重建 DOM，导致 `<details>` 默认回到折叠状态。
- 已新增独立的监视展开状态缓存 `flowtrace.watchOpenItems.v1`。
- 已将监视项数据与监视项展开状态解耦：监视项负责“固定看什么”，展开状态负责“当前怎么看”。
- 删除监视项时会同步清理对应展开状态，避免无效状态残留。
- 后续如用户继续要求“内容快照冻结”，可在当前实时监视基础上增加“锁定当前帧 / 跟随最新帧”切换。

### 2026-06-29 Asia/Shanghai - 监视窗口快照刷新导致滚动位置回滚

状态：已完成
来源：用户在当前 Codex 线程中提出。
原始问题：
- 快照内容刷新会导致滚轮自动回滚。

当前处理意见：
- 已确认根因是实时刷新重建快照代码块，导致 `<pre>` 的 `scrollTop` / `scrollLeft` 回到默认值。
- 已新增会话级 `watchScrollItems` 状态，记录每个监视项快照代码块的滚动位置。
- 已在监视卡片重新挂载后恢复滚动位置，避免用户正在阅读堆栈或长 JSON 时被刷新拉回顶部。
- 该滚动位置不写入 `localStorage`，避免跨运行或跨页面刷新时应用过期阅读位置。

### 2026-06-29 Asia/Shanghai - 监视窗口需要支持快照锁定与跟随最新

状态：已完成
来源：MVP 连续完善。
问题背景：
- 监视窗口已经支持展开状态固化和滚动位置保持，但实时刷新仍会替换快照内容。
- 用户在排查长错误堆栈或长 JSON 时，需要临时冻结当前看到的一帧。

当前处理意见：
- 已新增“锁定 / 跟随”按钮。
- 锁定时复制当前输入、输出、输入契约、输出契约与错误信息。
- 跟随后恢复使用实时刷新数据。
- 冻结状态与冻结快照只保存在当前会话，避免跨运行应用过期快照。

### 2026-06-29 Asia/Shanghai - 主视图箭头路由与画布缩放优化

状态：已完成
来源：用户在当前 Codex 线程中提出。
原始问题：
- 有向箭头在模块相互调用时表现不佳。
- 不采用固定输入/输出端口语义，改为用箭头方向解释输出与输入。
- 底部横向滚轴不方便，需要主视图整体缩放，暂定 Ctrl + 滚轮控制，并覆盖浏览器默认缩放冲突。

当前处理意见：
- 已新增 `modules/graph/edge-router.js`。
- 已将层级流转和方法数据流改为动态端口路由：箭头从源节点朝向目标的一侧出发，指向目标朝向源节点的一侧。
- 已增加反向、上下、并行、双向和自循环场景的路由基础。
- 已新增 `modules/graph/viewport.js`。
- 已为层级流转和方法数据流接入 Ctrl + 滚轮缩放、缩放按钮、重置和适应视图。
- Ctrl + 滚轮在画布范围内调用 `preventDefault()`，覆盖浏览器默认页面缩放。

### 2026-06-29 Asia/Shanghai - 主视图直线优先路由与拖拽平移

状态：已完成
来源：用户在当前 Codex 线程中提出。
原始问题：
- 不能只使用独特线条，在某些时候是可以使用直线的，或者表现为直线。
- 新增功能完善用户 UI 交互：用户鼠标应当可以拖拽主视图。

当前处理意见：
- 已将单条边路由调整为直线优先。
- 无 lane 偏移的普通边直接从动态出线点连到动态入线点。
- 并行、双向、偏移和自循环场景仍保留折线/回环，用于避免重叠。
- 已新增主视图空白区域鼠标拖拽平移。
- 拖拽平移会避开节点、边、方法小窗和缩放按钮等已有交互目标。

### 2026-06-29 Asia/Shanghai - 组件页面拖拽停靠布局

状态：已完成
来源：用户在当前 Codex 线程中提出。
原始问题：
- 修改各个窗口的逻辑。
- 监视窗口与详情窗口可以采用上下排列方式。
- 更希望模仿网页：每个页面视为独立组件，能够自由拖拽固定在屏幕上下左右，同时可以像截图一般排列。
- 主要目标是组件页面能够自由拖拽。

当前处理意见：
- 已新增 `modules/ui/dock.js`。
- 已将监视窗口和事件详情窗口改为 `dock-panel`。
- 已将主内容区改为上、下、左、右四个 `dock-zone` 加中心主视图。
- 用户可以拖动组件标题栏，将组件停靠到上、下、左、右区域。
- 同一区域内多个组件按顺序排列；右侧默认保持截图中的纵向排列。
- 组件停靠位置写入 `localStorage`，刷新后保留。

### 2026-06-29 Asia/Shanghai - 撤回负面窗口优化并修正线条策略

状态：已完成
来源：用户在当前 Codex 线程中提出负面评价。
原始问题：
- 上一轮 dock 停靠方案被评价为负面优化。
- 有向线条不应普通边优先直线，而应以节点编辑器分段路由线条为主。
- 仅在上下、左右对齐，或偏差不大时表现为直线。
- 窗口视图应先生成方案供评估微调，不应直接接入主应用。

当前处理意见：
- 已撤回主应用中的 dock 停靠实现，恢复监视窗口与事件详情的稳定右栏布局。
- 已删除 `modules/ui/dock.js`。
- 已将边路由修正为“分段路由为主，近似水平/垂直时直线化”。
- 已新增 `docs/window_view_proposal.html`，作为浏览器页面卡式窗口视图评估稿。

### 2026-06-30 Asia/Shanghai - 窗口视图评估稿标签激活修正

状态：已完成
来源：用户在当前 Codex 线程中对评估稿提出修正。
原始问题：
- 不应出现两个监视窗口。
- 监视窗口标签点击后，应当在下方显示监视窗口页面。
- 其他组件也应采用同样逻辑。

当前处理意见：
- 已将 `docs/window_view_proposal.html` 调整为顶部页面标签 + 下方单一激活页面。
- 顶部标签是组件页面的唯一入口。
- 点击“监视窗口”“事件详情”“契约对比”等标签时，只切换下方页面内容，不额外显示第二个同名窗口。
- “并列/合并预览”保留为后续拖拽合并方案的视觉评估稿，不接入主应用。

### 2026-06-30 Asia/Shanghai - 窗口视图评估稿标签拖拽停靠

状态：已完成
来源：用户在当前 Codex 线程中确认方向后继续补充。
原始问题：
- 对应标签需要能够拖拽固化在工作区。
- 停靠区域包括屏幕上、下、左、右等位置。

当前处理意见：
- 已将 `docs/window_view_proposal.html` 从单一标签栏升级为工作区评估稿。
- 工作区包含上方、左侧、中心、右侧、下方五个停靠区域。
- 拖动页面标签到某个工作区后，标签和对应页面一起迁移。
- 同一组件仍然只存在一份，避免重复监视窗口或重复详情窗口。
- 当前布局写入 `localStorage`，刷新后保留评估稿中的停靠状态。

### 2026-06-30 Asia/Shanghai - 窗口视图评估稿空工作区折叠与二级分区

状态：已完成
来源：用户在当前 Codex 线程中继续校正。
原始问题：
- 工作区不应显式出现。
- 当工作区没有固化标签窗口时，应当被相邻工作区内容使用。
- 当所有标签集中在某一个工作区时，该工作区应当占据整个页面。
- 同一工作区内不应只有标签合并，还需要支持上下关系。
- 页面整体划分工作区后，工作区内部最多再划分一次，只做两层。

当前处理意见：
- 已将 `docs/window_view_proposal.html` 调整为“两层停靠模型”。
- 第一层为整页上、左、中、右、下五个潜在停靠区，但空区默认隐藏且不占位。
- 拖拽时显示临时边缘落点，用于将标签固化到上、下、左、右等一级区域。
- 第二层为单个已存在工作区内部的 `main / secondary` 子区。
- 单个工作区支持“合并 / 左右 / 上下”三种状态。
- 子区只允许存在一层，不继续嵌套第三层。
- 一级边缘落点改为坐标判断，覆盖层只做视觉提示，避免阻挡工作区内部二级拖拽。

### 2026-06-30 Asia/Shanghai - 窗口视图评估稿黑屏兜底修复

状态：已完成
来源：用户在当前 Codex 线程中反馈。
原始问题：
- 打开 `docs/window_view_proposal.html` 后页面全黑。

当前处理意见：
- 已将中心工作区默认内容直接写入 HTML。
- 空的上、左、右、下工作区在 HTML 初始状态下添加 `is-empty`，默认隐藏且不占位。
- 初始 HTML 内联设置中心工作区占满页面，避免脚本未运行时只剩空壳。
- `localStorage` 写入增加异常保护，避免 file:// 环境限制导致渲染中断。
- 初始化增加异常回退：渲染失败时恢复默认中心布局。

补充修复：
- 上一轮兜底仍未在用户浏览器中显示。
- 已将评估页改为静态 DOM 首屏 + JS 增强模式。
- 首屏中心工作区、5 个标签、5 个页面全部直接写在 HTML 中。
- 移除首屏对 `localStorage` 和动态重建布局的依赖。
- 新增右下角固定版本标记 `window-view stable 2026-06-30 00:fix2`，用于判断浏览器是否读到最新文件。

### 2026-06-30 Asia/Shanghai - Unity 式模板命中区与侧栏容器修正

状态：已完成
来源：用户在当前 Codex 线程中继续校正。
原始问题：
- 风格仍然僵硬，颜色对比和锐利度过高。
- 标签不需要 icon，只需要用文字标识区分。
- 标签拖到另一个标签旁边时应合并。
- 标签拖到另一个标签上方时应停靠上方。
- 左右侧栏应作为整块容器，而不是独立散落页面。
- 侧栏容器宽度应可用鼠标调整。
- 侧栏内部页面宽度跟随容器，高度可通过拖拽页面底部调整。
- 左右侧停靠判定区间应限制在左右边框中间约 60%。

当前处理意见：
- 已重写 `docs/window_view_proposal.html` 为更柔和的模板演示。
- 降低整体颜色对比，软化边框和圆角。
- 标签移除 icon，仅保留文字标题和关闭按钮。
- 标签栏附近命中优先执行合并。
- 上、下停靠由面板上缘/下缘触发。
- 左右停靠仅在 `y` 位于 20% 到 80% 且靠近左右边缘时触发。
- 左右停靠不再直接拆分中心布局，而是移动到左/右侧栏容器。
- 侧栏容器支持横向拖拽调整宽度。
- 侧栏内页面支持底部拖拽调整高度。

### 2026-06-30 Asia/Shanghai - 停靠提示隐藏、黑色低对比与二级挂靠规则修正

状态：已完成
来源：用户在当前 Codex 线程中继续校正。
原始问题：
- 显式停靠提示不美观，应在代码上注释掉。
- 次级页面挂靠逻辑需要重构。
- 标签旁边释放应合并。
- 标签上方释放应停靠上方。
- 左右挂靠应直接做在边框边缘，只在边缘释放时生效。
- 前端 UI 对比度仍偏高，考虑直接切换黑色背景。
- 只有一个窗口时，也应能调整窗口大小。

当前处理意见：
- 已将 `.tab-stack.drag-armed .drop-mask` 的显示逻辑注释关闭，保留命中逻辑但不显示大面积停靠提示。
- 已将背景和主要面板色切换到接近黑色的低对比方案。
- 已为 `workspace-root` 补充 `width: 100%; height: 100%;`，避免工作区只按内容宽度铺开。
- 已为中心单窗口添加 `resize: both`，允许用户直接拖拽调整单窗口大小。
- 已调整 `getDropArea(...)`：
  - 标签栏或标签附近释放优先合并。
  - 标签栏上方释放停靠上方。
  - 面板底部释放停靠下方。
  - 左右仅在贴近边框 14px 且位于中间 60% 高度区间时触发。
- 已调整侧栏内部二级挂靠：
  - 侧栏内部仅接受合并、上方、下方。
  - 侧栏内触发左右边缘时，移动到对应左右侧栏容器。

### 2026-06-30 Asia/Shanghai - 窗口边界、侧栏宽度方向与隐形容器修正

状态：已完成
来源：用户在当前 Codex 线程中继续校正。
原始问题：
- 窗口边界不明确，阻碍用户操作。
- 浏览器中侧栏宽度调整方向反了。
- 左右挂靠失败，上方挂靠失败。
- 容器不应有标识，视觉上不应显式存在。
- 减少标签与页面之间通过高对比显示层级，标签颜色与页面颜色统一。

当前处理意见：
- 已移除侧栏容器标题 DOM，仅保留内部页面窗口与拖拽边界。
- 已增强窗口自身边界，弱化容器视觉存在感。
- 已将标签栏、标签和页面标题区域统一为接近同色的低对比背景。
- 已将侧栏宽度调整改为基于容器真实 `left/right` 边界计算，避免方向反。
- 已增加 `dragPointerOffsetY`，用拖拽标签中心点与目标标签栏位置判断合并/上方停靠。
- 已新增 `getStageEdgeDrop(...)`，允许拖到整体工作区左右边缘中段时直接挂靠到对应侧栏。
- 已限制左右边缘命中在整体高度 20% 到 80% 区间。

### 2026-06-30 Asia/Shanghai - 右侧大面积黑色空白原因与布局修复

状态：已完成
来源：用户在当前 Codex 线程中反馈。
原始问题：
- 页面右侧存在大面积黑色空白。

根因判断：
- 外层 `.workspace-stage` 使用 `grid-template-columns: auto 1fr auto`。
- 中心窗口 `.center-host > .tab-stack` 同时启用了 `resize: both`。
- 当中心窗口被浏览器 resize 机制改成较小尺寸后，布局内容按实际窗口宽度收缩，右侧容器跟随内容靠左，剩余区域露出页面黑色背景。

当前处理意见：
- 已将 `.workspace-stage` 从 grid 改为 flex。
- 中心区域 `.center-host` 设置为 `flex: 1 1 auto`，强制吃满左右侧栏之外的剩余宽度。
- 左右侧栏设置为 `flex: 0 0 var(--side-width)`。
- 移除普通状态下中心窗口的 `resize: both`。
- 新增 `.workspace-stage.single-window`，只有无左右侧栏且中心为单个 tab stack 时，才允许中心窗口 `resize: both`。
- 新增 `isSingleWindowState()` 判断，避免有侧栏时中心窗口缩小导致右侧空白。

### 2026-06-30 Asia/Shanghai - 运行视图画布默认铺满修正

状态：已完成
来源：用户在当前 Codex 线程中反馈。
原始问题：
- 运行视图的网格背景被固定在一块区域内，默认没有占据整个视图。

根因判断：
- `graph-canvas` 仍保留示例用的固定 `min-width: 960px` 和 `min-height: 600px`。
- 普通 `.view-body` 统一带有 `14px` 内边距，使运行视图被当成普通信息页处理。
- 运行视图实际应该是主画布页，画布背景需要铺满标签页内容区。

当前处理意见：
- 为运行视图新增 `canvas-view` / `canvas-body` 标记。
- `canvas-body` 取消 padding，并隐藏普通页面滚动外壳。
- `graph-canvas` 改为 `width: 100%`、`height: 100%`、`min-width: 100%`、`min-height: 100%`。
- 保留其他详情页、监视页、日志页的普通 padding 与滚动行为。

验证结果：

```text
inline-script=ok
canvasBody=True
canvasView=True
graphCanvasFill=True
```

### 2026-06-30 Asia/Shanghai - 真实前端只迁移画布铺满功能

状态：已完成
来源：用户在当前 Codex 线程中确认采用，但要求只做功能，不影响项目真实前端页面当前样式。
约束：
- 评估稿中的窗口模板、颜色、边框、标签视觉不直接迁移到真实前端。
- 本轮只处理运行视图默认铺满的功能与尺寸逻辑。

当前处理意见：
- 已在 `modules/graph/viewport.js` 中增加可见区域测量。
- 图数据本身小于容器时，交互 surface 会自动扩展到容器可见宽高。
- 已在 `styles.css` 中只补充布局尺寸规则：`graph-panel` 采用标题行 + 剩余画布区，`animator-canvas` 高度跟随剩余区域。
- 未修改真实前端的配色、字体、边框、圆角、标签视觉样式。

验证结果：

```text
ui-js-syntax=ok
viewportMeasuresVisibleSize=True
surfaceKeepsVisibleMinimum=True
graphPanelUsesRemainingSpace=True
animatorCanvasFillsHeight=True
browser-check=blocked-by-windows-sandbox-spawn-setup-refresh
```

### 2026-06-30 Asia/Shanghai - 真实前端窗口功能迁移与直线路由修复

状态：已完成
来源：用户在当前 Codex 线程中提出。
原始问题：
- 页面窗口相关功能需要发布到真实前端页面，但只做功能迁移，标签样式从简。
- 相互调用的两个模块在复用对齐或轻微偏差时，未能直接使用有向直线链接。

当前处理意见：
- 新增 `modules/layout/workspace-windows.js`，把运行视图、监视窗口、事件详情作为可移动页面窗口管理。
- 默认布局仍保持运行视图在左、监视窗口和事件详情在右侧上下排列。
- 页面标签支持拖拽到目标窗口标签栏合并，也支持按释放位置停靠到目标窗口上、下、左、右。
- 停靠后产生的分割线支持鼠标拖拽调整比例，并持久化到 localStorage。
- 标签样式只保留简洁文字标签，不迁移评估稿中的高对比窗口模板视觉。
- `app.js` 只接入布局安装函数，业务组件 DOM 仍沿用原有 `#graph`、`#watchList`、`#details`。
- `edge-router.js` 将直线判断从 `laneOffset` 接近 0 放宽为端点水平或垂直近似对齐。
- 多条边仍通过 lane 平行错开，但对齐时不再被强制折线化。

验证结果：

```text
ui-js-syntax=ok
edge-route-sample-firstStraight=True
edge-route-sample-secondStraight=True
layoutImported=True
windowModule=True
simpleTabs=True
splitResize=True
browser-check=blocked-by-windows-sandbox-spawn-setup-refresh
```

### 2026-06-30 Asia/Shanghai - 窗口布局恢复入口与本地服务复核

状态：已完成
来源：用户要求继续完善。
处理内容：
- 为真实前端窗口布局增加无 UI 干扰的恢复默认能力。
- 访问 `http://127.0.0.1:8765/?resetWindows=1` 时，会清理窗口布局 localStorage 并恢复默认布局。
- 浏览器控制台可调用 `window.flowtraceResetWorkspaceLayout()` 恢复默认窗口布局。
- 复核本地 viewer 服务时发现 `.venv\Scripts\python.exe` 指向不可用的旧 Python 路径。
- 已改用系统 `D:\Anaconda\python.exe` 在沙箱外启动本地 viewer。

验证结果：

```text
ui-js-syntax=ok
layout-module-http=200
resetQuery=True
resetFunction=True
clearLayout=True
viewer-http=200
```

### 2026-06-30 Asia/Shanghai - 固化开发流程与层级边界

状态：已完成
来源：用户提出“开始，将开发流程固化，不希望后面修 bug 时需要添加新的层级解决 bug”。

处理内容：
- 新增 `docs/PROJECT_FLOW.md`，固化 FlowTrace 从读取项目到运行观测、结构对齐、可视化定位、导出复现的主流程。
- 新增 `docs/ARCHITECTURE_LAYERS.md`，固化 Adapter、Runtime、Instrumentation、Contract/Privacy、Storage、Project Scanner、Analysis、Service API、UI、Export/Diagnostics 等层级边界。
- 新增 `docs/DEVELOPMENT_PROCESS.md`，固化任务进入、bug 修复、新功能、重构、新增层级和验收流程。
- 在 `README.md` 中补充上述文档索引。

关键约束：
- 修 bug 必须先归因，再在归属层内修复。
- 默认不允许为单个 bug 增加新层级。
- 新增层级必须满足稳定职责、复用场景、独立输入输出、独立测试方式和文档更新。
- 后续阶段固定为“项目流程梳理与项目读取层 MVP”，不是直接全面工程化部署。

验证结果：

```text
PROJECT_FLOW.md=exists
ARCHITECTURE_LAYERS.md=exists
DEVELOPMENT_PROCESS.md=exists
default-no-new-layer-rule=True
runtime-fact-priority=True
next-stage-project-reader-mvp=True
```

### 2026-06-30 Asia/Shanghai - 项目读取层 MVP 第一版

状态：已完成
来源：用户要求“开始”，进入项目读取层 MVP。

处理内容：
- 扩展 `scanner.py`，新增 `scan_project(project_root)`。
- Project Scanner 现在输出 `project_model.v1`，包含模块、类、函数、入口候选、import、声明方法和扫描错误。
- 保留 `collect_declared_methods(...)`，内部复用 project model，避免旧层级调用断裂。
- 在 Analysis 层新增 `build_project_coverage(...)`，将静态声明方法与真实运行方法对齐。
- 新增 `/api/project` 与 `/api/project/scan`，返回项目扫描模型。
- 新增 `/api/project/coverage`，返回 `project_coverage.v1`。
- 前端新增“项目结构”视图，展示项目概览、入口候选、模块列表、方法覆盖和扫描错误。
- 更新 README，把项目结构视图和 scanner 职责同步到入口文档。

边界说明：
- 本轮没有引入 LLM。
- 静态扫描只产出候选结构，不宣称真实 workflow。
- 覆盖结果由 Analysis 层计算，前端只负责展示。

验证结果：

```text
python-ast-syntax=ok
ui-js-syntax=ok
project_model.v1=True
project_coverage.v1=True
/api/project=200
/api/project/coverage=200
/modules/components/project.js=200
declared_methods=5
covered_methods=5
scan_errors=0
```

### 2026-06-30 Asia/Shanghai - 运行子视图升级为一级工作区标签

状态：已完成
来源：用户提出“将项目结构、层级流转等标签升级为与运行视图等标签同等的位置，用户能够自由移动标签停靠在任意工作区”。

处理内容：
- 移除运行视图内部的二级视图标签栏。
- 将 `项目结构`、`层级流转`、`方法数据流`、`全量细节`、`问题列表`、`运行对比`、`事件流程` 全部注册为工作区一级标签。
- 上述视图现在与 `监视窗口`、`事件详情` 一样由 `workspace-windows.js` 管理。
- 用户可以拖拽这些一级标签进行合并、上/下/左/右停靠。
- `workspace-windows.js` 默认布局升级为主视图标签组 + 右侧监视/详情。
- 对旧 localStorage 布局做兼容：如果旧布局不包含任何主视图标签，则自动恢复新的默认布局；如果只缺少部分新标签，则自动补回第一个工作区。
- `app.js` 改为为每个主视图维护独立 panel/container，避免多个一级标签共享同一个 DOM 容器。
- `运行对比` 在没有可对比基准运行时只显示空状态，不阻断其他视图渲染。

验证结果：

```text
ui-js-syntax=ok
python-ast-syntax=ok
project_model_api=project_model.v1
app_resource_has_createMainViewPanels=True
app_resource_has_renderMainViews=True
```

### 2026-06-30 Asia/Shanghai - 一级标签重复标识移除与问题列表瘦身

状态：已完成。来源：用户指出“刚更新的标签页面还有额外标识，需要删除；问题列表页面的模块不够美观，过于肥硕，需要物理瘦身”，并补充“并非右侧窄栏阅读密度低，实际上这个标签在任意工作区的阅读密度都不高”。
处理内容：
- 删除一级工作区标签内部重复的二级标题区域，避免出现“标签名 + 页面内重复标题”的双重标识。
- `createMainViewPanels()` 复用原运行视图面板时会移除旧的 `.panel-heading`，新增主视图面板统一使用 `.main-view-panel`。
- `.graph-panel.main-view-panel` 改为单行内容布局，让一级标签页面由工作区标签本身承担页面标识。
- 问题列表按全局阅读密度进行瘦身，而不是只针对右侧窄栏。
- `.issue-list` 使用 `align-content: start` 与 `grid-auto-rows: max-content`，避免卡片在高工作区中被拉伸。
- `.issue-summary` 与 `.issue-card` 缩小 padding、圆角、间距和左侧状态条宽度。
- 问题卡片中当 `kind` 文案与 `title` 完全一致时，不再重复显示，避免“运行异常 运行异常”。

项目结构读取边界：
- 当前“项目结构”不是纯前端假占位，它已经通过后端 scanner/API 返回真实静态扫描结果。
- 但当前扫描根目录来自服务端运行目录；本地开发时服务端运行在 `D:\pyProject\flowtrace-mvp`，因此页面展示的是 FlowTrace 自身结构。
- 真实需求是读取用户目标项目，这一项尚未完成。下一步需要增加项目上下文配置，例如 `flowtrace.config.json`、CLI 参数 `--project` 或前端选择的项目根目录，并让 `/api/project` 从该根目录扫描。

验证结果：
```text
ui-js-syntax=ok
/app.js has main-view-panel=True
/modules/components/issues.js has showKind=True
/styles.css has compact issue-list rules=True
/api/project schema_version=project_model.v1
```

### 2026-06-30 Asia/Shanghai - 项目上下文层第一版

状态：已完成。来源：用户要求“下一步”，延续上一轮关于“项目结构当前读取的是本项目，真实需求是读取用户项目”的讨论。
处理内容：
- 新增 `src/flowtrace/project_context.py`，把“目标项目根目录从哪里来”收敛为独立上下文能力。
- `ProjectContext` 输出 `project_context.v1`，包含 `root`、`source`、`config_file`。
- 支持三种目标项目来源：CLI `--project`、配置文件 `flowtrace.config.json` / `.flowtrace.json`、默认当前启动目录。
- 配置文件支持 `{"project_root": "..."}` 与 `{"project": {"root": "..."}}` 两种结构。
- 配置读取使用 `utf-8-sig`，兼容 Windows PowerShell 生成的 UTF-8 BOM 文件。
- `server.py` 新增 `FlowTraceServer`，把 `project_context` 挂到服务实例上，避免 API 再直接读取 `Path.cwd()`。
- `/api/project/context` 返回当前项目上下文。
- `/api/project` 与 `/api/project/coverage` 改为使用目标项目根目录，并在 project model 中包含 `context`。
- `_method_catalog(...)` 改为使用目标项目根目录收集静态声明方法，运行方法目录与项目扫描口径保持一致。
- 前端“项目结构”视图新增目标项目根目录与来源展示，避免用户误判为固定读取 FlowTrace 自身。
- README 补充 `--project` 与 `flowtrace.config.json` 启动说明。

边界说明：
- 当前已支持“服务启动时指定用户项目根目录”。
- 还未实现“前端选择项目目录并热切换服务上下文”，这属于后续 Project Context UI/Runtime Reload 能力。

验证结果：
```text
python-source-syntax=ok 15
ui-js-syntax=ok
project_context_cli=project_context.v1 source=cli
project_context_config=project_context.v1 source=config
/api/project/context=project_context.v1
/api/project includes context_schema=project_context.v1
/api/project/coverage=project_coverage.v1
viewer-http=200
viewer-listening-pid=59352
```

### 2026-06-30 Asia/Shanghai - 运行对比/事件流程密度修复与 trace 目录上下文

状态：已完成。来源：用户指出“运行对比、事件流程页面的信息密度也偏低，需要瘦身，排查其他页面是否存在相同情况一并解决；然后继续开发”。

视图密度处理：
- 根因定位：多个列表型视图使用 CSS Grid，但未设置 `align-content: start` 与 `grid-auto-rows: max-content`，在大工作区中会把卡片行拉伸成大块空白。
- 为 `.graph`、`.comparison-list`、`.expanded-flow`、`.project-view`、`.project-list`、`.edge-detail` 增加紧凑行布局，禁止空白高度被分配给卡片。
- 压缩通用 `.node`、`.edge-card`、`.comparison-card`、`.expanded-edge`、`.comparison-pane` 的 padding、圆角、左侧状态条和行距。
- 为 `.comparison-card .meta` 补充紧凑 flex 布局，运行对比卡片不再依赖松散默认排版。
- 事件流程复用 `.graph` 与 `.node`，因此同步获得瘦身效果。
- 全量细节复用 `.expanded-flow`、`.expanded-edge`、`.comparison-pane`，因此同步解决同类拉伸问题。

继续开发内容：
- 发现项目结构已绑定 `ProjectContext.root`，但运行记录仍通过默认 `.flowtrace` 读取，真实用户项目下会出现“结构来自用户项目、运行记录来自 viewer 启动目录”的错位。
- 扩展 `ProjectContext`，新增 `trace_dir` 字段。
- trace 目录来源优先级：CLI `--trace-dir`、配置文件 `trace_dir` / `project.trace_dir`、环境变量 `FLOWTRACE_DIR`、默认 `project_root/.flowtrace`。
- `/api/project/context` 现在返回 `trace_dir`。
- `/api/runs`、`/api/runs/{id}/events`、graph、dataflow、layers、compare、issues、summary、project coverage 全部改为使用 `project_context.trace_dir`。
- 前端项目结构页显示“目标项目”和“运行记录”两条路径。
- README 增加 `--trace-dir` 和配置文件 `trace_dir` 示例。

浏览器验证说明：
- 尝试使用 in-app browser 做真实页面检查，但当前环境的浏览器运行时被 Windows sandbox 拦截。
- 已使用 HTTP 静态资源检查与 API 检查替代。

验证结果：
```text
python-source-syntax=ok 15
ui-js-syntax=ok
styles-density-rules=present
project_context.trace_dir=D:\pyProject\flowtrace-mvp\.flowtrace
/api/project/context includes trace_dir=True
/api/runs count=21
/api/runs/{id}/events count=8
/api/runs/{id}/compare comparisons=5
/api/project/coverage=project_coverage.v1
viewer-http=200
viewer-listening-pid=35412
browser-check=blocked_by_windows_sandbox
```

### 2026-06-30 Asia/Shanghai - 接入向导 MVP 与自动审查

状态：已完成。来源：用户要求“开始吧”，进入 Project Onboarding / 接入向导 MVP；随后要求“自动审查”。

实现内容：
- 新增 `src/flowtrace/onboarding.py`，输出 `project_onboarding.v1`。
- 接入建议使用确定性规则生成，不引入 LLM 判断，不自动修改用户项目代码。
- 建议来源包括：扫描错误、入口候选、已声明但未运行覆盖的方法、仅运行时发现的方法、疑似核心流程方法。
- 新增 `/api/project/onboarding`，复用当前 project model 与 project coverage。
- 新增前端 API `getProjectOnboarding()`。
- 新增 `src/flowtrace/ui/modules/components/onboarding.js`，渲染“接入概览”“推荐步骤”“接入建议”。
- “接入向导”升级为一级工作区标签，可像项目结构、层级流转一样自由停靠。
- `workspace-windows.js` 的主标签集合加入 `onboarding`，兼容旧 localStorage 布局自动补入新标签。
- README 增加接入向导与 onboarding 模块说明。

自动审查处理：
- 审查发现 `def your_function(...):` 不适合直接复制，已改为 `def your_function(*args, **kwargs):` 示例。
- 审查发现 `main_guard` 入口不应生成装饰器示例，已改为提示用户在该入口调用的核心函数上接入 `trace_node`。
- 检查旧布局兼容逻辑，确认缺失的新标签会通过 `ensureRegisteredPanels(...)` 自动补入第一个工作区。

验证结果：
```text
python-source-syntax=ok 16
ui-js-syntax=ok
direct_onboarding_schema=project_onboarding.v1
/api/project/onboarding=project_onboarding.v1
onboarding_suggestions=18
onboarding_high_priority=6
main_guard_has_code=False
/modules/components/onboarding.js=200
viewer-http=200
viewer-listening-pid=16568
```

### 2026-06-30 Asia/Shanghai - 接入向导清单化与复制交互

状态：已完成。来源：用户询问“下一步做什么”，在 Project Onboarding MVP 完成后，进入“让接入建议可执行、可追踪”的小闭环。

处理内容：
- 将“接入向导”从只读建议报告升级为本地清单。
- 每条建议支持 `待处理`、`已接入`、`忽略` 三种状态。
- 状态保存到浏览器 `localStorage`，键名为 `flowtrace.onboardingStatuses.v1`，不写入用户项目代码，也不自动修改用户项目。
- 接入概览新增 `已接入`、`忽略` 统计，方便判断当前目标项目还剩多少接入工作。
- 带代码片段的建议新增“复制片段”按钮，优先使用 Clipboard API，失败时回退到 textarea 复制。
- 状态值增加白名单校验，只接受 `pending`、`done`、`ignored`，避免 localStorage 被异常值污染后影响 UI class。
- 复制失败时显示“复制失败”，避免用户误以为片段已复制。
- `app.js` 将 onboarding 最新数据缓存为 `latestOnboarding`，状态改变时只重绘接入向导视图，不触发整页数据重载。

边界说明：
- 当前清单状态只保存在本机浏览器，不进入服务端数据库。
- 这一步仍然坚持“辅助接入，不自动侵入用户代码”的边界。
- 下一步更适合进入“真实用户项目接入闭环”：让用户指定目标项目、生成接入计划、执行一次真实/模拟流程、回收 trace、再用接入向导检查覆盖缺口。

验证结果：
```text
ui-js-syntax=ok
python-source-syntax=ok 16
/api/project/onboarding=project_onboarding.v1
/modules/components/onboarding.js contains status/copy handlers=True
/modules/state.js contains onboarding status whitelist=True
/app.js contains renderOnboardingView=True
/styles.css contains onboarding action/status styles=True
server-api=reachable
```

### 2026-06-30 Asia/Shanghai - 真实项目接入闭环：运行中切换 ProjectContext

状态：已完成。来源：用户确认“可以，开始吧”，进入“真实用户项目接入闭环”的第一步。

处理内容：
- 新增 `POST /api/project/context`，允许 viewer 运行中切换目标项目根目录、trace 目录和可选配置文件。
- 后端收到切换请求后复用 `load_project_context(...)` 做路径解析与校验，目标项目不存在时返回 400。
- 切换成功后替换 server 内部的 `ProjectContext`，后续 `/api/project`、`/api/project/coverage`、`/api/project/onboarding`、`/api/runs` 以及运行分析 API 都会读取新的上下文。
- 返回 payload 仍为 `project_context.v1`，成功切换后的 `source` 标记为 `runtime`。
- 前端 API 新增 `setProjectContext(payload)`，统一通过 JSON POST 调用后端。
- `项目结构` 页面新增“项目接入”区块，包含目标项目、运行记录、配置文件三个输入框和“应用项目”按钮。
- 应用项目后，前端会清空当前运行选择、刷新运行列表、刷新项目结构和接入向导。
- 项目接入区块明确提示“只切换 FlowTrace 读取上下文，不修改目标项目代码”。
- 修复一次自动审查发现的后端缩进问题：`self._serve_static(path)` 曾被误缩进到 `/summary` 分支的 `return` 之后，导致静态页面空响应；已恢复为 `do_GET` 的最终 fallback。
- README 增加“运行中切换目标项目”说明。

边界说明：
- 该能力属于 Service API 层和 UI 层的上下文切换，不新增分析层级。
- 后端只校验目标项目根目录存在；trace 目录允许不存在，因为新项目第一次运行前可能还没有 `.flowtrace/runs`。
- 当前仍不自动修改用户项目代码；接入仍通过接入向导建议、用户复制片段或后续 adapter 完成。

验证结果：
```text
python-source-syntax=ok 16
ui-js-syntax=ok
GET /=200
POST /api/project/context=project_context.v1 source=runtime
POST invalid project=400
GET /api/runs count=21
/modules/components/project.js contains project-context-form=True
viewer-listening-pid=48260
```

### 2026-06-30 Asia/Shanghai - 项目接入路径改为 Windows 原生选择器

状态：已完成。来源：用户要求“添加文件选择器让用户显式选择，而非提供文件路径”，并明确参考 Windows 文件选择窗口，要求用户能够逐步进入文件目录进行选择。

处理内容：
- 新增 `POST /api/fs/dialog`，由后端触发 Windows 原生选择窗口。
- `目标项目`、`运行记录` 使用 Explorer 风格 `OpenFileDialog` 作为目录选择器：用户逐级进入目标目录后点击打开，后端取当前目录作为路径。
- `配置文件` 使用 Explorer 风格文件选择器，只过滤展示 `.json` 配置和所有文件。
- 前端 `项目结构 -> 项目接入` 中每个路径输入框旁新增 `选择` 按钮。
- 点击 `选择` 后前端显示“请在系统窗口中选择路径”，选择完成后把绝对路径写回输入框。
- 用户仍需点击 `应用项目` 才会切换 ProjectContext，选择路径本身不触发扫描或切换。
- 移除未使用的网页内目录浏览接口，避免项目接入存在“网页浏览路径”和“系统选择路径”两套逻辑。
- README 补充原生选择器使用方式。

边界说明：
- 原生选择窗口通过本地后端 PowerShell STA 进程打开，只读路径，不写入用户项目。
- 自动验证不会真实打开选择窗口，因为该窗口需要人工操作；验证覆盖语法、静态资源发布和错误类型返回。
- 该能力仍属于 Service API 层和 UI 层，不新增独立工程层级。

验证结果：
```text
python-source-syntax=ok 16
ui-js-syntax=ok
GET /=200
/modules/api.js contains openPathDialog=True
/modules/components/project.js contains data-path-picker=True
POST /api/fs/dialog invalid kind=400
viewer-listening-pid=51732
```

### 2026-06-30 Asia/Shanghai - 原生选择窗口无法唤起的前后台边界修正

状态：已完成。来源：用户反馈“真实前端无法唤起窗口选择器是否正常”。

判断：
- 这不是最终产品里的正常体验。
- 但在当前 MVP 技术路径下可解释：浏览器前端不能直接拿本地绝对路径，因此原生窗口由本地后端进程打开；如果后端由隐藏进程、沙箱进程或非前台交互会话启动，窗口可能没有浮到前台，用户会感觉“没有唤起”。

处理内容：
- 保持现有架构：前端按钮 -> `POST /api/fs/dialog` -> 本地后端打开 Windows 原生选择窗口。
- 为 PowerShell WinForms 选择器增加置顶 owner 窗口。
- `OpenFileDialog.ShowDialog()` 改为 `ShowDialog($owner)`，降低窗口出现在浏览器背后或被隐藏父进程影响的概率。
- 文件选择和目录选择的 Explorer 风格窗口都使用同一置顶 owner 逻辑。

边界说明：
- 自动验证不触发真实选择窗口，因为它需要人工点击。
- 如果仍无法弹出，下一步应检查 viewer 是否运行在当前用户的交互桌面会话；不要把问题归因到浏览器 DOM。

验证结果：
```text
python-source-syntax=ok 16
GET /=200
POST /api/fs/dialog invalid kind=400
server.py contains TopMost owner=True
viewer-listening-pid=57680
```

### 2026-06-30 Asia/Shanghai - 工作区标签视觉与拖拽停靠微调

状态：已完成。来源：用户提出三项前端 UI 微调：标签与页面之间横线需要优化；同一标签组内应能拖拽改变相对顺序；底部停靠应以当前可见视窗底部为判定区域。

处理内容：
- 优化标签与页面之间的视觉连接：活动标签使用面板背景色、提高层级，并通过 `margin-bottom: -1px` 遮住活动标签下方边线。
- 工作区内容面板左上角在标签接壤处取消圆角，减少“标签悬浮在页面外”的割裂感。
- 新增同组标签重排逻辑：拖动标签到另一个标签左半边时插到其前面，拖到右半边时插到其后面。
- 跨工作区合并到标签栏时，也会按照释放位置插入，而不是总是追加到末尾。
- 拖到页面正文中央时只激活该标签，不再误触发重排。
- 底部停靠逻辑改为当前 pane 与浏览器视窗的可见底边判断，而不是只能拖到整个页面最底部。
- 新增 `BOTTOM_VISIBLE_EDGE_PX = 76` 作为可见底部停靠区域，适配页面滚动后只露出局部工作区的情况。

边界说明：
- 该修改只影响 `workspace-windows.js` 和工作区样式，不改变业务视图、运行分析或 ProjectContext。
- 底部停靠仍保留左右/上方停靠的现有判断规则；只是将 bottom 的触发位置从完整 pane 底部改为可见底边。

验证结果：
```text
ui-js-syntax=ok
GET /=200
/modules/layout/workspace-windows.js contains tabInsertIndex=True
/modules/layout/workspace-windows.js contains reorderPanel=True
/modules/layout/workspace-windows.js contains isVisibleBottomDock=True
/styles.css contains active tab seam rules=True
```

### 2026-06-30 Asia/Shanghai - 页面随标签整体拖动验证模板

状态：已完成模板。来源：用户要求“拖动标签时对应页面应当随之拖动，类似 Edge 浏览器页面，直接移动页面与标签，而非现在表现类似复制删除的样式”，并要求先给出理解模板进行验证。

处理内容：
- 新增 `docs/workspace_drag_template.html`，作为独立交互验证模板，不直接改动真实前端工作区逻辑。
- 模板把标签和页面视为同一个页面实例：拖动标签时生成随鼠标移动的页面预览，原标签位置留下占位，不表现为复制/删除。
- 支持同一标签组内按释放位置重排：拖动到目标标签左半侧插入其前方，拖动到右半侧插入其后方。
- 支持释放到当前 pane 边缘进行停靠：上、下、左、右停靠会把页面实例移动到对应工作区。
- 使用统一的布局状态模型 `state.zones`，避免用硬编码 DOM 位置模拟结果。

边界说明：
- 该模板仅用于讨论和验证“拖动手感与语义”，暂不影响 `src/flowtrace/ui` 真实前端页面。
- 模板中的停靠提示为验证用轻量提示，后续迁移到真实前端时可以继续按用户偏好弱化或取消显式提示。

验证结果：
```text
template=D:\pyProject\flowtrace-mvp\docs\workspace_drag_template.html
file-created=True
contains startDrag=True
contains finishDrag=True
contains moveToZone=True
contains floating-page=True
contains tab-placeholder=True
```

### 2026-06-30 Asia/Shanghai - 跳过页面随标签整体拖动优化

状态：已跳过。来源：用户明确要求“跳过本次优化，写入优化日志，我们继续开发项目”。

处理内容：
- 保留 `docs/workspace_drag_template.html` 作为讨论验证模板，不迁移到真实前端。
- 暂停“拖动标签时页面整体跟随移动”的交互实现。
- 真实前端继续维持当前工作区拖拽、重排、停靠逻辑，不为本次模板新增工程代码。

后续方向：
- 工作重心回到 FlowTrace 项目主线：真实项目接入、项目结构分析、运行记录读取、参数流追踪与自动审查能力。
- 后续如重新评估该交互，再基于已保留模板继续讨论，不在当前阶段消耗 MVP 开发节奏。

### 2026-06-30 Asia/Shanghai - 真实项目读取结构摘要增强

状态：已完成。来源：用户要求跳过标签拖动优化并继续开发项目，当前主线回到真实项目接入与项目结构读取。

处理内容：
- 在现有 `scanner.py` 内增强项目模型，不新增工程层级。
- `/api/project` 新增 `project_identity`：包含目标项目名称、根路径、顶层 Python 包候选。
- `/api/project` 新增 `file_summary`：包含文件总数、Python 文件数、顶层目录文件统计、文件类型分布、常见项目标记文件、框架/库导入线索。
- 项目结构页新增“项目结构摘要”区块，用于展示项目身份、项目标记、技术线索、文件类型与顶层目录摘要。
- 项目概览增加“文件”指标，帮助用户确认当前读取的是目标项目上下文，而不是 FlowTrace 自身占位数据。

边界说明：
- 该功能仍属于现有静态扫描层，不写入、不修改用户项目代码。
- 框架线索来自确定性文件和 import 名称，不使用 LLM 推断，不作为最终调用关系依据。
- 真实调用关系仍以运行记录为准，静态结构只提供候选上下文。

验证结果：
```text
scanner ast ok
python ast ok 14
project.js node --check ok
scan_project sample={"files":77,"identity":"flowtrace-mvp","markers":2,"frameworks":[],"top_level":5}
server restarted pid=56952
/api/project files=77
/api/project has project_identity=True
/api/project has file_summary=True
frontend project.js contains renderProjectSummary=True
frontend styles.css contains project-summary-grid=True
browser verification skipped: in-app browser connection was interrupted by local sandbox
```

### 2026-06-30 Asia/Shanghai - 新增仿真实项目测试样本

状态：已完成。来源：用户确认继续下一步后，按“先准备可控仿真实项目，再引入开源/真实项目”的测试路线推进。

处理内容：
- 新增 `examples/realistic_projects/ecommerce_checkout`，模拟订单提交项目，覆盖前端表单、API、服务、仓储层级传参。
- 新增 `examples/realistic_projects/inventory_cli`，模拟 CLI 库存调拨项目，覆盖脚本入口、业务校验、库存写入。
- 新增 `examples/realistic_projects/support_ticket`，模拟异步客服工单项目，覆盖 async workflow、分类、派单。
- 新增 `docs/REALISTIC_SAMPLE_PROJECTS.md`，记录三个样本的目标、路径、运行方式、viewer 接入方式和当前验证结果。
- 每个样本都有独立 `pyproject.toml`、README、包目录、入口文件和业务模块，可作为用户项目被 FlowTrace viewer 选择。

边界说明：
- 样本位于 FlowTrace 仓库内，但目录结构按外部用户项目模拟；viewer 接入时应选择具体样本根目录，而不是 FlowTrace 根目录。
- 样本运行会在各自项目根目录写入 `.flowtrace`，用于测试项目结构扫描和运行记录读取的闭环。
- 样本不引入外部依赖，避免工程化测试被依赖安装阻塞。

验证结果：
```text
sample python ast ok 16
ecommerce_checkout scan: files=9 modules=7 functions=6 declared_methods=5 scan_errors=0
inventory_cli scan: files=6 modules=4 functions=8 declared_methods=5 scan_errors=0
support_ticket scan: files=7 modules=5 functions=7 declared_methods=4 scan_errors=0
ecommerce_checkout run: 1 run, 14 events, 5/5 covered
inventory_cli run: 1 run, 14 events, 5/5 covered
support_ticket run: 1 run, 12 events, 4/4 covered
runtime_only_methods=[]
```

### 2026-06-30 Asia/Shanghai - 接入状态模型与边界审查

状态：已完成。来源：用户要求“开始，同时审查项目结构是否边界清晰，约束是否强力”。

处理内容：
- 新增 `src/flowtrace/readiness.py`，作为 Analysis 层的接入状态模型，不新增工程层级。
- 新增 `GET /api/project/readiness`，聚合 project model、coverage、runs、issues，输出项目接入状态。
- `readiness` 输出内容包括：项目状态、检查项、workflow 候选、已覆盖/未覆盖/运行时孤儿/缺契约方法、高风险边界、下一步建议。
- 扩展 `scanner.py` 输出 `traced_methods` 与 `contract_methods`，保留原有 `declared_methods` 兼容字段，用于稳定判断“追踪方法是否缺 contract”。
- 前端 `接入向导` 顶部新增“接入状态”区块，展示当前项目是否可用于排查、方法覆盖、缺契约数量、错误/警告、检查项和下一步动作。
- 新增 `tools/verify_realistic_samples.py`，把三个仿真实项目固化为自动验收对象。
- 更新 `docs/ARCHITECTURE_LAYERS.md`，明确 `onboarding` 与 `readiness` 属于 Analysis 层，只能消费确定性结果，不允许替代用户做最终 workflow 决策。

边界审查结论：
- 当前层级边界基本清晰：`scanner` 负责静态项目模型，`interpretation` 负责运行解释，`readiness` 负责聚合判断，`server` 负责 API 组织，`UI` 只负责展示。
- 本次没有把判断规则写入前端，也没有把业务判断塞进 `server.py`，约束方向正确。
- 约束仍需继续增强：后续所有“是否可接入”的判断应优先写入 `readiness.py`，不要散落到 onboarding 或 UI；后续所有“样本是否可用”的验证应优先进入 `tools/verify_realistic_samples.py`。

验证结果：
```text
python ast ok 16
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
ecommerce_checkout readiness: partial, 5/5 covered, 1 missing contract
inventory_cli readiness: risky, 5/5 covered, 1 missing contract, 1 error
support_ticket readiness: partial, 4/4 covered, 1 missing contract
server restarted pid=36868
/api/project/readiness status=risky checks=8 actions=3
runtime context switch to ecommerce_checkout readiness=partial known=5 covered=5
frontend static resources contain getProjectReadiness/renderReadiness/readiness-hero=True
browser visual verification skipped: in-app browser connection interrupted by local sandbox
```

### 2026-07-01 Asia/Shanghai - Runner 启动开关策略

状态：已完成。来源：继续项目开发，按固定流程在 Dry-run Runner 之后补充真实执行显式开关策略。

处理内容：
- 新增 `src/flowtrace/runner_launch_control.py`，输出 `project_runner_launch_controls.v1` 和 `runner_launch_control_schema.v1`。
- 新增只读 API `/api/project/runner-launch-controls`。
- 前端接入向导新增“Runner 启动开关”只读区块。
- 扩展 `tools/verify_realistic_samples.py`，覆盖启动开关状态、安全断言和 `launchable_count=0`。

边界说明：
- 本次仍不实现真实 runner。
- 没有新增 POST API。
- 没有新增存储文件。
- 即使 dry-run 已完成，真实 runner 启动仍被策略禁用。

验证结果：
```text
python ast ok 52
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-launch-controls schema=project_runner_launch_controls.v1
status=disabled_by_policy
launchable_count=0
launch_api_available=False
launch_enabled=False
executes=False
creates_process=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续步骤：
```text
1. 细化 stdout/stderr 分片、最大日志大小、尾部摘要和前端展示策略。
2. 设计取消、超时和完成刷新机制。
3. 设计未来真实执行开关所需的配置文件字段和服务启动参数，但仍保持默认禁用。
4. 审计通过后再接入可选真实执行。
```

### 2026-07-01 Asia/Shanghai - Runner 会话草案与事件 schema

状态：已完成。来源：继续项目开发，按照固定开发流程进入 runner 最小不可执行骨架。

处理内容：
- 新增 `src/flowtrace/runner_session_store.py`，用于保存 runner 会话草案。
- 新增 `src/flowtrace/runner_session.py`，输出 `project_runner_sessions.v1` 和 `runner_event_schema.v1`。
- 新增 `/api/project/runner-sessions`、`/api/project/runner-sessions/prepare`、`/api/project/runner-sessions/remove`。
- 前端接入向导新增“Runner 会话草案”区块，展示事件 schema、事件类型、草案状态和安全动作。
- 扩展 `tools/verify_realistic_samples.py`，覆盖 runner 会话草案生成、移除和安全断言。

边界说明：
- 本次仍不实现真实 runner。
- 生成 runner 会话草案不会执行命令，也不会创建进程。
- 只允许基于已二次确认的执行请求生成 runner 会话草案。
- `runner_session` 层只能负责会话草案和事件 schema，不能承担 subprocess 执行职责。

验证结果：
```text
python ast ok 47
python compileall blocked by pycache PermissionError in local environment
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-sessions schema=project_runner_sessions.v1
event_schema=runner_event_schema.v1
runner_session_after_prepare=drafted
runner_session_after_request_revoke=stale
runner_session_after_remove=none
executes=False
creates_process=False
runner=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续步骤：
```text
1. 设计启动前快照。
2. 设计真实 runner API 的 dry-run 边界。
3. 设计取消、超时、stdout/stderr 分片和结束刷新策略。
4. 审计通过后再接入真实进程启动。
```

### 2026-07-01 Asia/Shanghai - 启动前快照

状态：已完成。来源：继续项目开发，按固定流程在 Runner 会话草案之后补充启动前一致性证据层。

处理内容：
- 新增 `src/flowtrace/runner_launch_snapshot_store.py`，用于保存启动前快照。
- 新增 `src/flowtrace/runner_launch_snapshot.py`，输出 `project_runner_launch_snapshots.v1` 和 `runner_launch_snapshot_schema.v1`。
- 新增 `/api/project/runner-launch-snapshots`、`/api/project/runner-launch-snapshots/prepare`、`/api/project/runner-launch-snapshots/remove`。
- 前端接入向导新增“启动前快照”区块，展示快照 schema、证据摘要、快照状态和安全动作。
- 扩展 `tools/verify_realistic_samples.py`，覆盖快照生成、上游会话移除后的 stale 状态、移除和安全断言。

边界说明：
- 本次仍不实现真实 runner。
- 生成启动前快照不会执行命令，也不会创建进程。
- 启动前快照只能基于已生成的 runner 会话草案创建。
- `runner_launch_snapshot` 层只能负责一致性证据封存，不能承担 subprocess 或 dry-run 执行职责。

验证结果：
```text
python ast ok 49
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-launch-snapshots schema=project_runner_launch_snapshots.v1
snapshot_schema=runner_launch_snapshot_schema.v1
runner_launch_snapshot_after_prepare=snapshotted
runner_launch_snapshot_after_session_remove=stale
runner_launch_snapshot_after_remove=none
executes=False
creates_process=False
launch_enabled=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续步骤：
```text
1. 设计 dry-run runner API。
2. dry-run runner API 只消费启动前快照，不启动真实进程。
3. 设计执行日志目录、stdout/stderr 分片、取消、超时和完成刷新策略。
4. 审计通过后再考虑真实进程启动。
```

### 2026-07-01 Asia/Shanghai - Dry-run Runner API

状态：已完成。来源：继续项目开发，按固定流程在启动前快照之后补充 dry-run runner 层。

处理内容：
- 新增 `src/flowtrace/runner_dry_run_store.py`，用于保存 dry-run runner 记录。
- 新增 `src/flowtrace/runner_dry_run.py`，输出 `project_runner_dry_runs.v1` 和 `runner_dry_run_schema.v1`。
- 新增 `/api/project/runner-dry-runs`、`/api/project/runner-dry-runs/prepare`、`/api/project/runner-dry-runs/remove`。
- 前端接入向导新增“Dry-run Runner”区块，展示 dry-run schema、生命周期预览、日志计划和安全动作。
- 扩展 `tools/verify_realistic_samples.py`，覆盖 dry-run 生成、上游快照移除后的 stale 状态、移除和安全断言。

边界说明：
- 本次仍不实现真实 runner。
- 生成 dry-run runner 记录不会执行命令，也不会创建进程。
- dry-run 只规划日志路径，不创建 stdout/stderr 日志文件。
- dry-run runner 只能基于已生成的启动前快照创建。
- `runner_dry_run` 层只能负责 dry-run 报告、schema 和日志计划，不能承担 subprocess 职责。

验证结果：
```text
python ast ok 51
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-dry-runs schema=project_runner_dry_runs.v1
dry_schema=runner_dry_run_schema.v1
runner_dry_run_after_prepare=prepared
runner_dry_run_after_snapshot_remove=stale
runner_dry_run_after_remove=none
planned_logs=True
executes=False
creates_process=False
launch_enabled=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续步骤：
```text
1. 设计真实 runner 显式开关，默认禁用。
2. 细化 stdout/stderr 分片、最大日志大小、尾部摘要和前端展示策略。
3. 设计取消、超时和完成刷新机制。
4. 审计通过后再接入可选真实执行。
```

### 2026-07-01 Asia/Shanghai - Runner 隔离设计报告

状态：已完成。来源：继续项目开发，从最终执行确认门推进到独立 runner 设计，但仍不实现命令执行。

处理内容：
- 新增 `src/flowtrace/runner_plan.py`，输出 `project_runner_plan.v1`。
- 新增 `GET /api/project/runner-plan`。
- 前端接入向导新增“Runner 隔离设计”区块。
- Runner 设计报告展示隔离策略、生命周期状态、计划日志路径和失败回收策略。
- 扩展 `tools/verify_realistic_samples.py`，把 runner plan 纳入真实样例验收。

边界说明：
- 当前仍没有 runner。
- 当前不会启动目标项目命令。
- Runner plan 只消费 run profile 和最终执行门状态，不修改用户项目。
- 前端不提供执行按钮，只展示设计报告。
- 后续真实执行必须单独经过 runner 边界审计，不能绕过预检确认和最终确认。

验证结果：
```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-plan schema=project_runner_plan.v1
runner_plan_after_final_confirm=ready_for_runner_implementation
runner plan executes_commands=False
runner plan runner_implemented=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续开发标记：
```text
下一轮可以做 runner 最小骨架或执行请求草案存储，但仍不应直接执行命令。
必须先补二次确认 UI、执行日志写入策略和进程生命周期事件结构。
```

### 2026-07-01 Asia/Shanghai - 执行请求草案与二次确认

状态：已完成。来源：继续项目开发，从 runner 隔离设计推进到执行请求草案和二次确认 UI，仍不执行命令。

处理内容：
- 新增 `src/flowtrace/execution_request_store.py`，保存执行请求草案和二次确认状态。
- 新增 `src/flowtrace/execution_request.py`，输出 `project_execution_requests.v1`。
- 新增 `GET /api/project/execution-requests`。
- 新增 `POST /api/project/execution-requests/prepare`。
- 新增 `POST /api/project/execution-requests/confirm`。
- 新增 `POST /api/project/execution-requests/revoke`。
- 新增 `POST /api/project/execution-requests/remove`。
- 前端接入向导新增“执行请求草案”区块。
- 扩展 `tools/verify_realistic_samples.py`，覆盖准备草案、二次确认、撤销、移除全流程。

边界说明：
- 当前仍没有 runner。
- 当前不会启动目标项目命令。
- 执行请求草案和二次确认只写入 FlowTrace trace 目录。
- 二次确认不等于执行动作；后续真实执行仍需单独 runner API。

验证结果：
```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/execution-requests schema=project_execution_requests.v1
prepared=prepared
confirmed=second_confirmed
revoked=prepared
removed=none
executes=False
runner=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续开发标记：
```text
下一轮可实现 runner 最小不可执行骨架和 runner 事件 schema。
真实执行仍需等待 runner 骨架、事件日志、取消/超时策略、前端执行按钮和自动验收全部过审。
```

### 2026-07-01 Asia/Shanghai - 最终执行确认门

状态：已完成。来源：继续项目开发，沿既定流程从“预检确认状态”推进到“最终执行确认门”，仍不实现命令执行。

处理内容：
- 新增 `src/flowtrace/run_final_confirmation_store.py`，负责保存、读取、撤销最终执行确认记录。
- 新增确认存储文件 `run_final_confirmations.json`。
- 新增 `src/flowtrace/run_execution_gate.py`，输出 `project_run_execution_gate.v1`。
- 新增 `GET /api/project/run-execution-gate`。
- 新增 `POST /api/project/run-execution-gate/confirm`。
- 新增 `POST /api/project/run-execution-gate/revoke`。
- 前端接入向导新增“最终执行确认”区块，展示最终确认状态、阻断项、安全边界和确认/撤销按钮。
- 扩展 `tools/verify_realistic_samples.py`，把最终执行门纳入真实样例和保存状态验收。

边界说明：
- 最终确认只表示“用户已复核运行配置与预检确认状态”，不执行命令。
- 预检未确认、预检失效或预检阻断时，最终确认被阻断。
- 最终确认记录绑定 run profile 指纹、预检状态、预检确认状态和检查项；任一关键条件变化后需要重新确认。
- 新模块不扫描项目、不修改用户项目、不生成 runner。

验证结果：
```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/run-execution-gate schema=project_run_execution_gate.v1
API save profile -> confirm preflight -> confirm final -> revoke final -> revoke preflight -> remove profile ok
final gate executes_commands=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续开发标记：
```text
下一轮工程主线应进入独立 runner 设计，但必须先明确执行隔离、日志结构、进程生命周期、失败回收和前端最终执行按钮的二次确认。
禁止将命令执行逻辑写入 run_profile、run_preflight、run_confirmation_store 或 run_final_confirmation_store。
```

### 2026-07-01 Asia/Shanghai - 前端层级流转画布批量编辑优化记录

状态：待开发。来源：用户提出“层级流转页面的模块应当能够被批量框选，进行对齐操作，用户也应当能够对模块进行微调”。

优化内容：
- 层级流转页面中的模块节点需要支持批量框选。
- 用户应能够通过拖拽选区一次性选择多个模块节点。
- 被选中的多个模块节点应支持对齐操作，例如左对齐、右对齐、上对齐、下对齐、水平居中、垂直居中。
- 被选中的多个模块节点应支持等距分布操作，例如水平等距、垂直等距。
- 用户应能够对单个模块或选中模块进行微调。
- 微调方式建议支持键盘方向键移动；后续可扩展为 `Shift + 方向键` 大步长移动、`Alt + 方向键` 小步长移动。
- 微调与批量对齐后的节点位置需要继续复用现有节点位置持久化机制，避免刷新后布局丢失。

边界说明：
- 该优化属于前端层级流转画布交互，不应改变后端运行分析、数据流解释或项目扫描逻辑。
- 该优化应复用现有节点拖拽与位置持久化能力，不应新增与业务分析无关的后端层级。
- 批量编辑只改变用户画布布局，不改变真实项目结构、不改变运行记录、不改变参数流判断。

后续实现建议：
```text
1. 在层级流转画布中增加 selection state，记录当前选中节点 id 集合。
2. 在画布空白区域实现 marquee selection 框选。
3. 在节点点击逻辑中支持单选、Ctrl 多选、框选合并选择。
4. 增加 alignment commands，统一处理选中节点坐标。
5. 增加 keyboard nudge handler，用于方向键微调选中节点。
6. 对齐、分布、微调完成后调用现有 persistNodePositions。
7. 补充前端静态检查与人工视觉验证。
```

### 2026-07-01 Asia/Shanghai - Run Profile 保存/恢复闭环

状态：已完成。来源：用户要求继续项目开发，并明确后续开发需要保持边界、硬性约束、自动审计和文档更新。

处理内容：
- 新增 `src/flowtrace/run_profile_store.py`，负责读取、保存、取消保存 trace 目录下的 `run_profiles.json`。
- `GET /api/project/run-profiles` 现在返回草案 profile 的保存状态、保存时间、保存数量和存储元信息。
- 新增 `POST /api/project/run-profiles/save`，只接收 `profile_id`，由后端从当前确定性草案中查找并保存。
- 新增 `POST /api/project/run-profiles/remove`，按 `profile_id` 取消保存。
- 前端“运行配置草案”区块增加“保存草案 / 取消保存”按钮和“已保存 / 未保存”状态。
- 扩展 `tools/verify_realistic_samples.py`，使用临时目录验证 run profile store 的保存、标记、取消保存闭环。
- 新增 `docs/AUTO_AUDIT_REPORT.md`，记录本轮自动审计报告。

边界说明：
- 保存接口不接受任意命令内容，只接受 `profile_id`。
- 保存的 profile 必须来自后端当前生成的 run profile 草案。
- 当前能力只写入 FlowTrace trace 目录下的 `run_profiles.json`，不修改用户源码。
- 当前没有命令执行接口、没有执行按钮、没有 runner。
- 后续如果实现执行能力，必须进入独立 runner 层，并经过安全预检和用户确认。

验证结果：
```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
run_profile_store saved_count_after_save=1
run_profile_store profile_saved_flag=True
run_profile_store saved_count_after_remove=0
GET /api/project/run-profiles schema=project_run_profiles.v1
GET /api/project/run-profiles storage=run_profile_store.v1
API save/remove with temporary trace dir ok
```

下一轮开发：
```text
执行前安全预检。目标是为已保存 run profile 生成可审查的 preflight report，显示工作目录、argv、环境变量、trace 目录、入口文件、潜在写入风险和确认状态；仍不执行命令。
```

### 2026-07-01 Asia/Shanghai - 执行前安全预检

状态：已完成。来源：上一轮 Run Profile 保存/恢复闭环完成后的下一轮工程主线；用户要求完成本轮后暂停并总结前两轮。

处理内容：
- 修复 `run_profile.py` 的 `FLOWTRACE_DIR` 生成逻辑，使其跟随当前 `ProjectContext.trace_dir`，不再固定为项目根目录下 `.flowtrace`。
- 新增 `src/flowtrace/run_preflight.py`，输出 `project_run_preflight.v1`。
- 新增 `GET /api/project/run-preflight`，为已保存 run profile 生成执行前安全预检报告。
- 前端接入向导新增“执行前安全预检”区块。
- 保存/取消保存 run profile 后，前端会同步刷新 preflight 数据。
- 扩展 `tools/verify_realistic_samples.py`，断言无保存配置时 `no_saved_profiles`，保存后可生成预检报告，移除后回到 `no_saved_profiles`。

边界说明：
- 预检只读，不执行命令。
- 预检不修改用户项目。
- 前端只展示预检报告，不提供执行按钮。
- `run_preflight.py` 明确 safety：`executes_commands=false`、`requires_user_confirmation=true`、`allows_shell_string=false`。

验证结果：
```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
run_preflight no_saved_profiles for three samples ok
run_profile_store preflight_status_after_save=ready_for_confirmation
run_profile_store preflight_status_after_remove=no_saved_profiles
GET /api/project/run-preflight schema=project_run_preflight.v1
GET /api/project/run-preflight executes_commands=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

本轮结束状态：
```text
按用户要求，本轮开发完成后暂停，不自动进入下一轮。
```

### 2026-07-01 Asia/Shanghai - 预检确认状态

状态：已完成。来源：继续项目开发，沿既定流程从执行前安全预检推进到用户确认状态，但仍不实现命令执行。

处理内容：
- 新增 `src/flowtrace/run_confirmation_store.py`，负责保存、读取、撤销预检确认记录。
- 新增确认存储文件 `run_profile_confirmations.json`。
- 新增 `POST /api/project/run-preflight/confirm`。
- 新增 `POST /api/project/run-preflight/revoke`。
- `GET /api/project/run-preflight` 返回每条报告的确认状态：`none`、`confirmed`、`stale`。
- 确认状态绑定 profile 指纹；如果 profile 的 argv、工作目录、环境变量等发生变化，确认会自动失效。
- 前端“执行前安全预检”区块新增“确认预检 / 撤销确认”。
- 扩展 `tools/verify_realistic_samples.py`，验证保存、预检、确认、撤销确认的完整闭环。

边界说明：
- 确认只表示用户复核了预检报告，不执行命令。
- 阻断状态的预检报告不能确认。
- 确认状态不是最终执行授权；后续 runner 仍必须单独设计最终确认。
- 当前没有命令执行接口，没有 runner。

验证结果：
```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
API save profile ok
API confirm preflight -> confirmed ok
API revoke preflight -> none ok
confirmed preflight executes_commands=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 2026-07-01 Asia/Shanghai - 真实项目接入计划模型

状态：已完成。来源：用户要求“继续开发，而非纠缠前端细节 / 继续执行”。

处理内容：
- 新增 `src/flowtrace/integration_plan.py`，输出 `project_integration_plan.v1`。
- 新增 `GET /api/project/integration-plan`，聚合 project model、coverage、readiness、audit，生成确定性的接入计划。
- 接入计划包含：当前目标项目、计划状态、执行入口候选、五个接入阶段、阻断项、验收门和下一步动作。
- 前端 `api.js` 增加 `getProjectIntegrationPlan()`，接入向导消费该接口并展示“接入计划”区块。
- 扩展 `tools/verify_realistic_samples.py`，把 integration plan 纳入真实样本回归验收。

边界说明：
- `integration_plan.py` 属于 Analysis 层，不读取文件、不扫描项目、不修改用户代码。
- `integration_plan.py` 只消费 `scanner/readiness/audit/coverage` 已经产出的确定性数据，不引入 LLM 推断。
- server 只负责组装 API 输入；接入计划规则不写入 server。
- 前端只展示接入计划，不重新判断阻断项或入口优先级。

验证结果：
```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
/api/project/integration-plan schema=project_integration_plan.v1
flowtrace-mvp integration plan: status=blocked phases=5 targets=16 gates=5
ecommerce_checkout integration plan: status=partial phases=5 targets=6 first_target=main
verify_realistic_samples.py ok
ecommerce_checkout plan=partial phases=5 targets=6 gates=5
inventory_cli plan=blocked phases=5 targets=5 gates=5
support_ticket plan=partial phases=5 targets=5 gates=5
```

后续优化标记：
```text
- 自动运行用户项目仍未实现：接入计划目前只告诉用户“跑什么”，下一步需要新增 run profile/command profile。
- 浏览器真实输入录制仍未实现：Web 项目需要 Playwright/浏览器录制层把用户操作转为可重复运行流程。
- contract 草案生成仍未实现：应基于 runtime payload 与静态函数签名生成草案，但必须保持人工确认。
- 源文件/图节点跳转仍未实现：audit location 与 integration target 现在可展示，但不能直接跳转 IDE 或聚焦画布。
```

### 2026-07-01 Asia/Shanghai - 字体统一与运行配置草案

状态：已完成。来源：用户反馈“字体需要统一，修复过后继续项目开发”。

处理内容：
- 全局 UI 字体栈调整为 `Segoe UI / Microsoft YaHei UI / Microsoft YaHei / Arial`，减少中文、英文、路径混排时的割裂感。
- 为接入计划区块增加 `.integration-plan` 局部字体继承约束，避免入口候选中的 `code` 标签误用全局等宽字体。
- 新增 `src/flowtrace/run_profile.py`，输出 `project_run_profiles.v1`。
- 新增 `GET /api/project/run-profiles`，基于接入计划中的执行入口候选生成运行配置草案。
- 运行配置草案当前只描述命令，不执行命令、不写入用户项目，并且标记为必须用户确认。
- 前端接入向导新增“运行配置草案”区块，展示草案数量、可执行命令数量、工作目录、命令文本和安全边界。
- 扩展 `tools/verify_realistic_samples.py`，把 run profile 纳入真实样本验收。

边界说明：
- `run_profile.py` 只把 integration target 转换为可确认命令草案，不负责执行。
- 当前没有执行按钮，没有后台自动运行目标项目。
- 后续如果增加执行能力，必须新增用户确认、预检和运行隔离流程，不能直接复用草案接口执行。

验证结果：
```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
/api/project/run-profiles schema=project_run_profiles.v1
ecommerce_checkout run profiles: total=6 executable=4 safe=True
inventory_cli run profiles: total=5 executable=4 safe=True
support_ticket run profiles: total=5 executable=4 safe=True
styles.css served=200
browser visual verification skipped: in-app browser connection interrupted by local sandbox
```

后续优化标记：
```text
- 运行配置草案需要增加保存/恢复能力。
- 执行前需要增加 command preflight 页面，显示工作目录、环境变量、trace 目录和潜在写入风险。
- Web 项目仍需要浏览器录制能力，不能只依靠 python 文件入口。
```

### 2026-06-30 Asia/Shanghai - 侧边栏与主视图滚动归属小优化

状态：已完成第一阶段。来源：用户反馈“侧边栏内容被固定住了，导致主视窗下滑时需要反复上下滑动才能同时观察到主视窗底部内容与侧边栏内容”，并要求“开始，但是附带上需要后续优化的标记”。

处理内容：
- 将页面滚动模型调整为固定应用壳：`html`、`body` 使用 100% 高度并关闭全局纵向滚动。
- 左侧运行列表、主工作区、右侧详情/监视区收敛为各自 pane 内部滚动。
- `.sidebar` 改为三段式布局：品牌区、刷新按钮、运行列表；运行列表内部独立滚动。
- `.workspace`、`.content`、`.right-rail` 增加 `min-height: 0` / `overflow: hidden`，避免主页面被内容撑高后出现全局滚动。
- `.workspace-pane-body` 收敛内部滚动边界，避免工作区停靠页面撑开浏览器页面。
- 新增中文代码注释“后续优化标记”，明确当前只完成页面级滚动收敛，后续还需要继续细化画布类页面的内部拖拽、缩放和焦点定位体验。
- 增加小屏回退：窄屏下恢复页面可滚动，避免移动尺寸下内容被固定壳截断。

后续优化标记：
```text
当前只收敛页面级滚动。
画布类页面还需要继续细化内部拖拽、缩放和焦点定位体验。
后续还应检查各工作区标签停靠后的 pane 高度、滚动保持、右侧详情与监视窗口的默认高度策略。
```

验证结果：
```text
python ast ok 16
styles.css contains 后续优化标记=True
GET / = 200 text/html
/styles.css served length=33826
/styles.css has body overflow hidden=True
/styles.css has main-view-panel=True
server restarted pid=34728
browser visual verification skipped: in-app browser connection interrupted by local sandbox
```

### 2026-06-30 Asia/Shanghai - 自动审查报告与项目状态梳理

状态：已完成。来源：用户要求“开始，顺便给出接下来的开发步骤，总结一下项目进度，梳理项目尚需完善的功能”。

处理内容：
- 新增 `src/flowtrace/audit.py`，作为 Analysis 层的自动审查模型。
- 新增 `GET /api/project/audit`，返回审查状态、问题数量、问题清单、严重级别、归属层级、目标、证据和推荐动作。
- 前端接入向导新增“自动审查”区块，展示 audit 摘要、finding 列表和优先动作。
- 扩展 `tools/verify_realistic_samples.py`，加入 audit 状态、finding 数量、错误/警告数量断言。
- 新增 `docs/PROJECT_STATUS.md`，集中记录当前项目进度、已完成能力、下一步开发步骤和尚需完善功能。

边界说明：
- `audit.py` 属于 Analysis 层，不新增工程层级。
- `audit.py` 不扫描项目、不读写存储、不修改用户代码，只消费 project/readiness/coverage/runs/issues。
- 前端只展示审查结果，不重新推断问题。
- `server.py` 只负责聚合 API 输入，审查规则不写入 server。

验证结果：
```text
python ast ok 17
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
ecommerce_checkout audit: warn, findings=2, errors=0, warnings=2
inventory_cli audit: fail, findings=4, errors=2, warnings=2
support_ticket audit: warn, findings=2, errors=0, warnings=2
server restarted pid=12192
/api/project/audit status=fail findings=27 errors=7 warnings=20
runtime switch inventory_cli audit=fail findings=4 errors=2
frontend resources contain getProjectAudit/renderAudit/audit-summary=True
```

后续步骤：
```text
1. 审查结果跳转与定位。
2. 缺 contract 辅助生成。
3. 接入状态持久化。
4. 自动审查回归强化。
5. 真实项目接入体验完善。
```

### 2026-06-30 Asia/Shanghai - 自动审查详情定位

状态：已完成第一阶段。来源：继续开发自动审查闭环，优先让审查 finding 可以被用户点开查看证据和定位信息。

处理内容：
- `audit.py` 的每条 finding 新增 `location` 字段。
- `location` 当前支持 `check`、`method`、`runtime_issue`、`file` 等定位类型。
- 新增 `renderAuditFindingDetail(...)`，复用事件详情面板展示审查问题。
- 自动审查列表条目改为可点击按钮，点击后在详情面板显示标题、严重级别、归属层、目标、问题说明、建议动作、定位信息、证据和原始审查项。
- 扩展 `tools/verify_realistic_samples.py`，断言每个 audit finding 都包含 location，避免后续退化成纯文本问题列表。
- 更新 `docs/PROJECT_STATUS.md`，把审查详情能力纳入已完成范围，并把下一步调整为“从详情继续跳转到图节点/数据流边/源文件位置”。

边界说明：
- 本次只增强 UI 展示和 audit 输出结构，不修改用户项目。
- 前端仍不重新推断问题，只消费后端 `finding.location` 和 `finding.evidence`。
- 当前定位是“详情定位”，还不是“画布聚焦/源文件跳转”。

验证结果：
```text
python ast ok 17
node --check app.js ok
node --check onboarding.js ok
node --check details.js ok
verify_realistic_samples.py ok
ecommerce_checkout findings_with_location=2/2
inventory_cli findings_with_location=4/4
support_ticket findings_with_location=2/2
server restarted pid=55604
/api/project/audit first_has_location=True
frontend resources contain installAuditActions/renderAuditFindingDetail/finding-detail=True
browser visual verification skipped: in-app browser connection interrupted by local sandbox
```
### 2026-07-01 Asia/Shanghai - Runner 运行时策略

状态：已完成。来源：继续开发真实 runner 前的工程化执行准备链路。

处理内容：
- 新增 `src/flowtrace/runner_runtime_policy.py`，生成只读 Runner 运行时策略报告。
- 新增 `GET /api/project/runner-runtime-policies`。
- 接入向导新增“Runner 运行时策略”展示区块。
- 运行时策略覆盖 stdout/stderr 分片、最大输出限制、尾部摘要、取消、超时和完成刷新。
- 验收脚本增加完整 dry-run 链路后的运行时策略断言。

边界说明：
- 本轮不启用真实 runner。
- 本轮不提供执行 POST。
- 本轮不创建进程。
- 本轮不创建 stdout/stderr 文件。
- 本轮不写用户项目。
- `launch_enabled` 仍保持 `False`。

验证结果：
```text
python ast ok 53
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-runtime-policies schema=project_runner_runtime_policies.v1
runtime_schema=runner_runtime_policy_schema.v1
status=ready_but_launch_disabled
launchable_count=0
stdout_chunk_bytes=4096
stderr_chunk_bytes=4096
default_timeout_seconds=120
executes=False
creates_process=False
launch_enabled=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续优化标记：
```text
- 继续补齐未来真实执行所需的显式配置字段。
- 真实执行必须由单独开关和服务启动参数控制，不能由确认链路自动推导。
- 前端需要在接入向导中继续保持“草案/策略/禁用真实执行”的语义区分。
```
### 2026-07-01 Asia/Shanghai - Runner 执行配置只读层

状态：已完成。来源：继续项目工程化开发，固化真实 runner 前的显式配置需求。

处理内容：
- 新增 `src/flowtrace/runner_execution_config.py`，生成只读 Runner 执行配置报告。
- 新增 `GET /api/project/runner-execution-configs`。
- 接入向导新增“Runner 执行配置”展示区块。
- 执行配置报告覆盖 `flowtrace.runner.json`、`--allow-real-execution`、`FLOWTRACE_ALLOW_REAL_EXECUTION=1`、确认短语、argv 分离、禁用 shell 字符串和日志限制。
- 修正前端刷新链路：session、snapshot、dry-run 变化后，下游启动开关、运行时策略和执行配置会同步刷新。

边界说明：
- 本轮不启用真实 runner。
- 本轮不提供执行 POST。
- 本轮不创建配置文件。
- 本轮不创建进程。
- 本轮不创建 stdout/stderr 文件。
- 本轮不写用户项目。
- `launch_enabled` 仍保持 `False`。

验证结果：
```text
compileall ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-execution-configs schema=project_runner_execution_configs.v1
config_schema=runner_execution_config_schema.v1
status=configuration_required
launchable_count=0
typed=RUN TARGET PROJECT
argv_tokenized=True
executes=False
creates_process=False
launch_enabled=False
launch_api=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续优化标记：
```text
- 下一轮可设计真实执行配置文件解析草案，但仍不能自动创建或修改配置文件。
- 服务启动参数审计需要独立成层，不能揉进 server 路由。
- 真实 launch API 必须晚于配置解析、服务开关审计和日志目录策略。
```

### 2026-07-01 Asia/Shanghai - Runner 配置检查只读层

状态：已完成。来源：继续项目工程化开发，在执行配置只读层之后新增配置文件只读检查。

处理内容：
- 新增 `src/flowtrace/runner_execution_config_check.py`，生成只读 Runner 配置检查报告。
- 新增 `GET /api/project/runner-execution-config-checks`。
- 接入向导新增“Runner 配置检查”展示区块。
- 配置检查只读取候选位置里的 `flowtrace.runner.json`，候选位置包括目标项目根目录和 trace 目录。
- 缺少配置文件时返回 `config_missing`，不会自动创建配置。
- 临时合法配置存在时返回 `config_present_but_launch_disabled`，仍保持不可启动。
- 验收脚本覆盖缺少配置文件、临时合法配置文件、安全断言和 `launchable_count=0`。

边界说明：
- 本轮不启用真实 runner。
- 本轮不提供执行 POST。
- 本轮不创建配置文件。
- 本轮不修改配置文件。
- 本轮不执行命令。
- 本轮不创建进程。
- 本轮不创建 stdout/stderr 文件。
- 本轮不写用户项目。
- `launch_enabled` 仍保持 `False`。

验证结果：
```text
python ast ok 37
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-execution-config-checks schema=project_runner_execution_config_checks.v1
status=config_missing
launchable_count=0
executes=False
creates_process=False
creates_config=False
launch_enabled=False
launch_api=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续优化标记：
```text
- 下一轮可设计服务启动参数审计层，仍保持只读。
- 日志目录策略需要独立成层，不能由配置存在直接推导真实启动。
- 真实 launch API 必须晚于配置解析、服务开关审计、日志目录策略和用户再次确认。
```

### 2026-07-01 Asia/Shanghai - Runner 服务开关审计只读层

状态：已完成。来源：严格按照后续开发路径继续开发，并遵守“边界、硬性约束不得触碰”的要求。

处理内容：
- 新增 `src/flowtrace/runner_service_flag_audit.py`，生成只读 Runner 服务开关审计报告。
- 新增 `GET /api/project/runner-service-flag-audits`。
- 接入向导新增“Runner 服务开关审计”展示区块。
- 服务开关审计只消费 Runner 配置检查报告。
- 审计报告列出未来真实执行必须满足的 `--allow-real-execution`、`FLOWTRACE_ALLOW_REAL_EXECUTION=1`、`runner.enable_real_execution=true` 和确认短语。
- 验收脚本覆盖服务开关审计安全断言。

边界说明：
- 本轮不启用真实 runner。
- 本轮不提供执行 POST。
- 本轮不创建或修改配置文件。
- 本轮不读取环境变量。
- 本轮不解析进程参数。
- 本轮不执行命令。
- 本轮不创建进程。
- 本轮不创建 stdout/stderr 文件。
- 本轮不写用户项目。
- `launch_enabled` 仍保持 `False`。

验证结果：
```text
python ast ok 38
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-service-flag-audits schema=project_runner_service_flag_audits.v1
status=no_saved_profiles
store_path_status=service_flags_required
launchable_count=0
executes=False
creates_process=False
reads_environment=False
parses_process_args=False
launch_enabled=False
launch_api=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续优化标记：
```text
- 下一轮可设计 Runner 日志目录策略层，仍保持只读。
- 日志目录策略不得创建目录或文件，只报告未来写入要求。
- 真实 launch API 仍必须晚于配置解析、服务开关审计、日志目录策略和用户再次确认。
```
## 2026-07-01 Asia/Shanghai - Runner 日志目录策略只读层

目标：在服务开关审计之后，补齐未来真实 runner 的日志目录策略只读报告。

实现：

- 新增 `src/flowtrace/runner_log_directory_policy.py`。
- 新增 `GET /api/project/runner-log-directory-policies`。
- 前端 API、应用数据流和 onboarding 展示已接入。
- 样本验证脚本增加日志目录策略状态与安全断言。

安全约束：

- `executes_commands=False`
- `creates_process=False`
- `launch_enabled=False`
- `launch_api_available=False`
- `creates_log_directory=False`
- `opens_log_files=False`
- `writes_logs=False`
- `writes_user_project=False`

验证：

- Python AST 检查通过。
- 全量 UI JS `node --check` 通过。
- `verify_realistic_samples.py` 通过。
- 新接口 live 验证通过。

限制：

- 浏览器可视化验证仍被本地沙箱阻断：`windows sandbox failed: spawn setup refresh`。
## 2026-07-01 Asia/Shanghai - Runner 日志保留/轮转策略只读层

目标：在日志目录策略之后，补齐未来真实 runner 的日志保留和轮转策略只读报告。

实现：

- 新增 `src/flowtrace/runner_log_retention_policy.py`。
- 新增 `GET /api/project/runner-log-retention-policies`。
- 前端 API、应用数据流和 onboarding 展示已接入。
- 样本验证脚本增加日志保留/轮转策略状态与安全断言。

安全约束：

- `executes_commands=False`
- `creates_process=False`
- `launch_enabled=False`
- `launch_api_available=False`
- `scans_log_directory=False`
- `deletes_logs=False`
- `rotates_logs=False`
- `renames_logs=False`
- `truncates_logs=False`
- `writes_logs=False`

验证：

- Python AST 检查通过。
- 全量 UI JS `node --check` 通过。
- `verify_realistic_samples.py` 通过。
- 新接口 live 验证通过。

限制：

- 浏览器可视化验证仍被本地沙箱阻断：`windows sandbox failed: spawn setup refresh`。
## 2026-07-02 Asia/Shanghai - Runner 日志清理预览只读层

目标：在日志保留/轮转策略之后，补齐未来真实日志清理前的预览报告层。

实现：

- 新增 `src/flowtrace/runner_log_cleanup_preview.py`。
- 新增 `GET /api/project/runner-log-cleanup-previews`。
- 前端 API、应用数据流和 onboarding 展示已接入。
- 样本验证脚本增加清理预览状态与安全断言。

安全约束：

- `executes_commands=False`
- `creates_process=False`
- `launch_enabled=False`
- `launch_api_available=False`
- `scans_log_directory=False`
- `reads_log_files=False`
- `deletes_logs=False`
- `rotates_logs=False`
- `renames_logs=False`
- `truncates_logs=False`
- `writes_logs=False`

验证：

- Python AST 检查通过。
- 全量 UI JS `node --check` 通过。
- `verify_realistic_samples.py` 通过。
- 新接口 live 验证通过。

限制：

- 浏览器可视化验证仍被本地沙箱阻断：`windows sandbox failed: spawn setup refresh`。
### 2026-07-02 Asia/Shanghai - Runner 配置检查只读层

状态：已完成。来源：继续项目工程化开发，读取并审查未来真实执行配置文件。

处理内容：
- 新增 `src/flowtrace/runner_execution_config_check.py`，生成只读 Runner 配置检查报告。
- 新增 `GET /api/project/runner-execution-config-checks`。
- 接入向导新增“Runner 配置检查”展示区块。
- 配置检查候选位置为目标项目根目录和 trace 目录下的 `flowtrace.runner.json`。
- 缺失配置文件时返回 `config_missing`，不自动创建文件。
- 临时合法配置存在时返回 `config_present_but_launch_disabled`，仍保持真实执行禁用。

边界说明：
- 本轮不启用真实 runner。
- 本轮不提供执行 POST。
- 本轮不创建配置文件。
- 本轮不修改配置文件。
- 本轮不创建进程。
- 本轮不创建 stdout/stderr 文件。
- 本轮不写用户项目。
- `launch_enabled` 仍保持 `False`。

验证结果：
```text
python ast ok 37
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-execution-config-checks schema=project_runner_execution_config_checks.v1
check_schema=runner_execution_config_check_schema.v1
status=config_missing
launchable_count=0
executes=False
creates_process=False
creates_config=False
launch_enabled=False
launch_api=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续优化标记：
```text
- 下一轮应设计服务启动参数审计层。
- 服务启动参数审计需要判断当前 FlowTrace 进程是否显式允许真实执行。
- 即使配置文件存在且合规，如果服务启动参数没有开启，也必须保持真实执行禁用。
```
### 2026-07-02 Asia/Shanghai - Runner 治理就绪度只读总闸门

状态：已完成。来源：继续项目工程化开发，在日志清理审计追踪之后汇总所有 Runner 治理层状态。

处理内容：
- 新增 `src/flowtrace/runner_governance_readiness.py`，生成只读 Runner 治理就绪度报告。
- 新增 `GET /api/project/runner-governance-readiness`。
- `/api/project/bootstrap` 新增 `runner_governance_readiness`。
- 接入向导新增“Runner 治理就绪度”展示区块。
- 汇总 17 个 Runner 治理层，统一输出 `launchable_count=0`。

边界说明：
- 本轮不启用真实 runner。
- 本轮不提供执行 POST。
- 本轮不创建进程。
- 本轮不执行命令。
- 本轮不读写日志。
- 本轮不删除、轮转、重命名或截断日志。
- 本轮不创建或修改配置文件。
- 本轮不写用户项目。
- `launch_enabled` 仍保持 `False`。

验证结果：
```text
python ast ok 44
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-governance-readiness schema=project_runner_governance_readiness.v1
status=governance_required
layers=17
launchable_count=0
bootstrap_has=True
executes=False
creates_process=False
launch_enabled=False
launch_api=False
writes_logs=False
deletes_logs=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续优化标记：
```text
- 下一轮可以设计真实执行适配器规范草案，但仍不得创建进程。
- 也可以设计启动 API 合约草案，但仍不得注册真实 launch POST。
- 总闸门必须继续作为真实执行前的聚合挡板。
```
### 2026-07-02 Asia/Shanghai - Runner 执行适配器合约只读层

状态：已完成。来源：继续项目工程化开发，在治理就绪度总闸门之后增加未来执行适配器合约。

处理内容：
- 新增 `src/flowtrace/runner_execution_adapter_contract.py`，生成只读执行适配器合约报告。
- 新增 `GET /api/project/runner-execution-adapter-contracts`。
- `/api/project/bootstrap` 新增 `runner_execution_adapter_contracts`。
- 接入向导新增“Runner 执行适配器合约”展示区块。
- 前端治理尾链刷新收敛为 `refreshRunnerGovernanceTail()`。
- `tools/verify_realistic_samples.py` 增加执行适配器合约验收。

边界说明：
- 本轮不启用真实 runner。
- 本轮不提供执行 POST。
- 本轮不创建进程。
- 本轮不执行命令。
- 本轮不打开 stdout/stderr 文件。
- 本轮不写 runner 事件日志。
- 本轮不读写日志。
- 本轮不删除、轮转或截断日志。
- 本轮不创建或修改配置文件。
- 本轮不写用户项目。
- `launch_enabled` 仍保持 `False`。

验证结果：
```text
python py_compile ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-execution-adapter-contracts schema=project_runner_execution_adapter_contracts.v1
status=adapter_contract_required
launchable_count=0
bootstrap_has=True
executes=False
creates_process=False
launch_enabled=False
launch_api=False
writes_logs=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续优化标记：
```text
- 下一轮可以设计启动 API 合约草案，但只能输出只读报告。
- 不得注册真实 launch POST。
- 不得创建进程。
- 不得执行命令。
- 可考虑新增执行适配器审查报告，用于未来真实适配器落地前的静态门禁。
```
### 2026-07-02 Asia/Shanghai - Runner 启动 API 合约只读层

状态：已完成。来源：继续项目工程化开发，在执行适配器合约之后增加未来启动 API 合约。

处理内容：
- 新增 `src/flowtrace/runner_launch_api_contract.py`，生成只读启动 API 合约报告。
- 新增 `GET /api/project/runner-launch-api-contracts`。
- `/api/project/bootstrap` 新增 `runner_launch_api_contracts`。
- 接入向导新增“Runner 启动 API 合约”展示区块。
- `tools/verify_realistic_samples.py` 增加启动 API 合约验收。

边界说明：
- 本轮不启用真实 runner。
- 本轮不注册真实 launch POST。
- 本轮不调用执行适配器。
- 本轮不创建进程。
- 本轮不执行命令。
- 本轮不打开 stdout/stderr 文件。
- 本轮不写 runner 事件日志。
- 本轮不读写日志。
- 本轮不删除、轮转或截断日志。
- 本轮不创建或修改配置文件。
- 本轮不写用户项目。
- `launch_enabled` 仍保持 `False`。

验证结果：
```text
python py_compile ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-launch-api-contracts schema=project_runner_launch_api_contracts.v1
status=launch_api_contract_required
registered_endpoint_count=0
launchable_count=0
bootstrap_has=True
executes=False
creates_process=False
launch_enabled=False
launch_api=False
registers_post=False
writes_logs=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续优化标记：
```text
- 下一轮可以设计执行适配器审查报告。
- 也可以设计真实执行前最终阻断矩阵。
- 不得注册真实 launch POST。
- 不得创建进程。
- 不得执行命令。
- 不得写日志。
```
### 2026-07-02 Asia/Shanghai - Runner 执行适配器审查只读层

状态：已完成。来源：继续项目工程化开发，在启动 API 合约之后增加执行适配器预实现审查矩阵。

处理内容：
- 新增 `src/flowtrace/runner_execution_adapter_review.py`，生成只读执行适配器审查报告。
- 新增 `GET /api/project/runner-execution-adapter-reviews`。
- `/api/project/bootstrap` 新增 `runner_execution_adapter_reviews`。
- 接入向导新增“Runner 执行适配器审查”展示区块。
- `tools/verify_realistic_samples.py` 增加执行适配器审查验收。

边界说明：
- 本轮不启用真实 runner。
- 本轮不扫描代码。
- 本轮不导入执行适配器。
- 本轮不调用执行适配器。
- 本轮不注册真实 launch POST。
- 本轮不创建进程。
- 本轮不执行命令。
- 本轮不打开 stdout/stderr 文件。
- 本轮不写 runner 事件日志。
- 本轮不读写日志。
- 本轮不删除、轮转或截断日志。
- 本轮不创建或修改配置文件。
- 本轮不写用户项目。
- `launch_enabled` 仍保持 `False`。

验证结果：
```text
python py_compile ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-execution-adapter-reviews schema=project_runner_execution_adapter_reviews.v1
status=adapter_review_required
implemented_adapter_count=0
violation_count=0
launchable_count=0
bootstrap_has=True
executes=False
creates_process=False
launch_enabled=False
launch_api=False
scans_code=False
imports_adapter=False
calls_adapter=False
writes_logs=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

后续优化标记：
```text
- 下一轮可以设计真实执行前最终阻断矩阵。
- 阻断矩阵只聚合条件，不执行修复。
- 不得注册真实 launch POST。
- 不得调用执行适配器。
- 不得创建进程。
- 不得执行命令。
- 不得写日志。
```

### 2026-07-02 Asia/Shanghai - Runner 日志清理执行计划只读层

状态：已完成。来源：继续项目工程化开发，在 Runner 日志清理审计追踪之后增加清理执行计划合约层。

处理内容：
- 新增 `src/flowtrace/runner_log_cleanup_execution_plan.py`。
- 新增 `GET /api/project/runner-log-cleanup-execution-plans`。
- `/api/project/bootstrap` 新增 `runner_log_cleanup_execution_plans`。
- `runner_governance_readiness` 纳入该层，治理层数更新为 18。
- 接入向导新增“Runner 日志清理执行计划”展示区块。
- `tools/verify_realistic_samples.py` 增加执行计划安全断言。

边界说明：
- 本轮不开放真实 launch API。
- 本轮不执行命令，不创建进程。
- 本轮不生成、保存或读取候选清单。
- 本轮不保存执行计划，不执行清理。
- 本轮不扫描目录，不读取日志，不删除、轮转、重命名、截断或写入日志。
- 本轮不读写审计日志，不写用户项目。

验证结果：
```text
Python AST parse ok
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
GET /api/project/runner-log-cleanup-execution-plans schema=project_runner_log_cleanup_execution_plans.v1
status=no_saved_profiles
planned_operation_count=0
launchable_count=0
bootstrap_has=True
governance_layer_count=18
Playwright Edge bodyHasExecutionPlan=true
```

后续优化标记：
```text
- 下一轮可继续做真实执行前最终阻断矩阵或清理计划审查矩阵。
- 仍不得注册真实 launch POST。
- 仍不得调用执行适配器、创建进程、执行命令或写日志。
```
### 2026-07-02 Asia/Shanghai - Runner final block matrix read-only layer

Status: completed.

Changes:
- Added src/flowtrace/runner_final_block_matrix.py.
- Added GET /api/project/runner-final-block-matrices.
- Added bootstrap field runner_final_block_matrices.
- Added onboarding UI section Runner 最终阻断矩阵.
- Added verification coverage for the new layer.
- Optimized server single-endpoint governance construction with _project_runner_governance_chain() to avoid repeated recursive 18-layer rebuilds.

Boundaries:
- No real launch POST registration.
- No adapter import or call.
- No subprocess or command execution.
- No stdout/stderr file opening.
- No runner event writes.
- No log scan/read/write/delete/rotate/rename/truncate.
- No audit log read/write.
- No user project writes.
- launchable_count remains 0.

Verification:
```text
Python AST parse ok: 67 files
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
compileall ok with isolated PYTHONPYCACHEPREFIX
GET /api/project/runner-final-block-matrices ok
GET /api/project/runner-governance-readiness ok
Playwright Edge visual check ok
mojibake check false
```
### 2026-07-02 Asia/Shanghai - Runner authorization unlock audit read-only layer

Status: completed.

Changes:
- Added src/flowtrace/runner_authorization_unlock_audit.py.
- Added GET /api/project/runner-authorization-unlock-audits.
- Added bootstrap field runner_authorization_unlock_audits.
- Added onboarding UI section Runner 授权解锁审计.
- Added verification coverage for the new layer.

Boundaries:
- No real launch POST registration.
- No adapter import or call.
- No subprocess or command execution.
- No human authorization collection.
- No launch permission grant.
- No authorization storage.
- No stdout/stderr file opening.
- No runner event writes.
- No log scan/read/write/delete/rotate/rename/truncate.
- No audit log read/write.
- No user project writes.
- launchable_count remains 0.

Verification:
```text
Python AST parse ok: 68 files
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
compileall ok with isolated PYTHONPYCACHEPREFIX
GET /api/project/runner-authorization-unlock-audits ok
Playwright Edge visual check ok
mojibake check false
```

### 2026-07-02 Asia/Shanghai - Frontend UX optimization may interrupt the backend flow when needed

Status: recorded as a conditional optimization track.

Decision:
- Future frontend human-computer interaction optimization is allowed to interrupt the normal development flow when it becomes necessary.
- The default main path remains the Runner real-execution readiness path.
- UX work should interrupt only when the current UI blocks understanding, safe operation, validation, or future real-test usability.

Recommended UX target:
```text
Move from a long engineering report page to a Runner workbench:
- current status summary
- current phase
- next action
- current blockers
- staged workflow
- audit details
- future execution console
```

Interrupt triggers:
- The user cannot tell why real launch is blocked.
- The onboarding page becomes too long to navigate safely.
- New Runner execution features need a stable interaction container.
- Visual or text issues, including mojibake, reduce trust in validation.
- A workflow needs clear actionable states before backend implementation continues.

Implementation rule:
- Prefer a protective frontend skeleton first: runner workbench, blocker panel, stage flow, audit details.
- Keep existing API contracts stable during UX refactoring.
- Keep read-only governance reports available for audit/debug views.
- Do not add fake launch buttons before backend launch eligibility exists.

Boundary:
```text
UX optimization must not register real launch APIs.
UX optimization must not grant authorization.
UX optimization must not call adapters.
UX optimization must not create processes.
UX optimization must not execute commands.
UX optimization must not write logs or user project files.
```

### 2026-07-03 Asia/Shanghai - Runner implementation gap checklist read-only layer

Status: completed.

Changes:
- Added src/flowtrace/runner_implementation_gap_checklist.py.
- Added GET /api/project/runner-implementation-gap-checklists.
- Added bootstrap field runner_implementation_gap_checklists.
- Added onboarding UI section Runner 实现差距清单.
- Added verification coverage for the new layer.

Declared missing components:
- execution_adapter
- launch_post_api
- runner_session_state
- stdout_stderr_streams
- runner_event_log
- cancel_timeout_endpoints
- audit_persistence
- execution_console_ui

Boundaries:
- No real launch POST registration.
- No runner implementation or code writes.
- No adapter import or call.
- No subprocess or command execution.
- No authorization collection or permission grant.
- No stdout/stderr file opening.
- No runner event writes.
- No log scan/read/write/delete/rotate/rename/truncate.
- No audit log read/write.
- No user project writes.
- launchable_count remains 0.

Verification:
```text
Python AST parse ok: 69 files
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
compileall ok with isolated PYTHONPYCACHEPREFIX
GET /api/project/runner-implementation-gap-checklists ok
Playwright Edge visual check ok
mojibake check false
```
### 2026-07-03 Asia/Shanghai - UX interruption note after cancel/timeout contract

The onboarding page now contains another Runner governance section. Visual validation still passes and mojibake is false, but the page is getting long. If the user reports confusion, navigation friction, or another text rendering issue, interrupt backend layering and build the Runner workbench skeleton before adding more report sections. The skeleton must remain read-only and must not expose fake launch, cancel, timeout, adapter, process, log, audit, or user-project write actions.

### 2026-07-03 Asia/Shanghai - UX interruption note after session state schema

The onboarding page now contains the Runner session state schema section. Visual validation still passes and mojibake is false, but the report stack is long. If the user asks about confusion, navigation friction, or front-end interaction quality, interrupt backend layering and build the read-only Runner workbench skeleton before adding more report sections. The skeleton must not expose fake launch, cancel, timeout, adapter, process, session mutation, log, audit, or user-project write actions.

## 2026-07-03 Asia/Shanghai - Runner workbench UX optimization

Status: completed and verified.

Implemented:
- Added read-only Runner workbench component: D:\pyProject\flowtrace-mvp\src\flowtrace\ui\modules\components\runner-workbench.js.
- Added main workspace tab: Runner workbench.
- Added runner panel to workspace layout registration and default main-panel order.
- Kept existing onboarding page and all existing API contracts unchanged.
- Fixed static HTML mojibake text in D:\pyProject\flowtrace-mvp\src\flowtrace\ui\index.html.
- Added CSS for dense workbench summary, blockers, hard boundary, and stage flow.

Compatibility notes:
```text
No API schema changed.
No existing endpoint path changed.
No existing onboarding section removed.
No existing saved workspace layout is invalidated.
The workspace layout registry appends missing panels to old layouts through the existing ensureRegisteredPanels path.
The new workbench reads already-loaded bootstrap data only.
```

Workbench purpose:
```text
Expose current Runner status without forcing users through the long onboarding report stack.
Show current phase, next action, blockers, hard boundary, and a compact stage flow.
Keep all actions read-only. No fake launch/cancel/timeout controls are shown.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No process signal or kill operation.
No timeout worker scheduling.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
UI JS node --check ok
app.js ESM syntax check ok
Python AST parse ok: 53 files in src/tools
tools/verify_realistic_samples.py ok
compileall ok with isolated PYTHONPYCACHEPREFIX
git diff --check ok
Static HTML smoke check ok: brand and refresh text render as Chinese, no known mojibake markers
Playwright Edge desktop visual check ok
Runner workbench tab appears after resetWindows=1
Runner workbench DOM present
Runner workbench shows hard boundary text
Runner workbench shows launchable 0 and registered endpoint 0
Browser text mojibake check false
Console errors after reload: 0
CLI viewport resize did not take effect for mobile verification; responsive CSS rules are present but mobile visual verification is not trusted in this run.
```

Service:
```text
http://127.0.0.1:8765/
PID 52204
```

Screenshots:
```text
D:\pyProject\flowtrace-mvp\output\playwright\flowtrace-runner-workbench-optimization.png
D:\pyProject\flowtrace-mvp\output\playwright\flowtrace-runner-workbench-mobile.png
```

Next recommended step:
```text
Use the Runner workbench as the default place for future human-interaction optimization.
Continue backend read-only layers only when the workbench remains understandable and safe.
Real execution still requires a separate implementation and explicit authorization round.
```
## 2026-07-03 Asia/Shanghai - Runner workbench filters and collapsible onboarding sections

Status: completed and verified.

Implemented:
- Added Runner workbench stage filters: All, Blocked, Ready, Missing, Governance.
- Added click/keyboard selectable stage cards.
- Added Runner stage detail panel showing schema, next action, summary, and selected safety flags.
- Converted onboarding sections into collapsible dropdown panels.
- Runner-heavy onboarding sections default to collapsed.
- Collapse state is stored only in browser localStorage: flowtrace.onboardingSectionCollapse.v1.
- Existing onboarding content, actions, and API payloads remain available.

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No existing onboarding section removed.
No real execution action was added.
No user project write was added.
The dropdown state is browser-local UI preference only.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No process signal or kill operation.
No timeout worker scheduling.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
compileall ok with isolated PYTHONPYCACHEPREFIX
git diff --check ok
Playwright Edge workbench filter check ok
Workbench governance filter visible_count=14
Stage detail updates after card click
Onboarding section_count=34
Onboarding toggle_count=34
Onboarding collapsed_count=26
Runner onboarding sections default collapsed
Onboarding section expand click ok
Collapse state stored in localStorage ok
Browser text mojibake check false
Console only has favicon.ico 404
```

Service:
```text
http://127.0.0.1:8765/
PID 52204
```

Screenshots:
```text
D:\pyProject\flowtrace-mvp\output\playwright\flowtrace-runner-workbench-filter-detail.png
D:\pyProject\flowtrace-mvp\output\playwright\flowtrace-onboarding-collapsible-sections.png
```

Next recommended step:
```text
Continue refining the Runner workbench as the main human-facing surface before adding more long read-only report sections.
Real execution still requires a separate implementation and explicit authorization round.
```

## 2026-07-03 - Onboarding Collapse Audit Fix

Issue:
```text
The onboarding dropdown state was toggled correctly in JavaScript, but collapsed
sections still occupied the full body height. Users saw Open/Close labels while
the long page remained visually long.
```

Root cause:
```text
.onboarding-section-body declared display: grid.
That author CSS overrode the browser default [hidden] { display: none; } behavior.
As a result, body.hidden became true but the body still rendered as grid.
```

Fix:
```text
Added .onboarding-section-body[hidden] { display: none; }.
This keeps the existing DOM, localStorage state, API usage, and onboarding logic
compatible while restoring native hidden behavior.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/app.js ok
Playwright DOM audit ok
Collapsed Runner section bodyDisplay=none
Collapsed Runner section bodyHeight=0
Collapsed Runner section height=40
Manual click collapse: 接入状态 height 882 -> 40
Browser mojibake check false
```

## 2026-07-04 - Runner Stream Capture Implementation Audit Read-Only Layer

Status: completed and verified.

Implemented:
- Added a read-only stdout/stderr capture implementation audit layer.
- Added `GET /api/project/runner-stream-capture-implementation-audits`.
- Added bootstrap payload `runner_stream_capture_implementation_audits`.
- Added onboarding section `Runner stdout/stderr 捕获实现准备审计`.
- Added Runner Workbench stage `输出审计`; stage count is now 34.
- Added realistic sample verification for empty profiles and temporary saved-profile chains.

Compatibility notes:
```text
No existing endpoint path changed.
No existing schema key was removed.
No existing UI section was renamed.
No frontend optimization behavior was changed.
The new payload is additive and read-only.
```

Hard boundary:
```text
No stdout/stderr opening.
No stdout/stderr reading.
No stdout/stderr capture.
No runner event writes.
No log file reads or writes.
No audit log persistence.
No process creation or control.
No real timeout scheduling.
No launch/cancel/timeout POST API.
No adapter import or invocation.
No command execution.
No session creation or persistence.
No session state mutation.
No authorization collection or storage.
No permission grants.
No user project writes.
```

Validation:
```text
python ast ok 77
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
API schema project_runner_stream_capture_implementation_audits.v1 ok
Bootstrap schema project_runner_stream_capture_implementation_audits.v1 ok
Playwright stageCount=34
Playwright hasStreamStage=true
Playwright onboarding sectionExists=true
Browser mojibake check false
```

Next suggestion:
```text
Add a read-only Runner event writer implementation audit layer.

作用：提前约束真实执行事件的 schema、顺序、终止态写入、失败处理和脱敏规则，避免后续实现时事件链不可信。
```

## 2026-07-04 - Runner Process Lifecycle Implementation Audit Read-Only Layer

Status: completed and verified.

Implemented:
- Added a read-only process lifecycle implementation audit layer.
- Added `GET /api/project/runner-process-lifecycle-implementation-audits`.
- Added bootstrap payload `runner_process_lifecycle_implementation_audits`.
- Added onboarding section `Runner 进程生命周期实现准备审计`.
- Added Runner Workbench stage `进程审计`; stage count is now 33.
- Added realistic sample verification for empty profiles and temporary saved-profile chains.

Compatibility notes:
```text
No existing endpoint path changed.
No existing schema key was removed.
No existing UI section was renamed.
No frontend optimization behavior was changed.
The new payload is additive and read-only.
```

Hard boundary:
```text
No real launch API.
No launch/cancel/timeout POST API.
No runner implementation.
No adapter import or invocation.
No process creation or control.
No process signalling.
No process cancellation or kill.
No real timeout scheduling.
No command execution.
No session creation or persistence.
No session state mutation.
No stdout/stderr opening.
No runner event writes.
No log file reads or writes.
No audit log persistence.
No authorization collection or storage.
No permission grants.
No user project writes.
```

Validation:
```text
python ast ok 76
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
API schema project_runner_process_lifecycle_implementation_audits.v1 ok
Bootstrap schema project_runner_process_lifecycle_implementation_audits.v1 ok
Playwright stageCount=33
Playwright hasProcessStage=true
Playwright onboarding sectionExists=true
Browser mojibake check false
```

## 2026-07-03 - Runner Execution Adapter Implementation Audit Read-Only Layer

Status: completed and verified.

Implemented:
- Added a read-only execution adapter implementation audit layer.
- Added `GET /api/project/runner-execution-adapter-implementation-audits`.
- Added bootstrap payload `runner_execution_adapter_implementation_audits`.
- Added onboarding section `Runner 执行适配器实现准备审计`.
- Added Runner Workbench stage `适配器审计`; stage count is now 32.
- Added realistic sample verification for empty profiles and temporary saved-profile chains.

Compatibility notes:
```text
No existing endpoint path changed.
No existing schema key was removed.
No existing UI section was renamed.
No frontend optimization behavior was changed.
The new payload is additive and read-only.
```

Hard boundary:
```text
No real launch API.
No launch/cancel/timeout POST API.
No runner implementation.
No adapter implementation.
No adapter import or invocation.
No process creation or control.
No command execution.
No session creation or persistence.
No session state mutation.
No stdout/stderr opening.
No runner event writes.
No log file reads or writes.
No audit log persistence.
No authorization collection or storage.
No permission grants.
No user project writes.
```

Validation:
```text
python ast ok 75
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
API schema project_runner_execution_adapter_implementation_audits.v1 ok
Bootstrap schema project_runner_execution_adapter_implementation_audits.v1 ok
Playwright stageCount=32
Playwright hasAuditStage=true
Playwright onboarding sectionExists=true
Browser mojibake check false
```

## 2026-07-03 - Runner Real Execution Implementation Plan Read-Only Layer

Status: completed and verified.

Implemented:
- Added a read-only real execution implementation plan layer.
- Added `GET /api/project/runner-real-execution-implementation-plans`.
- Added bootstrap payload `runner_real_execution_implementation_plans`.
- Added onboarding section `Runner 真实执行实现计划`.
- Added Runner Workbench stage `实现计划`; stage count is now 31.
- Added realistic sample verification for empty profiles and temporary saved-profile chains.

Compatibility notes:
```text
No existing endpoint path changed.
No existing schema key was removed.
No existing UI section was renamed.
No frontend optimization behavior was changed.
The new payload is additive and read-only.
```

Hard boundary:
```text
No real launch API.
No launch/cancel/timeout POST API.
No runner implementation.
No adapter import or invocation.
No process creation or control.
No command execution.
No session creation or persistence.
No session state mutation.
No stdout/stderr opening.
No runner event writes.
No log file reads or writes.
No audit log persistence.
No authorization collection or storage.
No permission grants.
No user project writes.
```

Validation:
```text
python ast ok 74
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
API schema project_runner_real_execution_implementation_plans.v1 ok
Bootstrap schema project_runner_real_execution_implementation_plans.v1 ok
Playwright stageCount=31
Playwright hasPlanStage=true
Playwright onboarding sectionExists=true
Browser mojibake check false
```

## 2026-07-03 - Runner Real-Test Readiness Read-Only Layer

Status: completed and verified.

Implemented:
- Added `src/flowtrace/runner_real_test_readiness.py`.
- Added `GET /api/project/runner-real-test-readiness`.
- Added `runner_real_test_readiness` to project bootstrap.
- Added Runner real-test readiness to onboarding.
- Added real-test readiness as the 29th Runner workbench stage.
- Extended realistic sample verification for empty-profile and saved-profile governance chains.

Compatibility notes:
```text
No existing endpoint path changed.
No existing schema was removed.
No existing runner payload was changed.
No existing POST API behavior changed.
The new layer is additive and read-only.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No adapter import or invocation.
No process creation or control.
No command execution.
No session creation or persistence.
No stdout/stderr opening.
No runner event writes.
No log file reads or writes.
No audit log persistence.
No authorization collection or storage.
No permission grants.
No user project writes.
```

Validation:
```text
python ast ok 72
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-real-test-readiness -> project_runner_real_test_readiness.v1
/api/project/bootstrap.runner_real_test_readiness -> project_runner_real_test_readiness.v1
Playwright stageCount=29
Playwright hasRealTestStage=true
Playwright onboarding section exists=true
Browser mojibake check false
Service restarted on http://127.0.0.1:8765/ with PID 64560
```

## 2026-07-03 - Runner Real-Test Authorization Checklist Read-Only Layer

Status: completed and verified.

Implemented:
- Added `src/flowtrace/runner_real_test_authorization_checklist.py`.
- Added `GET /api/project/runner-real-test-authorization-checklists`.
- Added `runner_real_test_authorization_checklists` to project bootstrap.
- Added Runner real-test authorization checklist to onboarding.
- Added authorization checklist as the 30th Runner workbench stage.
- Extended realistic sample verification for empty-profile and saved-profile governance chains.

Compatibility notes:
```text
No existing endpoint path changed.
No existing schema was removed.
No existing runner payload was changed.
No existing POST API behavior changed.
The new layer is additive and read-only.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No adapter import or invocation.
No process creation or control.
No command execution.
No session creation or persistence.
No stdout/stderr opening.
No runner event writes.
No log file reads or writes.
No audit log persistence.
No authorization collection or storage.
No permission grants.
No user project writes.
```

Validation:
```text
python ast ok 73
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-real-test-authorization-checklists -> project_runner_real_test_authorization_checklists.v1
/api/project/bootstrap.runner_real_test_authorization_checklists -> project_runner_real_test_authorization_checklists.v1
Playwright stageCount=30
Playwright hasAuthorizationStage=true
Playwright onboarding section exists=true
Browser mojibake check false
Service restarted on http://127.0.0.1:8765/ with PID 39724
```

Boundary:
```text
No backend API changed.
No runner execution feature added.
No launch/cancel/timeout/session mutation added.
No user project write added.
```

## 2026-07-03 - Runner Workbench Critical Path Optimization

Status: completed and verified.

Implemented:
- Changed Runner workbench current-stage selection to prioritize the earliest actionable blocker.
- When no run profile is saved, the workbench now focuses on "等待保存运行配置" instead of the last loaded governance layer.
- Added a read-only "关键路径" panel with four steps: run profile, confirmation chain, read-only governance, and unlock gaps.
- Added stage summary chips for blocked, warning, ready, and missing counts.
- Localized remaining workbench fallback text that appeared in stage details.

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No existing runner payload changed.
No real execution action was added.
No user project write was added.
The new panel is derived only from existing bootstrap payloads.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright Edge workbench DOM check ok
Current title=等待保存运行配置
Critical path count=4
Stage chips show blocked/warn/ready/missing counts
Governance filter visible_count=14
Browser text mojibake check false
Old English fallback check false
```

## 2026-07-03 - Runner Workbench Critical Path Navigation

Status: completed and verified.

Implemented:
- Made each critical-path step keyboard-focusable and clickable.
- Selecting a critical-path step now updates the shared stage detail panel.
- Stage cards and critical-path steps share the same selected state.
- Critical-path selection restores the stage filter to "全部" so the target stage is never hidden by a previous filter.
- Added display-layer localization for known English runner next-action fallback strings.

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No existing runner payload changed.
No real execution action was added.
No user project write was added.
Navigation is derived only from existing bootstrap payloads and DOM state.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright click navigation ok
Playwright keyboard Enter navigation ok
Critical path count=4
Clicking unlock gap selects runner_implementation_gap_checklists
Keyboard Enter on confirmation path selects run_execution_gate
Path navigation resets active filter to 全部
Browser text mojibake check false
Old English fallback check false
```

## 2026-07-03 - Runner Workbench Read-Only Evidence Panel

Status: completed and verified.

Implemented:
- Added a read-only evidence panel inside Runner stage details.
- Evidence is extracted from existing payload summaries and schema objects only.
- The panel shows compact metric chips and collapsible evidence groups.
- Supported evidence sources include blocked actions, blocking dimensions, required future unlocks, authorization records, required evidence, implementation components, governance layers, future blocker layers, unlock states, and reports.
- Added display-layer localization for known schema evidence strings without changing backend payloads.

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No existing runner payload changed.
No real execution action was added.
No user project write was added.
Evidence display is derived only from existing bootstrap payloads.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright evidence panel check ok
Implementation gap evidence groups=2
Implementation gap known English blocker strings=false
Governance readiness evidence groups=2
Evidence details can expand
Browser text mojibake check false
```

## 2026-07-03 - Runner Workbench Blocker Evidence Navigation

Status: completed and verified.

Implemented:
- Made blocker cards keyboard-focusable and clickable when they have an evidence target.
- Added blocker-to-stage mappings for saved-profile blockers, launch blockers, endpoint blockers, and current-stage blockers.
- Clicking "真实启动仍被阻断" selects the final block matrix stage and opens the "阻断动作" evidence group.
- Keyboard Enter on "尚未保存运行配置" selects the run profile stage.
- Blocker navigation restores the stage filter to "全部" before selecting the target stage.

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No existing runner payload changed.
No real execution action was added.
No user project write was added.
Navigation is derived only from existing DOM state and bootstrap payloads.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright blocker click navigation ok
Playwright blocker keyboard Enter navigation ok
Launch blocker selects runner_final_block_matrices
Launch blocker opens 阻断动作 evidence group
Saved-profile blocker selects run_profiles
Blocker navigation resets active filter to 全部
Browser text mojibake check false
```

## 2026-07-03 - Runner Workbench Safety Boundary Grouping

Status: completed and verified.

Implemented:
- Replaced raw safety key=value chips with grouped Chinese safety boundary cards.
- Safety groups now cover execution, API, session, log/audit, project write, and read-only declaration boundaries.
- Each safety flag shows a readable state: 已阻断, 只读声明, 需要审查, or 未声明.
- Internal *_only safety keys are localized in the UI.

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No existing runner payload changed.
No real execution action was added.
No user project write was added.
Safety grouping is derived only from existing payload.safety fields.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright safety grouping check ok
Final block matrix safety groups=6
Session state schema safety groups=6
Old key=value safety text=false
Raw *_only safety key text=false
Browser text mojibake check false
```

## 2026-07-03 - Runner Workbench Copy Read-Only Audit Summary

Status: completed and verified.

Implemented:
- Added a "复制摘要" action to Runner stage details.
- The copied text is generated from the currently selected stage payload already present in the page.
- The summary includes stage status, schema version, next action, safety boundaries, read-only evidence, and hard boundary text.
- Clipboard write uses browser clipboard when available and a textarea fallback otherwise.
- Copy status is shown inline as "已复制" or "复制失败".

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No existing runner payload changed.
No real execution action was added.
No user project write was added.
No file is created or modified by the UI copy action.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright copy summary check ok with clipboard stub
Copy status=已复制
Copied summary includes stage, safety boundaries, read-only evidence, and hard boundary text
Browser text mojibake check false
```

## 2026-07-03 - Runner Workbench Stage Detail Compact Mode

Status: completed and verified.

Implemented:
- Added a "压缩视图 / 展开视图" toggle to Runner stage details.
- Compact mode keeps headings, metrics, and group counts visible while hiding long safety flag and evidence lists.
- The compact state is page-local DOM state only; it does not write files or user project data.
- The selected stage remains unchanged when toggling compact mode.
- The compact mode button stays synchronized after switching stages.

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No existing runner payload changed.
No real execution action was added.
No user project write was added.
No localStorage or file persistence was added.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright compact mode check ok
Detail height 1176 -> 755 in compact mode
Compact mode hides safety flag lists and evidence lists
Expand mode restores safety flag lists
Compact state persists across stage switch and button text stays synchronized
Browser text mojibake check false
```

## 2026-07-03 - Runner Workbench Stage Flow Density And Scope

Status: completed and verified.

Implemented:
- Added stage flow density controls: 标准密度 and 紧凑密度.
- Added stage scope controls: 全部阶段 and 关键阶段.
- Critical stages are derived from the existing critical path and blocker targets.
- Stage filter, density, and scope controls compose together.
- Fixed governance readiness grouping so it appears under the 治理 filter.

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No existing runner payload changed.
No real execution action was added.
No user project write was added.
No persistence was added; controls only affect current DOM state.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright stage density/scope check ok
Total stages=28
Critical stages=5
Dense card height=78
Critical scope visible_count=5
Governance + critical visible_count=2
Governance + critical includes runner_governance_readiness
Browser text mojibake check false
```

## 2026-07-03 - Runner Workbench Stage Search And Quick Locate

Status: completed and verified.

Implemented:
- Added a stage search input to Runner 工作台.
- Search matches stage key, title, status, summary, group, and kind.
- Added a visible-count indicator so filtered results are immediately auditable.
- Search composes with the existing stage group filter, compact density mode, and critical-only scope.
- The feature only changes current DOM visibility and does not persist state.

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No runner payload changed.
No real execution action was added.
No user project write was added.
No persistence was added; controls only affect current DOM state.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright stage search check ok
Initial visible=28/28
session search visible=2
日志 search visible=1
governance + critical + governance search visible=2
Browser mojibake check false
```

## 2026-07-03 - Runner Workbench Stage Search Clear And Empty State

Status: completed and verified.

Implemented:
- Added a clear button for the Runner stage search input.
- Clear button is disabled while the search query is empty.
- Added a no-result empty state for combined stage search/filter/scope results.
- Clearing search restores the full visible stage set without changing the selected stage.
- The behavior remains current-page DOM state only.

Compatibility notes:
```text
No backend API changed.
No endpoint path changed.
No schema changed.
No runner payload changed.
No persistence was added.
No user project write was added.
No execution side effect was added.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No session creation.
No session persistence.
No session state mutation.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright search empty/clear check ok
No-match visible=0/28
No-match empty state visible=true
Clear restores visible=28/28
Clear button disabled after clearing=true
Browser mojibake check false
```
## 2026-07-04 - Runner Event Writer Implementation Audit Read-Only Layer

Status: completed and verified.

Implemented:
- Added `src/flowtrace/runner_event_writer_implementation_audit.py`.
- Added read-only endpoint `GET /api/project/runner-event-writer-implementation-audits`.
- Added bootstrap field `runner_event_writer_implementation_audits`.
- Added API client `getProjectRunnerEventWriterImplementationAudits`.
- Added onboarding section `Runner 事件写入实现准备审计`.
- Added Runner Workbench stage `事件审计`; stage count is now 35.
- Extended `tools/verify_realistic_samples.py` with no-profile and saved-profile chain coverage.

Compatibility notes:
```text
No existing endpoint path changed.
No existing schema field was removed.
No POST API was added.
No runner implementation was added.
No adapter import or invocation was added.
No process/session/log/event mutation was added.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No adapter import or invocation.
No process creation or control.
No command execution.
No session creation or mutation.
No stdout/stderr opening, reading, or capture.
No runner event writes.
No runner event log opening.
No event log writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No authorization collection or storage.
No permission grants.
No user project writes.
```

Validation:
```text
python ast ok 78
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
tools/verify_realistic_samples.py ok
git diff --check ok
compileall ok
API schema project_runner_event_writer_implementation_audits.v1 ok
Bootstrap schema project_runner_event_writer_implementation_audits.v1 ok
Playwright stageCount=35 hasEventStage=true
Playwright onboarding section/schema/evidence ok
Browser mojibake check false
Service restarted on http://127.0.0.1:8765/ with PID 49320
```

Next development suggestion:
```text
Add a read-only "Runner audit persistence implementation audit" layer.
作用：提前约束未来人工授权证据、启动决策、事件链摘要如何进入审计记录，避免真实测试后无法追责或审计记录与事件流不一致。
```
## 2026-07-04 - Runner Audit Persistence Implementation Audit Read-Only Layer

Status: completed and verified.

Implemented:
- Added `src/flowtrace/runner_audit_persistence_implementation_audit.py`.
- Added read-only endpoint `GET /api/project/runner-audit-persistence-implementation-audits`.
- Added bootstrap field `runner_audit_persistence_implementation_audits`.
- Added API client `getProjectRunnerAuditPersistenceImplementationAudits`.
- Added onboarding section `Runner 审计持久化实现准备审计`.
- Added Runner Workbench stage `审计持久化`; stage count is now 36.
- Extended `tools/verify_realistic_samples.py` with no-profile and saved-profile chain coverage.

Compatibility notes:
```text
No existing endpoint path changed.
No existing schema field was removed.
No POST API was added.
No runner implementation was added.
No adapter import or invocation was added.
No process/session/log/event/audit mutation was added.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No adapter import or invocation.
No process creation or control.
No command execution.
No session creation or mutation.
No stdout/stderr opening, reading, or capture.
No runner event writes.
No runner event log opening.
No event log writes.
No audit log opening.
No audit log reads.
No audit log writes.
No audit record persistence.
No log scan/read/write/delete/rotate/rename/truncate.
No authorization collection or storage.
No permission grants.
No user project writes.
```

Validation:
```text
python ast ok 79
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
tools/verify_realistic_samples.py ok
git diff --check ok
compileall ok
API schema project_runner_audit_persistence_implementation_audits.v1 ok
Bootstrap schema project_runner_audit_persistence_implementation_audits.v1 ok
Playwright stageCount=36 hasAuditPersistenceStage=true
Playwright onboarding section/schema/evidence ok
Browser mojibake check false
Service restarted on http://127.0.0.1:8765/ with PID 33696
```

Next development suggestion:
```text
Add a read-only "Runner audit integrity and replay verification preparation audit" layer.
作用：提前约束真实测试后的校验闭环，避免后续即使写入了事件和审计记录，也无法证明二者一致、完整、可回放。
```
## 2026-07-04 - Runner Audit Integrity Replay Verification Audit Read-Only Layer

Status: completed and verified.

Implemented:
- Added `src/flowtrace/runner_audit_integrity_replay_verification_audit.py`.
- Added read-only endpoint `GET /api/project/runner-audit-integrity-replay-verification-audits`.
- Added bootstrap field `runner_audit_integrity_replay_verification_audits`.
- Added API client `getProjectRunnerAuditIntegrityReplayVerificationAudits`.
- Added onboarding section `Runner 审计完整性与回放校验准备审计`.
- Added Runner Workbench stage `回放校验`; stage count is now 37.
- Extended `tools/verify_realistic_samples.py` with no-profile and saved-profile chain coverage.

Compatibility notes:
```text
No existing endpoint path changed.
No existing schema field was removed.
No POST API was added.
No runner implementation was added.
No adapter import or invocation was added.
No process/session/log/event/audit mutation was added.
No audit/event/config reads were added.
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No adapter import or invocation.
No process creation or control.
No command execution.
No session creation or mutation.
No stdout/stderr opening, reading, or capture.
No runner event reads or writes.
No runner event log opening.
No event log writes.
No audit log opening.
No audit log reads or writes.
No audit record reads or persistence.
No config snapshot reads.
No integrity checks.
No replay checks.
No consistency checks.
No log scan/read/write/delete/rotate/rename/truncate.
No authorization collection or storage.
No permission grants.
No user project writes.
```

Validation:
```text
python ast ok 80
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
tools/verify_realistic_samples.py ok
git diff --check ok
compileall ok
API schema project_runner_audit_integrity_replay_verification_audits.v1 ok
Bootstrap schema project_runner_audit_integrity_replay_verification_audits.v1 ok
Playwright stageCount=37 hasIntegrityReplayStage=true
Playwright onboarding section/schema/evidence ok
Browser mojibake check false
Service restarted on http://127.0.0.1:8765/ with PID 55348
```

Next development suggestion:
```text
Add a read-only "Runner verification discrepancy report implementation audit" layer.
作用：提前约束异常校验结果的用户可理解输出，避免后续发现事件链与审计记录不一致时只能得到模糊错误，无法定位原因或决定是否阻断真实测试。
```
## 2026-07-04 - Runner Verification Discrepancy Report Audit Read-Only Layer

Status: completed

作用：
- 为未来完整性/回放校验差异报告建立只读准备审计层。
- 明确差异分类、严重级别、阻断决策、证据关联、操作者提示、机器可读结构、脱敏和 UI 呈现这些合约要求。
- 保持真实执行链路关闭，避免在审计准备阶段误读事件、误生成报告或误做阻断决策。

Implemented:
- Added `runner_verification_discrepancy_report_audit.py`.
- Added `GET /api/project/runner-verification-discrepancy-report-audits`.
- Added bootstrap payload `runner_verification_discrepancy_report_audits`.
- Added Runner Workbench stage `差异报告`.
- Added onboarding section `Runner 校验差异报告实现准备审计`.
- Added realistic sample verification coverage.

Verification:
```text
python ast ok 81
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
python tools/verify_realistic_samples.py ok
git diff --check ok
compileall ok
API schema=project_runner_verification_discrepancy_report_audits.v1
API status=no_saved_profiles
launchable_count=0
audit_only=True
generates_discrepancy_reports=False
makes_blocking_decisions=False
reads_runner_events=False
UI runner stage count=38
UI mojibake=false
```

Boundary:
- No real launch API.
- No command execution.
- No process creation.
- No runner event read/write.
- No audit log read/write.
- No integrity/replay execution.
- No discrepancy report generation.
- No blocking decision.
- No user project modification.

Next suggestion:

Add a “Runner real-launch final read-only gate preparation audit” layer.

作用：aggregate all previous read-only runner audit layers into one final pre-launch gate, so future implementation can see exactly which evidence remains missing and which hard blocks still prevent real launch.

## 2026-07-04 - Runner Real Launch Final Gate Audit Read-Only Layer

Status: completed

作用：
- Add the final read-only pre-launch gate for the Runner governance chain.
- Aggregate prerequisite layers, missing evidence, blocked actions, API absence, authorization boundary, and safety invariants.
- Keep the real execution surface closed until a separate authorized implementation round exists.

Implemented:
- Added `runner_real_launch_final_gate_audit.py`.
- Added `GET /api/project/runner-real-launch-final-gate-audits`.
- Added bootstrap payload `runner_real_launch_final_gate_audits`.
- Added Runner Workbench stage `最终闸门`.
- Added onboarding section `Runner 真实启动最终闸门准备审计`.
- Added realistic sample verification coverage.

Verification:
```text
python ast ok 64
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
python tools/verify_realistic_samples.py ok
git diff --check ok
compileall ok
API schema=project_runner_real_launch_final_gate_audits.v1
API status=no_saved_profiles
required_layer_count=14
launchable_count=0
registered_endpoint_count=0
final_gate_decision_count=0
audit_only=True
registers_launch_api=False
enables_launch_ui=False
creates_process=False
makes_launch_decisions=False
UI runner stage count=39
UI mojibake=false
```

Boundary:
- No real launch/cancel/timeout POST API.
- No launch UI enablement.
- No command execution.
- No process creation.
- No adapter import or call.
- No runner session mutation.
- No stdout/stderr open/read/capture.
- No runner event read/write.
- No audit log or audit record read/write.
- No config snapshot read.
- No integrity/replay/check execution.
- No discrepancy report generation.
- No launch decision.
- No authorization collection/storage/permission grant.
- No log read/write.
- No config write.
- No user project modification.

Next suggestion:

Add a “Runner evidence index and gap navigation read-only layer”.

作用：turn the final gate blockers and missing evidence into a navigable index that maps each gap to its owning upstream layer and next remediation target, while still avoiding logs, processes, real launch APIs, and user-project mutation.

## 2026-07-04 - Runner Evidence Gap Index Read-Only Layer

Status: completed

作用：
- Convert final gate missing evidence, pre-launch blockers, and required layers into a navigable read-only index.
- Map each gap to an owning Runner Workbench stage, evidence group, source report, and remediation hint.
- Keep the index UI-only and side-effect free.

Implemented:
- Added `runner_evidence_gap_index.py`.
- Added `GET /api/project/runner-evidence-gap-indexes`.
- Added bootstrap payload `runner_evidence_gap_indexes`.
- Added Runner Workbench stage `缺口索引`.
- Added onboarding section `Runner 证据索引与缺口导航`.
- Added realistic sample verification coverage.

Verification:
```text
python ast ok 65
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
python tools/verify_realistic_samples.py ok
git diff --check ok
compileall ok
API schema=project_runner_evidence_gap_indexes.v1
API status=no_saved_profiles
launchable_count=0
index_entry_count=0
navigation_target_count=0
unresolved_gap_count=0
audit_only=True
reads_log_files=False
reads_runner_events=False
registers_launch_api=False
creates_process=False
calls_execution_adapter=False
UI runner stage count=40
UI mojibake=false
```

Boundary:
- No command execution.
- No process creation.
- No launch/cancel/timeout POST API registration.
- No launch UI enablement.
- No adapter import or call.
- No session mutation.
- No stdout/stderr open/read/capture.
- No runner event read/write.
- No audit log or audit record read/write.
- No config snapshot read.
- No integrity/replay/check execution.
- No discrepancy report generation.
- No launch decision.
- No authorization collection/storage/permission grant.
- No log read/write.
- No config write.
- No user project modification.

Next suggestion:

Add a “Runner gap navigation UI linking read-only layer”.

作用：make evidence index entries select their owning Runner Workbench stage and open the relevant evidence group/blocker location, while only changing UI selection state and never touching logs, processes, real launch APIs, or user-project files.

## 2026-07-04 - Runner Gap Navigation UI Linking Read-Only Layer

Status: completed

作用：
- Turn evidence gap index entries into clickable Runner Workbench navigation targets.
- Let a gap entry select its owning stage and open the matching evidence group.
- Keep the behavior UI-only and side-effect free.

Implemented:
- Added `reports[].index_entries[]` normalization in `runner-workbench.js`.
- Added gap target rendering with `data-runner-gap-target`, `data-stage-key`, `data-evidence-title`, and `data-item-key`.
- Added delegated click handling that reuses existing stage selection and evidence group opening.
- Added compact gap target CSS.
- Added `_project_runner_real_launch_audit_chain()` in `server.py` to remove repeated recursive downstream Runner audit construction for final-gate and evidence-index endpoints.

Root cause:
- UI: backend navigation fields existed, but the frontend rendered index entries only as plain report evidence text.
- API latency: `/api/project/runner-evidence-gap-indexes` rebuilt the downstream Runner audit chain recursively, taking about 21.774 seconds in direct timing before optimization.

Verification:
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
python -m compileall -q src ok
python tools/verify_realistic_samples.py ok
git diff --check ok
direct evidence gap endpoint builder timing=0.702s
API schema=project_runner_evidence_gap_indexes.v1
API status=no_saved_profiles
launchable_count=0
executes_commands=False
creates_process=False
evidence_gap_index_only=True
synthetic UI click runner_evidence_gap_indexes -> runner_launch_api_contracts
opened evidence group=阻断动作
UI runner stage count=40
UI evidence index stage exists=true
UI mojibake=false
```

Service:
```text
http://127.0.0.1:8765/
PID: 62748
```

Boundary:
- No command execution.
- No process creation.
- No launch/cancel/timeout POST API registration.
- No launch UI enablement.
- No adapter import or call.
- No session mutation.
- No stdout/stderr open/read/capture.
- No runner event read/write.
- No audit log or audit record read/write.
- No config snapshot read.
- No integrity/replay/check execution.
- No discrepancy report generation.
- No launch decision.
- No authorization collection/storage/permission grant.
- No log read/write.
- No config write.
- No user project modification.

Next suggestion:

Add a “Runner config schema stabilization read-only layer”.

作用：define versioned `flowtrace.runner.json` fields, default-disabled policy, compatibility rules, and validation error mapping before real testing, while still avoiding config creation, command execution, and launch API exposure.

## 2026-07-04 - Runner Config Schema Stabilization Read-Only Layer

Status: completed

作用：
- Stabilize the future `flowtrace.runner.json` schema as `flowtrace_runner_config.v1`.
- Define default-disabled behavior, field contracts, compatibility rules, and validation error codes.
- Give future UI and real-test readiness layers one stable contract to reference without creating config files or enabling launch.

Implemented:
- Added `runner_config_schema_stabilization.py`.
- Added `GET /api/project/runner-config-schema-stabilizations`.
- Added bootstrap payload `runner_config_schema_stabilizations`.
- Added Runner Workbench stage `配置 Schema`; stage count is now 41.
- Added onboarding section `Runner 配置 Schema 稳定化`.
- Added the layer to governance readiness; governance layer count is now 19.
- Added realistic sample verification coverage.

Verification:
```text
python -m compileall -q src tools ok
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
python tools/verify_realistic_samples.py ok
git diff --check ok
API schema=project_runner_config_schema_stabilizations.v1
API status=no_saved_profiles
launchable_count=0
stable_schema_count=1
field_contract_count=13
compatibility_rule_count=8
error_code_count=11
executes_commands=False
creates_process=False
reads_config_file=False
writes_config_file=False
launch_enabled=False
launch_api_available=False
bootstrap includes new payload=true
governance_layer_count=19
UI runner stage count=41
UI config schema stage exists=true
UI onboarding section exists=true
UI stable schema version visible=true
UI mojibake=false
```

Service:
```text
http://127.0.0.1:8765/
PID: 15572
```

Boundary:
- No command execution.
- No process creation.
- No launch/cancel/timeout POST API registration.
- No launch UI enablement.
- No adapter import or call.
- No session mutation.
- No stdout/stderr open/read/capture.
- No runner event read/write.
- No audit log or audit record read/write.
- No config snapshot read.
- No direct config file read in this layer.
- No config creation or write.
- No launch decision.
- No authorization collection/storage/permission grant.
- No user project modification.

Next suggestion:

Add a “Runner config compatibility report read-only layer”.

作用：use the stabilized `flowtrace_runner_config.v1` field contract to produce a compatibility report for candidate configs, mapping missing fields, type mismatches, defaults, and version issues to stable error codes before real testing; still no config creation, command execution, or launch API exposure.
## 2026-07-04 - Runner Config Compatibility Report Read-Only Layer

Status: completed

作用：
- Use the stabilized `flowtrace_runner_config.v1` field contract to produce compatibility reports for candidate Runner config payloads.
- Detect unsupported versions, missing required fields, type mismatches, default-policy violations, and stable error-code mappings before real testing.
- Keep the layer read-only: no config creation, no command execution, no process creation, and no launch API exposure.

Implemented:
- Added `src/flowtrace/runner_config_compatibility_report.py`.
- Added `GET /api/project/runner-config-compatibility-reports`.
- Added bootstrap payload `runner_config_compatibility_reports`.
- Added Runner Workbench stage `配置兼容`; stage count is now 42.
- Added onboarding section `Runner 配置兼容性报告`.
- Added the layer to governance readiness; governance layer count is now 20.
- Extended `tools/verify_realistic_samples.py` coverage for empty and saved-config paths.

Verification:
```text
python -m compileall -q src tools ok
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
python tools/verify_realistic_samples.py ok
git diff --check ok
API schema=project_runner_config_compatibility_reports.v1
API status=no_saved_profiles
launchable_count=0
compatibility_issue_count=0
missing_field_count=0
type_mismatch_count=0
reads_config_file=False
uses_in_memory_config_payload=True
writes_config_file=False
executes_commands=False
creates_process=False
launch_enabled=False
bootstrap includes new payload=true
governance_layer_count=20
realistic saved config status=compatibility_report_required
realistic saved config issue_count=4
realistic saved config missing_field_count=4
UI config compatibility stage exists=true
UI onboarding section exists=true
UI mojibake=false
```

Service:
```text
http://127.0.0.1:8765/
PID: 61056
```

Boundary:
- No command execution.
- No process creation.
- No launch/cancel/timeout POST API registration.
- No launch UI enablement.
- No adapter import or call.
- No Runner session creation or mutation.
- No stdout/stderr open/read/capture.
- No runner event read/write.
- No audit log or audit record read/write.
- No config snapshot read.
- No direct config file read in this layer; it consumes the in-memory payload from the existing config-check layer.
- No config creation or write.
- No authorization collection/storage/permission grant.
- No user project modification.

Next suggestion:

Add a `Runner config error-code navigation UI read-only layer`.

作用：turn compatibility-report issues into clickable UI navigation from error code and field path to the relevant schema contract and explanation, while only changing frontend selection state; still no config reads/writes, command execution, or real launch API exposure.
## 2026-07-04 - Runner Config Error-Code Navigation UI Read-Only Layer

Status: completed

作用：
- Turn Runner config compatibility issues into clickable UI navigation targets.
- Let onboarding issue buttons jump to Runner Workbench, select the config compatibility stage, open the config issue evidence group, and highlight the target item.
- Keep this as a UI-only read-only layer: no new API, no config reads/writes, no command execution, no process creation, and no launch API exposure.

Implemented:
- Added `navigation` metadata to compatibility issues.
- Added `reports[].index_entries[]` for config compatibility issue targets.
- Added `summary.issue_navigation_target_count`.
- Reused Runner Workbench stage selection and evidence-group expansion.
- Added onboarding issue target buttons that dispatch `flowtrace:runner-stage-target`.
- Added realistic sample assertions for navigation target coverage.

Verification:
```text
python -m compileall -q src tools ok
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
python tools/verify_realistic_samples.py ok
git diff --check ok
saved config issue_count=4
saved config issue_navigation_target_count=4
API schema=project_runner_config_compatibility_reports.v1
API current status=no_saved_profiles
API current issue_navigation_target_count=0
executes_commands=False
creates_process=False
reads_config_file=False
writes_config_file=False
browser hasOpenFunction=True
browser selectedStageKey=runner_config_compatibility_reports
browser runnerTabActive=True
browser mojibake=False
```

Service:
```text
http://127.0.0.1:8765/
PID: 19168
```

Boundary:
- No command execution.
- No process creation.
- No launch/cancel/timeout POST API registration.
- No launch UI enablement.
- No adapter import or call.
- No Runner session creation or mutation.
- No stdout/stderr open/read/capture.
- No runner event read/write.
- No audit log or audit record read/write.
- No config snapshot read.
- No direct config file read; this layer consumes existing compatibility report payload.
- No config creation or write.
- No authorization collection/storage/permission grant.
- No user project modification.

Next suggestion:

Add a `Runner config remediation summary read-only layer`.

作用：group config compatibility issues by field, error code, and stable schema contract into a repair checklist before real testing; still recommendation-only, with no config writes, command execution, or real launch API exposure.
## 2026-07-04 - Runner Config Remediation Summary Read-Only Layer

Status: completed

作用：group config compatibility issues by field, error code, and stable schema contract into manual remediation recommendations. It consumes only compatibility reports and still performs no config reads/writes, command execution, process creation, or launch API exposure.

Implemented:
- Added `runner_config_remediation_summary.py`.
- Added `GET /api/project/runner-config-remediation-summaries`.
- Added bootstrap, onboarding, Runner Workbench, and governance readiness integration.

Minimal verification:
```text
compileall ok
node --check app/onboarding/runner-workbench ok
verify_realistic_samples.py ok
saved config remediation_status=remediation_required
saved config recommendation_count=4
API current status=no_saved_profiles
launchable_count=0
executes_commands=False
creates_process=False
reads_config_file=False
writes_config_file=False
browser stageCount=43
browser hasRemediationStage=True
browser mojibake=False
```

Service: `http://127.0.0.1:8765/`, PID `2044`.

Next suggestion: Runner config remediation navigation read-only layer.
作用：make remediation items jump back to the matching compatibility issue evidence and field contract, UI-only with no config writes or execution.
## 2026-07-04 - Runner Config Remediation Navigation Read-Only Layer

Status: completed

作用：add navigation metadata to remediation recommendations and render them as existing Runner stage-target buttons, UI-only with no config writes or execution.

Minimal verification:
```text
compileall ok
node --check onboarding ok
verify_realistic_samples.py ok
API status=no_saved_profiles
launchable_count=0
executes_commands=False
reads_config_file=False
writes_config_file=False
browser hasRemediationSection=True
browser mojibake=False
```

Service: `http://127.0.0.1:8765/`, PID `46200`.

Next suggestion: Runner config field contract explanation read-only layer.
作用：show stable schema field types, defaults, and error codes as a standalone explanation view for manual fixes; no config writes or execution.
