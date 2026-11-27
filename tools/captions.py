#!/usr/bin/env python3
"""Word-highlight captions for VOICED Reels (see STYLE.md "WORD-HIGHLIGHT CAPTIONS").
Run in the Higgsfield sandbox (has faster-whisper, ffmpeg+libass, Montserrat).
  python3 tools/captions.py voice.wav video.mp4 out.mp4 [--speed 1.0] [--margin 300]
voice.wav = the SAME narration that is already in video.mp4 (timings come from it).
Words are shown 3 at a time, uppercase, the spoken word in mint. Needs no credits."""
import argparse, json, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("voice"); ap.add_argument("video"); ap.add_argument("out")
ap.add_argument("--speed", type=float, default=1.0, help="if the voice in the video was sped up (atempo), pass the factor")
ap.add_argument("--margin", type=int, default=300, help="px from bottom; keep clear of the Instagram UI")
a = ap.parse_args()

from faster_whisper import WhisperModel
segs, _ = WhisperModel("base.en", device="cpu", compute_type="int8").transcribe(a.voice, word_timestamps=True, language="en")
W = [{"w": w.word.strip(), "s": float(w.start) / a.speed, "e": float(w.end) / a.speed} for s in segs for w in s.words]

chunks, cur = [], []
for w in W:
    cur.append(w)
    if len(cur) == 3 or re.search(r"[.!?:]$", w["w"]):
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

def t(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
MINT = "&H0090F5A8&"  # BGR of #A8F590
hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: C,Montserrat,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,2,2,60,60,{a.margin},1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
ev = []
for ci, c in enumerate(chunks):
    for i, w in enumerate(c):
        last = i + 1 == len(c)
        nxt = c[i+1]["s"] if not last else (chunks[ci+1][0]["s"] if ci + 1 < len(chunks) else w["e"] + 0.3)
        en = min(nxt, w["e"] + 0.5) if last else nxt
        txt = " ".join((f"{{\\c{MINT}}}{x['w'].upper()}{{\\c&HFFFFFF&}}" if j == i else x["w"].upper()) for j, x in enumerate(c))
        ev.append(f"Dialogue: 0,{t(w['s'])},{t(en)},C,,0,0,0,,{txt}")
open("/tmp/cap.ass", "w").write(hdr + "\n".join(ev))
r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.video, "-vf", "ass=/tmp/cap.ass:fontsdir=/usr/share/fonts",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "copy", a.out])
sys.exit(r.returncode)
