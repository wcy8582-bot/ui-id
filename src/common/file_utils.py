import os
import shutil
import time
from typing import List, Optional


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def create_directory(path: str) -> None:
        """创建目录
        
        Args:
            path: 目录路径
        """
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def write_file(file_path: str, content: str) -> None:
        """写入文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
        """
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path:
            FileUtils.create_directory(dir_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """读取文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def join_path(*paths) -> str:
        """拼接路径
        
        Args:
            *paths: 路径片段
            
        Returns:
            拼接后的路径
        """
        return os.path.join(*paths)
    
    @staticmethod
    def get_absolute_path(relative_path: str) -> str:
        """获取绝对路径
        
        Args:
            relative_path: 相对路径
            
        Returns:
            绝对路径
        """
        return os.path.abspath(relative_path)
    
    @staticmethod
    def clean_expired_files(directory: str, expired_days: int) -> None:
        """清理过期文件
        
        Args:
            directory: 目录路径
            expired_days: 过期天数
        """
        if not os.path.exists(directory):
            return
        
        current_time = time.time()
        expired_time = current_time - (expired_days * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(directory):
            # 清理文件
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < expired_time:
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
            
            # 清理空目录
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):
                    try:
                        os.rmdir(dir_path)
                    except Exception:
                        pass
    
    @staticmethod
    def compress_directory(directory: str, output_file: str) -> None:
        """压缩目录
        
        Args:
            directory: 要压缩的目录
            output_file: 输出压缩文件路径
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir:
            FileUtils.create_directory(output_dir)
        
        # 压缩目录
        shutil.make_archive(
            output_file.replace('.zip', ''),
            'zip',
            directory
        )
    
    @staticmethod
    def get_file_list(directory: str, pattern: Optional[str] = None) -> List[str]:
        """获取文件列表
        
        Args:
            directory: 目录路径
            pattern: 文件匹配模式
            
        Returns:
            文件路径列表
        """
        file_list = []
        
        if not os.path.exists(directory):
            return file_list
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if pattern:
                    if fnmatch.fnmatch(file, pattern):
                        file_list.append(os.path.join(root, file))
                else:
                    file_list.append(os.path.join(root, file))
        
        return file_list


# 导入fnmatch模块
import fnmatch
