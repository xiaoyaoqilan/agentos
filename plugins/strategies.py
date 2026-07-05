"""策略插件 - 技术分析方法"""

import random
from typing import Dict, Any, List
from agent_os.plugins import Plugin


class BollingerBandStrategy(Plugin):
    name = "BollingerBand"
    description = "布林带策略：下轨做多，上轨看空"
    category = "strategy"
    
    def execute(self, config: Dict) -> Any:
        prices = config.get('prices', [])
        if not prices:
            prices = [random.uniform(40000, 45000) for _ in range(20)]
        
        avg = sum(prices) / len(prices)
        std = (sum((p - avg) ** 2 for p in prices) / len(prices)) ** 0.5
        upper = avg + 2 * std
        lower = avg - 2 * std
        current = prices[-1]
        
        if current < lower:
            signal = '做多'
        elif current > upper:
            signal = '看空'
        else:
            signal = '观望'
        
        return {
            'strategy': 'BollingerBand',
            'signal': signal,
            'current': round(current, 2),
            'upper': round(upper, 2),
            'lower': round(lower, 2),
            'middle': round(avg, 2),
            'prices': prices,
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'period': {'type': 'integer', 'description': '计算周期', 'default': 20},
            'std_multiplier': {'type': 'number', 'description': '标准差倍数', 'default': 2.0},
            'strategy_desc': {'type': 'string', 'description': '策略描述', 'default': '下轨做多，上轨看空'},
        }


class MACDStrategy(Plugin):
    name = "MACD"
    description = "MACD策略：金叉做多，死叉看空"
    category = "strategy"
    
    def execute(self, config: Dict) -> Any:
        prices = config.get('prices', [])
        if not prices:
            prices = [random.uniform(40000, 45000) for _ in range(30)]
        
        ema12 = self._ema(prices, 12)
        ema26 = self._ema(prices, 26)
        macd = [ema12[i] - ema26[i] for i in range(len(ema12))]
        signal = self._ema(macd, 9)
        
        last_macd = macd[-1]
        last_signal = signal[-1]
        
        if last_macd > last_signal and macd[-2] <= signal[-2]:
            signal_type = '金叉做多'
        elif last_macd < last_signal and macd[-2] >= signal[-2]:
            signal_type = '死叉看空'
        else:
            signal_type = '观望'
        
        return {
            'strategy': 'MACD',
            'signal': signal_type,
            'macd': round(last_macd, 2),
            'signal_line': round(last_signal, 2),
            'histogram': round(last_macd - last_signal, 2),
        }
    
    def _ema(self, prices: List[float], period: int) -> List[float]:
        ema = []
        multiplier = 2 / (period + 1)
        ema.append(prices[0])
        for i in range(1, len(prices)):
            ema.append(prices[i] * multiplier + ema[i-1] * (1 - multiplier))
        return ema
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'fast_period': {'type': 'integer', 'description': '快线周期', 'default': 12},
            'slow_period': {'type': 'integer', 'description': '慢线周期', 'default': 26},
            'signal_period': {'type': 'integer', 'description': '信号周期', 'default': 9},
        }


class RSIStrategy(Plugin):
    name = "RSI"
    description = "RSI策略：超卖做多，超买看空"
    category = "strategy"
    
    def execute(self, config: Dict) -> Any:
        prices = config.get('prices', [])
        if not prices:
            prices = [random.uniform(40000, 45000) for _ in range(20)]
        
        gains = []
        losses = []
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        avg_gain = sum(gains[-14:]) / 14 if len(gains) >= 14 else sum(gains) / len(gains)
        avg_loss = sum(losses[-14:]) / 14 if len(losses) >= 14 else sum(losses) / len(losses)
        
        if avg_loss == 0:
            rsi = 100
        else:
            rsi = 100 - (100 / (1 + avg_gain / avg_loss))
        
        if rsi < 30:
            signal = '超卖做多'
        elif rsi > 70:
            signal = '超买看空'
        else:
            signal = '观望'
        
        return {
            'strategy': 'RSI',
            'signal': signal,
            'rsi': round(rsi, 2),
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'period': {'type': 'integer', 'description': '计算周期', 'default': 14},
            'oversold': {'type': 'number', 'description': '超卖阈值', 'default': 30},
            'overbought': {'type': 'number', 'description': '超买阈值', 'default': 70},
        }


class SimpleHoldStrategy(Plugin):
    name = "SimpleHold"
    description = "简单持有策略：不做判断，只展示数据"
    category = "strategy"
    
    def execute(self, config: Dict) -> Any:
        prices = config.get('prices', [])
        current = prices[-1] if prices else 0
        return {
            'strategy': 'SimpleHold',
            'signal': '持有',
            'current_price': round(current, 2),
            'message': '当前策略：持有观望',
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {}
