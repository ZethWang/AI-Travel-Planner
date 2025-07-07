"""
API密钥配置管理模块
API Keys Configuration Management Module
"""

import os
from typing import Dict, List, Optional

def load_env_file(env_path: str = ".env") -> None:
    """
    手动加载.env文件中的环境变量
    
    Args:
        env_path: .env文件路径
    """
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
    except FileNotFoundError:
        print(f"⚠️ 环境变量文件 {env_path} 未找到，请确保已正确配置API密钥")
    except Exception as e:
        print(f"⚠️ 加载环境变量文件时出错: {e}")

# 初始化环境变量
load_env_file()

class APIKeyManager:
    """API密钥管理器"""
    
    def __init__(self):
        self.keys = {
            "searchapi_key": os.getenv("SEARCHAPI_API_KEY"),
            "openai_key": os.getenv("OPENAI_API_KEY"),
            "openai_key2": os.getenv("OPENAI_API_KEY2"),
            "google_key": os.getenv("GOOGLE_API_KEY"),
            "gemini_key": os.getenv("GEMINI_API_KEY"),
            "flights_key": os.getenv("FLIGHTS_API_KEY"),
            "hotels_key": os.getenv("HOTELS_API_KEY"),
            "maps_key": os.getenv("MAPS_API_KEY"),
        }
    
    def get_key(self, key_name: str) -> Optional[str]:
        """获取指定的API密钥"""
        return self.keys.get(key_name)
    
    def validate_keys(self, required_keys: List[str] = None) -> Dict:
        """
        验证必要的API密钥是否存在
        
        Args:
            required_keys: 必需的API密钥列表
            
        Returns:
            dict: 验证结果
        """
        if required_keys is None:
            required_keys = ["searchapi_key", "openai_key"]
        
        missing_keys = []
        for key in required_keys:
            if not self.keys.get(key):
                missing_keys.append(key)
        
        return {
            "valid": len(missing_keys) == 0,
            "missing_keys": missing_keys,
            "message": f"缺少API密钥: {', '.join(missing_keys)}" if missing_keys else "所有必需的API密钥已配置"
        }
    
    def set_environment_variables(self) -> None:
        """将API密钥设置为环境变量"""
        for key, value in self.keys.items():
            if value:
                env_key = key.upper().replace("_KEY", "_API_KEY")
                os.environ[env_key] = value

# 创建全局API密钥管理器实例
api_manager = APIKeyManager()

# 导出常用配置
API_CONFIG = api_manager.keys

def get_api_key(key_name: str) -> Optional[str]:
    """便捷函数：获取API密钥"""
    return api_manager.get_key(key_name)

def validate_api_setup(required_keys: List[str] = None) -> Dict:
    """便捷函数：验证API设置"""
    return api_manager.validate_keys(required_keys)
