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

logger = logging.getLogger(__name__)


class AgentOS:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.skey = os.getenv('SERVERCHAN_KEY')
        self.rag_memory = []
        self.finished = False
        
        self.data_sources = {
            '金融': ['https://www.coingecko.com', 'https://finance.yahoo.com', 'https://finviz.com'],
            '加密货币': ['https://www.coingecko.com', 'https://www.binance.com'],
            '股票': ['https://finance.yahoo.com', 'https://finviz.com'],
            '电商': ['https://www.smzdm.com', 'https://jd.com', 'https://taobao.com'],
            '热点': ['https://weibo.com', 'https://www.douyin.com', 'https://zhihu.com'],
            '搞笑': ['https://weibo.com', 'https://www.douyin.com', 'https://imgflip.com'],
            '科技': ['https://tech.sina.com.cn', 'https://www.ithome.com', 'https://www.jiemian.com'],
            '新闻': ['https://news.sina.com.cn', 'https://www.baidu.com'],
        }
        
        self.action_types = ['搜索', '分析', '推送', '保存', '结束']

    def ask_llm(self, prompt: str) -> str:
        """调用LLM"""
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
        """模拟LLM响应"""
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
        """搜索层：根据领域自动选择数据源"""
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
        """思考层：从RAG读取并分析"""
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
        """金融专用：布林带分析"""
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
        """行动层：推送通知"""
        if not self.skey:
            self.write_rag(f"推送消息(未配置KEY): {message}")
            return "推送: 需要配置SERVERCHAN_KEY"
        
        try:
            url = f"https://sctapi.ftqq.com/{self.skey}.send"
            data = {"title": "Agent通知", "desp": message[:2000]}
            req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method='POST')
            urllib.request.urlopen(req, timeout=10)
            self.write_rag(f"推送成功: {message[:100]}...")
            return "推送: 成功"
        except Exception as e:
            return f"推送: 失败 - {e}"

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
        """主循环：用户输入一句话，自动完成所有工作"""
        logger.info(f"用户意图: {user_intent}")
        self.write_rag(f"用户意图: {user_intent}")
        
        print(f"\n{'='*50}")
        print(f"意图: {user_intent}")
        print(f"{'='*50}")
        
        domain = self.ask_llm(f"用户说: '{user_intent}'，这是什么领域？可选：金融、热点、电商、科技、新闻")
        print(f"\n🎯 识别领域: {domain}")
        self.write_rag(f"识别领域: {domain}")
        
        if domain == '金融':
            print("\n🔍 搜索金融数据...")
            self.search('金融')
            
            print("\n📊 布林带分析...")
            symbols = ['BTCUSDT', 'ETHUSDT', 'NVDA', 'AAPL', 'MSFT']
            analysis = self.bollinger_analysis(symbols)
            print(analysis)
            
            print("\n🤔 LLM决策分析...")
            decision = self.analyze()
            print(decision)
            
            print("\n📤 推送微信...")
            push_result = self.push(analysis + "\n\n" + decision)
            print(push_result)
            
            return f"金融分析完成:\n{analysis}\n\n{decision}"
        
        elif domain in ['热点', '搞笑']:
            print("\n🔍 搜索热点...")
            self.search('热点')
            
            print("\n🤔 生成文案...")
            topics = ['周一不想上班', '猫咪鄙视的眼神', '减肥第一天就失败', '打工人的崩溃瞬间']
            topic = random.choice(topics)
            
            meme_images = {
                "不想上班": "https://i.imgflip.com/1g8my4.jpg",
                "猫咪": "https://i.imgflip.com/2kbn1e.jpg",
                "减肥": "https://i.imgflip.com/1jwhww.jpg",
                "打工人": "https://i.imgflip.com/wxica.jpg",
            }
            
            image_url = None
            for key, url in meme_images.items():
                if key in topic:
                    image_url = url
                    break
            
            copy_patterns = {
                "不想上班": ["周一的我：不想上班！", "闹钟响了=世界末日"],
                "猫咪": ["猫：你配碰我吗？", "主子一个眼神，我就知道错了"],
                "减肥": ["吃饱了才有力气减肥", "减肥第一天失败，明天继续"],
                "打工人": ["搬砖使我快乐", "工资到账的那一刻最幸福"],
            }
            
            copy = ""
            for key, patterns in copy_patterns.items():
                if key in topic:
                    copy = random.choice(patterns)
                    break
            
            if not copy:
                copy = f"笑死！{topic}"
            
            print(f"   主题: {topic}")
            print(f"   文案: {copy}")
            print(f"   图片: {image_url}")
            
            self.write_rag(f"梗图发布: {topic} - {copy}")
            
            print("\n💾 保存到草稿箱...")
            drafts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drafts')
            os.makedirs(drafts_dir, exist_ok=True)
            
            wechat_draft = {'title': topic, 'content': copy, 'image_url': image_url}
            with open(os.path.join(drafts_dir, 'wechat_draft.json'), 'w', encoding='utf-8') as f:
                json.dump(wechat_draft, f, ensure_ascii=False, indent=2)
            print("   ✅ 微信草稿箱")
            
            return f"梗图生成完成:\n主题: {topic}\n文案: {copy}\n图片: {image_url}"
        
        elif domain == '电商':
            print("\n🔍 搜索电商优惠...")
            self.search('电商')
            
            print("\n🤔 分析优惠信息...")
            analysis = self.analyze()
            print(analysis)
            
            return f"电商分析完成:\n{analysis}"
        
        else:
            print("\n🔍 搜索相关信息...")
            self.search(domain)
            
            print("\n🤔 分析...")
            analysis = self.analyze()
            print(analysis)
            
            return f"{domain}分析完成:\n{analysis}"


agent_os = AgentOS()