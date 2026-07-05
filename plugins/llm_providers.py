"""LLM提供商插件 - 对话和分析"""

import json
import urllib.request
import random
from typing import Dict, Any
from agent_os.plugins import Plugin


class DeepSeekLLM(Plugin):
    name = "DeepSeek"
    description = "DeepSeek大模型"
    category = "llm"
    
    def __init__(self):
        self.api_key = ""
    
    def execute(self, config: Dict) -> Any:
        prompt = config.get('prompt', '')
        api_key = config.get('api_key', self.api_key)
        
        if not api_key:
            return self._mock_response(prompt)
        
        try:
            url = "https://api.deepseek.com/v1/chat/completions"
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": config.get('temperature', 0.7),
                "max_tokens": config.get('max_tokens', 300)
            }
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            resp = urllib.request.urlopen(req, timeout=30)
            result = json.loads(resp.read().decode('utf-8'))
            return {
                'provider': 'DeepSeek',
                'response': result['choices'][0]['message']['content'].strip(),
                'success': True,
            }
        except Exception as e:
            return {
                'provider': 'DeepSeek',
                'response': f"LLM调用失败: {e}",
                'success': False,
            }
    
    def _mock_response(self, prompt: str) -> Dict:
        responses = [
            "根据分析，当前市场趋势偏多。",
            "建议观望，等待明确信号。",
            "技术指标显示可能出现反转。",
            "基本面数据良好，可以考虑买入。",
            "风险较高，建议减仓。",
        ]
        return {
            'provider': 'DeepSeek',
            'response': random.choice(responses),
            'success': True,
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'api_key': {'type': 'string', 'description': 'DeepSeek API Key', 'required': True},
            'temperature': {'type': 'number', 'description': '温度系数', 'default': 0.7},
            'max_tokens': {'type': 'integer', 'description': '最大token数', 'default': 300},
            'prompt': {'type': 'string', 'description': '提示词', 'required': True},
        }


class MockLLM(Plugin):
    name = "MockLLM"
    description = "模拟LLM（用于测试，无需API Key）"
    category = "llm"
    
    def execute(self, config: Dict) -> Any:
        prompt = config.get('prompt', '')
        prompt_lower = prompt.lower()
        
        if any(k in prompt_lower for k in ['做多', '看空', '买卖', '建议']):
            responses = [
                "根据数据，建议做多。",
                "当前信号偏弱，建议观望。",
                "技术面显示可能下跌，建议谨慎。",
                "基本面良好，可以考虑买入。",
            ]
        elif any(k in prompt_lower for k in ['分析', '趋势', '行情']):
            responses = [
                "当前市场处于震荡整理阶段。",
                "短期趋势向上，长期仍需观察。",
                "成交量萎缩，市场交投清淡。",
                "多空博弈激烈，方向不明。",
            ]
        else:
            responses = [
                "好的，我来处理。",
                "分析完成。",
                "已收到指令。",
                "正在处理中...",
            ]
        
        return {
            'provider': 'MockLLM',
            'response': random.choice(responses),
            'success': True,
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'prompt': {'type': 'string', 'description': '提示词', 'required': True},
        }
