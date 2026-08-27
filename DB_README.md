# 测试结果数据库功能说明

## 概述

本项目提供测试执行结果的数据库存储功能，支持 **SQLite** 和 **MySQL** 两种后端，通过配置文件切换。每次执行测试时会自动记录：
- 每次执行的整体信息（开始时间、结束时间、用例总数、成功数、失败数、版本号等）
- 每条用例的详细信息（用例名称、执行状态、执行时长、日志、错误信息等）
- 用例元信息（用例场景描述、ms_id、所属项目/模块等）
- 版本控制信息（版本号、备份人、备份时间、是否有效等）

## 架构设计

数据库模块采用 **抽象层模式**，通过统一接口屏蔽不同数据库后端的差异：

```
TestResultDB（统一接口层）
    ├── SQLiteDatabaseBackend（SQLite 后端）
    └── MySQLDatabaseBackend（MySQL 后端）
```

- `TestResultDB`：对外统一接口类，根据配置自动选择后端
- `SQLiteDatabaseBackend`：SQLite 实现，使用 Python 内置 `sqlite3` 模块，无需安装依赖
- `MySQLDatabaseBackend`：MySQL 实现，依赖 `pymysql` 库

### 后端选择逻辑

1. 读取配置中 `backend` 字段（`sqlite` / `mysql`）
2. 若为 `sqlite`，解析数据库文件路径（支持相对路径，自动转为项目根目录下的绝对路径）
3. 若为 `mysql`，校验必需配置字段（host、port、user、database_name），缺失则抛出 `DatabaseError`

## 数据库配置

在 `config/execution_config.yaml` 中配置：

```yaml
database:
  # 是否启用数据库保存
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

| 特性 | SQLite | MySQL |
|------|--------|-------|
| 安装要求 | 无需安装，Python 内置 | 需安装 MySQL 服务和 pymysql 库 |
| 数据存储 | 本地文件 `data/test_results.db` | 远程数据库服务器 |
| 初始化方式 | 首次运行自动建表 | 需先运行 `python rebuild_db.py` |
| 适用场景 | 单机使用、快速上手、零依赖部署 | 团队协作、数据集中管理 |
| 并发写入 | WAL 模式支持多读单写 | 支持多用户并发读写 |
| 占位符 | `?` | `%s` |
| 自增主键 | `INTEGER PRIMARY KEY AUTOINCREMENT` | `INT PRIMARY KEY AUTO_INCREMENT` |

## 数据库表结构

### 1. test_execution（执行记录主表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT / INTEGER | 主键，自增 |
| start_time | DATETIME | 执行开始时间 |
| end_time | DATETIME | 执行结束时间 |
| total_cases | INT | 执行用例总数，默认 0 |
| passed_cases | INT | 成功用例数，默认 0 |
| failed_cases | INT | 失败用例数，默认 0 |
| status | VARCHAR(20) | 执行状态：`running` / `completed` / `failed` / `timeout`，默认 running |
| duration | FLOAT | 执行时长（秒） |
| command | VARCHAR(500) | 执行命令 |
| project | VARCHAR(100) | 项目名 |
| module | VARCHAR(100) | 模块名 |
| case | VARCHAR(100) | 用例名 |
| version | VARCHAR(50) | 测试版本号 |
| timeout_minutes | INT | 超时时间（分钟），默认 30 |
| created_at | DATETIME | 记录创建时间，默认当前时间 |
| updated_at | DATETIME | 记录更新时间，默认当前时间 |

### 2. test_case_result（用例执行结果明细表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT / INTEGER | 主键，自增 |
| execution_id | INT | 关联 test_execution.id |
| case_name | VARCHAR(500) | 用例名称 |
| status | VARCHAR(20) | 状态：`passed` / `failed` |
| duration | FLOAT | 单条用例执行时长（秒） |
| log | TEXT | 单条用例的日志输出 |
| error_message | TEXT | 错误信息（失败时记录） |
| created_at | DATETIME | 记录创建时间，默认当前时间 |
| project | VARCHAR(100) | 项目名（非必填） |

**索引**：
- `idx_case_execution_id` — execution_id 字段索引
- `idx_case_status` — status 字段索引
- `idx_case_project` — project 字段索引

### 3. test_case_info（用例信息表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT / INTEGER | 主键，自增 |
| case_name | VARCHAR(100) | 用例名称（唯一约束） |
| case_scene | VARCHAR(500) | 用例场景描述 |
| ms_id | VARCHAR(50) | 用例管理系统 ID |
| project | VARCHAR(100) | 项目名 |
| module | VARCHAR(100) | 模块名 |
| created_at | DATETIME | 记录创建时间，默认当前时间 |
| updated_at | DATETIME | 记录更新时间，默认当前时间 |

**索引**：
- `idx_ci_case_name` — case_name 字段索引
- `idx_ci_project` — project 字段索引
- `idx_ci_module` — module 字段索引

### 4. test_versions（版本控制表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT / INTEGER | 主键，自增 |
| version | VARCHAR(50) | 版本号 |
| version_info | VARCHAR(500) | 版本信息描述 |
| backup_time | DATETIME | 备份时间 |
| backup_user | VARCHAR(100) | 备份人 |
| is_active | INT / TINYINT | 是否有效（1=有效，0=已删除），默认 1 |
| created_at | DATETIME | 记录创建时间，默认当前时间 |
| updated_at | DATETIME | 记录更新时间，默认当前时间 |

**索引**：
- `idx_tv_version` — version 字段索引
- `idx_tv_is_active` — is_active 字段索引

### 表关系

```
test_execution (1) ──── (N) test_case_result
     │                          │
     │ execution_id             │ case_name
     │                          │
     │                   test_case_info
     │
     └── version ──→ test_versions.version

test_case_result (1) ──── (N) fix_failed_case
     │                          │
     │ execution_id             │ execution_id
     │ case_name                │ case_name
```

### 5. fix_failed_case（用例修复任务表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT / INTEGER | 主键，自增，即修复任务ID |
| project | VARCHAR(100) | 项目名称 |
| case_name | VARCHAR(500) | 用例名称 |
| execution_id | INT | 用例执行ID（关联 test_case_result.execution_id） |
| error_analysis | TEXT | 错误分析（AI返回） |
| source_code | TEXT | 用例原始源代码 |
| fixed_code | TEXT | 修复后代码（AI返回） |
| status | VARCHAR(20) | 任务状态：`进行中` / `已完成` / `失败`，默认 进行中 |
| start_time | DATETIME | 任务开始时间 |
| end_time | DATETIME | 任务结束时间 |
| created_at | DATETIME | 记录创建时间，默认当前时间 |

**索引**：
- `idx_ffc_case_name` — case_name 字段索引
- `idx_ffc_status` — status 字段索引

## 快速开始

### 方式一：SQLite（零配置）

1. 在配置文件中设置 `backend: "sqlite"`
2. 直接运行测试，数据库文件和表结构会自动创建

```bash
python run.py -p LX -m work_order
```

### 方式二：MySQL

1. 在配置文件中设置 `backend: "mysql"` 并填写连接信息
2. 初始化数据库

```bash
python db_init.py
```

3. 运行测试

```bash
python run.py -p LX -m work_order
```

## TestResultDB 接口说明

`TestResultDB` 是对外统一接口类，所有方法自动委托给对应的后端实现。

### 执行记录操作

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `insert_execution_start(command, project, module, case, timeout_minutes, version)` | 插入一条执行记录（状态为 running） | 执行记录 ID（int），失败返回 -1 |
| `update_execution_complete(execution_id, total_cases, passed_cases, status)` | 更新执行记录为完成状态 | bool |
| `update_execution_timeout(execution_id)` | 标记执行记录为超时 | bool |
| `check_and_update_timeout_executions()` | 检查并更新所有超时的执行记录 | 更新数量（int） |
| `get_execution_by_id(execution_id)` | 根据 ID 查询执行记录 | Dict 或 None |
| `get_recent_executions(limit)` | 查询最近 N 条执行记录 | List[Dict] |

### 用例结果操作

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `insert_case_result(execution_id, case_name, status, duration, log, error_message, project)` | 插入单条用例结果 | bool |
| `batch_insert_case_results(execution_id, results, project)` | 批量插入用例结果 | 成功数量（int） |
| `get_case_results_by_execution(execution_id)` | 查询某次执行的所有用例结果 | List[Dict] |
| `get_failed_cases(limit)` | 查询最近的失败用例 | List[Dict] |

### 用例信息操作

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `insert_or_update_case_info(case_name, case_scene, ms_id, project, module)` | 插入或更新用例信息 | bool |
| `batch_insert_case_info(case_list)` | 批量插入用例信息 | 成功数量（int） |
| `get_case_info_by_name(case_name)` | 根据名称查询用例信息 | Dict 或 None |
| `get_all_case_info()` | 查询所有用例信息 | List[Dict] |
| `clear_case_info_table()` | 清空用例信息表 | bool |

### 版本控制操作

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `insert_or_update_version(version, backup_user, version_info)` | 插入或更新版本信息 | bool |
| `get_active_version(version)` | 查询指定有效版本 | Dict 或 None |
| `get_all_active_versions()` | 查询所有有效版本 | List[Dict] |
| `mark_version_deleted(version)` | 标记版本为已删除 | bool |

### 统计操作

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `get_statistics()` | 查询整体统计信息 | Dict 或 None |

### 用例修复任务操作

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `insert_fix_task(project, case_name, execution_id, source_code)` | 创建修复任务（状态为进行中） | 任务ID（int），失败返回 -1 |
| `update_fix_task_result(task_id, error_analysis, fixed_code, status)` | AI返回后更新任务结果 | bool |
| `update_fix_task_status(task_id, status)` | 更新任务状态（超时失败时调用） | bool |
| `get_fix_task(task_id)` | 根据任务ID查询修复任务详情 | Dict 或 None |

### 通用操作

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `connect()` | 连接数据库 | bool |
| `close()` | 关闭数据库连接 | - |
| `create_tables()` | 创建所有表（如不存在） | bool |

## 查询测试结果

### SQL 查询示例

以下示例以 SQLite 语法为主，MySQL 用法类似。

#### 查询最近10次执行记录
```sql
SELECT * FROM test_execution ORDER BY id DESC LIMIT 10;
```

#### 查询某次执行的所有用例
```sql
SELECT * FROM test_case_result WHERE execution_id = 1 ORDER BY id;
```

#### 查询所有失败的用例
```sql
SELECT
    e.id AS execution_id,
    e.start_time,
    c.case_name,
    c.error_message
FROM test_execution e
JOIN test_case_result c ON e.id = c.execution_id
WHERE c.status = 'failed'
ORDER BY e.start_time DESC;
```

#### 统计成功率
```sql
SELECT
    COUNT(*) AS total_executions,
    SUM(total_cases) AS total_cases,
    SUM(passed_cases) AS passed_cases,
    SUM(failed_cases) AS failed_cases,
    ROUND(SUM(passed_cases) * 100.0 / SUM(total_cases), 2) AS success_rate
FROM test_execution;
```

#### 查询指定项目的执行记录
```sql
SELECT * FROM test_execution WHERE project = 'LX' ORDER BY id DESC;
```

#### 查询所有有效版本
```sql
SELECT version, version_info, backup_time, backup_user
FROM test_versions
WHERE is_active = 1
ORDER BY updated_at DESC;
```

#### 按用例场景查询用例信息
```sql
SELECT case_name, case_scene, project, module
FROM test_case_info
WHERE project = 'LX' AND module = 'work_order';
```

## 维护脚本

| 脚本 | 说明 | 适用后端 |
|------|------|----------|
| `rebuild_db.py` | 删除旧表并重新创建，会清空所有数据 | SQLite / MySQL |
| `scan_case_info.py` | 扫描用例文件，提取信息写入 test_case_info 表 | SQLite / MySQL |
| `create_fix_failed_case_table.py` | 临时脚本：仅在现有数据库中创建 fix_failed_case 表（不删除旧表） | SQLite / MySQL |

## 注意事项

1. **SQLite 数据库文件**：默认存储在 `data/test_results.db`，该目录会自动创建，建议不要纳入版本控制
2. **MySQL 依赖**：使用 MySQL 后端需安装 `pymysql`（`pip install pymysql`），SQLite 无需额外依赖
3. **日志大小**：单条用例的日志可能较大，建议定期清理历史数据
4. **超时检测**：执行记录默认超时时间为 30 分钟，超过此时间仍为 `running` 状态的记录会被自动标记为 `timeout`
5. **并发安全**：SQLite 使用 WAL 模式支持多读单写；MySQL 支持多用户并发读写
6. **后端切换**：切换后端只需修改配置文件中的 `backend` 字段，无需修改代码。但注意两种后端的数据不互通
7. **版本控制**：删除版本仅在数据库中标记 `is_active = 0`，不会物理删除记录

## 故障排查

### SQLite 连接失败
- 检查 `data/` 目录是否有写入权限
- 确认磁盘空间是否充足
- 查看日志中的错误信息

### MySQL 连接失败
- 检查 MySQL 服务是否启动
- 验证主机、端口、用户名、密码是否正确
- 检查防火墙设置
- 确认 pymysql 已安装（`pip install pymysql`）

### 表不存在
- SQLite：首次运行会自动建表，如仍报错可运行 `python rebuild_db.py`

### 数据写入失败
- 检查用户是否有写入权限
- 查看日志中的错误信息
- 确认表结构是否与当前版本一致（可运行 `python rebuild_db.py` 重建）

## 文件说明

| 文件 | 说明 |
|------|------|
| `src/common/database.py` | 数据库核心模块，包含抽象层、SQLite 后端、MySQL 后端、统一接口类 |
| `run.py` | 测试执行入口，自动保存结果到数据库 |
| `app.py` | Web 管理平台，读取数据库展示用例和执行记录 |
| `rebuild_db.py` | 数据库表重建脚本 |
| `scan_case_info.py` | 用例信息扫描脚本 |
| `db_query.py` | 数据库查询工具 |
| `db_init.py` | MySQL 数据库初始化脚本 |
| `version_manager.py` | 版本控制命令行工具 |
| `config/execution_config.yaml` | 配置文件（数据库配置在此） |
