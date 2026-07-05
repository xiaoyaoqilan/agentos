"""ToolRegistry - Skill注册中心"""
import logging
from typing import Dict, Type, Any, List, Callable
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseSkill(ABC):
    """所有Skill的基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Skill名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Skill描述"""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """输入参数schema"""
        pass
    
    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        """输出参数schema"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行Skill"""
        pass


class ToolRegistry:
    """Skill注册中心 - 管理所有可用的Skills"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.skills: Dict[str, Type[BaseSkill]] = {}
        return cls._instance
    
    def register(self, skill_class: Type[BaseSkill]) -> None:
        """注册一个Skill"""
        skill_name = skill_class.name
        if skill_name in self.skills:
            logger.warning(f"Skill已存在: {skill_name}")
            return
        self.skills[skill_name] = skill_class
        logger.info(f"注册Skill: {skill_name}")
    
    def unregister(self, skill_name: str) -> None:
        """注销一个Skill"""
        if skill_name in self.skills:
            del self.skills[skill_name]
            logger.info(f"注销Skill: {skill_name}")
    
    def get_skill(self, skill_name: str) -> Type[BaseSkill]:
        """获取Skill类"""
        return self.skills.get(skill_name)
    
    def get_all_skills(self) -> List[str]:
        """获取所有注册的Skill名称"""
        return list(self.skills.keys())
    
    def get_skill_info(self, skill_name: str) -> Dict[str, Any]:
        """获取Skill详细信息"""
        skill_class = self.skills.get(skill_name)
        if not skill_class:
            return None
        
        return {
            'name': skill_class.name,
            'description': skill_class.description,
            'input_schema': skill_class.input_schema,
            'output_schema': skill_class.output_schema
        }
    
    def create_skill_instance(self, skill_name: str, **kwargs) -> BaseSkill:
        """创建Skill实例"""
        skill_class = self.get_skill(skill_name)
        if not skill_class:
            raise ValueError(f"Skill不存在: {skill_name}")
        return skill_class(**kwargs)
    
    def execute_skill(self, skill_name: str, **kwargs) -> Dict[str, Any]:
        """直接执行Skill"""
        skill = self.create_skill_instance(skill_name)
        return skill.execute(**kwargs)
    
    def find_matching_skills(self, query: str) -> List[str]:
        """根据查询词匹配Skills"""
        query_lower = query.lower()
        matched = []
        for name, skill_class in self.skills.items():
            if query_lower in name.lower() or query_lower in skill_class.description.lower():
                matched.append(name)
        return matched


registry = ToolRegistry()


def register_skill(skill_class: Type[BaseSkill]) -> Type[BaseSkill]:
    """装饰器：注册Skill"""
    registry.register(skill_class)
    return skill_class