# support_ticket

异步客服工单仿真实项目，用于验证 async workflow：

```text
api.receive_ticket -> service.classify_ticket -> service.assign_ticket
```

该样本保留了一个轻微契约变化：分类方法会将 `severity` 标准化为 `priority`，用于观察字段名变化。

