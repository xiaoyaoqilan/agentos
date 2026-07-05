"""配置文件 - 只需填写API Key，其余自动完成"""

CONFIG = {
    "api_keys": {
        "deepseek": "",
        "serverchan": "",
        "bing_search": "",
        "imgflip_user": "",
        "imgflip_pass": "",
    },
    
    "settings": {
        "auto_publish_interval_minutes": 30,
        "push_to_wechat": True,
        "push_to_email": False,
        "email_recipient": "",
    },
    
    "domains": {
        "金融": {
            "enabled": True,
            "symbols": ["BTCUSDT", "ETHUSDT", "NVDA", "AAPL", "MSFT"],
        },
        "热点": {
            "enabled": True,
            "platforms": ["weibo", "douyin", "imgflip"],
        },
        "电商": {
            "enabled": False,
            "platforms": ["smzdm", "jd", "taobao"],
        },
    },
}


def load_config():
    import os
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    if key.startswith('API_'):
                        api_key = key.replace('API_', '').lower()
                        CONFIG['api_keys'][api_key] = value.strip('"').strip("'")
                    elif key == 'PUSH_TO_WECHAT':
                        CONFIG['settings']['push_to_wechat'] = value.lower() == 'true'
                    elif key == 'EMAIL_RECIPIENT':
                        CONFIG['settings']['email_recipient'] = value.strip('"').strip("'")
                    elif key == 'INTERVAL_MINUTES':
                        CONFIG['settings']['auto_publish_interval_minutes'] = int(value)
    
    return CONFIG
