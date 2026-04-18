#!/usr/bin/env python3
"""
StoryMinta 3:30 Marathon Bot v8.1
Repo: https://github.com/akinolaogunlana/story-marathon_bot.git
210s/story | akinolaogunlana5@gmail.com | Autonomous
"""
import webbrowser,time,threading,json,os,subprocess,psutil,requests,re,logging
from pathlib import Path;from datetime import datetime

class Bot:
    def __init__(self):
        self.stories,self.visits=[],[[]];self.i,self.run=0,True;self.t=210
        self.s=requests.Session();self.l();self.stories=list(set(sum([re.findall(r'<loc>(https://storyminta[^<]+story[^<]+)</loc>',self.s.get(u,timeout=10).text,re.I)for u in["https://storyminta.com/sitemap.xml","https://zccvawdmicngfqlkxsoc.supabase.co/functions/v1/sitemap"]if 1],[])))
        self.log.info(f"🚀 {len(self.stories)} stories | 3:30 each")
    
    def l(self):
        Path("stats").mkdir();logging.basicConfig(level=20,format='%(asctime)s | %(message)s',handlers=[logging.FileHandler("stats/bot.log"),logging.StreamHandler()]);self.log=logging.getLogger("Bot")
    
    def kc(self):[p.kill()for p in psutil.process_iter(['name'])if'chrome'in p.info['name'].lower()]
    
    def o(self,u):subprocess.Popen(["chrome","--new-window",u,"--window-size=1200,800","--disable-web-security"]);self.log.info(f"🕐 [{self.i+1}/{len(self.stories)}] {u.split('/')[-1]}")
    
    def v(self,u):
        self.kc();time.sleep(1);self.o(u);s=time.time();while self.run and time.time()-s<self.t:self.log.info(f"⏳{int((time.time()-s)/self.t*100)}% | {int((self.t-(time.time()-s))//60)}:{int((self.t-(time.time()-s))%60):02d}");time.sleep(10)
        self.visits.append(u);self.log.info(f"✅ {len(self.visits)}/{len(self.stories)}");self.i=(self.i+1)%len(self.stories)
    
    def p(self):json.dump({"visits":len(self.visits),"total":len(self.stories),"current":self.i},open("stats/p.json","w"),indent=2)
    
    def r(self):while self.run and self.stories:[self.v(self.stories[self.i]),self.p()for _ in[0]]

if __name__=='__main__':b=Bot();try:b.r();except KeyboardInterrupt:b.p();print("🛑")
