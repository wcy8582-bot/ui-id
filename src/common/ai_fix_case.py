"""
AI 用例修复模块

封装用例修复任务的后台执行逻辑：调用 AI API 对失败用例进行错误分析并生成修复代码，
将结果回写到 fix_failed_case 表。从 app.py 中抽离，便于单独维护提示词与执行流程。
"""
import json as _json

try:
    from .logger import logger
    from .ai_chat import ai_chat
except ImportError:
    from src.common.logger import logger
    from src.common.ai_chat import ai_chat


def _build_messages(source_code, error_log, error_message, supplement_info=None):
    """构造 AI 修复请求的消息列表（system + user）

    Args:
        source_code: 用例原始源代码
        error_log: 失败用例执行日志
        error_message: 失败用例错误信息
        supplement_info: 用户补充信息（非必填，如录制的原始脚本代码或页面元素）
    """
    system_prompt = (
        "你是一个自动化测试代码修复专家，必须遵循【最小化局部修复】原则。\n\n"
        "## 核心修复原则（不可违反）\n"
        "1. 精准定位错误点：根据错误信息和日志中的行号、报错内容、定位器语法，"
        "准确定位到导致失败的具体代码行或具体方法调用。\n"
        "2. 仅局部修改：只修改导致失败的代码片段（如某个定位器、某行语句、某个参数），"
        "禁止对整个用例、整个方法或多个步骤进行重写。\n"
        "3. 不改测试流程：禁止调整用例的执行步骤顺序、增删业务步骤、改变断言点，"
        "禁止把同步调用改为异步、禁止合并/拆分方法。\n"
        "4. 不动未报错部分：未触发报错的代码（包括登录、导航、其他业务步骤、断言）"
        "必须保持原样，一字不改。\n"
        "5. 不重构：禁止重命名变量、抽取函数、调整代码风格、补全类型注解、"
        "添加注释，禁止所谓\"顺手优化\"。\n"
        "6. 保留断言：只能修正断言中失效的定位器或预期值，禁止移除或弱化断言。\n"
        "7. 风格一致：修改后的代码风格、缩进、命名需与原代码保持一致。\n\n"
        "## 输出要求\n"
        "返回严格的JSON格式，fixed_code 字段必须是【修复后的完整用例源代码】"
        "（即原代码仅替换错误点后的版本，其余部分逐字保留）：\n"
        '{"error_analysis": "错误原因分析（说明定位到哪一行、为何报错、如何修）", '
        '"fixed_code": "修复后的完整用例源代码（仅错误点处与原代码不同）"}'
    )

    # 拼接用户补充信息（如有）
    supplement_section = ""
    if supplement_info:
        supplement_section = (
            "\n## 用户补充信息（请重点参考，如录制的原始脚本代码或页面元素）\n"
            f"{supplement_info}\n"
        )

    user_prompt = (
        f"## 用例源代码\n{source_code}\n\n"
        f"## 错误信息\n{error_message or '(无)'}\n\n"
        f"## 执行日志\n{error_log or '(无)'}\n\n"
        f"{supplement_section}"
        "## 任务\n"
        "请按以下步骤处理：\n"
        "1. 从错误信息中提取报错行号和报错语句。\n"
        "2. 结合日志和源码（以及用户补充信息，如有）分析该行失败的根本原因"
        "（如定位器失效、参数错误、iframe 变化、元素不唯一等）。\n"
        "3. 仅针对该错误点进行最小化修改，其余代码原样保留。"
        "若用户补充信息提供了正确的页面元素或脚本片段，请据此修正错误点。\n"
        "4. 返回JSON：error_analysis 说明错误定位与修复思路，"
        "fixed_code 为修复后的完整源代码。\n\n"
        "## 再次强调\n"
        "- 不要重构未报错的代码。\n"
        "- 不要改变用例的业务流程和断言结构。\n"
        "- 不要做任何\"改进性\"修改，只让用例能正确跑通。"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]


def execute_fix_task(task_id, source_code, error_log, error_message, db_instance,
                     supplement_info=None):
    """后台线程：调用AI修复用例

    Args:
        task_id: 修复任务 ID
        source_code: 用例原始源代码
        error_log: 失败用例执行日志
        error_message: 失败用例错误信息
        db_instance: 已连接的 TestResultDB 实例（调用方负责连接/关闭）
        supplement_info: 用户补充信息（非必填，不写入数据库，仅拼接到提示词）
    """
    db = db_instance
    try:
        messages = _build_messages(source_code, error_log, error_message, supplement_info)

        logger.info(f"修复任务 {task_id}: 开始调用AI API")
        response = ai_chat(messages)

        if isinstance(response, dict) and 'choices' in response:
            content = response['choices'][0]['message']['content']
            # 提取JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                result = _json.loads(content[start:end])
                db.update_fix_task_result(
                    task_id,
                    result.get('error_analysis', ''),
                    result.get('fixed_code', ''),
                    '已完成'
                )
                logger.info(f"修复任务 {task_id}: AI修复完成")
            else:
                db.update_fix_task_result(
                    task_id,
                    f"AI返回内容无法解析为JSON: {content[:500]}",
                    '',
                    '失败'
                )
                logger.error(f"修复任务 {task_id}: AI返回内容无法解析")
        else:
            db.update_fix_task_result(
                task_id,
                f"AI API调用失败: {str(response)[:500]}",
                '',
                '失败'
            )
            logger.error(f"修复任务 {task_id}: AI API调用失败: {response}")
    except _json.JSONDecodeError as e:
        db.update_fix_task_result(task_id, f"JSON解析失败: {str(e)}", '', '失败')
        logger.error(f"修复任务 {task_id}: JSON解析失败: {e}")
    except Exception as e:
        db.update_fix_task_result(task_id, f"执行异常: {str(e)}", '', '失败')
        logger.error(f"修复任务 {task_id}: 执行异常: {e}")
