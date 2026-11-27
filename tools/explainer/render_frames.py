#!/usr/bin/env python3
"""Render a deterministic HTML scene (window.seek(t), window.READY) to MP4, frame by frame.
Usage: python3 render_frames.py <file.html> <seconds> <out.mp4> [fps=30]
Serves this folder on localhost, uses Playwright + system Chrome (set CHROME=/path if needed), then ffmpeg (H.264, yuv420p, 1080x1920)."""
import os, sys, shutil, subprocess, threading, http.server, socketserver, tempfile, functools
from playwright.sync_api import sync_playwright
html, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
fps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
here = os.path.dirname(os.path.dirname(os.path.abspath(html)))  # serve tools/ so ../fonts resolves
sub = os.path.basename(os.path.dirname(os.path.abspath(html)))
chrome = os.environ.get("CHROME") or shutil.which("google-chrome") or shutil.which("chromium")
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=here)
handler.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]
tmp = tempfile.mkdtemp(prefix="frames_")
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome, args=["--no-sandbox"]) if chrome else p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto(f"http://127.0.0.1:{port}/{sub}/{os.path.basename(html)}")
    pg.wait_for_function("window.READY===true", timeout=30000)
    n = int(secs * fps)
    for i in range(n):
        pg.evaluate(f"seek({i/fps})")
        pg.screenshot(path=f"{tmp}/f{i:04d}.png")
    b.close()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", f"{tmp}/f%04d.png", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], check=True)
shutil.rmtree(tmp)
print("wrote", out)
