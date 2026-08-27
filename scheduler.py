import time
import subprocess
import sys
import os
from datetime import datetime

interval_minutes = 30

def run_test():
    """执行测试脚本"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 开始执行...")

    try:
        # 方法1：使用 os.system 打开新终端
        print(f"[{timestamp}] 使用 os.system 打开终端")
        os.system('start cmd /k "cd /d E:\\UIProject\\auto_ui\\playwright-ui-automation && python --version"')
        print(f"[{timestamp}] 命令已执行")

    except Exception as e:
        print(f"[{timestamp}] 执行异常: {str(e)}")

    print(f"[{timestamp}] 执行完成")

def schedule_task():
    """定时任务主循环"""
    print("定时任务已启动...")
    print(f"每{interval_minutes}分钟打开一个终端窗口执行命令")
    print("按 Ctrl+C 停止定时任务\n")

    # 立即执行第一次
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行任务")
    run_test()

    # 然后每30分钟执行一次
    while True:
        next_run_time = time.time() + (interval_minutes * 60)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 下次执行时间: {datetime.fromtimestamp(next_run_time).strftime('%H:%M:%S')}")

        time.sleep(interval_minutes * 60)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行任务")
        run_test()

def main():
    try:
        schedule_task()
    except KeyboardInterrupt:
        print("\n\n定时任务已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
