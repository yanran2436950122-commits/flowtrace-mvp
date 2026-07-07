# inventory_cli

库存调拨仿真实项目，用于验证 CLI/脚本型项目：

```text
cli.parse_transfer -> inventory.validate_transfer -> inventory.reserve_stock -> inventory.commit_transfer
```

该样本覆盖“脚本入口 + 业务函数 + 仓储写入”的路径，适合验证没有 Web 框架的项目能否被正确读取。

