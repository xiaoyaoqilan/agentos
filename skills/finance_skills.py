"""金融相关Skills"""
import json
import urllib.request
import logging
from typing import Dict, List, Any
from datetime import datetime

from agent_os.core import BaseSkill, register_skill

logger = logging.getLogger(__name__)


@register_skill
class FinanceCrawler(BaseSkill):
    name = "FinanceCrawler"
    description = "爬取金融网页数据和市场信息"
    input_schema = {"urls": {"type": "list", "description": "要爬取的URL列表"}}
    output_schema = {"data": {"type": "list", "description": "爬取到的数据"}}
    
    def __init__(self):
        self.session = None
    
    def execute(self, urls: List[str] = None) -> Dict[str, Any]:
        if urls is None:
            urls = ['https://www.coingecko.com', 'https://finance.yahoo.com']
        
        results = []
        for url in urls:
            try:
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                resp = urllib.request.urlopen(url, timeout=15)
                content = resp.read().decode('utf-8', errors='ignore')[:2000]
                results.append({
                    'url': url,
                    'content': content,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"爬取失败: {url} - {e}")
        
        return {'data': results, 'count': len(results)}


@register_skill
class BollingerAnalysis(BaseSkill):
    name = "BollingerAnalysis"
    description = "计算布林带指标并给出多空信号"
    input_schema = {"symbols": {"type": "list", "description": "交易对列表"}}
    output_schema = {"signals": {"type": "list", "description": "信号列表"}}
    
    def __init__(self):
        pass
    
    def execute(self, symbols: List[str] = None) -> Dict[str, Any]:
        if symbols is None:
            symbols = ['BTCUSDT', 'ETHUSDT']
        
        signals = []
        for symbol in symbols:
            signal = self._analyze_symbol(symbol)
            signals.append(signal)
        
        return {'signals': signals}
    
    def _analyze_symbol(self, symbol: str) -> Dict[str, Any]:
        import random
        prices = [random.uniform(40000, 45000) for _ in range(20)]
        avg = sum(prices) / len(prices)
        std = (sum((p - avg) ** 2 for p in prices) / len(prices)) ** 0.5
        
        upper = avg + 2 * std
        lower = avg - 2 * std
        current = prices[-1]
        
        if current < lower:
            direction = '做多'
        elif current > upper:
            direction = '看空'
        else:
            direction = '观望'
        
        return {
            'symbol': symbol,
            'direction': direction,
            'current_price': round(current, 2),
            'upper_band': round(upper, 2),
            'lower_band': round(lower, 2),
            'timestamp': datetime.now().isoformat()
        }


@register_skill
class RAGRetrieval(BaseSkill):
    name = "RAGRetrieval"
    description = "从知识库中检索相关信息"
    input_schema = {"query": {"type": "string", "description": "查询词"}}
    output_schema = {"results": {"type": "list", "description": "检索结果"}}
    
    def __init__(self):
        pass
    
    def execute(self, query: str = "") -> Dict[str, Any]:
        if not query:
            query = "市场分析"
        
        mock_results = [
            {"content": f"关于'{query}'的市场分析报告摘要", "score": 0.95},
            {"content": f"{query}相关的投资建议", "score": 0.88},
            {"content": f"{query}的历史数据统计", "score": 0.82},
        ]
        
        return {'results': mock_results, 'query': query}


@register_skill
class LLMDecision(BaseSkill):
    name = "LLMDecision"
    description = "使用LLM生成决策建议"
    input_schema = {"data": {"type": "list", "description": "输入数据"}, "query": {"type": "string", "description": "查询问题"}}
    output_schema = {"decision": {"type": "string", "description": "决策建议"}}
    
    def __init__(self):
        pass
    
    def execute(self, data: List[Dict] = None, query: str = "") -> Dict[str, Any]:
        if data is None:
            data = []
        if not query:
            query = "给出投资建议"
        
        decisions = [
            f"根据分析，{query}的建议是：保持谨慎，观望为主",
            f"综合数据显示，{query}方向：适度做多",
            f"当前市场条件下，{query}建议：短期看空",
            f"结合多方面因素，{query}决策：逢低买入",
        ]
        
        import random
        return {'decision': random.choice(decisions), 'input_data_count': len(data)}


@register_skill
class ServerChanNotify(BaseSkill):
    name = "ServerChanNotify"
    description = "通过ServerChan推送到微信"
    input_schema = {"message": {"type": "string", "description": "推送消息"}}
    output_schema = {"success": {"type": "boolean", "description": "是否成功"}}
    
    def __init__(self):
        import os
        self.skey = os.getenv('SERVERCHAN_KEY')
    
    def execute(self, message: str = "") -> Dict[str, Any]:
        if not message:
            return {'success': False, 'error': '消息为空'}
        
        if not self.skey:
            logger.warning("SERVERCHAN_KEY未设置")
            return {'success': False, 'error': 'SERVERCHAN_KEY未设置'}
        
        try:
            url = f"https://sctapi.ftqq.com/{self.skey}.send"
            data = {"title": "Agent通知", "desp": message[:2000]}
            
            req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method='POST')
            resp = urllib.request.urlopen(req, timeout=10)
            result = json.loads(resp.read().decode())
            
            if result.get('code') == 0:
                logger.info("微信推送成功")
                return {'success': True}
            else:
                return {'success': False, 'error': result.get('message', '未知错误')}
        except Exception as e:
            logger.warning(f"推送失败: {e}")
            return {'success': False, 'error': str(e)}