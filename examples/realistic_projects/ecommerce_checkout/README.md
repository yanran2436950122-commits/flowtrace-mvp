# ecommerce_checkout

订单提交仿真实项目，用于验证跨层参数传递：

```text
frontend.validate_cart -> api.submit_checkout -> service.price_order -> repository.save_order
```

该样本故意保留一个参数问题：API 层会丢失 `customer_tier` 字段，服务层会因此用默认折扣策略继续执行。FlowTrace 应能在数据流与问题列表中暴露字段变化。

