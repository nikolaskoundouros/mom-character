# Can code set particle hair guide shapes headless? Test A: write hair_keys directly. Test B: Curves -> particle system operator.
import bpy, numpy as np
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1); ob = bpy.context.object
m = ob.modifiers.new("hair", 'PARTICLE_SYSTEM'); s = m.particle_system.settings
s.type = 'HAIR'; s.count = 20; s.hair_length = 1.0; s.hair_step = 5
dg = bpy.context.evaluated_depsgraph_get(); dg.update()
ps = ob.particle_systems[0]
print("A keys per particle", len(ps.particles[0].hair_keys), "first", tuple(ps.particles[0].hair_keys[-1].co))
for p in ps.particles:
    r = np.array(p.hair_keys[0].co)
    for k, hk in enumerate(p.hair_keys):
        hk.co = tuple(r + np.array([0.5 * k / 5, 0, -0.4 * k / 5]))
dg.update()
ev = ob.evaluated_get(dg).particle_systems[0]
print("A after write, evaluated tip", tuple(ev.particles[0].hair_keys[-1].co), "orig", tuple(ps.particles[0].hair_keys[-1].co))
print("A co_hair_space tip via ev", tuple(ev.co_hair(ob, particle_no=0, step=5)))
# Test B
cu = bpy.data.hair_curves.new("C") if hasattr(bpy.data, "hair_curves") else None
print("B hair_curves datablock:", cu is not None, "ops:", [o for o in dir(bpy.ops.curves) if "particle" in o])
