---
name: blender-hair
description: Everything learned so far about making hair in Blender for Nick's characters, so a new head does not start from scratch. The craft that applies to any character (guides then Interpolate Hair Curves, curl and clump, ends, the Principled Hair shader, Hair Dynamics, brush limits), the 2.79 "locks" method from the Hair With Curves video, what the hair-cards article adds, the mom's project state and what went wrong, and what is still unverified. Use for any hair groom, hairstyle, bun, bangs, hair shader or hair sim, and when Nick types /blender-hair.
argument-hint: [which hair job]
---

# /blender-hair

Run /blender first (tools, rules, pod cost). This page holds the hair craft only.
Checked 15 Nov 2026. The pod runs Blender 5.2.2, the manual notes are from the 5.3 manual: names can differ, check on the pod.

## Craft that applies to any character
Source: ~/Desktop/mom-character/notes/blender-manual-hair.md and blender-manual-materials.md (Blender 5.3 manual, read 15 Nov).
Offline manual on the box: `bman "words"`. Quotes marked [checked] I compared myself against the saved page
~/Projects/hair-research/manual/hair_principled.html on 15 Nov; the rest are as the notes give them.

**The pro flow the manual describes**
1. Few guide curves, shaped by hand in Curves Sculpt mode (mouse, see /blender). Header option Use Sculpt Collision
   keeps segments out of the surface. Add Curves with Interpolate Shape adds strands already combed like neighbours.
2. Interpolate Hair Curves fills the dense hair from the guides; Distribution Method Poisson Disk keeps spacing even;
   Density Mask or Mask Texture paints where hair grows.
3. Then Clump, Curl, Noise, Frizz, Smooth, Set Hair Curve Profile.
4. Optional Hair Dynamics node (geometry nodes, XPBD, marked experimental) for gravity drape.
5. Cycles Curves Shape: 3D Curves, "for accurate results when viewing curves close up".

**Curl and clump.** Curl Hair Curves has a Subdivision input; higher is smoother. At 1 on about 17-point strands the
curls came out coarse and ribbon-like (14 Nov). Build one guide map with Create Guide Index Map and feed the same Guide Index
to Clump and Curl.

**Ends.** Roll Hair Curves "coils or curls the tips of hair curves, rolling them inward or outward": Roll Length,
Roll Radius, Roll Depth, Roll Taper, Subdivision, Retain Overall Shape, Preserve Length. Built for curled-under ends.

**Shader (Principled Hair).**
- Chiang Roughness [checked]: "Too low values will smoothen the hair to the point of looking almost metallic, making
  glints look like Fireflies". Coat [checked]: "Simulate a shiny coat of fur", so not for human hair.
- Huang model [checked]: Aspect Ratio recommended "0.65~0.9 for Caucasian hair" (0.8~1 Asian, 0.5~0.65 African); its major
  axis follows the curve normal, "not supported in legacy particle hair". So Huang needs curves hair, not particle hair.

**Hair Dynamics.** Only closed-mesh colliders; open meshes "can lead to sudden jumping". Keep Substeps below 20 and raise
Constraint Iterations; check Residual error (1 or less is good). A shirt or collar that is an open mesh will jump.

**Brushes and posed bodies.** Curves Sculpt tools "only use the original mesh of the surface object" and ignore its
modifiers. Groom on the rest body, then carry the hair onto the pose with Deform Curves on Surface; use Snap to Deformed
Surface or Snap to Nearest Surface after changes.

## The 2.79 locks method (video "Blender Tutorial - Hair With Curves", 20:40)
Source: ~/Projects/hair-research/page/hair_research.html, evidence in ~/Projects/hair-research/video (1 frame per second,
whisper transcript, key overlay). I re-checked two frames and the transcript lines myself: 2:36 (Blender v2.79, Ctrl+T tilt
-43.6, Bevel Object BezierCircle) and 18:01 (Anisotropic BSDF GGX roughness 0.635, anisotropy 0.800, rotation 0.247, mix
0.387; Principled subsurface 0.100). The rest below is the research chat's reading, not re-checked by me.
- It is Blender 2.79 Path curves with a Bezier Circle as bevel. It is not the Curves hair object and shows no brushes.
- One lock = one path plus the shared bevel; width with Alt+S and twist with Ctrl+T per point, then copy and rotate round the
  3D cursor; editing the shared bevel grooves every lock at once.
- Shading along each lock: curve setting Use UV for mapping, a Noise texture driving Bump and a colour ramp, a gradient that
  darkens roots, ends mixed with a Transparent BSDF so tips break into strands.
- Every setting is a number, so it can be written as code.

## The hair-cards article (yelzkizi.org, 27 Apr 2025)
Game-engine hair cards. Its own FAQ says the Principled Hair BSDF is for strand hair, not cards. Only three things carry
to Cycles strands (research chat's reading): an opaque under-layer for volume, small per-lock colour shifts (about 5 %),
thin pieces at the hairline. Full text: ~/Projects/hair-research/article/text.md.

## Two ways to build a groom (Nick decides per job)
| | A: locks in code (video) | B: guides by mouse then Interpolate (manual) |
|---|---|---|
| Good for | the bun and twisted knots, a solid under-layer | the flowing top, bangs, lower length |
| How | path per lock + shared bevel, numbers in a script | Add, Comb, Pull Tips on guides, Interpolate Hair Curves |
| Catch | old 2.79 idea, needs a 5.2 test | needs the mouse and the GPU-drawn screen |
Research chat's pick for the mom's bun: A. Manual notes' pick for the rest: B. Not tried yet on the mom.

## Project pointer: the mom (~/Desktop/mom-character, git)
Read notes/HANDOFF.md first: it holds the HOLD (no pod jobs until Nick says the research is done) and the run order.
Look Nick saw last (render w3, 14 Nov), his open notes: ends should curl more; darker and more contrasty than her honey;
top sheen is thin streaks where hers is broad and soft; bun is a smooth ball where hers is a twisted knot.
Not on the mom yet, each from the notes: raise roughness from 0.13, Coat back to 0 (finish_hair.py sets 0.16), Huang
Aspect Ratio about 0.75, Roll Hair Curves for the ends, one guide map for clump and curl, locks for the bun, under-layer.

## To verify (not confirmed by me)
- Anisotropic BSDF versus Glossy in 5.2; whether Use UV for mapping on curves still exists in 5.2 (pod test).
- Names that may differ between the 5.3 manual and the 5.2.2 pod (Pull Tips versus Snake Hook).
- Whether roughness went to 0.09 live on 14 Nov (the notes say so, finish_hair.py has 0.13, never saved).
- Which parameter set made render w3: live-blender/scripts/rebuild_live.py has N_TOP 60000, N_BANG 9000; the mom-character
  copy has N_TOP 20000, N_BANG 3500 (the research page says w3 had 60,000 and 9,000).

## Learned (add one line per job: what, source, date)
