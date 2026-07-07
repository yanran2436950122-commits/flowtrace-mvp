# 仿真实项目样本

## 目标

这些样本用于验证 FlowTrace 的真实项目接入闭环：

```text
选择目标项目 -> 静态扫描 -> 运行样本流程 -> 读取 .flowtrace -> 覆盖对齐 -> 参数流分析
```

样本不是单文件 demo，而是模拟用户项目的目录结构、入口文件和业务分层。它们用于后续开发接入状态模型、自动审查和运行覆盖验收。

## 样本列表

### ecommerce_checkout

位置：

```text
D:\pyProject\flowtrace-mvp\examples\realistic_projects\ecommerce_checkout
```

业务形态：

```text
frontend.validate_cart -> api.submit_checkout -> service.price_order -> repository.save_order
```

覆盖重点：

- 前端表单到 API 的参数传递。
- API 层丢失字段后的下游默认策略。
- 跨层 contract 和字段差异检查。

运行：

```powershell
cd D:\pyProject\flowtrace-mvp\examples\realistic_projects\ecommerce_checkout
$env:PYTHONPATH = "D:\pyProject\flowtrace-mvp\src;."
python checkout\main.py
```

### inventory_cli

位置：

```text
D:\pyProject\flowtrace-mvp\examples\realistic_projects\inventory_cli
```

业务形态：

```text
cli.parse_transfer -> inventory.validate_transfer -> inventory.reserve_stock -> inventory.commit_transfer
```

覆盖重点：

- CLI/脚本型项目接入。
- 无 Web 框架项目的入口识别。
- 库存读取、校验、写入的参数传递。

运行：

```powershell
cd D:\pyProject\flowtrace-mvp\examples\realistic_projects\inventory_cli
$env:PYTHONPATH = "D:\pyProject\flowtrace-mvp\src;."
python inventory\main.py
```

### support_ticket

位置：

```text
D:\pyProject\flowtrace-mvp\examples\realistic_projects\support_ticket
```

业务形态：

```text
api.receive_ticket -> service.classify_ticket -> service.assign_ticket
```

覆盖重点：

- async workflow 接入。
- 异步函数 trace_node 包装。
- 字段语义从 `severity` 到 `priority` 的变化。

运行：

```powershell
cd D:\pyProject\flowtrace-mvp\examples\realistic_projects\support_ticket
$env:PYTHONPATH = "D:\pyProject\flowtrace-mvp\src;."
python support\main.py
```

## Viewer 接入方式

运行样本后，在 FlowTrace viewer 的“项目接入”中选择对应路径：

```text
目标项目：样本项目根目录
运行记录：样本项目根目录\.flowtrace
```

示例：

```text
目标项目：D:\pyProject\flowtrace-mvp\examples\realistic_projects\ecommerce_checkout
运行记录：D:\pyProject\flowtrace-mvp\examples\realistic_projects\ecommerce_checkout\.flowtrace
```

## 当前验证结果

```text
ecommerce_checkout: 1 run, 14 events, 5/5 methods covered
inventory_cli: 1 run, 14 events, 5/5 methods covered
support_ticket: 1 run, 12 events, 4/4 methods covered
```

这些样本后续应作为固定回归对象，避免真实项目接入能力只依赖 FlowTrace 自身项目或单文件 demo。

