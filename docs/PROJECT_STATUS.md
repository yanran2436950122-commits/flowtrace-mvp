# FlowTrace 项目进度

## 当前状态

FlowTrace MVP 已从“运行记录可视化”推进到“真实项目接入诊断”阶段。

当前闭环：

```text
选择目标项目 -> 扫描项目结构 -> 读取运行记录 -> 生成覆盖状态 -> 生成接入状态 -> 生成自动审查报告 -> 生成接入计划 -> 前端展示
```

## 已完成功能

### 本地运行采集

- `trace_node` 装饰器采集函数输入、输出、异常、耗时和调用关系。
- `contract` 定义输入/输出契约。
- `start_run` 与 `record_user_action` 记录一次真实或模拟流程。
- `.flowtrace/runs/*/events.jsonl` 存储运行事件。

### 运行分析

- 方法级数据流。
- 层级流转。
- 全量细节。
- 问题列表。
- 运行对比。
- 监视窗口。

### 真实项目接入

- 前端支持选择目标项目、运行记录目录和配置文件。
- 后端支持运行时切换 `ProjectContext`。
- 项目结构页展示项目摘要、入口候选、模块列表、覆盖状态和扫描错误。

### 接入诊断

- `readiness.py` 输出接入状态。
- `/api/project/readiness` 返回项目是否可用于排查、覆盖情况、缺契约、运行风险和下一步动作。
- 接入向导展示接入状态。

### 自动审查

- `audit.py` 输出确定性审查报告。
- `/api/project/audit` 返回问题清单、严重级别、归属层级、目标、证据和推荐动作。
- 接入向导展示自动审查区块。
- 自动审查条目可点击，并在事件详情面板展示定位信息、证据、建议动作和原始审查项。

### 接入计划

- `integration_plan.py` 输出确定性接入计划。
- `/api/project/integration-plan` 返回执行入口候选、接入阶段、阻断项、验收门和下一步动作。
- 接入向导展示接入计划区块。
- `tools/verify_realistic_samples.py` 已将接入计划纳入样本验收。

### 运行配置草案

- `run_profile.py` 输出运行配置草案。
- `/api/project/run-profiles` 返回命令草案、工作目录、环境变量和安全边界。
- 接入向导展示运行配置草案。
- `run_profile_store.py` 支持保存、恢复、取消保存用户确认过的草案。
- 当前只生成和保存草案，不执行命令，不写入用户源码。

### 执行前安全预检

- `run_preflight.py` 输出执行前安全预检报告。
- `/api/project/run-preflight` 返回已保存运行配置的预检状态、检查项和下一步动作。
- 接入向导展示执行前安全预检。
- 当前只预检，不执行命令。

### 预检确认状态

- `run_confirmation_store.py` 保存用户对预检报告的确认状态。
- `/api/project/run-preflight/confirm` 确认预检报告。
- `/api/project/run-preflight/revoke` 撤销确认。
- 确认状态绑定 profile 指纹；配置变化后确认会失效。
- 当前只记录确认，不执行命令。

### 测试样本

- `ecommerce_checkout`：订单提交流程。
- `inventory_cli`：CLI 库存调拨流程。
- `support_ticket`：异步客服工单流程。
- `tools/verify_realistic_samples.py` 固化样本验收。

## 当前边界

```text
scanner.py      -> 静态项目模型
interpretation.py -> 运行事件解释
readiness.py    -> 接入状态判断
audit.py        -> 自动审查问题清单
integration_plan.py -> 真实项目接入计划
run_profile.py -> 运行配置草案
run_profile_store.py -> 运行配置草案保存/恢复
run_preflight.py -> 执行前安全预检
run_confirmation_store.py -> 预检确认状态
server.py       -> API 聚合与静态资源
ui/             -> 展示与交互
```

约束：

- UI 不直接推断 workflow。
- server 不承载业务判断规则。
- readiness 只判断接入状态。
- audit 只输出审查问题，不修改用户项目。
- integration_plan 只编排接入路线，不扫描项目、不修改用户项目、不执行命令。
- run_profile 只生成命令草案，不执行命令。
- run_profile_store 只写入 trace 目录下的 FlowTrace 配置资产，不写用户源码。
- run_preflight 只生成执行前预检报告，不执行命令。
- run_confirmation_store 只保存预检确认状态，不执行命令。
- LLM 后续只能作为辅助解释，不替代确定性判断。

## 下一步开发步骤

1. 运行配置 / 命令配置
   - 当前已能从入口候选生成命令草案。
   - 当前已支持保存/恢复用户确认过的 run profile。

2. 自动运行前安全预检
   - 当前已检查命令工作目录、argv、入口文件、trace 目录和确认门。
   - 下一步若进入执行能力，必须先增加用户确认页面。
   - 禁止 FlowTrace 在未确认时修改用户项目。

3. 浏览器真实输入录制
   - 为 Web 项目记录用户真实页面操作。
   - 将录制结果转成可重复执行的流程。

4. 缺 contract 辅助生成
   - 根据已观察到的输入/输出快照生成 contract 草案。
   - 只生成建议，不自动写入用户项目。

5. 审查结果深度定位
   - 当前已支持点击 finding 展开详情。
   - 下一步需要从详情进一步跳转到数据流边、运行记录或项目结构位置。

6. 自动审查回归强化
   - 扩展 `tools/verify_realistic_samples.py`，断言具体 finding 类型。
   - 增加空项目、无运行记录、扫描错误项目样本。

## 尚需完善功能

- 自动运行用户项目仍未实现；当前需要用户自己跑流程。
- Run profile 草案、保存、恢复、执行前安全预检已实现；命令执行能力还未实现。
- 预检确认状态和最终执行确认门已实现；runner 还未实现。
- 浏览器/前端真实输入录制还未实现。
- Contract 草案生成还未实现。
- 审查结果已能点击展开详情，但尚不能自动聚焦图节点、数据流边或源文件位置。
- 多语言项目扫描还未支持，当前重点是 Python。
- 大型项目扫描性能和缓存还未工程化。
- 项目配置文件 schema 还不完整。
- UI 视觉验证受当前本地浏览器沙箱影响，仍需人工确认。
- 缺少正式 `tests/` 单元测试目录，目前依赖 `tools/verify_realistic_samples.py` 作为验收脚本。

## 2026-07-01 更新：最终执行确认门

### 已完成

- `run_final_confirmation_store.py` 保存最终执行确认状态。
- `run_execution_gate.py` 输出 `project_run_execution_gate.v1`。
- `/api/project/run-execution-gate` 返回最终执行门报告。
- `/api/project/run-execution-gate/confirm` 记录最终确认。
- `/api/project/run-execution-gate/revoke` 撤销最终确认。
- 接入向导展示“最终执行确认”区块。
- `tools/verify_realistic_samples.py` 已覆盖最终确认、撤销最终确认和不执行命令断言。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认
```

### 新增边界

```text
run_execution_gate.py -> 最终执行门报告
run_final_confirmation_store.py -> 最终执行确认状态
```

硬性约束：
- 最终执行确认不执行命令。
- 最终执行确认不等同于 runner。
- 预检未确认时不能最终确认。
- runner 后续必须单独设计，不能并入 run profile、preflight 或 confirmation store。

### 下一步

1. 设计独立 runner 的隔离边界。
2. 设计执行日志结构和进程生命周期状态。
3. 在前端最终执行门之后增加二次确认按钮，但只有 runner 边界审计通过后才能接入真实执行。
4. 继续保留真实样例验收，确保任何执行能力不会绕过预检与最终确认。

## 2026-07-01 更新：Runner 隔离设计报告

### 已完成

- `runner_plan.py` 输出 `project_runner_plan.v1`。
- `/api/project/runner-plan` 返回 runner 隔离设计报告。
- 接入向导展示“Runner 隔离设计”区块。
- Runner 设计报告包含隔离策略、生命周期状态、日志计划、失败回收策略和前置检查。
- `tools/verify_realistic_samples.py` 已覆盖 runner plan 的不执行命令断言。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告
```

### 新增边界

```text
runner_plan.py -> runner 隔离设计报告
```

硬性约束：
- runner plan 不执行命令。
- runner plan 不代表 runner 已实现。
- runner plan 只写明未来 runner 的隔离、日志、生命周期和失败回收策略。
- 后续真实 runner 必须继续沿用预检确认和最终确认门。

### 下一步

1. 设计执行请求草案存储，仍不执行命令。
2. 设计二次确认 UI，明确点击后才进入真实 runner。
3. 设计 runner 进程日志事件 schema。
4. 完成以上审计后，再实现最小 runner。

## 2026-07-01 更新：执行请求草案与二次确认

### 已完成

- `execution_request_store.py` 保存执行请求草案和二次确认状态。
- `execution_request.py` 输出 `project_execution_requests.v1`。
- `/api/project/execution-requests` 返回执行请求报告。
- `/api/project/execution-requests/prepare` 准备执行请求草案。
- `/api/project/execution-requests/confirm` 记录二次确认。
- `/api/project/execution-requests/revoke` 撤销二次确认。
- `/api/project/execution-requests/remove` 移除请求草案。
- 接入向导展示“执行请求草案”区块。
- `tools/verify_realistic_samples.py` 已覆盖请求准备、二次确认、撤销和移除。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认
```

### 新增边界

```text
execution_request.py -> 执行请求报告
execution_request_store.py -> 执行请求草案与二次确认状态
```

硬性约束：
- 执行请求草案不执行命令。
- 二次确认不执行命令。
- 二次确认不等于 runner。
- 后续真实执行必须由独立 runner API 承担，不能并入 execution_request 模块。

### 下一步

1. 设计 runner 最小不可执行骨架。
2. 固化 runner 事件 schema。
3. 设计取消、超时、失败保留日志策略。
4. 通过审计后再考虑真实进程启动。

## 2026-07-01 更新：Runner 会话草案与事件 schema

### 已完成

- `runner_session_store.py` 保存 runner 会话草案。
- `runner_session.py` 输出 `project_runner_sessions.v1`。
- `/api/project/runner-sessions` 返回 runner 会话草案报告。
- `/api/project/runner-sessions/prepare` 生成会话草案。
- `/api/project/runner-sessions/remove` 移除会话草案。
- `runner_event_schema.v1` 固化未来 runner JSONL 事件字段、事件类型和 payload 规则。
- 接入向导展示“Runner 会话草案”区块。
- `tools/verify_realistic_samples.py` 已覆盖 runner 会话草案生成、移除和安全断言。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案
```

### 新增边界

```text
runner_session.py -> Runner 会话草案报告与事件 schema
runner_session_store.py -> Runner 会话草案状态
```

硬性约束：
- Runner 会话草案不执行命令。
- Runner 会话草案不创建进程。
- Runner 会话草案不等于真实 runner。
- Runner 会话草案只能基于已二次确认的执行请求生成。
- 后续真实执行必须由独立 runner API 承担，不能并入 runner_session 模块。

### 下一步

1. 设计启动前快照，固化 profile、preflight、final gate、execution request、runner session 的一致性证据。
2. 设计真实 runner API，但默认仍处于禁用或 dry-run 状态。
3. 设计取消、超时、stdout/stderr 分片和运行结束刷新策略。
4. 通过审计后再接入真实进程启动。

## 2026-07-01 更新：启动前快照

### 已完成

- `runner_launch_snapshot_store.py` 保存启动前快照。
- `runner_launch_snapshot.py` 输出 `project_runner_launch_snapshots.v1`。
- `/api/project/runner-launch-snapshots` 返回启动前快照报告。
- `/api/project/runner-launch-snapshots/prepare` 生成启动前快照。
- `/api/project/runner-launch-snapshots/remove` 移除启动前快照。
- `runner_launch_snapshot_schema.v1` 固化快照证据段和规则。
- 接入向导展示“启动前快照”区块。
- `tools/verify_realistic_samples.py` 已覆盖快照生成、上游会话移除后的 stale 状态、快照移除和安全断言。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照
```

### 新增边界

```text
runner_launch_snapshot.py -> 启动前快照报告与 schema
runner_launch_snapshot_store.py -> 启动前快照状态
```

硬性约束：
- 启动前快照不执行命令。
- 启动前快照不创建进程。
- 启动前快照不等于真实 runner。
- 启动前快照只能基于已生成的 runner 会话草案创建。
- 后续真实 runner API 必须消费启动前快照，不能绕过确认链路重新推断状态。

### 下一步

1. 设计 dry-run runner API。
2. dry-run runner API 只消费启动前快照，不启动真实进程。
3. 设计真实执行日志目录、stdout/stderr 分片、取消、超时和完成刷新策略。
4. 审计通过后再将 dry-run API 升级为可选真实执行。

## 2026-07-01 更新：Dry-run Runner API

### 已完成

- `runner_dry_run_store.py` 保存 dry-run runner 记录。
- `runner_dry_run.py` 输出 `project_runner_dry_runs.v1`。
- `/api/project/runner-dry-runs` 返回 dry-run runner 报告。
- `/api/project/runner-dry-runs/prepare` 生成 dry-run runner 记录。
- `/api/project/runner-dry-runs/remove` 移除 dry-run runner 记录。
- `runner_dry_run_schema.v1` 固化生命周期预览、输出分片策略和日志计划。
- 接入向导展示“Dry-run Runner”区块。
- `tools/verify_realistic_samples.py` 已覆盖 dry-run 生成、上游快照移除后的 stale 状态、dry-run 移除和安全断言。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner
```

### 新增边界

```text
runner_dry_run.py -> dry-run runner 报告与 schema
runner_dry_run_store.py -> dry-run runner 记录
```

硬性约束：
- Dry-run Runner 不执行命令。
- Dry-run Runner 不创建进程。
- Dry-run Runner 不创建 stdout/stderr 日志文件。
- Dry-run Runner 只能基于已生成的启动前快照创建。
- 后续真实 runner 必须有显式开关，默认禁用，且不能绕过 dry-run 与启动前快照。

### 下一步

1. 设计真实 runner 显式开关。
2. 细化 stdout/stderr 分片、最大日志大小、尾部摘要和前端展示策略。
3. 设计取消、超时和完成刷新机制。
4. 审计通过后再接入可选真实执行。

## 2026-07-01 更新：Runner 启动开关策略

### 已完成

- `runner_launch_control.py` 输出 `project_runner_launch_controls.v1`。
- `/api/project/runner-launch-controls` 返回 runner 启动开关策略报告。
- `runner_launch_control_schema.v1` 固化未来真实执行必须满足的显式开关条件。
- 接入向导展示“Runner 启动开关”只读区块。
- `tools/verify_realistic_samples.py` 已覆盖启动开关状态、安全断言和 `launchable_count=0`。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner -> Runner 启动开关策略
```

硬性约束：
- 不执行命令。
- 不创建进程。
- 不提供 POST API。
- 不写存储文件。
- 真实启动 API 当前不可用，`launchable_count` 必须为 0。

### 下一步

1. 细化 stdout/stderr 分片、最大日志大小、尾部摘要和前端展示策略。
2. 设计取消、超时和完成刷新机制。
3. 设计未来真实执行开关所需的配置文件字段和服务启动参数，但仍保持默认禁用。
4. 审计通过后再接入可选真实执行。
## 2026-07-01 更新：Runner 运行时策略

### 已完成

- `runner_runtime_policy.py` 输出 `project_runner_runtime_policies.v1`。
- `/api/project/runner-runtime-policies` 返回 Runner 运行时策略报告。
- `runner_runtime_policy_schema.v1` 固化输出分片、最大输出、尾部摘要、取消、超时和完成刷新规则。
- 接入向导展示“Runner 运行时策略”只读区块。
- `tools/verify_realistic_samples.py` 已覆盖运行时策略的安全断言和完整链路状态。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner -> Runner 启动开关策略 -> Runner 运行时策略
```

### 新增边界

```text
runner_runtime_policy.py -> Runner 运行时策略报告
```

硬性约束：
- Runner 运行时策略不执行命令。
- Runner 运行时策略不创建进程。
- Runner 运行时策略不创建 stdout/stderr 文件。
- Runner 运行时策略不写用户项目。
- Runner 运行时策略没有 POST API。
- Runner 运行时策略没有存储文件。
- 当前真实启动仍禁用，`launch_enabled=false`。

### 下一步

1. 设计未来真实执行所需的显式配置字段和服务启动开关。
2. 将真实执行配置继续做成只读报告或草案层，不直接执行。
3. 继续保持默认禁用真实执行，直到隔离、日志、取消、超时和完成刷新策略全部通过审计。
## 2026-07-01 更新：Runner 执行配置只读层

### 已完成

- `runner_execution_config.py` 输出 `project_runner_execution_configs.v1`。
- `/api/project/runner-execution-configs` 返回未来真实执行所需配置报告。
- `runner_execution_config_schema.v1` 固化配置文件名、服务开关、环境开关、确认短语、隔离和日志限制字段。
- 接入向导展示“Runner 执行配置”只读区块。
- 上游链路状态变化后，执行配置区块会同步刷新。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner -> Runner 启动开关策略 -> Runner 运行时策略 -> Runner 执行配置只读层
```

### 新增边界

```text
runner_execution_config.py -> Runner 执行配置需求报告
```

硬性约束：
- Runner 执行配置只读层不执行命令。
- Runner 执行配置只读层不创建进程。
- Runner 执行配置只读层不创建 stdout/stderr 文件。
- Runner 执行配置只读层不写 `flowtrace.runner.json`。
- Runner 执行配置只读层不写用户项目。
- Runner 执行配置只读层没有 POST API。
- Runner 执行配置只读层没有存储文件。
- 当前真实启动仍禁用，`launch_enabled=false`。

### 下一步

1. 设计真实执行配置文件解析草案，仍只读、不自动创建配置文件。
2. 设计服务启动参数审计，明确什么情况下允许真实执行开关存在。
3. 在审计通过前，不增加真实 launch API。

## 2026-07-01 更新：Runner 配置检查只读层

### 已完成

- `runner_execution_config_check.py` 输出 `project_runner_execution_config_checks.v1`。
- `/api/project/runner-execution-config-checks` 返回 Runner 配置检查报告。
- `runner_execution_config_check_schema.v1` 固化候选配置路径和必需字段。
- 接入向导展示“Runner 配置检查”只读区块。
- 配置检查候选路径包括目标项目根目录和 trace 目录下的 `flowtrace.runner.json`。
- `tools/verify_realistic_samples.py` 已覆盖缺少配置文件和临时合法配置文件两种状态。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner -> Runner 启动开关策略 -> Runner 运行时策略 -> Runner 执行配置只读层 -> Runner 配置检查只读层
```

### 新增边界

```text
runner_execution_config_check.py -> Runner 配置文件只读检查报告
```

硬性约束：
- Runner 配置检查只读层不执行命令。
- Runner 配置检查只读层不创建进程。
- Runner 配置检查只读层不创建 stdout/stderr 文件。
- Runner 配置检查只读层不创建 `flowtrace.runner.json`。
- Runner 配置检查只读层不修改 `flowtrace.runner.json`。
- Runner 配置检查只读层不写用户项目。
- Runner 配置检查只读层没有 POST API。
- Runner 配置检查只读层没有存储文件。
- 当前真实启动仍禁用，`launch_enabled=false`。

### 下一步

1. 设计服务启动参数审计层，确认 `--allow-real-execution` 与环境变量开关只能被只读审计。
2. 设计日志目录策略，明确未来 stdout/stderr 写入目录、大小限制和清理策略。
3. 在配置解析、服务开关审计、日志目录策略全部通过前，不增加真实 launch API。

## 2026-07-01 更新：Runner 服务开关审计只读层

### 已完成

- `runner_service_flag_audit.py` 输出 `project_runner_service_flag_audits.v1`。
- `/api/project/runner-service-flag-audits` 返回 Runner 服务开关审计报告。
- `runner_service_flag_audit_schema.v1` 固化未来真实执行所需的服务参数、环境开关、配置开关和确认短语。
- 接入向导展示“Runner 服务开关审计”只读区块。
- `tools/verify_realistic_samples.py` 已覆盖服务开关审计状态、安全断言和 `launchable_count=0`。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner -> Runner 启动开关策略 -> Runner 运行时策略 -> Runner 执行配置只读层 -> Runner 配置检查只读层 -> Runner 服务开关审计只读层
```

### 新增边界

```text
runner_service_flag_audit.py -> Runner 服务开关只读审计报告
```

硬性约束：
- Runner 服务开关审计只读层不执行命令。
- Runner 服务开关审计只读层不创建进程。
- Runner 服务开关审计只读层不创建 stdout/stderr 文件。
- Runner 服务开关审计只读层不创建或修改配置文件。
- Runner 服务开关审计只读层不读取 `os.environ`。
- Runner 服务开关审计只读层不解析 `process.argv`。
- Runner 服务开关审计只读层不写用户项目。
- Runner 服务开关审计只读层没有 POST API。
- Runner 服务开关审计只读层没有存储文件。
- 当前真实启动仍禁用，`launch_enabled=false`。

### 下一步

1. 设计 Runner 日志目录策略层，仍只读，明确未来 stdout/stderr 写入目录、文件命名、大小限制和清理规则。
2. 继续保持真实执行禁用，不增加 launch POST。
3. 后续再考虑真实执行前的最终审计汇总层。
## 2026-07-01 更新：Runner 日志目录策略只读层

当前最新能力：Runner 日志目录策略报告。

- 新增 `runner_log_directory_policy.py`，输出 `project_runner_log_directory_policies.v1`。
- 新增只读 API `GET /api/project/runner-log-directory-policies`。
- 前端 onboarding 已展示 “Runner 日志目录策略” 区块。
- 该层只声明未来 runner 日志候选目录、目录模板、未来文件名和路径约束。

硬边界：

- 不创建目录。
- 不打开日志文件。
- 不写日志。
- 不执行命令。
- 不创建进程。
- 不开放真实启动 API。
- 不写用户项目。

当前 live 验证：

- `status=no_saved_profiles`
- `launchable_count=0`
- `creates_log_directory=False`
- `opens_log_files=False`
- `writes_logs=False`
- `launch_enabled=False`
- `launch_api_available=False`

下一步建议：继续做 Runner 日志保留/轮转策略只读层，仍不得创建目录、写日志、执行命令或开放启动入口。
## 2026-07-01 更新：Runner 日志保留/轮转策略只读层

当前最新能力：Runner 日志保留/轮转策略报告。

- 新增 `runner_log_retention_policy.py`，输出 `project_runner_log_retention_policies.v1`。
- 新增只读 API `GET /api/project/runner-log-retention-policies`。
- 前端 onboarding 已展示 “Runner 日志保留策略” 区块。
- 该层只声明未来日志保留上限、轮转上限和清理规则。

硬边界：

- 不扫描日志目录。
- 不删除日志。
- 不轮转日志。
- 不重命名日志。
- 不截断日志。
- 不写日志。
- 不执行命令。
- 不创建进程。
- 不开放真实启动 API。

当前 live 验证：

- `status=no_saved_profiles`
- `launchable_count=0`
- `scans_log_directory=False`
- `deletes_logs=False`
- `rotates_logs=False`
- `renames_logs=False`
- `truncates_logs=False`
- `writes_logs=False`
- `launch_enabled=False`
- `launch_api_available=False`

下一步建议：继续做 Runner 日志清理预览只读层，只生成计划和风险提示，不枚举真实目录、不删除文件、不写日志、不执行命令。
## 2026-07-02 更新：Runner 日志清理预览只读层

当前最新能力：Runner 日志清理预览报告。

- 新增 `runner_log_cleanup_preview.py`，输出 `project_runner_log_cleanup_previews.v1`。
- 新增只读 API `GET /api/project/runner-log-cleanup-previews`。
- 前端 onboarding 已展示 “Runner 日志清理预览” 区块。
- 该层只基于日志保留策略生成未来清理预览规则、风险提示和确认要求。

硬边界：

- 不扫描日志目录。
- 不读取日志文件。
- 不删除日志。
- 不轮转日志。
- 不重命名日志。
- 不截断日志。
- 不写日志。
- 不执行命令。
- 不创建进程。
- 不开放真实启动 API。

当前 live 验证：

- `status=no_saved_profiles`
- `launchable_count=0`
- `previewed_deletion_count=0`
- `scans_log_directory=False`
- `reads_log_files=False`
- `deletes_logs=False`
- `rotates_logs=False`
- `renames_logs=False`
- `truncates_logs=False`
- `writes_logs=False`
- `launch_enabled=False`
- `launch_api_available=False`

下一步建议：继续做 Runner 日志清理确认只读层，只声明确认短语、确认范围和风险门槛，不执行任何清理动作。
## 2026-07-02 更新：Runner 配置检查只读层

### 已完成

- `runner_execution_config_check.py` 输出 `project_runner_execution_config_checks.v1`。
- `/api/project/runner-execution-config-checks` 返回配置文件只读检查报告。
- `runner_execution_config_check_schema.v1` 固化配置文件候选位置和必须字段。
- 接入向导展示“Runner 配置检查”只读区块。
- 验收脚本覆盖缺配置文件与临时合法配置两种状态。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner -> Runner 启动开关策略 -> Runner 运行时策略 -> Runner 执行配置只读层 -> Runner 配置检查只读层
```

### 新增边界

```text
runner_execution_config_check.py -> Runner 配置文件只读检查报告
```

硬性约束：
- Runner 配置检查只读层不执行命令。
- Runner 配置检查只读层不创建进程。
- Runner 配置检查只读层不创建 stdout/stderr 文件。
- Runner 配置检查只读层不创建 `flowtrace.runner.json`。
- Runner 配置检查只读层不修改 `flowtrace.runner.json`。
- Runner 配置检查只读层不写用户项目。
- Runner 配置检查只读层没有 POST API。
- Runner 配置检查只读层没有存储文件。
- 当前真实启动仍禁用，`launch_enabled=false`。

### 下一步

1. 设计服务启动参数审计层，检查当前 FlowTrace 服务是否显式允许真实执行。
2. 该层仍只读，不新增真实 launch API。
3. 真实执行必须晚于服务开关审计、日志目录策略和最终人工授权。
## 2026-07-02 更新：Runner 治理就绪度只读总闸门

### 已完成

- `runner_governance_readiness.py` 输出 `project_runner_governance_readiness.v1`。
- `/api/project/runner-governance-readiness` 返回 Runner 治理就绪度报告。
- `/api/project/bootstrap` 已包含 `runner_governance_readiness`。
- `runner_governance_readiness_schema.v1` 固化需要纳入总闸门的治理层。
- 接入向导展示“Runner 治理就绪度”只读区块。
- 验收脚本覆盖未保存状态与完整治理链路状态。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner -> Runner 启动开关策略 -> Runner 运行时策略 -> Runner 执行配置只读层 -> Runner 配置检查只读层 -> Runner 服务开关审计 -> Runner 日志目录策略 -> Runner 日志保留策略 -> Runner 日志清理预览 -> Runner 日志清理确认 -> Runner 日志清理审计追踪 -> Runner 治理就绪度
```

### 新增边界

```text
runner_governance_readiness.py -> Runner 治理总闸门只读报告
```

硬性约束：
- Runner 治理就绪度不执行命令。
- Runner 治理就绪度不创建进程。
- Runner 治理就绪度不开放真实启动 API。
- Runner 治理就绪度不读写日志。
- Runner 治理就绪度不删除、轮转、重命名或截断日志。
- Runner 治理就绪度不创建或修改配置文件。
- Runner 治理就绪度不写用户项目。
- 当前真实启动仍禁用，`launch_enabled=false`。

### 下一步

1. 继续设计只读治理层，例如真实执行适配器规范草案。
2. 或设计启动 API 合约草案，但只能是合约报告，不能注册真实 POST。
3. 在真实执行前，必须继续维持总闸门 `launchable_count=0`。
## 2026-07-02 更新：Runner 执行适配器合约只读层

### 已完成

- `runner_execution_adapter_contract.py` 输出 `project_runner_execution_adapter_contracts.v1`。
- `/api/project/runner-execution-adapter-contracts` 返回执行适配器合约报告。
- `/api/project/bootstrap` 已包含 `runner_execution_adapter_contracts`。
- `runner_execution_adapter_contract_schema.v1` 固化未来执行适配器接口、输入输出、argv/env 约束、生命周期钩子和禁止动作。
- 接入向导展示“Runner 执行适配器合约”只读区块。
- 前端治理刷新尾链收敛为单函数，减少后续新增层级时的同步遗漏风险。
- 验收脚本覆盖未保存状态与完整治理链路状态。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner -> Runner 启动开关策略 -> Runner 运行时策略 -> Runner 执行配置只读层 -> Runner 配置检查只读层 -> Runner 服务开关审计 -> Runner 日志目录策略 -> Runner 日志保留策略 -> Runner 日志清理预览 -> Runner 日志清理确认 -> Runner 日志清理审计追踪 -> Runner 治理就绪度 -> Runner 执行适配器合约
```

### 新增边界

```text
runner_execution_adapter_contract.py -> Runner 执行适配器合约只读报告
```

硬性约束：
- Runner 执行适配器合约不执行命令。
- Runner 执行适配器合约不创建进程。
- Runner 执行适配器合约不开放真实启动 API。
- Runner 执行适配器合约不打开 stdout/stderr 文件。
- Runner 执行适配器合约不写 runner 事件日志。
- Runner 执行适配器合约不读写日志。
- Runner 执行适配器合约不删除、轮转或截断日志。
- Runner 执行适配器合约不创建或修改配置文件。
- Runner 执行适配器合约不写用户项目。
- 当前真实启动仍禁用，`launch_enabled=false`。

### 下一步

1. 继续设计启动 API 合约草案，但只能输出只读报告，不能注册真实 POST。
2. 或补充执行适配器审查报告，用于检查未来适配器实现是否满足本轮合约。
3. 真实执行必须继续晚于人工授权、服务开关、日志策略和执行适配器合约审查。
## 2026-07-02 更新：Runner 启动 API 合约只读层

### 已完成

- `runner_launch_api_contract.py` 输出 `project_runner_launch_api_contracts.v1`。
- `/api/project/runner-launch-api-contracts` 返回启动 API 合约报告。
- `/api/project/bootstrap` 已包含 `runner_launch_api_contracts`。
- `runner_launch_api_contract_schema.v1` 固化未来启动端点、请求字段、响应字段、幂等规则和启动前门槛。
- 接入向导展示“Runner 启动 API 合约”只读区块。
- 验收脚本覆盖未保存状态与完整治理链路状态。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner -> Runner 启动开关策略 -> Runner 运行时策略 -> Runner 执行配置只读层 -> Runner 配置检查只读层 -> Runner 服务开关审计 -> Runner 日志目录策略 -> Runner 日志保留策略 -> Runner 日志清理预览 -> Runner 日志清理确认 -> Runner 日志清理审计追踪 -> Runner 治理就绪度 -> Runner 执行适配器合约 -> Runner 启动 API 合约
```

### 新增边界

```text
runner_launch_api_contract.py -> Runner 启动 API 合约只读报告
```

硬性约束：
- Runner 启动 API 合约不注册真实 POST。
- Runner 启动 API 合约不执行命令。
- Runner 启动 API 合约不创建进程。
- Runner 启动 API 合约不调用执行适配器。
- Runner 启动 API 合约不打开 stdout/stderr 文件。
- Runner 启动 API 合约不写 runner 事件日志。
- Runner 启动 API 合约不读写日志。
- Runner 启动 API 合约不删除、轮转或截断日志。
- Runner 启动 API 合约不创建或修改配置文件。
- Runner 启动 API 合约不写用户项目。
- 当前真实启动仍禁用，`launch_enabled=false`。

### 下一步

1. 做执行适配器审查报告，检查未来适配器实现是否满足适配器合约与启动 API 合约。
2. 或设计真实执行前的最终阻断矩阵，把所有 `launch_enabled=false` 的原因汇总为用户可读状态。
3. 真实执行仍不能开始，直到明确实现真实 runner 并通过新的人工授权轮次。
## 2026-07-02 更新：Runner 执行适配器审查只读层

### 已完成

- `runner_execution_adapter_review.py` 输出 `project_runner_execution_adapter_reviews.v1`。
- `/api/project/runner-execution-adapter-reviews` 返回执行适配器审查报告。
- `/api/project/bootstrap` 已包含 `runner_execution_adapter_reviews`。
- `runner_execution_adapter_review_schema.v1` 固化未来适配器实现前必须通过的审查门槛和证据集合。
- 接入向导展示“Runner 执行适配器审查”只读区块。
- 验收脚本覆盖未保存状态与完整治理链路状态。

### 当前执行链路

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认 -> Runner 隔离设计报告 -> 执行请求草案 -> 二次确认 -> Runner 会话草案 -> 启动前快照 -> Dry-run Runner -> Runner 启动开关策略 -> Runner 运行时策略 -> Runner 执行配置只读层 -> Runner 配置检查只读层 -> Runner 服务开关审计 -> Runner 日志目录策略 -> Runner 日志保留策略 -> Runner 日志清理预览 -> Runner 日志清理确认 -> Runner 日志清理审计追踪 -> Runner 治理就绪度 -> Runner 执行适配器合约 -> Runner 启动 API 合约 -> Runner 执行适配器审查
```

### 新增边界

```text
runner_execution_adapter_review.py -> Runner 执行适配器预实现审查只读报告
```

硬性约束：
- Runner 执行适配器审查不扫描代码。
- Runner 执行适配器审查不导入执行适配器。
- Runner 执行适配器审查不调用执行适配器。
- Runner 执行适配器审查不注册真实 POST。
- Runner 执行适配器审查不执行命令。
- Runner 执行适配器审查不创建进程。
- Runner 执行适配器审查不打开 stdout/stderr 文件。
- Runner 执行适配器审查不写 runner 事件日志。
- Runner 执行适配器审查不读写日志。
- Runner 执行适配器审查不删除、轮转或截断日志。
- Runner 执行适配器审查不创建或修改配置文件。
- Runner 执行适配器审查不写用户项目。
- 当前真实启动仍禁用，`launch_enabled=false`。

### 下一步

1. 设计真实执行前最终阻断矩阵，聚合所有仍为 false 的启动条件。
2. 阻断矩阵仍只能只读，不得注册真实 POST、不得调用适配器。
3. 真实执行仍需要新的人工授权和单独实现轮次。

## 2026-07-02 更新：Runner 日志清理执行计划只读层

### 已完成

- `runner_log_cleanup_execution_plan.py` 输出 `project_runner_log_cleanup_execution_plans.v1`。
- `/api/project/runner-log-cleanup-execution-plans` 返回日志清理执行计划只读报告。
- `/api/project/bootstrap` 已包含 `runner_log_cleanup_execution_plans`。
- `runner_log_cleanup_execution_plan_schema.v1` 固化未来候选清单 hash、允许操作类型、禁止操作类型和必需门槛。
- 接入向导展示“Runner 日志清理执行计划”。
- 治理就绪度已纳入该层，`layer_count=18`。

### 当前边界

- 不生成候选清单。
- 不保存执行计划。
- 不执行清理。
- 不扫描日志目录。
- 不读取日志文件。
- 不删除、轮转、重命名、截断或写入日志。
- 不读写审计日志。
- 不开放真实启动 API。

### 验证

```text
verify_realistic_samples.py ok
live API status=no_saved_profiles
planned_operation_count=0
launchable_count=0
Playwright Edge visual check ok
```
## 2026-07-02 Asia/Shanghai - Runner final block matrix status

Current status: completed and verified.

Implemented:
- Read-only final block matrix layer: src/flowtrace/runner_final_block_matrix.py
- Endpoint: GET /api/project/runner-final-block-matrices
- Bootstrap field: runner_final_block_matrices
- UI onboarding section: Runner 最终阻断矩阵
- Server helper optimization: _project_runner_governance_chain() prevents single endpoint timeout from repeated recursive governance rebuilds.

Schemas:
```text
project_runner_final_block_matrices.v1
runner_final_block_matrix_schema.v1
```

Live service:
```text
URL: http://127.0.0.1:8765/
PID: 59296
```

Verified live values:
```text
runner_final_block_matrices.status=no_saved_profiles
runner_final_block_matrices.summary.launchable_count=0
runner_final_block_matrices.summary.blocking_reason_count=0
runner_governance_readiness.summary.layer_count=18
```

Hard boundary remains:
```text
No real launch API.
No launch POST registration.
No adapter import or invocation.
No process creation.
No command execution.
No stdout/stderr sink writes.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Visual verification:
```text
D:\pyProject\flowtrace-mvp\output\playwright\flowtrace-final-block-matrix.png
```

Next recommended step:
```text
Continue only with read-only authorization/unlock checklist audit for the final block matrix.
Real execution still requires a separate implementation and explicit new authorization round.
```
## 2026-07-02 Asia/Shanghai - Runner authorization unlock audit status

Current status: completed and verified.

Implemented:
- Read-only authorization unlock audit layer: src/flowtrace/runner_authorization_unlock_audit.py
- Endpoint: GET /api/project/runner-authorization-unlock-audits
- Bootstrap field: runner_authorization_unlock_audits
- UI onboarding section: Runner 授权解锁审计

Schemas:
```text
project_runner_authorization_unlock_audits.v1
runner_authorization_unlock_audit_schema.v1
```

Live service:
```text
URL: http://127.0.0.1:8765/
PID: 26532
```

Verified live values:
```text
runner_authorization_unlock_audits.status=no_saved_profiles
runner_authorization_unlock_audits.summary.launchable_count=0
runner_authorization_unlock_audits.summary.missing_evidence_count=0
runner_authorization_unlock_audits.summary.future_unlock_count=0
```

Hard boundary remains:
```text
No real launch API.
No launch POST registration.
No adapter import or invocation.
No process creation.
No command execution.
No authorization collection.
No launch permission grant.
No authorization storage.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Visual verification:
```text
D:\pyProject\flowtrace-mvp\output\playwright\flowtrace-authorization-unlock-audit.png
```

Next recommended step:
```text
Continue only with read-only runner implementation gap checklist or cancel/timeout endpoint contract draft.
Real execution still requires a separate implementation and explicit new authorization round.
```
## 2026-07-03 Asia/Shanghai - Runner implementation gap checklist status

Current status: completed and verified.

Implemented:
- Read-only implementation gap checklist layer: src/flowtrace/runner_implementation_gap_checklist.py
- Endpoint: GET /api/project/runner-implementation-gap-checklists
- Bootstrap field: runner_implementation_gap_checklists
- UI onboarding section: Runner 实现差距清单

Schemas:
```text
project_runner_implementation_gap_checklists.v1
runner_implementation_gap_checklist_schema.v1
```

Live service:
```text
URL: http://127.0.0.1:8765/
PID: 62036
```

Verified live values:
```text
runner_implementation_gap_checklists.status=no_saved_profiles
runner_implementation_gap_checklists.summary.launchable_count=0
runner_implementation_gap_checklists.summary.gap_count=0
runner_implementation_gap_checklists.summary.component_count=0
```

Hard boundary remains:
```text
No real launch API.
No launch POST registration.
No runner implementation.
No code writes.
No adapter import or invocation.
No process creation.
No command execution.
No authorization collection or permission grant.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Visual verification:
```text
D:\pyProject\flowtrace-mvp\output\playwright\flowtrace-implementation-gap-checklist.png
```

Next recommended step:
```text
Continue with read-only cancel/timeout endpoint contract draft, or interrupt with Runner workbench UX skeleton if the UI becomes difficult to operate.
Real execution still requires a separate implementation and explicit authorization round.
```
## 2026-07-03 Asia/Shanghai - Runner cancel/timeout endpoint contract read-only layer

Status: completed and verified.

Implemented:
- Added D:\pyProject\flowtrace-mvp\src\flowtrace\runner_cancel_timeout_contract.py.
- Added GET /api/project/runner-cancel-timeout-contracts.
- Added bootstrap field runner_cancel_timeout_contracts.
- Added onboarding section for the Runner cancel/timeout contract.

Schemas:
```text
project_runner_cancel_timeout_contracts.v1
runner_cancel_timeout_contract_schema.v1
```

Purpose:
```text
Declare the future cancel and timeout endpoint contract before real runner execution exists.
The layer documents future POST /api/project/runner/cancel and POST /api/project/runner/timeout fields, idempotency, forbidden request fields, state transitions, guards, and event names.
It is contract-only and read-only.
```

Live result:
```text
status=no_saved_profiles
future_endpoint_count=0
registered_endpoint_count=0
launchable_count=0
cancel_timeout_contract_only=True
registers_cancel_api=False
registers_timeout_api=False
cancels_process=False
sends_process_signal=False
kills_process=False
schedules_timeout=False
writes_runner_events=False
```

Hard boundary:
```text
No real launch API.
No launch POST registration.
No cancel POST registration.
No timeout POST registration.
No runner implementation.
No adapter import or invocation.
No process creation.
No process signal or kill operation.
No timeout worker scheduling.
No command execution.
No authorization collection or permission grant.
No launch state storage.
No stdout/stderr file opening.
No runner event writes.
No log scan/read/write/delete/rotate/rename/truncate.
No audit log persistence.
No user project writes.
```

Validation:
```text
Python AST parse ok: 70 files
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
compileall ok with isolated PYTHONPYCACHEPREFIX
git diff --check ok
GET /api/project/runner-cancel-timeout-contracts -> project_runner_cancel_timeout_contracts.v1
GET /api/project/bootstrap includes runner_cancel_timeout_contracts
Playwright Edge visual check ok after clicking onboarding tab
page contains Runner cancel/timeout contract section
page contains runner_cancel_timeout_contract_schema.v1
mojibake check false
console only has favicon.ico 404
```

Service:
```text
http://127.0.0.1:8765/
PID 59656
```

Screenshot:
```text
D:\pyProject\flowtrace-mvp\output\playwright\flowtrace-cancel-timeout-contract.png
```

Next recommended step:
```text
Continue with a read-only Runner session state schema draft, or interrupt with the Runner workbench UX skeleton if onboarding becomes too long or hard to operate.
Real execution still requires a separate implementation and explicit authorization round.
```
## 2026-07-03 Asia/Shanghai - Runner session state schema read-only layer

Status: completed and verified.

Implemented:
- Added D:\pyProject\flowtrace-mvp\src\flowtrace\runner_session_state_schema.py.
- Added GET /api/project/runner-session-state-schemas.
- Added bootstrap field runner_session_state_schemas.
- Added onboarding section Runner session state schema.

Schemas:
```text
project_runner_session_state_schemas.v1
runner_session_state_schema.v1
```

Purpose:
```text
Declare the future Runner session state model before real execution exists.
The layer documents identity fields, future state fields, forbidden current fields, allowed states, allowed transitions, terminal states, guards, and events.
It is schema-only and read-only.
```

Live result:
```text
status=no_saved_profiles
state_count=0
persisted_session_count=0
active_session_count=0
launchable_count=0
session_state_schema_only=True
creates_session=False
stores_session_state=False
mutates_session_state=False
reads_session_state_store=False
writes_session_state_store=False
registers_launch_api=False
registers_cancel_api=False
registers_timeout_api=False
creates_process=False
calls_execution_adapter=False
opens_stdout_stderr=False
writes_runner_events=False
writes_logs=False
writes_audit_log=False
writes_user_project=False
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
Python AST parse ok: 53 files in src/tools
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
compileall ok with isolated PYTHONPYCACHEPREFIX
git diff --check ok
GET /api/project/runner-session-state-schemas -> project_runner_session_state_schemas.v1
GET /api/project/bootstrap includes runner_session_state_schemas
Playwright Edge visual check ok after clicking onboarding tab
page contains Runner session state schema section
page contains runner_session_state_schema.v1
mojibake check false
console only has favicon.ico 404
```

Service:
```text
http://127.0.0.1:8765/
PID 52204
```

Screenshot:
```text
D:\pyProject\flowtrace-mvp\output\playwright\flowtrace-session-state-schema.png
```

Next recommended step:
```text
Continue with a read-only Runner event log schema contract, or interrupt with the Runner workbench UX skeleton if onboarding becomes too long or hard to operate.
Real execution still requires a separate implementation and explicit authorization round.
```
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

## 2026-07-03 - Runner 工作台关键路径优化

状态：已完成并验证。

本轮完成：
- Runner 工作台默认当前阶段改为优先显示最早可行动阻断点。
- 未保存运行配置时，顶部状态聚焦“等待保存运行配置”，避免误导用户先看最后一个治理层。
- 新增“关键路径”面板，按运行配置、确认链路、只读治理、解锁缺口四步展示当前进度。
- 新增阻断、警告、就绪、未加载阶段统计 chip。
- 清理工作台阶段详情中的旧英文 fallback 文案。

边界：
```text
不新增后端接口。
不修改现有 schema。
不开放真实 launch/cancel/timeout API。
不创建进程。
不调用执行适配器。
不创建或持久化 Runner session。
不写用户项目。
```

验证：
```text
node --check runner-workbench.js ok
node --check app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright Edge DOM check ok
当前标题=等待保存运行配置
关键路径=4 步
治理筛选 visible_count=14
乱码检查 false
旧英文 fallback 检查 false
```

下一步建议：
```text
继续围绕 Runner 工作台做人机交互优化，优先补齐“从关键路径跳到对应详情/接入向导位置”的只读导航能力。
真实执行仍需要独立授权轮次，不在当前优化中开放。
```

## 2026-07-03 - Runner 工作台关键路径导航

状态：已完成并验证。

本轮完成：
- 关键路径步骤现在可点击、可键盘聚焦。
- 点击关键路径步骤会更新同一个阶段详情面板。
- 阶段卡片和关键路径步骤共享选中状态。
- 从关键路径跳转时自动恢复“全部”筛选，避免目标阶段被当前筛选隐藏。
- 对已知英文 runner next_action fallback 做展示层本地化，不修改接口 payload。

边界：
```text
不新增后端接口。
不修改现有 schema。
不开放真实 launch/cancel/timeout API。
不创建进程。
不调用执行适配器。
不创建或持久化 Runner session。
不写用户项目。
```

验证：
```text
node --check runner-workbench.js ok
node --check app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright 点击导航 ok
Playwright Enter 键导航 ok
点击解锁缺口选中 runner_implementation_gap_checklists
Enter 选择确认链路选中 run_execution_gate
路径导航后 active filter=全部
乱码检查 false
旧英文 fallback 检查 false
```

下一步建议：
```text
继续把 Runner 工作台作为主交互面，下一步可增加“只读证据摘要/阻断证据展开”，帮助用户理解每个阻断来自哪个治理层。
真实执行仍必须等待独立授权轮次。
```

## 2026-07-03 - Runner 工作台只读证据面板

状态：已完成并验证。

本轮完成：
- 在 Runner 阶段详情中新增“只读证据”面板。
- 证据只从现有 payload 的 summary 和 schema 字段派生。
- 证据面板包含紧凑指标 chip 和可折叠证据组。
- 支持展示阻断动作、阻断维度、后续解锁项、授权记录要求、证据要求、实现组件、治理层、未来阻断层、解锁状态和报告证据。
- 对已知 schema 枚举项做展示层本地化，不修改后端 payload。

边界：
```text
不新增后端接口。
不修改现有 schema。
不修改现有 runner payload。
不开放真实 launch/cancel/timeout API。
不创建进程。
不调用执行适配器。
不创建或持久化 Runner session。
不写用户项目。
```

验证：
```text
node --check runner-workbench.js ok
node --check app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright evidence panel check ok
实现差距 evidence groups=2
治理就绪 evidence groups=2
证据 details 可展开
乱码检查 false
已知英文阻断动作残留 false
```

下一步建议：
```text
继续围绕 Runner 工作台优化，下一步可让阻断原因卡片直接跳转到对应证据组。
真实执行仍必须等待独立授权轮次。
```

## 2026-07-03 - Runner 工作台阻断证据导航

状态：已完成并验证。

本轮完成：
- 阻断原因卡片在存在目标阶段时可点击、可键盘聚焦。
- 为保存配置阻断、真实启动阻断、端点阻断和当前阶段阻断增加只读导航目标。
- 点击“真实启动仍被阻断”会选中最终阻断阶段，并打开“阻断动作”证据组。
- 对“尚未保存运行配置”按 Enter 会选中运行配置阶段。
- 阻断导航前自动恢复“全部”筛选，避免目标阶段被隐藏。

边界：
```text
不新增后端接口。
不修改现有 schema。
不修改现有 runner payload。
不开放真实 launch/cancel/timeout API。
不创建进程。
不调用执行适配器。
不创建或持久化 Runner session。
不写用户项目。
```

验证：
```text
node --check runner-workbench.js ok
node --check app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright blocker click navigation ok
Playwright blocker keyboard Enter navigation ok
真实启动阻断选中 runner_final_block_matrices
真实启动阻断打开 阻断动作 证据组
保存配置阻断选中 run_profiles
阻断导航后 active filter=全部
乱码检查 false
```

下一步建议：
```text
继续围绕 Runner 工作台优化，下一步可增加阶段详情中的安全标记分组/中文化，降低 key=value 列表的阅读成本。
真实执行仍必须等待独立授权轮次。
```

## 2026-07-03 - Runner 工作台安全边界分组

状态：已完成并验证。

本轮完成：
- 将阶段详情中的原始安全标记 `key=value` 列表改为中文分组展示。
- 安全边界分为执行边界、API 边界、会话边界、日志与审计、项目写入、只读声明。
- 每个安全项展示为“已阻断 / 只读声明 / 需要审查 / 未声明”等可读状态。
- 对内部 `*_only` 安全声明键做中文化展示。

边界：
```text
不新增后端接口。
不修改现有 schema。
不修改现有 runner payload。
不开放真实 launch/cancel/timeout API。
不创建进程。
不调用执行适配器。
不创建或持久化 Runner session。
不写用户项目。
```

验证：
```text
node --check runner-workbench.js ok
node --check app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright safety grouping check ok
最终阻断 safety groups=6
会话状态 safety groups=6
旧 key=value 安全文案 false
裸露 *_only 内部键 false
乱码检查 false
```

下一步建议：
```text
继续围绕 Runner 工作台优化，下一步可增加阶段详情的“复制只读审计摘要”功能，方便人工交接但不写文件、不触碰用户项目。
真实执行仍必须等待独立授权轮次。
```

## 2026-07-03 - Runner 工作台复制只读审计摘要

状态：已完成并验证。

本轮完成：
- Runner 阶段详情新增“复制摘要”按钮。
- 摘要文本只从当前页面已加载的阶段 payload 生成。
- 摘要包含阶段状态、结构版本、下一步、安全边界、只读证据和硬边界说明。
- 复制优先使用浏览器剪贴板，失败时使用 textarea fallback。
- 页面内显示“已复制 / 复制失败”状态。

边界：
```text
不新增后端接口。
不修改现有 schema。
不修改现有 runner payload。
不开放真实 launch/cancel/timeout API。
不创建进程。
不调用执行适配器。
不创建或持久化 Runner session。
不写文件。
不写用户项目。
```

验证：
```text
node --check runner-workbench.js ok
node --check app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright copy summary check ok
复制状态=已复制
复制摘要包含阶段、安全边界、只读证据和硬边界
乱码检查 false
```

下一步建议：
```text
继续围绕 Runner 工作台优化，下一步可增加“阶段详情压缩/展开视图”，让安全边界、只读证据和阶段流在长页面中更易扫描。
真实执行仍必须等待独立授权轮次。
```

## 2026-07-03 - Runner 工作台阶段详情压缩视图

状态：已完成并验证。

本轮完成：
- Runner 阶段详情新增“压缩视图 / 展开视图”切换。
- 压缩视图保留标题、关键字段、分组标题和计数，隐藏较长的安全标记列表与证据列表。
- 压缩状态只是页面 DOM 状态，不写文件、不写用户项目、不新增持久化。
- 切换压缩视图时选中阶段不变。
- 切换阶段后按钮文案和压缩状态保持同步。

边界：
```text
不新增后端接口。
不修改现有 schema。
不修改现有 runner payload。
不开放真实 launch/cancel/timeout API。
不创建进程。
不调用执行适配器。
不创建或持久化 Runner session。
不写文件。
不写用户项目。
```

验证：
```text
node --check runner-workbench.js ok
node --check app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright compact mode check ok
压缩后详情高度 1176 -> 755
压缩模式隐藏安全标记列表和证据列表
展开模式恢复安全标记列表
切换阶段后压缩状态和按钮文案同步
乱码检查 false
```

下一步建议：
```text
继续围绕 Runner 工作台优化，下一步可增加“阶段流密度切换/只看关键阶段”，进一步降低 28 个阶段同时展示时的扫描成本。
真实执行仍必须等待独立授权轮次。
```

## 2026-07-03 - Runner 工作台阶段流密度与范围

状态：已完成并验证。

本轮完成：
- 阶段流新增“标准密度 / 紧凑密度”切换。
- 阶段流新增“全部阶段 / 关键阶段”切换。
- 关键阶段由现有关键路径和阻断目标派生，不新增业务判断。
- 阶段筛选、密度切换、范围切换可以组合使用。
- 修正治理就绪阶段分组，使其能出现在“治理”筛选中。

边界：
```text
不新增后端接口。
不修改现有 schema。
不修改现有 runner payload。
不开放真实 launch/cancel/timeout API。
不创建进程。
不调用执行适配器。
不创建或持久化 Runner session。
不写文件。
不写用户项目。
不新增持久化状态。
```

验证：
```text
node --check runner-workbench.js ok
node --check app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright stage density/scope check ok
总阶段数=28
关键阶段数=5
紧凑卡片高度=78
关键阶段 visible_count=5
治理+关键 visible_count=2
治理+关键包含 runner_governance_readiness
乱码检查 false
```

下一步建议：
```text
继续围绕 Runner 工作台优化，下一步可增加“阶段流搜索/按状态快速定位”，继续降低阶段数量增长后的定位成本。
真实执行仍必须等待独立授权轮次。
```

## 2026-07-03 - Runner 工作台阶段搜索与快速定位

状态：已完成并验证。

本轮完成：
- Runner 工作台阶段流新增搜索框。
- 搜索范围覆盖阶段 key、标题、状态、摘要、分组与类型。
- 新增可见数量提示，便于确认当前筛选结果。
- 搜索可与阶段分组筛选、紧凑密度、只看关键阶段组合使用。
- 搜索只影响当前页面 DOM 显示，不写入文件、不写入用户项目、不新增持久化状态。

边界：
```text
不新增后端接口。
不修改现有 schema。
不修改现有 runner payload。
不开放真实 launch/cancel/timeout API。
不创建进程。
不调用执行适配器。
不创建或持久化 Runner session。
不写运行日志。
不写审计日志。
不写用户项目。
```

验证：
```text
node --check runner-workbench.js ok
node --check app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright stage search check ok
初始可见=28/28
session 搜索可见=2
日志 搜索可见=1
治理+关键+governance 搜索可见=2
乱码检查=false
```

下一步建议：
```text
继续围绕 Runner 工作台优化。下一步可增加搜索清空按钮与空结果提示，让阶段数量继续增长后仍能快速恢复视图。
真实执行仍必须等待独立授权轮次。
```

## 2026-07-03 - Runner 工作台搜索清空与空结果提示

状态：已完成并验证。

本轮完成：
- Runner 阶段搜索新增“清空”按钮。
- 搜索为空时清空按钮保持禁用，避免无效操作。
- 搜索、筛选和关键阶段范围组合后如果没有可见阶段，会显示空结果提示。
- 点击清空会恢复完整阶段流可见数量，不改变当前选中的阶段详情。
- 所有状态仅存在于当前页面 DOM，不写入文件、不写入用户项目、不新增持久化。

边界：
```text
不新增后端接口。
不修改现有 schema。
不修改现有 runner payload。
不开放真实 launch/cancel/timeout API。
不创建进程。
不执行命令。
不调用执行适配器。
不创建或持久化 Runner session。
不写运行日志。
不写审计日志。
不写用户项目。
```

验证：
```text
node --check runner-workbench.js ok
node --check app.js ok
tools/verify_realistic_samples.py ok
compileall ok
git diff --check ok
Playwright search empty/clear check ok
无匹配可见=0/28
空结果提示可见=true
清空后恢复=28/28
清空后按钮禁用=true
乱码检查=false
```

下一步建议：
```text
继续围绕 Runner 工作台优化。下一步可做阶段卡片键盘导航或将搜索命中词做轻量高亮，继续改善人机交互但仍保持只读边界。
真实执行仍必须等待独立授权轮次。
```

## 2026-07-03 - Runner 真实测试准入只读层

状态：已完成并验证。

本轮完成：
- 新增 `runner_real_test_readiness.py`，提供真实测试准入只读评估。
- 新增接口：`GET /api/project/runner-real-test-readiness`。
- bootstrap 新增 `runner_real_test_readiness` 字段。
- 接入向导新增“Runner 真实测试准入”功能区块。
- Runner 工作台阶段流新增“真实测试准入”阶段，阶段数从 28 增至 29。
- 验证脚本纳入新层回归：未保存 profile 时为 `no_saved_profiles`，完整临时治理链下为 `real_test_blocked`。

边界：
```text
不开放真实 launch/cancel/timeout POST API。
不实现 Runner。
不导入或调用执行适配器。
不创建或控制进程。
不执行命令。
不创建、保存或修改 Runner session。
不打开 stdout/stderr。
不写 Runner 事件。
不读写日志文件。
不写审计日志。
不收集或保存人工授权。
不授予启动权限。
不写用户项目。
```

验证：
```text
python ast ok 72
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-real-test-readiness -> project_runner_real_test_readiness.v1
/api/project/bootstrap.runner_real_test_readiness -> project_runner_real_test_readiness.v1
Playwright Runner 工作台 stageCount=29
Playwright hasRealTestStage=true
Playwright 接入向导 has Runner 真实测试准入=true
Browser mojibake check false
服务已重启：PID 64560，URL http://127.0.0.1:8765/
```

下一步建议：
```text
继续项目功能开发，下一步可新增“真实测试授权前检查清单”的只读接口，用于列出未来授权轮次必须人工确认的证据项，但仍不收集授权、不写授权记录、不开放真实执行。
```

## 2026-07-03 - Runner 真实测试授权检查清单只读层

状态：已完成并验证。

本轮完成：
- 新增 `runner_real_test_authorization_checklist.py`，提供真实测试授权前证据清单。
- 新增接口：`GET /api/project/runner-real-test-authorization-checklists`。
- bootstrap 新增 `runner_real_test_authorization_checklists` 字段。
- 接入向导新增“Runner 真实测试授权检查清单”功能区块。
- Runner 工作台阶段流新增“授权检查”阶段，阶段数从 29 增至 30。
- 验证脚本纳入新层回归：未保存 profile 时为 `no_saved_profiles`，完整临时治理链下为 `authorization_checklist_required`。

边界：
```text
不收集人工授权。
不保存授权记录。
不授予启动权限。
不开放真实 launch/cancel/timeout POST API。
不实现 Runner。
不导入或调用执行适配器。
不创建或控制进程。
不执行命令。
不创建、保存或修改 Runner session。
不打开 stdout/stderr。
不写 Runner 事件。
不读写日志文件。
不写审计日志。
不写用户项目。
```

验证：
```text
python ast ok 73
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-real-test-authorization-checklists -> project_runner_real_test_authorization_checklists.v1
/api/project/bootstrap.runner_real_test_authorization_checklists -> project_runner_real_test_authorization_checklists.v1
Playwright Runner 工作台 stageCount=30
Playwright hasAuthorizationStage=true
Playwright 接入向导 sectionExists=true
Browser mojibake check false
服务已重启：PID 39724，URL http://127.0.0.1:8765/
```

下一步建议：
```text
继续项目功能开发。下一步可新增“真实执行能力实现计划”只读层，把执行适配器、进程生命周期、session 状态、stdout/stderr 捕获、Runner event、audit log、取消/超时、前端执行控制台拆成实现模块；仍不写实现、不启动进程。
```

## 2026-07-03 - Runner 真实执行实现计划只读层

状态：已完成并验证。

本轮完成：
- 新增 `runner_real_execution_implementation_plan.py`，把未来真实执行能力拆成实现模块和验收证据。
- 新增接口：`GET /api/project/runner-real-execution-implementation-plans`。
- bootstrap 新增 `runner_real_execution_implementation_plans` 字段。
- 接入向导新增“Runner 真实执行实现计划”功能区块。
- Runner 工作台阶段流新增“实现计划”阶段，阶段数从 30 增至 31。
- 验证脚本纳入新层回归：未保存 profile 时为 `no_saved_profiles`，完整临时治理链下为 `implementation_plan_required`。

边界：
```text
不写 Runner 实现代码。
不开放真实 launch/cancel/timeout POST API。
不导入或调用执行适配器。
不创建或控制进程。
不执行命令。
不创建、保存或修改 Runner session。
不打开 stdout/stderr。
不写 Runner 事件。
不读写日志文件。
不写审计日志。
不收集或保存授权。
不授予启动权限。
不写用户项目。
```

验证：
```text
python ast ok 74
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-real-execution-implementation-plans -> project_runner_real_execution_implementation_plans.v1
/api/project/bootstrap.runner_real_execution_implementation_plans -> project_runner_real_execution_implementation_plans.v1
Playwright Runner 工作台 stageCount=31
Playwright hasPlanStage=true
Playwright 接入向导 sectionExists=true
Browser mojibake check false
服务已重启：PID 48728，URL http://127.0.0.1:8765/
```

下一步建议：
```text
继续项目功能开发。下一步可新增“Runner 执行适配器实现准备审计”只读层，检查未来实现前需要锁定的接口输入、输出、错误、事件和审计证据；仍不写实现、不启动进程。
```

## 2026-07-03 - Runner 执行适配器实现准备审计只读层

状态：已完成并验证。

本轮完成：
- 新增 `runner_execution_adapter_implementation_audit.py`，审计未来执行适配器实现前必须锁定的证据。
- 新增接口：`GET /api/project/runner-execution-adapter-implementation-audits`。
- bootstrap 新增 `runner_execution_adapter_implementation_audits` 字段。
- 接入向导新增“Runner 执行适配器实现准备审计”功能区块。
- Runner 工作台阶段流新增“适配器审计”阶段，阶段数从 31 增至 32。
- 验证脚本纳入新层回归：未保存 profile 时为 `no_saved_profiles`，完整临时治理链下为 `adapter_implementation_audit_required`。

边界：
```text
不写执行适配器实现代码。
不导入执行适配器模块。
不调用执行适配器。
不开放真实 launch/cancel/timeout POST API。
不创建或控制进程。
不执行命令。
不创建、保存或修改 Runner session。
不打开 stdout/stderr。
不写 Runner 事件。
不读写日志文件。
不写审计日志。
不收集或保存授权。
不授予启动权限。
不写用户项目。
```

验证：
```text
python ast ok 75
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-execution-adapter-implementation-audits -> project_runner_execution_adapter_implementation_audits.v1
/api/project/bootstrap.runner_execution_adapter_implementation_audits -> project_runner_execution_adapter_implementation_audits.v1
Playwright Runner 工作台 stageCount=32
Playwright hasAuditStage=true
Playwright 接入向导 sectionExists=true
Browser mojibake check false
服务已重启：PID 57692，URL http://127.0.0.1:8765/
```

下一步建议：
```text
继续项目功能开发。下一步可新增“Runner 进程生命周期实现准备审计”只读层，检查未来进程创建、PID 归属、终止态、取消、超时和清理边界；仍不创建进程、不写实现。
```

## 2026-07-04 - Runner 进程生命周期实现准备审计只读层

状态：已完成并验证。

本轮完成：
- 新增 `runner_process_lifecycle_implementation_audit.py`，审计未来进程生命周期实现前必须锁定的证据。
- 新增接口：`GET /api/project/runner-process-lifecycle-implementation-audits`。
- bootstrap 新增 `runner_process_lifecycle_implementation_audits` 字段。
- 接入向导新增“Runner 进程生命周期实现准备审计”功能区块。
- Runner 工作台阶段流新增“进程审计”阶段，阶段数从 32 增至 33。
- 验证脚本纳入新层回归：未保存 profile 时为 `no_saved_profiles`，完整临时治理链下为 `process_lifecycle_audit_required`。

边界：
```text
不写进程生命周期实现代码。
不创建进程。
不控制或发送进程信号。
不取消或杀进程。
不调度真实超时。
不开放真实 launch/cancel/timeout POST API。
不导入或调用执行适配器。
不创建、保存或修改 Runner session。
不打开 stdout/stderr。
不写 Runner 事件。
不读写日志文件。
不写审计日志。
不收集或保存授权。
不授予启动权限。
不写用户项目。
```

验证：
```text
python ast ok 76
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-process-lifecycle-implementation-audits -> project_runner_process_lifecycle_implementation_audits.v1
/api/project/bootstrap.runner_process_lifecycle_implementation_audits -> project_runner_process_lifecycle_implementation_audits.v1
Playwright Runner 工作台 stageCount=33
Playwright hasProcessStage=true
Playwright 接入向导 sectionExists=true
Browser mojibake check false
服务已重启：PID 2252，URL http://127.0.0.1:8765/
```

下一步建议：
```text
继续项目功能开发。下一步可新增“Runner stdout/stderr 捕获实现准备审计”只读层，检查未来输出流分块、脱敏、背压、保留策略和终止态关联；仍不打开 stdout/stderr、不写日志、不创建进程。
```

## 2026-07-04 - Runner stdout/stderr 捕获实现准备审计只读层

状态：已完成并验证。

本轮完成：
- 新增 `runner_stream_capture_implementation_audit.py`，审计未来 stdout/stderr 捕获实现前必须锁定的证据。
- 新增接口：`GET /api/project/runner-stream-capture-implementation-audits`。
- bootstrap 新增 `runner_stream_capture_implementation_audits` 字段。
- 接入向导新增“Runner stdout/stderr 捕获实现准备审计”功能区块。
- Runner 工作台阶段流新增“输出审计”阶段，阶段数从 33 增至 34。
- 验证脚本纳入新层回归：未保存 profile 时为 `no_saved_profiles`，完整临时治理链下为 `stream_capture_audit_required`。

边界：
```text
不打开 stdout/stderr。
不读取 stdout/stderr。
不捕获真实输出流。
不写 Runner 事件。
不读写日志文件。
不写审计日志。
不创建或控制进程。
不调度真实超时。
不开放真实 launch/cancel/timeout POST API。
不导入或调用执行适配器。
不创建、保存或修改 Runner session。
不收集或保存授权。
不授予启动权限。
不写用户项目。
```

验证：
```text
python ast ok 77
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-stream-capture-implementation-audits -> project_runner_stream_capture_implementation_audits.v1
/api/project/bootstrap.runner_stream_capture_implementation_audits -> project_runner_stream_capture_implementation_audits.v1
Playwright Runner 工作台 stageCount=34
Playwright hasStreamStage=true
Playwright 接入向导 sectionExists=true
Browser mojibake check false
服务已重启：PID 66836，URL http://127.0.0.1:8765/
```

下一步建议：
```text
继续项目功能开发。下一步可新增“Runner 事件写入实现准备审计”只读层，检查未来 Runner event schema、顺序、终止态写入、失败处理和脱敏规则；仍不写 Runner event、不写日志、不创建进程。

作用：提前约束真实执行产生的事件格式和写入边界，避免后续实现时出现事件乱序、终止态丢失、敏感信息泄露或写入失败不可追踪的问题。
```
## 2026-07-04 - Runner 事件写入实现准备审计只读层

状态：已完成并验证。

本轮完成：
- 新增 `runner_event_writer_implementation_audit.py`，审计未来 Runner event 写入实现前必须锁定的证据。
- 新增接口：`GET /api/project/runner-event-writer-implementation-audits`。
- bootstrap 新增 `runner_event_writer_implementation_audits` 字段。
- 接入向导新增“Runner 事件写入实现准备审计”功能区块。
- Runner 工作台阶段流新增“事件审计”阶段，阶段数从 34 增至 35。
- 验证脚本纳入新层回归：未保存 profile 时为 `no_saved_profiles`，完整临时治理链下为 `event_writer_audit_required`。

边界：
```text
不写 Runner event。
不打开 runner event log。
不持久化 runner event。
不读写日志文件。
不扫描日志目录。
不打开、读取或捕获 stdout/stderr。
不创建或控制进程。
不调度真实 timeout。
不开放真实 launch/cancel/timeout POST API。
不导入或调用执行适配器。
不创建、保存或修改 Runner session。
不写审计日志。
不收集或保存授权。
不授予启动权限。
不写用户项目。
```

验证：
```text
python ast ok 78
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-event-writer-implementation-audits -> project_runner_event_writer_implementation_audits.v1
/api/project/bootstrap.runner_event_writer_implementation_audits -> project_runner_event_writer_implementation_audits.v1
API status=no_saved_profiles launchable_count=0 event_write_count=0 log_write_count=0
Playwright Runner 工作台 stageCount=35
Playwright hasEventStage=true
Playwright 接入向导 sectionExists=true
Playwright textIncludesSchema=true
Playwright textIncludesEvidence=true
Browser mojibake check false
服务已重启：PID 49320，URL http://127.0.0.1:8765/
```

下一步建议：
```text
继续项目功能开发。下一步可新增“Runner 审计持久化实现准备审计”只读层，检查未来人工授权证据、启动决策、事件链摘要、失败原因和不可抵赖审计记录之间的关联规则；仍不写审计日志、不写事件、不写日志、不创建进程。
作用：提前约束真实测试后的追责链路，避免后续出现 Runner event 与人工授权、启动配置、失败原因、审计记录互相对不上的问题。
```
## 2026-07-04 - Runner 审计持久化实现准备审计只读层

状态：已完成并验证。

本轮完成：
- 新增 `runner_audit_persistence_implementation_audit.py`，审计未来 Runner 审计记录持久化实现前必须锁定的证据。
- 新增接口：`GET /api/project/runner-audit-persistence-implementation-audits`。
- bootstrap 新增 `runner_audit_persistence_implementation_audits` 字段。
- 接入向导新增“Runner 审计持久化实现准备审计”功能区块。
- Runner 工作台阶段流新增“审计持久化”阶段，阶段数从 35 增至 36。
- 验证脚本纳入新层回归：未保存 profile 时为 `no_saved_profiles`，完整临时治理链下为 `audit_persistence_audit_required`。

边界：
```text
不写审计记录。
不打开 audit log。
不读取 audit log。
不持久化审计记录。
不写 Runner event。
不打开 runner event log。
不写 event log。
不读写日志文件。
不扫描日志目录。
不打开、读取或捕获 stdout/stderr。
不创建或控制进程。
不调度真实 timeout。
不开放真实 launch/cancel/timeout POST API。
不导入或调用执行适配器。
不创建、保存或修改 Runner session。
不收集或保存授权。
不授予启动权限。
不写用户项目。
```

验证：
```text
python ast ok 79
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-audit-persistence-implementation-audits -> project_runner_audit_persistence_implementation_audits.v1
/api/project/bootstrap.runner_audit_persistence_implementation_audits -> project_runner_audit_persistence_implementation_audits.v1
API status=no_saved_profiles launchable_count=0 audit_record_count=0 audit_write_count=0 audit_read_count=0
API audit_only=true opens_audit_log=false writes_audit_log=false stores_audit_records=false
Playwright Runner 工作台 stageCount=36
Playwright hasAuditPersistenceStage=true
Playwright 接入向导 sectionExists=true
Playwright textIncludesSchema=true
Playwright textIncludesEvidence=true
Browser mojibake check false
服务已重启：PID 33696，URL http://127.0.0.1:8765/
```

下一步建议：
```text
继续项目功能开发。下一步可新增“Runner 审计完整性与回放校验准备审计”只读层，检查未来审计记录、Runner event、启动配置、失败原因之间如何做一致性校验和回放核验；仍不读取或写入审计日志、不写事件、不创建进程。
作用：提前约束真实测试后的校验闭环，避免后续即使写入了事件和审计记录，也无法证明二者一致、完整、可回放。
```
## 2026-07-04 - Runner 审计完整性与回放校验准备审计只读层

状态：已完成并验证。

本轮完成：
- 新增 `runner_audit_integrity_replay_verification_audit.py`，审计未来审计记录、Runner event、启动配置、失败原因之间的一致性校验和回放核验规则。
- 新增接口：`GET /api/project/runner-audit-integrity-replay-verification-audits`。
- bootstrap 新增 `runner_audit_integrity_replay_verification_audits` 字段。
- 接入向导新增“Runner 审计完整性与回放校验准备审计”功能区块。
- Runner 工作台阶段流新增“回放校验”阶段，阶段数从 36 增至 37。
- 验证脚本纳入新层回归：未保存 profile 时为 `no_saved_profiles`，完整临时治理链下为 `integrity_replay_audit_required`。

边界：
```text
不读取 audit log。
不打开 audit log。
不写 audit log。
不读取审计记录。
不持久化审计记录。
不读取 Runner event。
不写 Runner event。
不打开 runner event log。
不写 event log。
不读取配置快照。
不执行完整性校验。
不执行回放校验。
不执行一致性校验。
不读写日志文件。
不扫描日志目录。
不打开、读取或捕获 stdout/stderr。
不创建或控制进程。
不调度真实 timeout。
不开放真实 launch/cancel/timeout POST API。
不导入或调用执行适配器。
不创建、保存或修改 Runner session。
不收集或保存授权。
不授予启动权限。
不写用户项目。
```

验证：
```text
python ast ok 80
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
tools/verify_realistic_samples.py ok
compileall ok with isolated pycache
git diff --check ok
/api/project/runner-audit-integrity-replay-verification-audits -> project_runner_audit_integrity_replay_verification_audits.v1
/api/project/bootstrap.runner_audit_integrity_replay_verification_audits -> project_runner_audit_integrity_replay_verification_audits.v1
API status=no_saved_profiles launchable_count=0 integrity_check_count=0 replay_check_count=0 consistency_check_count=0
API audit_only=true reads_audit_log=false reads_events=false performs_replay=false
Playwright Runner 工作台 stageCount=37
Playwright hasIntegrityReplayStage=true
Playwright 接入向导 sectionExists=true
Playwright textIncludesSchema=true
Playwright textIncludesEvidence=true
Browser mojibake check false
服务已重启：PID 55348，URL http://127.0.0.1:8765/
```

下一步建议：
```text
继续项目功能开发。下一步可新增“Runner 校验差异报告实现准备审计”只读层，检查未来完整性/回放校验发现差异后如何分类、分级、展示、关联证据和阻断真实启动；仍不读取审计日志、不执行回放、不写事件、不创建进程。
作用：提前约束异常校验结果的用户可理解输出，避免后续发现事件链与审计记录不一致时只能得到模糊错误，无法定位原因或决定是否阻断真实测试。
```
## 2026-07-04 - Runner 校验差异报告实现准备审计只读层

作用：
- 约束未来完整性/回放校验发现差异后，如何分类、分级、展示、关联证据和映射阻断原因。
- 在真实启动能力进入实现前，先明确差异报告必须具备的机器可读结构、操作者提示、脱敏规则和无副作用边界。
- 防止后续把“审计准备”误当成“已经执行回放、已经生成真实差异报告、已经做出启动阻断决策”。

已完成：
- 新增 `runner_verification_discrepancy_report_audit.py`。
- 新增接口 `GET /api/project/runner-verification-discrepancy-report-audits`。
- bootstrap 新增 `runner_verification_discrepancy_report_audits`。
- Runner 工作台新增“差异报告”阶段，当前阶段总数为 38。
- 接入向导新增“Runner 校验差异报告实现准备审计”区块。
- `tools/verify_realistic_samples.py` 已纳入样例验证。

验证结果：
```text
python ast ok 81
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
verify_realistic_samples.py ok
git diff --check ok
compileall ok
/api/project/runner-verification-discrepancy-report-audits -> project_runner_verification_discrepancy_report_audits.v1
status=no_saved_profiles
launchable_count=0
audit_only=True
generates_discrepancy_reports=False
makes_blocking_decisions=False
reads_runner_events=False
Runner 工作台 stageCount=38
接入向导区块存在=True
乱码检测=False
```

当前服务：
```text
http://127.0.0.1:8765/
PID: 40148
```

边界：
- 不执行命令。
- 不创建进程。
- 不读取 runner event。
- 不读取或写入审计日志。
- 不执行完整性校验或回放校验。
- 不生成真实差异报告。
- 不做真实启动阻断决策。
- 不生成真实操作者消息。
- 不开放真实启动 API。
- 不修改用户项目。

下一步建议：

继续项目功能开发。下一步可新增“Runner 真实启动只读最终闸门准备审计”层。

作用：把所有前置只读审计层汇总成一个真实启动前最终只读门禁，明确哪些证据仍缺失、哪些动作仍被禁止、哪些条件满足后才允许进入真实实现讨论，避免后续过早开放真实启动 API。

## 2026-07-04 - Runner 真实启动最终闸门准备审计只读层

作用：
- 汇总前置 Runner 只读审计层，形成真实启动前的最终只读门禁。
- 明确真实启动仍被哪些证据缺口、实现缺口、API 缺席、授权边界和安全不变量阻断。
- 防止后续在未完成授权实现轮次前误注册启动 API、误启用启动 UI、误创建进程或误做真实启动决策。

已完成：
- 新增 `runner_real_launch_final_gate_audit.py`。
- 新增接口 `GET /api/project/runner-real-launch-final-gate-audits`。
- bootstrap 新增 `runner_real_launch_final_gate_audits`。
- Runner 工作台新增“最终闸门”阶段，当前阶段总数为 39。
- 接入向导新增“Runner 真实启动最终闸门准备审计”区块。
- `tools/verify_realistic_samples.py` 已纳入样例验证。

验证结果：
```text
python ast ok 64
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
verify_realistic_samples.py ok
git diff --check ok
compileall ok
/api/project/runner-real-launch-final-gate-audits -> project_runner_real_launch_final_gate_audits.v1
status=no_saved_profiles
required_layer_count=14
launchable_count=0
registered_endpoint_count=0
final_gate_decision_count=0
audit_only=True
registers_launch_api=False
enables_launch_ui=False
creates_process=False
makes_launch_decisions=False
Runner 工作台 stageCount=39
接入向导区块存在=True
乱码检测=False
```

当前服务：
```text
http://127.0.0.1:8765/
PID: 53076
```

边界：
- 不执行命令。
- 不创建进程。
- 不注册 launch/cancel/timeout POST API。
- 不启用启动 UI。
- 不授权、不采集授权、不存储授权。
- 不调用执行适配器。
- 不创建或修改 Runner session。
- 不打开 stdout/stderr。
- 不读写 runner event。
- 不读写 audit log 或 audit record。
- 不读取 config snapshot。
- 不执行完整性/回放校验。
- 不生成真实差异报告。
- 不做真实启动决策。
- 不读写日志。
- 不写配置文件。
- 不修改用户项目。

下一步建议：

继续项目功能开发。下一步可新增“Runner 证据索引与缺口导航只读层”。

作用：把最终闸门汇总出的缺失证据、预启动阻断、必备层和上游阶段映射成可导航索引，让后续实现或测试前能快速定位“缺什么、归属哪一层、下一步补哪里”，仍不读取日志、不创建进程、不开放真实启动 API。

## 2026-07-04 - Runner 证据索引与缺口导航只读层

作用：
- 把最终闸门中的缺失证据、预启动阻断和必备层整理成统一索引。
- 为每个缺口生成 owning stage、证据组、来源报告和修复提示，帮助后续定位“缺什么、归属哪一层、下一步补哪里”。
- 保持导航只读和无副作用，不读日志、不读事件、不读审计记录、不读取配置快照、不执行校验、不创建进程、不开放真实启动 API。

已完成：
- 新增 `runner_evidence_gap_index.py`。
- 新增接口 `GET /api/project/runner-evidence-gap-indexes`。
- bootstrap 新增 `runner_evidence_gap_indexes`。
- Runner 工作台新增“缺口索引”阶段，当前阶段总数为 40。
- 接入向导新增“Runner 证据索引与缺口导航”区块。
- `tools/verify_realistic_samples.py` 已纳入样例验证。

验证结果：
```text
python ast ok 65
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
verify_realistic_samples.py ok
git diff --check ok
compileall ok
/api/project/runner-evidence-gap-indexes -> project_runner_evidence_gap_indexes.v1
status=no_saved_profiles
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
Runner 工作台 stageCount=40
接入向导区块存在=True
乱码检测=False
```

当前服务：
```text
http://127.0.0.1:8765/
PID: 57808
```

边界：
- 不执行命令。
- 不创建进程。
- 不注册 launch/cancel/timeout POST API。
- 不启用启动 UI。
- 不调用执行适配器。
- 不创建或修改 Runner session。
- 不打开 stdout/stderr。
- 不读写 runner event。
- 不读写 audit log 或 audit record。
- 不读取 config snapshot。
- 不执行完整性/回放校验。
- 不生成真实差异报告。
- 不做真实启动决策。
- 不读写日志。
- 不采集、不存储、不授予授权。
- 不写配置文件。
- 不修改用户项目。

下一步建议：

继续项目功能开发。下一步可新增“Runner 缺口导航 UI 联动只读层”。

作用：让证据索引中的条目能在 Runner 工作台中选中对应阶段、打开对应证据组或定位到对应阻断项，使索引真正成为排查入口；仍只改变页面选择状态，不读取日志、不创建进程、不开放真实启动 API。

## 2026-07-04 - Runner 缺口导航 UI 联动只读层

作用：
- 让 Runner 工作台“缺口索引”中的条目可点击。
- 点击后自动选中 owning stage，并打开对应证据组，形成从“缺口”到“责任层”的页面内定位链路。
- 保持只读 UI 联动：只改变页面选择状态，不读取日志、不创建进程、不开放真实启动 API、不写用户项目。

已完成：
- `runner-workbench.js` 从 `reports[].index_entries[].navigation` 提取 `stage_key`、`evidence_group` 和 `item_key`。
- 缺口条目新增紧凑导航按钮，显示标题、详情、状态、profile 和目标阶段。
- 新增缺口导航事件委托，复用现有 `selectStage` 与 `openEvidenceGroup`。
- `styles.css` 新增缺口导航条目样式。
- 修复后半段 Runner 审计端点的递归重复构建问题：新增 `_project_runner_real_launch_audit_chain()`，让最终闸门和缺口索引等接口复用单次链式聚合结果。

根因：
- UI 联动根因：后端已提供缺口导航字段，但前端此前只把 `index_entries` 当作普通报告证据文本展示，没有渲染为可点击定位目标。
- 接口超时根因：`/api/project/runner-evidence-gap-indexes` 通过多层函数递归重建上游 Runner 审计链，直接函数计时约 21.774 秒，导致真实 HTTP 请求容易超时。

验证结果：
```text
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
node --check src/flowtrace/ui/app.js ok
python -m compileall -q src ok
python tools/verify_realistic_samples.py ok
git diff --check ok
direct _project_runner_evidence_gap_indexes timing: 0.702s
/api/project/runner-evidence-gap-indexes -> project_runner_evidence_gap_indexes.v1
status=no_saved_profiles
launchable_count=0
executes_commands=False
creates_process=False
evidence_gap_index_only=True
synthetic UI click: runner_evidence_gap_indexes -> runner_launch_api_contracts
opened evidence group: 阻断动作
Runner 工作台 stageCount=40
缺口索引阶段存在=True
乱码检测=False
```

当前服务：
```text
http://127.0.0.1:8765/
PID: 62748
```

边界：
- 不执行命令。
- 不创建进程。
- 不注册 launch/cancel/timeout POST API。
- 不启用启动 UI。
- 不调用执行适配器。
- 不创建或修改 Runner session。
- 不打开 stdout/stderr。
- 不读写 runner event。
- 不读写 audit log 或 audit record。
- 不读取 config snapshot。
- 不执行完整性/回放校验。
- 不生成真实差异报告。
- 不做真实启动决策。
- 不读写日志。
- 不采集、不存储、不授予授权。
- 不写配置文件。
- 不修改用户项目。

下一步建议：

继续项目功能开发。下一步可新增“Runner 配置 schema 稳定化只读层”。

作用：为 `flowtrace.runner.json` 的未来真实执行配置明确字段版本、默认禁用策略、兼容性规则和错误映射，避免后续进入真实测试时因配置格式漂移造成不兼容 bug；仍只做 schema 与校验报告，不创建配置、不执行命令、不开放启动 API。

## 2026-07-04 - Runner 配置 Schema 稳定化只读层

作用：
- 固定未来 `flowtrace.runner.json` 的 schema 版本：`flowtrace_runner_config.v1`。
- 明确默认禁用策略、字段契约、兼容性规则和错误码映射，降低后续真实测试前的配置不兼容风险。
- 让前端、配置检查、真实测试准备层可以复用同一套错误码和字段契约；当前仍只读，不创建配置、不执行命令、不开放启动 API。

已完成：
- 新增 `runner_config_schema_stabilization.py`。
- 新增接口 `GET /api/project/runner-config-schema-stabilizations`。
- bootstrap 新增 `runner_config_schema_stabilizations`。
- Runner 工作台新增“配置 Schema”阶段，当前阶段总数为 41。
- 接入向导新增“Runner 配置 Schema 稳定化”区块。
- 治理汇总层纳入该层，治理层数从 18 增至 19。
- `tools/verify_realistic_samples.py` 已覆盖空路径和保存配置路径。

验证结果：
```text
python -m compileall -q src tools ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
node --check runner-workbench.js ok
python tools/verify_realistic_samples.py ok
git diff --check ok
/api/project/runner-config-schema-stabilizations -> project_runner_config_schema_stabilizations.v1
status=no_saved_profiles
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
bootstrap includes runner_config_schema_stabilizations=True
governance_layer_count=19
Runner 工作台 stageCount=41
配置 Schema 阶段存在=True
接入向导区块存在=True
flowtrace_runner_config.v1 可见=True
乱码检测=False
```

当前服务：
```text
http://127.0.0.1:8765/
PID: 15572
```

边界：
- 不执行命令。
- 不创建进程。
- 不注册 launch/cancel/timeout POST API。
- 不启用启动 UI。
- 不调用执行适配器。
- 不创建或修改 Runner session。
- 不打开 stdout/stderr。
- 不读写 runner event。
- 不读写 audit log 或 audit record。
- 不读取 config snapshot。
- 不直接读取配置文件；只消费上游配置检查报告。
- 不创建或写入配置文件。
- 不做真实启动决策。
- 不采集、不存储、不授予授权。
- 不修改用户项目。

下一步建议：

继续项目功能开发。下一步可新增“Runner 配置兼容性报告只读层”。

作用：基于本轮稳定的 `flowtrace_runner_config.v1` 字段契约，把候选配置的版本兼容性、字段缺失、类型错误、默认值收敛和错误码映射生成独立报告，帮助真实测试前提前发现配置不兼容；仍不创建配置、不执行命令、不开放真实启动 API。
## 2026-07-04 - Runner 配置兼容性报告只读层

作用：
- 基于已稳定的 `flowtrace_runner_config.v1` 字段契约，对候选 `flowtrace.runner.json` 生成配置兼容性报告。
- 在真实测试前提前识别版本不兼容、必填字段缺失、类型不匹配、默认值策略不收敛等问题。
- 统一输出稳定错误码映射，供接入向导、Runner 工作台和后续准入层复用；当前仍只读，不创建配置、不执行命令、不开放真实启动 API。

已完成：
- 新增 `src/flowtrace/runner_config_compatibility_report.py`。
- 新增接口 `GET /api/project/runner-config-compatibility-reports`。
- bootstrap 新增 `runner_config_compatibility_reports`。
- Runner 工作台新增“配置兼容”阶段，当前阶段总数为 42。
- 接入向导新增“Runner 配置兼容性报告”区块。
- 治理汇总层纳入该层，治理层数从 19 增至 20。
- `tools/verify_realistic_samples.py` 已覆盖空路径和保存配置路径。

验证结果：
```text
python -m compileall -q src tools ok
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/api.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
python tools/verify_realistic_samples.py ok
git diff --check ok
/api/project/runner-config-compatibility-reports -> project_runner_config_compatibility_reports.v1
status=no_saved_profiles
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
bootstrap includes runner_config_compatibility_reports=True
governance_layer_count=20
realistic saved config status=compatibility_report_required
realistic saved config issue_count=4
realistic saved config missing_field_count=4
UI 配置兼容阶段存在=True
UI Runner 配置兼容性报告区块存在=True
UI 乱码检测=False
```

当前服务：
```text
http://127.0.0.1:8765/
PID: 61056
```

边界：
- 不执行命令。
- 不创建进程。
- 不注册 `launch/cancel/timeout` POST API。
- 不启用启动 UI。
- 不导入或调用执行适配器。
- 不创建或修改 Runner session。
- 不打开、读取或捕获 stdout/stderr。
- 不读写 runner event。
- 不读写 audit log 或 audit record。
- 不读取 config snapshot。
- 本层不直接读取配置文件，只消费 Runner 配置检查层已返回的内存 payload。
- 不创建、不写入、不修改 `flowtrace.runner.json`。
- 不采集、不存储、不授予授权。
- 不修改用户项目。

下一步建议：

继续项目功能开发。下一步可新增“Runner 配置错误码定位 UI 只读层”。
作用：把兼容性报告中的错误码、字段路径和 schema 契约说明在前端形成可点击定位链路，帮助用户从配置问题跳到具体字段约束与修复建议；仍只改变 UI 选择状态，不读取配置文件、不写配置、不执行命令、不开放真实启动 API。
## 2026-07-04 - Runner 配置错误码定位 UI 只读层

作用：
- 将 Runner 配置兼容性报告中的错误码、字段路径和问题说明转换为前端可定位对象。
- 支持从接入向导里的配置问题按钮跳转到 Runner 工作台，并自动选中“配置兼容”阶段。
- 在 Runner 工作台内新增“配置问题定位”证据组，点击定位项会展开对应证据组并高亮目标项。
- 当前只改变前端选择、展开和高亮状态；不新增 API、不读取配置文件、不写配置、不执行命令、不开放真实启动 API。

已完成：
- `runner_config_compatibility_report.py` 为每个兼容性 issue 补充 `navigation` 和 `index_entries`。
- 兼容性报告 summary 新增 `issue_navigation_target_count`。
- Runner 工作台复用已有缺口导航机制，支持外部 `flowtrace:runner-stage-target` 事件定位。
- 接入向导为兼容性报告新增错误码定位按钮。
- `tools/verify_realistic_samples.py` 新增导航目标断言。

验证结果：
```text
python -m compileall -q src tools ok
node --check src/flowtrace/ui/app.js ok
node --check src/flowtrace/ui/modules/components/onboarding.js ok
node --check src/flowtrace/ui/modules/components/runner-workbench.js ok
python tools/verify_realistic_samples.py ok
git diff --check ok
realistic saved config issue_count=4
realistic saved config issue_navigation_target_count=4
/api/project/runner-config-compatibility-reports -> project_runner_config_compatibility_reports.v1
current status=no_saved_profiles
current issue_navigation_target_count=0
executes_commands=False
creates_process=False
reads_config_file=False
writes_config_file=False
browser hasOpenFunction=True
browser selectedStageKey=runner_config_compatibility_reports
browser runnerTabActive=True
browser mojibake=False
```

当前服务：
```text
http://127.0.0.1:8765/
PID: 19168
```

边界：
- 不执行命令。
- 不创建进程。
- 不注册 `launch/cancel/timeout` POST API。
- 不启用启动 UI。
- 不导入或调用执行适配器。
- 不创建或修改 Runner session。
- 不打开、读取或捕获 stdout/stderr。
- 不读写 runner event。
- 不读写 audit log 或 audit record。
- 不读取 config snapshot。
- 不直接读取配置文件，只消费已有兼容性报告 payload。
- 不创建、不写入、不修改 `flowtrace.runner.json`。
- 不采集、不存储、不授予授权。
- 不修改用户项目。

下一步建议：

继续项目功能开发。下一步可新增“Runner 配置修复建议汇总只读层”。
作用：把兼容性问题按字段、错误码和稳定 schema 契约聚合成修复清单，帮助用户在真实测试前知道应先补哪些配置字段、调整哪些默认策略；仍只输出建议，不写配置、不执行命令、不开放真实启动 API。
## 2026-07-04 - Runner 配置修复建议汇总只读层

作用：按字段、错误码和稳定 schema 契约聚合配置兼容性问题，形成手动修复清单；只消费兼容性报告，不读写配置、不执行命令、不开放真实启动 API。

已完成：
- 新增 `runner_config_remediation_summary.py`。
- 新增 `GET /api/project/runner-config-remediation-summaries`。
- bootstrap / Runner 工作台 / 接入向导 / 治理就绪度已接入。
- Runner 工作台阶段数：43；治理层数：21。

最小验证：
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

当前服务：`http://127.0.0.1:8765/`，PID `2044`。

下一步建议：Runner 配置修复建议定位联动只读层。
作用：让修复建议条目点击后回到兼容性问题证据和对应字段契约，仅做 UI 定位，不写配置、不执行命令。
## 2026-07-04 - Runner 配置修复建议定位联动只读层

作用：让配置修复建议条目携带导航信息，点击后可复用已有定位链路跳回兼容性问题证据；仅做 UI 定位，不写配置、不执行命令。

最小验证：
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

当前服务：`http://127.0.0.1:8765/`，PID `46200`。

下一步建议：Runner 配置字段契约说明只读层。作用：把稳定 schema 的字段类型、默认值和错误码整理成独立说明视图，辅助用户手动修复配置；不写配置、不执行命令。
