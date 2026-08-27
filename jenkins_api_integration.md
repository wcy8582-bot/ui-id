# Playwright UI自动化测试项目与Jenkins API集成方案

## 一、方案概述

本方案通过在测试服务器上提供一个RESTful API接口，接收测试执行参数并调用run.py脚本执行测试。Jenkins通过Pipeline脚本调用该接口，实现UI自动化测试的远程执行和参数传递。

### 优势
- 接口化调用，参数传递灵活
- 与Jenkins Pipeline无缝集成
- 支持所有run.py的参数
- 执行状态实时反馈

### 架构图

```
Jenkins Server        ─────────── POST请求 ───────────>        Flask API (Server B)
    │                                                                          │
    │                                                                          │
    │                                                                          │
    │                                                                          │
    └─────────────────── 接收响应 ──────────────────────────────────┘
                                    ▲
                                    │
                                    ▼
                               执行run.py脚本
```

## 二、API接口说明

### 1. 执行测试接口

#### 1.1 接口地址
```
POST http://<测试服务器IP>:5000/execute_test
```

#### 1.2 请求参数

接口支持run.py的所有参数，参数以JSON格式传递。

| 参数名 | 类型 | 必选 | 默认值 | 说明 |
|-------|------|------|-------|------|
| project | string | 否 | None | 项目名 |
| url | string | 否 | None | 项目登录URL（不传则从配置文件获取） |
| username | string | 否 | None | 登录用户名（必须和pwd一起传递） |
| pwd | string | 否 | None | 登录密码（必须和username一起传递） |
| module | string | 否 | None | 模块名 |
| case | string | 否 | None | 用例名 |
| browser | string | 否 | None | 浏览器类型 |
| headless | boolean | 否 | None | 无头模式开关 |
| retry | integer | 否 | None | 重试次数 |
| parallel | integer | 否 | None | 并行数 |
| clean | boolean | 否 | false | 执行前清理历史日志/截图/报告 |
| report_type | string | 否 | allure | 报告类型（allure/html） |
| email | boolean | 否 | false | 执行完成后发送邮件通知 |
| wh | integer | 否 | 1 | 是否推送webhook（0=不推送，1=推送） |

#### 1.3 请求示例

使用默认配置：
```json
{
  "project": "LX",
  "module": "work_order",
  "case": "workorder_new_page",
  "browser": "chromium",
  "headless": true,
  "retry": 2,
  "clean": true,
  "report_type": "allure",
  "email": false,
  "wh": 1
}
```

使用自定义登录信息：
```json
{
  "project": "LX",
  "url": "http://10.30.22.45:8080/login.html",
  "username": "admin",
  "pwd": "Supcon@1304",
  "module": "work_order",
  "case": "workorder_new_page",
  "browser": "chromium",
  "headless": true,
  "retry": 2,
  "clean": true,
  "report_type": "allure",
  "email": false,
  "wh": 1
}
```

#### 1.4 响应示例

```json
{
  "success": true,
  "message": "测试执行已启动",
  "command": "python run.py -p LX -m work_order -c workorder_new_page -b chromium --headless --retry 2 --clean --report-type allure --wh 1",
  "execution_id": 1
}
```

#### 1.5 响应示例（数据库连接失败）

```json
{
  "success": true,
  "message": "测试执行已启动",
  "command": "python run.py -p LX -m work_order -c workorder_new_page -b chromium --headless --retry 2 --clean --report-type allure --wh 1",
  "warning": "无法创建执行记录，可能是数据库连接失败"
}
```

### 2. 更新项目接口

#### 2.1 接口地址
```
POST http://<测试服务器IP>:5000/update_project
```

#### 2.2 请求参数

| 参数名 | 类型 | 必选 | 默认值 | 说明 |
|-------|------|------|-------|------|
| branch | string | 否 | main | Git分支名称 |

#### 2.3 请求示例

```json
{
  "branch": "main"
}
```

### 3. 测试状态查询API

#### 3.1 接口地址
```
GET http://<测试服务器IP>:5000/get_execution_status/<execution_id>
```

#### 3.2 请求参数

| 参数名 | 类型 | 必选 | 说明 |
|-------|------|------|------|
| execution_id | integer | 是 | 测试执行ID |

#### 3.3 响应示例

```json
{
  "success": true,
  "execution": {
    "id": 1,
    "start_time": "2026-05-18 10:00:00",
    "end_time": "2026-05-18 10:15:30",
    "duration": 930.5,
    "total_cases": 10,
    "passed_cases": 8,
    "status": "completed",
    "command": "python run.py -p LX -m work_order --headless",
    "project": "LX",
    "module": "work_order",
    "case": null
  }
}
```

### 4. 测试结果获取API

#### 4.1 接口地址
```
GET http://<测试服务器IP>:5000/get_test_results/<execution_id>
```

#### 4.2 请求参数

| 参数名 | 类型 | 必选 | 说明 |
|-------|------|------|------|
| execution_id | integer | 是 | 测试执行ID |

#### 4.3 响应示例

```json
{
  "success": true,
  "execution": {
    "id": 1,
    "start_time": "2026-05-18 10:00:00",
    "end_time": "2026-05-18 10:15:30",
    "duration": 930.5,
    "total_cases": 10,
    "passed_cases": 8,
    "status": "completed",
    "command": "python run.py -p LX -m work_order --headless",
    "project": "LX",
    "module": "work_order",
    "case": null
  },
  "case_results": [
    {
      "id": 1,
      "execution_id": 1,
      "case_name": "workorder_new_page",
      "status": "passed",
      "duration": 30.2,
      "log": "测试执行成功...",
      "error_message": null
    },
    {
      "id": 2,
      "execution_id": 1,
      "case_name": "workorder_approval",
      "status": "failed",
      "duration": 25.8,
      "log": "测试执行失败...",
      "error_message": "元素未找到: #approval-button"
    }
  ],
  "statistics": {
    "total_cases": 10,
    "passed_cases": 8,
    "failed_cases": 2
  }
}
```

### 5. 报告下载API

#### 5.1 接口地址
```
GET http://<测试服务器IP>:5000/download_report/<report_type>/<execution_id>
```

#### 5.2 请求参数

| 参数名 | 类型 | 必选 | 说明 |
|-------|------|------|------|
| report_type | string | 是 | 报告类型（allure/html） |
| execution_id | integer | 是 | 测试执行ID |

#### 5.3 响应

- 如果成功，返回相应类型的报告文件（Allure为zip压缩包，HTML为单个html文件）
- 如果失败，返回JSON格式的错误信息

#### 5.4 响应示例（失败情况）

```json
{
  "success": false,
  "message": "未找到执行ID为 1 的Allure报告"
}
```

### 6. 获取日志API

#### 6.1 接口地址
```
GET http://<测试服务器IP>:5000/get_logs/<execution_id>
```

#### 6.2 请求参数

| 参数名 | 类型 | 必选 | 默认值 | 说明 |
|-------|------|------|-------|------|
| execution_id | integer | 是 | - | 测试执行ID |
| page | integer | 否 | 1 | 分页页码 |
| page_size | integer | 否 | 100 | 每页日志行数 |
| max_length | integer | 否 | 100000 | 最大返回长度（字符数） |

#### 6.3 响应示例

```json
{
  "success": true,
  "execution_id": 1,
  "log_content": "2026-05-18 10:00:00 - INFO - run.py:166 - main - 开始执行测试\n2026-05-18 10:00:01 - INFO - run.py:185 - main - 使用单线程运行测试，避免Playwright Sync API在asyncio循环中的错误\n2026-05-18 10:00:02 - INFO - run.py:216 - main - Pytest执行参数: ['src/testcase/LX/work_order', '-p', 'no:xdist', '--tb=short']\n...",
  "file_path": "e:\\UIProject\\auto_ui\\playwright-ui-automation\\logs\\run_all_20260518_100000.log",
  "file_size": 12345,
  "truncated": false,
  "current_page": 1,
  "page_size": 100,
  "total_pages": 1
}
```

#### 6.4 分页查询示例

```
GET http://<测试服务器IP>:5000/get_logs/1?page=2&page_size=50
```

#### 6.5 限制日志长度示例

```
GET http://<测试服务器IP>:5000/get_logs/1?max_length=5000
```

### 7. 响应格式说明

除报告下载API外，其他API的响应格式均为JSON格式：

| 字段名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 执行是否成功 |
| message | string | 执行结果消息（失败时返回） |
| command | string | 实际执行的命令（仅执行类接口返回） |
| execution_id | integer | 测试执行ID（执行测试接口和查询接口返回） |
| execution | object | 执行信息（查询类接口返回） |
| case_results | array | 用例结果列表（测试结果接口返回） |
| statistics | object | 统计信息（测试结果接口返回） |
| log_content | string | 日志内容（获取日志接口返回） |
| file_path | string | 日志文件路径（获取日志接口返回） |
| file_size | integer | 日志文件大小（字节，获取日志接口返回） |
| truncated | boolean | 日志是否被截断（获取日志接口返回） |
| current_page | integer | 当前页码（获取日志接口返回） |
| page_size | integer | 每页日志行数（获取日志接口返回） |
| total_pages | integer | 总页数（获取日志接口返回） |
| warning | string | 警告信息（仅当有警告时返回） |
```

## 三、Jenkins Pipeline配置

### 1. Pipeline脚本示例

```groovy
pipeline {
    agent any
    
    parameters {
        // 定义参数
        string(name: 'PROJECT', defaultValue: 'LX', description: '项目名')
        string(name: 'MODULE', defaultValue: 'work_order', description: '模块名')
        string(name: 'CASE', defaultValue: '', description: '用例名（可选）')
        string(name: 'BROWSER', defaultValue: 'chromium', description: '浏览器类型')
        booleanParam(name: 'HEADLESS', defaultValue: true, description: '无头模式')
        booleanParam(name: 'CLEAN', defaultValue: true, description: '清理历史文件')
        choice(name: 'REPORT_TYPE', choices: ['allure', 'html'], description: '报告类型')
        booleanParam(name: 'EMAIL', defaultValue: false, description: '发送邮件')
        choice(name: 'WH', choices: ['0', '1'], description: '推送webhook')
        booleanParam(name: 'UPDATE_PROJECT', defaultValue: true, description: '是否更新项目代码')
        string(name: 'GIT_BRANCH', defaultValue: 'main', description: 'Git分支名称')
    }
    
    stages {
        stage('Update Project') {
            when {
                expression { params.UPDATE_PROJECT }
            }
            steps {
                script {
                    // 构建请求参数
                    def updateParams = [
                        branch: params.GIT_BRANCH
                    ]
                    
                    // 发送POST请求到API
                    def response = httpRequest(
                        url: 'http://<测试服务器IP>:5000/update_project',
                        httpMode: 'POST',
                        contentType: 'APPLICATION_JSON',
                        requestBody: groovy.json.JsonOutput.toJson(updateParams),
                        timeout: 300 // 5分钟超时
                    )
                    
                    // 解析响应
                    def responseJson = groovy.json.JsonSlurper().parseText(response.content)
                    
                    // 输出结果
                    echo "API响应: ${responseJson}"
                    
                    // 检查执行是否成功
                    if (!responseJson.success) {
                        error "项目更新失败: ${responseJson.message}"
                    }
                    
                    echo "项目更新命令已执行: ${responseJson.command}"
                    
                    // 等待更新完成（根据实际情况调整等待时间）
                    sleep(time: 30, unit: 'SECONDS')
                }
            }
        }
        
        stage('Execute UI Test') {
            steps {
                script {
                    // 构建请求参数
                    def testParams = [
                        project: params.PROJECT,
                        module: params.MODULE,
                        browser: params.BROWSER,
                        headless: params.HEADLESS,
                        clean: params.CLEAN,
                        report_type: params.REPORT_TYPE,
                        email: params.EMAIL,
                        wh: Integer.parseInt(params.WH)
                    ]
                    
                    // 如果指定了用例名，添加到参数中
                    if (params.CASE) {
                        testParams.case = params.CASE
                    }
                    
                    // 发送POST请求到API
                    def response = httpRequest(
                        url: 'http://<测试服务器IP>:5000/execute_test',
                        httpMode: 'POST',
                        contentType: 'APPLICATION_JSON',
                        requestBody: groovy.json.JsonOutput.toJson(testParams),
                        timeout: 600 // 10分钟超时
                    )
                    
                    // 解析响应
                    def responseJson = groovy.json.JsonSlurper().parseText(response.content)
                    
                    // 输出结果
                    echo "API响应: ${responseJson}"
                    
                    // 检查执行是否成功
                    if (!responseJson.success) {
                        error "测试执行失败: ${responseJson.message}"
                    }
                    
                    echo "测试命令已执行: ${responseJson.command}"
                }
            }
        }
        
        stage('Monitor Test Status') {
            steps {
                script {
                    // 这里可以添加监控测试状态的逻辑
                    // 例如，定期查询数据库中的执行状态
                    echo "测试已启动，正在执行中..."
                    // 可以根据实际情况添加等待时间或轮询逻辑
                    sleep(time: 30, unit: 'SECONDS')
                }
            }
        }
        
        stage('Get Test Results') {
            steps {
                script {
                    // 这里可以添加获取测试结果的逻辑
                    // 例如，通过API获取执行记录或报告
                    echo "测试执行中，请在测试服务器查看详细结果"
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline执行完成"
        }
    }
}
```

### 2. 安装必要插件

在Jenkins的插件管理中安装以下插件：
- HTTP Request Plugin：用于发送HTTP请求
- Pipeline Utility Steps Plugin：用于处理JSON数据

### 3. 配置Pipeline参数

在Jenkins Pipeline配置中，勾选「This project is parameterized」，然后添加以下参数：
- PROJECT：字符串参数，默认值为「LX」
- MODULE：字符串参数，默认值为「work_order」
- CASE：字符串参数，默认值为空（可选）
- BROWSER：字符串参数，默认值为「chromium」
- HEADLESS：布尔参数，默认值为「true」
- CLEAN：布尔参数，默认值为「true」
- REPORT_TYPE：选择参数，选项为「allure」和「html」
- EMAIL：布尔参数，默认值为「false」
- WH：选择参数，选项为「0」和「1」
- UPDATE_PROJECT：布尔参数，默认值为「true」
- GIT_BRANCH：字符串参数，默认值为「main」


```
### 2. Jenkins Pipeline执行

1. 在Jenkins控制台选择创建的Pipeline项目
2. 点击「Build with Parameters」
3. 根据需要修改参数值
4. 点击「Build」开始执行

## 六、常见问题与解决方案

### 1. API连接失败
- 检查测试服务器的网络连接
- 检查Flask API是否正在运行
- 检查防火墙设置，确保5000端口开放

### 2. 参数传递错误
- 检查参数名称是否正确
- 检查参数类型是否符合要求
- 检查JSON格式是否正确

### 3. 测试执行失败
- 检查测试服务器上的Python环境和依赖
- 检查Playwright浏览器是否正确安装
- 查看API日志，了解详细错误信息

### 4. Jenkins Pipeline错误
- 检查HTTP Request Plugin是否正确安装
- 检查Pipeline脚本中的API地址是否正确
- 检查参数类型转换是否正确

## 七、优化建议

### 1. 安全性优化
- 添加API认证机制（如API Key）
- 使用HTTPS协议加密传输
- 限制API访问IP

### 2. 功能优化
- 添加测试状态查询API
- 添加测试结果获取API
- 添加报告下载API

### 3. 性能优化
- 使用异步处理提高API并发能力
- 优化测试执行逻辑，减少资源消耗
- 添加测试队列，避免并发执行过多测试

## 八、总结

本方案通过提供RESTful API接口，实现了UI自动化测试项目与Jenkins CI/CD流程的无缝集成。该方案具有参数传递灵活、与Jenkins Pipeline兼容性好、支持所有run.py参数等优点，适合需要灵活控制测试执行的场景。

进一步扩展后，可以实现以下高级功能：
- **测试状态查询API**：实时查询测试执行状态，便于Jenkins Pipeline监控测试进度
- **测试结果获取API**：获取测试执行结果和统计信息，用于自动化报告生成
- **报告下载API**：支持直接下载Allure或HTML测试报告，方便结果查看和分享
- **异步处理机制**：提高API并发处理能力，支持同时执行多个测试任务
- **测试队列功能**：智能管理测试任务队列，避免资源过载，优化执行效率

通过合理配置和优化这些功能，可以进一步提高API的安全性、功能完整性和性能，为UI自动化测试的持续集成提供更好的支持。

---

**作者**：AI Assistant
**日期**：2026-05-18