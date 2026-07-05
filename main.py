"""Agent OS - 分层自治系统主入口"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║              Agent OS - 分层自治系统                      ║
║                                                          ║
║         简单说一句话，系统自动完成所有工作                   ║
║         无需懂代码，无需懂API，无需懂逻辑                    ║
╚══════════════════════════════════════════════════════════╝
""")
    
    from agent_os.core.agent_os import agent_os
    
    while True:
        print("\n" + "="*50)
        user_input = input("你想干什么？(输入 '退出' 结束) ")
        
        if user_input in ['退出', 'exit', 'quit']:
            print("再见！")
            break
        
        if not user_input.strip():
            print("请输入你的意图")
            continue
        
        try:
            result = agent_os.run(user_input)
            print(f"\n✅ {result}")
        except Exception as e:
            print(f"❌ 出错了: {e}")


if __name__ == '__main__':
    main()