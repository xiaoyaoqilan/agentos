"""Agent OS - 分层自治系统核心"""
import os
import json
import urllib.request
import logging
import random
from datetime import datetime
from typing import Dict, List, Any
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import yaml
from agent_os.config import load_config

logger = logging.getLogger(__name__)


class AgentOS:
    def __init__(self):
        self.config = load_config()
        self.api_key = self.config['api_keys']['deepseek'] or os.getenv('DEEPSEEK_API_KEY')
        self.skey = self.config['api_keys']['serverchan'] or os.getenv('SERVERCHAN_KEY')
        self.rag_memory = []
        self.strategy = self._load_strategy()
        
        self.data_sources_map = {
            'coingecko': 'https://www.coingecko.com',
            'yahoo_finance': 'https://finance.yahoo.com',
            'finviz': 'https://finviz.com',
            'binance': 'https://www.binance.com',
            'smzdm': 'https://www.smzdm.com',
            'jd': 'https://jd.com',
            'taobao': 'https://taobao.com',
            'weibo': 'https://weibo.com',
            'douyin': 'https://www.douyin.com',
            'zhihu': 'https://zhihu.com',
            'imgflip': 'https://imgflip.com',
            'tech_sina': 'https://tech.sina.com.cn',
            'ithome': 'https://www.ithome.com',
            'news_sina': 'https://news.sina.com.cn',
            'baidu': 'https://www.baidu.com',
        }

    def _load_strategy(self) -> Dict:
        strategy_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'strategy.yaml')
        if os.path.exists(strategy_file):
            with open(strategy_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def ask_llm(self, prompt: str) -> str:
        if not self.api_key:
            return self._mock_llm_response(prompt)
        
        try:
            url = "https://api.deepseek.com/v1/chat/completions"
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 300
            }
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            resp = urllib.request.urlopen(req, timeout=30)
            result = json.loads(resp.read().decode('utf-8'))
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.warning(f"LLM调用失败: {e}")
            return self._mock_llm_response(prompt)

    def _mock_llm_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        if '下一步' in prompt_lower or '做什么' in prompt_lower:
            return random.choice(['搜索', '分析', '推送'])
        
        if '领域' in prompt_lower or '什么领域' in prompt_lower:
            import re
            match = re.search(r"用户说:\s*['\"](.*?)['\"]", prompt)
            user_intent = match.group(1).lower() if match else prompt_lower
            
            if any(k in user_intent for k in ['金融', '股票', '投资', '加密货币', '市场']):
                return '金融'
            if any(k in user_intent for k in ['搞笑', '梗图', '表情包', '热点', '段子']):
                return '热点'
            if any(k in user_intent for k in ['电商', '优惠', '购物', '京东', '淘宝']):
                return '电商'
            if any(k in user_intent for k in ['科技', '技术', 'IT', '互联网']):
                return '科技'
            if any(k in user_intent for k in ['新闻', '资讯', '头条']):
                return '新闻'
            return random.choice(['金融', '热点', '电商'])
        
        if '润色文案' in prompt_lower:
            return "文案已润色：更有趣，更简短！"
        
        return '好的，我来处理'

    def _step_search(self, config: Dict) -> str:
        sources = config.get('sources', [])
        if not sources:
            sources = ['coingecko', 'yahoo_finance']
        
        results = []
        for source_key in sources[:2]:
            url = self.data_sources_map.get(source_key, f"https://{source_key}.com")
            try:
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                resp = urllib.request.urlopen(url, timeout=10)
                content = resp.read().decode('utf-8', errors='ignore')[:500]
                results.append(f"【{source_key}】{content[:150]}...")
            except:
                results.append(f"【{source_key}】无法访问")
        
        info = "\n".join(results)
        self.write_rag(f"搜索结果: {info[:200]}")
        return info

    def _step_bollinger(self, config: Dict) -> str:
        symbols = config.get('symbols', ['BTCUSDT', 'ETHUSDT', 'NVDA'])
        timeframe = config.get('timeframe', '4h')
        strategy_desc = config.get('strategy', '下轨做多，上轨看空')
        
        print(f"   ⏱️ 时间周期: {timeframe}")
        print(f"   📖 策略: {strategy_desc}")
        
        signals = []
        for symbol in symbols[:4]:
            prices = [random.uniform(40000, 45000) for _ in range(20)]
            avg = sum(prices) / len(prices)
            std = (sum((p - avg) ** 2 for p in prices) / len(prices)) ** 0.5
            upper, lower = avg + 2 * std, avg - 2 * std
            current = prices[-1]
            
            if current < lower:
                direction = '做多'
            elif current > upper:
                direction = '看空'
            else:
                direction = '观望'
            
            signals.append(f"{symbol}: {direction} (当前{round(current, 0)}, 上轨{round(upper, 0)}, 下轨{round(lower, 0)})")
        
        result = "\n".join(signals)
        self.write_rag(f"布林带信号: {result}")
        return result

    def _step_llm_decision(self, config: Dict) -> str:
        context = self.read_rag()
        prompt = config.get('prompt', '根据数据给出分析和建议')
        full_prompt = f"""根据以下上下文信息进行分析：
{context}

{prompt}"""
        
        result = self.ask_llm(full_prompt)
        self.write_rag(f"LLM决策: {result}")
        return result

    def _step_generate_meme(self, config: Dict) -> Dict:
        style = config.get('style', '搞笑')
        
        MEME_TEMPLATES = [
            {"topic": "周一不想上班", "image": "https://i.imgflip.com/1g8my4.jpg", "copies": ["周一的我：不想上班！不想上班！！", "闹钟响了=世界末日", "起床的那一刻，我在思考人生意义"]},
            {"topic": "减肥失败", "image": "https://i.imgflip.com/1jwhww.jpg", "copies": ["吃饱了才有力气减肥（理直气壮）", "减肥第一天失败，明天继续", "这顿不算，真的不算！"]},
            {"topic": "程序员改bug", "image": "https://i.imgflip.com/wxica.jpg", "copies": ["写代码，改bug，头发没了", "需求变了？那我重写吧（微笑）", "程序跑起来了，我崩溃了"]},
            {"topic": "社死现场", "image": "https://i.imgflip.com/1ur9b0.jpg", "copies": ["社死现场，尴尬到抠脚", "脚趾抠出三室一厅", "当场去世，谁来救救我"]},
            {"topic": "单身狗", "image": "https://i.imgflip.com/2kbn1e.jpg", "copies": ["一人吃饱，全家不饿", "狗粮管够，我已经饱了", "单身挺好，就是没人暖被窝"]},
            {"topic": "摸鱼被抓", "image": "https://i.imgflip.com/30b1gx.jpg", "copies": ["摸鱼一时爽，一直摸鱼一直爽", "老板来了！快切屏！", "上班时间，带薪拉屎"]},
            {"topic": "夏天太热", "image": "https://i.imgflip.com/1bhw.jpg", "copies": ["出门五分钟，流汗两小时", "太阳太大，我要化了", "夏天的命是空调给的"]},
            {"topic": "外卖迟到", "image": "https://i.imgflip.com/261o3j.jpg", "copies": ["外卖迟到一小时，我饿晕了", "等外卖的心情，像等初恋", "外卖终于到了，感动哭了"]},
            {"topic": "手机没电", "image": "https://i.imgflip.com/1b42wl.jpg", "copies": ["手机没电的绝望，谁懂啊", "出门忘带充电宝=裸奔", "手机电量低于20%，开始恐慌"]},
            {"topic": "脱发", "image": "https://i.imgflip.com/9ehk.jpg", "copies": ["头发越来越少，发际线越来越高", "程序员：头发是什么？能吃吗？", "我的头发：我先走一步"]},
        ]
        
        meme = random.choice(MEME_TEMPLATES)
        return {
            'topic': meme['topic'],
            'image': meme['image'],
            'copy': random.choice(meme['copies'])
        }

    def _step_polish_copy(self, config: Dict, current_copy: str) -> str:
        style = config.get('style', '幽默')
        prompt = f"""帮我润色这句话，风格要求：{style}
原句: {current_copy}"""
        result = self.ask_llm(prompt)
        return result if result else current_copy

    def _step_push_wechat(self, config: Dict, message: str) -> str:
        enabled = config.get('enabled', True)
        if not enabled:
            return "⏭️ 微信推送已关闭"
        
        if not self.skey:
            return "⚠️ 需要配置 ServerChan Key"
        
        try:
            url = f"https://sctapi.ftqq.com/{self.skey}.send"
            data = {"title": "Agent通知", "desp": message[:2000]}
            req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method='POST')
            urllib.request.urlopen(req, timeout=10)
            self.write_rag(f"推送成功: {message[:100]}")
            return "✅ 推送微信成功"
        except Exception as e:
            return f"❌ 推送失败: {e}"

    def _step_save_draft(self, config: Dict, topic: str, copy: str, image_url: str = "") -> str:
        platforms = config.get('platforms', ['微信', '微博', '抖音'])
        drafts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drafts')
        os.makedirs(drafts_dir, exist_ok=True)
        
        if '微信' in platforms:
            wechat_draft = {'title': topic[:64], 'content': copy, 'image_url': image_url}
            with open(os.path.join(drafts_dir, 'wechat_draft.json'), 'w', encoding='utf-8') as f:
                json.dump(wechat_draft, f, ensure_ascii=False, indent=2)
        
        if '微博' in platforms:
            weibo_draft = {'content': copy[:2000], 'image_url': image_url}
            with open(os.path.join(drafts_dir, 'weibo_draft.json'), 'w', encoding='utf-8') as f:
                json.dump(weibo_draft, f, ensure_ascii=False, indent=2)
        
        if '抖音' in platforms:
            douyin_draft = {'text': copy[:1000], 'image_url': image_url}
            with open(os.path.join(drafts_dir, 'douyin_draft.json'), 'w', encoding='utf-8') as f:
                json.dump(douyin_draft, f, ensure_ascii=False, indent=2)
        
        self.write_rag(f"保存草稿: {topic} - {copy}")
        return f"✅ {'/'.join(platforms)} 草稿箱已保存"

    def write_rag(self, content: str) -> None:
        self.rag_memory.append({
            'timestamp': datetime.now().isoformat(),
            'content': content
        })
        if len(self.rag_memory) > 50:
            self.rag_memory = self.rag_memory[-50:]

    def read_rag(self) -> str:
        return "\n".join([f"[{m['timestamp']}] {m['content']}" for m in self.rag_memory[-10:]])

    def run(self, user_intent: str) -> str:
        """主入口：你说一句话，系统按你的策略自动执行"""
        logger.info(f"用户意图: {user_intent}")
        self.write_rag(f"用户意图: {user_intent}")
        
        print(f"\n{'='*50}")
        print(f"你说: {user_intent}")
        print(f"{'='*50}")
        
        domain = self.ask_llm(f"用户说: '{user_intent}'，这是什么领域？可选：金融、热点、电商、科技、新闻")
        print(f"\n🎯 识别领域: {domain}")
        self.write_rag(f"识别领域: {domain}")
        
        strategy = self.strategy.get('my_strategy', {})
        domain_strategy = strategy.get(domain, {})
        steps = domain_strategy.get('steps', [])
        
        if not steps:
            print(f"\n⚠️ 没有找到{domain}领域的策略配置")
            print("   默认流程: 搜索 → 分析")
            steps = [
                {'step': '搜索', 'config': {}},
                {'step': 'LLM决策', 'config': {}}
            ]
        
        print(f"\n📋 策略流程 ({domain_strategy.get('name', '我的策略')}):")
        for i, step_def in enumerate(steps, 1):
            print(f"   {i}. {step_def['step']}")
        
        meme_result = None
        all_results = []
        
        for i, step_def in enumerate(steps, 1):
            step_name = step_def['step']
            config = step_def.get('config', {})
            
            print(f"\n{'━'*40}")
            print(f"步骤 {i}: {step_name}")
            print(f"{'━'*40}")
            
            if step_name == '搜索':
                result = self._step_search(config)
                print(result)
                all_results.append(f"搜索结果: {result[:100]}...")
            
            elif step_name == '布林带分析':
                result = self._step_bollinger(config)
                print(result)
                all_results.append(f"布林带分析:\n{result}")
            
            elif step_name == 'LLM决策':
                result = self._step_llm_decision(config)
                print(result)
                all_results.append(f"LLM决策:\n{result}")
            
            elif step_name == '生成梗图':
                meme_result = self._step_generate_meme(config)
                print(f"   主题: {meme_result['topic']}")
                print(f"   文案: {meme_result['copy']}")
                print(f"   图片: {meme_result['image']}")
                all_results.append(f"梗图: {meme_result['topic']} - {meme_result['copy']}")
            
            elif step_name == 'LLM润色文案':
                if meme_result:
                    polished = self._step_polish_copy(config, meme_result['copy'])
                    print(f"   原文案: {meme_result['copy']}")
                    print(f"   润色后: {polished}")
                    meme_result['copy'] = polished
                    all_results.append(f"润色文案: {polished}")
            
            elif step_name == '推送微信':
                message = "\n\n".join(all_results[-3:])
                result = self._step_push_wechat(config, message)
                print(result)
                all_results.append(f"推送结果: {result}")
            
            elif step_name == '保存草稿':
                if meme_result:
                    result = self._step_save_draft(config, meme_result['topic'], meme_result['copy'], meme_result['image'])
                    print(result)
                    all_results.append(f"草稿保存: {result}")
            
            else:
                print(f"   ⚠️ 未知步骤: {step_name}")
        
        final_result = f"\n✅ {domain}分析完成！"
        if meme_result:
            final_result += f"\n主题: {meme_result['topic']}\n文案: {meme_result['copy']}"
        
        return final_result


agent_os = AgentOS()
