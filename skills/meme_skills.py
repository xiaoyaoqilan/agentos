"""梗图相关Skills"""
import os
import json
import random
import urllib.request
import logging
from typing import Dict, List, Any
from datetime import datetime

from agent_os.core import BaseSkill, register_skill

logger = logging.getLogger(__name__)


@register_skill
class HotCrawler(BaseSkill):
    name = "HotCrawler"
    description = "爬取热点话题和搞笑内容"
    input_schema = {"platforms": {"type": "list", "description": "平台列表"}}
    output_schema = {"topics": {"type": "list", "description": "热点话题列表"}}
    
    def __init__(self):
        self.meme_topics = {
            'weibo': ['周一不想上班', '猫咪鄙视的眼神', '减肥第一天就失败', '打工人的崩溃瞬间', '程序员改bug的日常'],
            'douyin': ['搞笑猫咪视频', '萌宠成精了', '人类迷惑行为', '社死现场', '情侣日常互怼'],
            'jokes': ['老板说今天加班，我说明天吧太累了', '减肥第一天：吃了蛋糕，明天再开始'],
            'tieba': ['沙雕表情包大赛', '今日份快乐源泉', '人类迷惑行为大赏'],
            'zhihu': ['如何优雅地拒绝加班', '猫咪为什么看不起人', '减肥失败是种什么体验'],
        }
    
    def execute(self, platforms: List[str] = None) -> Dict[str, Any]:
        if platforms is None:
            platforms = ['weibo', 'douyin', 'jokes']
        
        all_topics = []
        for platform in platforms:
            topics = self.meme_topics.get(platform, [])
            all_topics.extend(topics)
        
        return {'topics': list(set(all_topics))[:10], 'platforms': platforms}


@register_skill
class MemeSearch(BaseSkill):
    name = "MemeSearch"
    description = "搜索搞笑表情包图片"
    input_schema = {"query": {"type": "string", "description": "搜索关键词"}}
    output_schema = {"images": {"type": "list", "description": "图片URL列表"}}
    
    def __init__(self):
        self.meme_images = {
            "不想上班": ["https://i.imgflip.com/1g8my4.jpg", "https://i.imgflip.com/2fm6x.jpg"],
            "猫咪": ["https://i.imgflip.com/2kbn1e.jpg", "https://i.imgflip.com/345v97.jpg"],
            "减肥": ["https://i.imgflip.com/1jwhww.jpg", "https://i.imgflip.com/2w6w7l.jpg"],
            "打工人": ["https://i.imgflip.com/wxica.jpg", "https://i.imgflip.com/1bhw.jpg"],
            "程序员": ["https://i.imgflip.com/1x3lyq.jpg", "https://i.imgflip.com/1o00in.jpg"],
            "沙雕": ["https://i.imgflip.com/1ur9b0.jpg", "https://i.imgflip.com/1g8my4.jpg"],
            "崩溃": ["https://i.imgflip.com/261o3j.jpg", "https://i.imgflip.com/1b42wl.jpg"],
            "放假": ["https://i.imgflip.com/39t1o.jpg", "https://i.imgflip.com/23ls.jpg"],
            "热": ["https://i.imgflip.com/1bhw.jpg", "https://i.imgflip.com/2w6w7l.jpg"],
            "外卖": ["https://i.imgflip.com/261o3j.jpg", "https://i.imgflip.com/2v3x9a.jpg"],
            "手机": ["https://i.imgflip.com/1b42wl.jpg", "https://i.imgflip.com/2x7x5s.jpg"],
            "单身": ["https://i.imgflip.com/2kbn1e.jpg", "https://i.imgflip.com/1o0z76.jpg"],
            "头发": ["https://i.imgflip.com/9ehk.jpg", "https://i.imgflip.com/2x8q9t.jpg"],
            "社死": ["https://i.imgflip.com/1ur9b0.jpg", "https://i.imgflip.com/37i81w.jpg"],
            "翻车": ["https://i.imgflip.com/1jwhww.jpg", "https://i.imgflip.com/2fm6x.jpg"],
        }
    
    def execute(self, query: str = "") -> Dict[str, Any]:
        if not query:
            query = "搞笑"
        
        for key, images in self.meme_images.items():
            if key in query:
                return {'images': images, 'matched_keyword': key}
        
        fallback_images = [
            'https://i.imgflip.com/30b1gx.jpg',
            'https://i.imgflip.com/1g8my4.jpg',
            'https://i.imgflip.com/1ur9b0.jpg',
        ]
        
        return {'images': fallback_images, 'query': query}


@register_skill
class Copywriter(BaseSkill):
    name = "Copywriter"
    description = "生成搞笑文案"
    input_schema = {"topic": {"type": "string", "description": "主题"}, "image_keyword": {"type": "string", "description": "图片关键词"}}
    output_schema = {"copy": {"type": "string", "description": "生成的文案"}}
    
    def __init__(self):
        self.emotional_templates = {
            "不想上班": ["周一的我：不想上班！不想上班！！不想上班！！！", "闹钟响了=世界末日", "起床的那一刻，我在思考人生意义"],
            "猫咪": ["猫：你配碰我吗？人类！", "主子一个眼神，我就知道错了", "吸猫使人快乐，也使人贫穷"],
            "减肥": ["吃饱了才有力气减肥（理直气壮）", "减肥第一天失败，明天继续", "这顿不算，真的不算！"],
            "打工人": ["搬砖使我快乐，工资使我痛苦", "工资到账的那一刻是最幸福的", "摸鱼一时爽，一直摸鱼一直爽"],
            "程序员": ["写代码，改bug，头发没了", "需求变了？那我重写吧（微笑）", "程序跑起来了，我崩溃了"],
            "沙雕": ["沙雕网友欢乐多", "今天也是沙雕的一天", "迷惑行为大赏"],
            "崩溃": ["成年人的崩溃，就在一瞬间", "我太难了，真的太难了", "破防了，彻底破防了"],
            "放假": ["终于解放了，谁也别想找到我", "放假第一天：睡觉，第二天：继续睡觉", "假期余额不足，请及时充值"],
            "热": ["出门五分钟，流汗两小时", "太阳太大，我要化了", "夏天的命是空调给的"],
            "外卖": ["外卖迟到一小时，我饿晕了", "等外卖的心情，像等初恋", "外卖终于到了，感动哭了"],
            "手机": ["手机没电的绝望，谁懂啊", "出门忘带充电宝=裸奔", "手机电量低于20%，开始恐慌"],
            "单身": ["一人吃饱，全家不饿", "狗粮管够，我已经饱了", "单身挺好，就是没人暖被窝"],
            "头发": ["头发越来越少，发际线越来越高", "程序员：头发是什么？能吃吗？", "我的头发：我先走一步"],
            "社死": ["社死现场，尴尬到抠脚", "脚趾抠出三室一厅", "当场去世，谁来救救我"],
            "翻车": ["翻车现场，大型翻车现场", "自信满满，结果翻车了", "以为是王者，结果是青铜"],
        }
    
    def execute(self, topic: str = "", image_keyword: str = "") -> Dict[str, Any]:
        if not topic:
            topic = "搞笑"
        
        for key, copies in self.emotional_templates.items():
            if key in topic:
                return {'copy': random.choice(copies), 'topic': topic}
        
        patterns = [
            f"笑死！{topic}",
            f"{topic}？哈哈哈哈",
            f"这就是{topic}吗？绝了！",
            f"{topic}使人快乐",
            f"关于{topic}这件事，我只能说...太真实了！",
        ]
        
        return {'copy': random.choice(patterns), 'topic': topic}


@register_skill
class DraftPoster(BaseSkill):
    name = "DraftPoster"
    description = "保存内容到各平台草稿箱"
    input_schema = {"topic": {"type": "string", "description": "主题"}, "copy": {"type": "string", "description": "文案"}, "image_path": {"type": "string", "description": "图片路径"}}
    output_schema = {"results": {"type": "list", "description": "各平台保存结果"}}
    
    def __init__(self):
        pass
    
    def execute(self, topic: str = "", copy: str = "", image_path: str = "") -> Dict[str, Any]:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drafts')
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        wechat_draft = {'title': topic[:64], 'content': f'<p>{copy}</p>', 'image_path': image_path}
        with open(os.path.join(output_dir, 'wechat_draft.json'), 'w', encoding='utf-8') as f:
            json.dump(wechat_draft, f, ensure_ascii=False, indent=2)
        results.append({'platform': 'wechat', 'success': True})
        
        weibo_draft = {'content': copy[:2000], 'image_path': image_path}
        with open(os.path.join(output_dir, 'weibo_draft.json'), 'w', encoding='utf-8') as f:
            json.dump(weibo_draft, f, ensure_ascii=False, indent=2)
        results.append({'platform': 'weibo', 'success': True})
        
        douyin_draft = {'text': copy[:1000], 'video_path': image_path}
        with open(os.path.join(output_dir, 'douyin_draft.json'), 'w', encoding='utf-8') as f:
            json.dump(douyin_draft, f, ensure_ascii=False, indent=2)
        results.append({'platform': 'douyin', 'success': True})
        
        logger.info(f"保存到各平台草稿箱: {[r['platform'] for r in results]}")
        return {'results': results, 'topic': topic}