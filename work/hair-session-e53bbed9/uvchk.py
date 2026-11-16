import bpy, numpy as np
sc = bpy.context.window_manager.windows[0].scene
ob = next(o for o in sc.objects if o.name.startswith("Lock_Top_0_"))
ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
me = ev.to_mesh()
print("verts", len(me.vertices), "uv layers", [u.name for u in me.uv_layers], "attrs", [a.name for a in me.attributes][:8])
if me.uv_layers:
    uv = np.zeros(len(me.uv_layers[0].data) * 2); me.uv_layers[0].data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
    loop_v = np.zeros(len(me.loops), dtype=int); me.loops.foreach_get("vertex_index", loop_v)
    co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    p = co[loop_v]
    # which uv axis correlates with distance from the root point
    root = co[np.argmin(co[:, 2] * -0 + np.linalg.norm(co - co.mean(0), axis=1) * 0 + (co[:, 1]))]
    d = np.linalg.norm(p - p[np.argmin(uv[:, 0])], axis=1)
    print("uv range x", uv[:, 0].min().round(3), uv[:, 0].max().round(3), "y", uv[:, 1].min().round(3), uv[:, 1].max().round(3))
    print("corr(u, spatial extent along lock):", np.corrcoef(uv[:, 0], p[:, 1])[0, 1].round(2), np.corrcoef(uv[:, 1], p[:, 1])[0, 1].round(2), " z:", np.corrcoef(uv[:, 0], p[:, 2])[0, 1].round(2), np.corrcoef(uv[:, 1], p[:, 2])[0, 1].round(2))
ev.to_mesh_clear()
