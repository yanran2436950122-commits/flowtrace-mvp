# FlowTrace MVP 验收记录

更新时间：2026-06-29 13:58:00 +08:00

## 验收结论

MVP 功能闭环已完成。

当前状态：

```text
MVP 已达到可本地运行、可采集、可解释、可视化排查的最小可用闭环。
```

建议阶段：

```text
进入 MVP 人工 UI 验收与细节打磨阶段。
```

## 已通过项

### 1. 示例运行

命令：

```powershell
$env:PYTHONPATH = "src"
python examples\order_flow.py
```

结果：

```text
通过。
示例订单提交流程可以写入本地运行记录。
```

### 2. 模拟输入

命令：

```powershell
$env:PYTHONPATH = "src;examples"
python examples\simulated_inputs.py
```

结果：

```text
通过。
生成 3 个场景：
- 管理员带优惠券：ok
- 普通用户无优惠券：ok
- 缺少用户 ID：error
```

### 3. Python 编译检查

命令：

```powershell
$env:PYTHONPATH = "src"
python -m compileall -q src examples
```

结果：

```text
通过。
```

### 4. 前端 JS 语法检查

命令：

```powershell
Get-ChildItem -Path src\flowtrace\ui -Recurse -Filter *.js | ForEach-Object { node --check $_.FullName }
```

结果：

```text
通过。
```

### 5. 核心解释层数据

最新验收运行：

```text
订单模拟输入 - 缺少用户 ID
```

结果：

```json
{
  "events": 8,
  "dataflow_nodes": 2,
  "dataflow_edges": 2,
  "layer_nodes": 6,
  "layer_edges": 2,
  "summary_layer_count": 6,
  "summary_status": "error",
  "issue_total": 3,
  "compare_count": 5
}
```

### 6. HTTP API

已验证接口：

```text
GET /api/runs
GET /api/runs/{run_id}/events
GET /api/runs/{run_id}/dataflow
GET /api/runs/{run_id}/layers
GET /api/runs/{run_id}/summary
GET /api/runs/{run_id}/issues
GET /api/runs/{run_id}/compare
```

结果：

```text
通过。
summary.layer_count 已与 layers.nodes.length 对齐。
```

### 7. 前端静态资源

已验证资源：

```text
/
/app.js
/styles.css
/modules/components/layers.js
/modules/components/watch.js
/modules/components/expanded-dataflow.js
/modules/components/issues.js
/modules/components/comparison.js
```

结果：

```text
通过。
服务端可正确返回页面与关键前端模块。
```

## 本轮修复

验收中发现：

```text
/layers 使用静态扫描方法目录。
/summary 原先只使用当前运行事件。
```

这会导致顶部摘要中的层级数与层级流转视图不一致。

已修复：

```text
interpretation.build_run_summary(...) 增加 method_catalog 可选参数。
server.py 的 /summary API 传入与 /layers 相同的方法目录。
```

修复后：

```text
layers.nodes.length = 6
summary.layer_count = 6
```

## 需要人工 UI 验收项

由于本轮 Codex in-app browser 控制通道多次报本地沙箱连接失败，以下内容需要用户在页面中手动点一遍：

```text
http://127.0.0.1:8765
```

建议人工确认：

- 左侧运行列表可切换运行。
- 顶部摘要与当前运行同步变化。
- `层级流转` 中节点可以拖动。
- 双击层级节点后，小窗在节点附近打开，并有关闭按钮。
- 小窗中的方法可以点击“监视”或拖入监视窗口。
- 监视窗口快照展开后不会自动折叠。
- 监视窗口快照滚动后不会因刷新回到顶部。
- 点击“锁定”后快照内容不再跟随刷新。
- 点击“跟随”后快照重新使用最新数据。
- `方法数据流`、`全量细节`、`问题列表`、`运行对比`、`事件流程` 页面可正常切换。

## 当前边界

当前 MVP 不声明支持：

- 任意语言自动接入。
- 自动识别所有项目 workflow。
- 远程团队协作。
- 生产级链路追踪。
- LLM 主导定位。

当前 MVP 声明支持：

- Python 本地项目的手动接入。
- 真实运行或模拟输入产生 trace。
- 参数流、契约、diff、问题聚合和本地可视化排查。

