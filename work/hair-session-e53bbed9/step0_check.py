import bpy, os, glob, bmesh
print("version", bpy.app.version_string)
root = bpy.utils.system_resource('DATAFILES', path='assets')
print("assets root", root, os.path.isdir(root))
ng, br = [], []
for p in sorted(glob.glob(root + "/**/*.blend", recursive=True)):
    try:
        with bpy.data.libraries.load(p, assets_only=True) as (df, dt):
            ng += [(os.path.relpath(p, root), n) for n in df.node_groups]
            br += [(os.path.relpath(p, root), n) for n in getattr(df, "brushes", [])]
    except Exception as e:
        print("lib error", p, e)
print("node group assets:", len(ng), " brush assets:", len(br))
for rel, n in ng:
    if any(k in n for k in ("Hair", "Curl", "Clump", "Braid", "Roll", "Guide", "Fur", "Frizz", "Dynamics", "Deform")):
        print("  NODE", rel, "|", n)
for rel, n in br:
    if any(k in n for k in ("Curve", "Comb", "Puff", "Pinch", "Snake", "Pull", "Density", "Slide", "Smooth", "Grow", "Cut", "Delete", "Selection", "Add")):
        print("  BRUSH", rel, "|", n)
W = bpy.context.window_manager.windows[0]
sc = W.scene
print("window", W.width, W.height, [(a.type, a.width, a.height) for a in W.screen.areas])
mom = sc.objects["Mom"]
print("Mom modifiers", [(m.type, m.name) for m in mom.modifiers], "parent", mom.parent.name if mom.parent else None,
      "uv", [u.name for u in mom.data.uv_layers], "loc", tuple(mom.location), "dims", tuple(round(d, 3) for d in mom.dimensions))
bm = bmesh.new(); bm.from_mesh(mom.data)
print("Mom non-manifold edges:", sum(1 for e in bm.edges if not e.is_manifold), "of", len(bm.edges)); bm.free()
suit = sc.objects["Mom_female_casualsuit01"]
bm = bmesh.new(); bm.from_mesh(suit.data)
print("suit non-manifold edges:", sum(1 for e in bm.edges if not e.is_manifold), "of", len(bm.edges)); bm.free()
rig = sc.objects["Mom_rig"]
posed = []
for b in rig.pose.bones:
    if b.location.length > 1e-5 or abs(b.rotation_quaternion.w - 1) > 1e-4 or (b.rotation_euler.x, b.rotation_euler.y, b.rotation_euler.z) != (0, 0, 0):
        posed.append(b.name)
print("posed bones:", len(posed), posed[:12], "of", len(rig.pose.bones))
print("head bone:", [b.name for b in rig.pose.bones if "head" in b.name.lower()][:5])
