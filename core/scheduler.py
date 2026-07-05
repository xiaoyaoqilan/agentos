"""Scheduler - 定时调度器"""
import logging
import time
import threading
from datetime import datetime
from typing import Dict, Callable, Optional

logger = logging.getLogger(__name__)


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.running = False
        self.thread = None
    
    def add_task(self, name: str, cron_expr: str, task_func: Callable, args: tuple = (), kwargs: dict = None):
        """添加定时任务"""
        if kwargs is None:
            kwargs = {}
        
        self.tasks[name] = {
            'cron': cron_expr,
            'func': task_func,
            'args': args,
            'kwargs': kwargs,
            'last_run': None
        }
        logger.info(f"添加定时任务: {name} - {cron_expr}")
    
    def remove_task(self, name: str):
        """移除定时任务"""
        if name in self.tasks:
            del self.tasks[name]
            logger.info(f"移除定时任务: {name}")
    
    def parse_cron(self, cron_expr: str) -> tuple:
        """解析cron表达式"""
        parts = cron_expr.split()
        if len(parts) != 5:
            return None
        
        minute, hour, day, month, weekday = parts
        
        return (minute, hour, day, month, weekday)
    
    def should_run(self, cron_expr: str, last_run: Optional[datetime] = None) -> bool:
        """判断是否应该执行任务"""
        parsed = self.parse_cron(cron_expr)
        if not parsed:
            return False
        
        minute, hour, day, month, weekday = parsed
        now = datetime.now()
        
        if minute != '*' and int(minute) != now.minute:
            return False
        if hour != '*' and int(hour) != now.hour:
            return False
        if day != '*' and int(day) != now.day:
            return False
        if month != '*' and int(month) != now.month:
            return False
        if weekday != '*' and int(weekday) != now.weekday():
            return False
        
        if last_run:
            if last_run.minute == now.minute and last_run.hour == now.hour:
                return False
        
        return True
    
    def run_task(self, task_name: str):
        """执行任务"""
        task = self.tasks.get(task_name)
        if not task:
            return
        
        try:
            logger.info(f"执行任务: {task_name}")
            task['func'](*task['args'], **task['kwargs'])
            task['last_run'] = datetime.now()
            logger.info(f"任务执行完成: {task_name}")
        except Exception as e:
            logger.error(f"任务执行失败: {task_name} - {e}")
    
    def start(self):
        """启动调度器"""
        self.running = True
        logger.info("定时调度器启动")
        
        def loop():
            while self.running:
                now = datetime.now()
                for name, task in self.tasks.items():
                    if self.should_run(task['cron'], task.get('last_run')):
                        self.run_task(name)
                time.sleep(60)
        
        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("定时调度器停止")


scheduler = TaskScheduler()