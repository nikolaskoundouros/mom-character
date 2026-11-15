"""The tutorial's method for her lower hair (particle hair, 0:15 to 0:49 of the FilmTush short):
painted scalp area (vertex group) -> Particle System, Hair -> interpolated children -> Hair Dynamics with a pin goal
and collisions, then gravity settles it. Run inside the live pod Blender with exec(); uses the scene already built.
Knobs: os.environ DYN_* (see below)."""
import os

import bpy
import numpy as np
from mathutils import Vector

from recipes import haircut, human, sculpt
from recipes import rig as _rig

env = lambda k, d: type(d)(os.environ.get(k, d))
sig = haircut._sigmoid
W = bpy.context.window_manager.windows[0]
sc = W.scene
S = dict(gender=0.0, age=0.70, muscle=0.45, weight=0.50, height=0.55, proportions=0.6, cupsize=0.75, firmness=0.6, caucasian=1, african=0, asian=0)
base = human.morphed_base(**S)
scalp = haircut.Scalp(base)
lm = sculpt.landmarks(human.to_blender(base))
E, F = scalp.eye_z, scalp.lm["front_y"]
rig = next(o for o in sc.objects if o.type == "ARMATURE")

# 1. the painted area (tutorial 0:15 "paint the area you want hair to grow"): the lower half, under the half-up line
v = scalp.verts
h, back, x = v[:, 2] - E, v[:, 1] - F, np.abs(v[:, 0])
fl = 0.060 - 0.025 * np.clip(x / 0.07, 0, 1)
w_face = sig(0.085 - back, 0.008)
w_side = sig(0.14 - back, 0.008) * (1 - w_face)
line = w_face * fl + w_side * (-0.005) + (1 - w_face - w_side) * (-0.075)
ears = np.hypot(v[:, 1] - (F + 0.105), v[:, 2] - (E - 0.03))
grow = sig(h - line, 0.004) * np.where(x > 0.055, sig(ears - 0.036, 0.004), 1.0)
top_line = 0.000 + (0.035 - 0.000) * sig(back - 0.15, 0.015)
weight = grow * sig(top_line - h, 0.006) * sig(back - 0.112, 0.006)      # under the half-up line, behind the ears

used = sorted({i for f in scalp.faces for i in f})
remap = {o: n for n, o in enumerate(used)}
me = bpy.data.meshes.new("ScalpLower")
me.from_pydata([tuple(v[i]) for i in used], [], [tuple(remap[i] for i in f) for f in scalp.faces])
me.update()
old = bpy.data.objects.get("ScalpLower")
if old:
    bpy.data.objects.remove(old, do_unlink=True)
em = bpy.data.objects.new("ScalpLower", me)
sc.collection.objects.link(em)
vg = em.vertex_groups.new(name="hair group")
for o, n in remap.items():
    if weight[o] > 0.01:
        vg.add([n], float(weight[o]), "REPLACE")
lift = em.modifiers.new("LiftOffHead", "DISPLACE"); lift.mid_level = 0.0; lift.strength = 0.006   # roots outside the head's collision shell
_rig.parent_to_bone(em, rig, "head")

# 2. particle hair (tutorial 0:21 to 0:28), growing down instead of straight out (stands in for the combing at 0:29)
m = em.modifiers.new("hair", "PARTICLE_SYSTEM")
ps = m.particle_system
s = ps.settings
s.name = "LowerHair"
s.type = "HAIR"
s.count = env("DYN_GUIDES", 1500)
s.hair_step = env("DYN_STEPS", 10)
s.display_step = s.render_step = 4
s.use_advanced_hair = True
# in this mode the length comes from the growth speed: measured 4.13 m per unit speed on 14 Nov, so scale to DYN_LEN
k = env("DYN_LEN", 0.13) / 4.13
s.normal_factor = env("DYN_NORMAL", 0.25) * k
s.object_align_factor = (0.0, env("DYN_BACK", 0.25) * k, -1.0 * k)   # out and down: starting clear of the neck and collar keeps the simulation stable
ps.vertex_group_density = "hair group"
s.render_type = "PATH"
import mom_hair
mat = mom_hair.hair_material("HairLowerDark", env("DYN_MEL", 0.62), 0.50, root=0.04)   # darker chestnut underneath
me.materials.append(mat)
s.material = len(me.materials)
em.show_instancer_for_render = False      # "Show Emitter" off
# 3. interpolated children (tutorial 0:34 to 0:39)
s.child_type = "INTERPOLATED"
s.child_percent = env("DYN_CHILD_VIEW", 40)
s.rendered_child_count = env("DYN_CHILD", 80)
s.clump_factor = env("DYN_CLUMP", 0.55)
s.clump_shape = -0.2
s.kink = "WAVE"; s.kink_amplitude = env("DYN_WAVE", 0.005); s.kink_frequency = 1.6; s.kink_shape = 0.3
s.roughness_1 = s.roughness_2 = s.roughness_endpoint = 0.0
s.root_radius = s.tip_radius = 1.0
s.radius_scale = env("DYN_RADIUS", 0.00011) * 2
s.tip_radius = 0.3
# 4. hair dynamics with pin goal and collisions (tutorial 0:43 to 0:48)
ps.use_hair_dynamics = True
cs = ps.cloth.settings
cs.quality = 10
cs.pin_stiffness = env("DYN_PIN", 0.46)
cs.bending_stiffness = env("DYN_BEND", 3.0)
cs.mass = env("DYN_MASS", 0.3)
ps.cloth.collision_settings.distance_min = 0.004
ps.cloth.collision_settings.collision_quality = 2
for name in ("Mom", "Mom_female_casualsuit01", "Collar"):
    o = bpy.data.objects.get(name)
    if o and not any(md.type == "COLLISION" for md in o.modifiers):
        o.modifiers.new("Collision", "COLLISION")
        o.collision.thickness_outer = 0.002
ps.point_cache.frame_start, ps.point_cache.frame_end = 1, 60
print(f"lower hair: {s.count} guides x {s.rendered_child_count} children, about {env('DYN_LEN', 0.13)} m, pin {cs.pin_stiffness}")
