# mom-character: where it stands (15 Nov 2026)

Goal: the mom from "My Mom Cracked The Dinosaur" (reference: ~/Desktop/My Mom Cracked The Dinosaur 🦖.mp4 on the Mac;
head crops in refs/heads, haircut analysis refs/mom_haircut_analysis.jpg, hair flow refs/flow_traced.jpg) as a 3D character
that matches the reference. Current focus: her hair (half-up bun, curtain bangs, lower half to the collar, honey, glossy).

## HOLD (Nick, 15 Nov): no pod jobs until the hair research is done.
Do not run live/pod_live.sh or rent a pod until Nick says the research is finished.

## Run it (everything from the box; the Mac can be closed)
1. `live/pod_live.sh` rents a pod (ask Nick first: ~$0.89/h RTX 4090), copies blender-funnel + this project,
   starts live Blender (GPU-drawn via VirtualGL), tunnels 127.0.0.1:9876 on the box to it. The blender MCP connector
   in the box's Claude then drives it. The box pod-guard stops the pod after 10 idle minutes.
2. In the live Blender, in this order (each one connector call):
   - `exec(open("/Users/nick/Desktop/mom-character/scripts/rebuild_live.py").read())`  (body, outfit, top hair, lower particle hair)
   - `STEP="gloss"; exec(open(".../scripts/finish_hair.py").read())`, then `STEP="top"` the same way
   - gravity: `A,B=1,10; exec(open(".../live/sim.py").read())`, then 11-25, then 26-40
   - `STEP="lower"; exec(open(".../scripts/finish_hair.py").read())`
   - `exec(open(".../live/live_tools.py").read())` then `bpy.app.driver_namespace["shoot"]("tag", samples=64)`
3. `live/pullcmp.sh tag` on the box -> live/tag_cmp.jpg, reference on top, four views below. Send it to Nick.
4. Mouse: `live/drag.sh "x1,y1 x2,y2 ..."` (one stroke per argument; screen_xy() in live_tools gives coordinates).
   Hair brushes (curves sculpt: Comb, Pull Tips, Pinch, Smooth...) and mesh sculpt work by mouse. Never activate the window first.

## Look Nick saw last (14 Nov, render w3)
Shape close: half-up bun, temples swept back, bangs to the brows, lower half to the collar, ends drawn in and turned under,
glossy wet sheen. Nick's open notes: ends should curl more, darker/contrasty vs her lighter honey, top sheen is thin streaks
vs her broad soft sheen, bun is a smooth ball (hers a twisted knot). Back middle "too thick" = shape (flare), not density.

## Rules learned
- Every setting that works goes into a script before the turn ends (a dead pod loses live-only changes).
- Never end a turn with the pod up unless Nick knows it is billing.
- Show both options with pictures when there are two ways (Nick: "if you can do something better and fast, tell me").
- Details on the live setup and gotchas: ~/.claude/skills/live-blender (Mac) and memory blender-live-on-pod.
