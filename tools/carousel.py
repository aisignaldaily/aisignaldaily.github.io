#!/usr/bin/env python3
"""AI Signal Daily carousel slide builder (Claude-made slides, no credits).
Slide types: cover, point, steps, chart, quote, end, swap (free-swap card with screenshot), bill (monthly-cost list with total), code (folder tree / prompt / flow card); see each function docstring.
Usage: python3 carousel.py spec.json  -> writes 02.jpg, 03.jpg ... into spec["outdir"] (default ".")
spec = {"total": 6, "start": 2, "outdir": "out",
  "slides": [
    {"type":"point", "headline":"ONE CART FOR *EVERY STORE*", "body":"short explanation, 1-2 sentences"},
    {"type":"steps", "headline":"HOW TO *USE IT*", "steps":["Find a product...","Tap Add to cart","Wait for the alert"], "note":"US only"},
    {"type":"chart", "headline":"IT'S *290X* CHEAPER", "bars":[{"label":"Before","value":290},{"label":"After","value":1}], "unit":"x cost", "note":"Source: ..."},
    {"type":"quote", "headline":"WHAT THEY SAID", "quote":"exact short quote", "who":"Company blog"},
    {"type":"end", "text":"SEND THIS TO THE FRIEND WHO *ALWAYS PAYS FULL PRICE*"}
  ]}
Wrap words for mint highlight in *...* (multi-word spans allowed)."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE=os.path.dirname(os.path.abspath(__file__))
W,H=1080,1350; BG=(6,9,15); ACC=(61,245,200); WHITE=(245,247,250); MUTED=(139,152,165); CARD=(14,20,30)
ANTON=f"{HERE}/fonts/Anton-Regular.ttf"; IB=f"{HERE}/fonts/Inter-Bold.otf"; IM=f"{HERE}/fonts/Inter-Medium.otf"
F=ImageFont.truetype; LOGO=Image.open(f"{HERE}/logo.png").convert("RGBA")

def norm(text):
    out=[]; on=False
    for w in text.split():
        st=w.startswith("*"); en=w.endswith("*") and len(w)>1; core=w.strip("*")
        if st: on=True
        out.append(("*"+core+"*") if on else core)
        if en or (st and w.count("*")>=2): on=False
    return " ".join(out)
def wrap(d,text,fnt,maxw):
    lines,cur=[],[]
    for w in text.split():
        t=" ".join(cur+[w]).replace("*","")
        if d.textlength(t,font=fnt)<=maxw or not cur: cur.append(w)
        else: lines.append(cur); cur=[w]
    lines.append(cur); return lines
def head(d,text,y,size=104,maxw=940,center=True,x0=70):
    text=norm(text); fnt=F(ANTON,size); lines=wrap(d,text,fnt,maxw)
    while len(lines)>3 and size>72: size-=6; fnt=F(ANTON,size); lines=wrap(d,text,fnt,maxw)
    lh=int(size*1.06)
    for ln in lines:
        ws=[d.textlength(w.strip("*")+" ",font=fnt) for w in ln]; tw=sum(ws)-d.textlength(" ",font=fnt)
        x=(W-tw)/2 if center else x0
        for w,wd in zip(ln,ws): d.text((x,y),w.strip("*"),font=fnt,fill=ACC if w.startswith("*") else WHITE); x+=wd
        y+=lh
    return y
def para(d,text,y,size=40,col=WHITE,maxw=920,center=True,x0=80,font=IM):
    fnt=F(font,size)
    for ln in wrap(d,text,fnt,maxw):
        s=" ".join(ln); x=(W-d.textlength(s,font=fnt))/2 if center else x0
        d.text((x,y),s,font=fnt,fill=col); y+=int(size*1.38)
    return y
def layer():
    L=Image.new("RGBA",(W,H),(0,0,0,0)); return L,ImageDraw.Draw(L)
def base(n,total,swipe=True):
    img=Image.new("RGB",(W,H),BG)
    glow=Image.new("RGB",(W,H),BG); gd=ImageDraw.Draw(glow)
    gd.ellipse((W*0.15,-H*0.25,W*0.85,H*0.35),fill=(16,60,52)); glow=glow.filter(ImageFilter.GaussianBlur(160))
    img=Image.blend(img,glow,0.9).convert("RGBA")
    img.alpha_composite(LOGO.resize((52,52)),(48,44)); d=ImageDraw.Draw(img)
    d.text((112,46),"AI Signal Daily",font=F(IB,26),fill=WHITE); d.text((112,76),"@aisignaldaily.news",font=F(IB,20),fill=MUTED)
    t=f"{n}/{total}"; tf=F(IB,26); tw=d.textlength(t,font=tf)
    d.rounded_rectangle((W-48-tw-32,50,W-48,92),21,fill=CARD); d.text((W-48-tw-16,55),t,font=tf,fill=WHITE)
    d.line((70,H-120,W-70,H-120),fill=(30,40,52),width=2)
    d.text((70,H-95),"aisignaldaily",font=F(IB,22),fill=MUTED)
    s="SWIPE →"
    if swipe: d.text((W-70-d.textlength(s,font=F(IB,24)),H-97),s,font=F(IB,24),fill=ACC)
    return img,d
def point(s,n,T):
    img,d=layer(); y=head(d,s["headline"],300,s.get("size",110)); y=para(d,s.get("body",""),y+50,42,(214,222,230))
    if s.get("note"): para(d,s["note"],y+40,28,MUTED)
    return img
def steps(s,n,T):
    img,d=layer(); y=head(d,s["headline"],220,104)+40
    for i,st in enumerate(s["steps"],1):
        d.rounded_rectangle((70,y,W-70,y+150),28,fill=CARD)
        d.ellipse((100,y+40,170,y+110),fill=ACC); num=str(i); nf=F(ANTON,46); d.text((135-d.textlength(num,font=nf)/2,y+44),num,font=nf,fill=BG)
        yy=y+38; fnt=F(IB,36)
        for ln in wrap(d,st,fnt,760)[:2]: d.text((200,yy),' '.join(ln),font=fnt,fill=WHITE); yy+=46
        y+=175
    if s.get("note"): para(d,s["note"],y+10,30,MUTED)
    return img
def chart(s,n,T):
    img,d=layer(); y=head(d,s["headline"],220,104)+60
    bars=s["bars"]; mx=max(b["value"] for b in bars) or 1; bw=W-140-260
    for b in bars:
        d.text((70,y+18),b["label"],font=F(IB,34),fill=WHITE)
        L=max(8,int(bw*b["value"]/mx)); d.rounded_rectangle((330,y,330+L,y+76),16,fill=ACC if b.get("hl",b["value"]==mx) else (60,78,96))
        v=f'{b["value"]:g}{s.get("unit","")}'; d.text((330+L+16,y+16),v,font=F(IB,34),fill=WHITE) if 330+L+16+d.textlength(v,font=F(IB,34))<W-30 else d.text((330+L-16-d.textlength(v,font=F(IB,34)),y+16),v,font=F(IB,34),fill=BG)
        y+=120
    if s.get("note"): para(d,s["note"],y+30,30,MUTED)
    return img
def quote(s,n,T):
    img,d=layer(); y=head(d,s.get("headline",""),220,90)+50
    d.rounded_rectangle((70,y,W-70,y+520),32,fill=CARD); d.text((110,y+10),"“",font=F(ANTON,180),fill=ACC)
    yy=para(d,s["quote"],y+170,46,WHITE,820,False,120,IB); para(d,"— "+s.get("who",""),yy+20,32,MUTED,820,False,120)
    return img
def end(s,n,T):
    img,d=layer(); img.alpha_composite(LOGO.resize((120,120)),(int(W/2-60),100)); d=ImageDraw.Draw(img)
    y=head(d,s["text"],290,108)
    d.rounded_rectangle((130,y+50,W-130,y+160),55,fill=ACC); t='Comment "AI" for today\'s tools'; tf=F(IB,40); d.text(((W-d.textlength(t,font=tf))/2,y+80),t,font=tf,fill=BG)
    y=para(d,"+ our free AI toolkit, straight to your DMs",y+190,32,WHITE)
    t="Follow @aisignaldaily.news"; d.text(((W-d.textlength(t,font=tf))/2,y+40),t,font=tf,fill=WHITE)
    return img
def icon_cart(d,cx,cy,sc=1.0,col=ACC,w=10):
    # simple line-art shopping cart
    P=lambda x,y:(cx+x*sc,cy+y*sc)
    d.line([P(-170,-110),P(-120,-110),P(-70,70),P(130,70)],fill=col,width=w,joint="curve")
    d.line([P(-100,-50),P(170,-50),P(140,30),P(-80,30)],fill=col,width=w,joint="curve")
    for x in (-50,110): d.ellipse([P(x-22,95),P(x+22,139)],outline=col,width=w)
def cover(s,n,T):
    img,d=layer()
    if s.get("icon")=="cart":
        glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow); icon_cart(gd,W/2,330,1.25,(61,245,200,255),26)
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18))); d=ImageDraw.Draw(img); icon_cart(d,W/2,330,1.25,ACC,12)
    y=head(d,s["headline"],560,s.get("size",132))
    if s.get("sub"): y=para(d,s["sub"],y+30,36,WHITE,980)
    return img
def pill(d,x,y,text,fill,ink,size=34,pad=26):
    f=F(IB,size); w=d.textlength(text,font=f)+2*pad; d.rounded_rectangle((x,y,x+w,y+size+30),(size+30)//2,fill=fill); d.text((x+pad,y+13),text,font=f,fill=ink); return x+w
def swap(s,n,T):
    """Free-swap slide: {"type":"swap","num":"01","paid":"Notion Plus","free":"AppFlowy","price":"$10/mo",
    "headline":"NOTION, *WITHOUT THE BILL*","body":"1-2 sentences","image":"local screenshot path (official page, no people)",
    "tags":["Notes","Open source","Self-host"],"note":"Needs: download + install (5 min)"}"""
    img,d=layer(); y=150
    d.text((70,y-20),s["num"],font=F(ANTON,150),fill=ACC)
    nx=70+d.textlength(s["num"],font=F(ANTON,150))+30
    d.text((nx,y+40),f'{s["paid"]}  →  {s["free"]}',font=F(IB,34),fill=WHITE)
    d.text((nx,y+90),f'{s["price"]}  →  $0',font=F(IB,34),fill=MUTED)
    y=head(d,s["headline"],y+200,s.get("size",88),center=False,x0=70)
    y=para(d,s.get("body",""),y+36,34,(214,222,230),940,False,70)
    if s.get("image") and os.path.exists(s["image"]):
        im=Image.open(s["image"]).convert("RGB"); maxw,maxh=W-140,360
        r=min(maxw/im.width,maxh/im.height); im=im.resize((int(im.width*r),int(im.height*r)))
        fr=Image.new("RGBA",(im.width+16,im.height+16),(0,0,0,0)); ImageDraw.Draw(fr).rounded_rectangle((0,0,fr.width-1,fr.height-1),18,fill=(40,52,66))
        fr.paste(im,(8,8)); img.alpha_composite(fr,(int((W-fr.width)/2),int(y+24))); y+=fr.height+44
    x=70
    for t in s.get("tags",[])[:4]: x=pill(d,x,y,t,CARD,WHITE,28,20)+12
    y+=80
    x=pill(d,70,y,"YOU PAY "+s["price"],(255,107,107),BG,34); pill(d,x+16,y,"FREE OPTION $0",ACC,BG,34)
    if s.get("note"): para(d,s["note"],y+90,28,MUTED,940,False,70)
    return img
def bill(s,n,T):
    """Bill slide: {"type":"bill","headline":"*$305* A MONTH","items":[{"name":"Notion","plan":"Plus","price":10}, ...],"note":"Prices: official pricing pages, <date>"}"""
    img,d=layer(); y=head(d,s["headline"],170,s.get("size",110))+30
    items=s["items"]; tot=sum(i["price"] for i in items)
    d.rounded_rectangle((70,y,W-70,y+70*len(items)+150),28,fill=CARD); yy=y+30
    for i in items:
        d.text((110,yy),i["name"],font=F(IB,34),fill=WHITE); d.text((110+d.textlength(i["name"]+"  ",font=F(IB,34)),yy+4),i.get("plan",""),font=F(IM,28),fill=MUTED)
        p=f'${i["price"]:g}/mo'; d.text((W-110-d.textlength(p,font=F(IB,34)),yy),p,font=F(IB,34),fill=(255,140,140)); yy+=70
    d.line((110,yy+5,W-110,yy+5),fill=(40,52,66),width=2)
    t=f'${tot:,.2f}'.rstrip('0').rstrip('.')+"/mo"; d.text((110,yy+30),"Every month",font=F(IB,34),fill=WHITE); d.text((W-110-d.textlength(t,font=F(ANTON,64)),yy+12),t,font=F(ANTON,64),fill=ACC)
    y=yy+150
    if s.get("note"): para(d,s["note"],y+10,26,MUTED)
    return img
MONO=f"{HERE}/fonts/DejaVuSansMono.ttf"
def code(s,n,T):
    """Code/diagram card: {"type":"code","headline":"BUILD THE *MEMORY*","body":"optional 1-2 sentences",
    "lines":["vault/","├── raw/      everything captured","└── CLAUDE.md  the map"],"note":"optional tip"}
    Use for folder trees, prompts to copy, simple flows (A → B → C). Lines starting with '>' are drawn in mint."""
    img,d=layer(); y=head(d,s["headline"],170,s.get("size",100))
    if s.get("body"): y=para(d,s["body"],y+44,34,(214,222,230),940)
    lines=s["lines"]; fs=s.get("font",34); f=F(MONO,fs); lh=int(fs*1.5)
    top=y+40; d.rounded_rectangle((70,top,W-70,top+70+lh*len(lines)+30),26,fill=(14,18,26))
    for i,c in enumerate([(255,95,87),(254,188,46),(40,200,64)]): d.ellipse((100+i*34,top+22,120+i*34,top+42),fill=c)
    yy=top+70
    for ln in lines:
        col=ACC if ln.startswith(">") else (225,232,240); d.text((110,yy),ln.lstrip(">").rstrip(),font=f,fill=col); yy+=lh
    if s.get("note"): para(d,s["note"],yy+60,30,MUTED,940)
    return img
R={"cover":cover,"point":point,"steps":steps,"chart":chart,"quote":quote,"end":end,"swap":swap,"bill":bill,"code":code}
def main(p):
    s=json.load(open(p)); T=s["total"]; n=s.get("start",2); out=s.get("outdir","."); os.makedirs(out,exist_ok=True); files=[]
    for sl in s["slides"]:
        f=f"{out}/{n:02d}.jpg"
        bg,_=base(n,T,swipe=sl["type"]!="end"); L=R[sl["type"]](sl,n,T); bb=L.getbbox() or (0,0,W,H)
        top,bot=130,H-140; h=bb[3]-bb[1]; y0=top+max(0,((bot-top)-h)//2)
        bg.alpha_composite(L.crop((0,bb[1],W,bb[3])),(0,y0)); bg.convert("RGB").save(f,quality=92); files.append(f); n+=1
    print(json.dumps(files))
if __name__=="__main__": main(sys.argv[1])
