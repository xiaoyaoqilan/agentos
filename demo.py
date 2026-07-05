"""Agent OS 演示脚本"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agent_os.core.agent_os import agent_os


def demo():
    print("""
╔══════════════════════════════════════════════════════════╗
║              Agent OS - 分层自治系统演示                   ║
╚══════════════════════════════════════════════════════════╝
""")
    
    test_cases = [
        "帮我分析一下今天的金融市场",
        "给我生成一个搞笑梗图",
        "查一下电商优惠信息",
    ]
    
    for i, intent in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"测试 {i}: {intent}")
        print(f"{'='*50}")
        
        try:
            result = agent_os.run(intent)
            print(f"\n✅ 完成")
        except Exception as e:
            print(f"❌ 出错: {e}")


if __name__ == '__main__':
    demo()