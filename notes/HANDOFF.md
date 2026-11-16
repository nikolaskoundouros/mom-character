# HANDOFF for the next agent: mom-character (written 16 Nov 2026, about 10:00 UTC)

This replaces the 15 Nov version (still in git at `774c3bb`).

**Evidence labels used below:**
- **[checked 16 Nov]**: seen first-hand on 16 Nov 2026 (file exists, usage read, command output).
- **[ran per <session>, <date>]**: another session reported it working; it has not been re-run since.
- **[untested]**: nobody has run it.

Treat [ran per ...] as a recipe to confirm on first use, not as fact.

## First screen: what to do

1. **Read this file to the end.** Then read these absolute paths; they are not loaded automatically from this folder:
   - `~/.claude/skills/blender/SKILL.md` and `~/.claude/skills/blender-hair/SKILL.md`, plus `build-method.md` and `sources-checklist.md` in the same folder.
   - `~/.claude/skills/live-blender/SKILL.md` and `~/.claude/skills/live-blender/cursor-recipe.md`.
   - Memory in `/Users/nick/.claude/projects/-Users-nick/memory/`:
     - `blender-live-on-pod.md`
     - `mom-character-hair.md`
     - `hair-process-research-every-step.md`
     - `system-that-doesnt-need-nick.md`
     - `pod-idle-10-min-stop.md`
     - `pod-day-cap-removed-2026-11-15.md`
     - `never-save-blender-without-filepath.md`
     - `research-before-execute.md`
     - `aow-3d-runs-on-box.md`

   This project's own memory folder is empty [checked 16 Nov].
2. **Ask Nick for the go to rent a pod.** It costs about $0.89/h (RTX 4090). Never rent without his "go".
3. **Smoke test on the new pod**, before any hair work. This turns the recipes below into first-hand evidence:
   - On the box: `~/Desktop/mom-character/live/pod_live.sh`, run under `flock /tmp/aow-wb-up.lock`. It rents if needed, copies blender-funnel and this project to the pod, starts Blender on the GPU with the MCP add-on, and tunnels box 127.0.0.1:9876.
   - On the box: `python3 ~/Desktop/mom-character/live/bcall.py 'import bpy; print(bpy.app.version_string)'`. Expect 5.2.2.
   - Dismiss the splash. A fresh Blender shows Quick Setup, which swallows the mouse. Run `xdotool mousemove 300 300; xdotool key Escape` on the pod's screen.
   - On the Mac: `FALLOFF=PROJECTED ~/Desktop/mom-character/scripts/harness.sh Comb`. Expect about 900 of 3,000 points moved [ran per cursor session, 16 Nov 08:43: 915].
4. **Rebuild the hair from scripts** (see "Hair"), then continue the task list at the end.

## Goal
- **What:** the mom from "My Mom Cracked The Dinosaur" as a 3D character that matches the reference. Current focus is her hair: a half-up bun, curtain bangs, the lower half to the collar, honey colour, glossy.
- **Reference video:** `/Users/nick/Desktop/My Mom Cracked The Dinosaur 🦖.mp4` [checked 16 Nov, Mac].
- **Reference stills:** head crops in `refs/heads/`; `refs/mom_haircut_analysis.jpg`; `refs/flow_traced.jpg`.
- **Best state so far:**
  - Mean silhouette IoU **0.794**: side 0.821, three-quarter 0.768 [results.tsv row, checked 16 Nov].
  - Saved as `blend/blendpull/mom_hair_L42.blend` [checked 16 Nov: exists on the Mac only, 17.7 MB].
  - The back view is not scored yet.
- **Done means** `./verify.sh` exits 0. Never edit `verify.sh`, `checks/` or `program.md`.

## Machines and access [checked 16 Nov]

| Machine | What it is | What it has |
|---|---|---|
| Mac | Nick's laptop, 8 GB | Never runs Blender. Holds clip-analyzer, the blend copies, `results.tsv` (all 55 runs) and the newest skills and memory. Reaches the box with `ssh nick@37.27.148.115` (BatchMode works). |
| Box `37.27.148.115` | Always-on server, 2 CPU, 3 GB | Claude Code 2.1.295; a `blender` MCP server in `~/.claude.json`; `RUNPOD_API_KEY` and `RUNPOD_SSH_KEY` set in `~/.config/render-desk/render.env` (names only, never print the values); `pod-guard.timer` active; tmux sessions `mom` and `aow`; no `gh`. |
| Pod | RunPod RTX 4090, rented per use | Blender 5.2.2. Sees only files pushed from the box (`workbench push DIR` copies to the same absolute path). |

**Paths are the same everywhere.** The box's home is also `/Users/nick`, so absolute paths like `/Users/nick/Desktop/mom-character/...` are the same on the Mac, the box and the pod.

**Pod commands** (on the box, `~/Desktop/render-desk/bin/workbench`; usage read 16 Nov):

| Command | What it does |
|---|---|
| `up` | rent |
| `status` | `WB up` or `WB down`, and cost |
| `push DIR` | copy a folder to the pod |
| `run 'CMD'` | run on the pod (`$BLENDER` is set) |
| `pull REMOTE LOCAL` | copy back |
| `down` | destroy the pod and log its cost |

**Idle stop:** `pod-guard.timer` on the box terminates a pod 10 minutes after the last workbench or connector command. Each `bcall.py` call counts. A stopped pod loses the live scene.

## Where everything lives [checked 16 Nov]

| What | Path | Machines | Git |
|---|---|---|---|
| This project (hair scripts, cameras, outlines, cursor harness) | `~/Desktop/mom-character` | Mac and box | Local only, no remote. Last commit `774c3bb` (15 Nov 10:53 +02:00). 36 uncommitted entries on the Mac, 120 on the box. |
| Pods (`workbench`, pod guard) | `~/Desktop/render-desk` | box (real), Mac (copy) | Two histories: the box has commits up to 28 Sep plus 12 uncommitted; the Mac copy has no commits. |
| Character and scene pipeline | `~/Desktop/blender-funnel` on the box, `~/Projects/blender-funnel` on the Mac | both | GitHub `nikolaskoundouros/blender-funnel` (private), last pushed 14 Nov 13:34 UTC. Uncommitted changes since: 5 on the box, 10 on the Mac. |
| Clip analyzer (OpenCV motion, faces, sound, captions, COLMAP tools) | `~/Projects/clip-analyzer`, page on port 8570 | Mac only | Local only. 1 commit, 19 uncommitted. |
| PlotPointe Animate page | `~/Projects/plotpointe-animate`, port 8575 | Mac | Local only. |
| Skills | `~/.claude/skills/` (`blender`, `blender-hair`, `live-blender`, `clip-analyzer`, `camera-moves`, `learning-loop`) | Mac. The box lacks `blender` and `blender-hair`. | Not in git. |
| Memory | `/Users/nick/.claude/projects/-Users-nick/memory/` | Mac; the box has a partial copy | Not in git. |
| Older hair handoff | `~/AgencyOS/handoffs/2026-11-15-mom-hair.md` | Mac | Superseded by this file. Its cursor numbers and cap note are out of date. |

## How to run each piece

### Live Blender and the connector
- **Start it:** `live/pod_live.sh` on the box [ran per hair and cursor sessions, 15 and 16 Nov]. `live/pod_live.sh tunnel` only reopens the tunnel.
- **Drive it:**
  - The box's Claude can use the `blender` MCP tools.
  - From any shell on the box: `python3 live/bcall.py 'code'` or `python3 live/bcall.py -f file.py [--timeout 600]` [file and usage read 16 Nov].
- **Look at it:** in the live Blender, `exec(open("/Users/nick/Desktop/mom-character/live/live_tools.py").read())`. Then use `snap()` / `shoot(tag)`, and fetch the images with `workbench pull /root/live_snaps DIR` [ran per sessions 14 and 15 Nov]. The connector's own `look` fails remotely.

### Real mouse (cursor) [ran per cursor session, 16 Nov; recipe file checked 16 Nov]
- **Recipe:** `~/.claude/skills/live-blender/cursor-recipe.md`. Follow it exactly.
- **One held drag:** pass all points as ONE quoted argument: `ssh box "cd ~/Desktop/mom-character && STEP=0.06 live/drag.sh 'x,y x,y ...'"`. Never use `eval` (that turned each drag into 31 clicks).
- **Before the first stroke:** dismiss the splash with Escape, and keep the strands in view.
- **No focus click:** never activate the window first.
- **After the stroke:** leave the mode before reading results.
- **Comb:** needs `brush.falloff_shape = "PROJECTED"`.
- **Slide:** needs surface UVs set by hand (`SURFACE_UV=1` in the harness).
- **Test harness:** `scripts/harness.sh "<Brush>"` (run from the Mac; it scp's to the box) on a throwaway TestSphere/TestHair.
- **Measured on a test object:**

  | Brush | Points moved (of 3,000) |
  |---|---|
  | Comb, PROJECTED | 915 |
  | Slide | 920 |
  | Pinch | 57 |
  | Puff | 52 |
  | Smooth | 27 |
  | Pull Tips | 3 |

  Delete went from 300 to 284 curves; Add went from 300 to 306.
- **[untested]** on the real hair layers (434k and 34k points).

### Hair (build from scripts) [ran per hair session, 15 Nov]
1. **Copy to the pod.** Make sure `scripts/` and `refs/` are on the box, then `workbench push ~/Desktop/mom-character`. The pod only sees the box copy.
2. **Run in the live Blender, in this order** (each via `bcall.py -f` or `exec(open(...).read())`):
   - `scripts/hair2_body.py`: body and outfit, no hair.
   - `scripts/hair2_setup.py`: rest pose.
   - `scripts/hair2_locks.py`: all the hair, built as one connected field of locks with fine strands on top.
   - `scripts/ref_overlay.py`: her frames behind matched cameras from `refs/cams.json`.
3. **Score:** `scripts/fitm.sh GAP FLARE CURL ZEND "label"` (from the Mac). It runs `scripts/fit_multi.py` in the live Blender and prints `FITM ... MEAN=`.
   - It renders only our hair from each reference camera and compares it with `refs/outline_<view>.npy`.
   - Defaults per the old handoff: P_GAP -0.020, P_GAP2 -0.035, P_ZEND 0.035.
4. **Log every pass** as one row in `results.tsv` (on the Mac).

### Clip analyzer [skill `clip-analyzer`; the skill says every command ran on 15 Nov]
- **Where:** Mac only; the box is too small (2 CPU, 3 GB, checked 16 Nov).
- **Page:** `PORT=8570 python3 ~/Projects/clip-analyzer/server.py`.
- **By hand:** `scan.py`, then `build_data.py`, `onscreen.py`, `captions.py`, `sound.py` and `script_align.py`. The steps and outputs are in the skill.
- **COLMAP camera solve:** this step runs on the box.

## Known breakage and drift [checked 16 Nov]
- **`./verify.sh` fails (exit 1).** These files hard-code a Claude chat temp folder (`/private/tmp/claude-501/-Users-nick/e53bbed9-.../scratchpad`, which holds the working masks `vm/`, outputs `ana/` and `scan/`):
  - `scripts/patchscan.py`
  - `outline_auto.py`
  - `viz.py`
  - `viz_multi.py`
  - `fitm.sh`
  - `fit.sh`

  Verify does not scan `.sh`, so it misses the last two. The folder still exists today, but macOS clears `/private/tmp` on reboot. Move its contents into the project and repoint the scripts.
- **Second temp folder:** `~/.claude/skills/live-blender/scripts/{rebuild_live.py,pullcmp.sh,drag.sh}` point into `/private/tmp/.../f3d1b7da-.../scratchpad`. It exists today; same risk. The project's own `live/drag.sh` is clean.
- **The box is missing:**
  - `scripts/outline_auto.py`, `viz.py`, `viz_multi.py`, `fit.sh`, `fitm.sh` and `harness.sh`
  - `results.tsv` rows (the box copy is the header only)
  - `blend/`
  - skills `blender` and `blender-hair`
  - 5 memory files: `blender-skills-library`, `hair-process-research-every-step`, `mom-character-hair`, `pod-day-cap-removed-2026-11-15`, `system-that-doesnt-need-nick`

  `hair2_locks.py`, `fit_multi.py` and `cursor_harness.py` are identical on both machines (md5).
- **The box `notes/HANDOFF.md` is still the old one** that says HOLD.
- **Spend caps differ between the machines.**

  | | Mac `render.env` | Box `render.env` |
  |---|---|---|
  | Monthly | $65 | $40 |
  | Daily | $20 | $20 |
  | `WORKBENCH_DAY_CAP_USD` | 1000 (Nick removed the daily workbench cap on 15 Nov) | not set |

  A rental from the box went through on 16 Nov 08:32.
- **`refs/outline_back.npy` is invalid.** It was built from the old back camera.

## Open mismatches against the reference
These are the hair session's own list at matched cameras, 15 Nov 13:43. Nick has not confirmed them one by one.
- **Back/nape:** ours tapers in and leaves the neck bare. Hers is a full curtain to the collar.
- **Bun:** ours sticks up like a comb. Hers is low, soft and twisted.
- **Back:** hard vertical splits where strand sheets meet.
- **Side:** a crescent at the back-left. Her hem flares out over the shoulder in an S.
- **Bangs:** ours are straight blades. Hers are soft and swept.
- **Colour:** lightness is near hers; chroma is about half. Ours reads pale.
- **Crown dome:** too big. A plain lift cut scored 0.791 against 0.794 and was reverted.
- **Ends and gloss:** ends should curl more, and the top gloss is weaker (Nick, 14 Nov).

## Task list, in order

| # | Task | Who |
|---|---|---|
| 1 | Move the temp-folder contents into the project and repoint the 6 scripts. Make `./verify.sh` exit 0. | Agent can do |
| 2 | Sync the box: the 6 scripts, `results.tsv`, this handoff, and the 2 skills plus 5 memory files. | Agent can do |
| 3 | Commit this project. Push anything to GitHub. | Nick's go |
| 4 | Rent a pod and run the smoke test above. | Nick's go and cost |
| 5 | Rebuild the hair from scripts. Confirm the mean is about 0.794 at L42 settings. | Agent, on the pod |
| 6 | Rebuild the back outline from the new back camera (`view_masks.py`, then `outline_auto.py back`). Add `back` to VIEWS in `fit_multi.py`, and score three views. | Agent |
| 7 | Try the cursor recipe on the real hair layers (Comb PROJECTED, Pinch, Smooth). Record moved-point counts. | Agent |
| 8 | Measured passes, biggest gap first: nape curtain and bun, then the side crescent and hem, then chroma, then bangs. One change per pass, logged in `results.tsv`, keep or revert. | Agent |

## Rules (Nick's, from the weekend chats and memory)
- **Research first:** read the reference, the research (`sources-checklist.md`, the Blender manual via `bman "words"` on the box) and the last result before each step. Say plainly what was done by code and what by hand.
- **Don't stall:** don't ask after every pass. Compare with the reference, find the gap, fix it, show the result. Don't sit idle while the goal is not met.
- **Compare properly:** compare at matched cameras, region by region, pixel by pixel, not thumbnails. Use all angles; the side and back matter as much as the front.
- **One mass:** her hair is one connected mass. The sides sweep up into the bun, and strands rise from the root, then fall.
- **Pod while working:** don't propose killing the pod mid-work.
- **Pod at end of turn:** never end a turn with it billing unless Nick knows.
- **Save every live setting:** write it into a script before the turn ends. Live-only changes die with the pod.
- **Never in a live session:**
  - `bpy.ops.curves.snap_curves_to_surface` (the live Blender exited right after it on 15 Nov; cause unproven);
  - `bpy.ops.wm.read_factory_settings`;
  - saving an open .blend without an explicit filepath.
- **No Blender on the Mac.**
- **Showing videos:** two separate videos, not side by side or stacked.
- **Shell gotchas:**
  - zsh does not split unquoted variables.
  - Never write the bare word blender next to `-a` (a gate hook reads it as a Mac render).
  - Files must reach the box before `workbench push`.
- **Writing:** no em or en dashes. Answer plainly.
