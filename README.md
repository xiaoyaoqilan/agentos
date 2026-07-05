# Agent OS - 通用Agent操作系统

> **像安卓/Linux一样，你在上面做开发**
> 
> 内核是通用的，插件是可扩展的，策略是你定义的。

---

## 🚀 三步上手

### 第一步：安装依赖
```bash
pip install -r requirements.txt
```

### 第二步：配置系统（交互式）
```bash
python setup_wizard.py
```

系统会问你：
1. 你想用哪个交易所？（Binance/CoinGecko/YahooFinance/Finviz）
2. 你想用哪个策略？（布林带/MACD/RSI）
3. 你想用哪个大模型？（DeepSeek/MockLLM）
4. 是否推送微信？
5. 交易对是什么？
6. 时间周期是多少？

### 第三步：开始使用
```bash
python demo.py
```

---

## 🏗️ 架构设计

```
┌────────────────────────────────────────────────────────┐
│                    Agent OS 内核                        │
│  - 意图识别     - 插件调度     - RAG记忆     - 执行管道   │
│  (零业务逻辑，纯调度)                                    │
└──────────────────┬─────────────────────────────────────┘
                   │ 插件接口
┌──────────────────▼─────────────────────────────────────┐
│                     插件层                              │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────┐ │
│  │交易所插件  │ │策略插件    │ │LLM插件    │ │行动插件  │ │
│  │Binance    │ │Bollinger  │ │DeepSeek   │ │微信推送  │ │
│  │CoinGecko  │ │MACD       │ │MockLLM    │ │保存草稿  │ │
│  │YahooFin   │ │RSI        │ │           │ │生成梗图  │ │
│  │Finviz     │ │SimpleHold │ │           │ │润色文案  │ │
│  └───────────┘ └───────────┘ └───────────┘ └─────────┘ │
│  (可自由添加新插件)                                      │
└────────────────────────────────────────────────────────┘
```

---

## 📦 插件列表

### 交易所插件 (exchange)
| 插件名 | 描述 | 参数 |
|--------|------|------|
| Binance | Binance交易所K线 | symbol, timeframe |
| CoinGecko | 加密货币数据 | symbol |
| YahooFinance | 股票数据 | symbol, timeframe |
| Finviz | 股票基本面 | symbol |

### 策略插件 (strategy)
| 插件名 | 描述 | 参数 |
|--------|------|------|
| BollingerBand | 布林带策略 | period, std_multiplier |
| MACD | MACD策略 | fast_period, slow_period |
| RSI | RSI策略 | period, oversold, overbought |
| SimpleHold | 简单持有 | - |

### LLM插件 (llm)
| 插件名 | 描述 | 参数 |
|--------|------|------|
| DeepSeek | DeepSeek大模型 | api_key, prompt |
| MockLLM | 模拟LLM（测试用） | prompt |

### 行动插件 (action)
| 插件名 | 描述 | 参数 |
|--------|------|------|
| ServerChanPush | 推送微信 | skey, message |
| SaveDraft | 保存草稿箱 | topic, copy, platforms |
| MemeGenerator | 生成梗图 | style |
| Polisher | 润色文案 | original, style |

---

## 📋 策略配置

打开 `strategy.yaml`，定义你的流程：

```yaml
my_strategy:
  金融:
    steps:
      - plugin: Binance
        config:
          symbol: BTCUSDT
          timeframe: 4h
      - plugin: BollingerBand
        config: {}
      - plugin: DeepSeek
        config:
          prompt: "给出明确的买卖建议"
      - plugin: ServerChanPush
        config: {}
```

---

## 🧩 开发新插件

只需创建一个继承 `Plugin` 的类：

```python
from agent_os.plugins import Plugin

class MyPlugin(Plugin):
    name = "MyPlugin"
    description = "我的自定义插件"
    category = "strategy"
    
    def execute(self, config):
        # 你的业务逻辑
        return {
            'success': True,
            'signal': '做多',
        }
    
    def get_params(self):
        return {
            'param1': {'type': 'string', 'description': '参数说明'},
        }
```

保存到 `plugins/my_plugin.py`，系统会自动加载！

---

## 📁 项目结构

```
agent_os/
├── core/
│   └── agent_os.py      # 内核（纯调度，零业务逻辑）
├── plugins/
│   ├── __init__.py      # 插件基类和管理器
│   ├── exchanges.py     # 交易所插件
│   ├── strategies.py    # 策略插件
│   ├── llm_providers.py # LLM插件
│   └── actions.py       # 行动插件
├── strategy.yaml        # 策略配置（你定义流程）
├── config.py            # API配置
├── setup_wizard.py      # 交互式配置向导
├── demo.py              # 演示脚本
└── .env.example         # API Key模板
```

---

## 🎯 使用示例

```
你说：帮我分析今天的金融市场

系统按你的策略执行：
📋 策略流程: Binance → BollingerBand → DeepSeek → ServerChanPush

步骤 1: Binance
{exchange: Binance, symbol: BTCUSDT, prices: [...]}

步骤 2: BollingerBand
信号: 做多
当前: 42000
上轨: 45000
下轨: 41500

步骤 3: DeepSeek
根据分析，建议做多。

步骤 4: ServerChanPush
✅ 推送微信成功
```

---

## 📌 核心理念

1. **内核是通用的**：不管你做什么领域，内核逻辑都一样
2. **插件是可替换的**：换交易所、换策略、换LLM，都不用改内核
3. **策略是你定义的**：你决定流程，系统帮你执行
4. **低认知成本**：不懂代码也能用配置向导配置

> **就像安卓一样**：Google提供操作系统，开发者在上面做App。
> **Agent OS提供内核**，你在上面定义你的业务流程。

---

## 📄 许可证

MIT License
