"""插件系统 - 所有业务逻辑都在这里"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class Plugin(ABC):
    """插件基类"""
    name: str = ""
    description: str = ""
    category: str = ""
    
    @abstractmethod
    def execute(self, config: Dict) -> Any:
        pass
    
    def get_params(self) -> Dict[str, Dict]:
        """返回参数定义"""
        return {}


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """自动加载所有插件"""
        plugins_dir = os.path.dirname(__file__)
        for filename in os.listdir(plugins_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    module = __import__(f'agent_os.plugins.{module_name}', fromlist=[''])
                    for attr in dir(module):
                        obj = getattr(module, attr)
                        if isinstance(obj, type) and issubclass(obj, Plugin) and obj != Plugin:
                            instance = obj()
                            self.plugins[instance.name] = instance
                except Exception as e:
                    print(f"加载插件失败 {module_name}: {e}")
    
    def get(self, name: str) -> Optional[Plugin]:
        return self.plugins.get(name)
    
    def list_by_category(self, category: str) -> Dict[str, Plugin]:
        return {k: v for k, v in self.plugins.items() if v.category == category}
    
    def list_all(self) -> Dict[str, Plugin]:
        return self.plugins


plugin_manager = PluginManager()
