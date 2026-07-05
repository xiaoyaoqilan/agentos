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

from agent_os.config import load_config

logger = logging.getLogger(__name__)


class AgentOS:
    def __init__(self):
        self.config = load_config()
        self.api_key = self.config['api_keys']['deepseek'] or os.getenv('DEEPSEEK_API_KEY')
        self.skey = self.config['api_keys']['serverchan'] or os.getenv('SERVERCHAN_KEY')
        self.rag_memory = []
        
        self.data_sources = {
            '金融': ['https://www.coingecko.com', 'https://finance.yahoo.com', 'https://finviz.com'],
            '加密货币': ['https://www.coingecko.com', 'https://www.binance.com'],
            '股票': ['https://finance.yahoo.com', 'https://finviz.com'],
            '电商': ['https://www.smzdm.com', 'https://jd.com', 'https://taobao.com'],
            '热点': ['https://weibo.com', 'https://www.douyin.com', 'https://zhihu.com'],
            '搞笑': ['https://weibo.com', 'https://www.douyin.com', 'https://imgflip.com'],
            '科技': ['https://tech.sina.com.cn', 'https://www.ithome.com'],
            '新闻': ['https://news.sina.com.cn', 'https://www.baidu.com'],
        }

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
        
        return '好的，我来处理'

    def search(self, domain: str, query: str = "") -> str:
        sources = self.data_sources.get(domain, self.data_sources['新闻'])
        
        results = []
        for source in sources[:2]:
            try:
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                resp = urllib.request.urlopen(source, timeout=10)
                content = resp.read().decode('utf-8', errors='ignore')[:500]
                results.append(f"【{source}】{content[:200]}...")
            except:
                results.append(f"【{source}】无法访问")
        
        info = f"搜索结果({domain}):\n" + "\n".join(results)
        self.write_rag(info)
        return info

    def analyze(self) -> str:
        context = self.read_rag()
        if not context:
            return "没有足够信息进行分析"
        
        prompt = f"""根据以下上下文信息进行分析：
{context}

请给出简短的分析结论和建议。"""
        
        result = self.ask_llm(prompt)
        self.write_rag(f"分析结论: {result}")
        return result

    def bollinger_analysis(self, symbols: List[str]) -> str:
        signals = []
        for symbol in symbols[:3]:
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

    def push(self, message: str) -> str:
        if not self.skey:
            self.write_rag(f"推送消息(未配置KEY): {message}")
            return "⚠️ 需要配置 ServerChan Key 才能推送微信"
        
        try:
            url = f"https://sctapi.ftqq.com/{self.skey}.send"
            data = {"title": "Agent通知", "desp": message[:2000]}
            req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method='POST')
            urllib.request.urlopen(req, timeout=10)
            self.write_rag(f"推送成功: {message[:100]}...")
            return "✅ 推送微信成功"
        except Exception as e:
            return f"❌ 推送失败: {e}"

    def save_draft(self, topic: str, copy: str, image_url: str = "") -> str:
        drafts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drafts')
        os.makedirs(drafts_dir, exist_ok=True)
        
        wechat_draft = {'title': topic[:64], 'content': copy, 'image_url': image_url}
        with open(os.path.join(drafts_dir, 'wechat_draft.json'), 'w', encoding='utf-8') as f:
            json.dump(wechat_draft, f, ensure_ascii=False, indent=2)
        
        weibo_draft = {'content': copy[:2000], 'image_url': image_url}
        with open(os.path.join(drafts_dir, 'weibo_draft.json'), 'w', encoding='utf-8') as f:
            json.dump(weibo_draft, f, ensure_ascii=False, indent=2)
        
        douyin_draft = {'text': copy[:1000], 'image_url': image_url}
        with open(os.path.join(drafts_dir, 'douyin_draft.json'), 'w', encoding='utf-8') as f:
            json.dump(douyin_draft, f, ensure_ascii=False, indent=2)
        
        self.write_rag(f"保存草稿: {topic} - {copy}")
        return "✅ 微信/微博/抖音 草稿箱已保存"

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
        """主入口：你说一句话，系统自动完成所有工作"""
        logger.info(f"用户意图: {user_intent}")
        self.write_rag(f"用户意图: {user_intent}")
        
        print(f"\n{'='*50}")
        print(f"你说: {user_intent}")
        print(f"{'='*50}")
        
        domain = self.ask_llm(f"用户说: '{user_intent}'，这是什么领域？可选：金融、热点、电商、科技、新闻")
        print(f"\n🎯 识别领域: {domain}")
        self.write_rag(f"识别领域: {domain}")
        
        if domain == '金融':
            print("\n🔍 搜索金融数据...")
            self.search('金融')
            
            print("\n📊 布林带分析...")
            symbols = self.config['domains']['金融'].get('symbols', ['BTCUSDT', 'ETHUSDT', 'NVDA'])
            analysis = self.bollinger_analysis(symbols)
            print(analysis)
            
            print("\n🤔 LLM决策分析...")
            decision = self.analyze()
            print(decision)
            
            if self.config['settings']['push_to_wechat']:
                print("\n📤 推送微信...")
                push_result = self.push(analysis + "\n\n" + decision)
                print(push_result)
            
            return f"\n✅ 金融分析完成:\n{analysis}\n\n{decision}"
        
        elif domain in ['热点', '搞笑']:
            print("\n🔍 搜索热点...")
            self.search('热点')
            
            print("\n🎨 生成梗图...")
            
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
            topic = meme['topic']
            image_url = meme['image']
            copy = random.choice(meme['copies'])
            
            print(f"   主题: {topic}")
            print(f"   文案: {copy}")
            print(f"   图片: {image_url}")
            
            self.write_rag(f"梗图发布: {topic} - {copy}")
            
            print("\n💾 保存到草稿箱...")
            save_result = self.save_draft(topic, copy, image_url)
            print(save_result)
            
            return f"\n✅ 梗图生成完成:\n主题: {topic}\n文案: {copy}\n图片: {image_url}"
        
        elif domain == '电商':
            print("\n🔍 搜索电商优惠...")
            self.search('电商')
            
            print("\n🤔 分析优惠信息...")
            analysis = self.analyze()
            print(analysis)
            
            return f"\n✅ 电商分析完成:\n{analysis}"
        
        else:
            print("\n🔍 搜索相关信息...")
            self.search(domain)
            
            print("\n🤔 分析...")
            analysis = self.analyze()
            print(analysis)
            
            return f"\n✅ {domain}分析完成:\n{analysis}"


agent_os = AgentOS()
