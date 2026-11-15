# Blender 5.3 manual: outfits and cloth (read 15 Nov 2026, with `bman` on the box)

Applies to her polo and trousers and to the boy's T-shirt (blender-funnel). Page paths are under
https://docs.blender.org/manual/en/latest/ ; `bman -p <path>` prints them on the box.

## Three ways the manual offers
1. **Cloth modifier** (physics/cloth/*): the full simulation. Collider objects need Collision physics; the manual
   recommends self-collision and higher `Quality` for "less tears and penetrations".
   - **Sewing springs** (physics/cloth/settings/shape): loose edges (not in any face) that pull panels together, the way
     garments are sewn from flat pieces; set `Max Sewing Force` (zero "can cause instability").
   - **Shrinking Factor**: shrink the cloth to fit tighter; negative grows it.
   - **Rest Shape Key**: "start the cloth simulation in a pre-draped state without applying that shape as a plastic
     deformation". **Dynamic Mesh** lets an armature drive the rest shape.
   - **Pin Group**: weight-painted vertices that hold (collar, waistband).
2. **Cloth Sculpting** (sculpt_paint/sculpting/introduction/cloth_sculpting): "a simplified Cloth Physics Simulation"
   inside Sculpt mode, "especially useful for base mesh creation and larger clothing folds and draping".
   Masked vertices are pinned. Fold size depends on topology: "an optimal and evenly distributed topology is important".
   - **Cloth brush** (sculpt_paint/sculpting/brushes/cloth): simulates cloth only under the cursor; small brush = fast;
     `Persistent` keeps simulating from the same base; `Pin Simulation Boundary` for soft edges. Works with our mouse setup.
   - **Cloth Filter** (sculpt_paint/sculpting/tools/cloth_filter): the whole mesh at once: Gravity, Inflate, Expand, Pinch,
     Scale (makes folds); `Use Collisions` with objects that have Collision physics.
3. **Cloth Dynamics node** (modeling/geometry_nodes/simulation/cloth_dynamics): XPBD, experimental, "Some features are
   currently missing, such as self-collision". Pin Group, Stretchiness, Bendiness.

## What it means for past problems (not tried yet)
- The boy's T-shirt crumpled and rode up when draped (11-13 Nov): the manual's answer is a pre-draped Rest Shape Key or
  Shrinking Factor + pinning at collar/hem, higher Quality and self-collision, not a raw drop.
- "Not smooth or uniform" cloth: fold quality follows topology; even quads first (remesh), then Cloth Filter Gravity with
  collisions for the drape, Cloth brush by mouse for local folds.
