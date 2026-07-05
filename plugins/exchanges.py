"""交易所插件 - 提供K线数据"""

import random
from typing import Dict, Any, List
from agent_os.plugins import Plugin


class BinanceExchange(Plugin):
    name = "Binance"
    description = "Binance交易所K线数据"
    category = "exchange"
    
    def execute(self, config: Dict) -> Any:
        symbol = config.get('symbol', 'BTCUSDT')
        timeframe = config.get('timeframe', '4h')
        
        prices = [random.uniform(40000, 45000) for _ in range(20)]
        return {
            'exchange': 'Binance',
            'symbol': symbol,
            'timeframe': timeframe,
            'prices': prices,
            'current': prices[-1],
            'open': prices[0],
            'high': max(prices),
            'low': min(prices),
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'symbol': {'type': 'string', 'description': '交易对，如 BTCUSDT', 'default': 'BTCUSDT'},
            'timeframe': {'type': 'string', 'description': '时间周期', 'options': ['1m', '5m', '15m', '1h', '4h', '1d'], 'default': '4h'},
        }


class CoinGeckoExchange(Plugin):
    name = "CoinGecko"
    description = "CoinGecko加密货币数据"
    category = "exchange"
    
    def execute(self, config: Dict) -> Any:
        symbol = config.get('symbol', 'bitcoin')
        current_price = random.uniform(40000, 45000)
        return {
            'exchange': 'CoinGecko',
            'symbol': symbol,
            'current_price': current_price,
            'market_cap': current_price * 18000000,
            'volume_24h': current_price * 10000,
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'symbol': {'type': 'string', 'description': '币种名称', 'default': 'bitcoin'},
        }


class YahooFinanceExchange(Plugin):
    name = "YahooFinance"
    description = "Yahoo Finance股票数据"
    category = "exchange"
    
    def execute(self, config: Dict) -> Any:
        symbol = config.get('symbol', 'NVDA')
        prices = [random.uniform(400, 450) for _ in range(20)]
        return {
            'exchange': 'YahooFinance',
            'symbol': symbol,
            'prices': prices,
            'current': prices[-1],
            'open': prices[0],
            'high': max(prices),
            'low': min(prices),
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'symbol': {'type': 'string', 'description': '股票代码', 'default': 'NVDA'},
            'timeframe': {'type': 'string', 'description': '时间周期', 'options': ['1m', '5m', '15m', '1h', '4h', '1d'], 'default': '1d'},
        }


class FinvizExchange(Plugin):
    name = "Finviz"
    description = "Finviz股票基本面数据"
    category = "exchange"
    
    def execute(self, config: Dict) -> Any:
        symbol = config.get('symbol', 'AAPL')
        return {
            'exchange': 'Finviz',
            'symbol': symbol,
            'pe_ratio': random.uniform(15, 30),
            'eps': random.uniform(2, 10),
            'dividend': random.uniform(0, 3),
            'market_cap': random.uniform(100, 500) * 10**9,
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'symbol': {'type': 'string', 'description': '股票代码', 'default': 'AAPL'},
        }
