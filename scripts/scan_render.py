# renders, for each hi-res view, three images: normal, LOCKS in magenta (flat ribbons showing through the strands), BODY+CAP in magenta (skin/scalp showing)
import bpy
from mathutils import Vector
exec(open("/Users/nick/Desktop/mom-character/live/live_tools.py").read())
sc = WIN.scene; gpu_cycles()
cam = sc.camera
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 800, 1000, 100
sc.cycles.samples = 24
mag = bpy.data.materials.get("_Magenta") or bpy.data.materials.new("_Magenta")
mag.use_nodes = True; nt = mag.node_tree; nt.nodes.clear()
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1, 0, 1, 1)
o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], o.inputs["Surface"])
mom = sc.objects["Mom"]; cap = bpy.data.objects.get("Hair2_Cap")
locks = [ob for ob in sc.objects if ob.name.startswith("Lock_") and ob.type == "CURVE"]
V = {"top": ((0.0, -0.03, 2.25), (0.0, -0.03, 1.62), 85), "crown": ((0.0, 0.50, 2.00), (0.0, 0.00, 1.64), 85),
     "ear": ((-0.38, -0.02, 1.58), (0.0, -0.02, 1.58), 85), "back": ((0.0, 0.62, 1.58), (0.0, 0.0, 1.56), 70),
     "front": ((0.0, -0.62, 1.60), (0.0, 0.0, 1.58), 70)}
def shoot(tag, k, loc, at, lens):
    cam.data.lens = lens; cam.location = Vector(loc)
    cam.rotation_euler = (Vector(at) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = f"/root/live_snaps/scan_{tag}_{k}.png"; bpy.ops.render.render(write_still=True, scene=sc.name)
for k, (loc, at, lens) in V.items():
    shoot("n", k, loc, at, lens)
# locks magenta
orig = {ob.name: [m for m in ob.data.materials] for ob in locks}
for ob in locks:
    ob.data.materials.clear(); ob.data.materials.append(mag)
for k, (loc, at, lens) in V.items():
    shoot("lock", k, loc, at, lens)
for ob in locks:
    ob.data.materials.clear()
    for m in orig[ob.name]: ob.data.materials.append(m)
# body + cap magenta
slots = [s.material for s in mom.material_slots]
for s in mom.material_slots: s.material = mag
capm = None
if cap:
    capm = list(cap.data.materials); cap.data.materials.clear(); cap.data.materials.append(mag)
for k, (loc, at, lens) in V.items():
    shoot("skin", k, loc, at, lens)
for s, m in zip(mom.material_slots, slots): s.material = m
if cap:
    cap.data.materials.clear()
    for m in capm: cap.data.materials.append(m)
print("scan renders done:", len(V) * 3)
