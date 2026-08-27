from openai import OpenAI
import time
import sys
import os

# 添加项目根目录到Python路径，解决相对导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    # 尝试相对导入
    from .logger import logger
    from .config_loader import config_loader
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from src.common.logger import logger
    from src.common.config_loader import config_loader

# 全局配置
config = config_loader.get_config()['model_config']

def ai_chat(messages):
    """调用AI API（使用OpenAI SDK）
    
    Args:
        messages: 消息列表
        
    Returns:
        API返回结果
    """
    logger.info("开始调用AI API...")
    
    # 从配置文件获取参数
    api_key = config['API_KEY']
    endpoint_id = config['MODEL_NAME']
    base_url = config.get('API_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
    max_tokens = config.get('MAX_TOKENS', 1024)
    temperature = config.get('TEMPERATURE', 0.7)
    top_p = config.get('TOP_P', 0.9)
    
    logger.debug(f"API配置: base_url={base_url}, model={endpoint_id}, max_tokens={max_tokens}")
    logger.debug(f"API Key: {'已设置' if api_key else '未设置'}")
    
    # 创建OpenAI客户端
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    logger.debug(f"请求数据: messages={len(messages)}条")
    
    try:
        start_time = time.time()
        logger.info(f"发送请求到: {base_url}")
        
        # 使用OpenAI SDK调用API
        response = client.chat.completions.create(
            model=endpoint_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        
        end_time = time.time()
        
        # 转换为字典格式以便与原代码兼容
        result = response.model_dump()
        
        # 打印token消耗和耗时
        if 'usage' in result:
            logger.info(f"总token消耗: {result['usage']['total_tokens']}")
        logger.info(f"豆包AI API调用成功，耗时: {end_time - start_time:.2f}秒")
        logger.debug(f"API响应: {result}")
        
        return result
    except Exception as e:
        logger.error(f"请求出错: {str(e)}")
        return f"请求出错: {e}"

# --- 测试调用 ---
if __name__ == "__main__":
    conversation = [
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
    
    reply = ai_chat(conversation)
    if isinstance(reply, dict) and 'choices' in reply:
        try:
            # 使用sys.stdout.buffer直接输出UTF-8编码的内容
            content = reply["choices"][0]["message"]["content"]
            # 移除所有emoji和特殊字符
            import re
            content = re.sub(r'[\U00010000-\U0010ffff]', '', content)
            print("豆包回答：", content)
        except Exception as e:
            print(f"打印出错: {e}")
            # 直接打印原始内容（可能会有乱码但至少能看到）
            print("原始回答:", reply)
    else:
        print("豆包回答：", reply)
