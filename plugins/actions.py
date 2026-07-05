"""行动插件 - 推送和保存"""

import json
import os
import urllib.request
from typing import Dict, Any
from agent_os.plugins import Plugin


class ServerChanPush(Plugin):
    name = "ServerChanPush"
    description = "通过ServerChan推送微信"
    category = "action"
    
    def execute(self, config: Dict) -> Any:
        message = config.get('message', '')
        skey = config.get('skey', '')
        
        if not skey:
            return {
                'action': 'ServerChanPush',
                'success': False,
                'message': '⚠️ 需要配置 ServerChan Key',
            }
        
        try:
            url = f"https://sctapi.ftqq.com/{skey}.send"
            data = {"title": "Agent通知", "desp": message[:2000]}
            req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method='POST')
            urllib.request.urlopen(req, timeout=10)
            return {
                'action': 'ServerChanPush',
                'success': True,
                'message': '✅ 推送微信成功',
            }
        except Exception as e:
            return {
                'action': 'ServerChanPush',
                'success': False,
                'message': f'❌ 推送失败: {e}',
            }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'skey': {'type': 'string', 'description': 'ServerChan Key', 'required': True},
            'message': {'type': 'string', 'description': '推送内容', 'required': True},
        }


class SaveDraft(Plugin):
    name = "SaveDraft"
    description = "保存到各平台草稿箱"
    category = "action"
    
    def execute(self, config: Dict) -> Any:
        topic = config.get('topic', '')
        copy = config.get('copy', '')
        image_url = config.get('image_url', '')
        platforms = config.get('platforms', ['微信', '微博', '抖音'])
        drafts_dir = config.get('drafts_dir', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'drafts'))
        
        os.makedirs(drafts_dir, exist_ok=True)
        saved = []
        
        if '微信' in platforms:
            wechat_draft = {'title': topic[:64], 'content': copy, 'image_url': image_url}
            with open(os.path.join(drafts_dir, 'wechat_draft.json'), 'w', encoding='utf-8') as f:
                json.dump(wechat_draft, f, ensure_ascii=False, indent=2)
            saved.append('微信')
        
        if '微博' in platforms:
            weibo_draft = {'content': copy[:2000], 'image_url': image_url}
            with open(os.path.join(drafts_dir, 'weibo_draft.json'), 'w', encoding='utf-8') as f:
                json.dump(weibo_draft, f, ensure_ascii=False, indent=2)
            saved.append('微博')
        
        if '抖音' in platforms:
            douyin_draft = {'text': copy[:1000], 'image_url': image_url}
            with open(os.path.join(drafts_dir, 'douyin_draft.json'), 'w', encoding='utf-8') as f:
                json.dump(douyin_draft, f, ensure_ascii=False, indent=2)
            saved.append('抖音')
        
        return {
            'action': 'SaveDraft',
            'success': True,
            'message': f'✅ {"、".join(saved)} 草稿箱已保存',
            'platforms': saved,
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'topic': {'type': 'string', 'description': '主题', 'required': True},
            'copy': {'type': 'string', 'description': '文案', 'required': True},
            'image_url': {'type': 'string', 'description': '图片URL', 'default': ''},
            'platforms': {'type': 'list', 'description': '平台列表', 'options': ['微信', '微博', '抖音'], 'default': ['微信', '微博', '抖音']},
        }


class MemeGenerator(Plugin):
    name = "MemeGenerator"
    description = "生成搞笑梗图"
    category = "action"
    
    def execute(self, config: Dict) -> Any:
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
        
        import random
        meme = random.choice(MEME_TEMPLATES)
        
        return {
            'action': 'MemeGenerator',
            'success': True,
            'topic': meme['topic'],
            'image_url': meme['image'],
            'copy': random.choice(meme['copies']),
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'style': {'type': 'string', 'description': '梗图风格', 'options': ['搞笑', '自嘲', '打工人', '情感'], 'default': '搞笑'},
        }


class Polisher(Plugin):
    name = "Polisher"
    description = "LLM润色文案"
    category = "action"
    
    def execute(self, config: Dict) -> Any:
        original = config.get('original', '')
        style = config.get('style', '幽默')
        
        from agent_os.plugins.llm_providers import MockLLM
        llm = MockLLM()
        prompt = f"帮我润色这句话，风格要求：{style}\n原句: {original}"
        result = llm.execute({'prompt': prompt})
        
        return {
            'action': 'Polisher',
            'success': result['success'],
            'original': original,
            'polished': result.get('response', original),
        }
    
    def get_params(self) -> Dict[str, Dict]:
        return {
            'original': {'type': 'string', 'description': '原文案', 'required': True},
            'style': {'type': 'string', 'description': '润色风格', 'options': ['幽默', '简短', '有情绪价值', '专业'], 'default': '幽默'},
        }
