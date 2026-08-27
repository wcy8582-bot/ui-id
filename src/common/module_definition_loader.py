import os
import yaml
from typing import Dict, Optional, List
from .file_utils import FileUtils
from .logger import logger


class ModuleDefinitionError(Exception):
    """模块定义异常"""
    pass


class ModuleDefinitionLoader:
    """项目和模块定义加载器"""

    _instance = None

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(ModuleDefinitionLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化模块定义加载器"""
        if not self._initialized:
            self.module_def_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'config', 'module_definitions.yaml'
            )
            self.module_def = self._load_module_def()
            self._initialized = True

    def _load_module_def(self) -> Dict:
        """加载模块定义文件"""
        try:
            if not os.path.exists(self.module_def_path):
                logger.warning(f"模块定义文件不存在: {self.module_def_path}")
                return {
                    'projects': {},
                    'modules': {}
                }

            with open(self.module_def_path, 'r', encoding='utf-8') as f:
                module_def = yaml.safe_load(f)

            # 填充默认结构
            if not module_def:
                module_def = {}
            if 'projects' not in module_def:
                module_def['projects'] = {}
            if 'modules' not in module_def:
                module_def['modules'] = {}

            logger.info(f"模块定义加载成功，包含 {len(module_def['projects'])} 个项目，{len(module_def['modules'])} 个模块")
            return module_def

        except Exception as e:
            logger.error(f"加载模块定义文件失败: {str(e)}")
            return {
                'projects': {},
                'modules': {}
            }

    def reload_module_def(self) -> None:
        """重新加载模块定义"""
        self.module_def = self._load_module_def()
        logger.info("模块定义已重新加载")

    def get_project_name_cn(self, project_en: str) -> str:
        """
        获取项目中文名

        Args:
            project_en: 项目英文名

        Returns:
            str: 项目中文名，如果未找到则返回原英文名
        """
        project_name_cn = self.module_def['projects'].get(project_en)
        if project_name_cn:
            return project_name_cn
        logger.warning(f"未找到项目 {project_en} 的中文名定义，返回原名称")
        return project_en

    def get_module_name_cn(self, module_en: str) -> str:
        """
        获取模块中文名

        Args:
            module_en: 模块英文名

        Returns:
            str: 模块中文名，如果未找到则返回原英文名
        """
        module_name_cn = self.module_def['modules'].get(module_en)
        if module_name_cn:
            return module_name_cn
        logger.warning(f"未找到模块 {module_en} 的中文名定义，返回原名称")
        return module_en

    def get_all_projects(self) -> Dict[str, str]:
        """
        获取所有项目定义

        Returns:
            Dict[str, str]: 项目英文名到中文名的映射
        """
        return self.module_def['projects'].copy()

    def get_all_modules(self) -> Dict[str, str]:
        """
        获取所有模块定义

        Returns:
            Dict[str, str]: 模块英文名到中文名的映射
        """
        return self.module_def['modules'].copy()

    def get_project_list(self) -> List[str]:
        """
        获取所有项目英文名列表

        Returns:
            List[str]: 项目英文名列表
        """
        return list(self.module_def['projects'].keys())

    def get_module_list(self) -> List[str]:
        """
        获取所有模块英文名列表

        Returns:
            List[str]: 模块英文名列表
        """
        return list(self.module_def['modules'].keys())


# 全局模块定义加载器实例
module_def_loader = ModuleDefinitionLoader()
