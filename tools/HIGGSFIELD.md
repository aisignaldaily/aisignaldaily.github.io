# Higgsfield pipeline (fully cloud, no computer needed)

All Higgsfield tools are `mcp__Higgsfield_Studio__*`. Plan: Plus (~1,200 credits/month; owner said credits are fine, but don't waste them).
Rough costs: image (gpt_image_2_6) ~0.75 credit; 5 s video (seedance_2_5, 9:16) ~35 credits; 20 s sound (mirelo_text_to_audio) small.

## Content rules for every generation (never break)
- No women or female figures. Men allowed only as fictional, fully and professionally dressed people (desk, lab, device use). Never real people or lookalikes.
- No nudity, nothing vulgar, suggestive, violent, gambling, alcohol, film/TV characters, logos/brands as art.
- Prefer robots, devices, objects, workspaces, abstract tech. Every AI visual is labeled "Made with AI" (on slide + caption) and posts set Instagram `isAiGenerated: true`.
- Never music. Sound = cinematic sound design / dramatic nature ambience only.

## A) Carousels (morning + afternoon): text baked in by Higgsfield
1. `generate_image_batch` 5-6 base images, model `gpt_image_2_6`, aspect `4:5`, `use_unlim:false`. Start EVERY prompt with the same series style line so slides match, e.g.:
   "Series style: premium 3D render, dark navy-black background (#06090F), glossy minimal objects, mint-green (#3DF5C8) glowing rim light, soft haze, hero object in the upper half, empty dark lower half for text, no people, no text, no logos. Scene: ..."
   One visual idea per slide, all in the same world (same object/scene family).
2. `generate_image_batch` again with each base image as `medias:[{role:"image", value:<job_id>}]` and a prompt that adds the text: huge condensed bold all-caps headline (Anton/Bebas style) centered in the lower half with 1-2 key words in mint #3DF5C8, a short Inter-style sub line, top-left "AI Signal Daily" / "@aisignaldaily.news", top-right pill "n/N" + tiny "Made with AI". Cover adds "SWIPE →". Last slide: "SEND THIS TO ... *FULL PRICE*" style + mint button "Comment AI for today's tools" + "Follow @aisignaldaily.news". Say "Spell every word exactly as given. No other text."
3. Proofread EVERY slide: in `sandbox_exec`, curl the result PNGs, make a contact sheet with ImageMagick (`montage` or ffmpeg hstack, keep it under 512 KiB as JPEG) and pass it in `image_paths`. Regenerate any slide with a typo or wrong fact (max 2 retries), else fall back to a cleaner text-free slide plus caption.
4. Post the result URLs (cloudfront .png) directly as Buffer image assets.

## B) Reel (evening): one continuous world + sound, built in the Higgsfield sandbox
1. Keyframe: one `gpt_image_2_6` image (aspect 9:16) of the scene. Then 3-4 clips with `generate_video_batch`, model `seedance_2_5`, 9:16, duration 5, each using the keyframe as reference media (role per model schema, see `models_explore get seedance_2_5`) and a prompt that keeps the SAME subject/set and only changes camera move or action ("same lab, same robot, camera dollies left..."). This avoids the disconnected look.
2. Sound bed: `generate_audio`, model `mirelo_text_to_audio`, duration = Reel length (~16-20 s). Prompt starts "Cinematic sound design, no music, no melody, no voices:" then matches the story:
   - big/alarming: deep rolling thunder, wind gusts, low rumble building, whoosh on cuts
   - calm/useful: soft rain, light wind, distant ocean
   - futuristic: deep cinematic drone, electric hum, soft whooshes
3. Build: `sandbox_exec` → `git clone --depth 1 https://github.com/aisignaldaily/aisignaldaily.github.io repo`, write spec.json, `python3 repo/tools/reel.py spec.json` (see header of reel.py: beats with clip URL + text with *mint* words + sub + dur, end text, audio URL). It makes reel.mp4, cover.jpg and check_*.jpg. Inspect check frames via `image_paths`.
4. Upload: call `media_upload` (filename reel.mp4, video/mp4) FIRST, then in one sandbox_exec run the PUT exactly as given (`curl -X PUT -H "Content-Type: video/mp4" --data-binary @reel.mp4 '<upload_url>'`, expect 200), then `media_confirm` type video. The public URL is the `url` from media_upload (https://d2ol7oe51mr4n9.cloudfront.net/...mp4). Same for cover.jpg if wanted.
5. Post that URL to Buffer as an Instagram reel.

## Fallbacks
- Higgsfield tools missing or erroring twice: use the old method (local Pillow/ffmpeg build, media pushed to repo/media/, GitHub Pages URLs).
- Never post a slide/reel you have not looked at.
