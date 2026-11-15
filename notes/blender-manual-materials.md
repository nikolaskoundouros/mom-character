# Blender 5.3 manual: Principled BSDF (skin, shirt, trousers) and geometry-nodes basics (read 15 Nov 2026)

## Principled BSDF (render/shader_nodes/shader/principled)
OpenPBR-based layers: base (metal / diffuse / subsurface / transmission), specular, optional coat, sheen on top, emission.
- **Skin**: Subsurface `Method: Random Walk (Skin)`, "optimized for skin rendering ... retain greater surface detail and
  color and matches measured skin more closely". `Radius` per RGB, "skin where red light scatters deeper"; "skin has been
  measured to have an anisotropy of 0.8". Weight "Typically should be zero or one". Random Walk "works best for closed meshes".
  Her face read young and plastic: check whether her skin uses subsurface at all.
- **Cloth (polo, trousers)**: Sheen "simulates very small fibers ... For cloth this adds a soft velvet like reflection near
  edges". Thin Wall for "thin structures, such as papers, leaves" (single-layer cloth panels).
- **Coat** here is "a clearcoat, lacquer or car paint" (a wet-skin sheen could use it, not cloth).
- Specular `IOR Level` 0.5 = unchanged; `Anisotropy` (Cycles) stretches highlights along the tangent.

## Geometry nodes: the parts that matter for her (modeling/geometry_nodes/*, ~500 pages)
- **Fields**: per-element functions (dashed links); Sample Index / Attribute Statistic to pull one value out.
- **Baking**: Bake node or Simulation Zone baking stores a result (e.g. a settled drape) so it is not recomputed;
  "Blend-files must be saved to a disk before data can be baked"; bakes are not portable across Blender versions.
- **Deform Curves on Surface** (curve/operations): moves each hair by the difference between the surface's original mesh and
  its final (posed) mesh. The standard pipeline: groom on the rest body (curves sculpt sees only the original mesh), then this
  node carries the hair onto the posed body. Needs the curves' surface + UV map and `surface_uv_coordinate`.
- Sections and page counts (for `bman`): utilities 113, mesh 70, geometry 54, curve 53, volume 42, input 41, hair 33,
  grease_pencil 16, instances 15, point 12, texture 12, attribute 10, simulation 9.
