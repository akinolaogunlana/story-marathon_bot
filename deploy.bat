@echo off
pip install -r requirements.txt
mkdir stats
echo 🚀 StoryMinta 3:30 Bot Deployed!
start /B python marathon_bot.py
echo ✅ Running! Check stats/p.json
pause
