#!/bin/bash
# Deploy: https://github.com/akinolaogunlana/story-marathon_bot.git
pip install -r requirements.txt 2>/dev/null||pip3 install -r requirements.txt
mkdir -p stats
echo "🚀 StoryMinta 3:30 Bot Deployed!"
nohup python3 marathon_bot.py > bot.log 2>&1 &
echo $! > bot.pid
echo "✅ PID: $(cat bot.pid) | Stats: stats/p.json"
