---
name: fix-failed-case
description: "Fix failed test cases by analyzing execution logs and error messages from the database. Invoke when user says '帮我自动修复这条用例' or asks to fix/repair a failed test case."
---

# 自动修复失败用例（Fix Failed Case）

根据用例名称，从数据库中获取最近一次执行失败的日志和错误信息，结合用例源码进行错误分析并自动修复。

## 启动前先收集参数

调用本 skill 需要用户提供以下参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `case_name` | 用例名称（不含 `test_` 前缀和 `.py` 后缀） | `workorder_approval` |

若用户未提供用例名称，**先向用户询问后再继续**。

## 执行流程

整个流程共 6 个步骤：

### 步骤 1：读取用例源码

1. 根据用例名称，在项目目录 `src/testcase/` 下递归查找 `test_{case_name}.py` 文件。
   - 使用 Glob 工具搜索 `src/testcase/**/test_{case_name}.py`
2. 读取该用例文件的完整代码，了解用例的功能和执行步骤。
3. 如果用例引用了页面层（`src/pages/`）或数据层（`src/data/`）的文件，也一并读取相关文件。

### 步骤 2：查询数据库获取执行记录

通过 RunCommand 工具执行预置脚本 [scripts/get_failed_case_log.py](scripts/get_failed_case_log.py)，从 `test_case_result` 表中查询该用例最近一条 `status='failed'` 的记录，获取 `log` 和 `error_message` 字段。

执行命令：

```
python .trae/skills/fix-failed-case/scripts/get_failed_case_log.py <case_name>
```

脚本会自动读取 `config/execution_config.yaml` 中的数据库配置（支持 SQLite 和 MySQL），输出格式为：

```
CASE_NAME: workorder_approval
STATUS: failed
DURATION: 30.5
CREATED_AT: 2026-07-16 10:30:00
PROJECT: LX

ERROR_MESSAGE:
Locator.click: Timeout 30000ms exceeded...

LOG:
INFO ... 登录成功
INFO ...
```

若输出 `NO_FAILED_RECORD`，说明数据库中无该用例的失败记录，需向用户说明并询问是否直接提供错误日志。

### 步骤 3：分析错误并展示修改思路

1. 综合用例源码、执行日志、错误信息进行错误分析。
2. 重点分析以下几类常见错误：
   - **页面元素定位失败**：`Locator.click: Timeout`、`waiting for selector` 等，通常是元素定位器失效或页面结构变化。
   - **断言失败**：`AssertionError`，通常是预期值与实际值不符。
   - **iframe 相关错误**：`content_frame` 定位失败，可能是页面已移除 iframe。
   - **超时错误**：`TimeoutError`，可能是页面加载慢或操作顺序有误。
   - **方法调用错误**：参数不匹配、方法不存在等。
3. 向用户展示：
   - **错误结论**：明确指出失败原因。
   - **修改思路**：具体的修改方案，涉及哪些文件、哪些方法、怎么改。

### 步骤 4：询问用户是否有补充信息

使用 AskUserQuestion 工具询问用户：

> 是否有补充信息需要提供？（例如页面元素已变更、业务逻辑已调整等）
> - 选项1：没有补充信息，直接修复
> - 选项2：有补充信息

- 如果用户选择"没有补充信息"，直接进入步骤 6。
- 如果用户选择"有补充信息"，进入步骤 5。

### 步骤 5：接收补充信息并调整修改思路

1. 接收用户的补充信息（可能包括：新的页面元素 HTML、业务规则变更说明、参考文件路径等）。
2. 综合补充信息调整修改思路。
3. 更新修改方案后进入步骤 6。

### 步骤 6：执行修改

1. 根据最终的修改思路，使用 Edit 工具对用例代码进行修改。
2. 修改原则：
   - **最小化修改**：只修改导致失败的部分，不重构不相关的代码。
   - **保持风格一致**：修改后的代码风格与原代码保持一致。
   - **参考同类方法**：如果项目中已有类似功能的正确实现，参考其实现方式。
3. 修改完成后，向用户展示修改摘要，包括：
   - 修改了哪些文件
   - 每个文件的具体修改内容
   - 修改原因
4. 提供执行命令供用户验证：`python run.py -p {project} -m {module} -c {case_name}`

## 不可违反的底线

- **不要改变用例的测试目的**：修复是让用例能正确执行，而不是改变测试逻辑。
- **不要删除断言**：断言是用例的核心，只能修正断言中的定位器或预期值，不能移除断言。
- **不要过度重构**：只修复失败点，不做额外的"改进"。
- **修改前必须先读取原文件**：不允许在未读取文件的情况下直接修改。
