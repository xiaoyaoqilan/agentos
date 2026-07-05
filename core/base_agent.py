"""BaseAgent - Agent OS核心抽象类"""
import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """所有Agent的基类，定义生命周期方法"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'Untitled Agent')
        self.description = config.get('description', '')
        self.skills = []
        self.scheduled_tasks = []
        self.results = {}
        logger.info(f"初始化Agent: {self.name}")
    
    @abstractmethod
    def register_tools(self) -> None:
        """注册需要的工具/Skills"""
        pass
    
    @abstractmethod
    def run_pipeline(self, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行主管道流程"""
        pass
    
    @abstractmethod
    def notify(self, result: Dict[str, Any]) -> None:
        """通知推送结果"""
        pass
    
    def schedule(self, cron_expr: str, task_func) -> None:
        """注册定时任务"""
        self.scheduled_tasks.append({
            'cron': cron_expr,
            'task': task_func
        })
        logger.info(f"注册定时任务: {cron_expr}")
    
    def save_result(self, key: str, value: Any) -> None:
        """保存执行结果"""
        self.results[key] = value
    
    def get_result(self, key: str) -> Any:
        """获取执行结果"""
        return self.results.get(key)
    
    def execute(self, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行完整生命周期"""
        logger.info(f"{'='*50}")
        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行Agent: {self.name}")
        logger.info(f"{'='*50}")
        
        try:
            self.register_tools()
            
            result = self.run_pipeline(input_data)
            
            self.notify(result)
            
            logger.info(f"✅ Agent执行完成: {self.name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Agent执行失败: {e}")
            return {'error': str(e), 'success': False}


class AgentConfig:
    """Agent配置类"""
    
    def __init__(self, name: str, description: str, skills: List[str], 
                 schedule: Optional[str] = None, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.skills = skills
        self.schedule = schedule
        self.params = params or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'skills': self.skills,
            'schedule': self.schedule,
            'params': self.params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            skills=data.get('skills', []),
            schedule=data.get('schedule'),
            params=data.get('params', {})
        )
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)