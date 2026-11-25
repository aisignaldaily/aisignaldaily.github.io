"""AI Signal Daily brand helpers: headline(), avatar(), post_layer(), closing_slide(), render(). Import from a scratch working directory."""
import subprocess, os, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
BG = (6, 9, 15)
ACC = (61, 245, 200)
WHITE = (245, 247, 250)
MUTED = (139, 152, 165)
ANTON = "/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"
IB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
IX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
IR = "/usr/share/fonts/opentype/inter/Inter-Medium.otf" if os.path.exists("/usr/share/fonts/opentype/inter/Inter-Medium.otf") else "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
f = ImageFont.truetype
C = "clips/"
os.makedirs("out", exist_ok=True); os.makedirs("layers", exist_ok=True)

def toks(line):
    out = []
    for w in line.split(" "):
        if w.startswith("*") and w.endswith("*"): out.append((w.strip("*"), ACC))
        else: out.append((w, WHITE))
    return out

def wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(" "), [], []
    for w in words:
        test = " ".join(cur + [w]).replace("*", "")
        if d.textlength(test, font=fnt) <= maxw or not cur: cur.append(w)
        else: lines.append(" ".join(cur)); cur = [w]
    lines.append(" ".join(cur)); return lines

def headline(d, text, top, bottom, maxw=990, start=104):
    size = start
    while True:
        fnt = f(ANTON, size); lines = wrap(d, text, fnt, maxw); lh = int(size * 1.08)
        if len(lines) * lh <= bottom - top or size <= 50: break
        size -= 2
    y = top + (bottom - top - len(lines) * lh) // 2
    for ln in lines:
        tk = toks(ln); sp = d.textlength(" ", font=fnt)
        ws = [d.textlength(t, font=fnt) for t, _ in tk]
        x = (W - (sum(ws) + sp * (len(tk) - 1))) / 2
        for (t, c), wd in zip(tk, ws):
            d.text((x, y), t, font=fnt, fill=c); x += wd + sp
        y += lh

def brand(d, y, cx=W / 2):
    fnt = f(IX, 24); t = "AI SIGNAL DAILY"; tw = d.textlength(t, font=fnt)
    x = cx - (tw + 26) / 2
    d.ellipse([x, y + 4, x + 16, y + 20], fill=ACC); d.text((x + 26, y), t, font=fnt, fill=WHITE)

def rounded_hole(img, box, r=28):
    """Punch a transparent rounded rectangle into an RGBA image."""
    m = Image.new("L", img.size, 255)
    ImageDraw.Draw(m).rounded_rectangle(box, radius=r, fill=0)
    a = img.getchannel("A"); a = Image.composite(a, Image.new("L", img.size, 0), m)
    img.putalpha(a)

def avatar(d, x, y, s=84):
    d.ellipse([x, y, x + s, y + s], fill=(14, 22, 36), outline=(40, 60, 80), width=2)
    r = s * 0.17
    d.ellipse([x + s / 2 - r, y + s / 2 - r, x + s / 2 + r, y + s / 2 + r], fill=ACC)
    for k, rr in enumerate([0.30, 0.40]):
        R = s * rr
        d.arc([x + s / 2 - R, y + s / 2 - R, x + s / 2 + R, y + s / 2 + R], 300, 60, fill=ACC, width=3)

# ---------------- layers ----------------
def cover_layer(path, vid_h, text, credit):
    im = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, vid_h - 3, W, vid_h], fill=ACC)
    brand(d, vid_h + 28)
    headline(d, text, vid_h + 76, H - 92)
    d.text((W / 2, H - 50), "SWIPE TO SEE ALL 6  →", font=f(IB, 25), fill=MUTED, anchor="mm")
    rounded_hole(im, [0, 0, W, vid_h - 3], r=0)
    d = ImageDraw.Draw(im)
    # credit pill over video
    fnt = f(IB, 20); tw = d.textlength(credit, font=fnt)
    d.rounded_rectangle([W - tw - 46, vid_h - 52, W - 18, vid_h - 18], radius=17, fill=(0, 0, 0, 150))
    d.text((W - 32, vid_h - 35), credit, font=fnt, fill=(230, 235, 240, 255), anchor="rm")
    im.save(path)

def post_layer(path, text, vw, vh, credit, tag):
    """Returns the video box after centering the whole post vertically."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    x0 = 48
    fnt = f(IR, 42)
    lines = []
    for para in text.split("\n"):
        lines.append(textwrap.wrap(para, 40))
    text_h = sum(len(p) * 56 for p in lines) + 18 * (len(lines) - 1)
    total = 96 + 34 + text_h + 40 + vh + 70
    top = max(40, (H - total) // 2)
    avatar(d, x0, top)
    d.text((x0 + 104, top + 6), "AI Signal Daily", font=f(IX, 36), fill=WHITE)
    d.text((x0 + 104, top + 52), "@aisignaldaily", font=f(IR, 29), fill=MUTED)
    y = top + 96 + 34
    for p in lines:
        for ln in p:
            d.text((x0, y), ln, font=fnt, fill=WHITE); y += 56
        y += 18
    y += 40 - 18
    bx0 = (W - vw) // 2
    box = (bx0, y, bx0 + vw, y + vh)
    d.rounded_rectangle([box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1], radius=30, outline=(47, 51, 54), width=2)
    rounded_hole(im, box, r=28)
    d = ImageDraw.Draw(im)
    tf = f(IB, 24); tw = d.textlength(tag, font=tf)
    d.rounded_rectangle([box[0] + 18, box[3] - 60, box[0] + tw + 54, box[3] - 18], radius=21, fill=(0, 0, 0, 170))
    d.text((box[0] + 36, box[3] - 39), tag, font=tf, fill=ACC + (255,), anchor="lm")
    d.text((x0, box[3] + 24), credit, font=f(IR, 27), fill=MUTED)
    d.text((W - 48, box[3] + 26), "AI SIGNAL DAILY", font=f(IX, 22), fill=(70, 80, 95), anchor="ra")
    im.save(path)
    return box

def closing_slide(path):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill=(14, 20, 30))
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(14, 20, 30))
    brand(d, 90)
    lab = "WHY IT MATTERS"; fnt = f(IX, 30); tw = d.textlength(lab, font=fnt)
    d.rounded_rectangle([(W - tw) / 2 - 30, 220, (W + tw) / 2 + 30, 280], radius=30, outline=ACC, width=3)
    d.text((W / 2, 250), lab, font=fnt, fill=ACC, anchor="mm")
    headline(d, "3D SCENES LIKE THESE USED TO TAKE A WHOLE TEAM. NOW IT TAKES *ONE* *PERSON* *AND* *AN* *AI.*", 320, 760, start=104)
    y = 830
    d.text((W / 2, y), "Which one would you build first? 👇".replace(" 👇", ""), font=f(IX, 46), fill=WHITE, anchor="mm"); y += 90
    for ln in ["Try it: Gemini 4 Hydrogen is in the Gemini app's", "model menu, Google Search and Google AI Studio."]:
        d.text((W / 2, y), ln, font=f(IB, 32), fill=MUTED, anchor="mm"); y += 48
    y += 40
    d.text((W / 2, y), "Source: Google blog, Nov 23, 2026", font=f(IB, 30), fill=MUTED, anchor="mm"); y += 46
    d.text((W / 2, y), "Follow @aisignaldaily for daily AI news", font=f(IB, 30), fill=ACC, anchor="mm")
    d.text((W / 2, H - 50), "SAVE THIS POST", font=f(IB, 25), fill=MUTED, anchor="mm")
    im.save(path, quality=94)

# ---------------- ffmpeg ----------------
def render(out, layer, clip, ss, dur, box, speed=1.0, keep_audio=False, fit="cover"):
    x0, y0, x1, y1 = box; bw, bh = x1 - x0, y1 - y0
    if fit == "cover":
        sc = f"scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh}"
    else:
        sc = f"scale={bw}:{bh}:force_original_aspect_ratio=decrease"
    vf = (f"[0:v]setpts=(PTS-STARTPTS)/{speed},fps=30,{sc},setsar=1[v];"
          f"color=c=black:s={W}x{H}:r=30:d={dur}[bg];"
          f"[bg][v]overlay=x={x0}+({bw}-overlay_w)/2:y={y0}+({bh}-overlay_h)/2:shortest=1[b];"
          f"[b][1:v]overlay=0:0,format=yuv420p[o]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-t", str(dur * speed), "-i", C + clip,
           "-loop", "1", "-i", layer]
    if keep_audio:
        af = f"[0:a]atempo={speed},afade=t=in:d=0.3,afade=t=out:st={dur-0.6}:d=0.6[a]" if speed != 1 else f"[0:a]afade=t=in:d=0.3,afade=t=out:st={dur-0.6}:d=0.6[a]"
        cmd += ["-filter_complex", vf + ";" + af, "-map", "[o]", "-map", "[a]"]
    else:
        cmd += ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo",
                "-filter_complex", vf, "-map", "[o]", "-map", "2:a"]
    cmd += ["-t", str(dur), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
            "-r", "30", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out + ".part.mp4"]
    r = subprocess.run(cmd)
    if r.returncode == 0: os.replace(out + ".part.mp4", out)
    else: raise SystemExit(f"failed {out}")

