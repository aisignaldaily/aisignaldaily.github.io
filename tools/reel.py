#!/usr/bin/env python3
"""AI Signal Daily Reel builder. Works anywhere with python3+Pillow+ffmpeg+curl (incl. the Higgsfield sandbox).
Usage: python3 reel.py spec.json
spec = {
  "beats": [ {"clip": "<url or path to mp4, or \"dark\" for a free animated brand background>", "text": "HEADLINE with *mint* words", "sub": "optional small line", "dur": 3.2}, ... ],
  "end":   {"text": "SEND THIS TO SOMEONE WHO *...*", "dur": 2.6},
  "audio": "<url or path to sound bed (no music)>",   # optional; else silent
  "audio_volume": 0.9,
  "ai_label": true,
  "out": "reel.mp4"
}
Output: 1080x1920, 30fps, H.264+AAC, crossfades between beats, beat counter, safe-area text, cover.jpg (first frame)."""
import json, os, subprocess, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
BG=(6,9,15); ACC=(61,245,200); WHITE=(245,247,250); MUTED=(139,152,165)
ANTON=f"{HERE}/fonts/Anton-Regular.ttf"; IB=f"{HERE}/fonts/Inter-Bold.otf"; IM=f"{HERE}/fonts/Inter-Medium.otf"
F=ImageFont.truetype
LOGO=Image.open(f"{HERE}/logo.png").convert("RGBA")
XF=0.35  # crossfade seconds

def dark_bg(name, dur):
    # free animated brand background: dark navy with a slowly drifting mint glow
    from PIL import ImageFilter
    big=Image.new("RGB",(int(W*1.3),int(H*1.3)),BG); gd=ImageDraw.Draw(big)
    gd.ellipse((big.width*0.1,big.height*0.05,big.width*0.9,big.height*0.55),fill=(18,70,60))
    big=big.filter(ImageFilter.GaussianBlur(200)); big.save("_darkbg.png")
    subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-framerate","30","-i","_darkbg.png","-vf",
      f"crop={W}:{H}:x='(in_w-{W})/2+60*sin(t/2)':y='(in_h-{H})/2+80*cos(t/3)',format=yuv420p","-t",str(dur+1),
      "-c:v","libx264","-preset","veryfast","-crf","22",name],check=True)
    return name

def fetch(src, name, dur=6):
    if src=="dark": return dark_bg(name, dur)
    if os.path.exists(src): return src
    subprocess.run(["curl","-sSfL","-o",name,src],check=True); return name

def wrap(d,text,fnt,maxw):
    lines,cur=[],[]
    for w in text.split():
        t=" ".join(cur+[w]).replace("*","")
        if d.textlength(t,font=fnt)<=maxw or not cur: cur.append(w)
        else: lines.append(cur); cur=[w]
    lines.append(cur); return lines

def norm(text):
    # allow *multi word* highlights: mark every word inside a *...* span
    out=[]; on=False
    for w in text.split():
        st=w.startswith("*"); en=w.endswith("*") and len(w)>1
        core=w.strip("*")
        if st: on=True
        out.append(("*"+core+"*") if on else core)
        if en or (st and w.count("*")>=2): on=False
    return " ".join(out)

def head(d,text,y_bottom,size):
    text=norm(text)
    fnt=F(ANTON,size); lines=wrap(d,text,fnt,940); lh=int(size*1.08)
    while len(lines)>4 and size>70:
        size-=8; fnt=F(ANTON,size); lines=wrap(d,text,fnt,940); lh=int(size*1.08)
    y=y_bottom-lh*len(lines)
    for ln in lines:
        ws=[d.textlength(w.strip("*")+" ",font=fnt) for w in ln]
        x=(W-sum(ws)+d.textlength(" ",font=fnt))/2
        for w,wd in zip(ln,ws):
            s=w.strip("*"); d.text((x+4,y+4),s,font=fnt,fill=(0,0,0,190)); d.text((x,y),s,font=fnt,fill=ACC if w.startswith("*") else WHITE); x+=wd
        y+=lh

def brand(img,d,y=230):
    pw=430; x0=(W-pw)//2
    d.rounded_rectangle((x0,y,x0+pw,y+84),42,fill=(6,9,15,190))
    img.alpha_composite(LOGO.resize((64,64)),(x0+14,y+10))
    d.text((x0+92,y+12),"AI Signal Daily",font=F(IB,30),fill=WHITE)
    d.text((x0+92,y+46),"@aisignaldaily.news",font=F(IB,22),fill=MUTED)

def beat_layer(path,b,i,n,ai,dark=False):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); g=Image.new("RGBA",(W,H)); gd=ImageDraw.Draw(g)
    for yy in range(760,H): gd.line((0,yy,W,yy),fill=(6,9,15,int(min(235,(yy-760)/650*255))))
    img.alpha_composite(g); d=ImageDraw.Draw(img); brand(img,d)
    yb=1150 if dark else 1470
    head(d,b["text"],yb,b.get("size",112))
    if b.get("sub"):
        sf=F(IM,34); s=b["sub"]; d.text(((W-d.textlength(s,font=sf))/2,yb+22),s,font=sf,fill=MUTED)
    t=f"{i}/{n}"; tf=F(IB,26); tw=d.textlength(t,font=tf)
    d.rounded_rectangle((W-70-tw-28,240,W-70,282),21,fill=(6,9,15,200)); d.text((W-70-tw-14,245),t,font=tf,fill=WHITE)
    if ai:
        tf2=F(IB,22); s="Made with AI"; d.text((W-70-d.textlength(s,font=tf2),292),s,font=tf2,fill=MUTED)
    img.save(path)

def end_card(path,e):
    img=Image.new("RGBA",(W,H),BG+(255,)); d=ImageDraw.Draw(img); brand(img,d,300)
    head(d,e["text"],1150,98)
    tf=F(IB,46); t='Comment "AI" for today\'s tools'
    d.rounded_rectangle((120,1220,W-120,1320),50,fill=ACC); d.text(((W-d.textlength(t,font=tf))/2,1243),t,font=tf,fill=BG)
    t2="Follow @aisignaldaily.news"; d.text(((W-d.textlength(t2,font=tf))/2,1370),t2,font=tf,fill=WHITE)
    img.convert("RGB").save(path)

def main(spec_path):
    s=json.load(open(spec_path)); beats=s["beats"]; n=len(beats); ai=s.get("ai_label",True); out=s.get("out","reel.mp4")
    parts=[]
    for i,b in enumerate(beats):
        clip=fetch(b.get("clip","dark"),f"_clip{i}.mp4",b.get("dur",3.2)+1); lay=f"_L{i}.png"; beat_layer(lay,b,i+1,n,ai and b.get("clip","dark")!="dark",dark=b.get("clip","dark")=="dark")
        dur=b.get("dur",3.2)+XF; o=f"_b{i}.mp4"
        subprocess.run(["ffmpeg","-v","error","-y","-stream_loop","-1","-i",clip,"-i",lay,"-filter_complex",
          f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,trim=duration={dur},setpts=PTS-STARTPTS[v];[v][1:v]overlay,format=yuv420p",
          "-an","-t",str(dur),"-c:v","libx264","-preset","veryfast","-crf","19",o],check=True); parts.append((o,dur))
    e=s.get("end",{"text":"SEND THIS TO SOMEONE WHO NEEDS TO SEE *THIS*"}); end_card("_END.png",e); ed=e.get("dur",2.6)
    subprocess.run(["ffmpeg","-v","error","-y","-framerate","30","-i","_END.png","-vf",f"format=yuv420p,loop=-1:1,trim=duration={ed}","-t",str(ed),"-c:v","libx264","-preset","veryfast","-crf","19","_bend.mp4"],check=True)
    parts.append(("_bend.mp4",ed))
    # crossfade chain
    inputs=[]; [inputs.extend(["-i",p]) for p,_ in parts]
    fc=[]; prev="[0:v]"; t=parts[0][1]
    for k in range(1,len(parts)):
        off=t-XF; lab=f"[x{k}]"; fc.append(f"{prev}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}{lab}"); prev=lab; t=off+parts[k][1]
    total=t
    subprocess.run(["ffmpeg","-v","error","-y",*inputs,"-filter_complex",";".join(fc),"-map",prev,"-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-r","30","_video.mp4"],check=True)
    if s.get("audio"):
        a=fetch(s["audio"],"_audio"); vol=s.get("audio_volume",0.9)
        af=f"[1:a]aloop=loop=-1:size=2e9,atrim=duration={total:.3f},volume={vol},afade=t=in:d=0.3,afade=t=out:st={max(0,total-1.2):.3f}:d=1.2,aresample=44100,aformat=channel_layouts=stereo[a]"
        cmd=["ffmpeg","-v","error","-y","-i","_video.mp4","-i",a,"-filter_complex",af,"-map","0:v","-map","[a]"]
    else:
        cmd=["ffmpeg","-v","error","-y","-i","_video.mp4","-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-map","0:v","-map","1:a"]
    subprocess.run(cmd+["-t",f"{total:.3f}","-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart",out+".tmp.mp4"],check=True)
    os.replace(out+".tmp.mp4",out)
    subprocess.run(["ffmpeg","-v","error","-y","-i",out,"-frames:v","1","cover.jpg"],check=True)
    for k in (0.1,total/2,total-1):
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{k:.2f}","-i",out,"-frames:v","1","-vf","scale=360:-1",f"check_{int(k*10):03d}.jpg"],check=True)
    print(json.dumps({"out":out,"seconds":round(total,2),"bytes":os.path.getsize(out)}))
if __name__=="__main__": main(sys.argv[1])
