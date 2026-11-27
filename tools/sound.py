#!/usr/bin/env python3
"""AI Signal Daily sound design: our own synthesized foley + a quiet ambient bed. No music, no samples, no licences, 0 credits.
Everything is generated from numpy maths, so it is ours and safe to publish (label stays "Voice: AI-generated" only when a voice is used).

Usage:  python3 tools/sound.py spec.json out.wav
        ffmpeg -i video.mp4 -i out.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest final.mp4
spec = {"dur": 15, "bed": "night" | "air" | "rain" | "none", "bed_db": -30,
        "cues": [[0.2, "pop"], [2.9, "whoosh", {"len": 0.9}], [8.0, "chime"], ...]}
Cue names: pop (soft bubble in), pop_hi (reply), tick (key/row tick), whoosh (camera travel; opts len, up=true for rising),
           chime (small success), stamp (thud + chime, big payoff), ring (gentle two-tone phone ring), swell (end lift), click.
Mixing rule for voiced Reels: build the bed + foley first, then duck it ~12 dB under the narrator (see STYLE.md "SOUND DESIGN").
"""
import json, sys, wave
import numpy as np
SR = 44100
rng = np.random.default_rng(7)

def t_(d): return np.arange(int(SR * d)) / SR
def env(n, a=0.005, r=0.2):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    nr = max(1, min(n, int(r * SR))); e[-nr:] *= np.linspace(1, 0, nr) ** 2; return e
def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x): s = (1 - a) * v + a * s; y[i] = s
    return y
def lp_fast(x, fc):  # vectorised one-pole via FFT for long arrays
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); H = 1 / np.sqrt(1 + (f / fc) ** 4); return np.fft.irfft(X * H, len(x))
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); H = ((f > lo) & (f < hi)).astype(float)
    k = max(1, int(len(f) * 0.004)); H = np.convolve(H, np.ones(k) / k, "same"); return np.fft.irfft(X * H, len(x))
def stereo(x, pan=0.0):  # pan -1..1
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4); return np.stack([x * l, x * r], 1)

def pop(f0=520, f1=860, d=0.16, g=0.5):
    t = t_(d); f = f0 + (f1 - f0) * (1 - np.exp(-t * 30)); ph = 2 * np.pi * np.cumsum(f) / SR
    return stereo(np.sin(ph) * env(len(t), .003, d * .9) * g, 0.1)
def tick(g=0.35):
    t = t_(0.05); n = bp(rng.standard_normal(len(t)), 1800, 5200) * np.exp(-t * 90); s = np.sin(2 * np.pi * 2100 * t) * np.exp(-t * 120)
    return stereo((n * 0.8 + s * 0.4) * g, rng.uniform(-.15, .15))
def click(g=0.4):
    t = t_(0.04); return stereo(bp(rng.standard_normal(len(t)), 900, 3500) * np.exp(-t * 140) * g, 0)
def whoosh(length=0.9, up=False, g=0.45):
    n = int(SR * length); x = rng.standard_normal(n); out = np.zeros(n); seg = 256
    for i in range(0, n, seg):  # sweeping band-pass via blockwise filtering
        p = i / n; c = (500 + 2600 * p) if up else (2800 - 2200 * p); blk = x[i:i + seg]
        out[i:i + seg] = bp(np.pad(blk, (0, 0)), c * 0.6, c * 1.5) if len(blk) > 8 else 0
    out = lp_fast(out, 5200) * np.sin(np.linspace(0, np.pi, n)) ** 2; out /= (np.abs(out).max() + 1e-9)
    pan = np.linspace(-0.6, 0.6, n) * (1 if up else -1); l = out * np.cos((pan + 1) * np.pi / 4); r = out * np.sin((pan + 1) * np.pi / 4)
    return np.stack([l, r], 1) * g
def chime(g=0.4, base=880):
    t = t_(0.9); x = sum(a * np.sin(2 * np.pi * base * m * t) * np.exp(-t * k) for m, a, k in ((1, 1, 5), (1.5, .55, 6), (2.01, .25, 9)))
    return stereo(x * env(len(t), .004, .85) * g, 0.0)
def stamp(g=0.7):
    t = t_(0.5); th = np.sin(2 * np.pi * (95 - 30 * t) * t) * np.exp(-t * 11) + bp(rng.standard_normal(len(t)), 120, 900) * np.exp(-t * 40) * 0.6
    out = stereo(th * g * 0.9, 0); ch = chime(0.35, 988); pad = np.zeros_like(ch); pad[:len(out)] += out; return pad + np.roll(ch, int(0.06 * SR), 0) * (np.arange(len(ch)) > 0.06 * SR)[:, None]
def ring(g=0.28):
    t = t_(0.5); one = (np.sin(2 * np.pi * 740 * t) + np.sin(2 * np.pi * 988 * t) * .7) * env(len(t), .01, .3) * np.exp(-t * 3)
    gap = np.zeros(int(0.12 * SR)); x = np.concatenate([one, gap, one]); return stereo(x * g, 0)
def swell(g=0.4, length=1.4):
    t = t_(length); x = np.sin(2 * np.pi * 330 * t) * 0.5 + np.sin(2 * np.pi * 495 * t) * 0.35 + np.sin(2 * np.pi * 660 * t) * 0.2
    return stereo(x * np.sin(np.linspace(0, np.pi, len(t))) ** 2 * g, 0)
CUES = {"pop": lambda o: pop(520, 860), "pop_hi": lambda o: pop(700, 1150, 0.18), "tick": lambda o: tick(), "click": lambda o: click(),
        "whoosh": lambda o: whoosh(o.get("len", .9), o.get("up", False)), "chime": lambda o: chime(), "stamp": lambda o: stamp(),
        "ring": lambda o: ring(), "swell": lambda o: swell(length=o.get("len", 1.4))}

def bed(kind, dur):
    n = int(SR * dur); t = np.arange(n) / SR
    if kind == "none": return np.zeros((n, 2))
    base = rng.standard_normal(n); wind = lp_fast(base, 380) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t + 1.0)) ** 2
    if kind == "air":  # soft room air / distant wind
        x = wind / (np.abs(wind).max() + 1e-9); return np.stack([x, np.roll(x, 900)], 1)
    if kind == "rain":
        r = bp(rng.standard_normal(n), 2500, 9000) * 0.35 + lp_fast(rng.standard_normal(n), 900) * 0.4
        r *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t); r /= np.abs(r).max() + 1e-9; return np.stack([r, np.roll(r, 700)], 1)
    # night: wind + faint crickets (4.6 kHz chirps pulsed ~ 14 Hz in groups) = "after hours" mood
    x = wind / (np.abs(wind).max() + 1e-9) * 0.9; ck = np.zeros(n)
    for start in np.arange(0.3, dur, 1.3):
        for k in range(3):
            s0 = int((start + k * 0.19) * SR); L = int(0.14 * SR); tt = np.arange(L) / SR
            if s0 + L < n: ck[s0:s0 + L] += np.sin(2 * np.pi * 4600 * tt) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 60 * tt))) * np.sin(np.pi * tt / tt[-1]) ** 2
    ck *= 0.22 * (0.5 + 0.5 * np.cos(np.pi * np.clip(t / dur * 1.4, 0, 1)))  # crickets fade out as the story moves on
    return np.stack([x + ck, x + np.roll(ck, 300)], 1)

def build(spec):
    dur = spec["dur"]; n = int(SR * dur); out = bed(spec.get("bed", "air"), dur); out = out / (np.abs(out).max() + 1e-9) * 10 ** (spec.get("bed_db", -30) / 20)
    fo = np.zeros((n, 2))
    for c in spec["cues"]:
        t0, name = c[0], c[1]; o = c[2] if len(c) > 2 else {}; s = CUES[name](o); i = int(t0 * SR); j = min(n, i + len(s))
        if i < n: fo[i:j] += s[:j - i]
    fo *= 10 ** (spec.get("foley_db", -9) / 20); mix = out + fo; mix[:int(.05 * SR)] *= np.linspace(0, 1, int(.05 * SR))[:, None]
    mix[-int(.4 * SR):] *= np.linspace(1, 0, int(.4 * SR))[:, None]; mix *= 0.7 / (np.abs(mix).max() + 1e-9); return mix  # peak about -3 dBFS
def write(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
if __name__ == "__main__":
    write(sys.argv[2], build(json.load(open(sys.argv[1])))); print("wrote", sys.argv[2])
