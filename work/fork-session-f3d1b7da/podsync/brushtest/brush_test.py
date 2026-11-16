"""Can a script use Blender's hand tools (sculpt brush, particle comb) when Blender has a screen?
Run inside a GUI Blender (virtual display): blender --python brush_test.py
Prints how many vertices / hair tips each stroke moved and saves viewport pictures."""
import os

import bpy
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
KEYS = set(bpy.types.OperatorStrokeElement.bl_rna.properties.keys()) - {"rna_type"}


def stroke(region, pts, size=60):
    out = []
    for i, (x, y) in enumerate(pts):
        e = {"name": "", "mouse": (x, y), "mouse_event": (x, y), "pressure": 1.0, "size": size, "time": float(i),
             "is_start": i == 0, "pen_flip": False, "x_tilt": 0.0, "y_tilt": 0.0, "location": (0.0, 0.0, 0.0)}
        out.append({k: v for k, v in e.items() if k in KEYS})
    return out


def shot(name):
    try:
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)
        bpy.ops.screen.screenshot(filepath=os.path.join(OUT, name))
    except Exception as exc:
        print("screenshot failed:", exc)


def run():
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    w, h = region.width, region.height
    print("STROKE KEYS", sorted(KEYS), "region", w, h)
    import gpu
    print("GPU", gpu.platform.renderer_get(), gpu.platform.version_get(), flush=True)

    def draw():
        with bpy.context.temp_override(window=win, area=area, region=region):
            bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    bpy.context.preferences.view.smooth_view = 0                 # camera moves happen at once, not over 200 ms
    print("region offset", region.x, region.y, "rv3d", area.spaces.active.region_3d.view_distance, flush=True)

    # 1. sculpt: a Draw stroke across a sphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48)
    ob = bpy.context.active_object
    before = np.array([v.co[:] for v in ob.data.vertices])
    with bpy.context.temp_override(window=win, area=area, region=region):
        bpy.ops.view3d.view_axis(type="FRONT")
        bpy.ops.view3d.view_selected()
        bpy.ops.object.mode_set(mode="SCULPT")
        try:
            bpy.ops.brush.asset_activate(asset_library_type="ESSENTIALS", relative_asset_identifier="brushes/essentials_brushes-mesh_sculpt.blend/Brush/Draw")
        except Exception as exc:
            print("brush activate failed:", exc)
        print("SCULPT BRUSH", getattr(bpy.context.tool_settings.sculpt.brush, "name", None), flush=True)
    draw()
    with bpy.context.temp_override(window=win, area=area, region=region):
        pts = [(w * 0.35 + w * 0.30 * i / 29, h * 0.5) for i in range(30)]
        bpy.ops.sculpt.brush_stroke(stroke=stroke(region, pts), mode="NORMAL")
        bpy.ops.object.mode_set(mode="OBJECT")
    print("rv3d after", area.spaces.active.region_3d.view_distance, tuple(round(v,2) for v in area.spaces.active.region_3d.view_location), flush=True)
    d = np.linalg.norm(np.array([v.co[:] for v in ob.data.vertices]) - before, axis=1)
    print(f"SCULPT moved {int((d > 1e-5).sum())} of {len(d)} verts, max {d.max():.4f} m", flush=True)
    shot("sculpt.png")

    # 2. hair: particle hair on a second sphere, then a Comb stroke in Particle Edit
    bpy.data.objects.remove(ob)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16)
    hb = bpy.context.active_object
    m = hb.modifiers.new("hair", "PARTICLE_SYSTEM")
    s = m.particle_system.settings
    s.type = "HAIR"; s.count = 400; s.hair_length = 0.6; s.hair_step = 5
    with bpy.context.temp_override(window=win, area=area, region=region):
        bpy.ops.view3d.view_axis(type="FRONT")
        bpy.ops.view3d.view_selected()
        bpy.ops.particle.particle_edit_toggle()
        bpy.context.scene.tool_settings.particle_edit.tool = "COMB"
        bpy.ops.object.mode_set(mode="OBJECT")
    ps = hb.particle_systems[0]
    tips0 = np.array([p.hair_keys[-1].co[:] for p in ps.particles])
    with bpy.context.temp_override(window=win, area=area, region=region):
        bpy.ops.particle.particle_edit_toggle()
    draw()
    with bpy.context.temp_override(window=win, area=area, region=region):
        pts = [(w * 0.30 + w * 0.40 * i / 29, h * 0.70) for i in range(30)]
        bpy.ops.particle.brush_edit(stroke=stroke(region, pts, size=120))
        bpy.ops.particle.particle_edit_toggle()
    tips1 = np.array([p.hair_keys[-1].co[:] for p in ps.particles])
    d = np.linalg.norm(tips1 - tips0, axis=1)
    print(f"COMB moved {int((d > 1e-4).sum())} of {len(d)} hair tips, max {d.max():.4f} m", flush=True)
    shot("comb.png")
    bpy.ops.wm.quit_blender()


def safe():
    try:
        run()
    except Exception:
        import traceback
        traceback.print_exc()
        bpy.ops.wm.quit_blender()


bpy.app.timers.register(safe, first_interval=2.0)
