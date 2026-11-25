# Making media: Claude + Higgsfield (hybrid, fully cloud)

Owner's rule: use what is BEST for growth, honestly. Higgsfield = the scroll-stopping hero visual + realistic sound. Claude-made = everything that carries information (clean slides, charts, steps, real screenshots, animated text). Don't spend credits on slides people read.

Higgsfield tools are `mcp__Higgsfield_Studio__*`. Plan: Plus (~1,200 credits/month). Prices: image gpt_image_2_6 ~0.75 cr; 5 s video seedance_2_5 (9:16) 35 cr; sound mirelo_text_to_audio 20 s = 5 cr.
Budget per post (target ~1,500-2,500 credits/month total): carousel <= 8 cr, Reel <= 80 cr, mini-reel carousel <= 110 cr. Check `balance` first; if under 150 credits, use Claude-made media only (dark animated beats, no Higgsfield clips) and email Raheel once that credits are low.

## Content rules for every visual (never break)
- No women or female figures. Men only as fictional, fully and professionally dressed people. Never real people or lookalikes.
- No nudity, nothing vulgar, suggestive, violent, gambling, alcohol, film/TV characters.
- Label AI visuals "Made with AI" (on the media + caption) and set Instagram `isAiGenerated: true` when any AI visual is used.
- Never music. Sound = cinematic sound design / dramatic nature ambience.

## A) Carousel (default for morning + afternoon): 1 Higgsfield cover + Claude-made slides
1. Cover (slide 1) with Higgsfield, 2 calls: (a) `generate_image` gpt_image_2_6, aspect 4:5, `use_unlim:false`, prompt starts "premium 3D render, dark navy-black background (#06090F), glossy minimal objects, mint-green (#3DF5C8) glowing rim light, soft haze, hero object in the upper half, empty dark lower half for text, no people, no text, no logos. Scene: ..."; (b) same model with the first result as `medias:[{role:"image", value:<job_id>}]` adding the text: huge condensed all-caps headline (Anton/Bebas style) in the lower half with 1-2 key words in mint, short Inter-style sub line, "SWIPE →", top-left "AI Signal Daily"/"@aisignaldaily.news", top-right pill "1/N" + tiny "Made with AI". "Spell every word exactly as given. No other text."
2. Slides 2..N, choose per slide (owner compared both side by side on Nov 25: Higgsfield clearly looks better for picture/point slides; plain Claude text slides look empty):
   - **Point / "what it does" slides -> Higgsfield** (same series style + text baked in, like the cover; ~1.5 credits each). This is the default for slides 2-4.
   - **Chart, steps/how-to, exact quote, end slide -> Claude-made** with `repo/tools/carousel.py` (free, numbers always exact, never typos).
   Typical 6-slide post: cover + 2-3 Higgsfield point slides + 1-2 Claude chart/steps slides + Claude end slide = ~5-8 credits.
3. Optional real screenshot slide: in Higgsfield `sandbox_exec` use Playwright (headless Chromium) to screenshot the official announcement/product page, then show it inside a slide. Never screenshot people.
4. Hosting: slide 1 = its Higgsfield cloudfront URL. Slides 2..N: copy to `repo/media/YYYY-MM-DD-<slot>/02.jpg...`, push, wait ~90 s, use https://aisignaldaily.github.io/media/... URLs. Buffer accepts both.
5. Proofread: Read every local slide; for slide 1 curl it inside sandbox_exec and pass it via image_paths. Regenerate on any typo (max 2 tries), else use a Claude-made cover.

## B) Reel (evening): 2 Higgsfield clips + Claude animated beats + Higgsfield sound
1. Keyframe image (gpt_image_2_6, 9:16) of ONE scene, then 2 clips (`generate_video_batch`, seedance_2_5, 9:16, duration 5) that keep the SAME scene/subject, only the camera moves. Use the keyframe as reference media if the model accepts it (check `models_explore get seedance_2_5`).
2. Sound: `generate_audio` mirelo_text_to_audio, duration = Reel length (16-20 s), prompt "Cinematic sound design, no music, no melody, no voices: ..." matched to mood (big news: thunder, wind, low rumble, whooshes; calm tips: soft rain, light wind, ocean; futuristic: deep drone, electric hum, whooshes).
3. Build in Higgsfield `sandbox_exec`: `git clone --depth 1 https://github.com/aisignaldaily/aisignaldaily.github.io repo`; spec.json beats: Higgsfield clip beats (hook first, cinematic) + `"clip":"dark"` beats for facts/numbers (free animated brand background, text centered); end card. `python3 repo/tools/reel.py spec.json` → reel.mp4, cover.jpg, check_*.jpg (inspect via image_paths).
4. Upload from the sandbox: `media_upload` (reel.mp4, video/mp4) FIRST, then the PUT exactly as given in the same sandbox_exec (expect 200), then `media_confirm` type video. Public URL = the `url` from media_upload.

## C) Mini-reel carousel (optional, afternoon, when 3-4 related stories): NOT live yet
Waiting on a Buffer test of video slides in carousels. Until then, don't use.

## Fallbacks
- Higgsfield missing/erroring twice: Claude-made only (carousel.py for all slides incl. cover; reel.py with all "dark" beats, rendered locally and hosted on GitHub Pages; silent audio).
- Never post anything you have not looked at.
