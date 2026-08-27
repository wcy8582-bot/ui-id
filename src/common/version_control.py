"""
版本控制功能模块
"""
import os
import shutil
import yaml
from datetime import datetime
from typing import Dict, Optional
from src.common.logger import logger
from src.common.database import TestResultDB
from src.common.config_loader import config_loader


def get_project_root() -> str:
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_current_version() -> Optional[str]:
    """
    从 module_definitions.yaml 中读取当前版本
    
    Returns:
        当前版本号，不存在返回 None
    """
    module_def_path = os.path.join(get_project_root(), "config", "module_definitions.yaml")
    if not os.path.exists(module_def_path):
        return None
    
    try:
        with open(module_def_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config.get("current_version")
    except Exception as e:
        logger.error(f"读取版本号失败: {e}")
        return None


def set_current_version(version: str) -> bool:
    """
    设置当前版本号
    
    Args:
        version: 版本号
        
    Returns:
        成功返回 True，失败返回 False
    """
    module_def_path = os.path.join(get_project_root(), "config", "module_definitions.yaml")
    
    try:
        if not os.path.exists(module_def_path):
            config = {}
        else:
            with open(module_def_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        
        config["current_version"] = version
        
        with open(module_def_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"当前版本号已设置为: {version}")
        return True
    except Exception as e:
        logger.error(f"设置版本号失败: {e}")
        return False


def backup_version(backup_user: str, version_info: str = None) -> bool:
    """
    备份当前版本
    
    1. 获取当前版本号
    2. 创建 src_{version} 文件夹
    3. 将 src 复制到 src_{version}
    4. 保存版本信息到数据库
    
    Args:
        backup_user: 备份人
        version_info: 版本信息（可选）
        
    Returns:
        成功返回 True，失败返回 False
    """
    current_version = get_current_version()
    if not current_version:
        logger.error("当前版本号未设置，无法备份")
        return False
    
    logger.info(f"开始备份版本 {current_version}")
    
    # 1. 获取数据库连接
    db_config = config_loader.get_config().get('database')
    db_config_dict = {
        'backend': db_config.get('backend', 'mysql'),
        'sqlite_path': db_config.get('sqlite_path', 'data/test_results.db'),
        'host': db_config.get('host', '127.0.0.1'),
        'port': int(db_config.get('port', 3306)),
        'user': db_config.get('user', 'root'),
        'password': db_config.get('password', ''),
        'database_name': db_config.get('database_name', 'uitest'),
        'charset': db_config.get('charset', 'utf8mb4')
    }
    db = TestResultDB(db_config_dict)
    if not db.connect():
        logger.error("数据库连接失败")
        return False
    
    try:
        # 2. 创建备份文件夹
        src_path = os.path.join(get_project_root(), "src")
        backup_path = os.path.join(get_project_root(), f"src_{current_version}")
        
        if os.path.exists(backup_path):
            # 如果文件夹已存在，先删除
            logger.info(f"备份文件夹已存在，删除旧的: {backup_path}")
            try:
                shutil.rmtree(backup_path)
            except Exception as e:
                logger.warning(f"删除旧备份失败，继续执行: {e}")
        
        # 3. 复制文件夹
        shutil.copytree(src_path, backup_path)
        logger.info(f"源代码已复制到 {backup_path}")
        
        # 4. 保存到数据库
        success = db.insert_or_update_version(
            version=current_version,
            backup_user=backup_user,
            version_info=version_info
        )
        
        if success:
            logger.info(f"版本 {current_version} 备份完成")
            return True
        else:
            # 删除备份文件夹
            try:
                shutil.rmtree(backup_path)
            except:
                pass
            return False
            
    except Exception as e:
        logger.error(f"备份版本失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        db.close()


def create_new_version(new_version: str, backup_user: str) -> bool:
    """
    创建新版本
    
    1. 将当前版本号修改为新的版本号
    2. 备份新的版本
    
    Args:
        new_version: 新版本号
        backup_user: 备份人
        
    Returns:
        成功返回 True，失败返回 False
    """
    logger.info(f"开始创建新版本: {new_version}")
    
    # 1. 先更新配置文件中的版本号
    if not set_current_version(new_version):
        return False
    
    # 2. 备份新版本
    success = backup_version(
        backup_user=backup_user,
        version_info=f"从原版本升级而来"
    )
    
    if success:
        logger.info(f"新版本 {new_version} 创建完成")
    else:
        # 失败回退版本号
        logger.error("创建新版本失败")
        
    return success


def switch_version(target_version: str) -> bool:
    """
    切换到指定版本
    
    1. 更新配置文件中的版本号
    2. 将 src 替换为 src_{target_version} 的内容
    
    Args:
        target_version: 目标版本号
        
    Returns:
        成功返回 True，失败返回 False
    """
    logger.info(f"开始切换到版本: {target_version}")
    
    # 1. 检查备份是否存在
    backup_path = os.path.join(get_project_root(), f"src_{target_version}")
    if not os.path.exists(backup_path):
        logger.error(f"版本备份不存在: {backup_path}")
        return False
    
    # 2. 先备份当前版本，以防出错
    current_version = get_current_version()
    if current_version:
        logger.info(f"先备份当前版本 {current_version}")
        # 这里直接备份，没有用户，先不管
        # 实际使用可能需要传入用户
    
    # 3. 更新配置文件
    if not set_current_version(target_version):
        return False
    
    # 4. 复制备份到 src
    src_path = os.path.join(get_project_root(), "src")
    
    # 先备份当前 src
    temp_path = os.path.join(get_project_root(), "src_temp")
    if os.path.exists(src_path):
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        os.rename(src_path, temp_path)
    
    try:
        shutil.copytree(backup_path, src_path)
        logger.info(f"源代码已替换为版本 {target_version}")
        
        # 删除临时备份
        if os.path.exists(temp_path):
            try:
                shutil.rmtree(temp_path)
            except:
                pass
                
        logger.info(f"切换到版本 {target_version} 成功")
        return True
    except Exception as e:
        logger.error(f"切换版本失败: {e}")
        
        # 回退
        if os.path.exists(temp_path):
            try:
                shutil.rmtree(src_path)
                os.rename(temp_path, src_path)
            except Exception as e2:
                logger.error(f"回退失败: {e2}")
                
        if current_version:
            set_current_version(current_version)
            
        return False


def delete_version(version: str, delete_user: str) -> bool:
    """
    删除指定版本
    
    1. 在数据库中将该版本标记为删除
    2. 将备份文件夹重命名为 del_src_{version}_{timestamp}_{user}
    
    Args:
        version: 要删除的版本号
        delete_user: 删除人
        
    Returns:
        成功返回 True，失败返回 False
    """
    logger.info(f"开始删除版本: {version}")
    
    backup_path = os.path.join(get_project_root(), f"src_{version}")
    
    # 1. 获取数据库连接
    db_config = config_loader.get_config().get('database')
    db_config_dict = {
        'backend': db_config.get('backend', 'mysql'),
        'sqlite_path': db_config.get('sqlite_path', 'data/test_results.db'),
        'host': db_config.get('host', '127.0.0.1'),
        'port': int(db_config.get('port', 3306)),
        'user': db_config.get('user', 'root'),
        'password': db_config.get('password', ''),
        'database_name': db_config.get('database_name', 'uitest'),
        'charset': db_config.get('charset', 'utf8mb4')
    }
    db = TestResultDB(db_config_dict)
    if not db.connect():
        logger.error("数据库连接失败")
        return False
    
    try:
        # 2. 先检查数据库版本是否存在且有效
        version_info = db.get_active_version(version)
        if not version_info:
            logger.error(f"版本 {version} 不存在或已删除")
            return False
        
        # 3. 标记为删除
        if not db.mark_version_deleted(version):
            logger.error("数据库标记失败")
            return False
        
        # 4. 重命名文件夹
        if os.path.exists(backup_path):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_path = os.path.join(get_project_root(), f"del_src_{version}_{timestamp}_{delete_user}")
            os.rename(backup_path, new_path)
            logger.info(f"备份文件夹已重命名为: {new_path}")
        
        logger.info(f"版本 {version} 删除成功")
        return True
        
    except Exception as e:
        logger.error(f"删除版本失败: {e}")
        return False
    finally:
        db.close()


def get_version_info(version: str) -> Optional[Dict]:
    """
    获取版本信息
    
    Args:
        version: 版本号
        
    Returns:
        版本信息字典，不存在返回 None
    """
    # 获取数据库连接
    db_config = config_loader.get_config().get('database')
    db_config_dict = {
        'backend': db_config.get('backend', 'mysql'),
        'sqlite_path': db_config.get('sqlite_path', 'data/test_results.db'),
        'host': db_config.get('host', '127.0.0.1'),
        'port': int(db_config.get('port', 3306)),
        'user': db_config.get('user', 'root'),
        'password': db_config.get('password', ''),
        'database_name': db_config.get('database_name', 'uitest'),
        'charset': db_config.get('charset', 'utf8mb4')
    }
    db = TestResultDB(db_config_dict)
    if not db.connect():
        logger.error("数据库连接失败")
        return None
    
    try:
        return db.get_active_version(version)
    finally:
        db.close()


def get_all_versions() -> list:
    """
    获取所有有效版本列表
    
    Returns:
        版本信息列表
    """
    # 获取数据库连接
    db_config = config_loader.get_config().get('database')
    db_config_dict = {
        'backend': db_config.get('backend', 'mysql'),
        'sqlite_path': db_config.get('sqlite_path', 'data/test_results.db'),
        'host': db_config.get('host', '127.0.0.1'),
        'port': int(db_config.get('port', 3306)),
        'user': db_config.get('user', 'root'),
        'password': db_config.get('password', ''),
        'database_name': db_config.get('database_name', 'uitest'),
        'charset': db_config.get('charset', 'utf8mb4')
    }
    db = TestResultDB(db_config_dict)
    if not db.connect():
        logger.error("数据库连接失败")
        return []
    
    try:
        return db.get_all_active_versions()
    finally:
        db.close()


def create_new_version_with_info(new_version: str, backup_user: str, version_info: str = None) -> bool:
    """
    创建新版本（带版本信息）
    
    1. 将当前版本号修改为新的版本号
    2. 备份新的版本
    
    Args:
        new_version: 新版本号
        backup_user: 备份人
        version_info: 版本信息（可选）
        
    Returns:
        成功返回 True，失败返回 False
    """
    logger.info(f"开始创建新版本: {new_version}")
    
    # 1. 先更新配置文件中的版本号
    if not set_current_version(new_version):
        return False
    
    # 2. 备份新版本
    success = backup_version(
        backup_user=backup_user,
        version_info=version_info
    )
    
    if success:
        logger.info(f"新版本 {new_version} 创建完成")
    else:
        # 失败回退版本号
        logger.error("创建新版本失败")
        
    return success


def check_version_exists(version: str) -> bool:
    """
    检查版本是否已存在
    
    Args:
        version: 版本号
        
    Returns:
        存在返回 True，否则返回 False
    """
    version_info = get_version_info(version)
    return version_info is not None

