"""Hair from scratch, step 0 (15 Nov 2026), run live after hair2_body.py:
 1. head and neck bones back to rest (Curves Sculpt only sees the ORIGINAL mesh, manual page
    sculpt_paint/curves_sculpting/introduction); the posed values are kept in bpy.app.driver_namespace["orig_pose"]
 2. one Empty Hair object on her mesh (manual page modeling/curves_new/primitives): Surface = Mom, parent, deform modifier
 3. Surface UV Map set, viewport aimed at the head
Run: exec(open("/Users/nick/Desktop/mom-character/scripts/hair2_setup.py").read())"""
import bpy
from mathutils import Vector

exec(open("/Users/nick/Desktop/mom-character/live/live_tools.py").read())
sc = WIN.scene
rig, mom = sc.objects["Mom_rig"], sc.objects["Mom"]

orig = {n: (tuple(rig.pose.bones[n].rotation_quaternion), tuple(rig.pose.bones[n].rotation_euler),
            rig.pose.bones[n].rotation_mode, tuple(rig.pose.bones[n].location)) for n in ("neck01", "head")}
if "orig_pose" not in bpy.app.driver_namespace:
    bpy.app.driver_namespace["orig_pose"] = orig
print("posed values (kept):", orig)
for n in ("neck01", "head"):
    b = rig.pose.bones[n]
    b.rotation_quaternion = (1, 0, 0, 0)
    b.rotation_euler = (0, 0, 0)
    b.location = (0, 0, 0)
bpy.context.view_layer.update()

if "Hair_Top" not in sc.objects:
    with ctx(mom):
        for o in sc.objects:
            o.select_set(False)
        mom.select_set(True)
        bpy.context.view_layer.objects.active = mom
        print("add empty hair:", bpy.ops.object.curves_empty_hair_add())
    new = bpy.context.view_layer.objects.active
    new.name = "Hair_Top"
hair = sc.objects["Hair_Top"]
hair.data.surface = mom
hair.data.surface_uv_map = "UVMap"
print("Hair_Top:", hair.type, "surface", hair.data.surface.name, "uv", hair.data.surface_uv_map,
      "modifiers", [(m.type, m.name) for m in hair.modifiers], "parent", hair.parent.name if hair.parent else None)

head = rig.matrix_world @ rig.pose.bones["head"].head
tail = rig.matrix_world @ rig.pose.bones["head"].tail
print("head bone head/tail:", tuple(round(c, 3) for c in head), tuple(round(c, 3) for c in tail))
view_on(Vector((head.x, head.y, head.z + 0.10)), dist=0.9)
