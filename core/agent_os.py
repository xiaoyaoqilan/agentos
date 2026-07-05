"""Agent OS 内核 - 纯调度引擎，不含业务逻辑"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import yaml
from agent_os.config import load_config
from agent_os.plugins import plugin_manager

logger = logging.getLogger(__name__)


class AgentOS:
    """Agent OS 内核"""
    
    def __init__(self):
        self.config = load_config()
        self.strategy = self._load_strategy()
        self.rag_memory = []
        self.shared_context = {}
    
    def _load_strategy(self) -> Dict:
        strategy_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'strategy.yaml')
        if os.path.exists(strategy_file):
            with open(strategy_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def list_plugins(self, category: str = None) -> Dict[str, Any]:
        """列出所有可用插件"""
        if category:
            return plugin_manager.list_by_category(category)
        return plugin_manager.list_all()
    
    def identify_domain(self, user_intent: str) -> str:
        """识别用户意图所属领域"""
        prompt_lower = user_intent.lower()
        
        if any(k in prompt_lower for k in ['金融', '股票', '投资', '加密货币', '市场', '交易所']):
            return '金融'
        if any(k in prompt_lower for k in ['搞笑', '梗图', '表情包', '热点', '段子']):
            return '热点'
        if any(k in prompt_lower for k in ['电商', '优惠', '购物', '京东', '淘宝']):
            return '电商'
        if any(k in prompt_lower for k in ['科技', '技术', 'IT', '互联网']):
            return '科技'
        if any(k in prompt_lower for k in ['新闻', '资讯', '头条']):
            return '新闻'
        
        return '通用'
    
    def get_domain_strategy(self, domain: str) -> Dict:
        """获取领域策略配置"""
        my_strategy = self.strategy.get('my_strategy', {})
        domain_strategy = my_strategy.get(domain, {})
        steps = domain_strategy.get('steps', [])
        
        if not steps:
            steps = [
                {'plugin': 'DeepSeek', 'config': {'prompt': f'分析{domain}相关信息'}}
            ]
        
        return {
            'name': domain_strategy.get('name', '默认策略'),
            'steps': steps,
        }
    
    def execute_step(self, step: Dict, context: Dict) -> Any:
        """执行单个步骤"""
        plugin_name = step.get('plugin', '')
        config = step.get('config', {})
        
        plugin = plugin_manager.get(plugin_name)
        if not plugin:
            return {
                'success': False,
                'error': f'插件不存在: {plugin_name}',
                'available_plugins': list(plugin_manager.list_all().keys()),
            }
        
        merged_config = {**config}
        
        if 'prices' in context:
            merged_config['prices'] = context['prices']
        if 'current_price' in context:
            merged_config['current_price'] = context['current_price']
        if 'api_key' not in merged_config and self.config['api_keys'].get('deepseek'):
            merged_config['api_key'] = self.config['api_keys']['deepseek']
        if 'skey' not in merged_config and self.config['api_keys'].get('serverchan'):
            merged_config['skey'] = self.config['api_keys']['serverchan']
        
        try:
            result = plugin.execute(merged_config)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def update_context(self, context: Dict, result: Any) -> Dict:
        """从执行结果更新上下文"""
        if isinstance(result, dict):
            if 'prices' in result:
                context['prices'] = result['prices']
            if 'current' in result:
                context['current_price'] = result['current']
            if 'signal' in result:
                context['signal'] = result['signal']
            if 'response' in result:
                context['llm_response'] = result['response']
            if 'topic' in result:
                context['meme_topic'] = result['topic']
            if 'copy' in result:
                context['meme_copy'] = result['copy']
            if 'image_url' in result:
                context['meme_image'] = result['image_url']
            if 'polished' in result:
                context['meme_copy'] = result['polished']
        
        return context
    
    def write_rag(self, content: str) -> None:
        """写入RAG记忆"""
        self.rag_memory.append({
            'timestamp': datetime.now().isoformat(),
            'content': content
        })
        if len(self.rag_memory) > 50:
            self.rag_memory = self.rag_memory[-50:]
    
    def read_rag(self) -> str:
        """读取RAG记忆"""
        return "\n".join([f"[{m['timestamp']}] {m['content']}" for m in self.rag_memory[-10:]])
    
    def run(self, user_intent: str) -> str:
        """主入口：你说一句话，系统按策略执行"""
        logger.info(f"用户意图: {user_intent}")
        self.write_rag(f"用户意图: {user_intent}")
        
        print(f"\n{'='*50}")
        print(f"你说: {user_intent}")
        print(f"{'='*50}")
        
        domain = self.identify_domain(user_intent)
        print(f"\n🎯 识别领域: {domain}")
        self.write_rag(f"识别领域: {domain}")
        
        strategy = self.get_domain_strategy(domain)
        steps = strategy['steps']
        
        print(f"\n📋 策略流程 ({strategy['name']}):")
        for i, step in enumerate(steps, 1):
            plugin_name = step.get('plugin', '')
            plugin = plugin_manager.get(plugin_name)
            desc = plugin.description if plugin else '未知'
            print(f"   {i}. {plugin_name} - {desc}")
        
        context = {}
        all_results = []
        
        for i, step in enumerate(steps, 1):
            plugin_name = step.get('plugin', '')
            plugin = plugin_manager.get(plugin_name)
            desc = plugin.description if plugin else '未知'
            
            print(f"\n{'━'*40}")
            print(f"步骤 {i}: {plugin_name}")
            print(f"描述: {desc}")
            print(f"{'━'*40}")
            
            result = self.execute_step(step, context)
            context = self.update_context(context, result)
            
            if isinstance(result, dict) and result.get('success', True):
                if 'message' in result:
                    print(result['message'])
                elif 'response' in result:
                    print(result['response'])
                elif 'signal' in result:
                    print(f"信号: {result['signal']}")
                    print(f"当前: {result.get('current', '-')}")
                    print(f"上轨: {result.get('upper', '-')}")
                    print(f"下轨: {result.get('lower', '-')}")
                elif 'topic' in result:
                    print(f"主题: {result['topic']}")
                    print(f"文案: {result.get('copy', '')}")
                    print(f"图片: {result.get('image_url', '')}")
                elif 'polished' in result:
                    print(f"原文: {result.get('original', '')}")
                    print(f"润色后: {result['polished']}")
                else:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                
                all_results.append(f"[{plugin_name}] {json.dumps(result, ensure_ascii=False)[:200]}")
            else:
                print(f"❌ 执行失败: {result.get('error', '未知错误')}")
        
        final_result = f"\n✅ {domain}处理完成！"
        if context.get('meme_topic'):
            final_result += f"\n主题: {context['meme_topic']}\n文案: {context['meme_copy']}"
        
        return final_result


agent_os = AgentOS()
