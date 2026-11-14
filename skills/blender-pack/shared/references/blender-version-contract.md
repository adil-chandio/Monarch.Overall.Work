# Blender Version Contract

Every skill in this pack assumes **Blender 4.2 LTS or 4.5 LTS**. Anything written
against 3.x API assumptions is a bug in the skill, not in your Blender.

Read this before running `bpy` through MCP. Version drift is the single most common
cause of an agent silently doing the wrong thing: a call succeeds, the scene changes,
and the result is not what the skill said to make.

## Why a contract, not a preference

Blender's Python API breaks across minor versions in ways that do not raise errors:

| Change | Where | What fails silently |
| --- | --- | --- |
| `Principled BSDF` socket renames | 4.0 | `Specular` → `Specular IOR Level`; `Transmission` → `Transmission Weight`; `Subsurface` → `Subsurface Weight`; `Sheen`/`Sheen Tint` → `Sheen Weight`/`Sheen Tint`; `Emission` → `Emission Color` |
| `Subsurface Radius` semantics | 4.0 | both scale and radius behave differently; the old values give plastic skin |
| Principled `Coat` | 4.0 | `Clearcoat` → `Coat Weight`, `Clearcoat Roughness` → `Coat Roughness` |
| Auto Smooth removal | 4.1 | `mesh.use_auto_smooth` is gone; use `bpy.ops.object.shade_smooth_by_angle()` or the Weighted Normal modifier |
| `bpy.context.view_layer.objects.active` | stable, but | setting `select_set(True)` alone no longer activates; the operator acts on the previous active object |
| Eevee | 4.2 | Eevee Next; `use_gtao` is gone, `use_raytracing` replaced it; old AO settings do nothing |
| Color management | 4.0 | `Filmic` replaced by `AgX`; a scene still set to Filmic renders flat and desaturated under 4.x |
| `bmesh.ops` signatures | occasional | keyword renames raise, but geometry can be wrong without an error |
| Cycles denoiser | 4.1+ | OIDN GPU vs CPU availability differs; a silently CPU-only run is 10x slower |

## Rules

1. **Query before you write.** At the start of any session that will execute `bpy`,
   read `bpy.app.version` and record it. If it is below 4.0, stop and say so.
2. **Set sockets by name, and check the name exists.** Never index a Principled
   socket by number; the order changed in 4.0.
   ```python
   bsdf = mat.node_tree.nodes["Principled BSDF"]
   for name, value in {"Base Color": (0.8, 0.1, 0.1, 1),
                       "Roughness": 0.4,
                       "Coat Weight": 1.0}.items():
       if name in bsdf.inputs:
           bsdf.inputs[name].default_value = value
   ```
3. **Never assume a rendering engine default.** Write the engine explicitly:
   `scene.render.engine = 'BLENDER_EEVEE_NEXT'` on 4.2+, `'BLENDER_EEVEE'` before.
4. **Color management is part of the look.** State the view transform in the scene
   setup, not in a comment: `scene.view_settings.view_transform = 'AgX'`.
5. **Auto-smooth is a modifier now.** For hard-surface work that needs sharp edges
   on smooth shading, the contract is: shade smooth, then Weighted Normal, then
   mark sharp edges. Do not call `use_auto_smooth`.
6. **If a socket or operator is missing, report it.** Do not "fix" a missing socket
   by picking a similar one. That is how a specular map ends up driving roughness.

## Reporting the version

When a skill produces a scene, its validation note should carry the version it was
built on:

```
blender 4.5.2 LTS · eevee next · agx · 1280x720 @ 30fps
```

If the version is not in the note, the scene is not reproducible and the skill has
not done its job.
