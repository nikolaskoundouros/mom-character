import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add()
ob=bpy.context.object
vg=ob.vertex_groups.new(name="hair group"); vg.add([v.index for v in ob.data.vertices if v.co.z>0.2],1.0,'REPLACE')
m=ob.modifiers.new("hair",'PARTICLE_SYSTEM'); ps=m.particle_system; s=ps.settings
s.type='HAIR'; s.count=1000; s.hair_length=1.76; s.hair_step=5
ps.vertex_group_density="hair group"
s.render_type='PATH'; s.display_step=3; s.render_step=3
s.child_type='INTERPOLATED'; s.child_percent=200; s.rendered_child_count=200
ps.use_hair_dynamics=True; ps.cloth.settings.quality=5; ps.cloth.settings.pin_stiffness=0.46
ps.cloth.collision_settings.distance_min=0.015
print("version", bpy.app.version_string)
print("type", s.type, "count", s.count, "len", s.hair_length, "children", s.child_type, s.child_percent, s.rendered_child_count)
print("dynamics", ps.use_hair_dynamics, "pin", ps.cloth.settings.pin_stiffness, "quality", ps.cloth.settings.quality, "coll", ps.cloth.collision_settings.distance_min)
dg=bpy.context.evaluated_depsgraph_get(); pe=ob.evaluated_get(dg).particle_systems[0]
print("evaluated particles", len(pe.particles), "child_particles", len(pe.child_particles))
print("hair BSDF node", [n for n in dir(bpy.types) if n=="ShaderNodeBsdfHairPrincipled"])
