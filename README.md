# Playwright+Python UI自动化测试框架

## 本项目测试前准备项目：

创建部门：uitest
创建岗位：uitest

创建作业区域：uitestArea

创建人员：uitest，uitestres，uitestop
分配权限并且添加作业人和监护人的资格证书

## 环境搭建

### 前置条件

- Python 3.13
- pip 20.0+

### 依赖安装

1. 克隆项目到本地
2. 进入项目目录
3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
4. 安装Playwright浏览器
   ```bash
   playwright install
   ```

## 目录结构

```
playwright-ui-automation/
├── config/                              # 全局配置文件目录
│   ├── execution_config.yaml            # 主配置文件（数据库、浏览器、AI模型等）
│   └── module_definitions.yaml          # 项目/模块定义与版本号
│
├── src/                                 # 项目核心业务代码目录
│   ├── base/                            # 基类封装目录
│   │   ├── base_page.py                 # 页面基类，封装通用元素操作（点击、输入、等待等）
│   │   ├── base_test.py                 # 用例基类，提供浏览器启动/关闭、登录、截图等fixture
│   │
│   ├── pages/                           # 页面对象类目录（Page层）
│   │   └── {项目}/{模块}/               # 按项目/模块组织，每个文件对应一个页面对象
│   │
│   ├── data/                            # 数据操作类目录（Data层）
│   │   └── {项目}/{模块}/               # 按项目/模块组织，每个文件对应一组测试数据
│   │
│   ├── testcase/                        # 测试用例目录（Test层）
│   │   └── {项目}/{模块}/               # 按项目/模块组织，用例与项目解耦可动态扩展
│   │
│   └── common/                          # 全局公共工具类目录
│       ├── ai_chat.py                   # AI大模型调用接口（基于OpenAI SDK）
│       ├── ai_formatting.py             # AI代码格式化，优化录制脚本可读性
│       ├── ai_layering.py               # AI代码分层，自动拆分为Page/Data/Test三层
│       ├── config_loader.py             # 配置加载器（单例），支持热更新
│       ├── module_definition_loader.py  # 项目/模块定义加载器（单例），管理中英文映射
│       ├── database.py                  # 数据库抽象层，支持SQLite和MySQL双后端
│       ├── data_generator.py            # 测试数据生成器（基于Faker），支持AI生成
│       ├── excel_utils.py               # Excel通用操作工具类（基于openpyxl）
│       ├── file_utils.py                # 文件/目录操作工具类
│       ├── logger.py                    # 日志工具（单例），支持按任务类型分文件
│       ├── screenshot.py                # 截图工具类，按执行时间戳/项目/模块/用例归档
│       ├── tool.py                      # 公用方法集合（按钮状态检查、表格操作等）
│       ├── version_control.py           # 版本控制功能模块（备份/切换/删除版本）
│       └── webhook.py                   # 企业微信Webhook推送客户端
│
├── templates/                           # Flask页面模板目录
│   ├── case_list.html                   # 用例列表页面
│   ├── execution_list.html              # 执行记录列表页面
│   ├── report.html                      # 测试报告详情页面
│   └── version_management.html          # 版本管理页面
│
├── static/                              # 静态资源目录（Bootstrap等）
├── data/                                # SQLite数据库文件目录
├── logs/                                # 日志文件归档目录
├── screenshots/                         # 截图文件归档目录
├── reports/                             # 测试报告归档目录
├── videos/                              # 视频录制归档目录
│
├── app.py                               # Web管理平台（Flask），含用例管理、执行记录、版本管理
├── run.py                               # 统一测试执行入口
├── record.py                            # 统一录制功能入口
├── conftest.py                          # Pytest全局fixture与钩子配置
├── rebuild_db.py                        # 数据库表重建脚本
├── scan_case_info.py                    # 用例信息扫描脚本
├── version_manager.py                   # 版本控制命令行工具
├── scheduler.py                         # 定时调度脚本
├── requirements.txt                     # 项目依赖清单
└── README.md                            # 项目说明文档
```

## 数据库配置

框架支持 **SQLite** 和 **MySQL** 两种数据库后端，通过配置文件切换。默认使用 SQLite，无需安装任何数据库软件。

### 配置方式

在 `config/execution_config.yaml` 中配置：

```yaml
database:
  enabled: true
  # 数据库后端: sqlite / mysql
  backend: "sqlite"
  # SQLite 数据库文件路径（相对于项目根目录，仅 backend 为 sqlite 时生效）
  sqlite_path: "data/test_results.db"
  # MySQL 配置（仅 backend 为 mysql 时生效）
  host: "127.0.0.1"
  port: 3306
  user: "root"
  password: "your-password"
  database_name: "uitest"
  charset: "utf8mb4"
  connect_timeout: 30
```

### 两种后端对比

| 特性       | SQLite                            | MySQL                          |
| ---------- | --------------------------------- | ------------------------------ |
| 安装要求   | 无需安装，Python内置              | 需安装MySQL服务                |
| 数据存储   | 本地文件 `data/test_results.db` | 远程数据库服务器               |
| 适用场景   | 单机使用、快速上手                | 团队协作、数据集中管理         |
| 初始化方式 | 自动建表，首次运行即可            | 需先运行 `python db_init.py` |

### 数据库表结构

**test_execution** - 测试执行记录表

| 字段名          | 类型     | 说明                                         |
| --------------- | -------- | -------------------------------------------- |
| id              | INT      | 主键，自增                                   |
| start_time      | DATETIME | 执行开始时间                                 |
| end_time        | DATETIME | 执行结束时间                                 |
| duration        | FLOAT    | 执行时长（秒）                               |
| total_cases     | INT      | 用例总数                                     |
| passed_cases    | INT      | 通过用例数                                   |
| failed_cases    | INT      | 失败用例数                                   |
| status          | VARCHAR  | 执行状态（running/completed/failed/timeout） |
| command         | VARCHAR  | 执行命令                                     |
| project         | VARCHAR  | 项目名                                       |
| module          | VARCHAR  | 模块名                                       |
| case            | VARCHAR  | 用例名                                       |
| version         | VARCHAR  | 测试版本号                                   |
| timeout_minutes | INT      | 超时时间（分钟）                             |

**test_case_result** - 用例执行结果表

| 字段名        | 类型    | 说明                      |
| ------------- | ------- | ------------------------- |
| id            | INT     | 主键，自增                |
| execution_id  | INT     | 关联执行记录ID            |
| case_name     | VARCHAR | 用例名称                  |
| status        | VARCHAR | 执行状态（passed/failed） |
| duration      | FLOAT   | 执行时长（秒）            |
| log           | TEXT    | 执行日志                  |
| error_message | TEXT    | 错误信息                  |

**test_case_info** - 用例信息表

| 字段名     | 类型    | 说明             |
| ---------- | ------- | ---------------- |
| id         | INT     | 主键，自增       |
| case_name  | VARCHAR | 用例名称（唯一） |
| case_scene | VARCHAR | 用例场景描述     |
| ms_id      | VARCHAR | 用例管理系统ID   |
| project    | VARCHAR | 项目名           |
| module     | VARCHAR | 模块名           |

**test_versions** - 版本控制表

| 字段名       | 类型     | 说明                         |
| ------------ | -------- | ---------------------------- |
| id           | INT      | 主键，自增                   |
| version      | VARCHAR  | 版本号                       |
| version_info | VARCHAR  | 版本信息                     |
| backup_time  | DATETIME | 备份时间                     |
| backup_user  | VARCHAR  | 备份人                       |
| is_active    | INT      | 是否有效（1=有效，0=已删除） |

## AI模型配置

在 `config/execution_config.yaml` 中配置大模型参数：

```yaml
model_config:
  API_BASE_URL: "https://ark.cn-beijing.volces.com/api/v3"
  API_KEY: "your-api-key-here"
  MODEL_NAME: "doubao-seed-2-0-lite-260428"
  REQUEST_TIMEOUT: 30
  TEMPERATURE: 0.3
  MAX_TOKENS: 20000
  TOP_P: 0.9
```

### 使用场景

AI模型主要用于 `record.py` 录制脚本时的代码处理：

- **代码格式化**（`-f 1`）：使用大模型优化录制代码的结构和可读性
- **代码分层**（`-f 1 -l 1`）：自动将脚本拆分为Page层、Data层和Test层

## 录制脚本使用教程（record.py）

### 基本用法

```bash
python record.py -p <项目名> -m <模块名> -c <用例名> [选项]
```

### 参数说明

| 参数           | 简写    | 必填 | 默认值     | 说明                                         |
| -------------- | ------- | ---- | ---------- | -------------------------------------------- |
| `--project`  | `-p`  | 是   | -          | 项目名                                       |
| `--module`   | `-m`  | 是   | -          | 模块名                                       |
| `--case`     | `-c`  | 是   | -          | 用例名                                       |
| `--url`      | `-u`  | 否   | 配置文件   | 被测网站地址，不传则从配置文件获取           |
| `--username` | `-U`  | 否   | 配置文件   | 登录用户名，不传则从配置文件获取             |
| `--pwd`      | `-P`  | 否   | 配置文件   | 登录密码，不传则从配置文件获取               |
| `--browser`  | `-b`  | 否   | chromium   | 浏览器类型（chromium/firefox/webkit）        |
| `--output`   | `-o`  | 否   | 项目根目录 | 输出路径                                     |
| `--format`   | `-f`  | 否   | 0          | 是否AI格式化代码（0=否，1=是）               |
| `--layering` | `-l`  | 否   | 0          | 是否AI分层代码（0=否，1=是，仅在-f=1时生效） |
| `--ms_id`    | `-ms` | 否   | 0          | 用例ms的id                                   |

### 录制流程

1. 启动 Playwright Codegen 录制浏览器
2. 用户在浏览器中操作，Playwright 自动录制操作脚本
3. 关闭浏览器后，根据参数决定后续处理：
   - **不格式化**（`-f 0`）：直接保存原始录制代码到 `src/testcase/{项目}/{模块}/test_{用例}.py`
   - **仅格式化**（`-f 1 -l 0`）：AI优化代码后保存到 testcase 目录
   - **格式化+分层**（`-f 1 -l 1`）：AI将代码拆分为三层文件：
     - `src/testcase/{项目}/{模块}/test_{用例}.py` — 测试用例层
     - `src/pages/{项目}/{模块}/page_{用例}.py` — 页面对象层
     - `src/data/{项目}/{模块}/data_{用例}.py` — 数据层

### 示例

```bash
# 基本录制（不使用AI处理）
python record.py -p LX -m work_order -c workorder_new_page

# 录制并指定URL

python record.py -p LD -m material_file -c   -u https://poc02.iclouddemo.supcon.com/lingoWeb
# 录制并使用AI格式化代码
python record.py -p LX -m work_order -c workorder_new_page -f 1

# 录制并使用AI格式化+分层
python record.py -p LX -m work_order -c workorder_new_page -f 1 -l 1

# 录制并指定ms_id
python record.py -p LX -m work_order -c workorder_new_page -f 1 -l 1 -ms 12345
```

## 执行脚本使用教程（run.py）

### 基本用法

```bash
python run.py -p <项目名> [选项]
```

### 参数说明

| 参数              | 简写      | 必填 | 默认值   | 说明                                |
| ----------------- | --------- | ---- | -------- | ----------------------------------- |
| `--project`     | `-p`    | 否   | 配置文件 | 项目名                              |
| `--url`         | `-u`    | 否   | 配置文件 | 项目登录URL，不传则从配置文件获取   |
| `--username`    | `-user` | 否   | 配置文件 | 登录用户名（必须和-pwd一起使用）    |
| `--pwd`         | `-pwd`  | 否   | 配置文件 | 登录密码（必须和-username一起使用） |
| `--module`      | `-m`    | 否   | 全部     | 模块名                              |
| `--case`        | `-c`    | 否   | 全部     | 用例名                              |
| `--browser`     | `-b`    | 否   | 配置文件 | 浏览器类型                          |
| `--headless`    | `-hl`   | 否   | 配置文件 | 无头模式开关（true/false）          |
| `--retry`       | `-r`    | 否   | 配置文件 | 重试次数                            |
| `--parallel`    | `-pl`   | 否   | 配置文件 | 并行数                              |
| `--clean`       | -         | 否   | -        | 执行前清理历史日志/截图/报告        |
| `--report-type` | -         | 否   | allure   | 报告类型（allure/html）             |
| `--email`       | `-e`    | 否   | -        | 执行完成后发送邮件通知              |
| `--wh`          | `-w`    | 否   | 1        | 是否推送webhook（0=不推送，1=推送） |

### 执行流程

1. 初始化配置，处理参数覆盖
2. 如指定 `--clean`，清理过期的日志/截图/报告文件
3. 连接数据库，插入执行记录（状态为 running）
4. 检查并更新历史超时执行记录
5. 按 项目→模块→用例 路径构建Pytest参数
6. 执行测试用例（单线程依次执行）
7. 执行完成后更新数据库记录（completed/failed）
8. 保存每条用例的详细执行结果到数据库
9. 生成测试报告（Allure/HTML）
10. 可选：发送邮件通知、推送Webhook

### 登录信息优先级

- 若 `--username` 和 `--pwd` 同时传入，使用命令行参数
- 否则使用 `config/execution_config.yaml` 中 `project_login` 下的配置

### 示例

```bash
# 执行指定项目的全部用例
python run.py -p LX

# 执行指定模块
python run.py -p LX -m work_order

# 执行指定用例
python run.py -p LD -m material_file -c product-definition02

python run.py -p LD -m production_management -c creat_query_edit_delet_pm

# 使用自定义登录信息
python run.py -p LX -u http://10.30.22.45:8080/ -user admin -pwd Supcon@1304 -m work_order

# 无头模式执行
python run.py -p LX -m work_order -hl true

# 生成HTML报告
python run.py -p LX -m work_order --report-type html

# 执行前清理历史文件
python run.py -p LX -m work_order --clean

# 不推送webhook
python run.py -p LX -m work_order -w 0

# 执行后发送邮件
python run.py -p LX -m work_order -e
```

## Web管理平台（app.py）

基于 Flask 的测试管理Web平台，提供用例管理、执行记录查看、版本管理等功能。

### 启动方式

```bash
python app.py
```

### 访问地址

- 用例列表：http://localhost:5000/cases
- 执行记录：http://localhost:5000/executions
- 测试报告：http://localhost:5000/report/{execution_id}

### 功能说明

#### 用例列表页面（/cases） 

- 展示所有测试用例信息（从 test_case_info 表读取）
- 支持按项目和模块筛选用例
- **更新用例**：点击按钮执行 scan_case_info.py 脚本，刷新用例列表
- **单条执行**：点击执行按钮执行指定用例
- **批量执行**：选择项目和模块后批量执行
- 显示当前测试版本号

#### 执行记录页面（/executions）

- 展示最近50条测试执行记录
- 显示字段：ID、项目、模块、用例、开始/结束时间、用例数、通过/失败数、状态、版本
- **查看报告**：点击查看该次执行的详细报告（含截图和视频）
- **查看日志**：点击查看单条用例的详细日志
- 自动检测并标记超时记录

#### 测试报告页面（/report/）

- 展示单次执行的详细用例结果
- 支持查看失败用例的截图和视频
- 统计通过率、耗时等信息

#### 版本管理页面

- 查看当前版本和所有历史版本
- 创建新版本、切换版本、删除版本

#### 热更新

- 修改 `src/` 目录下的Python文件后，Web平台自动检测变化并重新加载模块，无需重启服务

## 版本控制功能

框架内置版本控制功能，支持对 `src/` 目录进行版本备份、切换和删除。

### 命令行工具（version_manager.py）

```bash
# 查看当前版本
python version_manager.py current

# 查看所有版本列表
python version_manager.py list

# 查看指定版本信息
python version_manager.py info <版本号>

# 备份当前版本
python version_manager.py backup -u <备份人> [-i <版本信息>]

# 创建新版本（自动更新版本号并备份）
python version_manager.py create -v <新版本号> -u <备份人>

# 切换到指定版本（替换src目录内容）
python version_manager.py switch <版本号>

# 删除指定版本
python version_manager.py delete <版本号> -u <删除人>
```

### 版本控制机制

- 备份时将 `src/` 目录复制为 `src_{版本号}/`
- 版本信息保存在数据库的 `test_versions` 表中
- 删除版本时，备份文件夹重命名为 `del_src_{版本号}_{时间戳}_{用户}`，数据库标记为无效
- 切换版本时，先备份当前src，再替换为目标版本内容，失败自动回退

## 内置工具库

### DataGenerator（数据生成器）

基于 Faker 的测试数据生成器，支持生成姓名、地址、手机号、公司名等常见数据，并支持通过AI大模型生成特定格式的数据。

```python
from src.common.data_generator import DataGenerator

gen = DataGenerator()
name = gen.get_name()           # 生成姓名
phone = gen.get_phone()         # 生成手机号
address = gen.get_address()     # 生成地址
```

### Tool（公用方法）

提供常用页面操作方法：

- `check_button_disabled()` — 检查按钮是否禁用/置灰
- `check_button_visible()` — 检查按钮是否可见
- `table_operation()` — 表格操作（查询、翻页等）
- `generate_random_float()` — 生成随机浮点数

### ExcelUtils（Excel工具）

基于 openpyxl 的通用Excel操作类，支持创建工作簿、写入表头/数据、设置样式与列宽、保存、读取等。

### ScreenshotUtils（截图工具）

按 `screenshots/{执行时间戳}/{项目}/{模块}/{用例}/` 结构归档截图，支持全步骤截图和失败截图。

### FileUtils（文件工具）

文件/目录操作工具，支持创建目录、写入文件、清理过期文件等。

### WebhookClient（Webhook推送）

企业微信Webhook推送客户端，测试执行完成后自动推送执行结果（项目、模块、用例场景、状态、耗时等）。

## 初始化与维护脚本

### rebuild_db.py — 数据库表重建

删除旧表并重新创建新表结构，支持SQLite和MySQL双后端。

```bash
python rebuild_db.py
```

> ⚠️ 此操作会清空所有数据，请谨慎使用。

### scan_case_info.py — 用例信息扫描

扫描 `src/testcase/` 目录下所有测试用例文件，提取用例信息（用例名、场景描述、ms_id、项目、模块）并写入数据库。

```bash
python scan_case_info.py
```

扫描规则：

- 从文件路径提取项目、模块和用例名
- 从类级别docstring提取 ms_id（格式：`用例ms的id：12345`）
- 从方法级别docstring提取用例场景描述（第一个非空非标记行）
- 插入前会先清空用例信息表，再全量写入

### scheduler.py — 定时调度脚本

简单的定时执行脚本，可配置执行间隔，用于周期性运行测试任务。

```bash
python scheduler.py
```

## 编码规范

1. **PEP8规范**：所有代码严格遵循Python PEP8编码规范，缩进4空格，行宽不超过120字符
2. **命名规范**：
   - 类名：大驼峰命名法，例如：BasePage、LoginPage
   - 函数/方法/变量：蛇形命名法，例如：click_submit_btn、input_username
   - 常量：全大写蛇形命名法，例如：DEFAULT_TIMEOUT、API_BASE_URL
3. **类型注解**：所有函数、方法的入参、返回值必须添加完整的类型注解
4. **文档注释**：所有类、方法、函数必须添加完整的docstring文档字符串
5. **异常处理**：所有可能出现异常的代码必须添加try-except异常捕获
6. **设计模式**：遵循Page Object设计模式，页面、数据、用例完全解耦

## 测试报告

### Allure报告

```bash
# 生成报告
allure generate reports/allure_report_xxx -o reports/allure_report_xxx_html --clean

# 查看报告
allure serve reports/allure_report_xxx
```

### HTML报告

```bash
python run.py -p LX -m work_order --report-type html
```
