import sys
import os
import time
import json

# 添加项目根目录到搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# 导入AI聊天模块
from src.common.ai_chat import ai_chat
from src.common.logger import logger

def format_recorded_code(recorded_code, project_name, module_name, case_name, ms_id):
    """使用AI处理录制的原始代码
    
    Args:
        recorded_code: 录制的原始代码
        project_name: 项目名称
        module_name: 模块名称
        case_name: 用例名称
        ms_id: 用例ms的id
        
    Returns:
        处理后的代码
    """
    logger.info("=" * 60)
    logger.info("开始处理录制代码...")
    logger.info("=" * 60)
    
    try:
        # 构建提示词
        timestamp = int(time.time())
        prompt = f'''请严格参考我给的示例代码对录制脚本进行优化：
        ```python
        录制脚本：
        {recorded_code}
        ```
        要求：
        1. 保持核心操作步骤代码保持完全不变
        2. 去除多余的操作（如重复的点击、按键操作）
        3. 添加适当的注释和日志记录
        4. 将登陆步骤修改为公用登录方法，用示例代码中已经封装好的公用登陆方法不要进行任何更改
        5. 示例代码中import的模块，保持不变
        6. 主方法的参数(self, page: Page, project_name: str)不要变
        7. 该用例的ms的id为{ms_id}，该用例的名称为{case_name}

        请直接返回优化后的代码，不要包含其他解释性文字。
        
        请严格参考以下示例代码：
        ```python
        import re
        import pytest
        from playwright.sync_api import Page, expect
        from src.base.base_test import BaseTest
        from src.common.logger import logger
        
        class TestAddBOM(BaseTest):
            """
            用例名：{case_name}
            用例ms的id：{ms_id}
            """
        
            def test_add_bom(self, page: Page, project_name: str):
                f"""测试新增BOM功能
                用例名：{case_name}
                用例ms的id：{ms_id}
                项目名：{project_name}
                
                Args:
                    page: 页面实例
                    project_name: 项目名称
                """
                logger.info("=" * 60)
                logger.info(f"开始执行{case_name}")
                logger.info(f"用例ms的id：{ms_id}")
                logger.info("=" * 60)
                
                # 使用公用登录方法
                self.login(page, project_name)
                
                # 进入产品BOM页面
                logger.info("进入产品BOM页面")
                page.get_by_role("listitem", name="产品管理").click()
                page.get_by_text("产品BOM").click()
                
                # 点击新增按钮
                logger.info("点击新增按钮")
                with page.expect_popup() as page1_info:
                    page.locator("iframe[name=\"ProductBOM\"]").content_frame.get_by_role("button", name="新 增").click()
                page1 = page1_info.value
            '''
        
        logger.info(f"构建提示词完成，时间戳: {timestamp}")
        logger.info("调用AI处理录制代码...")
        
        # 调用AI处理代码
        messages = [
            {"role": "system", "content": "你是一个专业的自动化测试代码优化专家，擅长优化Playwright录制的测试代码。"},
            {"role": "user", "content": prompt}
        ]
        
        logger.debug(f"发送给AI的消息长度: {len(str(messages))} 字符")
        
        response = ai_chat(messages)
        
        logger.info(f"AI返回原始响应类型: {type(response)}")
        
        # 处理AI返回的结果
        if isinstance(response, dict) and 'choices' in response:
            content = response['choices'][0]['message']['content']
            logger.info("AI处理代码成功")
            
            # 提取代码部分（如果有代码块标记）
            if '```python' in content:
                start = content.find('```python') + len('```python')
                end = content.rfind('```')
                if start < end:
                    processed_code = content[start:end].strip()
                    logger.info("提取代码块成功")
                else:
                    processed_code = content.strip()
                    logger.info("未找到代码块标记，使用整段内容")
            else:
                processed_code = content.strip()
                logger.info("未找到代码块标记，使用整段内容")
            
            logger.info("=" * 60)
            logger.info("代码处理完成")
            logger.info("=" * 60)
            return processed_code
        else:
            logger.warning(f"AI返回格式不正确，期望dict包含'choices'，实际类型: {type(response)}")
            logger.warning(f"AI返回内容: {response}")
            # 返回原始代码作为fallback
            return recorded_code
            
    except Exception as e:
        logger.error(f"AI处理代码失败: {str(e)}")
        logger.error(f"异常类型: {type(e).__name__}")
        logger.error(f"异常详情: {str(e)}")
        # 出错时返回原始代码
        return recorded_code

if __name__ == "__main__":
    # 测试代码
    test_code = '''
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://10.30.22.45:8080/login.html")
    page.get_by_role("textbox", name="请输入用户名").click()
    page.get_by_role("textbox", name="请输入用户名").fill("admin")
    page.get_by_role("textbox", name="请输入密码").click()
    page.get_by_role("textbox", name="请输入密码").fill("Supcon@1304")
    page.get_by_role("button", name="登录").click()
    page.close()
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)'''
    
    result = format_recorded_code(test_code, "LD", "TEST", "1")
    print("处理后的代码:")
    print(result)
