# FlowTrace 架构层级边界

本文档用于固化 FlowTrace 的长期层级边界。后续修 bug 时默认在既有层级内解决，不允许因为单个 bug 随意增加新层级。

## 层级总览

```text
用户项目
  -> Adapter 接入层
  -> Runtime Context 层
  -> Instrumentation 采集层
  -> Contract / Privacy 层
  -> Storage 层
  -> Project Scanner 层
  -> Analysis 层
  -> Service API 层
  -> UI 层
  -> Export / Diagnostics 层
```

## 层级职责

### 1. Adapter 接入层

职责：

```text
把不同运行入口接到 FlowTrace
```

包括：

```text
手动装饰器
CLI run
pytest
FastAPI
Flask
未来浏览器/IDE 触发入口
```

不负责：

```text
分析数据流
决定 workflow
渲染 UI
写复杂业务逻辑
```

### 2. Runtime Context 层

职责：

```text
维护当前 run / trace / span 上下文
```

不负责：

```text
存储文件
解释事件
扫描项目
```

### 3. Instrumentation 采集层

职责：

```text
记录方法输入、输出、异常、耗时和调用关系
```

不负责：

```text
生成前端图
判断业务正确性
推断未运行 workflow
```

### 4. Contract / Privacy 层

职责：

```text
契约校验
字段 diff
快照脱敏
快照大小控制
```

不负责：

```text
存储运行记录
渲染差异 UI
推断调用图
```

### 5. Storage 层

职责：

```text
原始事件写入
运行记录读取
索引缓存
```

原则：

```text
原始事件可信。
分析结果可重建。
```

不负责：

```text
分析事件
扫描源码
生成业务解释
```

### 6. Project Scanner 层

职责：

```text
读取用户项目
扫描模块、类、函数、入口候选、import 关系
生成 project model
```

不负责：

```text
证明真实 workflow
替代运行时采集
决定参数是否正确
```

### 7. Analysis 层

职责：

```text
把原始事件和 project model 解释成可展示结构
```

包括：

```text
dataflow
layers
issues
summary
compare
coverage
onboarding
readiness
```

不负责：

```text
写原始事件
处理 HTTP
操作 DOM
修改用户项目
替用户做最终 workflow 决策
```

约束：

```text
onboarding 只输出接入建议。
readiness 只输出接入状态判断。
二者都只能消费 scanner / storage / interpretation 的确定性结果。
LLM 后续只能作为辅助解释层，不允许替代 readiness 的硬判断。
```

### 8. Service API 层

职责：

```text
暴露本地 HTTP API
提供静态前端资源
组织请求参数
返回标准 JSON
```

不负责：

```text
直接修改分析逻辑
直接拼 UI
直接扫描项目细节
```

### 9. UI 层

职责：

```text
展示 API 返回的数据
提供用户交互
保存纯前端布局状态
```

不负责：

```text
重新推断 workflow
修改原始事件
决定运行事实
```

### 10. Export / Diagnostics 层

职责：

```text
导出可复现记录包
检查环境、端口、路径、配置、数据可读性
```

不负责：

```text
业务分析
前端展示
采集事件
```

## 依赖方向

允许方向：

```text
Adapter -> Runtime -> Instrumentation -> Contract/Privacy -> Storage
Project Scanner -> Analysis
Storage -> Analysis
Analysis -> Service API -> UI
Diagnostics -> 各层只读检查
Export -> Storage / Analysis / Project Scanner
```

禁止方向：

```text
UI -> Storage 直接读写
UI -> Instrumentation
Storage -> UI
Instrumentation -> UI
Scanner -> UI
Analysis -> DOM
Contract -> HTTP
```

## Bug 归属表

| 问题类型 | 默认归属层 |
| --- | --- |
| 方法没有被记录 | Adapter / Instrumentation |
| run_id 丢失 | Runtime Context |
| 输入输出快照不对 | Instrumentation / Privacy |
| 契约判断错误 | Contract |
| JSONL 丢失或读不出 | Storage |
| 项目函数没扫出来 | Project Scanner |
| 数据流边不对 | Analysis |
| 层级归类不对 | Analysis / Project Scanner |
| API 返回结构不对 | Service API |
| 前端显示/拖拽/缩放错误 | UI |
| 启动失败 | Diagnostics / CLI |
| 导出包不完整 | Export |

## 新增层级准入规则

默认不允许为单个 bug 增加新层级。

只有同时满足以下条件，才允许新增层级：

```text
1. 出现新的稳定职责，不属于现有任何层级。
2. 该职责至少被两个以上模块复用。
3. 该职责有独立输入、输出和测试方式。
4. 不新增层级会导致现有层级职责明显混乱。
5. 已在 docs/ARCHITECTURE_LAYERS.md 中更新边界。
```

如果只是 bug：

```text
先定位归属层。
在归属层修复。
补测试或复现记录。
不新增抽象。
```

## 层级收敛原则

每个层级都必须能回答：

```text
我输入什么？
我输出什么？
我不负责什么？
谁可以调用我？
我可以调用谁？
如何验证我没有坏？
```

回答不清楚时，不允许继续扩展该层级。
