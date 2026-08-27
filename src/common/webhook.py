import requests
import json
from datetime import datetime
from src.common.config_loader import config_loader
from src.common.module_definition_loader import module_def_loader
from src.common.database import TestResultDB
from src.common.logger import logger


class WebhookClient:
    def __init__(self):
        config = config_loader.get_config()
        self.webhook_config = config.get('webhook', {})
        self.enabled = self.webhook_config.get('enabled', False)
        self.url = self.webhook_config.get('url', '')
        self.case_platform_url = self.webhook_config.get('case_platform_url', '')
    
    def get_case_scene(self, case_name: str) -> str:
        """从数据库获取用例的场景信息
        
        Args:
            case_name: 用例名称
            
        Returns:
            str: 用例场景信息
        """
        try:
            import os
            config = config_loader.get_config()
            db_config = config.get('database', {})
            db_config_dict = {
                'backend': db_config.get('backend', 'mysql'),
                'sqlite_path': db_config.get('sqlite_path', 'data/test_results.db'),
                'host': db_config.get('host', 'localhost'),
                'port': int(db_config.get('port', 3306)),
                'user': db_config.get('user', 'root'),
                'password': db_config.get('password', ''),
                'database_name': db_config.get('database_name', 'test_results_db'),
                'charset': db_config.get('charset', 'utf8mb4')
            }
            
            db = TestResultDB(db_config_dict)
            if db.connect():
                case_info = db.get_case_info_by_name(case_name)
                db.close()
                
                if case_info and case_info.get('case_scene'):
                    return case_info['case_scene']
        except Exception as e:
            logger.warning(f"获取用例场景信息失败: {e}")
        
        return case_name  # 如果找不到场景，返回原用例名称
    
    def send_execution_result(self, project, module, case, status, total_cases, passed_cases, start_time, end_time):
        """发送执行结果到企业微信 webhook
        
        注意：
        - 项目和模块使用配置文件中的中文名
        - 用例名称使用 case_scene 字段
        """
        if not self.enabled or not self.url:
            print("Webhook 未启用或未配置地址")
            return False
        
        try:
            # 获取项目和模块中文名
            project_name_cn = module_def_loader.get_project_name_cn(project)
            module_name_cn = module_def_loader.get_module_name_cn(module)
            
            # 获取用例场景信息作为用例名称
            if case:
                display_case_name = self.get_case_scene(case)
            else:
                display_case_name = '全部'
            
            failed_cases = total_cases - passed_cases
            
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(start_time, datetime) else str(start_time)
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(end_time, datetime) else str(end_time)
            
            if isinstance(start_time, datetime) and isinstance(end_time, datetime):
                duration = end_time - start_time
                duration_str = f"{int(duration.total_seconds())}秒"
            else:
                duration_str = ""
            
            if status == 'completed':
                status_text = "✅ 成功"
                status_color = "info"
            elif status == 'failed':
                status_text = "❌ 失败"
                status_color = "warning"
            elif status == 'timeout':
                status_text = "⏱️ 超时"
                status_color = "warning"
            else:
                status_text = status
                status_color = "comment"
            
            content = f"**自动化测试执行结果**\n\n"
            content += f"> **执行项目:** {project_name_cn or '未指定'}\n"
            content += f"> **执行模块:** {module_name_cn or '全部'}\n"
            content += f"> **场景名称:** {display_case_name or '全部'}\n"
            content += f"> **执行结果:** <font color=\"{status_color}\">{status_text}</font>\n"
            content += f"> **场景总数:** {total_cases}\n"
            content += f"> **成功场景:** {passed_cases}\n"
            content += f"> **失败场景:** {failed_cases}\n"
            content += f"> **开始时间:** {start_time_str}\n"
            content += f"> **结束时间:** {end_time_str}\n"
            content += f"> **执行时长:** {duration_str}\n"
            
            if self.case_platform_url:
                content += f"> **测试结果详情:** [点击查看]({self.case_platform_url})\n"
            
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            
            response = requests.post(
                self.url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print(f"Webhook 推送成功")
                    return True
                else:
                    print(f"Webhook 推送失败，错误码: {result.get('errmsg')}")
                    return False
            else:
                print(f"Webhook 推送失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Webhook 推送异常: {e}")
            import traceback
            logger.error(f"Webhook 推送异常: {traceback.format_exc()}")
            return False
