# Weekend progress report, 14 to 16 Nov 2026 (written Mon 16 Nov, about 09:15 UTC)

**What this is based on.**
- **Checked first-hand on 16 Nov:**
  - `results.tsv`: all 55 runs read.
  - `./verify.sh`, run on the Mac and on the box.
  - git state on both machines (last commit `774c3bb`, 15 Nov 10:53 +02:00).
  - Pod status on the box.
  - The saved .blend files.
  - The spend-cap files on both machines.
  - The handoff file `~/AgencyOS/handoffs/2026-11-15-mom-hair.md`.
  - Nick's quotes below, each found word for word in the chat files.
- **Second-hand:**
  - The chats were read as text only, with tool output stripped. Anything below about what a session "did" or "rendered" is that session's own claim unless marked as checked.

All times are UTC. The Mac clock is UTC+2. The box and pod logs appear to be UTC+3.

Chats covered, all in the "Blender research" sidebar group:

| Chat | When |
|---|---|
| Blender setup upgrade | Sat morning |
| FaceTracker Blender video analysis | Fri evening to Sun morning |
| FaceTracker Blender video analysis (fork) | Sat 12:31 to Sun 08:58 |
| Skills for all chats | Sun 07:49 to 08:56 |
| Hair research | Sun 08:12 to 08:56 |
| Mom's hair recreation plan | Sun 09:18 to Mon 08:32 |
| Zooms continuation | Sun 10:44 to 13:38 |
| Fix cursor: curve sculpt brushes by mouse | Sun 13:29 to Mon 08:44 |

---

## 1. The weekend in brief

**Saturday** was split between three things:
- **The boy:** muscle, T-shirt, trousers.
- **A new clip analyzer:** OpenCV motion, sound and captions, with a live page on port 8570.
- **The reference camera:** recreating it in run 021 with COLMAP-solved cameras.

In the evening the fork chat started the mom's hair from scratch and got a live Blender running on the pod, worked by mouse.

**Sunday** was the big hair day:
- The project `~/Desktop/mom-character` was created.
- Skills were written so every chat can reuse the work.
- The hair research was done.
- The hair was rebuilt over 42 passes (L1 to L42).
- Scoring switched from by-eye to measured silhouette overlap (IoU) at cameras matched to her reference frames. The side and three-quarter views went from **0.718 to 0.794 mean IoU**.

**Monday morning** the cursor session proved real mouse brushes move hair. The pod is down.

---

## 2. Sunday 15 Nov (yesterday)

### Mom's hair: achieved (from `results.tsv` and the hair chat)
- **Method changed three times, each after Nick pushed back.**
  - Dense strands by code. Nick, 10:15: "this is close to the result we got yesterday which was suboptimal".
  - The tutorial's locks method (NURBS locks with a grooved bevel). This read "far better" (results row L1 to L3).
  - Locks as the under-layer with fine strands on top (L13 to L15), the article's layering.
  - From L33: one connected field of hair instead of separate groups. Nick, 11:29: "you should think of her hair as one connect clump of hair not different groups."
- **Fixes that worked**, each recorded as worked in results.tsv:
  - The seam ring was flat square lock ends (diagnosed live, fixed L10).
  - Bangs rebuilt to rise from the root before falling (L25/26).
  - Sides swept up into the bun with the ear visible (L27 to L30).
  - Forehead clumps from the part (L32).
  - Bun colour measured equal to the hair; it only looks black in shadow.
- **Measured loop built:**
  - `refs/cams.json` holds cameras solved per reference frame.
  - `ref_overlay.py` puts her frames behind those cameras inside Blender.
  - `outline_auto.py` gives an automatic hair outline.
  - `fit_multi.py` scores the views.
  - A patch scanner and a live board show each pass.
- **Best state:** mean IoU **0.794** (side 0.821, three-quarter 0.768), saved as `blend/blendpull/mom_hair_L42.blend`. Checked: the file exists on the Mac, 15 Nov 15:36 local. A crown-volume cut scored 0.791 and was reverted.
- **Back camera re-solved** from ear and bun landmarks: about 10 px error, consistent across 3 focal lengths.
- **Skills written:**
  - `/blender` and `/blender-hair` (Nick: "sure save both").
  - `blender-hair/build-method.md` and `sources-checklist.md`.

### Skills and pod guard (Skills chat, morning)
- **Skills:** `clip-analyzer`, `live-blender`, `learning-loop` and `camera-moves` were written.
- **Pod guard:** built on the box. It stops a pod after 10 idle minutes. The chat says it killed a real pod at 08:14.

### Hair research (Hair research chat)
- **Sources read:** the yelzkizi hair-cards article, the 20:40 "Hair With Curves" tutorial (all frames plus a transcript), and the Blender 5.3 manual. The manual is offline on the box; search it with `bman`.
- **Main findings:**
  - The tutorial is the 2.79 locks method: bezier locks, Alt+S width, Ctrl+T twist.
  - The bun should be twisted locks, not a ball.
  - Roughness 0.13 was too low; it gives thin metallic streaks.
  - Coat is for fur.

### Camera / zooms (Zooms continuation chat)
- **Zoom presets:** 9 built.
  - Nick, 11:17: "our one looks cut in many places and it isnt smooth".
- **Copying the reference motion graph:** tried 3 ways (match A/B, a graph loop, a whip bridge).
  - Nick, 12:49: "oh no it is horrible. i think we should just create the zooms as presets and continue that way".
- **Zoom-game prototype:** Nick, 12:57: "this looks really average."
- **New T-Rex:** downloaded (Nick picked candidate C), credit in `notes/credits.md`. No verdict.
- **Spend cap:** Nick ordered the daily workbench cap removed. Nick, 11:38: "in the previous chats i removed this rule. i thought you had memory..."

### Cursor fix (side chat, started 13:29)
- **Two harness bugs found:**
  - ssh plus `eval` split each drag into 31 single clicks.
  - The test strands were built off screen.

---

## 3. Saturday 14 Nov

- **The boy:**
  - A muscle comparison sheet.
  - T-shirt analysis, and a reshaped tee (`tee_hang.py`) in a box test copy only (`~/probe013/run`).
  - Nick, 08:23: "i think its too edgy you need too smooth a bit... also the pants need fixing too." Still open.
- **Clip analyzer:** `~/Projects/clip-analyzer`, page on port 8570.
  - Every-frame motion with captions masked: 97% of frames read.
  - 3D move labels.
  - A sound/voice split, a caption lane, and play/scrub controls.
  - blender-funnel was pushed to GitHub (private).
  - A transcript of the clip was saved.
- **Camera in run 021:** COLMAP solved the opening shot (55/55 frames, 0.79 px).
  - Four renders were rejected. Nick, 15:49: "you zoom only in one plane instead of three planes"; 16:48: "i think we are not progress and regressing."; 17:36: "our one looks really bad."
  - The "over to rope" orbit was agreed as 3 parts ("yes perfect"). Three versions were rendered on Sunday and never scored.
- **Mom's hair, first attempt (fork chat):**
  - Code tests on the box took about 4 min each. Nick, 13:39: "we've been working on creating references for weeks and we never seem to do it successfully."
  - Then live Blender on the pod with VirtualGL and the mouse.
  - The shape improved (Nick, 16:39: "the shape is much bettter").
  - Nick's last notes, 17:37: "the curls need to be more intense at the end, the hair shouldnt be so open in the end and the wet glossy look more intense".
  - These live-only settings were lost with the pod. They survive only as `finish_hair.py`.

---

## 4. This morning (16 Nov)
- **Pods:** Nick approved "Yes, rent pod" (08:32). The cursor session rented pod `x3ql9921y73vcy`, ran all brushes, and stopped it: 0.19 h, $0.16 (its claim).
- **Brushes now proven on a test object** (one held drag, size 120 px, strength 1.0):

  | Brush | Result |
  |---|---|
  | Comb, PROJECTED falloff | 915 of 3,000 points moved |
  | Comb, default SPHERE falloff | 58 |
  | Pull Tips | 3 |
  | Smooth | 27 |
  | Puff | 52 |
  | Pinch | 57 |
  | Delete | 300 to 284 curves |
  | Slide, surface UVs set by hand | 920 |
  | Add, held drag | 300 to 306 curves |

- **Third cause found:** the "Quick Setup" splash on a fresh Blender swallows the mouse. Escape clears it.
- **Recipe:** `~/.claude/skills/live-blender/cursor-recipe.md` (checked: exists, 16 Nov 10:43 local).
- **Not tested yet:** the real hair layers.

---

## 5. State right now (checked first-hand, about 08:50 to 09:10 UTC)
- **Pod: down.** `workbench status` on the box says `WB down`. Nothing is billing.
- **`./verify.sh` fails (exit 1).**
  - On the Mac, 4 scripts point into a chat's temporary folder: `patchscan.py`, `outline_auto.py`, `viz.py` and `viz_multi.py`.
  - On the box, only `patchscan.py` fails, because the other three are not on the box at all.
  - That temporary folder still exists today (`vm/`, `ana/`, `scan/`), but a reboot or cleanup can wipe it. That would take the outline tool's inputs with it.
- **Nothing from the weekend is committed.**
  - The last commit is 15 Nov 10:53 +02:00.
  - All hair scripts, cameras, outlines and cursor tools are uncommitted on both machines.
  - The chats also say nothing was committed in blender-funnel, clip-analyzer, render-desk or zoom-game.
- **The Mac and the box have drifted.**
  - The box is missing `outline_auto.py`, `viz.py`, `viz_multi.py`, `fit.sh`, `fitm.sh` and `harness.sh`. The rule is that everything runs from the box.
  - The box `results.tsv` is the header only; all 55 runs are on the Mac.
  - The blend copies L19 to L42 are only on the Mac.
  - The three main scripts I hashed are the same on both (`hair2_locks.py`, `fit_multi.py`, `cursor_harness.py`).
- **The spend caps differ between the machines.**

  | | Mac `render.env` | Box `render.env` |
  |---|---|---|
  | Monthly | $65 | $40 |
  | Daily | $20 | $20 |
  | Workbench daily | $1000 (Nick: "remove the fucking cap") | no such line |

  This morning's rental went through, so the box caps did not block it then.
- **The handoff is stale.** `~/AgencyOS/handoffs/2026-11-15-mom-hair.md` was written before this morning's pod run:
  - It has the pod-1 numbers (Comb 900, Pull Tips 33, Pinch 43, "Slide 0 untested").
  - It does not mention the splash fix.
  - It says the monthly cap "was exhausted... only Nick raises it", but Nick raised it to $65 on the Mac.
  - It correctly flags `refs/outline_back.npy` as INVALID (built from the old back camera).

---

## 6. Open mismatches against the reference

### Mom's hair
These are the hair chat's own findings at matched cameras. Nick has not confirmed them one by one.
- **Back/nape:** hers is a full curtain down to the collar. Ours tapers in and leaves the neck bare.
- **Bun:** ours sticks up like a comb. Hers sits low and soft, a twisted knot.
- **Back:** hard vertical splits where strand sheets meet.
- **Side:** a crescent at the back-left. Her hem flares out over the shoulder in an S; ours is mixed.
- **Bangs:** ours are straight blades. Hers are soft and swept.
- **Colour:** lightness is near hers, but chroma is about half. Ours reads pale where hers is golden.
- **Crown dome:** too big. A plain lift cut did not help.
- **Gloss and ends:** the top gloss is weaker than hers. The ends should curl more (Nick, Sat 17:37).
- **Back view:** cannot be scored yet; the back outline must be rebuilt from the new camera.

### Camera (run 021)
- **Static camera:** the clip is still too calm, and at 2 s the whips land on bare wall.
- **Shots:** 5 are unsolved.
- **Orbit:** the "over to rope" orbit is still unscored.
- **Pan and tilt:** not in the presets.

### Boy and outfit
- **T-shirt:** still too edgy.
- **Trousers:** not fixed.
- **Characters:** none of them act.
- **Mom:** still a placeholder in run 021.
- **Polo and sheen:** the polo is untested on her body, and the clothes have no Sheen.

---

## 7. Failed loops and common pitfalls (grouped across all chats)

1. **Quoting and shell bugs cost a day of false "the brushes don't work".**
   - Comb by mouse was tried in 3 rounds on Sunday (09:59, 13:06, 13:21) and moved 0 points every time.
   - The cause was the test harness, not Blender: `eval` over ssh split each drag into 31 clicks.
   - zsh not splitting `$cfg` broke other runs too. Other casualties include a missing quote, a comment swallowing a line, and a regex swallowing a name.
   - About 15 small script and ordering bugs each cost a loop in the hair chat.
2. **The pod lifecycle lost work and money.**
   - Sat evening to Sun morning: a pod ran idle 16.06 h for $14.29, about $12 wasted. The idle stop ran on the Mac, which slept, and an open live Blender counted as "in use".
   - Sunday: the idle guard stopped the pod under live hair work 3 times, and each time the scene was rebuilt from scripts.
   - The live Blender died at 13:41 right after a `snap_curves_to_surface` call (cause unproven). Unsaved work after L42 was lost.
   - Saturday's live-only hair settings were lost entirely.
   - The chat contradicted itself on keep-alive pings: "I now send a cheap command at least every five minutes" (11:27), then "I won't add a keep-alive ping" (12:50).
3. **Falling back to code on the first blocker.**
   - Nick, 10:24: "the blender file has not moved at all which shows me that you still do most things by code am i correct?" The assistant agreed.
   - Its own lesson (11:52): when one method hit a blocker it dropped the source's whole approach.
4. **Measuring the wrong thing.**
   - Widths and directions were measured at mismatched angles, then withdrawn.
   - Thumbnails hid problems.
   - The camera checker "called a bad video good".
   - Strands were about 4 times too thick.
   - Nick, 11:32: "measuring doesnt get us the right results."
5. **Idle or asking instead of finishing.**
   - Nick, 12:51: "why are you staying idle though? why do you need me to give you feedback if you havent achieved the goal?"
   - Nick, 10:41: "you dont need to ask me every step."
   - Nick, 13:15: "the goal is to build a system which doesnt neeed me".
6. **Rules Nick had to repeat.**
   - The cap he had already removed, and "i thought you had memory..."
   - Stop proposing to kill the pod while working.
   - Two separate videos, not side by side or stacked (Sat 16:16).
   - Research before building. On Saturday the assistant admitted this was the third time it had researched only after testing.
7. **Housekeeping drift.** Files left in chat temp folders, the Mac and box out of sync, the handoff out of date, and nothing committed all weekend.

**Money:**
- Spend I can source: the overnight pod at $14.29, and $0.16 this morning.
- Other runs were each a few cents to about $0.25 where stated, but most were not stated.
- **Weekend total: not computed.**

---

## 8. What we can solve today (ranked)

| # | Task | Who |
|---|---|---|
| 1 | Make `verify.sh` pass. Move the 4 scripts' inputs out of the chat temp folder into the project (for example `refs/` or `live/scan/`) before it gets wiped. | Agent can do |
| 2 | Sync the box with the Mac. Copy the 6 missing scripts and `results.tsv`, and decide where the blend copies live. | Agent can do |
| 3 | Update the hair handoff with the pod-2 cursor numbers, the splash fix and the real cap state. | Agent can do |
| 4 | Commit the weekend's work in mom-character, and in clip-analyzer, blender-funnel and render-desk if you want. | Needs your go |
| 5 | Make the spend caps match on the Mac and the box. | Needs your go on the numbers |
| 6 | Rent a pod (about $0.89/h) and rebuild the scene from scripts: `hair2_body`, `hair2_setup`, `hair2_locks`, `ref_overlay`. | Needs your go |
| 7 | Rebuild the back outline from the new back camera, then score side, three-quarter and back together. | After 6 |
| 8 | Try the cursor recipe (Comb PROJECTED, Pinch, Smooth) on the real hair layers. Never call `snap_curves_to_surface` in the shared Blender. | After 6 |
| 9 | Fix by measured passes, biggest gap first: nape curtain and bun, then the side crescent and hem, then chroma, then the bangs. | After 7 |

The camera work (score the 3 orbit versions, presets with pan and tilt) and the boy's tee and trousers are separate threads. They need your call on priority.

---

## To verify (for Nick only, not checked)
- The cause of the Blender exit at 13:41 Sunday. The suspect is `snap_curves_to_surface`; it is unproven.
- Why Pull Tips and Pinch gave different counts on pod 1 and pod 2 (33 vs 3, 43 vs 57).
- Several of your Sunday messages in the hair chat are missing from the saved chat, though the assistant answers them (10:53, 11:48, 12:19, 13:04, 13:38). Their exact words are unknown.
- Whether the Saturday downloads (demucs and a 346 MB sound model) had your approval. The answer is not in the saved chat.
- Saturday's claims (the boy's tee measurements, 26 analyzer checks passing, the GitHub push of 35 commits) were not re-checked today.
