# AI Signal Daily: start here

Instagram **@aisignaldaily.news**: faceless page with AI news + "AI you can use" for normal people and small-business owners. Owner: **Raheel** (raheelsohail@gmail.com, America/Chicago; all dates and times in Central Time). Goal right now: grow followers fast through **sends, saves, follows**, and later bring leads to **Allyzent AI** and **Latis AI** (our team's companies).

This file is the short brief. The full playbook is `tools/STYLE.md` (read it fully before making any post; it wins on style details). Updated Nov 26, 2026.

## Working with Raheel
- Be direct and honest, no flattery; give your own opinion and push back when something won't work.
- He wants it hands-off and fully cloud: never depend on his computer. Things that need his login (ManyChat, Instagram app settings, scheduled-task toggles) go to him as short step-by-step instructions.
- When he sends example posts: learn the pattern (why it worked, sends vs likes), add our own spin. Never copy text, visuals or clips.
- When he asks for ANY change, be a critic first, not PR. Check it against this file, `tools/STYLE.md`, `tools/REVIEW_RUBRIC.md` (benchmarks + research) and our own numbers (`tools/REVIEW_LOG.md`, weekly report rules). Then say plainly:
  1. Whether it will help followers, sends, saves or revenue, and why. Use evidence, not enthusiasm.
  2. The risks (rules, trust, credits, effort) and what it would break or contradict.
  3. A better or cheaper alternative if there is one.
  4. What you'll change and where it's recorded.
  Agree only when it's actually good; say "I don't think this works, because..." when it isn't. Then do what he decides, inside the rules.
- Every lasting decision goes into the files (this file for the summary, `tools/STYLE.md` for details) in the same session. Chat memory does not carry over; the files do.

## Rules that never break
- Every post cites its source; no rumors, leaks or "reportedly". Dates in Central Time.
- Never create AI likenesses of real people or AI women/female figures. AI men only fictional and fully, professionally dressed. Nothing nude, sexual or suggestive. No movie/TV content, gambling, alcohol, piracy.
- No income or "make money" claims. Market prices only with a source.
- Label "Made with AI" (and "Voice: AI-generated") when used; Instagram isAiGenerated true when any AI visual is used.
- No music (copyright). Never state a fixed number of posts per day.
- Write "Allyzent AI" and "Latis AI" exactly. Company mentions carry "Full disclosure: Allyzent AI / Latis AI is our team." Company posts are paused until ~400-500 followers (`tools/COMPANY_POSTS.txt`), except listed one-offs.
- Every post gets a preview email to Raheel 5 minutes before it goes out; a reply stops it; PAUSE stops everything until RESUME.

## How posting works
- Scheduled cloud tasks post through **Buffer** (org 6b06f0d4dc0cc7b427fd05ce, Instagram channel 6b06f1348541f09ecb9dc442).
  - Daily slots (CT): 9:15 morning carousel · 12:30 midday Reel · 5:45 practical carousel · 7:45 evening Reel · 8:30 Stories. The 3:45 afternoon carousel is OFF from Nov 27 (Raheel, Nov 26: quality over volume).
  - Also: hourly breaking-news watch (max 1/day) · watchdog · Monday 7:23 weekly report.
- Before making a post, a run claims its slot with `claims/YYYY-MM-DD-<slot>.txt`. If the file exists, someone else owns that slot.
- **Pre-flight review:** an independent agent scores every draft with `tools/REVIEW_RUBRIC.md` before the preview email. Scores go in `tools/REVIEW_LOG.md`.
- Media: Higgsfield (images, voice, sound) plus code-made slides and videos.
  - Credits: ~928 at last check; keep spend small.
  - The Higgsfield sandbox has internet access. The local shell can't reach github.io or cloudfront.
- Commit as "AI Signal Daily" <aisignaldaily.news@gmail.com>. Push with `git -c push.negotiate=true push origin HEAD:main`.

## Where things live
| Path | What |
|---|---|
| `tools/STYLE.md` | full playbook: series, hooks, captions, real-people rules, voice rules, research notes, weekly rules. The ONLY file to edit. |
| `tools/slots/<slot>.md` + `tools/build_slots.py` | GENERATED short slices of STYLE.md per run (morning, midday, practical, evening, stories, breaking, friday) so runs read ~50-90% less. After ANY edit to STYLE.md run `python3 tools/build_slots.py` and commit the slices with it. Never edit slices by hand. |
| `tools/REVIEW_RUBRIC.md` / `tools/REVIEW_LOG.md` | reviewer criteria + benchmark posts / scores per post |
| `tools/carousel.py`, `tools/reel.py`, `tools/story.py` | slide, Reel and Story builders. carousel.py has two themes (dark default, "theme":"paper") + slide types titlecard and versus; example: `tools/examples/paper_theme_sample.json` |
| `tools/explainer/sales_marketing.html` | code-animated explainer template (67 s, 13 scenes); copy it for industry videos |
| `tools/explainer/camera_world_demo.html` + `render_frames.py` | camera-world explainer example (15 s, GSAP bundled via npm) and the frame renderer; rules in STYLE.md "EXPLAINER DESIGN RULES" |
| `tools/radar.py` | trend radar (run in the Higgsfield sandbox) |
| `tools/HIGGSFIELD.md` | how to make media with Higgsfield + credit rules |
| `tools/MANYCHAT.txt`, `tools/COMPANY_POSTS.txt` | ManyChat keyword status, company-post switch + one-offs |
| `tools/AFFILIATES.md` | affiliate programs: status, terms, approved links (rules in STYLE.md "AFFILIATE RULES") |
| `index.html` | links page (`const signals`, newest first, max 30) |
| `toolkit/` | free AI toolkit (email signup via beehiiv) |
| `blueprints/sales-marketing/` | free blueprint page (video embedded, Allyzent AI / Latis AI booking) |
| `demo/` | book a demo of Allyzent AI or Latis AI |

## Weekly signature calendar (from Nov 30)
Mon 12:30 We asked AI + fact-check · Tue 5:45 Build it / prompt chain · Wed 12:30 Built with AI demo · Thu 5:45 Build it · Fri 12:30 60-s explainer (own scheduled run) · Sat 9:15 The List · Sun 7:45 Builder lessons · Mon/Wed/Fri/Sun 9:15 Free swaps. Details: STYLE.md "WEEKLY SIGNATURE CALENDAR".

## Comment keywords (ManyChat, live)
- **AI**: today's tools + the toolkit (default CTA). The toolkit is FOLLOW-GATED: never link aisignaldaily.github.io/toolkit/ directly in captions, slides, Stories, the bio or the links page; say "Follow + comment AI". Blueprint pages are not gated. Details: STYLE.md "FOLLOW-GATE".
- **BLUEPRINT**: the blueprint page + "Book a demo".
- **DEMO**: Allyzent AI booking flow.

## What works (from research + Raheel's examples)
- Sends per reach is a top ranking signal. Every post needs an obvious "send this to ___" person.
- Winners have five things:
  - a concrete result for a specific person;
  - proof on slide 1;
  - a big number or a chain;
  - one idea per slide;
  - surprise, or a worry plus its fix.
- Losers: income bait, comment-only bait (comment-gated Reels WITH a delivered DM payoff can win), niche audiences, reposts.
- Follow trigger (hard rule): every post names its series/number and promises the next post concretely. Details: STYLE.md "FOLLOW TRIGGER".
- Carousels get ~9x the saves of single images; Reels get the most interactions. The Reel payoff must start before ~8 s.
- Our edge: our own demos and checked facts (fact-checks, verified prices) where others repost.
- Viewer psychology + hook honesty (Nov 26 study of the top AI accounts): every post does 6 jobs (stop, stay, save, send, like, follow); carousel slide 2 is a second cover; no bait phrases and no engagement ask in the hook; one keyword per post with a real payoff; originality guard (third-party clips are a supporting beat, never the post). Tests: mascot, vote series, hook-type logging, carousel mix (Try-this card, who-can-use-it line, consistent cover pattern on ~half of practical carousels; from the @claudetipsandtricks study, Nov 26; Nov 27 added named-concept titles + Try-this card on Reels; parked: loop ending, recurring hero object, own screen recordings). Details: STYLE.md "VIEWER PSYCHOLOGY".
- Visual style v2 (Nov 27): two themes chosen by series, never mixed in a post. DARK for news, breaking, Price Drop, The List, company posts; PAPER (warm off-white, two-tone sentence-case headline, numbered kicker, mint highlighter, Before/After card pair, lots of white space) for how-to/utility (Tue/Thu Build it, Free swaps, Fix it). No brand logos, people or music. Evidence: polish is table stakes, utility drives sends; test = paper vs the previous 2 weeks of dark how-tos, 10+ posts, judged Dec 21; log "theme" and "layout". Reveal/panorama mechanics stay parked. Details: STYLE.md "VISUAL STYLE v2".
- New formats (Nov 26): **Price Drop** (real before/after prices, try it ourselves, never "free"/"open-source" unless true) and **Viral AI claim, fact-checked** (check the claim, never attack the creator). On news-light days use the fallback list in STYLE.md "NEWS-LIGHT DAYS" instead of a weak story.

## Running experiments (the Monday report decides)
- **Voice:** explainers and how-tos are always voiced ("Grady"). News Reels are voiced Mon/Wed/Fri only, as the test.
- **Hashtags:** max 3; zero on Tue/Thu/Sat. Log "hashtags: N".
- **Virality predictor:** Higgsfield's tool, checked against real results each week.
- **Clip test (from Nov 27):** the evening Reel uses the Higgsfield video clip (~35 credits) only Mon/Wed/Fri; other days use free motion (official clips, screen recordings, code animation). Log "clip: yes/no". Details: STYLE.md "Clip test".

- **cookin.code test (from Sat Nov 28, 2 weeks):** a MIX with AI news, not a replacement. Code-animated "free tool, verified" Reels take the Tue/Thu/Sat 7:45 slot (6 total: per week 2 "free tool, verified" + 1 news Reel in the same poster style, to separate style from topic), comment keyword + DM payoff. Pivot rule: if they clearly beat our news Reels (views >= 2x median OR comments >= 1% of views), make this the main Reel style (5-6/week); if mixed keep 1-2/week; if worse drop. Details: STYLE.md "Competitor study".

## Queued
- Fri Nov 27, 7:45 PM: first "Price Drop" Reel (MAGI-2, our own test clip with Higgsfield magi_2). Details: STYLE.md "Planned queue".
- Tue Dec 1, 5:45 PM: Allyzent AI blueprint post (sales half).
- Thu Dec 3, 5:45 PM: Latis AI blueprint post (marketing half).
- Friday explainer run (weekly, from Fri Dec 4): alternates an industry blueprint (law-firm intake first, with its own page) and a system explainer.
- Raheel to-do: ManyChat follow-up should skip people who tapped "Book a demo"; optional Latis AI button in the BLUEPRINT flow.
