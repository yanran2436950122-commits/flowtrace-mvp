# FlowTrace 仿真实项目样本

这些样本用于验证真实项目接入闭环。它们不是最小 demo，而是刻意模拟常见业务项目结构：

- `ecommerce_checkout/`：前端表单 -> API -> 服务 -> 仓储的订单提交流程。
- `inventory_cli/`：命令行库存调拨流程，包含库存读取、校验、写入。
- `support_ticket/`：异步客服工单流程，包含分类、优先级计算和派单。

运行样本时，请把 FlowTrace 源码目录和样本项目根目录同时加入 `PYTHONPATH`，并在样本项目根目录执行入口文件。这样 `.flowtrace/` 会写入样本项目内部，viewer 可以直接选择该样本作为目标项目。

示例：

```powershell
cd D:\pyProject\flowtrace-mvp\examples\realistic_projects\ecommerce_checkout
$env:PYTHONPATH = "D:\pyProject\flowtrace-mvp\src;."
python checkout\main.py
```

然后在 FlowTrace viewer 的“项目接入”中选择：

```text
目标项目：D:\pyProject\flowtrace-mvp\examples\realistic_projects\ecommerce_checkout
运行记录：D:\pyProject\flowtrace-mvp\examples\realistic_projects\ecommerce_checkout\.flowtrace
```

