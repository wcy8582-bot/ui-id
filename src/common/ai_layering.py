import sys
import os
import time
import json
import re

# 添加项目根目录到搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# 导入AI聊天模块
from src.common.ai_chat import ai_chat
from src.common.logger import logger

def clean_code_block(code_text):
    """清理代码块中的```python和```标记
    
    Args:
        code_text: 包含代码块标记的文本
        
    Returns:
        清理后的纯代码文本
    """
    if not code_text:
        return code_text
    
    # 去除开头的```python或```
    code_text = code_text.strip()
    if code_text.startswith('```python'):
        code_text = code_text[len('```python'):].strip()
    elif code_text.startswith('```'):
        code_text = code_text[len('```'):].strip()
    
    # 去除结尾的```
    if code_text.endswith('```'):
        code_text = code_text[:-len('```')].strip()
    
    return code_text

def ai_layering(formatted_code, project_name, module_name, case_name, ms_id):
    """使用AI将格式化后的代码分层为三层结构
    
    Args:
        formatted_code: 格式化后的代码
        project_name: 项目名称
        module_name: 模块名称
        case_name: 用例名称
        ms_id: 用例ms的id
        
    Returns:
        dict: 包含三层代码的字典，格式为：
            {
                'success': True/False,
                'test_case': '测试层代码',
                'page': '页面层代码', 
                'data': '数据层代码',
                'error': '错误信息（如果有）'
            }
    """
    logger.info("=" * 60)
    logger.info("开始AI代码分层...")
    logger.info("=" * 60)
    
    try:
        # 构建提示词
        timestamp = int(time.time())
        
        # 文件命名规则
        test_file_name = f"test_{case_name}.py"
        page_file_name = f"page_{case_name}.py"
        data_file_name = f"data_{case_name}.py"
        
        # 类名规则
        class_name = ''.join(word.capitalize() for word in case_name.split('_'))
        page_class_name = f"{class_name}Page"
        test_class_name = f"Test{class_name}"
        
        prompt = f'''请将以下Playwright测试代码重构为三层架构（Page Object Model模式）：
                ```python
                {formatted_code}
                ```
                
                文件命名规则（必须严格遵守）：
                - 测试层文件名：{test_file_name}
                - 页面层文件名：{page_file_name}
                - 数据层文件名：{data_file_name}
                
                类命名规则（必须严格遵守）：
                - 测试层类名：{test_class_name}
                - 页面层类名：{page_class_name}
                
                导入规则（必须严格遵守）：
                - 测试层导入页面层：from src.pages.{project_name}.{module_name}.{page_file_name.replace('.py', '')} import {page_class_name}
                - 测试层导入数据层：from src.data.{project_name}.{module_name}.{data_file_name.replace('.py', '')} import *
                - 页面层导入数据层：from src.data.{project_name}.{module_name}.{data_file_name.replace('.py', '')} import *
                
                要求：
                1. 将代码拆分为三层：测试层、页面层、数据层
                2. 测试层：继承BaseTest，管理测试数据（URL、账号、工单号等），支持参数化
                3. 页面层：封装页面元素定位和操作方法，隐藏细节，提供简洁接口
                4. 数据层：调用页面层方法，使用数据层数据，组织业务流程，专注于测试场景描述
                5. 严格核心操作逻辑不变
                6. 添加适当的注释和日志记录
                7. 严格按照上述文件命名和导入规则生成代码
                
                一、分层核心规则
                1. 用例层
                结构：测试类继承 BaseTest
                必须包含：
                导入：pytest、Page、logger、BaseTest、页面对象、数据对象。
                公用登录：self.login(page, project_name)。
                异常捕获：try-except 包裹流程，日志记录成败。
                2. 页面层
                结构：集中定义元素定位器。
                职责：封装所有页面交互（点击、输入、导航等），处理 iframe / 弹窗等复杂场景。
                如果一条用例有多个页面，则定义不同的class
                3. 数据层
                结构：以字典 XxxData = {{"key": "value"}} 存储所有测试数据。
                职责：数据与代码完全分离，仅维护测试输入（如编码、分组名称等）。
                测试数据定义：如订单号，数量，日期，备注等需要输入的内容，按钮的名称等不需要专门提取出来
                
                请严格按照以下JSON格式返回结果，不要包含其他文字：
                {{
                    "test_case": "测试层代码（纯代码，不要包含```python标记）",
                    "page": "页面层代码（纯代码，不要包含```python标记）",
                    "data": "数据层代码（纯代码，不要包含```python标记）"
                }}
                
                参考示例：
                
                用例层示例：
                ```python
                    from playwright.sync_api import Page
                    from src.common.logger import logger
                    from src.base.base_test import BaseTest
                    from src.pages.LD.BASE.page_sample SamplePage   #导入页面层
                    from src.data.LD.BASE.data_sample import SampleData   #导入数据层
                    
                    
                    class TestSample(BaseTest):
                        """用例描述"""
                        
                        def test_sample(self, page: Page, project_name: str, ms_id: str):
                            """主方法"""
                            try:
                                # 使用公用登录方法
                                self.login(page, project_name)
                                logger.info("登录成功，开始执行操作...")
                                
                                # 初始化页面对象
                                sample_page = SamplePage(page)
                                
                                # 导航到页面
                                sample_page.navigate_to_sample_page()
                                
                                # 获取 iframe
                                iframe = sample_page.get_iframe()
                                
                                # 点击新增按钮
                                modal = sample_page.click_add_button(iframe)
                    
                                # 填写编码信息
                                sample_page.fill_code(modal, SampleData["code"])
                                
                                # 选择分组
                                sample_page.select_group(iframe, SampleData["group"])
                                
                                # 选择类型
                                sample_page.select_type(iframe, SampleData["sample_type"])
                                
                                # 点击确定按钮
                                sample_page.click_confirm(iframe)
                                
                                logger.info("新增操作执行完成！")
                                
                            except Exception as e:
                                logger.error(f"测试执行失败: ")
                                raise
                ```
                
                页面层示例：
                ```python
                    from playwright.sync_api import Page
                    from src.data.LD.BASE.data_sample import SampleData   #导入数据层
                    from src.common.logger import logger
                    
                    class SamplePage:
                        def __init__(self, page: Page):
                            self.page = page
                            # 元素定位器（集中管理，页面变更只需修改此处）
                            self.sample_management = page.get_by_role("listitem", name="物料管理")
                            self.basic_sample = page.get_by_text("基础物料")
                            
                        def navigate_to_sample_page(self):
                            """导航到页面"""
                            logger.info("导航到页面...")
                            self.sample_management.click()
                            self.basic_sample.click()
                            # 等待页面加载完成
                            self.page.wait_for_load_state('networkidle')
                        
                        def get_iframe(self):
                            """获取 iframe"""
                            iframe = self.page.frame("BasicMaterial")
                            if not iframe:
                                raise Exception("无法找到 BasicMaterial iframe")
                            return iframe
                        
                        def click_add_button(self, iframe):
                            """点击新增按钮"""
                            logger.info("点击新增按钮...")
                            add_button = iframe.get_by_role("button", name="新 增")
                            add_button.click()
                            # 等待弹窗出现
                            modal = iframe.locator("div[role='dialog']", has_text="新增物料")
                            modal.wait_for(state="visible", timeout=10000)
                            return modal
                        
                        def select_group(self, iframe, group_name):
                            """选择分组"""
                            logger.info(f"选择分组: group_name...")
                            combobox = iframe.get_by_role("combobox", name="* 分组")
                            combobox.click()
                            # 等待下拉选项出现
                            self.page.wait_for_load_state('networkidle')
                            # 只选择下拉框中的分组选项（定位到下拉框的选项元素）
                            dropdown_option = iframe.locator(".ant-select-item-option-content", has_text=group_name)
                            dropdown_option.click()
                        
                        def select_type(self, iframe, material_type):
                            """选择物料类型"""
                            logger.info(f"选择物料类型: material_type...")
                            combobox = iframe.get_by_role("combobox", name="* 物料类型")
                            combobox.click()
                            # 等待下拉选项出现
                            self.page.wait_for_load_state('networkidle')
                            # 只选择下拉框中的物料类型选项
                            dropdown_option = iframe.locator(".ant-select-item-option-content", has_text=material_type)
                            dropdown_option.click()
                        
                        def fill_code(self, modal, code):
                            """填写物料编码"""
                            logger.info(f"填写物料编码: code...")
                            code_input = modal.locator("#code")
                            code_input.click()
                            code_input.fill(code)
                        
                        def click_confirm(self, iframe):
                            """点击确定按钮"""
                            logger.info("点击确定按钮...")
                            confirm_button = iframe.get_by_role("button", name="确 定")
                            confirm_button.click()
                            # 等待操作完成
                            self.page.wait_for_load_state('networkidle')
                ```               
                数据层示例：
                ```python
                # 测试数据
                    SampleData = {{
                    "code": code1,
                    "group": "分组1",
                    "type": "产品"
                    }}
                ```
                
                请严格按照JSON格式返回，确保JSON格式正确。返回的代码中不要包含```python或```标记。'''
        
        logger.info(f"构建分层提示词完成，时间戳: {timestamp}")
        logger.info("调用AI进行代码分层...")
        
        # 调用AI处理代码
        messages = [
            {"role": "system", "content": "你是一个专业的自动化测试代码架构师，擅长将测试代码重构为三层架构（Page Object模式）。请严格按照指定的文件命名规则和导入规则生成代码。"},
            {"role": "user", "content": prompt}
        ]
        
        logger.debug(f"发送给AI的消息长度: {len(str(messages))} 字符")
        
        response = ai_chat(messages)
        
        logger.info(f"AI返回原始响应类型: {type(response)}")
        
        # 处理AI返回的结果
        if isinstance(response, dict) and 'choices' in response:
            content = response['choices'][0]['message']['content']
            logger.info("AI分层代码生成成功")
            
            # 提取JSON部分
            start = content.find('{')
            end = content.rfind('}') + 1
            logger.debug(f"JSON起始位置: {start}, 结束位置: {end}")
            
            if start != -1 and end != -1 and end > start:
                json_str = content[start:end]
                logger.debug(f"提取的JSON字符串长度: {len(json_str)}")
                
                try:
                    # 解析JSON
                    layering_result = json.loads(json_str)
                    
                    # 验证返回结果
                    if 'test_case' in layering_result and 'page' in layering_result and 'data' in layering_result:
                        # 清理代码块标记
                        test_case_code = clean_code_block(layering_result['test_case'])
                        page_code = clean_code_block(layering_result['page'])
                        data_code = clean_code_block(layering_result['data'])
                        
                        logger.info("AI分层结果验证通过，代码块标记已清理")
                        logger.info("=" * 60)
                        logger.info("AI代码分层完成")
                        logger.info("=" * 60)
                        
                        return {
                            'success': True,
                            'test_case': test_case_code,
                            'page': page_code,
                            'data': data_code,
                            'error': None
                        }
                    else:
                        logger.error("AI返回的JSON缺少必要字段")
                        return {
                            'success': False,
                            'test_case': None,
                            'page': None,
                            'data': None,
                            'error': 'AI返回的JSON缺少必要字段'
                        }
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {str(e)}")
                    logger.error(f"解析失败的JSON字符串: {json_str}")
                    return {
                        'success': False,
                        'test_case': None,
                        'page': None,
                        'data': None,
                        'error': f'JSON解析失败: {str(e)}'
                    }
            else:
                logger.warning(f"AI返回内容中未找到JSON数据，start={start}, end={end}")
                return {
                    'success': False,
                    'test_case': None,
                    'page': None,
                    'data': None,
                    'error': 'AI返回内容中未找到JSON数据'
                }
        else:
            logger.warning(f"AI返回格式不正确，期望dict包含'choices'，实际类型: {type(response)}")
            logger.warning(f"AI返回内容: {response}")
            return {
                'success': False,
                'test_case': None,
                'page': None,
                'data': None,
                'error': 'AI返回格式不正确'
            }
            
    except Exception as e:
        logger.error(f"AI代码分层失败: {str(e)}")
        logger.error(f"异常类型: {type(e).__name__}")
        logger.error(f"异常详情: {str(e)}")
        return {
            'success': False,
            'test_case': None,
            'page': None,
            'data': None,
            'error': f'AI代码分层失败: {str(e)}'
        }

if __name__ == "__main__":
    # 测试代码
    test_code = '''
import pytest
from playwright.sync_api import Page
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestAddBOM(BaseTest):
    """新增BOM测试类"""
    
    def test_add_bom(self, page: Page, project_name: str):
        """测试新增BOM功能"""
        logger.info("开始执行新增BOM测试")
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入产品BOM页面
        page.get_by_role("listitem", name="产品管理").click()
        page.get_by_text("产品BOM").click()
        
        # 点击新增按钮
        with page.expect_popup() as page1_info:
            page.locator("iframe[name=\\"ProductBOM\\"]").content_frame.get_by_role("button", name="新 增").click()
        page1 = page1_info.value
        
        # 填写BOM编码
        page1.get_by_role("textbox", name="* BOM编码").fill("BOM_26040301")
        
        # 保存
        page1.get_by_role("button", name="保 存").click()
        
        logger.info("新增BOM测试完成")
'''
    
    result = ai_layering(test_code, "LD", "MES", "bom")
    print("分层结果:")
    print(f"成功: {result['success']}")
    if result['success']:
        print(f"测试层代码长度: {len(result['test_case'])}")
        print(f"页面层代码长度: {len(result['page'])}")
        print(f"数据层代码长度: {len(result['data'])}")
        
        # 检查是否包含代码块标记
        if '```python' in result['test_case'] or '```' in result['test_case']:
            print("警告：测试层代码包含代码块标记")
        else:
            print("检查通过：测试层代码不包含代码块标记")
            
        if '```python' in result['page'] or '```' in result['page']:
            print("警告：页面层代码包含代码块标记")
        else:
            print("检查通过：页面层代码不包含代码块标记")
            
        if '```python' in result['data'] or '```' in result['data']:
            print("警告：数据层代码包含代码块标记")
        else:
            print("检查通过：数据层代码不包含代码块标记")
    else:
        print(f"错误信息: {result['error']}")
