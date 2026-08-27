from faker import Faker
import random
from typing import Optional, List
from datetime import datetime, timedelta
import json
import time
import string
from src.common.ai_chat import ai_chat
from src.common.logger import logger


class DataGenerator:
    """数据生成工具类"""
    
    def __init__(self, locale: str = "zh_CN"):
        """初始化数据生成器
        
        Args:
            locale: 地区设置，默认为中文
        """
        self.faker = Faker(locale)
    
    def get_name(self) -> str:
        """生成姓名
        
        Returns:
            姓名
        """
        return self.faker.name()
    
    def get_phone_number(self) -> str:
        """生成手机号
        
        Returns:
            手机号
        """
        return self.faker.phone_number()
    
    def get_id_card(self) -> str:
        """生成身份证号
        
        Returns:
            身份证号
        """
        return self.faker.ssn()
    
    def get_email(self) -> str:
        """生成邮箱
        
        Returns:
            邮箱
        """
        return self.faker.email()
    
    def get_address(self) -> str:
        """生成地址
        
        Returns:
            地址
        """
        return self.faker.address()
    
    def get_random_number(self, min_value: int = 0, max_value: int = 100) -> int:
        """生成随机数字
        
        Args:
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            随机数字
        """
        return random.randint(min_value, max_value)
    
    def get_random_string(self, length: int = 10) -> str:
        """生成随机字符串
        
        Args:
            length: 字符串长度
            
        Returns:
            随机字符串
        """
        
        return self.faker.pystr(min_chars=length, max_chars=length)
    
    def get_datetime(self, pattern: str = "%Y-%m-%d %H:%M:%S") -> str:
        """生成日期时间
        
        Args:
            pattern: 日期时间格式
            
        Returns:
            日期时间字符串
        """
        return self.faker.datetime().strftime(pattern)
    
    def get_date(self, pattern: str = "%Y-%m-%d") -> str:
        """生成日期
        
        Args:
            pattern: 日期格式
            
        Returns:
            日期字符串
        """
        return self.faker.date().strftime(pattern)
    
    def get_time(self, pattern: str = "%H:%M:%S") -> str:
        """生成时间
        
        Args:
            pattern: 时间格式
            
        Returns:
            时间字符串
        """
        return self.faker.time().strftime(pattern)
    
    def get_random_choice(self, choices: List) -> any:
        """从列表中随机选择一个元素
        
        Args:
            choices: 选项列表
            
        Returns:
            随机选择的元素
        """
        return random.choice(choices)
    
    def get_password(self, length: int = 12) -> str:
        """生成密码
        
        Args:
            length: 密码长度
            
        Returns:
            密码
        """
        return self.faker.password(length=length)
    
    def get_company(self) -> str:
        """生成公司名称
        
        Returns:
            公司名称
        """
        return self.faker.company()
    
    def get_job(self) -> str:
        """生成职位
        
        Returns:
            职位
        """
        return self.faker.job()
    
    @staticmethod
    def get_order_no(prefix: str = "SCGD") -> str:
        """生成唯一的单号
        
        Args:
            prefix: 单号前缀
            
        Returns:
            唯一的单号
        """
        import time
        timestamp = time.strftime("%Y%m%d")
        random_num = random.randint(100, 999)
        return f"{prefix}{timestamp}{random_num:03d}"

    def generate_random_decimal(integer_digits: int, decimal_digits: int) -> float:
        """
        随机生成一个小数
        :param integer_digits: 整数部分的位数（必须 >= 1）
        :param decimal_digits: 小数部分的位数（必须 >= 0）
        :return: 符合位数要求的随机浮点数，例如 12567.365
        """
        # 生成整数部分：第一位不能为0
        if integer_digits < 1:
            raise ValueError("整数位数必须大于等于1")
        
        # 第一位：1-9
        first = random.randint(1, 9)
        # 剩余位数：0-9
        rest = [random.randint(0, 9) for _ in range(integer_digits - 1)]
        integer_part = int(str(first) + ''.join(map(str, rest)))

        # 生成小数部分
        if decimal_digits <= 0:
            decimal_part = 0
        else:
            decimal_num = random.randint(0, 10**decimal_digits - 1)
            decimal_part = decimal_num / (10**decimal_digits)

        # 合并成最终小数
        result = integer_part + decimal_part
        return result


    # 随机生成一个比开始日期大的结束日期
    @staticmethod
    def get_random_end_date(start_date: str = None) -> str:
        """
        随机生成一个比开始日期大的结束日期
        :param start_date: 开始日期，格式 'YYYY-MM-DD'，默认今天
        :return: 随机结束日期，格式与输入一致
        """
        # 如果没传开始日期，默认用今天
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")
        
        # 把字符串转成日期对象
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        
        # 随机加 1~30 天（可自己改范围）
        random_days = random.randint(1, 30)
        end_dt = start_dt + timedelta(days=random_days)
        
        # 转回字符串返回
        return end_dt.strftime("%Y-%m-%d")

    # 传入开始日期，随机生成一个比它小的开始日期
    @staticmethod
    def get_random_start_date(start_date: str) -> str:
        """
        传入开始日期，随机生成一个比它小的开始日期
        :param start_date: 开始日期，格式 'YYYY-MM-DD'
        :return: 随机开始日期，格式与输入一致
        """
        # 把字符串转成日期对象
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        
        # 随机往前推 1~30 天（可自己调整范围）
        random_days = random.randint(1, 30)
        start_dt = start_dt - timedelta(days=random_days)  
        
        # 转回字符串返回
        return start_dt.strftime("%Y-%m-%d")

    @staticmethod
    def get_reporting_start_time(days_offset: int = 0, hour: int = None) -> str:
        """
        生成报工开始时间，格式为 'YYYY-MM-DD HH:MM'
        
        Args:
            days_offset: 日期偏移量，0为今天，1为明天，-1为昨天，默认为0
            hour: 指定小时数（0-23），如果为None则使用当前小时
        
        Returns:
            报工开始时间字符串，格式 'YYYY-MM-DD HH:MM'
        """
        # 获取基准时间（当前时间 + 日期偏移）
        base_time = datetime.now() + timedelta(days=days_offset)
        
        # 如果指定了小时，使用指定小时，否则使用当前小时
        target_hour = hour if hour is not None else base_time.hour
        
        # 构建目标时间
        target_time = base_time.replace(hour=target_hour, minute=base_time.minute, second=0, microsecond=0)
        
        # 格式化输出
        return target_time.strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def get_reporting_end_time(start_time: str, hours_offset: int = 24) -> str:
        """
        根据报工开始时间生成报工结束时间
        
        Args:
            start_time: 报工开始时间，格式 'YYYY-MM-DD HH:MM'
            hours_offset: 结束时间相对于开始时间的小时偏移量，默认为24小时
        
        Returns:
            报工结束时间字符串，格式 'YYYY-MM-DD HH:MM'
        """
        # 解析开始时间
        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        
        # 计算结束时间
        end_dt = start_dt + timedelta(hours=hours_offset)
        
        # 格式化输出
        return end_dt.strftime("%Y-%m-%d %H:%M")
# 全局数据生成器实例
data_generator = DataGenerator()
