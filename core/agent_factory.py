"""AgentFactory - Agent工厂，LLM自动组装Skills"""
import os
import json
import logging
import urllib.request
from typing import Dict, List, Any, Optional

from .tool_registry import registry
from .base_agent import AgentConfig

logger = logging.getLogger(__name__)


class AgentFactory:
    """Agent工厂 - 根据用户描述自动创建Agent"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def analyze_requirement(self, description: str) -> Dict[str, Any]:
        """分析用户需求，返回Agent配置"""
        if self.api_key:
            return self._analyze_with_llm(description)
        else:
            return self._analyze_with_rules(description)
    
    def _analyze_with_llm(self, description: str) -> Dict[str, Any]:
        """使用LLM分析需求"""
        available_skills = registry.get_all_skills()
        if not available_skills:
            return self._analyze_with_rules(description)
        
        skill_info = []
        for skill_name in available_skills:
            info = registry.get_skill_info(skill_name)
            if info:
                skill_info.append(info)
        
        prompt = f"""你是一个Agent配置专家。根据用户的一句话描述，从可用Skills中选择合适的组合来创建一个Agent。

可用Skills:
{json.dumps(skill_info, ensure_ascii=False, indent=2)}

用户描述: {description}

请输出JSON格式的Agent配置，包含:
1. name: Agent名称
2. description: 简短描述
3. skills: 选中的Skill名称列表（从可用Skills中选择）
4. schedule: 定时任务表达式（如 "0 9 * * *" 每天9点，或留空）
5. params: 各Skill的参数配置

请只输出JSON，不要加任何解释。"""

        try:
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(self.base_url, data=data, headers=headers, method='POST')
            resp = urllib.request.urlopen(req, timeout=30)
            result = json.loads(resp.read().decode('utf-8'))
            
            config = json.loads(result['choices'][0]['message']['content'].strip())
            logger.info(f"LLM分析完成: {config.get('name')}")
            return config
            
        except Exception as e:
            logger.warning(f"LLM分析失败，使用规则匹配: {e}")
            return self._analyze_with_rules(description)
    
    def _analyze_with_rules(self, description: str) -> Dict[str, Any]:
        """使用规则匹配分析需求"""
        desc_lower = description.lower()
        
        if any(keyword in desc_lower for keyword in ['金融', '股票', '投资', '加密货币', 'crypto', 'bollinger']):
            return {
                'name': '金融信号Agent',
                'description': '每日金融信号分析和推送',
                'skills': ['FinanceCrawler', 'BollingerAnalysis', 'RAGRetrieval', 'LLMDecision', 'ServerChanNotify'],
                'schedule': '0 9 * * *',
                'params': {
                    'symbols': ['BTCUSDT', 'ETHUSDT', 'NVDA', 'AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN', 'TSLA']
                }
            }
        
        if any(keyword in desc_lower for keyword in ['搞笑', '表情包', '梗图', '热点', '段子', 'meme']):
            return {
                'name': '梗图收集Agent',
                'description': '自动收集热点梗图和生成文案',
                'skills': ['HotCrawler', 'MemeSearch', 'Copywriter', 'DraftPoster'],
                'schedule': '*/30 * * * *',
                'params': {}
            }
        
        if any(keyword in desc_lower for keyword in ['爬虫', '抓取', 'crawl']):
            return {
                'name': '内容爬虫Agent',
                'description': '网页内容爬虫',
                'skills': ['FinanceCrawler', 'HotCrawler'],
                'schedule': None,
                'params': {}
            }
        
        if any(keyword in desc_lower for keyword in ['通知', '推送', '微信', 'email']):
            return {
                'name': '通知推送Agent',
                'description': '消息推送服务',
                'skills': ['ServerChanNotify'],
                'schedule': None,
                'params': {}
            }
        
        return {
            'name': '通用Agent',
            'description': description,
            'skills': [],
            'schedule': None,
            'params': {}
        }
    
    def create_agent_config(self, description: str) -> AgentConfig:
        """创建Agent配置对象"""
        config_dict = self.analyze_requirement(description)
        return AgentConfig.from_dict(config_dict)
    
    def create_agent(self, description: str) -> 'BaseAgent':
        """创建Agent实例"""
        config = self.create_agent_config(description)
        return self._build_agent(config)
    
    def _build_agent(self, config: AgentConfig) -> 'BaseAgent':
        """根据配置构建Agent"""
        from .base_agent import BaseAgent
        
        class DynamicAgent(BaseAgent):
            def __init__(self, config_dict):
                super().__init__(config_dict)
                self.skill_instances = {}
            
            def register_tools(self):
                for skill_name in self.config.get('skills', []):
                    try:
                        skill = registry.create_skill_instance(skill_name)
                        self.skill_instances[skill_name] = skill
                        self.skills.append(skill_name)
                        logger.info(f"注册Skill: {skill_name}")
                    except Exception as e:
                        logger.warning(f"注册Skill失败: {skill_name} - {e}")
            
            def run_pipeline(self, input_data=None):
                result = {}
                params = self.config.get('params', {})
                
                for skill_name in self.skills:
                    skill = self.skill_instances.get(skill_name)
                    if skill:
                        try:
                            skill_params = params.get(skill_name, {})
                            skill_result = skill.execute(**skill_params)
                            result[skill_name] = skill_result
                            logger.info(f"执行Skill完成: {skill_name}")
                        except Exception as e:
                            logger.error(f"执行Skill失败: {skill_name} - {e}")
                            result[skill_name] = {'error': str(e)}
                
                return result
            
            def notify(self, result):
                if 'ServerChanNotify' in self.skill_instances:
                    self.skill_instances['ServerChanNotify'].execute(message=str(result))
        
        return DynamicAgent(config.to_dict())


factory = AgentFactory()