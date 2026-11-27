#!/usr/bin/env python3
"""AI Signal Daily carousel slide builder (Claude-made slides, no credits).
Slide types: cover, point, steps, chart, quote, end, swap (free-swap card with screenshot), bill (monthly-cost list with total), code (folder tree / prompt / flow card), chat (you/AI example exchange + checklist), list (one category of a curated mega-list with progress dots), titlecard (series cover with kicker pill + two-tone headline + card-stack hero), versus (Before/After card pair, two-tone headline, one problem line + one fix line); see each function docstring.
Usage: python3 carousel.py spec.json  -> writes 02.jpg, 03.jpg ... into spec["outdir"] (default ".")
spec = {"total": 6, "start": 2, "outdir": "out",
  "theme":"dark" or "paper" (optional; paper = VISUAL STYLE v2), "slides": [
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
THEMES={"dark":dict(BG=(6,9,15),ACC=(61,245,200),WHITE=(245,247,250),MUTED=(139,152,165),CARD=(14,20,30),SOFT=(214,222,230)),
 "paper":dict(BG=(246,244,239),ACC=(0,122,99),WHITE=(16,19,24),MUTED=(128,134,142),CARD=(232,229,221),SOFT=(58,64,72))}
THEME="dark"; HL=(61,245,200)
def set_theme(name):
    """"dark" (default, mint on near-black) or "paper" (warm off-white, ink text, mint highlighter; see STYLE.md VISUAL STYLE v2)."""
    global THEME; THEME=name; globals().update(THEMES[name])
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
    text=norm(text); HF=IB if THEME=="paper" else ANTON; size=int(size*0.8) if THEME=="paper" else size; fnt=F(HF,size); lines=wrap(d,text,fnt,maxw)
    while len(lines)>3 and size>60: size-=6; fnt=F(HF,size); lines=wrap(d,text,fnt,maxw)
    lh=int(size*1.06)
    for ln in lines:
        ws=[d.textlength(w.strip("*")+" ",font=fnt) for w in ln]; tw=sum(ws)-d.textlength(" ",font=fnt)
        x=(W-tw)/2 if center else x0
        for w,wd in zip(ln,ws):
            if w.startswith("*") and THEME=="paper": d.rectangle((x-8,y+int(size*0.14),x+wd-d.textlength(" ",font=fnt)+8,y+int(size*1.02)),fill=HL); d.text((x,y),w.strip("*"),font=fnt,fill=WHITE)
            else: d.text((x,y),w.strip("*"),font=fnt,fill=ACC if w.startswith("*") else WHITE)
            x+=wd
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
    if THEME=="paper":
        img=Image.new("RGBA",(W,H),BG); lg=LOGO.resize((52,52)); m=Image.new("L",(52,52),0); ImageDraw.Draw(m).rounded_rectangle((0,0,51,51),12,fill=255)
        img.paste(lg,(48,44),m); d=ImageDraw.Draw(img)
        d.text((112,46),"AI Signal Daily",font=F(IB,26),fill=WHITE); d.text((112,76),"@aisignaldaily.news",font=F(IB,20),fill=MUTED)
        t=f"{n}/{total}"; tf=F(IB,26); tw=d.textlength(t,font=tf)
        d.rounded_rectangle((W-48-tw-32,50,W-48,92),21,fill=CARD); d.text((W-48-tw-16,55),t,font=tf,fill=WHITE)
        d.line((70,H-120,W-70,H-120),fill=(214,210,201),width=2); d.text((70,H-95),"aisignaldaily",font=F(IB,22),fill=MUTED)
        if swipe: s="SWIPE →"; d.text((W-70-d.textlength(s,font=F(IB,24)),H-97),s,font=F(IB,24),fill=ACC)
        return img,d
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
    img,d=layer(); y=head(d,s["headline"],300,s.get("size",110)); y=para(d,s.get("body",""),y+50,42,SOFT)
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
        v=b.get("display") or f'{b["value"]:g}{s.get("unit","")}'; d.text((330+L+16,y+16),v,font=F(IB,34),fill=WHITE) if 330+L+16+d.textlength(v,font=F(IB,34))<W-30 else d.text((330+L-16-d.textlength(v,font=F(IB,34)),y+16),v,font=F(IB,34),fill=BG)
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
    if s.get("follow"): para(d,s["follow"],y+110,30,MUTED)
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
    y=para(d,s.get("body",""),y+36,34,SOFT,940,False,70)
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
    """Bill slide (money or time: add "unit":"min" and "total_label":"For ONE idea"): {"type":"bill","headline":"*$305* A MONTH","items":[{"name":"Notion","plan":"Plus","price":10}, ...],"note":"Prices: official pricing pages, <date>"}"""
    img,d=layer(); y=head(d,s["headline"],170,s.get("size",110))+30
    items=s["items"]; tot=sum(i["price"] for i in items)
    d.rounded_rectangle((70,y,W-70,y+70*len(items)+150),28,fill=CARD); yy=y+30
    for i in items:
        d.text((110,yy),i["name"],font=F(IB,34),fill=WHITE); d.text((110+d.textlength(i["name"]+"  ",font=F(IB,34)),yy+4),i.get("plan",""),font=F(IM,28),fill=MUTED)
        u=s.get("unit","$"); p=(f'{i["price"]:g} min' if u=="min" else f'${i["price"]:g}/mo'); d.text((W-110-d.textlength(p,font=F(IB,34)),yy),p,font=F(IB,34),fill=(255,140,140)); yy+=70
    d.line((110,yy+5,W-110,yy+5),fill=(40,52,66),width=2)
    t=(f'~{tot:g} min' if s.get("unit")=="min" else f'${tot:,.2f}'.rstrip('0').rstrip('.')+"/mo"); d.text((110,yy+30),s.get("total_label","Every month"),font=F(IB,34),fill=WHITE); d.text((W-110-d.textlength(t,font=F(ANTON,64)),yy+12),t,font=F(ANTON,64),fill=ACC)
    y=yy+150
    if s.get("note"): para(d,s["note"],y+10,26,MUTED)
    return img
MONO=f"{HERE}/fonts/DejaVuSansMono.ttf"
def code(s,n,T):
    """Code/diagram card: {"type":"code","headline":"BUILD THE *MEMORY*","body":"optional 1-2 sentences",
    "lines":["vault/","├── raw/      everything captured","└── CLAUDE.md  the map"],"note":"optional tip"}
    Use for folder trees, prompts to copy, simple flows (A → B → C). Lines starting with '>' are drawn in mint."""
    img,d=layer(); y=head(d,s["headline"],170,s.get("size",100))
    if s.get("body"): y=para(d,s["body"],y+44,34,SOFT,940)
    lines=s["lines"]; fs=s.get("font",34); f=F(MONO,fs); lh=int(fs*1.5)
    top=y+40; d.rounded_rectangle((70,top,W-70,top+70+lh*len(lines)+30),26,fill=(14,18,26))
    for i,c in enumerate([(255,95,87),(254,188,46),(40,200,64)]): d.ellipse((100+i*34,top+22,120+i*34,top+42),fill=c)
    yy=top+70
    for ln in lines:
        col=ACC if ln.startswith(">") else (225,232,240); d.text((110,yy),ln.lstrip(">").rstrip(),font=f,fill=col); yy+=lh
    if s.get("note"): para(d,s["note"],yy+60,30,MUTED,940)
    return img
def chat(s,n,T):
    """Chat example: {"type":"chat","headline":"DROP ONE IDEA. *AI DOES THE REST*","you":"what the user types",
    "ai":"short AI reply","checks":[["Hook ideas","5"],["Carousel outline","8 slides"]],"label":"Real example, made with ChatGPT"}
    Only show outputs we actually generated (label it). Right bubble = you (mint), left = AI."""
    img,d=layer(); y=head(d,s["headline"],170,s.get("size",96))+40
    f=F(IM,32)
    def bubble(text,right,y):
        lines=[" ".join(l) for l in wrap(d,text,f,620)]; h=len(lines)*44+40; w=max(d.textlength(l,font=f) for l in lines)+56
        x0=W-90-w if right else 90; d.rounded_rectangle((x0,y,x0+w,y+h),26,fill=ACC if right else CARD)
        for i,l in enumerate(lines): d.text((x0+28,y+20+i*44),l,font=f,fill=BG if right else WHITE)
        return y+h+24
    y=bubble(s["you"],True,y); y=bubble(s["ai"],False,y)
    if s.get("checks"):
        d.rounded_rectangle((90,y,W-90,y+len(s["checks"])*72+24),24,fill=(14,20,30)); yy=y+18
        for a,b in s["checks"]:
            d.ellipse((116,yy+10,150,yy+44),fill=ACC); d.text((122,yy+8),"✓",font=F(IB,28),fill=BG)
            d.text((170,yy+8),a,font=F(IB,32),fill=WHITE); d.text((W-120-d.textlength(b,font=F(IB,32)),yy+8),b,font=F(IB,32),fill=ACC); yy+=72
        y=yy+24
    if s.get("label"): para(d,s["label"],y+20,26,MUTED)
    return img
def listing(s,n,T):
    """Curated list slide (one category of a big list): {"type":"list","kicker":"ROW 02 · 6 TOOLS","headline":"RESEARCH & *UNDERSTANDING*",
    "items":[{"name":"NotebookLM","sub":"google · free","desc":"Chat with your PDFs and notes","badge":"Free"}, ...],
    "progress":[12,30]}  First item is highlighted as the pick of the row. badge = short verified fact (e.g. "49k+ stars", "Free", "$10/mo")."""
    img,d=layer(); y=170
    if s.get("kicker"): d.text((70,y),s["kicker"],font=F(IB,28),fill=ACC); y+=50
    y=head(d,s["headline"],y,s.get("size",92),center=False,x0=70)+24
    for i,it in enumerate(s["items"][:7]):
        hl=(i==0); h=112
        d.rounded_rectangle((70,y,W-70,y+h),22,fill=(20,64,56) if hl else CARD, outline=ACC if hl else None, width=3 if hl else 0)
        nm=it["name"]; d.text((100,y+16),nm,font=F(IB,36),fill=WHITE)
        if it.get("sub"): d.text((100+d.textlength(nm+"  ",font=F(IB,36)),y+24),it["sub"],font=F(IM,24),fill=MUTED)
        d.text((100,y+64),it.get("desc","")[:58],font=F(IM,27),fill=SOFT)
        if it.get("badge"):
            b=it["badge"]; bf=F(IB,28); bw=d.textlength(b,font=bf)
            d.rounded_rectangle((W-100-bw-28,y+16,W-100,y+60),22,fill=ACC if hl else (40,52,66)); d.text((W-100-bw-14,y+22),b,font=bf,fill=BG if hl else WHITE)
        y+=h+14
    if s.get("progress"):
        a,b=s["progress"]; t=f"{a} / {b} collected"; d.text((70,y+16),t,font=F(IB,28),fill=WHITE)
        x=70+d.textlength(t+"   ",font=F(IB,28)); r=9
        for k in range(b):
            if x>W-80: break
            d.ellipse((x,y+24,x+2*r,y+24+2*r),fill=ACC if k<a else (50,62,76)); x+=2*r+6
    return img

def tone(d,l1,l2,y,size=88,x0=70,maxw=940):
    """Two-tone headline: line 1 ink, line 2 grey (the gg.designhub-style hierarchy). Left aligned, Inter Bold, tight leading."""
    f=F(IB,size); 
    for text,col in ((l1,WHITE),(l2,MUTED)):
        for ln in wrap(d,text,f,maxw): d.text((x0,y),' '.join(ln),font=f,fill=col); y+=int(size*1.08)
    return y
def check(d,cx,cy,r,col,ink):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=col); d.line([(cx-r*0.45,cy),(cx-r*0.1,cy+r*0.38),(cx+r*0.5,cy-r*0.35)],fill=ink,width=max(3,int(r*0.22)),joint="curve")
def dash(d,cx,cy,r,col,ink):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=col); d.line([(cx-r*0.45,cy),(cx+r*0.45,cy)],fill=ink,width=max(3,int(r*0.22)))
def titlecard(s,n,T):
    """Series cover, paper-friendly: {"type":"titlecard","kicker":"FIX IT · 01","line1":"Stop typing","line2":"*vague* prompts","sub":"one line promise"}
    Pill kicker + two-tone headline + a stack of tilted cards as the hero object (no people, no logos)."""
    img,d=layer(); y=150
    pill(d,70,y,s.get("kicker","SERIES"),HL if THEME=="paper" else ACC,(16,19,24) if THEME=="paper" else BG,32,26); y+=130
    t1=norm(s["line1"]); y=head(d,t1+" "+s["line2"],y,s.get("size",118),center=False,x0=70) if False else y
    f=F(IB,s.get("size",112))
    for text,col in ((s["line1"],WHITE),(s["line2"],MUTED)):
        for ln in wrap(d,text,f,940):
            x=70
            for w in ln:
                ww=d.textlength(w.strip("*")+" ",font=f)
                if w.startswith("*") and THEME=="paper": d.rectangle((x-8,y+16,x+ww-d.textlength(" ",font=f)+8,y+int(s.get("size",112)*0.98)),fill=HL); d.text((x,y),w.strip("*"),font=f,fill=WHITE)
                else: d.text((x,y),w.strip("*"),font=f,fill=ACC if w.startswith("*") else col)
                x+=ww
            y+=int(s.get("size",112)*1.06)
    if s.get("sub"): y=para(d,s["sub"],y+24,38,MUTED,940,False,70)
    # hero: three tilted cards
    cy=max(y+120,760)
    for ang,dx,fill in ((-9,-150,CARD),(6,150,(210,206,196) if THEME=="paper" else (30,42,56)),(-2,0,HL if THEME=="paper" else ACC)):
        c=Image.new("RGBA",(420,520),(0,0,0,0)); cd=ImageDraw.Draw(c); cd.rounded_rectangle((0,0,419,519),38,fill=fill)
        for k,wd in enumerate((300,240,180)): cd.rounded_rectangle((44,60+k*54,44+wd,84+k*54),12,fill=(16,19,24) if fill in (HL,ACC) else MUTED)
        c=c.rotate(ang,expand=True,resample=Image.BICUBIC); img.alpha_composite(c,(int(W/2-c.width/2+dx),int(cy-60)))
    return img
def versus(s,n,T):
    """Before/After slide (our own version of the Don't/Do pair; fictional or our own examples, never brand logos):
    {"type":"versus","num":"01","line1":"Say who it is for","line2":"not just what you want","problem":"grey one-liner (what goes wrong)","fix":"ink one-liner (the fix)",
     "before":{"label":"Before","title":"Write me an email","lines":["no audience","no goal"],"caption":"Generic and forgettable."},
     "after":{"label":"After","title":"Write 3 lines to a customer who paid late. Friendly, one ask.","lines":["audience","goal"],"caption":"Specific and usable."},"note":"Example, made with ChatGPT"}"""
    img,d=layer(); y=140
    d.text((70,y),s["num"]+".",font=F(IB,34),fill=MUTED); y+=60
    y=tone(d,s["line1"],s["line2"],y,s.get("size",84))+14
    y=para(d,s["problem"],y,32,MUTED,940,False,70); y=para(d,s["fix"],y+6,32,WHITE,940,False,70,IB)+24
    cw=(W-140-28)//2; ch=s.get("card_h",470)
    for i,key in enumerate(("before","after")):
        c=s[key]; x0=70+i*(cw+28); good=(key=="after")
        fill=(16,19,24) if (good and THEME=="paper") else (CARD if not good else (20,64,56)); ink=(245,247,250) if good else (MUTED if THEME=="paper" else WHITE)
        d.rounded_rectangle((x0,y,x0+cw,y+ch),34,fill=fill)
        tf=F(IB,36 if good else 34); yy=y+36
        for ln in wrap(d,c["title"],tf,cw-64)[:6]: d.text((x0+32,yy),' '.join(ln),font=tf,fill=ink); yy+=48
        yy=max(yy+18,y+ch-40-len(c.get("lines",[]))*52)
        for t in c.get("lines",[])[:4]:
            (check if good else dash)(d,x0+48,yy+20,16,HL if good else (180,176,168),(16,19,24) if good else (255,255,255))
            d.text((x0+80,yy+4),t,font=F(IM,28),fill=ink); yy+=52
        pill(d,x0,y+ch+22,c.get("label","After" if good else "Before"),(16,19,24) if THEME=="paper" and good else (HL if good else CARD),(245,247,250) if THEME=="paper" and good else ((6,9,15) if good else WHITE),28,22)
        yc=y+ch+22+70
        for ln in wrap(d,c.get("caption",""),F(IM,28),cw)[:2]: d.text((x0,yc),' '.join(ln),font=F(IM,28),fill=MUTED if not good else WHITE); yc+=38
    if s.get("note"): para(d,s["note"],y+ch+175,26,MUTED,940,False,70)
    return img
R={"titlecard":titlecard,"versus":versus,"cover":cover,"point":point,"steps":steps,"chart":chart,"quote":quote,"end":end,"swap":swap,"bill":bill,"code":code,"chat":chat,"list":listing}
def main(p):
    s=json.load(open(p)); set_theme(s.get("theme","dark")); T=s["total"]; n=s.get("start",2); out=s.get("outdir","."); os.makedirs(out,exist_ok=True); files=[]
    for sl in s["slides"]:
        f=f"{out}/{n:02d}.jpg"
        bg,_=base(n,T,swipe=sl["type"]!="end"); L=R[sl["type"]](sl,n,T); bb=L.getbbox() or (0,0,W,H)
        top,bot=130,H-140; h=bb[3]-bb[1]; y0=top+max(0,((bot-top)-h)//2)
        if THEME=="paper" and sl["type"] in ("versus","titlecard"): y0=top
        bg.alpha_composite(L.crop((0,bb[1],W,bb[3])),(0,y0)); bg.convert("RGB").save(f,quality=92); files.append(f); n+=1
    print(json.dumps(files))
if __name__=="__main__": main(sys.argv[1])
