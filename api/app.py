"""Agent OS统一API入口"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AgentOSAPI:
    """Agent OS API接口"""
    
    def __init__(self):
        from agent_os.core import factory, registry, scheduler
        
        self.factory = factory
        self.registry = registry
        self.scheduler = scheduler
    
    def create_agent(self, description: str) -> Dict[str, Any]:
        """根据描述创建Agent"""
        try:
            agent = self.factory.create_agent(description)
            return {
                'success': True,
                'name': agent.name,
                'description': agent.description,
                'skills': agent.skills,
                'schedule': agent.config.get('schedule'),
                'message': f"Agent '{agent.name}' 创建成功"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_skills(self) -> Dict[str, Any]:
        """列出所有可用Skills"""
        skills = self.registry.get_all_skills()
        skill_info = []
        for skill_name in skills:
            info = self.registry.get_skill_info(skill_name)
            if info:
                skill_info.append(info)
        return {'skills': skill_info, 'count': len(skill_info)}
    
    def execute_agent(self, description: str) -> Dict[str, Any]:
        """创建并执行Agent"""
        try:
            agent = self.factory.create_agent(description)
            result = agent.execute()
            return {
                'success': True,
                'agent_name': agent.name,
                'result': result
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_scheduled_task(self, name: str, cron_expr: str, description: str) -> Dict[str, Any]:
        """添加定时任务"""
        try:
            agent = self.factory.create_agent(description)
            self.scheduler.add_task(name, cron_expr, agent.execute)
            return {'success': True, 'message': f"定时任务 '{name}' 添加成功"}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def start_scheduler(self) -> Dict[str, Any]:
        """启动调度器"""
        try:
            self.scheduler.start()
            return {'success': True, 'message': '调度器已启动'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def stop_scheduler(self) -> Dict[str, Any]:
        """停止调度器"""
        try:
            self.scheduler.stop()
            return {'success': True, 'message': '调度器已停止'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


api = AgentOSAPI()