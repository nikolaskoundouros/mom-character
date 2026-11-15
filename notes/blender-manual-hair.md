# Blender 5.3 manual: what matters for her hair (read 15 Nov 2026)

Source: https://docs.blender.org/manual/en/5.3/ (the pod runs Blender 5.2.2; check names there). Pages fetched directly;
the reader tools miss the text because ~100k characters of menu come first (use a direct fetch, keep the article body).

## Explains what went wrong on 14 Nov

- **Curl turned locks into flat ribbons.** Curl Hair Curves has a `Subdivision` input: "Higher values produce smoother
  curls". We left it at 1 on strands of ~17 points, so curls were coarse. Also Clump and Curl each built their own guide map;
  the manual says to build one with **Create Guide Index Map** and feed the same `Guide Index` to both ("allows for more
  control and consistency across multiple grooming operations").
  (modeling/geometry_nodes/hair/guides/curl_hair_curves.html, clump_hair_curves.html)
- **White streaky gloss.** Principled Hair (Chiang) `Roughness`: "Too low values will smoothen the hair to the point of
  looking almost metallic, making glints look like Fireflies". We went to 0.09. `Coat` is meant to "Simulate a shiny coat
  of fur", not human hair. For human hair the **Huang model** has `Aspect Ratio` "0.65~0.9 for Caucasian hair" and needs
  curve normals, which curves hair has (legacy particle hair does not). (render/shader_nodes/shader/hair_principled.html)
- **Simulation jumps / memory runaway.** Hair Dynamics (geometry nodes): "Only colliders with closed meshes are supported
  ... Collider meshes with open boundaries can lead to sudden jumping." Her shirt and collar are open meshes.
  Also "keep Substeps below 20 and instead increase the Constraint Iterations"; check `Residual error` (<= 1 is good).
  (modeling/geometry_nodes/simulation/hair_dynamics.html; marked experimental)
- **Brushes and the posed body.** "Curves Sculpt tools only use the original mesh of the surface object and don't take its
  modifiers into account." Her body is posed by an armature modifier, so brushes see the unposed body. Use
  `Snap to Deformed Surface` / `Snap to Nearest Surface` after changes. (sculpt_paint/curves_sculpting/introduction.html)

## The pro workflow the manual describes

1. Few **guide curves**, shaped by hand in Curves Sculpt mode: Comb ("preserving the initial length of every curve
   segment"), Snake Hook ("Extend existing curves in a specific direction"; called Pull Tips in our build), Pinch
   ("Converges adjacent curves"), Puff ("Makes the curves stand up"), Smooth ("makes curve segments ... more parallel"),
   Slide, Density. Header option **Use Sculpt Collision** "Prevents the curve segments from passing through the Surface".
   Add Curves with Interpolate Shape adds strands "already combed" like their neighbours.
2. **Interpolate Hair Curves** fills in the dense hair from the guides; `Distribution Method: Poisson Disk` keeps an even
   spacing; `Density Mask` / `Mask Texture` paint where hair grows.
3. Clump, then Curl (shared guide map), Noise, Frizz, Smooth, Set Hair Curve Profile.
4. Optional **Hair Dynamics** node (XPBD) on the curves themselves for a gravity drape: no particle round trip; needs closed
   colliders.
5. Render: Cycles Curves `Shape: 3D Curves` "for accurate results when viewing curves close up".

## Changes this suggests for her (not tried yet)

- Rebuild the groom as guides + Interpolate Hair Curves (Poisson Disk), groomed by mouse with collision on.
- One guide map; Curl with Subdivision 4+ on the lower ends.
- Huang model, Aspect Ratio ~0.75, roughness up from 0.09, Coat back to 0.
- Drape with geometry-nodes Hair Dynamics against a closed body collider (not the shirt).
