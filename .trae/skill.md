---
name: standardize-recorded-script
description: Convert a raw Playwright codegen recorded script into this project's standardized three-layer (Page Object Model) test code. Use when the user wants to "标准化录制脚本"、"把录制好的脚本转成标准脚本/三层脚本"、"格式化+分层录制代码", or invokes /standardize-recorded-script. Codifies the rules from src/common/ai_formatting.py (formatting) and src/common/ai_layering.py (layering).
---
# 标准化录制脚本（录制代码 → 三层 POM 脚本）

把 Playwright `codegen` 录制出来的原始脚本，转换成本项目规范的标准代码或者**三层架构**测试代码（测试层 / 页面层 / 数据层）。本 skill 固化了项目内 AI 链路（格式化 `ai_formatting`、分层 `ai_layering`）的处理规则，作为这两条 AI 途径之外的第三条人工/Claude 处理途径；所有规则与模板均内置在本 skill 的 `references/` 中，不依赖具体项目文件。

整个流程分两个阶段，默认完成阶段一，若用户触发语明确表示将录制好的脚本转成三层脚本，再执行阶段二：

1. **阶段一 格式化** —— 录制脚本整理成单文件规范用例。详见 [references/stage1-formatting.md](references/stage1-formatting.md)
2. **阶段二 分层** —— 单文件拆成三层 POM 架构。详见 [references/stage2-layering.md](references/stage2-layering.md)

## 启动前先收集 5 个参数

调用本 skill 必须确定以下 5 个值。若用户没给全，**先向用户询问后再继续**：

| 参数              | 说明                                     | 示例                   |
| ----------------- | ---------------------------------------- | ---------------------- |
| `recorded_code` | 原始录制脚本（文件路径或直接粘贴的代码） | `temp_xxx.py`        |
| `project`       | 项目名（一级目录）                       | `LX`                 |
| `module`        | 模块名（二级目录）                       | `work_order`         |
| `case`          | 用例名（不含 `test_` 前缀和 `.py`）  | `workorder_new_page` |
| `ms_id`         | 用例在 MS 平台的 id                      | `100403`             |

## 命名规则（必须严格遵守）

由上述参数推导命名：

- `class_name` = 把 `case` 按 `_` 分割后每段首字母大写再拼接。例：`workorder_new_page` → `WorkorderNewPage`
- 测试层文件：`src/testcase/{project}/{module}/test_{case}.py`，类名 `Test{class_name}`
- 页面层文件：`src/pages/{project}/{module}/page_{case}.py`，类名 `{class_name}Page`
- 数据层文件：`src/data/{project}/{module}/data_{case}.py`（无类，用字典）

## 执行流程

1. 收齐 5 个参数（缺则询问）。
2. 读 [references/stage1-formatting.md](references/stage1-formatting.md)，按 7 条规则产出单文件格式化代码。
3. 若用户需要，把阶段一结果作为输入，读 [references/stage2-layering.md](references/stage2-layering.md)，拆成三层。
4. 按 [references/stage2-layering.md](references/stage2-layering.md) 的「写文件与收尾」把三份代码写入对应路径（目录不存在则创建），代码中不要包含 ` ```python ` 代码块标记。
5. 给出执行命令：`python run.py -p {project} -m {module} -c {case}`

## 不可违反的底线

- **核心操作逻辑在任何阶段都不得改变**——定位器、点击、填值的实际调用不要改写或"优化"，只做去冗余、加日志注释、抽取数据、封装方法。
- 若分层困难/信息不足，至少先把阶段一的单文件代码写入 `src/testcase/{project}/{module}/test_{case}.py`（可直接跑），并向用户说明未分层的原因。

## 产出风格

- 三层代码的写法、命名、注释/日志风格，**完全以 [references/stage1-formatting.md](references/stage1-formatting.md) 和 [references/stage2-layering.md](references/stage2-layering.md) 里的模板为准**（模板自包含，不依赖任何具体项目的文件）。
- 公用登录方法：`self.login(page, project_name)`，定义在各项目的 `src/base/base_test.py`（`BaseTest`）中，直接调用即可，不要改动其实现。
