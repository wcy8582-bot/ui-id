import os
import yaml
from typing import Dict, Optional
from .file_utils import FileUtils


class ConfigError(Exception):
    """配置异常"""
    pass


class ConfigLoader:
    """全局配置加载器"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化配置加载器"""
        if not self._initialized:
            self.config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'execution_config.yaml')
            self.config = self._load_config()
            self._initialize_paths()
            self._initialized = True
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 填充缺省值
            config = self._fill_defaults(config)
            
            # 校验配置合法性
            self._validate_config(config)
            
            return config
            
        except Exception as e:
            raise ConfigError(f"加载配置文件失败: {str(e)}")
    
    def _fill_defaults(self, config: Dict) -> Dict:
        """填充缺省值"""
        # 执行范围配置缺省值
        if 'execution_scope' not in config:
            config['execution_scope'] = {}
        if 'target_project' not in config['execution_scope']:
            config['execution_scope']['target_project'] = "*"
        if 'target_modules' not in config['execution_scope']:
            config['execution_scope']['target_modules'] = ["*"]
        
        # 浏览器配置缺省值
        if 'browser' not in config:
            config['browser'] = {}
        if 'browser_type' not in config['browser']:
            config['browser']['browser_type'] = "Chromium"
        if 'headless' not in config['browser']:
            config['browser']['headless'] = False
        if 'viewport_size' not in config['browser']:
            config['browser']['viewport_size'] = {"width": 1920, "height": 1080}
        if 'slow_mo' not in config['browser']:
            config['browser']['slow_mo'] = 0
        if 'default_timeout' not in config['browser']:
            config['browser']['default_timeout'] = 3000000
        if 'ignore_https_errors' not in config['browser']:
            config['browser']['ignore_https_errors'] = False
        
        # 用例执行配置缺省值
        if 'execution' not in config:
            config['execution'] = {}
        if 'max_retry_count' not in config['execution']:
            config['execution']['max_retry_count'] = 2
        if 'run_in_parallel' not in config['execution']:
            config['execution']['run_in_parallel'] = True
        if 'parallel_workers' not in config['execution']:
            config['execution']['parallel_workers'] = 4
        if 'case_filter' not in config['execution']:
            config['execution']['case_filter'] = ""
        if 'fail_fast' not in config['execution']:
            config['execution']['fail_fast'] = False
        
        # 路径配置缺省值
        if 'paths' not in config:
            config['paths'] = {}
        if 'logs_root_dir' not in config['paths']:
            config['paths']['logs_root_dir'] = "logs"
        if 'screenshots_root_dir' not in config['paths']:
            config['paths']['screenshots_root_dir'] = "screenshots"
        if 'reports_root_dir' not in config['paths']:
            config['paths']['reports_root_dir'] = "reports"
        
        # 全局开关缺省值
        if 'global' not in config:
            config['global'] = {}
        if 'enable_full_step_screenshot' not in config['global']:
            config['global']['enable_full_step_screenshot'] = False
        if 'enable_video_record' not in config['global']:
            config['global']['enable_video_record'] = False
        if 'enable_debug_log' not in config['global']:
            config['global']['enable_debug_log'] = False
        if 'auto_clean_expired_files' not in config['global']:
            config['global']['auto_clean_expired_files'] = True
        if 'expired_days' not in config['global']:
            config['global']['expired_days'] = 7
        
        return config
    
    def _validate_config(self, config: Dict) -> None:
        """校验配置合法性"""
        # 校验浏览器类型
        valid_browsers = ["Chromium", "Firefox", "WebKit"]
        if config['browser']['browser_type'] not in valid_browsers:
            raise ConfigError(f"无效的浏览器类型: {config['browser']['browser_type']}")
        
        # 校验并行工作线程数
        if config['execution']['parallel_workers'] < 1:
            raise ConfigError("并行工作线程数必须大于0")
        
        # 校验过期天数
        if config['global']['expired_days'] < 1:
            raise ConfigError("文件保留天数必须大于0")
    
    def _initialize_paths(self) -> None:
        """初始化路径"""
        # 获取项目根目录
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        
        # 确保所有路径存在
        paths = [
            os.path.join(project_root, self.config['paths']['logs_root_dir']),
            os.path.join(project_root, self.config['paths']['screenshots_root_dir']),
            os.path.join(project_root, self.config['paths']['reports_root_dir'])
        ]
        
        for path in paths:
            FileUtils.create_directory(path)
    
    def reload_config(self) -> None:
        """重新加载配置"""
        self.config = self._load_config()
        self._initialize_paths()
    
    def get_config(self) -> Dict:
        """获取配置"""
        return self.config
    
    def update_config(self, updates: Dict) -> None:
        """更新配置"""
        def _update_recursive(config: Dict, updates: Dict):
            for key, value in updates.items():
                if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                    _update_recursive(config[key], value)
                else:
                    config[key] = value
        
        _update_recursive(self.config, updates)


# 全局配置实例
config_loader = ConfigLoader()