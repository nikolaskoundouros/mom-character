import bpy, os
print("LOCAL", bpy.utils.resource_path("LOCAL"))
print("SYSTEM", bpy.utils.resource_path("SYSTEM"))
print("sysres", repr(bpy.utils.system_resource("DATAFILES")))
for base in (bpy.utils.resource_path("LOCAL"), bpy.utils.resource_path("SYSTEM")):
    p = os.path.join(base, "datafiles", "assets", "nodes", "procedural_hair_node_assets.blend")
    print(p, os.path.exists(p))
