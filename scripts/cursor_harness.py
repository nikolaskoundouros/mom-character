"""CURSOR HARNESS (15 Nov 2026): test every Curves Sculpt brush by REAL mouse on a clean object, far from the hair scene.
MODE="build"  : (re)create TestSphere + TestHair (300 straight strands) at x=6 m, front orthographic view.
MODE="prep"   : BRUSH="Comb" ... enter Curves Sculpt, activate the brush, print the screen stroke (CLICK/STROKE json) across the strand tips.
MODE="measure": leave the mode, report how many points moved and by how much."""
import bpy, json, numpy as np
from mathutils import Vector, Euler
from bpy_extras.view3d_utils import location_3d_to_region_2d
W = bpy.context.window_manager.windows[0]; sc = W.scene
A = next(a for a in W.screen.areas if a.type == "VIEW_3D"); R = next(r for r in A.regions if r.type == "WINDOW"); SP = A.spaces.active
MODE = globals().get("MODE", "build"); NS = bpy.app.driver_namespace
def view_front():
    SP.shading.type = "SOLID"; rv = SP.region_3d; rv.view_perspective = "ORTHO"
    rv.view_rotation = Euler((1.5707963, 0, 0)).to_quaternion(); rv.view_location = Vector((6.0, 0.0, 0.25)); rv.view_distance = 1.6
    for ar in W.screen.areas: ar.tag_redraw()
if MODE == "build":
    for n in ("TestHair", "TestSphere"):
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)
    for d in [d for d in bpy.data.hair_curves if d.name.startswith("TestHair") and d.users == 0]: bpy.data.hair_curves.remove(d)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(6.0, 0.0, 0.0)); sph = bpy.context.active_object; sph.name = "TestSphere"
    rng = np.random.default_rng(1); N = 300; per = 10; pts = []
    for _ in range(N):
        v = rng.normal(size=3); v[2] = abs(v[2]) + 0.3; v /= np.linalg.norm(v); root = v * 0.12  # LOCAL to the sphere: TestHair is parented to it, world = sphere (x=6) + local (the first version used world coords and put the strands at x=12, off screen)
        if globals().get("WIGGLE"):  # wavy strands so Smooth has something to smooth
            w = np.cross(v, [0, 0, 1.0]); w /= (np.linalg.norm(w) + 1e-9)
            pts += [root + v * 0.30 * t / (per - 1) + w * 0.025 * np.sin(2 * np.pi * t / (per - 1)) for t in range(per)]
        else:
            pts += [root + v * 0.30 * t / (per - 1) for t in range(per)]
    cd = bpy.data.hair_curves.new("TestHair"); cd.add_curves([per] * N)
    cd.attributes["position"].data.foreach_set("vector", np.array(pts, np.float32).reshape(-1)); cd.surface = sph; cd.surface_uv_map = sph.data.uv_layers[0].name
    hair = bpy.data.objects.new("TestHair", cd); sc.collection.objects.link(hair); hair.parent = sph
    if globals().get("SURFACE_UV"):  # surface_uv_coordinate by hand (NOT bpy.ops.curves.snap_curves_to_surface: the live Blender exited right after that call on 15 Nov)
        from mathutils.bvhtree import BVHTree
        from mathutils import interpolate
        bvh = BVHTree.FromObject(sph, bpy.context.evaluated_depsgraph_get()); uvl = sph.data.uv_layers[0].data
        cd.attributes.new("surface_uv_coordinate", "FLOAT2", "CURVE"); uv = []
        for c in range(N):
            p = Vector(pts[c * per]); loc, nor, fi, dist = bvh.find_nearest(p); poly = sph.data.polygons[fi]
            vs = [sph.data.vertices[sph.data.loops[li].vertex_index].co for li in poly.loop_indices]
            wts = interpolate.poly_3d_calc(vs, loc)
            u = sum(w * uvl[li].uv.x for w, li in zip(wts, poly.loop_indices)); v_ = sum(w * uvl[li].uv.y for w, li in zip(wts, poly.loop_indices)); uv += [u, v_]
        cd.attributes["surface_uv_coordinate"].data.foreach_set("vector", np.array(uv, np.float32))
    view_front(); print("built", N, "strands", "uv attr", "surface_uv_coordinate" in cd.attributes)
elif MODE == "prep":
    hair = bpy.data.objects["TestHair"]; view_front()
    with bpy.context.temp_override(window=W, area=A, region=R, active_object=hair, object=hair):
        for o in sc.objects: o.select_set(False)
        hair.select_set(True); bpy.context.view_layer.objects.active = hair
        if hair.mode != "SCULPT_CURVES": bpy.ops.object.mode_set(mode="SCULPT_CURVES")
        r = bpy.ops.brush.asset_activate(asset_library_type='ESSENTIALS', relative_asset_identifier=f'brushes/essentials_brushes-curve_sculpt.blend/Brush/{BRUSH}')
    cs = bpy.context.tool_settings.curves_sculpt
    if globals().get("FALLOFF"): cs.brush.falloff_shape = FALLOFF
    cs.brush.size = 120; cs.unified_paint_settings.size = 120
    n = len(hair.data.points); P = np.zeros(n * 3, np.float32); hair.data.attributes["position"].data.foreach_get("vector", P); NS["h_before"] = P.copy(); NS["h_ncurves"] = len(hair.data.curves)
    tip = Vector((6.0, -0.12 if globals().get('ON_SURFACE') else 0.0, 0.08 if globals().get('ON_SURFACE') else 0.30)); a = location_3d_to_region_2d(R, SP.region_3d, tip); b = location_3d_to_region_2d(R, SP.region_3d, tip + Vector((0.18, 0, 0)))
    st = [[round(R.x + a.x), round(W.height - (R.y + a.y))], [round(R.x + b.x), round(W.height - (R.y + b.y))]]
    print("PREP", BRUSH, "activate", r, "brush", cs.brush.name, "tool", getattr(cs.brush, "curves_sculpt_tool", "?"), "size", cs.brush.size, "strength", round(cs.brush.strength, 2), "falloff", cs.brush.falloff_shape, "mode", hair.mode)
    print("STROKE", json.dumps(st))
else:
    hair = bpy.data.objects["TestHair"]
    with bpy.context.temp_override(window=W, area=A, region=R, active_object=hair, object=hair):
        bpy.ops.object.mode_set(mode="OBJECT")
    n = len(hair.data.points); P = np.zeros(n * 3, np.float32); hair.data.attributes["position"].data.foreach_get("vector", P)
    if len(P) != len(NS["h_before"]):
        print("RESULT", BRUSH, "point count changed", len(NS["h_before"]) // 3, "->", n, "| curves", NS["h_ncurves"], "->", len(hair.data.curves))
    else:
        d = np.linalg.norm((P - NS["h_before"]).reshape(-1, 3), axis=1)
        print("RESULT", BRUSH, "points moved >0.5mm:", int((d > 0.0005).sum()), "of", n, "| max cm", round(float(d.max()) * 100, 2), "| curves", NS["h_ncurves"], "->", len(hair.data.curves))
