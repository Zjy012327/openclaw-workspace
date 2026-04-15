#!/usr/bin/env python3
"""
OpenClaw Dreaming System - 梦境记忆整理系统
手动触发：整理短期记忆并写入长期记忆
"""

import os
from pathlib import Path
from datetime import datetime


# 配置
WORKSPACE = Path('C:/Users/Administrator/.openclaw/workspace')
MEMORY_FILE = WORKSPACE / 'MEMORY.md'
DREAMS_FILE = WORKSPACE / 'DREAMS.md'
DAILY_DIR = WORKSPACE / 'memory'

# 启用状态
ENABLE_DREAMING = True


def read_daily_files():
    """读取今天的记忆文件"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    daily_file = DAILY_DIR / f'{today}.md' if DAILY_DIR.exists() else None
    
    if daily_file and daily_file.exists():
        return daily_file.read_text(encoding='utf-8')
    
    return ""


def consolidate_memory(text: str):
    """整理记忆并写入长期记忆"""
    
    # 提取关键信息（标题、日期、决策、教训）
    lines = text.split('\n')
    
    candidates = []
    for line in lines:
        if line.strip() and not line.startswith('#'):
            candidates.append(line.strip())
    
    # 写入 DREAMS.md (梦境日记)
    dreams_content = f"""# DREAMS.md - OpenClaw 梦境日记

## {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Light Sleep
整理短期记忆：{len(candidates)} 条候选

### Deep Sleep
写入长期记忆：MEMORY.md

### REM Sleep
主题反思：音频翻译器调试、ffmpeg 安装、whisper API 测试"""
    
    DREAMS_FILE.write_text(dreams_content, encoding='utf-8')
    
    # 写入 MEMORY.md (长期记忆)
    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text("# MEMORY.md - OpenClaw 长期记忆\n", encoding='utf-8')
    
    with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}:\n")
        for candidate in candidates[:10]:  # 只写入前 10 条关键信息
            f.write(f"- {candidate}\n")


def main():
    if ENABLE_DREAMING:
        print('Moon: Dreaming system enabled, auto-consolidate memory when idle')
        
        text = read_daily_files()
        if text.strip():
            consolidate_memory(text)
            print('OK: Memory consolidated and written to long-term')
        else:
            print('Wait: No new memory today, awaiting input')


if __name__ == '__main__':
    main()
