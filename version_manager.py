"""
版本控制命令行工具
"""
import sys
import argparse
from src.common.version_control import (
    backup_version,
    create_new_version,
    switch_version,
    delete_version,
    get_version_info,
    get_all_versions,
    get_current_version
)


def main():
    parser = argparse.ArgumentParser(description="UI自动化测试版本控制工具")
    subparsers = parser.add_subparsers(title="子命令", dest="command")
    
    # 1. 查看当前版本
    current_parser = subparsers.add_parser("current", help="查看当前版本号")
    
    # 2. 查看版本信息
    info_parser = subparsers.add_parser("info", help="查看指定版本信息")
    info_parser.add_argument("version", help="版本号")
    
    # 3. 查看所有版本列表
    list_parser = subparsers.add_parser("list", help="查看所有有效版本")
    
    # 4. 备份当前版本
    backup_parser = subparsers.add_parser("backup", help="备份当前版本")
    backup_parser.add_argument("--user", "-u", required=True, help="备份人")
    backup_parser.add_argument("--info", "-i", required=False, help="版本信息（可选）")
    
    # 5. 创建新版本
    create_parser = subparsers.add_parser("create", help="创建新版本")
    create_parser.add_argument("--version", "-v", required=True, help="新版本号")
    create_parser.add_argument("--user", "-u", required=True, help="备份人")
    
    # 6. 切换版本
    switch_parser = subparsers.add_parser("switch", help="切换到指定版本")
    switch_parser.add_argument("version", help="目标版本号")
    
    # 7. 删除版本
    delete_parser = subparsers.add_parser("delete", help="删除指定版本")
    delete_parser.add_argument("version", help="要删除的版本号")
    delete_parser.add_argument("--user", "-u", required=True, help="删除人")
    
    args = parser.parse_args()
    
    # 执行命令
    if args.command == "current":
        v = get_current_version()
        if v:
            print(f"当前版本: {v}")
        else:
            print("未设置版本号")
            
    elif args.command == "info":
        info = get_version_info(args.version)
        if info:
            print("="*50)
            print(f"版本号: {info.get('version')}")
            print(f"版本信息: {info.get('version_info', '-')}")
            print(f"备份时间: {info.get('backup_time')}")
            print(f"备份人: {info.get('backup_user')}")
            print("="*50)
        else:
            print("未找到该版本或版本已无效")
            
    elif args.command == "list":
        versions = get_all_versions()
        if versions:
            print("="*70)
            print(f"{'版本号':<15}{'版本信息':<20}{'备份时间':<20}{'备份人':<15}")
            print("-"*70)
            for v in versions:
                info = v.get('version_info', '-')
                if info and len(info) > 20:
                    info = info[:17] + "..."
                print(f"{v.get('version'):<15}{info:<20}{str(v.get('backup_time')):<20}{v.get('backup_user'):<15}")
            print("="*70)
            print(f"共 {len(versions)} 个版本")
        else:
            print("暂无有效版本")
            
    elif args.command == "backup":
        print("="*50)
        print("正在备份当前版本...")
        if backup_version(args.user, args.info):
            print("✓ 备份成功！")
            sys.exit(0)
        else:
            print("✗ 备份失败！")
            sys.exit(1)
            
    elif args.command == "create":
        print("="*50)
        print(f"正在创建新版本: {args.version}")
        if create_new_version(args.version, args.user):
            print("✓ 版本创建成功！")
            sys.exit(0)
        else:
            print("✗ 版本创建失败！")
            sys.exit(1)
            
    elif args.command == "switch":
        print("="*50)
        print(f"正在切换到版本: {args.version}")
        confirm = input("确认要切换版本吗？(y/n): ")
        if confirm.lower() in ['y', 'yes']:
            if switch_version(args.version):
                print("✓ 版本切换成功！")
                print("请重新启动 app.py 使用新版本")
                sys.exit(0)
            else:
                print("✗ 版本切换失败！")
                sys.exit(1)
        else:
            print("操作已取消")
            
    elif args.command == "delete":
        print("="*50)
        print(f"正在删除版本: {args.version}")
        confirm = input("确认要删除此版本吗？此操作不可恢复！(yes/no): ")
        if confirm.lower() == "yes":
            if delete_version(args.version, args.user):
                print("✓ 版本删除成功！")
                sys.exit(0)
            else:
                print("✗ 版本删除失败！")
                sys.exit(1)
        else:
            print("操作已取消")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

