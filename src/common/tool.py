import re
import random
from decimal import Decimal
from playwright.sync_api import Locator, Page, expect
from src.common.logger import logger
from src.common.data_generator import DataGenerator
# from src.base.sop_materials import SOP_MATERIALS
from datetime import datetime, timedelta
from src.base.base_test import BaseTest


class Tool:
    """工具类，存放公用方法"""

    @staticmethod
    def check_button_disabled(button: Locator, button_name: str = "按钮") -> bool:
        """
        检查按钮是否被禁用（置灰）

        Args:
            button: 按钮定位器
            button_name: 按钮名称，用于日志输出

        Returns:
            bool: 如果按钮被禁用返回True，否则返回False
        """
        try:
            is_disabled = not button.is_enabled()
            if is_disabled:
                logger.info(f"{button_name}已被置灰，无法点击")
            else:
                logger.error(f"{button_name}未被置灰，测试失败")
            return is_disabled
        except Exception as e:
            logger.error(f"检查{button_name}状态时出错: {str(e)}")
            return False

    @staticmethod
    def assert_button_disabled(button: Locator, button_name: str = "按钮") -> None:
        """
        断言按钮是否被禁用（置灰），如果未被禁用则测试失败

        Args:
            button: 按钮定位器
            button_name: 按钮名称，用于日志输出
        """
        is_disabled = Tool.check_button_disabled(button, button_name)
        assert is_disabled, f"{button_name}未被置灰，测试失败"

    @staticmethod
    def select_workorder_types(page: Page, *types):
        """
        选择工单类型

        Args:
            page: 页面实例
            *types: 要选择的工单类型，可以是多个（编辑，审批，生效，废弃）
        """
        try:
            logger.info(f"开始选择工单类型: {types}")
            # 点击重置按钮
            logger.info("点击重置按钮")
            page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="重置").click()
            page.wait_for_load_state("networkidle")

            # 点击清除按钮
            logger.info("点击清除按钮")
            page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator(
                ".ant-select-clear > .anticon > svg").click()

            # 点击选择器
            logger.info("点击工单类型选择器")
            page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator(
                ".ant-select.ant-select-outlined.ant-select-in-form-item.ant-select-status-success > .ant-select-selector").click()

            # 根据参数选择工单类型
            for type_name in types:
                logger.info(f"选择工单类型: {type_name}")
                if type_name == "编辑":
                    try:
                        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("div").filter(
                            has_text=re.compile(r"^编辑$")).nth(1).click()
                    except:
                        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_text("编辑").click()
                elif type_name == "审批":
                    try:
                        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("div").filter(
                            has_text=re.compile(r"^审批$")).nth(1).click()
                    except:
                        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_text("审批").click()
                elif type_name == "生效":
                    try:
                        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("div").filter(
                            has_text=re.compile(r"^生效$")).nth(1).click()
                    except:
                        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_text("生效").click()
                elif type_name == "废弃":
                    try:
                        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("div").filter(
                            has_text=re.compile(r"^废弃$")).nth(1).click()
                    except:
                        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_text("废弃").click()
                else:
                    logger.warning(f"未知的工单类型: {type_name}")

            logger.info("工单类型选择完成")
        except Exception as e:
            logger.error(f"选择工单类型时出错: {str(e)}")
            raise

    # 创建生产订单
    @staticmethod
    def create_production_order(page: Page, plan_quantity: str, message: str = "测试订单"):
        order_no = DataGenerator().get_order_no("SCDD")
        try:
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("button", name="新 增").click()
            # 定位产线输入框及其参照按钮
            production_frame = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
            # 等待新增弹窗完全加载
            page.wait_for_timeout(2000)

            # 输入生产订单号
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("textbox", name="请输入").fill(
                order_no)

            # 点击物料参照按钮
            refer_button = production_frame.locator("button.ant-btn-icon-only").nth(6)
            refer_button.wait_for(state="visible", timeout=20000)
            refer_button.evaluate("el => el.click()")
            logger.info("成功: 物料参照按钮已点击")
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.locator("iframe").content_frame.get_by_role(
                "row").nth(1).get_by_label("", exact=True).check()
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_label("物料参照").get_by_role(
                "button", name="确 定").click()

            # 点击车间/产线参照按钮
            refer_button = production_frame.locator("button.ant-btn-icon-only").nth(5)  # 第二个按钮
            refer_button.wait_for(state="visible", timeout=20000)
            refer_button.evaluate("el => el.click()")
            logger.info("成功: 车间/产线参照按钮已点击")
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.locator("iframe").content_frame.get_by_role(
                "row").nth(1).get_by_label("", exact=True).check()
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_label("车间/产线参照").get_by_role(
                "button", name="确 定").click()

            # 输入计划数量
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("spinbutton",
                                                                                        name="* 计划数量").click()
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("spinbutton",
                                                                                        name="* 计划数量").fill(
                plan_quantity)

            # 输入计划日期
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("textbox",
                                                                                        name="计划结束日期").click()
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("textbox",
                                                                                        name="计划结束日期").fill(
                DataGenerator().get_random_end_date())
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_text("新增生产订单").click()

            # 输入备注
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("textbox", name="备注").click()
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("textbox", name="备注").fill(
                message)

            # 点击确认按钮
            page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("button", name="确 定").click()
            logger.info(f"成功: 生产订单 {order_no} 已创建")
            return order_no
        except Exception as e:
            logger.error(f"创建生产订单时出错: {str(e)}")
            return None

    # 创建生产工单并保存
    @staticmethod
    def create_work_order(page: Page, project_name: str = "LX", order_status: str = "保 存", plan_qty: str = "100",
                          message: str = "测试工单"):
        """
        创建生产工单

        Args:
            page: 页面实例
            project_name: 项目名
            order_status: 工单状态
            plan_qty: 计划产量
            message: 备注信息

        Returns:
            str: 创建的工单号，如果失败则返回None
        """
        workorder_no = DataGenerator().get_order_no("SCGD")
        material_code = Tool.get_random_sop_material(project_name)
        try:
            logger.info(f"开始创建生产工单: {workorder_no}")
            # 点击新增按钮
            with page.expect_popup() as popup_info:
                page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="新 增").click()
            popup_page = popup_info.value
            popup_page.wait_for_load_state("networkidle")

            # 输入工单号
            popup_page.get_by_role("textbox", name="* 工单号").click()
            popup_page.get_by_role("textbox", name="* 工单号").fill(workorder_no)

            # 选择物料
            popup_page.locator("svg").nth(4).click()
            popup_page.get_by_role("textbox", name="物料编码 :").fill(material_code)
            popup_page.get_by_role("button", name="查询").click()
            Tool.select_first_item_in_popup(popup_page)
            popup_page.get_by_role("button", name="确 定").click()

            # 输入计划产量
            popup_page.get_by_role("spinbutton", name="* 计划产量").click()
            popup_page.get_by_role("spinbutton", name="* 计划产量").fill(plan_qty)

            # 选择SOP
            popup_page.locator(
                "div:nth-child(5) > div > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-arrow > div > .anticon.anticon-search > svg").click()
            Tool.select_first_item_in_popup(popup_page)
            popup_page.get_by_role("button", name="确 定").click()

            # 输入备注
            popup_page.get_by_role("textbox", name="备注").click()
            popup_page.get_by_role("textbox", name="备注").fill(message)

            # 点击保存按钮
            popup_page.get_by_role("button", name=order_status).click()
            popup_page.wait_for_load_state("networkidle")
            popup_page.close()

            logger.info(f"成功: 生产工单 {workorder_no} 已创建")
            return workorder_no
        except Exception as e:
            logger.error(f"创建生产工单时出错: {str(e)}")
            return None

    # 判定小数位数，传入一个小数和位数，判定小数的位数与传入的位数是否相同
    @staticmethod
    def check_decimal_places(num, target_places):
        """
        判定小数的小数位数是否与指定位数相同

        Args:
            num: 待检测的数字（int/float/str）
            target_places: 指定的小数位数（int）

        Returns:
            bool: 位数相同返回True，否则返回False
        """
        # 先转换为字符串再转Decimal，避免浮点数精度干扰
        d = Decimal(str(num))
        # 获取小数部分的有效位数（通过exponent判断）
        if d.as_tuple().exponent >= 0:
            actual_places = 0
        else:
            actual_places = -d.as_tuple().exponent
        return actual_places == target_places

    @staticmethod
    def get_split_order_info(page: Page):
        """
        获取拆分单据的基础信息

        Args:
            page: 页面实例

        Returns:
            dict: 包含拆分单据基础信息的字典
        """
        try:
            logger.info("开始获取拆分单据基础信息")
            iframe = page.locator("iframe[name=\"ProductionOrders\"]").content_frame

            # 获取订单号（定位禁用的输入框）
            order_no = iframe.locator("#orderNo[disabled]").get_attribute("value")
            logger.info(f"订单号: {order_no}")

            # 获取产品编码
            product_code = iframe.locator("#product_code").get_attribute("value")
            logger.info(f"产品编码: {product_code}")

            # 获取产品名称
            product_name = iframe.locator("#product_name").get_attribute("value")
            logger.info(f"产品名称: {product_name}")

            # 获取可拆分数量
            remain_split_num = iframe.locator("#remainSplitNum").get_attribute("aria-valuenow")
            logger.info(f"可拆分数量: {remain_split_num}")

            # 获取计划开始时间
            plan_start_time = iframe.locator("#planStartTime").get_attribute("value")
            logger.info(f"计划开始时间: {plan_start_time}")

            # 获取计划结束时间
            plan_end_time = iframe.locator("#planEndTime").get_attribute("value")
            logger.info(f"计划结束时间: {plan_end_time}")

            # 构建返回字典
            split_order_info = {
                "order_no": order_no,
                "product_code": product_code,
                "product_name": product_name,
                "remain_split_num": remain_split_num,
                "plan_start_time": plan_start_time,
                "plan_end_time": plan_end_time
            }

            logger.info("拆分单据基础信息获取完成")
            return split_order_info
        except Exception as e:
            logger.error(f"获取拆分单据基础信息时出错: {str(e)}")
            return {
                "order_no": None,
                "product_code": None,
                "product_name": None,
                "remain_split_num": None,
                "plan_start_time": None,
                "plan_end_time": None
            }

    # 拆分订单数，返回最终订单数量
    @staticmethod
    def split_order_count(total, line_output):
        """
        拆分订单数，返回最终订单数量
        解决 float 报错，支持整数、小数输入
        """
        # 自动转成整数，避免类型报错
        total = int(total)
        line_output = int(line_output)

        if line_output <= 0:
            return 0

        # 向上取整计算订单数
        order_count = (total + line_output - 1) // line_output
        return order_count

    @staticmethod
    def get_random_sop_material(project_name: str):
        """
        根据项目名称随机获取一个有SOP的物料编码

        Args:
            project_name: 项目名称（如 "LX", "LD"）

        Returns:
            str: 随机的物料编码，如果没有找到则返回None
        """
        try:
            logger.info(f"开始获取 {project_name} 项目的随机SOP物料")

            if project_name not in SOP_MATERIALS:
                logger.error(f"项目中不存在: {project_name}，可用项目: {list(SOP_MATERIALS.keys())}")
                return None

            materials = SOP_MATERIALS[project_name].get("materials", [])

            if not materials:
                logger.error(f"{project_name} 项目没有SOP物料")
                return None

            random_material = random.choice(materials)
            logger.info(f"{project_name} 项目随机获取物料编码: {random_material}")
            return random_material

        except Exception as e:
            logger.error(f"获取随机SOP物料时出错: {str(e)}")
            return None

    @staticmethod
    def select_first_item_in_popup(page):
        """
        通用方法：选择弹窗中的第一条数据

        无论弹窗中有多少条数据，都能定位并选择第一条

        Args:
            page: 弹窗页面实例

        Returns:
            bool: 操作是否成功
        """
        try:
            logger.info("开始选择弹窗中的第一条数据")

            # 尝试两种定位方式
            try:
                # 方式1：通过row定位
                row = page.get_by_role("row").first
                checkbox = row.get_by_label("", exact=True)
                if checkbox.is_visible():
                    checkbox.check()
                    logger.info("成功：通过row定位选择第一条数据")
                    return True
            except Exception as e1:
                logger.debug(f"方式1失败: {str(e1)}")

            try:
                # 方式2：直接定位第一个checkbox
                checkbox = page.get_by_label("", exact=True).first
                if checkbox.is_visible():
                    checkbox.check()
                    logger.info("成功：直接定位选择第一条数据")
                    return True
            except Exception as e2:
                logger.debug(f"方式2失败: {str(e2)}")

            # 方式3：通过CSS选择器定位
            try:
                checkbox = page.locator("td.ant-table-selection-column input").first
                if checkbox.is_visible():
                    checkbox.check()
                    logger.info("成功：通过CSS选择器选择第一条数据")
                    return True
            except Exception as e3:
                logger.debug(f"方式3失败: {str(e3)}")

            logger.error("无法定位到弹窗中的第一条数据")
            return False

        except Exception as e:
            logger.error(f"选择弹窗第一条数据时出错: {str(e)}")
            return False

    @staticmethod
    def create_user(page, username="", pwd=""):
        """
        创建新用户

        Args:
            page: 页面实例
            username: 用户名，默认为空
            pwd: 密码，默认为空

        Returns:
            username, pwd 如果成功，否则返回 None, None
        """
        try:
            logger.info("开始创建新用户")
            initial_pwd = "Supcon1304@"

            # 生成随机用户名和密码（如果未提供）
            if not username:
                username = DataGenerator().get_order_no("uitest")
            if not pwd:
                pwd = "Supcon@1304"
            logger.info(f"用户名: {username}, 密码: {pwd}")

            # 打开设计期
            logger.info("打开设计期")
            with page.expect_popup() as page1_info:
                page.get_by_title("进入设计期").first.click()
            page1 = page1_info.value

            # 进入人员管理
            logger.info("进入人员管理")
            page1.get_by_text("企业组织架构").click()
            page1.get_by_text("人员管理").click()

            # 选择测试岗位并新增人员
            logger.info("选择测试岗位并新增人员")
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_text("测试岗位", exact=True).click()
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("button", name="新增").click()

            # 填写基本信息
            logger.info(f"填写基本信息: {username}")
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("textbox", name="* 姓名").click()
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("textbox", name="* 姓名").fill(username)
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("textbox", name="* 编号").click()
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("textbox", name="* 编号").fill(username)

            # 创建用户账号
            logger.info(f"创建用户账号: {username}")
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("checkbox", name="账号 创建用户账号").check()
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("textbox", name="* 用户名").click()
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("textbox", name="* 用户名").fill(username)

            # 选择角色
            logger.info(f"选择角色")
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_text("角色名").click()
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.locator("#roles > .btn-search > .supicon > svg").click()
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.locator(".sup-rc-virtual-tree-item-content > .sup-checkbox-wrapper > .sup-checkbox > .sup-checkbox-inner").first.click()
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("button", name="图标: right").click()
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("button", name="确认").click()

            # 设置初始密码
            logger.info(f"设置初始密码") 
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("textbox", name="* 密码").click()
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("textbox", name="* 密码").fill(initial_pwd)

            # 点击完成
            page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.get_by_role("button", name="完成", exact=True).click()

            # 断言新增成功
            expect(page1.locator("iframe[name=\"supos-tab-framework-1\"]").content_frame.locator("body")).to_contain_text("新增人员成功")

            # 退出登录
            page1.get_by_title("退出").locator("svg").click()
            page1.get_by_role("button", name="确定").click()

            # 登录新用户
            page1.get_by_role("textbox", name="请输入用户名").click()
            page1.get_by_role("textbox", name="请输入用户名").fill(username)
            page1.get_by_role("textbox", name="请输入密码").click()
            page1.get_by_role("textbox", name="请输入密码").fill(initial_pwd)
            page1.get_by_role("button", name="登 录").click()

            # 修改密码
            page1.get_by_role("textbox", name="* 现用密码:").click()
            page1.get_by_role("textbox", name="* 现用密码:").fill(initial_pwd)
            page1.get_by_role("textbox", name="* 新密码:").click()
            page1.get_by_role("textbox", name="* 新密码:").fill(pwd)
            page1.get_by_text("密码修改").click()
            page1.get_by_role("textbox", name="* 确认密码:").click()
            page1.get_by_role("textbox", name="* 确认密码:").fill(pwd)
            page1.get_by_role("button", name="确认").click()
            page1.close()

            logger.info(f"成功创建用户: {username}")
            return username, pwd
            

        except Exception as e:
            logger.error(f"创建用户时出错: {str(e)}")
            # 尝试关闭页面
            try:
                if 'page1' in locals():
                    page1.close()
            except:
                pass
            return None, None

    @staticmethod
    def confirm_production_order(page, order_no):
        """
        确认生产订单

        Args:
            page: 页面实例
            order_no: 订单号

        Returns:
            str: 订单号，如果确认成功；否则返回None
        """
        try:
            logger.info(f"开始确认生产订单: {order_no}")

            # 进入生产管理
            page.get_by_text("生产管理").click()
            page.get_by_text("生产订单").click()

            # 输入订单编码并查询
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="订单编码 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="订单编码 :").fill(order_no)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()

            # 点击确认按钮
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text("确认", exact=True).click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="确 定").click()

            # 断言确认成功
            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("确认成功！")

            logger.info(f"生产订单 {order_no} 确认成功")
            return order_no

        except Exception as e:
            logger.error(f"确认生产订单时出错: {str(e)}")
            return None

    @staticmethod
    def login_out(page):
        """
        退出登录

        Args:
            page: 页面实例

        Returns:
            如果成功，否则返回 None
        """
        try:
            logger.info("开始退出登录")

            page.get_by_title("退出").locator("svg").click()
            page.get_by_role("button", name="确定").click()
            logger.info("成功退出登录")
            return None
        except Exception as e:
            logger.error(f"退出登录时出错: {str(e)}")
            return None

    @staticmethod
    def create_sales_order(page, customer_name, product_code, order_no="", delivery_date="", quantity="100", unit_price="30"):
        """
        创建标准销售订单

        Args:
            page: 页面实例
            order_no: 订单号，默认为空（如果为空则自动生成）
            customer_name: 客户名称
            product_code: 产品编码
            delivery_date: 交付日期，默认为空（如果为空则使用默认日期）
            quantity: 订单数量，默认为"100"
            unit_price: 单价，默认为"30"

        Returns:
            str: 订单号，如果创建成功；否则返回None
        """
        try:
            logger.info("开始创建标准销售订单")

            # 进入销售管理
            page.get_by_text("销售管理").click()
            page.get_by_text("销售订单").click()

            # 新建销售订单
            logger.info("点击新建销售订单按钮")
            with page.expect_popup() as page1_info:
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name=" 新建销售订单").click()
            page1 = page1_info.value

            # 输入销售单号
            if order_no:
                logger.info(f"输入销售单号 {order_no}")
                page1.get_by_role("textbox", name="销售单号").click()
                page1.get_by_role("textbox", name="销售单号").fill(order_no)

            # 选择客户
            logger.info(f"选择客户 {customer_name}")
            page1.locator(".ant-form-item.input_SoHeader_customerName > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .cds_refer > .cds_refer_suffix > .anticon.anticon-search > svg").click()
            page1.locator("iframe").content_frame.get_by_role("textbox", name="客户名称/联系人").click()
            page1.locator("iframe").content_frame.get_by_role("textbox", name="客户名称/联系人").fill(customer_name)
            page1.locator("iframe").content_frame.get_by_role("textbox", name="客户名称/联系人").press("Enter")
            page1.locator("iframe").content_frame.get_by_text(customer_name).click()
            page1.locator("iframe").content_frame.locator("#root").get_by_text(customer_name).click()
            page1.locator("iframe").content_frame.locator("#root").get_by_text(customer_name).click()
            
            # 选择产品
            logger.info(f"选择产品 {product_code}")
            other_product_tab = page1.locator("iframe").content_frame.get_by_role("tab", name="其他产品")
            if other_product_tab.count() > 0:
                other_product_tab.click()
            page1.locator("iframe").content_frame.get_by_role("textbox", name="产品编码 :").click()
            page1.locator("iframe").content_frame.get_by_role("textbox", name="产品编码 :").fill(product_code)
            page1.locator("iframe").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(5000)
            if other_product_tab.count() > 0:
                page1.locator("iframe").content_frame.get_by_role("row", name="1 Increase Value Decrease").get_by_label("", exact=True).check()                 
            else:
                page1.locator("iframe").content_frame.get_by_label("", exact=True).check()
            page1.get_by_role("button", name="选择", exact=True).click()

            # 输入交付日期（如果提供）
            if delivery_date:
                logger.info(f"输入交付日期 {delivery_date}")
                page1.get_by_role("textbox", name="交付日期").click()
                page1.get_by_role("textbox", name="交付日期").fill(delivery_date)

            # 点击销售单新增区域
            page1.get_by_text("销售单新增").click()

            # 输入数量和单价
            logger.info(f"输入数量 {quantity} 和单价 {unit_price}")
            page1.get_by_role("spinbutton", name="请输入").first.click()
            page1.get_by_role("spinbutton", name="请输入").first.fill(quantity)
            page1.get_by_role("spinbutton", name="请输入").nth(1).click()
            page1.get_by_role("spinbutton", name="请输入").nth(1).fill(unit_price)

            # 保存单据
            logger.info("点击保存按钮")
            page1.get_by_role("button", name="保存").click()

            # 获取页面中的单号
            logger.info("获取销售单号")
            order_no = page1.locator("iframe[title=\"1\"]").content_frame.get_by_role("textbox", name="销售单号").get_attribute("value")
            logger.info(f"获取到销售单号: {order_no}")

            # 提交单据
            logger.info("点击提交按钮")
            page1.locator("iframe[title=\"1\"]").content_frame.get_by_role("button", name="提交").click()

            # 断言提交成功
            try:
                # 先尝试获取处理成功的提示信息
                expect(page1.locator("iframe[name=\"frame\"]").content_frame.get_by_role("paragraph")).to_contain_text("处理成功")
                logger.info("获取到处理成功提示")
            except:
                # 如果断言失败（可能页面已关闭），尝试等待页面关闭事件
                logger.info("尝试等待页面自动关闭")


            logger.info(f"成功创建销售订单: {order_no}")
            return order_no

        except Exception as e:
            logger.error(f"创建销售订单时出错: {str(e)}")
            # 尝试关闭页面
            try:
                if 'page1' in locals():
                    page1.close()
            except:
                pass
            return None

    @staticmethod
    def approve_sales_order(page):
        """
        审批标准销售订单

        Args:
            page: 页面实例

        Returns:
            bool: 如果审批成功返回True，否则返回False
        """
        try:
            logger.info("开始审批标准销售订单")

            # 进入待办中心
            page.get_by_title("待办中心").click()

            # 双击销售审批项
            logger.info("双击销售审批项")
            with page.expect_popup() as page1_info:
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("cell").first.dblclick()
            page1 = page1_info.value
            page1.wait_for_timeout(3000)

            # 提交审批
            logger.info("点击提交按钮")
            page1.locator("iframe[title=\"1\"]").content_frame.get_by_role("button", name="提交").click()

            # 等待页面自动关闭（处理成功后弹窗会自动关闭）
            # 使用 wait_for_event 等待页面关闭事件
            try:
                # 先尝试获取处理成功的提示信息
                expect(page1.locator("iframe[name=\"frame\"]").content_frame.get_by_role("paragraph")).to_contain_text("处理成功")
                logger.info("获取到处理成功提示")
                if 'page1' not in locals():
                    logger.info("页面已关闭，无需关闭")
                else:
                    page1.close()
            except:
                # 如果断言失败（可能页面已关闭），尝试等待页面关闭事件
                logger.info("尝试等待页面自动关闭")
                if 'page1' not in locals():
                    logger.info("页面已关闭，无需关闭")
                else:
                    page1.close()

            logger.info("销售订单审批成功")
            return True

        except Exception as e:
            logger.error(f"审批销售订单时出错: {str(e)}")
            # 尝试关闭页面
            try:
                if 'page1' in locals():
                    page1.close()
            except:
                pass
            return False

    @staticmethod
    def query_work_order(page: Page, order_no: str):
        """
        根据订单号查询生产工单号

        Args:
            page: 页面实例
            order_no: 关联订单号

        Returns:
            str: 查询到的工单号，如果查询失败返回None
        """
        try:
            logger.info(f"开始根据订单号查询生产工单: {order_no}")

            # 进入生产工单页面
            page.get_by_text("生产管理").click()
            page.get_by_text("生产工单").click()
            page.wait_for_timeout(3000)

            # 点击查询图标
            logger.info("点击查询图标")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("form").filter(
                has_text="工单编码产品编码产品名称产品规格批号产线请选择产线关联订单号创建人请选择人员创建时间业务员请选择人员查 询重 置"
            ).locator("img").click()

            # 输入关联订单号
            logger.info("输入关联订单号")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="关联订单号 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="关联订单号 :").fill(order_no)

            # 点击查询按钮
            logger.info("点击查询按钮")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(3000)

            # 获取第一行的工单编码
            logger.info("获取第一行的工单编码")
            first_row = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0").first
            work_order_code = first_row.locator(".level-type .table-tip").text_content()

            logger.info(f"获取到的工单编码: {work_order_code}")
            return work_order_code

        except Exception as e:
            logger.error(f"查询生产工单时出错: {str(e)}")
            return None

    @staticmethod
    def merge_work_order(page: Page, work_order_code1: str, work_order_code2: str, batch_no: str, 
    work_order_no: str = "", production_line_code: str = "", remark: str = ""):
        """
        合并生产工单

        Args:
            page: 页面实例
            work_order_code1: 要合并的工单号1
            work_order_code2: 要合并的工单号2
            batch_no: 批号
            work_order_no: 合并后的工单号，默认为空
            production_line_code: 产线编码，默认为空
            remark: 备注，默认为空
        Returns:
            bool: 如果合并成功返回True，否则返回None
        """
        try:
            logger.info(f"开始合并生产工单: {work_order_code1}, {work_order_code2}")

            # 进入生产工单页面
            page.get_by_text("生产管理").click()
            page.get_by_text("生产工单").click()
            page.wait_for_timeout(3000)
            logger.info("开始查询第一个工单")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编码 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编码 :").fill(work_order_code1)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()

            # 点击第一行的更多按钮展开菜单
            logger.info("开始点击第一个工单的更多按钮")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row > .ant-table-cell.ant-table-cell-fix-right > .ant-menu-overflow > .ant-menu-overflow-item-rest").first.click()
            # 等待菜单展开
            page.wait_for_timeout(2000)

            # 点击第一行的合并按钮（使用JavaScript直接点击，避免遮挡问题）
            logger.info("开始点击第一个工单的合并按钮")
            merge_button = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row > .ant-table-cell.ant-table-cell-fix-right > .ant-menu-overflow").first.get_by_text("合并")
            merge_button.evaluate("el => el.click()")
            # 等待合并操作完成
            page.wait_for_timeout(2000)

            # 勾选第二个工单数据
            logger.info("开始勾选第二个工单")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("row").filter(has_text=work_order_code2).get_by_label("", exact=True).check()
            page.wait_for_timeout(2000)

            # 点击下一步
            logger.info("开始点击下一步")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="下一步").click()
            page.wait_for_timeout(3000)

            # 输入合并后的工单号
            if work_order_no:
                logger.info(f"开始输入合并后的工单号: {work_order_no}")
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入，忽略将自动生成").click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入，忽略将自动生成").fill(work_order_no) 

            # 选择产线
            if production_line_code:
                logger.info(f"开始选择产线: {production_line_code}")
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("div:nth-child(6) > .ant-form-item > .ant-row > .ant-col.ant-col-16 > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-arrow > .anticon > svg").click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"productionLine\"]").content_frame.locator("#code").click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"productionLine\"]").content_frame.locator("#code").fill(production_line_code)
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"productionLine\"]").content_frame.get_by_role("button", name="查 询").click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"productionLine\"]").content_frame.get_by_label("", exact=True).check()
                # 点击保存
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="保 存").click()

            # 输入备注（如果提供）

            if not remark:
                remark = f"合并生产工单{work_order_code1}和{work_order_code2}"
            logger.info(f"开始输入备注: {remark}")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="备注 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="备注 :").fill(remark)

            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入批号").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入批号").fill(batch_no)

            # 点击确认
            logger.info("开始点击确认")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="确 认").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="确 定").click()

            # 验证操作成功
            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("操作成功！")
            logger.info(f"成功合并生产工单: {work_order_code1}, {work_order_code2}")
            return True

        except Exception as e:
            logger.error(f"合并生产工单时出错: {str(e)}")
            return None

    @staticmethod
    def get_material_shortage_info(page: Page, work_order_code: str):
        """
        获取物料统计列表中所有缺料的物料信息

        Args:
            page: 页面实例（已进入生产工单页面并点击物料统计按钮后）
            work_order_code: 工单号
        Returns:
            list: 缺料物料列表，每个元素为字典{"material_code": 物料编码, "shortage_qty": 现存量差额}
                  如果获取失败返回None
        """
        try:
            page.get_by_text("生产管理").click()
            page.get_by_text("生产工单").click()
            page.wait_for_timeout(2000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编码 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编码 :").fill(work_order_code)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(2000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("checkbox", name="Select all").check()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="picture 物料统计").click()
            page.wait_for_timeout(2000)
            logger.info("开始获取物料统计缺料信息")

            shortage_list = []
            rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
            row_count = rows.count()

            logger.info(f"物料统计列表共有 {row_count} 条记录")

            for i in range(row_count):
                row = rows.nth(i)

                # 获取物料属性（第4个td），只统计"物料"属性
                material_type = row.locator("td").nth(4).text_content()
                if material_type != "物料":
                    continue

                # 获取状态
                status_locator = row.locator(".shortage_status_bad__tSJoy")
                if status_locator.count() > 0 and status_locator.text_content() == "缺料":
                    # 获取物料编码（第2个td）
                    material_code = row.locator("td").nth(1).text_content()

                    # 获取现存量差额（第9个td，带有shortage_qty_neg类）
                    shortage_qty = row.locator(".shortage_qty_neg__QVt-j").text_content()

                    shortage_list.append({
                        "material_code": material_code,
                        "shortage_qty": shortage_qty.strip("-")
                    })

                    logger.info(f"缺料物料: {material_code}, 现存量差额: {shortage_qty}")

            logger.info(f"共找到 {len(shortage_list)} 种缺料物料")
            return shortage_list

        except Exception as e:
            logger.error(f"获取物料统计缺料信息时出错: {str(e)}")
            return None

    @staticmethod
    def create_purchase_order(page: Page, vendor_code: str, material_list: list, order_no: str = "", delivery_date: str = "", remark: str = "", unit_price: str = "50"):
        """
        创建采购订单

        Args:
            page: 页面实例
            vendor_code: 供应商编码
            material_list: 物料清单，格式为[{'material_code': 'WIP006', 'shortage_qty': '200'}, ...]
            order_no: 采购订单号，非必填（如果为空则自动生成）
            delivery_date: 预计送货日期，非必填
            remark: 备注，非必填
            unit_price: 物料单价，默认为"50"

        Returns:
            str: 创建成功返回订单号，否则返回None
        """
        try:
            logger.info(f"开始创建采购订单，供应商编码: {vendor_code}")

            # 进入采购订单页面
            page.get_by_text("采购管理").click()
            page.get_by_text("采购订单", exact=True).click()

            # 点击新建采购订单按钮
            logger.info("点击新建采购订单按钮")
            with page.expect_popup() as page1_info:
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name=" 新建采购订单").click()
            page1 = page1_info.value

            # 输入采购订单号（如果提供）
            if order_no:
                logger.info(f"输入采购订单号: {order_no}")
                page1.get_by_role("textbox", name="采购订单号").click()
                page1.get_by_role("textbox", name="采购订单号").fill(order_no)

            # 选择供应商
            logger.info(f"选择供应商: {vendor_code}")
            page1.locator(".ant-form-item.input_PoHeader_vendorName > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .cds_refer > .cds_refer_suffix > .anticon.anticon-search > svg").click()
            page1.locator("iframe").content_frame.get_by_role("textbox", name="供应商编码 :").click()
            page1.locator("iframe").content_frame.get_by_role("textbox", name="供应商编码 :").fill(vendor_code)
            page1.locator("iframe").content_frame.get_by_role("button", name="查 询").click()
            page1.locator("iframe").content_frame.get_by_role("radio").check()
            page1.get_by_role("button", name="选择", exact=True).click()

            # 输入预计送货日期（如果提供）
            if delivery_date:
                logger.info(f"输入预计送货日期: {delivery_date}")
                page1.get_by_role("textbox", name="预计送货日期").click()
                page1.get_by_role("textbox", name="预计送货日期").fill(delivery_date)
                page1.get_by_text("新增采购订单").click()

            # 输入备注（如果提供）
            if remark:
                logger.info(f"输入备注: {remark}")
                page1.get_by_role("textbox", name="备注").click()
                page1.get_by_role("textbox", name="备注").fill(remark)

            # 循环添加物料
            logger.info("开始添加物料")
            price_index = 1  # 价格输入框索引，从1开始，每次递增2
            for index, material in enumerate(material_list):
                material_code = material.get("material_code")
                shortage_qty = material.get("shortage_qty", "1")

                logger.info(f"添加物料 {index + 1}: {material_code}, 数量: {shortage_qty}")

                # 点击选择产品按钮
                page1.get_by_role("button", name=" 选择产品").click()

                # 输入产品编码并查询
                logger.info(f"输入产品编码: {material_code}")
                page1.locator("iframe").content_frame.get_by_role("textbox", name="产品编码 :").click()
                page1.locator("iframe").content_frame.get_by_role("textbox", name="产品编码 :").fill(material_code)
                page1.locator("iframe").content_frame.get_by_role("button", name="查 询").click()

                # 输入数量
                logger.info(f"输入数量: {shortage_qty}")
                page1.locator("iframe").content_frame.get_by_role("spinbutton", name="请输入数量").click()
                page1.locator("iframe").content_frame.get_by_role("spinbutton", name="请输入数量").fill(shortage_qty)

                # 点击选择按钮
                page1.get_by_role("button", name="选择", exact=True).click()

                # 设置物料价格
                logger.info(f"设置物料价格: {unit_price}")
                page1.get_by_role("spinbutton", name="请输入").nth(price_index).click()
                page1.get_by_role("spinbutton", name="请输入").nth(price_index).fill(unit_price)

                # 价格索引递增2
                price_index += 2

            # 点击保存按钮
            logger.info("点击保存按钮")
            page1.get_by_role("button", name="保存").click()

            # 获取页面中的订单号
            purchase_order_no = page1.locator("iframe[title=\"1\"]").content_frame.get_by_role("textbox", name="采购订单号").get_attribute("value")
            logger.info(f"获取到采购订单号: {purchase_order_no}")

            # 点击提交按钮
            page1.locator("iframe[title=\"1\"]").content_frame.get_by_role("button", name="提交").click()
            page1.wait_for_timeout(2000)
            page1.close()

            logger.info(f"成功创建采购订单: {purchase_order_no}")
            return purchase_order_no

        except Exception as e:
            logger.error(f"创建采购订单时出错: {str(e)}")
            return None

    @staticmethod
    def purchase_order_inbound(page: Page, purchase_order_no: str, warehouse_code: str = "ylc", goods_allocation_code: str = "hw1"):
        """
        采购订单入库

        Args:
            page: 页面实例
            purchase_order_no: 采购订单号
            warehouse_code: 仓库编码，默认为"ylc"
            goods_allocation_code: 货位编码，默认为"hw1"

        Returns:
            bool: 如果入库成功返回True，否则返回None
        """
        try:
            logger.info(f"开始采购订单入库，仓库编码: {warehouse_code}, 货位编码: {goods_allocation_code}")

            # 进入入库通知单页面
            page.get_by_text("仓库管理").click()
            page.get_by_text("入库管理").click()
            page.get_by_text("通知单").click()

            # 输入上游单据编号查询
            logger.info(f"输入上游单据编号: {purchase_order_no}")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="上游单据编号 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="上游单据编号 :").fill(purchase_order_no)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(2000)

            # 点击收货入库按钮
            logger.info("点击收货入库按钮")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text("收货入库").click()
            page.wait_for_timeout(2000)

            # 选择仓库按钮
            logger.info("点击选择仓库按钮")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-select.ant-select-in-form-item.refer-list-select.css-dev-only-do-not-override-1l6e01l.ant-select-single.ant-select-allow-clear.ant-select-show-arrow.ant-select-show-search > .ant-select-arrow > .anticon > svg").click()
            page.wait_for_timeout(2000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"wareHouse\"]").content_frame.get_by_role("textbox", name="编码 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"wareHouse\"]").content_frame.get_by_role("textbox", name="编码 :").fill(warehouse_code)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"wareHouse\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(2000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"wareHouse\"]").content_frame.get_by_label("", exact=True).check()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="选 择").click()

            # 为每行输入批号并选择货位
            page.wait_for_timeout(2000)
            rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
            row_count = rows.count()
            logger.info(f"找到 {row_count} 行数据")

            for i in range(row_count):
                # 输入批号（第5个td中的input）
                batch_no = DataGenerator.get_order_no(prefix="batch")
                logger.info(f"生成的批号: {batch_no}")
                batch_input = rows.nth(i).locator("td").nth(4).locator("input")
                if batch_input.is_visible():
                    batch_input.click()
                    batch_input.fill(batch_no)
                    logger.info(f"已为第 {i+1} 行输入批号: {batch_no}")

                # 点击选择货位图标（第6个td中的.refer-list图标）
                select_icon = rows.nth(i).locator("td").nth(5).locator(".refer-list .anticon svg")
                if select_icon.is_visible():
                    select_icon.click()
                    logger.info(f"已为第 {i+1} 行点击选择货位图标")

                    # 选择货位
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"goodsAllocation\"]").content_frame.get_by_role("textbox", name="货位编码 :").click()
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"goodsAllocation\"]").content_frame.get_by_role("textbox", name="货位编码 :").fill(goods_allocation_code)
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"goodsAllocation\"]").content_frame.get_by_role("button", name="查 询").click()
                    page.wait_for_timeout(1000)
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"goodsAllocation\"]").content_frame.get_by_label("", exact=True).check()
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="选 择").click()
                    logger.info(f"已为第 {i+1} 行选择货位")
                    page.wait_for_timeout(1000)

            # 提交入库
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="提 交").click()

            # 验证入库成功
            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("入库成功")
            logger.info("采购订单入库成功")
            return True

        except Exception as e:
            logger.error(f"采购订单入库时出错: {str(e)}")
            return None

    @staticmethod
    def start_work_order(page: Page, work_order_code: str):
        """
        开始工单并获取子工单列表

        Args:
            page: 页面实例
            work_order_code: 工单号

        Returns:
            list: 启动成功返回子工单列表（无子工单时返回空列表），失败返回None
        """
        try:
            logger.info(f"开始工单: {work_order_code}")

            # 进入生产工单页面
            page.get_by_text("生产管理").click()
            page.get_by_text("生产工单").click()

            # 查询工单
            logger.info(f"查询工单: {work_order_code}")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编码 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编码 :").fill(work_order_code)
            page.wait_for_timeout(5000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(5000)

            # 定位父工单行
            parent_row = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row-level-0").filter(has_text=work_order_code)

            # 展开父工单行以加载子工单
            expand_icon = parent_row.locator(".ant-table-row-expand-icon-collapsed")
            if expand_icon.count() > 0:
                logger.info("父工单行处于折叠状态，点击展开")
                expand_icon.first.click()
                page.wait_for_timeout(2000)
            else:
                logger.info("父工单行已展开或无展开按钮")

            # 获取所有子工单的工单号
            child_orders = []
            rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row")
            row_count = rows.count()

            for i in range(row_count):
                row = rows.nth(i)
                child_icon = row.locator(".child-icon")
                if child_icon.count() > 0:
                    child_work_order = row.locator(".level-type .table-tip").text_content()
                    child_orders.append(child_work_order)
                    logger.info(f"找到子工单: {child_work_order}")

            logger.info(f"共找到 {len(child_orders)} 个子工单")

            # 在父工单行点击"开始"按钮
            logger.info(f"点击父工单 {work_order_code} 的'开始'按钮")
            parent_row.locator(".ant-menu-overflow").get_by_text("开始").click()

            # 验证操作成功
            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("操作成功！")

            if child_orders:
                logger.info(f"工单 {work_order_code} 启动成功，子工单列表: {child_orders}")
            else:
                logger.info(f"工单 {work_order_code} 启动成功，无子工单")
            return child_orders

        except Exception as e:
            logger.error(f"开始工单时出错: {str(e)}")
            try:
                page.close()
            except:
                pass
            return None

    @staticmethod
    def production_material_allocation(page: Page, work_order_code: str):
        """
        生产配料

        Args:
            page: 页面实例
            work_order_code: 工单号

        Returns:
            str: 如果成功返回通知单编号，否则返回None
        """
        try:
            logger.info(f"开始生产配料，工单号: {work_order_code}")
            page_initial_url = page.url

            # 进入领料单页面
            page.get_by_text("生产管理").click()
            page.get_by_text("投料管理").click()
            page.get_by_text("领料单").click()

            # 查询工单
            logger.info(f"查询工单: {work_order_code}")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编号 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编号 :").fill(work_order_code)
            page.wait_for_timeout(5000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(2000)

            # 获取领料单号并审核
            rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
            row_count = rows.count()
            material_order_no = None
            logger.info(f"领料单列表共有 {row_count} 行数据")

            for i in range(row_count):
                row = rows.nth(i)
                # 检查工单号是否匹配
                order_cell = row.locator("td").nth(2)
                if order_cell.text_content() == work_order_code:
                    # 获取领料单号（第2个td中的a标签）
                    material_order_no = row.locator("td").nth(1).locator("a").text_content()
                    logger.info(f"获取到领料单号: {material_order_no}")

                    # 审核该行工单
                    logger.info(f"审核工单: {work_order_code}")
                    row.get_by_text("审核", exact=True).click()
                    page.wait_for_timeout(5000)
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="审核通过").click()
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="确 认").click()
                    page.wait_for_timeout(2000)
                    break

            if not material_order_no:
                logger.error(f"未找到工单 {work_order_code} 对应的领料单")
                return None

            page.goto(page_initial_url)
            # 进入出库通知单页面
            page.get_by_text("仓库管理").click()
            page.get_by_text("出库管理").click()
            page.get_by_text("通知单").click()

            # 查询通知单（使用领料单号）
            logger.info(f"查询通知单: {material_order_no}")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="上游单据编号 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="上游单据编号 :").fill(material_order_no)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(2000)

            # 获取通知单编号
            rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
            row_count = rows.count()
            notice_order_no = None

            logger.info(f"通知单列表共有 {row_count} 行数据")

            for i in range(row_count):
                row = rows.nth(i)
                # 获取该行所有列的文本内容用于调试
                cells_text = [row.locator("td").nth(j).text_content().strip() for j in range(row.locator("td").count())]
                logger.info(f"第 {i+1} 行数据: {cells_text}")

                # 检查上游单据编号是否匹配（领料单号在td[2]，即第3列）
                upstream_cell = row.locator("td").nth(2)
                if material_order_no in upstream_cell.text_content().strip():
                    # 获取通知单编号（td[1]，即第2列）
                    notice_order_no = row.locator("td").nth(1).text_content().strip()
                    logger.info(f"获取到通知单编号: {notice_order_no}")
                    break

            if not notice_order_no:
                logger.error(f"未找到领料单 {material_order_no} 对应的通知单")
                return None

            # 点击配货出库
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text("配货出库").click()
            page.wait_for_timeout(2000)

            # 点击推荐发货
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="fire 推荐发货").click()
            page.wait_for_timeout(3000)

            # 提交
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="提 交").click()

            # 验证出库成功
            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("创建出库单成功！")

            logger.info(f"生产配料成功，通知单编号: {notice_order_no}")
            return notice_order_no

        except Exception as e:
            logger.error(f"生产配料时出错: {str(e)}")
            return None

    @staticmethod
    def activate_outbound_order(page: Page, notice_order_no: str):
        """
        生效出库单（支持一个通知单对应多个出库单）

        Args:
            page: 页面实例
            notice_order_no: 通知单号

        Returns:
            list: 如果成功返回所有出库单编号列表，否则返回None
        """
        try:
            logger.info(f"开始生效出库单，通知单号: {notice_order_no}")

            # 进入出库单页面
            page.get_by_text("仓库管理").click()
            page.get_by_text("出库管理").click()
            page.get_by_text("出库单").click()

            # 查询通知单
            logger.info(f"查询通知单: {notice_order_no}")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="通知单编号 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="通知单编号 :").fill(notice_order_no)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(2000)

            # 获取所有出库单编号
            rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
            row_count = rows.count()
            outbound_order_nos = []

            for i in range(row_count):
                row = rows.nth(i)
                # 检查通知单编号是否匹配（td[10]）
                notice_cell = row.locator("td").nth(10)
                if notice_order_no in notice_cell.text_content().strip():
                    # 获取出库单编号（td[1]中的a标签）
                    outbound_order_no = row.locator("td").nth(1).locator("a").text_content().strip()
                    outbound_order_nos.append(outbound_order_no)
                    logger.info(f"找到出库单: {outbound_order_no}")

            if not outbound_order_nos:
                logger.error(f"未找到通知单 {notice_order_no} 对应的出库单")
                return None

            logger.info(f"共找到 {len(outbound_order_nos)} 个出库单")

            # 对每个出库单执行出库操作
            success_order_nos = []

            for outbound_order_no in outbound_order_nos:
                try:
                    # 重新查询以获取最新的行定位
                    rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
                    
                    # 找到对应的行并点击出库
                    for j in range(rows.count()):
                        row = rows.nth(j)
                        current_order = row.locator("td").nth(1).locator("a").text_content().strip()
                        if current_order == outbound_order_no:
                            # 点击该行的出库按钮
                            row.locator(".ant-menu-overflow").get_by_text("出库").click()
                            page.wait_for_timeout(1000)

                            # 提交
                            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="提 交").click()

                            # 验证出库成功
                            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("出库成功")
                            page.wait_for_timeout(1000)

                            success_order_nos.append(outbound_order_no)
                            logger.info(f"出库单 {outbound_order_no} 出库成功")

                            # 返回出库单列表页面继续处理下一个
                            page.get_by_text("出库单").click()
                            page.wait_for_timeout(1000)
                            
                            # 重新查询
                            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="通知单编号 :").fill(notice_order_no)
                            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
                            page.wait_for_timeout(2000)
                            
                            break

                except Exception as e:
                    logger.error(f"出库单 {outbound_order_no} 出库失败: {str(e)}")

            logger.info(f"共 {len(outbound_order_nos)} 个出库单，成功 {len(success_order_nos)} 个")
            
            if success_order_nos:
                return success_order_nos
            else:
                return None

        except Exception as e:
            logger.error(f"生效出库单时出错: {str(e)}")
            return None

    @staticmethod
    def production_reporting(page: Page, work_order_code: str, start_time: str="", end_time: str=""):
        """
        生产报工（支持一个工单对应多条任务）

        Args:
            page: 页面实例
            work_order_code: 生产工单号
            start_time: 开始时间，默认为空
            end_time: 结束时间，默认为空

        Returns:
            bool: 如果报工成功返回True，否则返回False
        """
        try:
            logger.info(f"开始生产报工，工单号: {work_order_code}")

            # 进入生产任务页面
            page.get_by_text("生产管理").click()
            page.get_by_text("生产任务").click()

            # 查询工单
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编码 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编码 :").fill(work_order_code)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(2000)

            # 获取所有匹配该工单的行（第一次查询）
            rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
            target_rows = []
            
            for i in range(rows.count()):
                row = rows.nth(i)
                order_code = row.locator("a").first.text_content().strip()
                if order_code == work_order_code:
                    target_rows.append(order_code)
                    logger.info(f"找到匹配的工单行: {order_code}")
            
            if not target_rows:
                logger.error(f"未找到工单 {work_order_code}")
                return False

            total_tasks = len(target_rows)
            logger.info(f"工单 {work_order_code} 共有 {total_tasks} 条任务需要报工")

            # 记录报工成功数量
            success_count = 0
            processed_tasks = []

            # 对每一条任务执行报工操作
            for task_idx in range(total_tasks):
                try:
                    # 每次循环都重新查询，因为页面可能刷新导致排序变化
                    rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
                    target_row = None
                    current_task_code = None
                    
                    # 找到第一个未处理的任务
                    for i in range(rows.count()):
                        row = rows.nth(i)
                        order_code = row.locator("a").first.text_content().strip()
                        if order_code == work_order_code and order_code not in processed_tasks:
                            target_row = row
                            current_task_code = order_code
                            processed_tasks.append(order_code)
                            logger.info(f"开始处理第 {task_idx + 1} 条任务: {current_task_code}")
                            break
                    
                    if not target_row:
                        logger.info(f"第 {task_idx + 1} 条任务已全部处理完毕，跳出循环")
                        break

                    # 点击查看任务
                    target_row.locator(".ant-menu-overflow").get_by_text("查看").click()
                    page.wait_for_timeout(1000)

                    # 获取计划数量
                    plan_qty = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="查看任务").locator("#planQty").input_value()
                    logger.info(f"第 {task_idx + 1} 条任务 - 获取到计划数量: {plan_qty}")

                    # 关闭查看任务弹窗
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="Close").click()
                    page.wait_for_timeout(1000)

                    # 重新获取行定位并点击报工（使用具体的任务编码匹配）
                    rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
                    for i in range(rows.count()):
                        row = rows.nth(i)
                        order_code = row.locator("a").first.text_content().strip()
                        if order_code == current_task_code:
                            row.locator(".ant-menu-overflow").get_by_text("报工").click()
                            logger.info(f"第 {task_idx + 1} 条任务 - 点击报工按钮")
                            break
                    
                    page.wait_for_timeout(1000)

                    # 填写良品数（计划数量）
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("spinbutton", name="* 良品数：").click()
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("spinbutton", name="* 良品数：").fill(plan_qty)

                    # 获取所有物料的领用剩余量并填写实际用量
                    cards = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-col .card")
                    card_count = cards.count()
                    logger.info(f"第 {task_idx + 1} 条任务 - 找到 {card_count} 个物料")

                    for i in range(card_count):
                        card = cards.nth(i)
                        # 获取物料名称
                        material_name = card.locator(".name").text_content()
                        # 获取领用剩余量文本，如"领用剩余量：200千克"
                        remaining_text = card.locator("span").last.text_content()
                        # 提取数字部分
                        import re
                        match = re.search(r'领用剩余量：(\d+)', remaining_text)
                        if match:
                            remaining_qty = match.group(1)
                            # 填写实际用量
                            card.locator(".inp input").click()
                            card.locator(".inp input").fill(remaining_qty)
                            logger.info(f"第 {task_idx + 1} 条任务 - 物料 {material_name} 实际用量填写为: {remaining_qty}")

                    # 填写报工开始时间
                    if start_time == "":
                        start_time = DataGenerator.get_reporting_start_time()
                        logger.info(f"第 {task_idx + 1} 条任务 - 报工开始时间: {start_time}")

                    if end_time == "":
                        end_time = DataGenerator.get_reporting_end_time(start_time)
                        logger.info(f"第 {task_idx + 1} 条任务 - 报工结束时间: {end_time}")

                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="报工开始时间：").click()
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="报工开始时间：").fill(start_time)
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="确 定").click()
                    page.wait_for_timeout(500)

                    # 填写报工结束时间
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="报工结束时间：").click()
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="报工结束时间：").fill(end_time)
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="确 定").click()
                    page.wait_for_timeout(500)

                    # 提交报工
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="提 交").click()

                    # 验证报工成功
                    expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("操作成功！")
                    page.wait_for_timeout(1000)

                    success_count += 1
                    logger.info(f"第 {task_idx + 1} 条任务 - 报工成功")

                    # 刷新列表页面，继续处理下一条
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="工单编码 :").fill(work_order_code)
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
                    page.wait_for_timeout(2000)

                except Exception as e:
                    logger.error(f"第 {task_idx + 1} 条任务报工失败: {str(e)}")

            logger.info(f"工单 {work_order_code} 报工完成，{success_count}/{total_tasks} 条任务成功")
            
            if success_count > 0:
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"生产报工时出错: {str(e)}")
            return False

    @staticmethod
    def production_inbound(page: Page, work_order_code: str, warehouse_code: str = "CK003", goods_allocation_code: str = "HC01"):
        """
        生产入库（精准匹配工单编码）

        Args:
            page: 页面实例
            work_order_code: 工单号
            warehouse_code: 仓库编码，默认为"CK003"
            goods_allocation_code: 货位编码，默认为"HC01"

        Returns:
            bool: 如果入库成功返回True，否则返回False
        """
        try:
            logger.info(f"开始生产入库，工单号: {work_order_code}")

            # 进入入库通知单页面
            page.get_by_text("仓库管理").click()
            page.get_by_text("入库管理").click()
            page.get_by_text("通知单").click()

            # 查询工单
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="上游单据编号 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="上游单据编号 :").fill(work_order_code)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(2000)

            # 精准匹配工单编码所在的行（工单号在第3个td，索引为2）
            rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
            found = False
            
            for i in range(rows.count()):
                row = rows.nth(i)
                # 工单号在第3个td（索引2）
                order_code = row.locator("td").nth(2).text_content().strip()
                if order_code == work_order_code:
                    # 点击该行的收货入库按钮
                    row.locator(".ant-menu-overflow").get_by_text("收货入库").click()
                    logger.info(f"找到匹配的工单 {work_order_code}，点击收货入库")
                    found = True
                    break
            
            if not found:
                logger.error(f"未找到工单 {work_order_code}")
                return False
            
            page.wait_for_timeout(1000)

            # 选择仓库
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-select.ant-select-in-form-item.refer-list-select.css-dev-only-do-not-override-1l6e01l.ant-select-single.ant-select-allow-clear.ant-select-show-arrow.ant-select-show-search > .ant-select-arrow > .anticon > svg").click()
            page.wait_for_timeout(1000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"wareHouse\"]").content_frame.get_by_role("textbox", name="编码 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"wareHouse\"]").content_frame.get_by_role("textbox", name="编码 :").press("CapsLock")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"wareHouse\"]").content_frame.get_by_role("textbox", name="编码 :").fill(warehouse_code)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"wareHouse\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(1000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"wareHouse\"]").content_frame.get_by_label("", exact=True).check()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="选 择").click()
            page.wait_for_timeout(1000)

            # 选择货位
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-cell > div > .refer-list > .anticon > svg").click()
            page.wait_for_timeout(1000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"goodsAllocation\"]").content_frame.get_by_role("textbox", name="货位编码 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"goodsAllocation\"]").content_frame.get_by_role("textbox", name="货位编码 :").fill(goods_allocation_code)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"goodsAllocation\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(1000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("iframe[name=\"goodsAllocation\"]").content_frame.get_by_label("", exact=True).check()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="选 择").click()
            page.wait_for_timeout(1000)

            # 提交
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="提 交").click()

            # 验证入库成功
            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("入库成功")

            logger.info(f"生产入库成功，工单号: {work_order_code}")
            return True

        except Exception as e:
            logger.error(f"生产入库时出错: {str(e)}")
            return False

    @staticmethod
    def sales_outbound(page: Page, order_no: str):
        """
        销售出库

        Args:
            page: 页面实例
            order_no: 销售单号

        Returns:
            bool: 如果出库成功返回True，否则返回False
        """
        try:
            logger.info(f"开始销售出库，销售单号: {order_no}")
            page_url = page.url

            # ==================== 第一步：查询通知单 ====================
            # 进入出库通知单页面
            page.get_by_text("仓库管理").click()
            page.get_by_text("出库管理").click()
            page.get_by_text("通知单").click()

            # 查询销售单号
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="上游单据编号 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="上游单据编号 :").fill(order_no)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(2000)

            # 获取通知单编号
            rows = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-table-row.ant-table-row-level-0")
            row_count = rows.count()
            notice_order_no = None

            logger.info(f"通知单列表共有 {row_count} 行数据")

            for i in range(row_count):
                row = rows.nth(i)
                # 获取该行所有列的文本内容用于调试
                cells_text = [row.locator("td").nth(j).text_content().strip() for j in range(row.locator("td").count())]
                logger.info(f"第 {i+1} 行数据: {cells_text}")

                # 检查上游单据编号是否匹配（销售单号在td[2]，即第3列）
                upstream_cell = row.locator("td").nth(2)
                if order_no in upstream_cell.text_content().strip():
                    # 获取通知单编号（td[1]，即第2列）
                    notice_order_no = row.locator("td").nth(1).text_content().strip()
                    logger.info(f"获取到通知单编号: {notice_order_no}")
                    break

            if not notice_order_no:
                logger.error(f"未找到销售单 {order_no} 对应的通知单")
                return False

            # 点击配货出库
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text("配货出库").click()
            page.wait_for_timeout(1000)

            # 点击推荐发货
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="fire 推荐发货").click()
            page.wait_for_timeout(1000)

            # 提交
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="提 交").click()

            # 验证创建出库单成功
            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("创建出库单成功！")
            logger.info(f"通知单 {notice_order_no} 配货出库成功")
            page.wait_for_timeout(1000)

            # ==================== 第二步：查询出库单并执行出库 ====================
            # 返回首页
            page.goto(page_url)
            page.wait_for_timeout(2000)

            # 进入出库单页面
            page.get_by_text("仓库管理").click()
            page.get_by_text("出库管理").click()
            page.get_by_text("出库单").click()

            # 查询通知单
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="通知单编号 :").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="通知单编号 :").fill(notice_order_no)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="查 询").click()
            page.wait_for_timeout(2000)

            # 点击出库
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text("出库", exact=True).click()
            page.wait_for_timeout(1000)

            # 提交
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="提 交").click()

            # 验证出库成功
            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("出库成功")

            logger.info(f"销售出库成功，销售单号: {order_no}")
            return True

        except Exception as e:
            logger.error(f"销售出库时出错: {str(e)}")
            return False

    @staticmethod
    def create_process(page: Page, process_code: str = "", process_name: str = "", work_rate: str = ""):
        """
        创建工序

        Args:
            page: 页面实例
            process_code: 工序编码，非必填，不传则随机生成
            process_name: 工序名称，非必填，不传则随机生成
            work_rate: 报工数配比，非必填

        Returns:
            str: 如果创建成功返回工序编码，否则返回None
        """
        try:
            code = DataGenerator().get_order_no("process")
            # 生成随机编码和名称（如果未提供）
            if not process_code:
                process_code = f"autoui{code}"
            if not process_name:
                process_name = f"UI自动化{code}"

            logger.info(f"开始创建工序，编码: {process_code}, 名称: {process_name}")

            # 进入工序配置页面
            logger.info("进入工序配置页面")
            page.get_by_text("生产管理").click()
            page.get_by_text("基础设置").click()
            page.get_by_text("工序配置").click()
            page.wait_for_timeout(1000)

            # 点击创建按钮
            logger.info("点击创建按钮")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="plus-circle 创建").click()
            page.wait_for_timeout(500)

            # 填写编码
            logger.info("填写编码")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入，忽略将自动生成").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入，忽略将自动生成").fill(process_code)

            # 填写名称
            logger.info("填写名称")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入工序名称").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入工序名称").fill(process_name)

            # 选择不良品项（第一个选项）
            logger.info("选择不良品项（第一个选项）")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("#substandardList").click()
            page.wait_for_timeout(500)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".ant-select-dropdown .ant-select-item").first.click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text("不良品项列表：").click()
            page.wait_for_timeout(500)

            # 输入报工数配比
            if work_rate:
                logger.info("输入报工数配比")
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="* 报工数配比：").click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="* 报工数配比：").fill(work_rate)

            # 选择自动审核
            logger.info("选择自动审核")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("div:nth-child(2) > .ant-checkbox-wrapper > .ant-checkbox > .ant-checkbox-input").check()

            # 点击保存
            logger.info("点击保存")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="保 存").click()
            page.wait_for_timeout(1000)

            # 验证保存成功
            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("保存成功！")

            logger.info(f"工序创建成功，编码: {process_code}")
            return process_code

        except Exception as e:
            logger.error(f"创建工序时出错: {str(e)}")
            return None

    @staticmethod
    def create_process_route(page: Page, route_code: str = "", route_name: str = "", process_name: str = ""):
        """
        创建工艺路线

        Args:
            page: 页面实例
            route_code: 工艺路线编码，非必填，不传则随机生成
            route_name: 工艺路线名称，非必填，不传则随机生成
            process_name: 绑定工序名称，必填

        Returns:
            str: 如果创建成功返回工艺路线编码，否则返回None
        """
        try:
            if not process_name:
                logger.error("创建工艺路线失败：工序名称为必填参数")
                return None

            code = DataGenerator().get_order_no("route")
            # 生成随机编码和名称（如果未提供）
            if not route_code:
                route_code = f"autoui{code}"
            if not route_name:
                route_name = f"UI自动化{code}"

            logger.info(f"开始创建工艺路线，编码: {route_code}, 名称: {route_name}, 绑定工序: {process_name}")

            page.get_by_text("生产管理").click()
            page.get_by_text("基础设置").click()
            page.get_by_text("工艺配置").click()
            page.wait_for_timeout(1000)

            # 点击创建按钮
            logger.info("点击创建按钮")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="plus-circle 创建").click()
            page.wait_for_timeout(500)

            # 填写编码
            logger.info("填写工艺路线编码")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入，忽略将自动生成").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入，忽略将自动生成").fill(route_code)

            # 填写名称
            logger.info("填写工艺路线名称")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入工艺路线名称").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="请输入工艺路线名称").fill(route_name)

            # 点击新增按钮
            logger.info("点击新增按钮绑定工序")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="plus-circle 新增").click()
            page.wait_for_timeout(500)

            # 点击工序下拉框
            logger.info("点击工序下拉框")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("#rc_select_2").click()
            page.wait_for_timeout(500)

            # 点击工序名称
            logger.info("点击工序名称")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("#rc_select_2").fill(process_name)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text(process_name).click()
            page.wait_for_timeout(500)

            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="保 存").click()
            page.wait_for_timeout(1000)

            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("保存成功！")

            logger.info(f"工艺路线创建成功，编码: {route_code}")
            return route_code

        except Exception as e:
            logger.error(f"创建工艺路线时出错: {str(e)}")
            return None

    @staticmethod
    def create_bom(page: Page, parent_product_code: str, child_items: list, process_name: str) -> bool:
        """
        创建物料清单

        Args:  
            page: 页面实例
            parent_product_code: 父项产品编码，必填
            child_items: 子项产品列表，每个元素为物料编码，必填
            process_name: 绑定工序名称，必填

        Returns:
            bool: 如果创建成功返回True，否则返回False
        """
        try:
            logger.info("开始创建物料清单")

            # 导航到物料清单页面
            logger.info("导航到物料清单页面")
            page.get_by_text("基础资料").click()
            page.get_by_text("物料清单").click()
            page.wait_for_timeout(1000)

            # 点击新增按钮
            logger.info("点击新增按钮")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="plus-circle 新增").click()
            page.wait_for_timeout(1000)

            # 点击搜索按钮选择父项产品
            logger.info("选择父项产品")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(".anticon.anticon-search > svg").click()
            page.wait_for_timeout(500)

            # 输入父项产品编码
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("#code").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("#code").fill(parent_product_code)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_label("产品参照").get_by_role("button", name="查 询").click()
            page.wait_for_timeout(500)

            # 选择第一条记录
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_label("", exact=True).check()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="选 择").click()
            page.wait_for_timeout(500)

            # 循环添加子项产品
            item_count = 0
            for item_code in child_items:
                logger.info(f"添加子项产品: {item_code}")

                # 点击添加子项产品按钮
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="plus-circle 添加子项产品").click()
                page.wait_for_timeout(500)

                # 输入子项产品编码
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="产品编码 :", exact=True).click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="产品编码 :", exact=True).fill(item_code)
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_label("产品参照").get_by_role("button", name="查 询").click()
                page.wait_for_timeout(500)

                # 选择第一条记录
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_label("", exact=True).check()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="选 择").click()
                page.wait_for_timeout(500)

                # 选择工序（根据索引确定选择器）
                # 第一个物料: #rc_select_9, get_by_text().click()
                # 第二个物料: #rc_select_12, get_by_text().nth(2).click()
                select_id = f"#rc_select_{9 + item_count * 3}"
                logger.info(f"选择工序，选择器: {select_id}")
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(select_id).click()
                page.wait_for_timeout(500)

                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator(select_id).fill(process_name)
                page.wait_for_timeout(500)

                if item_count == 0:
                    # 第一个物料直接点击
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text(process_name).click()
                else:
                    nth_count = 1 + item_count
                    page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text(process_name).nth(nth_count).click()
                page.wait_for_timeout(500)

                item_count += 1

            # 点击保存按钮
            logger.info("点击保存按钮")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="保 存").click()
            page.wait_for_timeout(1000)

            # 点击确认按钮
            logger.info("点击确认按钮")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="确 认").click()
            page.wait_for_timeout(1000)

            expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("body")).to_contain_text("保存成功！")

            logger.info("物料清单创建成功")
            return True

        except Exception as e:
            logger.error(f"创建物料清单时出错: {str(e)}")
            return False

    @staticmethod
    def create_material_file(page: Page, material_code: str = "", material_name: str = "", 
    route_name: str = "", specs: str = "", model: str = "", type: str = "物料", remark: str = "", source: str = "自制"):
        """
        创建物料档案

        Args:
            page: 页面实例
            material_code: 物料编码，非必填，不传则随机生成
            material_name: 物料名称，非必填，不传则随机生成 
            route_name: 工艺路线名称
            specs: 规格，非必填
            model: 型号，非必填
            type: 产品属性，必填
            remark: 备注，非必填
            source: 来源，必填

        Returns:
            str: 如果创建成功返回物料编码，否则返回None
        """
        try:
            code = DataGenerator().get_order_no("material")
            # 生成随机编码和名称（如果未提供）
            if not material_code:
                material_code = f"autoui{code}"
            if not material_name:
                material_name = f"UI自动化{code}"

            logger.info(f"开始创建物料，编码: {material_code}, 名称: {material_name}, 工艺路线名称: {route_name}, 规格: {specs}, 型号: {model}, 物料类型: {type}, 备注: {remark}, 来源: {source}")

            page.get_by_text("基础资料").click()
            page.get_by_text("产品档案").click()
            page.wait_for_timeout(1000)
            logger.info("点击新增按钮")
            page.wait_for_timeout(1000)
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="plus-circle 新增").click()
            logger.info(f"填写物料编码: {material_code}")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#code").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#code").fill(material_code)
            logger.info(f"填写物料名称: {material_name}")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#name").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#name").fill(material_name)
            if specs:
                logger.info(f"填写规格: {specs}")
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#spec").click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#spec").fill(specs)
            if model:
                logger.info(f"填写型号: {model}")
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#goodsType").click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#goodsType").fill(model)
            logger.info(f"选择产品属性: {type}")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#type").click()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_title(type, exact=True).click()
            if source != "自制":
                logger.info(f"选择来源: {source}")
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_title("自制").click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_title(source).click()
            if route_name:
                logger.info(f"选择工艺路线: {route_name}")
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#routeId").click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("dialog", name="创建产品").locator("#routeId").fill(route_name)
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text(route_name).click()
            if remark:
                logger.info(f"填写备注: {remark}")
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="备注").click()
                page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("textbox", name="备注").fill(remark)
            logger.info("选择是否批次: 是")
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("#enableBatch").get_by_role("radio", name="是").check()
            page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="保 存").click()

            return material_code

        except Exception as e:
            logger.error(f"创建物料时出错: {str(e)}")
            return None