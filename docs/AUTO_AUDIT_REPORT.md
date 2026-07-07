# FlowTrace 自动审计报告

## 2026-07-01 Asia/Shanghai - Run Profile 保存/恢复闭环

### 本轮目标

把“运行配置草案”推进为“可保存/可恢复”的用户确认资产，但不执行命令。

### 改动范围

```text
src/flowtrace/run_profile_store.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
src/flowtrace/ui/styles.css
tools/verify_realistic_samples.py
docs/OPTIMIZATION_LOG.md
docs/PROJECT_STATUS.md
D:\DEBUG\PROJECT_DEVELOPMENT.md
D:\DEBUG\FLOWTRACE_CODEX_HANDOFF_2026-07-01.md
```

### 边界审计

通过：

- `run_profile.py` 仍只生成命令草案。
- `run_profile_store.py` 只读写 trace 目录下的 `run_profiles.json`。
- `POST /api/project/run-profiles/save` 只接受 `profile_id`，后端从当前确定性草案中查找 profile 后保存。
- 前端不能提交任意命令内容给保存接口。
- 当前没有执行按钮，没有命令执行接口，没有 runner。
- 新增保存/取消保存只改变 FlowTrace 运行记录目录下的配置资产，不改变用户源码。

注意：

- `server.py` 中存在 `subprocess`，但用途是既有 Windows 原生文件选择器，不属于 run profile 执行路径。
- 后续如增加命令执行，必须新增独立 runner、安全预检和用户确认，不允许直接复用保存接口执行命令。

### 验证结果

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

### 结论

本轮通过。Run profile 已具备草案生成、保存、恢复、取消保存、前端状态展示和回归验收能力。下一轮应进入“执行前安全预检”，仍不直接执行目标项目命令。

## 2026-07-01 Asia/Shanghai - 执行前安全预检

### 本轮目标

为已保存 run profile 生成执行前安全预检报告，展示命令执行前需要人工复核的关键条件，但不执行目标项目命令。

### 改动范围

```text
src/flowtrace/run_profile.py
src/flowtrace/run_preflight.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
src/flowtrace/ui/styles.css
tools/verify_realistic_samples.py
docs/AUTO_AUDIT_REPORT.md
docs/OPTIMIZATION_LOG.md
docs/PROJECT_STATUS.md
D:\DEBUG\PROJECT_DEVELOPMENT.md
D:\DEBUG\FLOWTRACE_CODEX_HANDOFF_2026-07-01.md
```

### 修复的 bug

`run_profile.py` 原先生成默认环境变量时，`FLOWTRACE_DIR` 固定为目标项目根目录下的 `.flowtrace`。

这会在用户通过 `--trace-dir` 或前端选择运行记录目录时产生偏差：运行配置草案显示的 trace 目录与当前 `ProjectContext.trace_dir` 不一致。

已修复为：

```text
FLOWTRACE_DIR = ProjectContext.trace_dir
```

### 新增能力

- 新增 `src/flowtrace/run_preflight.py`，输出 `project_run_preflight.v1`。
- 新增 `GET /api/project/run-preflight`。
- 接入向导新增“执行前安全预检”区块。
- 保存 run profile 后会刷新 preflight 数据。
- 预检检查项包括：
  - 是否来自已保存 profile。
  - 是否保留用户确认门。
  - 工作目录是否存在。
  - argv 结构是否可审查。
  - 入口文件是否存在。
  - `FLOWTRACE_DIR` 是否与当前上下文一致。
  - 当前不会自动执行命令。

### 边界审计

通过：

- `run_preflight.py` 只读 profile 和上下文，不执行命令。
- `GET /api/project/run-preflight` 只返回预检报告。
- 前端只展示报告，不提供执行按钮。
- 预检 safety 标记为 `executes_commands=false`、`requires_user_confirmation=true`、`allows_shell_string=false`。

### 验证结果

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

### 结论

本轮通过。FlowTrace 现在具备 run profile 草案、保存/恢复、执行前预检报告这三段闭环，但仍不执行目标项目命令。按用户要求，本轮完成后暂停运行。

## 2026-07-01 Asia/Shanghai - 预检确认状态

### 本轮目标

在执行前安全预检之后，增加用户确认状态记录。确认只表示“用户已经复核该预检报告”，不执行目标项目命令，也不等同于最终运行授权。

### 改动范围

```text
src/flowtrace/run_confirmation_store.py
src/flowtrace/run_preflight.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
src/flowtrace/ui/styles.css
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `run_confirmation_store.py`，保存预检确认记录。
- 新增确认存储文件 `run_profile_confirmations.json`。
- 新增 `POST /api/project/run-preflight/confirm`。
- 新增 `POST /api/project/run-preflight/revoke`。
- `GET /api/project/run-preflight` 现在返回每条报告的确认状态：
  - `none`
  - `confirmed`
  - `stale`
- 确认记录绑定 profile 指纹；profile 的 argv、工作目录、环境变量等发生变化时，确认自动变成 stale。
- 前端“执行前安全预检”报告增加“确认预检 / 撤销确认”。

### 边界审计

通过：

- 确认接口只写入 FlowTrace trace 目录下的确认记录。
- 确认接口不执行命令。
- 阻断状态的预检报告不能确认。
- 确认状态不等于执行授权；后续如果增加 runner，仍必须设计最终执行确认。

注意：

- `server.py` 中的 `subprocess` 仍只用于 Windows 原生文件选择器，不属于确认或执行路径。

### 验证结果

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
GET /api/project/run-preflight schema=project_run_preflight.v1
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。FlowTrace 当前流程推进为：

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认
```

系统仍没有命令执行能力，也没有 runner。
## 2026-07-01 Asia/Shanghai - 最终执行确认门

### 本轮目标

在“运行配置保存”和“执行前安全预检确认”之后，增加单独的最终执行确认门。该确认只记录用户已经复核最终执行意图，仍不启动目标项目命令，也不引入 runner。

### 改动范围

```text
src/flowtrace/run_final_confirmation_store.py
src/flowtrace/run_execution_gate.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
src/flowtrace/ui/styles.css
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `run_final_confirmation_store.py`，保存最终执行确认记录。
- 新增确认存储文件 `run_final_confirmations.json`。
- 新增 `run_execution_gate.py`，输出 `project_run_execution_gate.v1`。
- 新增 `GET /api/project/run-execution-gate`。
- 新增 `POST /api/project/run-execution-gate/confirm`。
- 新增 `POST /api/project/run-execution-gate/revoke`。
- 接入向导新增“最终执行确认”区块。
- 最终确认绑定 run profile 指纹、预检状态、预检确认状态和预检检查项；配置或预检确认变化后会变成 stale。

### 边界审计

通过：
- 最终确认接口只写入 FlowTrace trace 目录下的 `run_final_confirmations.json`。
- 最终确认接口不会执行命令。
- 预检未确认时，最终确认接口返回阻断。
- `run_execution_gate.py` 只聚合 run profile、preflight 和最终确认状态，不扫描项目、不修改用户项目、不执行命令。
- safety 标记为 `executes_commands=false`、`requires_preflight_confirmation=true`、`requires_final_confirmation=true`、`writes_user_project=false`。

### 验证结果

```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
run_execution_gate no_saved_profiles for three samples ok
run_profile_store execution_gate_after_preflight_confirm=ready_for_final_confirmation
run_profile_store final_confirmation_after_confirm=confirmed
run_profile_store final_confirmation_after_revoke=none
GET /api/project/run-execution-gate schema=project_run_execution_gate.v1
API save profile -> confirm preflight -> confirm final -> revoke final -> revoke preflight -> remove profile ok
API final executes_commands=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。当前执行链路推进为：

```text
运行配置草案 -> 保存/恢复 -> 执行前安全预检 -> 预检确认/撤销确认 -> 最终执行确认/撤销最终确认
```

系统仍没有命令执行能力，也没有 runner。下一轮如果继续工程主线，应先设计独立 runner 的隔离边界和执行日志结构，不能把执行逻辑塞入 run profile、preflight 或 final confirmation 模块。

## 2026-07-01 Asia/Shanghai - Runner 隔离设计报告

### 本轮目标

在最终执行确认门之后，先固化独立 runner 的隔离边界、日志结构、生命周期和失败回收策略。该轮仍不实现 runner，也不执行目标项目命令。

### 改动范围

```text
src/flowtrace/runner_plan.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
src/flowtrace/ui/styles.css
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_plan.py`，输出 `project_runner_plan.v1`。
- 新增 `GET /api/project/runner-plan`。
- 接入向导新增“Runner 隔离设计”区块。
- Runner 设计报告包含：
  - 隔离策略。
  - 生命周期状态。
  - 计划日志路径。
  - 失败回收策略。
  - 前置检查项。
- 真实样例验收新增 runner plan 安全断言。

### 边界审计

通过：
- `runner_plan.py` 只生成设计报告，不启动进程。
- API 只读上下文、run profile 和最终执行门状态。
- 前端只展示设计报告，不提供执行按钮。
- safety 标记为 `executes_commands=false`、`runner_implemented=false`、`writes_user_project=false`。
- 只有最终确认完成后，runner plan 才进入 `ready_for_runner_implementation`。

### 验证结果

```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
runner_plan no_saved_profiles for three samples ok
run_profile_store runner_plan_after_final_confirm=ready_for_runner_implementation
GET /api/project/runner-plan schema=project_runner_plan.v1
API save profile -> confirm preflight -> confirm final -> runner plan -> cleanup ok
runner plan executes_commands=False
runner plan runner_implemented=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。当前工程主线仍停在“执行设计和确认门”，还没有真实执行器。下一轮如继续推进，应实现 runner 的最小不可执行骨架或执行请求草案存储；在真正启动进程前，仍需二次确认 UI 和执行日志写入策略审计。

## 2026-07-01 Asia/Shanghai - 执行请求草案与二次确认

### 本轮目标

在 Runner 隔离设计报告之后，增加执行请求草案存储和二次确认 UI。该轮仍不实现 runner，也不启动目标项目命令。

### 改动范围

```text
src/flowtrace/execution_request_store.py
src/flowtrace/execution_request.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
src/flowtrace/ui/styles.css
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `execution_request_store.py`，保存执行请求草案和二次确认状态。
- 新增存储文件 `execution_requests.json`。
- 新增 `execution_request.py`，输出 `project_execution_requests.v1`。
- 新增 `GET /api/project/execution-requests`。
- 新增 `POST /api/project/execution-requests/prepare`。
- 新增 `POST /api/project/execution-requests/confirm`。
- 新增 `POST /api/project/execution-requests/revoke`。
- 新增 `POST /api/project/execution-requests/remove`。
- 接入向导新增“执行请求草案”区块。

### 边界审计

通过：
- 执行请求接口只写入 FlowTrace trace 目录下的 `execution_requests.json`。
- 准备草案、二次确认、撤销确认和移除草案都不执行命令。
- 二次确认前必须先准备执行请求草案。
- 执行请求草案绑定 run profile 和 runner plan 指纹；关键条件变化后会变成 stale。
- safety 标记为 `executes_commands=false`、`runner_implemented=false`、`request_store_only=true`、`requires_second_confirmation=true`、`writes_user_project=false`。

### 验证结果

```text
python compileall src/tools/examples ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/execution-requests schema=project_execution_requests.v1
API save profile -> confirm preflight -> confirm final -> prepare request -> second confirm -> revoke -> remove -> cleanup ok
execution request executes_commands=False
execution request runner_implemented=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。当前工程主线仍没有真实执行器，但已经具备执行请求草案和二次确认状态。下一轮如继续推进，应先实现 runner 的最小不可执行骨架和 runner 事件 schema，再进入真实进程启动。

## 2026-07-01 Asia/Shanghai - Runner 会话草案与事件 schema

### 本轮目标

在执行请求二次确认之后，增加 runner 最小不可执行骨架。该骨架只生成 runner 会话草案和事件 schema 预览，不启动进程、不执行命令、不写用户源码。

### 改动范围

```text
src/flowtrace/runner_session_store.py
src/flowtrace/runner_session.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
src/flowtrace/ui/styles.css
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_session_store.py`，保存 runner 会话草案状态。
- 新增存储文件 `runner_sessions.json`。
- 新增 `runner_session.py`，输出 `project_runner_sessions.v1`。
- 新增 `runner_event_schema.v1`，定义未来 runner 日志 JSONL 的字段、事件类型和 payload 规则。
- 新增 `GET /api/project/runner-sessions`。
- 新增 `POST /api/project/runner-sessions/prepare`。
- 新增 `POST /api/project/runner-sessions/remove`。
- 接入向导新增“Runner 会话草案”区块。

### 边界审计

通过：
- runner 会话草案只能基于已二次确认的执行请求生成。
- runner 会话草案只写入 FlowTrace trace 目录下的 `runner_sessions.json`。
- `runner_session.py` 只生成报告和事件 schema，不实现 runner。
- `runner_session_store.py` 只保存会话草案，不创建进程。
- safety 标记为 `executes_commands=false`、`creates_process=false`、`runner_implemented=false`、`skeleton_only=true`、`session_store_only=true`、`requires_second_confirmed_request=true`、`writes_user_project=false`。

### 验证结果

```text
python ast ok 47
python compileall blocked by pycache PermissionError in local environment
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-sessions schema=project_runner_sessions.v1
event_schema=runner_event_schema.v1
API save profile -> confirm preflight -> confirm final -> prepare request -> second confirm -> prepare runner session -> remove session -> cleanup ok
runner session status=drafted
runner session after execution request revoke=stale
runner session stale can_remove=True
runner session executes_commands=False
runner session creates_process=False
runner session runner_implemented=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。当前工程主线已经推进到 runner 启动前的最后一层草案，但仍没有真实执行器。下一轮如继续推进，应设计启动前快照和真实 runner API 的审计边界；在审计前不要启动目标项目命令。

## 2026-07-01 Asia/Shanghai - 启动前快照

### 本轮目标

在 Runner 会话草案之后增加启动前快照层，固化 profile、runner session、execution request、event schema 和 safety 标记的一致性证据。该层仍不启动进程、不执行命令、不写用户源码。

### 改动范围

```text
src/flowtrace/runner_launch_snapshot_store.py
src/flowtrace/runner_launch_snapshot.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
src/flowtrace/ui/styles.css
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_launch_snapshot_store.py`，保存启动前快照状态。
- 新增存储文件 `runner_launch_snapshots.json`。
- 新增 `runner_launch_snapshot.py`，输出 `project_runner_launch_snapshots.v1`。
- 新增 `runner_launch_snapshot_schema.v1`，定义启动前快照必须包含的证据段和规则。
- 新增 `GET /api/project/runner-launch-snapshots`。
- 新增 `POST /api/project/runner-launch-snapshots/prepare`。
- 新增 `POST /api/project/runner-launch-snapshots/remove`。
- 接入向导新增“启动前快照”区块。

### 边界审计

通过：
- 启动前快照只能基于已生成的 runner 会话草案创建。
- 启动前快照只写入 FlowTrace trace 目录下的 `runner_launch_snapshots.json`。
- 上游 runner 会话被移除或失效后，已有启动前快照会变成 `stale`，且可移除。
- `runner_launch_snapshot.py` 只生成报告和 schema，不实现 runner。
- `runner_launch_snapshot_store.py` 只保存快照状态，不创建进程。
- safety 标记为 `executes_commands=false`、`creates_process=false`、`runner_implemented=false`、`launch_enabled=false`、`snapshot_store_only=true`、`requires_runner_session_drafted=true`、`writes_user_project=false`。

### 验证结果

```text
python ast ok 49
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-launch-snapshots schema=project_runner_launch_snapshots.v1
snapshot_schema=runner_launch_snapshot_schema.v1
API save profile -> confirm preflight -> confirm final -> prepare request -> second confirm -> prepare runner session -> prepare launch snapshot -> remove runner session -> stale snapshot -> remove snapshot -> cleanup ok
runner launch snapshot status=snapshotted
runner launch snapshot after session remove=stale
runner launch snapshot stale can_remove=True
runner launch snapshot executes_commands=False
runner launch snapshot creates_process=False
runner launch snapshot launch_enabled=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。当前工程已经具备真实 runner 启动前的一致性证据封存层，但仍没有真实执行器。下一轮可以设计 dry-run runner API；该 API 必须继续默认禁用真实进程启动，并消费启动前快照而不是重新推断上游状态。

## 2026-07-01 Asia/Shanghai - Dry-run Runner API

### 本轮目标

在启动前快照之后增加 dry-run runner 层。该层只消费已生成的启动前快照，生成 dry-run 记录、日志计划和生命周期预览；不启动进程、不执行命令、不创建 stdout/stderr 日志文件。

### 改动范围

```text
src/flowtrace/runner_dry_run_store.py
src/flowtrace/runner_dry_run.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_dry_run_store.py`，保存 dry-run runner 记录。
- 新增存储文件 `runner_dry_runs.json`。
- 新增 `runner_dry_run.py`，输出 `project_runner_dry_runs.v1`。
- 新增 `runner_dry_run_schema.v1`，定义生命周期预览、输出分片策略和日志计划。
- 新增 `GET /api/project/runner-dry-runs`。
- 新增 `POST /api/project/runner-dry-runs/prepare`。
- 新增 `POST /api/project/runner-dry-runs/remove`。
- 接入向导新增“Dry-run Runner”区块。

### 边界审计

通过：
- dry-run runner 只能基于已生成的启动前快照创建。
- dry-run runner 只写入 FlowTrace trace 目录下的 `runner_dry_runs.json`。
- 上游启动前快照被移除或失效后，已有 dry-run 记录会变成 `stale`，且可移除。
- `runner_dry_run.py` 只生成报告、schema 和日志计划，不实现真实 runner。
- `runner_dry_run_store.py` 只保存 dry-run 记录，不创建进程。
- safety 标记为 `executes_commands=false`、`creates_process=false`、`runner_implemented=false`、`dry_run_only=true`、`launch_enabled=false`、`dry_run_store_only=true`、`requires_launch_snapshot=true`、`writes_user_project=false`。

### 验证结果

```text
python ast ok 51
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-dry-runs schema=project_runner_dry_runs.v1
dry_schema=runner_dry_run_schema.v1
API save profile -> confirm preflight -> confirm final -> prepare request -> second confirm -> prepare runner session -> prepare launch snapshot -> prepare dry-run -> remove launch snapshot -> stale dry-run -> remove dry-run -> cleanup ok
runner dry-run status=prepared
runner dry-run after snapshot remove=stale
runner dry-run stale can_remove=True
runner dry-run planned_logs=True
runner dry-run executes_commands=False
runner dry-run creates_process=False
runner dry-run launch_enabled=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。当前工程已具备真实 runner 前的 dry-run 外壳，但仍没有真实执行器。下一轮可以设计真实 runner 的显式开关与更细的日志分片策略；默认仍应保持真实执行禁用。

## 2026-07-01 Asia/Shanghai - Runner 启动开关策略

本轮新增 `runner_launch_control.py`，输出 `project_runner_launch_controls.v1` 和 `runner_launch_control_schema.v1`，并新增只读 API `GET /api/project/runner-launch-controls`。

边界审计通过：没有新增 POST API，没有新增存储文件，不执行命令，不创建进程。即使完整 dry-run 链路就绪，真实启动仍为 `disabled_by_policy`，`launchable_count=0`，`launch_api_available=false`，`launch_enabled=false`。

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

结论：本轮通过。下一步继续细化 stdout/stderr 分片、最大日志大小、尾部摘要、取消、超时和完成刷新策略；仍不要启用真实执行。
## 2026-07-01 Asia/Shanghai - Runner 运行时策略

### 本轮目标

在 Runner 启动开关策略之后，补齐真实 runner 之前必须明确的运行时策略层：输出分片、最大输出限制、尾部摘要、取消、超时、完成刷新。该层只生成策略报告，不开启真实执行。

### 改动范围

```text
src/flowtrace/runner_runtime_policy.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_runtime_policy.py`，输出 `project_runner_runtime_policies.v1`。
- 新增 `runner_runtime_policy_schema.v1`，固化输出、取消、超时和完成策略。
- 新增只读 API `GET /api/project/runner-runtime-policies`。
- 接入向导新增“Runner 运行时策略”区块。
- 验收脚本覆盖完整链路后的运行时策略状态。

### 边界审计

通过：
- 没有新增 POST API。
- 没有新增存储文件。
- 不执行命令。
- 不创建进程。
- 不创建 stdout/stderr 文件。
- 不写用户项目。
- 真实启动仍为禁用状态。
- 完整 dry-run 链路后，运行时策略状态为 `ready_but_launch_disabled`，`launchable_count=0`。

### 验证结果

```text
python ast ok 53
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-runtime-policies schema=project_runner_runtime_policies.v1
runtime_schema=runner_runtime_policy_schema.v1
status=ready_but_launch_disabled
report=ready_but_launch_disabled
launchable_count=0
stdout_chunk_bytes=4096
stderr_chunk_bytes=4096
default_timeout_seconds=120
executes=False
creates_process=False
launch_enabled=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。当前执行准备链路已经推进到运行时策略层，但仍没有真实 runner。下一轮可以设计未来真实执行所需的显式配置字段和服务启动开关，或继续新增只读 `runner_execution_config.py`，默认仍保持真实执行禁用。
## 2026-07-01 Asia/Shanghai - Runner 执行配置只读层

### 本轮目标

在 Runner 运行时策略之后，新增真实执行配置只读层，固化未来真实 runner 必须满足的显式配置条件：配置文件、服务启动开关、环境开关、输入确认短语、进程隔离、日志限制、取消超时和完成刷新。该层不写配置、不保存状态、不提供真实启动 API。

### 改动范围

```text
src/flowtrace/runner_execution_config.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_execution_config.py`，输出 `project_runner_execution_configs.v1`。
- 新增 `runner_execution_config_schema.v1`。
- 新增只读 API `GET /api/project/runner-execution-configs`。
- 接入向导新增“Runner 执行配置”区块。
- 上游保存、确认、撤销、session、snapshot、dry-run 变化后，会刷新执行配置报告。

### 边界审计

通过：
- 没有新增 POST API。
- 没有新增存储文件。
- 不写 `flowtrace.runner.json`。
- 不执行命令。
- 不创建进程。
- 不创建 stdout/stderr 文件。
- 不写用户项目。
- 真实启动仍为禁用状态。
- 完整链路后状态为 `configuration_required`，`launchable_count=0`。

### 验证结果

```text
compileall ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
GET /api/project/runner-execution-configs schema=project_runner_execution_configs.v1
config_schema=runner_execution_config_schema.v1
status=configuration_required
report=configuration_required
launchable_count=0
config_file=flowtrace.runner.json
typed=RUN TARGET PROJECT
argv_tokenized=True
executes=False
creates_process=False
launch_enabled=False
launch_api=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。当前执行准备链路已经固化到“未来真实执行配置需求”，但仍没有真实 runner、没有启动接口、没有目标项目进程。下一轮可以继续做真实执行配置文件的解析草案或服务启动参数审计，仍保持默认禁用。

## 2026-07-01 Asia/Shanghai - Runner 配置检查只读层

### 本轮目标

在 Runner 执行配置需求报告之后，新增配置文件检查层。该层只读取候选 `flowtrace.runner.json`，报告配置文件是否存在、JSON 是否可解析、关键字段是否合规；不创建配置文件、不修改用户项目、不提供真实启动 API。

### 改动范围

```text
src/flowtrace/runner_execution_config_check.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_execution_config_check.py`，输出 `project_runner_execution_config_checks.v1`。
- 新增 `runner_execution_config_check_schema.v1`。
- 新增只读 API `GET /api/project/runner-execution-config-checks`。
- 接入向导新增“Runner 配置检查”区块。
- 配置检查候选位置为目标项目根目录和 trace 目录下的 `flowtrace.runner.json`。
- 缺少配置文件时报告 `config_missing`，不会自动创建文件。
- 临时合法配置存在时报告 `config_present_but_launch_disabled`，仍不可启动。

### 边界审计

通过：
- 没有新增 POST API。
- 没有新增存储文件。
- 不创建 `flowtrace.runner.json`。
- 不修改 `flowtrace.runner.json`。
- 不执行命令。
- 不创建进程。
- 不创建 stdout/stderr 文件。
- 不写用户项目。
- 真实启动仍为禁用状态。

### 验证结果

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
report=config_missing
config_file=missing
candidates=2
launchable_count=0
executes=False
creates_process=False
creates_config=False
launch_enabled=False
launch_api=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。当前工程已经能读取并审查未来真实执行配置文件，但仍不会创建配置、不会执行目标项目、不会开放真实启动接口。下一轮可以设计服务启动参数审计层，继续保持默认禁用真实执行。

## 2026-07-01 Asia/Shanghai - Runner 服务开关审计只读层

### 本轮目标

在 Runner 配置检查只读层之后，新增服务开关审计层。该层只消费已有的 Runner 配置检查报告，输出未来真实执行必须满足的服务启动参数、环境开关、配置开关和确认短语要求；不读取当前环境变量、不解析当前进程参数、不注册真实启动 API。

### 改动范围

```text
src/flowtrace/runner_service_flag_audit.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_service_flag_audit.py`，输出 `project_runner_service_flag_audits.v1`。
- 新增 `runner_service_flag_audit_schema.v1`。
- 新增只读 API `GET /api/project/runner-service-flag-audits`。
- 接入向导新增“Runner 服务开关审计”区块。
- 审计层声明未来真实执行需要 `--allow-real-execution`、`FLOWTRACE_ALLOW_REAL_EXECUTION=1`、`runner.enable_real_execution=true` 和确认短语 `RUN TARGET PROJECT`。
- 该层明确不检查 `process.argv`、`os.environ`、shell history 或外部 supervisor 状态。

### 边界审计

通过：
- 没有新增 POST API。
- 没有新增存储文件。
- 不读取环境变量。
- 不解析进程参数。
- 不创建 `flowtrace.runner.json`。
- 不修改 `flowtrace.runner.json`。
- 不执行命令。
- 不创建进程。
- 不创建 stdout/stderr 文件。
- 不写用户项目。
- 真实启动仍为禁用状态。

### 验证结果

```text
python ast ok 38
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-service-flag-audits schema=project_runner_service_flag_audits.v1
service_schema=runner_service_flag_audit_schema.v1
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

### 结论

本轮通过。当前工程已经能报告未来真实执行所需的服务级显式开关，但仍不读取实际运行环境、不解析当前进程参数、不创建进程、不开放真实启动接口。下一轮可以继续设计日志目录策略，仍保持只读。
## 2026-07-01 Asia/Shanghai - Runner 日志目录策略只读层

本轮新增 Runner 日志目录策略只读层，继续沿用 Runner 真实执行禁用边界。

新增文件：

- `src/flowtrace/runner_log_directory_policy.py`

新增接口：

- `GET /api/project/runner-log-directory-policies`

新增 schema：

- `project_runner_log_directory_policies.v1`
- `runner_log_directory_policy_schema.v1`

边界检查：

- 不执行命令。
- 不创建进程。
- 不创建日志目录。
- 不打开日志文件。
- 不写 stdout/stderr/events/summary。
- 不创建或修改 Runner 配置文件。
- 不开放真实 launch API。

验证结果：

- `python ast ok`
- `node --check` 全量前端 JS 通过。
- `verify_realistic_samples.py` 通过。
- `/api/project/runner-log-directory-policies` 返回 `schema=project_runner_log_directory_policies.v1`。
- 当前 live 状态为 `no_saved_profiles`，`launchable_count=0`。
- store 验证路径为 `log_directory_policy_required`，`launchable_count=0`。

浏览器可视化验证仍被本地沙箱阻断：`windows sandbox failed: spawn setup refresh`。
## 2026-07-01 Asia/Shanghai - Runner 日志保留/轮转策略只读层

本轮新增 Runner 日志保留/轮转策略只读层，继续保持真实执行和日志清理能力禁用。

新增文件：

- `src/flowtrace/runner_log_retention_policy.py`

新增接口：

- `GET /api/project/runner-log-retention-policies`

新增 schema：

- `project_runner_log_retention_policies.v1`
- `runner_log_retention_policy_schema.v1`

边界检查：

- 不扫描日志目录。
- 不删除日志。
- 不轮转日志。
- 不重命名日志。
- 不截断日志。
- 不写日志。
- 不执行命令。
- 不创建进程。
- 不开放真实 launch API。

验证结果：

- `python ast ok`
- 全量前端 JS `node --check` 通过。
- `verify_realistic_samples.py` 通过。
- `/api/project/runner-log-retention-policies` 返回 `schema=project_runner_log_retention_policies.v1`。
- 当前 live 状态为 `no_saved_profiles`，`launchable_count=0`。
- store 验证路径为 `log_retention_policy_required`，`launchable_count=0`。

浏览器可视化验证仍被本地沙箱阻断：`windows sandbox failed: spawn setup refresh`。
## 2026-07-02 Asia/Shanghai - Runner 日志清理预览只读层

本轮新增 Runner 日志清理预览只读层，继续保持真实清理和真实执行能力禁用。

新增文件：

- `src/flowtrace/runner_log_cleanup_preview.py`

新增接口：

- `GET /api/project/runner-log-cleanup-previews`

新增 schema：

- `project_runner_log_cleanup_previews.v1`
- `runner_log_cleanup_preview_schema.v1`

边界检查：

- 不扫描日志目录。
- 不读取日志文件。
- 不删除日志。
- 不轮转日志。
- 不重命名日志。
- 不截断日志。
- 不写日志。
- 不执行命令。
- 不创建进程。
- 不开放真实 launch API。

验证结果：

- `python ast ok`
- 全量前端 JS `node --check` 通过。
- `verify_realistic_samples.py` 通过。
- `/api/project/runner-log-cleanup-previews` 返回 `schema=project_runner_log_cleanup_previews.v1`。
- 当前 live 状态为 `no_saved_profiles`，`launchable_count=0`，`previewed_deletion_count=0`。
- store 验证路径为 `cleanup_preview_required`，`launchable_count=0`。

浏览器可视化验证仍被本地沙箱阻断：`windows sandbox failed: spawn setup refresh`。
## 2026-07-02 Asia/Shanghai - Runner 配置检查只读层

### 本轮目标

在 Runner 执行配置需求报告之后，新增配置文件检查层。该层只读取候选 `flowtrace.runner.json`，报告配置文件是否存在、JSON 是否可解析、关键字段是否合规；不创建配置文件、不修改用户项目、不提供真实启动 API。

### 改动范围

```text
src/flowtrace/runner_execution_config_check.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_execution_config_check.py`，输出 `project_runner_execution_config_checks.v1`。
- 新增 `runner_execution_config_check_schema.v1`。
- 新增只读 API `GET /api/project/runner-execution-config-checks`。
- 接入向导新增“Runner 配置检查”区块。
- 配置检查候选位置为目标项目根目录和 trace 目录下的 `flowtrace.runner.json`。
- 缺少配置文件时报告 `config_missing`，不会自动创建文件。
- 临时合法配置存在时报告 `config_present_but_launch_disabled`，仍不可启动。

### 边界审计

通过：
- 没有新增 POST API。
- 没有新增存储文件。
- 不创建 `flowtrace.runner.json`。
- 不修改 `flowtrace.runner.json`。
- 不执行命令。
- 不创建进程。
- 不创建 stdout/stderr 文件。
- 不写用户项目。
- 真实启动仍为禁用状态。

### 验证结果

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
report=config_missing
config_file=missing
candidates=2
launchable_count=0
executes=False
creates_process=False
creates_config=False
launch_enabled=False
launch_api=False
browser visual verification blocked by local sandbox: windows sandbox failed: spawn setup refresh
```

### 结论

本轮通过。当前工程已经能读取并审查未来真实执行配置文件，但仍不会创建配置、不会执行目标项目、不会开放真实启动接口。下一轮可以设计服务启动参数审计层，继续保持默认禁用真实执行。
## 2026-07-02 Asia/Shanghai - Runner 治理就绪度只读总闸门

### 本轮目标

在日志清理审计追踪之后，新增 Runner 治理就绪度总闸门。该层只汇总已有只读治理层的状态，输出“为什么仍不能启动”的统一报告；不新增真实启动 API、不执行命令、不创建进程、不读写日志、不清理日志。

### 改动范围

```text
src/flowtrace/runner_governance_readiness.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_governance_readiness.py`，输出 `project_runner_governance_readiness.v1`。
- 新增 `runner_governance_readiness_schema.v1`。
- 新增只读 API `GET /api/project/runner-governance-readiness`。
- `/api/project/bootstrap` 新增 `runner_governance_readiness`。
- 接入向导新增“Runner 治理就绪度”区块。
- 汇总 17 个 Runner 治理层状态，并保持 `launchable_count=0`。

### 边界审计

通过：
- 没有新增 POST API。
- 没有新增存储文件。
- 不执行命令。
- 不创建进程。
- 不开放真实启动 API。
- 不读取日志文件。
- 不写日志。
- 不删除、轮转、重命名或截断日志。
- 不创建或修改配置文件。
- 不写用户项目。

### 验证结果

```text
python ast ok 44
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-governance-readiness schema=project_runner_governance_readiness.v1
governance_schema=runner_governance_readiness_schema.v1
status=governance_required
report=governance_required
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

### 结论

本轮通过。当前 Runner 工程化链路已经具备只读总闸门，能够汇总所有治理层并明确真实执行仍被禁用。下一轮仍只能继续只读治理设计，例如真实执行适配器规范草案或启动 API 合约草案，不能直接实现真实执行。
## 2026-07-02 Asia/Shanghai - Runner 执行适配器合约只读层

### 本轮目标

在 Runner 治理就绪度总闸门之后，新增执行适配器合约只读层。该层定义未来真实 Runner 执行适配器的接口、输入输出、argv/env 约束、生命周期钩子和禁止动作；不注册真实启动 API、不执行命令、不创建进程、不读写日志、不修改用户项目。

### 改动范围

```text
src/flowtrace/runner_execution_adapter_contract.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_execution_adapter_contract.py`，输出 `project_runner_execution_adapter_contracts.v1`。
- 新增 `runner_execution_adapter_contract_schema.v1`。
- 新增只读 API `GET /api/project/runner-execution-adapter-contracts`。
- `/api/project/bootstrap` 新增 `runner_execution_adapter_contracts`。
- 接入向导新增“Runner 执行适配器合约”区块。
- 前端刷新尾链收敛为 `refreshRunnerGovernanceTail()`，避免后续新增治理层时重复散落刷新逻辑。

### 边界审计

通过：
- 没有新增真实 launch POST API。
- 没有新增存储文件。
- 不调用 `subprocess.Popen`。
- 不调用 `os.system`。
- 不允许 `shell=True`。
- 不执行命令。
- 不创建进程。
- 不打开 stdout/stderr 文件。
- 不写 runner 事件日志。
- 不读写、删除、轮转或截断日志。
- 不创建或修改配置文件。
- 不写用户项目。
- `launchable_count=0`。

### 验证结果

```text
python py_compile ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-execution-adapter-contracts schema=project_runner_execution_adapter_contracts.v1
contract_schema=runner_execution_adapter_contract_schema.v1
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

### 结论

本轮通过。当前链路已经从“治理就绪度总闸门”推进到“执行适配器合约”，但真实执行仍完全禁用。下一轮可以继续做启动 API 合约草案或适配器审查报告，仍不得注册真实启动入口。
## 2026-07-02 Asia/Shanghai - Runner 启动 API 合约只读层

### 本轮目标

在 Runner 执行适配器合约之后，新增启动 API 合约只读层。该层只声明未来启动入口的请求字段、禁止字段、响应字段、幂等规则和启动前门槛；不注册真实 POST、不调用执行适配器、不创建进程、不执行命令、不写日志、不修改用户项目。

### 改动范围

```text
src/flowtrace/runner_launch_api_contract.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_launch_api_contract.py`，输出 `project_runner_launch_api_contracts.v1`。
- 新增 `runner_launch_api_contract_schema.v1`。
- 新增只读 API `GET /api/project/runner-launch-api-contracts`。
- `/api/project/bootstrap` 新增 `runner_launch_api_contracts`。
- 接入向导新增“Runner 启动 API 合约”区块。
- 合约声明未来端点 `POST /api/project/runner/launch`，但 `registered_now=false`，当前不注册。

### 边界审计

通过：
- 没有注册真实 launch POST API。
- `registered_endpoint_count=0`。
- 不调用执行适配器。
- 不从 HTTP handler 启动进程。
- 不执行命令。
- 不创建进程。
- 不打开 stdout/stderr 文件。
- 不写 runner 事件日志。
- 不读写、删除、轮转或截断日志。
- 不创建或修改配置文件。
- 不写用户项目。
- `launchable_count=0`。

### 验证结果

```text
python py_compile ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-launch-api-contracts schema=project_runner_launch_api_contracts.v1
contract_schema=runner_launch_api_contract_schema.v1
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

### 结论

本轮通过。当前链路已经具备未来启动 API 的合约说明，但服务端仍没有真实启动入口。下一轮可以做执行适配器审查报告或真实执行前的最终阻断矩阵，仍不得注册真实 POST。
## 2026-07-02 Asia/Shanghai - Runner 执行适配器审查只读层

### 本轮目标

在 Runner 启动 API 合约之后，新增执行适配器审查只读层。该层只声明未来适配器实现前必须通过的审查矩阵与证据集合；不扫描代码、不导入适配器、不调用适配器、不注册真实 POST、不创建进程、不执行命令、不写日志、不修改用户项目。

### 改动范围

```text
src/flowtrace/runner_execution_adapter_review.py
src/flowtrace/server.py
src/flowtrace/ui/app.js
src/flowtrace/ui/modules/api.js
src/flowtrace/ui/modules/components/onboarding.js
tools/verify_realistic_samples.py
```

### 新增能力

- 新增 `runner_execution_adapter_review.py`，输出 `project_runner_execution_adapter_reviews.v1`。
- 新增 `runner_execution_adapter_review_schema.v1`。
- 新增只读 API `GET /api/project/runner-execution-adapter-reviews`。
- `/api/project/bootstrap` 新增 `runner_execution_adapter_reviews`。
- 接入向导新增“Runner 执行适配器审查”区块。
- 审查矩阵声明 HTTP handler、tokenized argv、shell 拒绝、环境变量白名单、stdout/stderr hook、取消、超时、完成刷新和用户项目只读边界。

### 边界审计

通过：
- 不扫描代码。
- 不导入执行适配器。
- 不调用执行适配器。
- 不注册真实 launch POST API。
- 不创建进程。
- 不执行命令。
- 不打开 stdout/stderr 文件。
- 不写 runner 事件日志。
- 不读写、删除、轮转或截断日志。
- 不创建或修改配置文件。
- 不写用户项目。
- `implemented_adapter_count=0`。
- `launchable_count=0`。

### 验证结果

```text
python py_compile ok
node --check app.js ok
node --check api.js ok
node --check onboarding.js ok
verify_realistic_samples.py ok
compileall ok
GET /api/project/runner-execution-adapter-reviews schema=project_runner_execution_adapter_reviews.v1
review_schema=runner_execution_adapter_review_schema.v1
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

### 结论

本轮通过。当前工程已具备未来执行适配器落地前的只读审查矩阵，但仍没有真实适配器实现和真实启动入口。下一轮可以做真实执行前最终阻断矩阵，继续汇总为什么仍不能启动。

## 2026-07-02 Asia/Shanghai - Runner 日志清理执行计划只读层

本轮新增 `runner_log_cleanup_execution_plan.py`，输出 `project_runner_log_cleanup_execution_plans.v1` 和 `runner_log_cleanup_execution_plan_schema.v1`。

新增 API：

```text
GET /api/project/runner-log-cleanup-execution-plans
```

审计结论：

```text
status=no_saved_profiles
planned_operation_count=0
launchable_count=0
executes_commands=False
creates_process=False
launch_enabled=False
launch_api_available=False
stores_execution_plan=False
executes_cleanup=False
generates_candidate_manifest=False
scans_log_directory=False
reads_log_files=False
deletes_logs=False
rotates_logs=False
renames_logs=False
truncates_logs=False
writes_logs=False
writes_audit_log=False
reads_audit_log=False
writes_user_project=False
```

验证结果：

```text
Python AST parse ok
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
live API ok
bootstrap includes runner_log_cleanup_execution_plans
runner_governance_readiness layer_count=18
Playwright Edge visual check ok
```

结论：本轮通过。该层只声明未来日志清理执行计划合约，不生成候选清单、不保存计划、不执行清理、不读写审计日志。
## 2026-07-02 Asia/Shanghai - Runner final block matrix read-only layer

Added endpoint:

```text
GET /api/project/runner-final-block-matrices
```

Schemas:

```text
project_runner_final_block_matrices.v1
runner_final_block_matrix_schema.v1
```

Audit result:

```text
status=no_saved_profiles
blocking_reason_count=0
launchable_count=0
executes_commands=False
creates_process=False
launch_enabled=False
launch_api_available=False
registers_post_api=False
imports_adapter=False
calls_execution_adapter=False
opens_stdout_stderr=False
writes_runner_events=False
stores_launch_state=False
scans_log_directory=False
reads_log_files=False
writes_logs=False
deletes_logs=False
rotates_logs=False
renames_logs=False
truncates_logs=False
writes_audit_log=False
reads_audit_log=False
writes_user_project=False
creates_config_file=False
```

Validation:

```text
Python AST parse ok: 67 files
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
compileall ok with isolated PYTHONPYCACHEPREFIX
live API ok
bootstrap includes runner_final_block_matrices
runner_governance_readiness single endpoint ok, layer_count=18
Playwright Edge visual check ok
mojibake check false
```

Conclusion: passed. The layer only aggregates final blockers before real execution. It does not open a launch API, import/call an adapter, create processes, execute commands, write logs, persist audit logs, or write user project files.
## 2026-07-02 Asia/Shanghai - Runner authorization unlock audit read-only layer

Added endpoint:

```text
GET /api/project/runner-authorization-unlock-audits
```

Schemas:

```text
project_runner_authorization_unlock_audits.v1
runner_authorization_unlock_audit_schema.v1
```

Audit result:

```text
status=no_saved_profiles
missing_evidence_count=0
future_unlock_count=0
launchable_count=0
executes_commands=False
creates_process=False
launch_enabled=False
launch_api_available=False
registers_post_api=False
imports_adapter=False
calls_execution_adapter=False
grants_permission=False
collects_human_authorization=False
stores_authorization=False
stores_launch_state=False
opens_stdout_stderr=False
writes_runner_events=False
scans_log_directory=False
reads_log_files=False
writes_logs=False
deletes_logs=False
rotates_logs=False
renames_logs=False
truncates_logs=False
writes_audit_log=False
reads_audit_log=False
writes_user_project=False
creates_config_file=False
```

Validation:

```text
Python AST parse ok: 68 files
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
compileall ok with isolated PYTHONPYCACHEPREFIX
live API ok
bootstrap includes runner_authorization_unlock_audits
Playwright Edge visual check ok
mojibake check false
```

Conclusion: passed. The layer lists future authorization records and unlock evidence only. It does not collect authorization, grant permission, register launch APIs, import/call adapters, create processes, execute commands, write logs, persist audit logs, or write user project files.
## 2026-07-03 Asia/Shanghai - Runner implementation gap checklist read-only layer

Added endpoint:

```text
GET /api/project/runner-implementation-gap-checklists
```

Schemas:

```text
project_runner_implementation_gap_checklists.v1
runner_implementation_gap_checklist_schema.v1
```

Audit result:

```text
status=no_saved_profiles
gap_count=0
component_count=0
launchable_count=0
executes_commands=False
creates_process=False
runner_implemented=False
launch_enabled=False
launch_api_available=False
implementation_gap_checklist_only=True
implements_runner=False
writes_code=False
registers_post_api=False
imports_adapter=False
calls_execution_adapter=False
grants_permission=False
collects_human_authorization=False
stores_authorization=False
opens_stdout_stderr=False
writes_runner_events=False
writes_logs=False
writes_audit_log=False
writes_user_project=False
creates_config_file=False
```

Validation:

```text
Python AST parse ok: 69 files
UI JS node --check ok
app.js ESM syntax check ok
tools/verify_realistic_samples.py ok
compileall ok with isolated PYTHONPYCACHEPREFIX
live API ok
bootstrap includes runner_implementation_gap_checklists
Playwright Edge visual check ok
mojibake check false
```

Conclusion: passed. The layer lists missing implementation components only. It does not implement a runner, write code, register launch APIs, import/call adapters, create processes, execute commands, write logs, persist audit logs, or write user project files.
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