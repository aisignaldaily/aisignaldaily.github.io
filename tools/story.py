#!/usr/bin/env python3
"""AI Signal Daily Story cards (1080x1920, free). Usage: python3 story.py spec.json
spec = {"outdir":"out", "cards":[
  {"type":"newpost", "kicker":"NEW POST", "headline":"STOP *OVERPAYING* THIS BLACK FRIDAY", "sub":"Tap our profile to see it"},
  {"type":"question", "kicker":"QUICK QUESTION", "headline":"WOULD YOU LET AI *SHOP* FOR YOU?", "options":["YES","NO"], "sub":"Reply in DM: YES or NO"}
]}  -> writes story_1.jpg, story_2.jpg ...
Keep text inside the safe area (220 px top, 380 px bottom)."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
W,H=1080,1920; BG=(6,9,15); ACC=(61,245,200); WHITE=(245,247,250); MUTED=(139,152,165); CARD=(14,20,30)
ANTON=f"{HERE}/fonts/Anton-Regular.ttf"; IB=f"{HERE}/fonts/Inter-Bold.otf"; IM=f"{HERE}/fonts/Inter-Medium.otf"
F=ImageFont.truetype; LOGO=Image.open(f"{HERE}/logo.png").convert("RGBA")
from carousel import norm, wrap
def head(d,text,y,size=130):
    text=norm(text); fnt=F(ANTON,size); lines=wrap(d,text,fnt,940)
    while len(lines)>4 and size>80: size-=8; fnt=F(ANTON,size); lines=wrap(d,text,fnt,940)
    for ln in lines:
        ws=[d.textlength(w.strip("*")+" ",font=fnt) for w in ln]; x=(W-sum(ws)+d.textlength(" ",font=fnt))/2
        for w,wd in zip(ln,ws): d.text((x,y),w.strip("*"),font=fnt,fill=ACC if w.startswith("*") else WHITE); x+=wd
        y+=int(size*1.06)
    return y
def center(d,t,y,f,col):
    d.text(((W-d.textlength(t,font=f))/2,y),t,font=f,fill=col)
def base():
    img=Image.new("RGB",(W,H),BG); g=Image.new("RGB",(W,H),BG); gd=ImageDraw.Draw(g)
    gd.ellipse((W*0.05,H*0.05,W*0.95,H*0.55),fill=(16,62,54)); g=g.filter(ImageFilter.GaussianBlur(220))
    img=Image.blend(img,g,0.95).convert("RGBA"); img.alpha_composite(LOGO.resize((110,110)),(int(W/2-55),260))
    d=ImageDraw.Draw(img); center(d,"AI Signal Daily",F(IB,40),WHITE) if False else None
    center(d,"AI Signal Daily",400,F(IB,40),WHITE); center(d,"@aisignaldaily.news",452,F(IB,30),MUTED); return img,d
def newpost(c):
    img,d=base(); kf=F(IB,36); k=c.get("kicker","NEW POST"); tw=d.textlength(k,font=kf)
    d.rounded_rectangle(((W-tw)/2-30,600,(W+tw)/2+30,664),32,fill=ACC); center(d,k,610,kf,BG)
    y=head(d,c["headline"],740,c.get("size",130))
    center(d,c.get("sub","Tap our profile to see it 👆").replace("👆",""),y+60,F(IM,40),WHITE)
    center(d,"↑",y+130,F(IB,90),ACC); return img
def question(c):
    img,d=base(); kf=F(IB,36); k=c.get("kicker","QUICK QUESTION"); tw=d.textlength(k,font=kf)
    d.rounded_rectangle(((W-tw)/2-30,600,(W+tw)/2+30,664),32,fill=ACC); center(d,k,610,kf,BG)
    y=head(d,c["headline"],740,c.get("size",120))+50
    for o in c.get("options",["YES","NO"]):
        d.rounded_rectangle((180,y,W-180,y+120),60,fill=CARD,outline=ACC,width=4); center(d,o,y+28,F(IB,52),WHITE); y+=150
    center(d,c.get("sub","Reply in DM"),y+20,F(IM,38),MUTED); return img
R={"newpost":newpost,"question":question}
def main(p):
    s=json.load(open(p)); out=s.get("outdir","."); os.makedirs(out,exist_ok=True); files=[]
    for i,c in enumerate(s["cards"],1):
        f=f"{out}/story_{i}.jpg"; R[c["type"]](c).convert("RGB").save(f,quality=92); files.append(f)
    print(json.dumps(files))
if __name__=="__main__": main(sys.argv[1])
