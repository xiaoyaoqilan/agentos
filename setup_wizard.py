"""Agent OS 配置向导 - 首次运行时引导用户配置"""

import os
import yaml
import json


def print_header():
    print("\n" + "="*60)
    print("          Agent OS - 配置向导")
    print("="*60)


def ask_choice(prompt: str, options: list) -> int:
    """让用户选择选项"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            choice = int(input(f"\n请输入序号 (1-{len(options)}): "))
            if 1 <= choice <= len(options):
                return choice
            print(f"请输入 1-{len(options)} 之间的数字")
        except ValueError:
            print("请输入数字")


def ask_string(prompt: str, default: str = "", required: bool = False) -> str:
    """让用户输入字符串"""
    while True:
        value = input(f"\n{prompt}")
        if value.strip():
            return value.strip()
        elif default:
            print(f"使用默认值: {default}")
            return default
        elif not required:
            return ""
        else:
            print("此项必填，请输入")


def ask_bool(prompt: str, default: bool = True) -> bool:
    """让用户确认是/否"""
    while True:
        value = input(f"\n{prompt} (y/n): ").lower()
        if value in ['y', 'yes', '是']:
            return True
        elif value in ['n', 'no', '否']:
            return False
        elif value == "":
            return default
        else:
            print("请输入 y/n")


def run_wizard():
    """运行配置向导"""
    print_header()
    print("首次运行，引导你配置系统\n")
    
    config = {
        'api_keys': {},
        'settings': {},
        'strategy': {},
    }
    
    print("="*60)
    print("1. 选择交易所数据源")
    print("="*60)
    
    exchanges = [
        ("Binance", "Binance交易所，适合加密货币"),
        ("CoinGecko", "CoinGecko，加密货币数据"),
        ("YahooFinance", "Yahoo Finance，股票数据"),
        ("Finviz", "Finviz，股票基本面"),
    ]
    
    exchange_idx = ask_choice("你想用哪个交易所的数据源？", [f"{e[0]} - {e[1]}" for e in exchanges])
    config['strategy']['exchange'] = exchanges[exchange_idx-1][0]
    
    print("\n" + "="*60)
    print("2. 选择技术分析策略")
    print("="*60)
    
    strategies = [
        ("BollingerBand", "布林带：下轨做多，上轨看空"),
        ("MACD", "MACD：金叉做多，死叉看空"),
        ("RSI", "RSI：超卖做多，超买看空"),
        ("SimpleHold", "简单持有：不做判断"),
    ]
    
    strategy_idx = ask_choice("你想用哪个技术分析策略？", [f"{s[0]} - {s[1]}" for s in strategies])
    config['strategy']['analysis'] = strategies[strategy_idx-1][0]
    
    print("\n" + "="*60)
    print("3. 选择大模型")
    print("="*60)
    
    llms = [
        ("DeepSeek", "DeepSeek大模型（需要API Key）"),
        ("MockLLM", "模拟LLM（无需API Key，用于测试）"),
    ]
    
    llm_idx = ask_choice("你想用哪个大模型？", [f"{l[0]} - {l[1]}" for l in llms])
    config['strategy']['llm'] = llms[llm_idx-1][0]
    
    if config['strategy']['llm'] == 'DeepSeek':
        api_key = ask_string("请输入 DeepSeek API Key: ", required=False)
        config['api_keys']['deepseek'] = api_key
    
    print("\n" + "="*60)
    print("4. 配置推送方式")
    print("="*60)
    
    push_wechat = ask_bool("是否推送微信？")
    config['settings']['push_wechat'] = push_wechat
    
    if push_wechat:
        skey = ask_string("请输入 ServerChan Key: ", required=False)
        config['api_keys']['serverchan'] = skey
    
    print("\n" + "="*60)
    print("5. 配置交易对")
    print("="*60)
    
    symbols = ask_string("请输入交易对（多个用逗号分隔）: ", "BTCUSDT,ETHUSDT,NVDA,AAPL")
    config['strategy']['symbols'] = [s.strip() for s in symbols.split(',')]
    
    print("\n" + "="*60)
    print("6. 配置时间周期")
    print("="*60)
    
    timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
    tf_idx = ask_choice("选择K线时间周期", timeframes)
    config['strategy']['timeframe'] = timeframes[tf_idx-1]
    
    print("\n" + "="*60)
    print("配置完成！")
    print("="*60)
    
    print("\n你的配置：")
    print(f"  交易所: {config['strategy']['exchange']}")
    print(f"  策略: {config['strategy']['analysis']}")
    print(f"  大模型: {config['strategy']['llm']}")
    print(f"  交易对: {', '.join(config['strategy']['symbols'])}")
    print(f"  时间周期: {config['strategy']['timeframe']}")
    print(f"  推送微信: {'是' if config['settings']['push_wechat'] else '否'}")
    
    confirm = ask_bool("\n确认保存配置？", True)
    if confirm:
        save_config(config)
        print("\n✅ 配置已保存！")
        print("现在运行 `python demo.py` 即可使用")
    else:
        print("\n配置已取消")


def save_config(config: dict):
    """保存配置到文件"""
    agent_os_dir = os.path.dirname(__file__)
    
    env_content = f"""# Agent OS 配置文件
# 由配置向导生成

# 交易所
EXCHANGE={config['strategy']['exchange']}
STRATEGY={config['strategy']['analysis']}
LLM={config['strategy']['llm']}
SYMBOLS={','.join(config['strategy']['symbols'])}
TIMEFRAME={config['strategy']['timeframe']}

# API Keys
API_DEEPSEEK={config['api_keys'].get('deepseek', '')}
API_SERVERCHAN={config['api_keys'].get('serverchan', '')}

# 设置
PUSH_TO_WECHAT={str(config['settings']['push_wechat']).lower()}
"""
    
    with open(os.path.join(agent_os_dir, '.env'), 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    strategy_yaml = f"""# Agent OS 策略配置文件
# 由配置向导生成

my_strategy:
  name: "我的策略"
  
  金融:
    steps:
      - plugin: {config['strategy']['exchange']}
        config:
          symbol: {config['strategy']['symbols'][0]}
          timeframe: {config['strategy']['timeframe']}
      - plugin: {config['strategy']['analysis']}
        config: {}
      - plugin: {config['strategy']['llm']}
        config:
          prompt: "根据分析结果，给出明确的买卖建议"
      - plugin: ServerChanPush
        config: {{}}
  
  热点:
    steps:
      - plugin: MemeGenerator
        config:
          style: "搞笑"
      - plugin: Polisher
        config:
          style: "幽默"
      - plugin: SaveDraft
        config:
          platforms: ["微信", "微博", "抖音"]
  
  电商:
    steps:
      - plugin: {config['strategy']['llm']}
        config:
          prompt: "分析今天的电商优惠信息"
  
  科技:
    steps:
      - plugin: {config['strategy']['llm']}
        config:
          prompt: "汇总今天的科技新闻"
  
  新闻:
    steps:
      - plugin: {config['strategy']['llm']}
        config:
          prompt: "汇总今天的重要新闻"
"""
    
    with open(os.path.join(agent_os_dir, 'strategy.yaml'), 'w', encoding='utf-8') as f:
        f.write(strategy_yaml)


if __name__ == '__main__':
    run_wizard()
