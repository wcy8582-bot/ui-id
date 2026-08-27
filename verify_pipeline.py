import requests
import time
import json
import sys

BASE_URL = "http://10.52.54.145:5000"
# BASE_URL = "http://localhost:5000"


def step1_execute_test():
    """模拟 Pipeline 中的 Execute UI Test 阶段"""
    print("=" * 60)
    print("Step 1: 发起测试执行 (POST /execute_test)")
    print("=" * 60)

    payload = {
        "project": "LX",
        "url": "http://10.54.48.143:8080",
        "username": "admin",
        "pwd": "Supcon1304@",
        "module": "scenario_case",
        "case": "positive_production_proc",
        "wh": 0
    }

    print(f"请求体: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        resp = requests.post(
            f"{BASE_URL}/execute_test",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=600
        )
        resp.raise_for_status()
        data = resp.json()
        print(f"\n响应: {json.dumps(data, indent=2, ensure_ascii=False)}")

        if not data.get("success"):
            print(f"\n❌ 测试发起失败: {data.get('message')}")
            return None

        execution_id = data.get("execution_id")
        if not execution_id:
            print(f"\n❌ 未获取到 execution_id: {data.get('warning', '未知原因')}")
            return None

        print(f"\n✅ 测试已发起，execution_id = {execution_id}")
        return execution_id

    except requests.exceptions.ConnectionError:
        print(f"\n❌ 无法连接到 {BASE_URL}，请确认服务是否已启动")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        sys.exit(1)


def step2_monitor_status(execution_id):
    """模拟 Pipeline 中的 Monitor Test Status 阶段"""
    print("\n" + "=" * 60)
    print(f"Step 2: 监控测试状态 (GET /get_execution_status/{execution_id})")
    print("=" * 60)

    max_wait_minutes = 60
    poll_interval_seconds = 10
    end_time = time.time() + max_wait_minutes * 60

    print(f"最长等待: {max_wait_minutes} 分钟 | 轮询间隔: {poll_interval_seconds} 秒")

    while time.time() < end_time:
        try:
            resp = requests.get(
                f"{BASE_URL}/get_execution_status/{execution_id}",
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            data = resp.json()

            if not data.get("success"):
                print(f"⚠️ 查询失败: {data.get('message')}")
                time.sleep(poll_interval_seconds)
                continue

            exec_info = data.get("execution", {})
            status = exec_info.get("status", "unknown")
            total = exec_info.get("total_cases", "?")
            passed = exec_info.get("passed_cases", "?")
            duration = exec_info.get("duration", "?")

            print(f"  📌 ID={exec_info.get('id')} | 状态={status} | 通过={passed}/{total}")

            if status == "completed":
                print(f"\n✅ 测试执行完成！耗时: {duration} 秒")
                return True
            elif status == "failed":
                print(f"\n❌ 测试执行失败！耗时: {duration} 秒")
                return True
            elif status == "timeout":
                print(f"\n⏰ 测试执行超时！")
                return False

            time.sleep(poll_interval_seconds)

        except Exception as e:
            print(f"⚠️ 查询异常: {e}")
            time.sleep(poll_interval_seconds)

    print(f"\n❌ 监控超时：超过 {max_wait_minutes} 分钟未完成")
    return False


def step3_get_results(execution_id):
    """模拟 Pipeline 中的 Get Test Results 阶段"""
    print("\n" + "=" * 60)
    print(f"Step 3: 获取测试结果 (GET /get_test_results/{execution_id})")
    print("=" * 60)

    try:
        resp = requests.get(
            f"{BASE_URL}/get_test_results/{execution_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        data = resp.json()

        if not data.get("success"):
            print(f"❌ 获取结果失败: {data.get('message')}")
            return False

        exec_info = data.get("execution", {})
        stats = data.get("statistics", {})
        case_results = data.get("case_results", [])

        print(f"\n📊 测试概览")
        print(f"  项目: {exec_info.get('project')} | 模块: {exec_info.get('module')}")
        print(f"  耗时: {exec_info.get('duration')} 秒")
        print(f"  通过: {exec_info.get('passed_cases')}/{exec_info.get('total_cases')}")

        print(f"\n📊 统计: 总计 {stats.get('total_cases', 0)} | "
              f"通过 {stats.get('passed_cases', 0)} | "
              f"失败 {stats.get('failed_cases', 0)}")

        print(f"\n🧪 用例详情:")
        failed_count = 0
        for cr in case_results:
            status = cr.get("status")
            name = cr.get("case_name")
            dur = cr.get("duration")
            if status == "failed":
                print(f"  ❌ {name} | 耗时: {dur}s | 错误: {cr.get('error_message', '')}")
                failed_count += 1
            else:
                print(f"  ✅ {name} | 耗时: {dur}s")

        if failed_count > 0:
            print(f"\n❌ 共 {failed_count} 个用例失败！")
            return False
        else:
            print(f"\n🎉 所有用例执行通过！")
            return True

    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False


def main():
    print("Pipeline 调用验证脚本")
    print(f"目标服务器: {BASE_URL}")
    print()

    execution_id = step1_execute_test()
    if not execution_id:
        print("\n❌ Step 1 失败，终止验证")
        sys.exit(1)

    monitor_ok = step2_monitor_status(execution_id)
    if not monitor_ok:
        print("\n❌ Step 2 监控异常（超时），终止验证")
        sys.exit(1)

    result_ok = step3_get_results(execution_id)

    print("\n" + "=" * 60)
    print(f"验证结果: {'✅ 全部通过' if result_ok else '❌ 存在失败用例'}")
    print("=" * 60)
    sys.exit(0 if result_ok else 1)


if __name__ == "__main__":
    main()
