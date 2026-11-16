---
name: blender
description: Front door for every Blender job in Nick's 3D work (hair, outfits, characters, live Blender on the pod). Says which tool does which job (real mouse, connector code, or script file), which topic skill and project notes to read first, the standing Blender rules with their sources, and how to save what was learned so the next job does not start from scratch. Use whenever Nick types /blender or asks for any Blender build, groom, sculpt, pose, outfit, material or render task.
argument-hint: [what to do in Blender]
---

# /blender

Written 15 Nov 2026 from: skill live-blender, memory blender-live-on-pod, never-save-blender-without-filepath,
tailor-the-garment-one-layer, research-by-topic, and ~/Desktop/mom-character/notes/HANDOFF.md.
This page adds no rule Nick did not give: every line below names its source. If a source and this page disagree,
the source wins and this page gets fixed.

## Do this first, in order
1. Say the plan: "Nick asked me to X, my plan: a, b, c" (memory index: SAY THE PLAN FIRST).
2. Read the topic skill for the job (list below), then the project's `notes/HANDOFF.md` (it holds holds and last state;
   mom: ~/Desktop/mom-character/notes/HANDOFF.md).
3. Read memory `blender-live-on-pod.md` (measured details and the cost incident).
4. Before touching the pod: say the cost and wait for Nick's "go" (see rules).

## Which tool does which job
Nick, 15 Nov 2026: "i dont need to tell the model to use its cursor for example. because im sure you would start
making python scripts again". So: if a job is in a Mouse row, use the mouse. Do not swap in a script brush or a
code-built imitation. Source of every row: memory `blender-live-on-pod.md` (proven 14 Nov 2026) and live-blender SKILL.md.

| Job | Use | Not this |
|---|---|---|
| Curves hair brushes: Add, Comb, Pull Tips, Pinch, Smooth, Density | real mouse: `drag.sh` (xdotool) on the GPU-drawn screen | `sculpt_curves.brush_stroke` from code returns PASS_THROUGH |
| Mesh sculpt Grab, Smooth | real mouse | Grab by scripted stroke "has no effect" |
| Mesh sculpt Draw | mouse, or `sculpt.brush_stroke` (raised a sphere about 10 cm) | |
| Particle hair Comb | mouse, or `particle.brush_edit` (combed visibly) | |
| Materials, node trees, modifiers, geometry nodes, object settings | connector `execute_blender_code` | |
| Seeing the result | `snap()` / `shoot(tag)` from live_tools.py, then `pullcmp.sh TAG` | connector `look` (fails remotely) |
| A setting that worked live | write it into a script file in the project | leaving it live only (dies with the pod) |

Proven by mouse on 14 Nov: curves hair Add (1,160 hairs from 3 drags) and Comb (516 tips moved about 6 cm), mesh
Draw, Grab, Smooth. Pull Tips, Pinch and Density are listed by the manual and by live-blender as mouse brushes but
were not individually run: try one stroke and look before relying on it.

Mouse details: screen X = region.x + mx, Y = window.height - (region.y + my), or `screen_xy(point)`. Never activate
the window before a batch of strokes (the first press is swallowed). Enter a mode in one call, stroke in the next,
read the result only after leaving the mode. In the 5.3 manual Pull Tips is called Snake Hook.

## Standing rules (each with its source)
- Pods cost money, $0.59 to $1.19 an hour: say the cost, get Nick's "go" before `workbench up` (live-blender).
- The monthly spend cap was used up on 15 Nov 2026; only Nick raises it (live-blender). Check before renting.
- Never end a turn with the pod up unless Nick knows it is billing; the pod guard stops an idle pod after 10 minutes
  (Nick, 15 Nov: "after 10 idle minutes please shut the pod down"). Cost incident 14 to 15 Nov: $14.29 (blender-live-on-pod).
- Blender never runs on the Mac, 8 GB (live-blender).
- Never `bpy.ops.wm.save_mainfile()` without an explicit filepath; print `bpy.data.filepath` first (never-save-blender-without-filepath).
- Never `bpy.ops.wm.read_factory_settings` in a live session; `bpy.context.window` is None in connector calls, use
  `bpy.context.window_manager.windows[0]` (blender-live-on-pod).
- Write `--auto-servernum`, never `-a`, next to the bare word blender (gate hook rule 14, blender-live-on-pod).
- Every setting that works goes into a script before the turn ends (live-blender, mom HANDOFF).
- Read the manual page before using a tool: `bman "words"` on the box, offline (mom HANDOFF, rules learned).
- Two ways to do it: show both with pictures and say which you pick; Nick: "if you can do something better and fast, tell me" (mom HANDOFF).
- Clothes: reshape the garment's own mesh in one layer, never lay shells or panels on top (tailor-the-garment-one-layer).
- Research is by topic and remade from tutorials first; apply to a reference after (research-by-topic).
- A project's own HANDOFF can hold a hold (mom: no pod jobs until Nick says the hair research is done, 15 Nov).

## Topic skills (each holds the research for one craft)
- `/blender-hair`: written, see its own page.
- `/blender-outfits`, `/blender-character`: not written yet. Existing material to start from: mom-character
  `notes/blender-manual-outfits.md` and `blender-manual-materials.md`, memory `tailor-the-garment-one-layer`, `hero-character`.

## After every Blender job, so the next one is not from scratch
1. Settings that worked: into the project's `scripts/`.
2. Craft learned: one line in the topic skill under "Learned", with source and date. Link the note, do not paste it.
3. Project state and holds: the project's `notes/HANDOFF.md`.
4. Pod: stopped, or say in one line that it is billing.

## Where this lives
Mac: ~/.claude/skills. The 3D System box (nick@37.27.148.115) lists the same folders (checked 15 Nov 2026 for live-blender).
Not checked: how a new skill reaches the box. After saving, look for it there.
