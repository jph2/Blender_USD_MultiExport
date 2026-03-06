# Handoff: Animation Export + Looks Rename Implementation

**Version**: 1.1.1 | **Date**: 06.02.2026 | **Time**: 19:50 | **GlobalID**: 20260206_1915_BlenderUSDME_AnimLooks_Handoff

**Tag block:**
#workflow_automation #export #usd_core #extension_development #blender #openusd #omniverse #hybrid #conversion #references #analysis #layers #composition #framework_integration #ai_coding_agents #validation #quality_assurance #best_practices #case_study #workflow_optimization

---

## Executive Summary

This consolidated handoff covers implementation of **three requirements** for the Blender USD MultiExport addon. Implementation order is critical.

| Order | Requirement | Priority | Description |
|-------|-------------|----------|-------------|
| 1 | **REQ-EXP-023** | Medium | Materials Scope → "Looks" rename (Omniverse convention) |
| 2 | **REQ-EXP-028** | Medium | Full Animation Export - all Blender-supported types |
| 3 | **REQ-EXP-029** | Low | Separate Animation Layer Export |

**Target Version**: v0.1.88

---

## Research Foundation (REQ-EXP-029)

**Full research documented in**: `00_Discovery.md` → "Session: Animation Layer Separation Research"

Key research findings that influenced implementation:

| Finding | Source | Impact |
|---------|--------|--------|
| `def→over` must be **selective** | NVIDIA Specifiers docs, Second Opinion, NIM | Keep `SkelAnimation` as `def` |
| `over` doesn't ignore geometry data | openusd.org, NIM | Must strip non-animated properties |
| `material:binding` can override lookdev | Sdf docs, NIM | Must remove from anim layer |
| UsdSkel designed for separation | UsdSkel Schemas, NIM | Use standard `SkelAnimation` pattern |
| Skeleton/SkelRoot should be `over` | NIM validation | Animation layer overrides, not redefines |
| Don't strip `skel:animationSource` | NIM warning | Required for skeleton binding |

### Reference Links

- [NVIDIA Learn OpenUSD - Specifiers](https://docs.nvidia.com/learn-openusd/latest/composition-basics/specifiers.html)
- [UsdSkel Schemas In-Depth](https://openusd.org/docs/api/_usd_skel__schemas.html)
- [Pixar Tutorial - Transformations & Animation](https://openusd.org/release/tut_xforms.html)
- [Blender USD Export Manual](https://docs.blender.org/manual/en/4.0/files/import_export/usd.html)
- [GitHub Issue #2246 - Multiple SkelAnimations](https://github.com/PixarAnimationStudios/USD/issues/2246)

---

## CRITICAL DESIGN CONSTRAINT: Animation vs. Normalization Conflict

### The Problem

**Baking transforms into mesh points destroys animation time-samples.**

The current `usd_bake.py` post-processing bakes scale/transforms into mesh point data:
- `normalize_position` = bake position into geometry
- `normalize_scale` = bake scale into geometry  
- `normalize_rotation` = bake rotation into geometry

When animation is enabled, USD stores `xformOp` time-samples (per-frame transform data). If we bake transforms into mesh points, those time-samples become meaningless.

### The Solution: Either/Or Setting

**Animation and Transform Normalization are mutually exclusive.**

When `export_animation = True`:
- Disable or grey-out: `normalize_position`, `normalize_scale`, `normalize_rotation`
- Skip the mesh point baking step in `usd_bake.py`
- Only set stage metadata (`metersPerUnit`, `upAxis`)

When `export_animation = False`:
- Current behavior unchanged
- Normalization options work as expected

### UI Implementation

```python
# In ui.py - Animation section
if start_point.export_animation:
    # Show warning about normalization conflict
    warn_row = box.row()
    warn_row.alert = True
    warn_row.label(text="Animation disables transform normalization", icon="INFO")

# In normalize section - disable when animation is on
row_norm = box_norm.row(align=True)
row_norm.enabled = not start_point.export_animation  # DISABLE when animation is on
row_norm.prop(start_point, "normalize_position", text="Normalize Position")
```

---

## PHASE 1: REQ-EXP-023 - Materials → Looks Rename

### Requirement

Rename the `/Materials` Scope prim to `/Looks` in exported USD files to conform with NVIDIA Omniverse standards.

### Implementation

Add function to `usd_bake.py`:

```python
def rename_materials_to_looks(filepath: str, logger=None, start_point_context=None) -> Dict[str, Any]:
    """Rename /Materials scope to /Looks for Omniverse conformance.
    
    Also updates all material:binding relationships to use /Looks/ paths.
    """
    result = {"success": False, "materials_renamed": False, "bindings_updated": 0}
    
    try:
        from pxr import Usd, Sdf
    except ImportError:
        result["reason"] = "pxr_unavailable"
        return result
    
    stage = Usd.Stage.Open(filepath)
    if not stage:
        result["reason"] = "stage_open_failed"
        return result
    
    root_layer = stage.GetRootLayer()
    
    # Find /Materials prim
    materials_path = Sdf.Path("/Materials")
    materials_prim = stage.GetPrimAtPath(materials_path)
    
    if not materials_prim or not materials_prim.IsValid():
        # No Materials prim - nothing to rename
        result["success"] = True
        result["reason"] = "no_materials_prim"
        return result
    
    # Use Sdf.BatchNamespaceEdit for atomic rename
    edit = Sdf.BatchNamespaceEdit()
    looks_path = Sdf.Path("/Looks")
    
    # Move /Materials to /Looks
    edit.Add(materials_path, looks_path)
    
    # Apply the edit
    if not root_layer.Apply(edit):
        result["reason"] = "rename_failed"
        return result
    
    result["materials_renamed"] = True
    
    # Update all material:binding relationships
    binding_count = 0
    for prim in stage.Traverse():
        if prim.HasRelationship("material:binding"):
            binding_rel = prim.GetRelationship("material:binding")
            targets = binding_rel.GetTargets()
            new_targets = []
            changed = False
            for target in targets:
                target_str = str(target)
                if target_str.startswith("/Materials/"):
                    new_target = target_str.replace("/Materials/", "/Looks/", 1)
                    new_targets.append(Sdf.Path(new_target))
                    changed = True
                else:
                    new_targets.append(target)
            if changed:
                binding_rel.SetTargets(new_targets)
                binding_count += 1
    
    result["bindings_updated"] = binding_count
    
    stage.Save()
    result["success"] = True
    return result
```

### Integration Point

Call `rename_materials_to_looks()` in `ops_export.py` after `bake_usd_geometry()`:

```python
# After bake_usd_geometry call
if bake_result.get("success"):
    # REQ-EXP-023: Rename Materials → Looks for Omniverse conformance
    looks_result = usd_bake.rename_materials_to_looks(
        filepath=filepath,
        logger=logger,
        start_point_context=start_point_context
    )
    logger.log_step("materials_to_looks", {
        **start_point_context,
        "result": looks_result
    })
```

### Testing

- [ ] Export with materials → verify `/Looks` exists (not `/Materials`)
- [ ] Verify material bindings reference `/Looks/...` paths
- [ ] Open in Omniverse → materials render correctly
- [ ] Export without materials → no error

---

## PHASE 2: REQ-EXP-028 - Full Animation Export

### Requirement

Enable animation export with a **global checkbox** that passes through to Blender's native USD exporter. Support all animation types Blender supports.

### Key Principle

**This is a pass-through implementation.** We expose Blender's native parameters and let Blender handle the export. We do NOT implement custom animation handling.

### Supported Animation Types (via Blender 5.0)

| Animation Type | USD Type | Auto-exported with `export_animation=True` |
|----------------|----------|---------------------------------------------|
| Transform (loc/rot/scale) | `xformOp` time-samples | Yes |
| Deforming meshes | Animated points | Yes |
| Armatures (skeletal) | UsdSkel | Requires `export_armatures=True` |
| Shape keys (morph) | USD BlendShapes | Requires `export_shapekeys=True` |
| Cameras/Lights | UsdGeomCamera/UsdLux | Yes |
| Visibility | `visibility` attr | Yes |

### Properties to Add (`props.py`)

Add to `USDME_StartPointPropertyGroup`:

```python
# Animation Export (REQ-EXP-028)
export_animation: BoolProperty(
    name="Export Animation",
    description="Export animation (baked per-frame transforms, armatures, shape keys)",
    default=False,
)

animation_frame_range: EnumProperty(
    name="Frame Range",
    description="Which frames to export",
    items=[
        ('SCENE', "Scene Range", "Use scene start/end frames"),
        ('CUSTOM', "Custom Range", "Specify custom frame range"),
    ],
    default='SCENE',
)

animation_frame_start: IntProperty(
    name="Start Frame",
    description="First frame to export",
    default=1,
    min=0,
)

animation_frame_end: IntProperty(
    name="End Frame",
    description="Last frame to export",
    default=250,
    min=1,
)

# Pass-through to Blender's exporter (use defaults)
export_armatures: BoolProperty(
    name="Export Armatures",
    description="Export armatures as UsdSkel skeletons",
    default=True,
)

export_shapekeys: BoolProperty(
    name="Export Shape Keys",
    description="Export shape keys as USD blend shapes",
    default=True,
)

only_deform_bones: BoolProperty(
    name="Only Deform Bones",
    description="Only export bones marked as deforming",
    default=False,
)
```

### UI Updates (`ui.py`)

Add animation section after the Y-up row:

```python
# Animation Export Section (REQ-EXP-028)
box_anim = box.box()
box_anim.label(text="Animation Export", icon="ACTION")

row_anim_enable = box_anim.row(align=True)
row_anim_enable.prop(start_point, "export_animation", text="Export Animation")

if start_point.export_animation:
    # Warning about normalization conflict
    warn_row = box_anim.row()
    warn_row.alert = True
    warn_row.scale_y = 0.8
    warn_row.label(text="Disables transform normalization (baked into geometry)", icon="INFO")
    
    # Frame range
    col_anim = box_anim.column(align=True)
    col_anim.prop(start_point, "animation_frame_range", text="Frame Range")
    
    if start_point.animation_frame_range == 'CUSTOM':
        row_frames = col_anim.row(align=True)
        row_frames.prop(start_point, "animation_frame_start", text="Start")
        row_frames.prop(start_point, "animation_frame_end", text="End")
    
    col_anim.separator()
    
    # Armature/Shape Key options
    col_anim.prop(start_point, "export_armatures", text="Armatures (UsdSkel)")
    if start_point.export_armatures:
        sub = col_anim.row()
        sub.prop(start_point, "only_deform_bones", text="Only Deform Bones")
    
    col_anim.prop(start_point, "export_shapekeys", text="Shape Keys (BlendShapes)")
```

**Also update the normalization section to be disabled when animation is on:**

```python
# Collection Normalize / Pivot section - DISABLE when animation is on
box_norm = box.box()
box_norm.enabled = not start_point.export_animation  # NEW: Disable when animation is on
box_norm.label(text="Collection Normalize / Pivot", icon="PIVOT_MEDIAN")
# ... rest of normalize UI ...
```

### Export Logic Updates (`ops_export.py`)

Around line 1174, update export_params:

```python
# Animation parameters (REQ-EXP-028)
export_params = {
    "filepath": filepath,
    "export_materials": True,
    "export_uvmaps": True,
    "export_normals": True,
    "export_animation": start_point.export_animation,  # CHANGED: was False
    "export_armatures": start_point.export_armatures if start_point.export_animation else True,
    "export_shapekeys": start_point.export_shapekeys if start_point.export_animation else True,
    "only_deform_bones": start_point.only_deform_bones if start_point.export_animation else False,
    "export_lights": False,
    "root_prim_path": f"/{sanitized_name}",
}
```

**Frame range handling** (Blender has no custom frame range params - must modify scene):

```python
# Handle custom frame range (before export call)
original_frame_start = None
original_frame_end = None

if start_point.export_animation and start_point.animation_frame_range == 'CUSTOM':
    original_frame_start = context.scene.frame_start
    original_frame_end = context.scene.frame_end
    context.scene.frame_start = start_point.animation_frame_start
    context.scene.frame_end = start_point.animation_frame_end

try:
    bpy.ops.wm.usd_export(**export_params)
finally:
    # Restore frame range
    if original_frame_start is not None:
        context.scene.frame_start = original_frame_start
        context.scene.frame_end = original_frame_end
```

### Post-Processing Updates (`usd_bake.py`)

Add `animation_mode` parameter to skip mesh baking:

```python
def bake_usd_geometry(
    filepath: str,
    scale_factor: float,
    y_is_up: bool,
    meters_per_unit: float,
    logger=None,
    start_point_context: Optional[Dict[str, Any]] = None,
    normalize_child_xforms: bool = False,
    animation_mode: bool = False,  # NEW: Skip mesh baking when True
) -> Dict[str, Any]:
    """..."""
    
    # ... setup code ...
    
    # v0.1.88: When animation_mode=True, skip mesh point baking
    # to preserve time-sampled xformOps
    if animation_mode:
        # Only set stage metadata, skip mesh baking
        UsdGeom.SetStageMetersPerUnit(stage, meters_per_unit)
        UsdGeom.SetStageUpAxis(
            stage, UsdGeom.Tokens.y if y_is_up else UsdGeom.Tokens.z
        )
        
        # Still apply default prim rotation for Y-up
        if default_prim and default_prim.IsValid() and y_is_up:
            xformable = UsdGeom.Xformable(default_prim)
            if xformable:
                # Only modify if no existing xformOps with timeSamples
                xform_ops = xformable.GetOrderedXformOps()
                has_time_samples = any(op.GetNumTimeSamples() > 0 for op in xform_ops)
                if not has_time_samples:
                    xformable.ClearXformOpOrder()
                    xformable.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0))
                    xformable.AddRotateXYZOp().Set(Gf.Vec3f(-90, 0, 0))
                    xformable.AddScaleOp().Set(Gf.Vec3f(1, 1, 1))
        
        stage.Save()
        result["success"] = True
        result["animation_mode"] = True
        return result
    
    # ... rest of existing mesh baking code (unchanged) ...
```

---

## PHASE 3: REQ-EXP-029 - Separate Animation Layer Export

### Requirement

Export animation to a **separate USD file** that can be composed with geometry using USD sublayers.

### Properties to Add (`props.py`)

```python
# Separate Animation Layer (REQ-EXP-029)
export_animation_separate_layer: BoolProperty(
    name="Export as Separate Layer",
    description="Export animation to a separate USD file for composition",
    default=False,
)

animation_layer_suffix: StringProperty(
    name="Animation Layer Suffix",
    description="Suffix for animation layer filename",
    default="_anim",
)

generate_composition_root: BoolProperty(
    name="Generate Composition Root",
    description="Create a USD file that combines geometry and animation layers",
    default=True,
)
```

### UI Updates

Add to animation section when `export_animation` is True:

```python
if start_point.export_animation:
    # ... existing animation UI ...
    
    col_anim.separator()
    col_anim.label(text="Layered Export (Advanced):", icon="OUTLINER_OB_GROUP_INSTANCE")
    col_anim.prop(start_point, "export_animation_separate_layer", text="Separate Animation Layer")
    
    if start_point.export_animation_separate_layer:
        col_anim.prop(start_point, "animation_layer_suffix", text="Suffix")
        col_anim.prop(start_point, "generate_composition_root", text="Generate Composition")
```

### Export Logic

When `export_animation_separate_layer=True`, perform TWO exports:

```python
if start_point.export_animation and start_point.export_animation_separate_layer:
    # Export 1: Geometry only (no animation)
    geometry_filepath = filepath
    geometry_params = {
        **export_params,
        "export_animation": False,
    }
    bpy.ops.wm.usd_export(**geometry_params)
    
    # Post-process geometry
    bake_usd_geometry(geometry_filepath, ...)
    rename_materials_to_looks(geometry_filepath, ...)
    
    # Export 2: Animation (full frame range)
    base, ext = os.path.splitext(filepath)
    anim_filepath = f"{base}{start_point.animation_layer_suffix}{ext}"
    anim_params = {
        **export_params,
        "filepath": anim_filepath,
        "export_animation": True,
    }
    bpy.ops.wm.usd_export(**anim_params)
    
    # Post-process: Convert 'def' to 'over' specifiers
    clean_animation_layer(anim_filepath)
    
    # Generate composition root if requested
    if start_point.generate_composition_root:
        comp_filepath = f"{base}_composed{ext}"
        generate_composition_file(comp_filepath, geometry_filepath, anim_filepath)
else:
    # Single export (existing behavior)
    bpy.ops.wm.usd_export(**export_params)
```

### New Functions for `usd_bake.py`

#### Function 1: Clean Animation Layer (REFINED - Based on Research)

**CRITICAL REFINEMENT**: Research revealed that simple `def→over` is insufficient. This function:
1. Converts `def→over` **selectively** (keeps `SkelAnimation` as `def`)
2. Strips non-animated properties (geometry, materials, primvars)
3. Removes material bindings (prevents lookdev override)

See `00_Discovery.md` section "Session: Animation Layer Separation Research" for full rationale.

```python
def clean_animation_layer(filepath: str, logger=None, start_point_context=None) -> Dict[str, Any]:
    """Clean animation layer: selective over + strip non-animated data.
    
    Based on combined research (NVIDIA, Pixar, second opinion analysis):
    - Convert def→over EXCEPT for SkelAnimation prims (they must stay def)
    - Strip geometry properties (points, topology, primvars) unless animated
    - Remove material:binding relationships
    - Keep only animation-relevant data (xformOps, timeSamples, skel data)
    
    Reference Links:
    - https://docs.nvidia.com/learn-openusd/latest/composition-basics/specifiers.html
    - https://openusd.org/docs/api/_usd_skel__schemas.html
    - https://openusd.org/release/tut_xforms.html
    """
    result = {
        "success": False,
        "prims_converted_to_over": 0,
        "skel_anims_kept_as_def": 0,
        "properties_removed": 0,
        "material_bindings_removed": 0,
    }
    
    try:
        from pxr import Usd, Sdf
    except ImportError:
        result["reason"] = "pxr_unavailable"
        return result
    
    stage = Usd.Stage.Open(filepath)
    if not stage:
        result["reason"] = "stage_open_failed"
        return result
    
    layer = stage.GetRootLayer()
    
    # Step 1: Identify SkelAnimation prims (must keep as def)
    skel_anim_paths = set()
    for prim in stage.Traverse():
        if prim.GetTypeName() == "SkelAnimation":
            skel_anim_paths.add(str(prim.GetPath()))
            result["skel_anims_kept_as_def"] += 1
    
    # Step 2: Selective def → over conversion
    def convert_selective(prim_spec):
        count = 0
        path_str = str(prim_spec.path)
        
        # Keep SkelAnimation as def (they define new animation data)
        if path_str not in skel_anim_paths:
            if prim_spec.specifier == Sdf.SpecifierDef:
                prim_spec.specifier = Sdf.SpecifierOver
                count += 1
        
        for child in prim_spec.nameChildren:
            count += convert_selective(child)
        return count
    
    for prim_spec in layer.rootPrims:
        result["prims_converted_to_over"] += convert_selective(prim_spec)
    
    # Step 3: Strip non-animated properties
    # Properties to always keep
    properties_to_keep = {
        "xformOpOrder",
        "visibility",
        "extent",
    }
    # Prefixes to keep (skel: includes skel:animationSource - critical for skeleton binding)
    prefixes_to_keep = ("xformOp:", "skel:")
    
    for prim in stage.Traverse():
        prim_spec = layer.GetPrimAtPath(prim.GetPath())
        if not prim_spec:
            continue
        
        # Skip SkelAnimation prims - keep all their data
        if str(prim.GetPath()) in skel_anim_paths:
            continue
        
        # Collect properties to remove
        props_to_remove = []
        for prop_spec in list(prim_spec.properties):
            prop_name = prop_spec.name
            
            # Keep xformOp and skel properties
            if any(prop_name.startswith(prefix) for prefix in prefixes_to_keep):
                continue
            
            # Keep allowed properties
            if prop_name in properties_to_keep:
                continue
            
            # Keep properties with timeSamples (animated)
            if hasattr(prop_spec, 'HasInfo') and prop_spec.HasInfo('timeSamples'):
                ts = prop_spec.GetInfo('timeSamples')
                if ts and len(ts) > 1:  # Has actual animation
                    continue
            
            # Remove everything else (geometry, materials, primvars)
            props_to_remove.append(prop_name)
        
        for prop_name in props_to_remove:
            if prop_name in prim_spec.properties:
                del prim_spec.properties[prop_name]
                result["properties_removed"] += 1
    
    # Step 4: Remove material:binding relationships
    for prim in stage.Traverse():
        prim_spec = layer.GetPrimAtPath(prim.GetPath())
        if prim_spec:
            for rel_name in list(prim_spec.relationships.keys()):
                if rel_name.startswith("material:"):
                    del prim_spec.relationships[rel_name]
                    result["material_bindings_removed"] += 1
    
    layer.Save()
    result["success"] = True
    
    if logger:
        logger.log_step("clean_animation_layer", {
            **(start_point_context or {}),
            "result": result,
        })
    
    return result


def generate_composition_file(
    comp_filepath: str,
    geometry_filepath: str,
    anim_filepath: str
) -> Dict[str, Any]:
    """Generate USD file that sublayers geometry and animation."""
    result = {"success": False}
    
    from pxr import Usd, Sdf
    import os
    
    stage = Usd.Stage.CreateNew(comp_filepath)
    root_layer = stage.GetRootLayer()
    
    # Add sublayers (animation first = stronger opinions)
    root_layer.subLayerPaths.append(os.path.basename(anim_filepath))
    root_layer.subLayerPaths.append(os.path.basename(geometry_filepath))
    
    stage.Save()
    result["success"] = True
    return result
```

---

## Testing Checklist

### Test Scene Creation (Blender 5.0)

**Simple Transform Animation Test:**
1. Open Blender, create new scene
2. Add default cube
3. Go to frame 1, press I → Location
4. Go to frame 24, move cube 5 units, press I → Location
5. Save as `test_transform_anim.blend`

**Armature/Skeletal Animation Test:**
1. Add → Armature → Single Bone
2. Add → Mesh → Cube
3. Select cube, then armature, Ctrl+P → Armature Deform
4. Pose mode on armature, keyframe bone rotation
5. Save as `test_armature_anim.blend`

**Shape Key Animation Test:**
1. Create cube
2. Object Data → Shape Keys → add Basis, add Key 1
3. Edit mode Key 1, move vertices
4. Keyframe shape key value from 0 to 1
5. Save as `test_shapekey_anim.blend`

### Test Matrix

| Test | REQ | Expected Result |
|------|-----|-----------------|
| Static export, no animation | - | Works as before |
| Animation enabled, play in usdview | 028 | Animation plays |
| Animation + custom frame range | 028 | Only specified frames exported |
| Animation + armature | 028 | UsdSkel skeleton animates |
| Animation + shape keys | 028 | BlendShapes morph |
| Animation + normalize disabled | 028 | UI greys out normalize options |
| Materials scope = /Looks | 023 | No /Materials, only /Looks |
| Separate anim layer | 029 | Two files: geo + anim |
| Composed file plays animation | 029 | Sublayered file animates |
| Animation layer has no geometry | 029 | Inspect: no `faceVertexCounts`, etc. |
| SkelAnimation kept as `def` | 029 | Armature test: check specifier |
| No material bindings in anim | 029 | Inspect: no `material:binding` |

### Clean Layer Verification Checklist (REQ-EXP-029)

After running `clean_animation_layer()`, verify the animation USD file:

| Check | How to Verify | Expected |
|-------|---------------|----------|
| Selective `def→over` | `usddump` or text inspect | Non-SkelAnimation prims are `over` |
| SkelAnimation as `def` | Find `def SkelAnimation` | Stays as `def` (not `over`) |
| No `material:binding` | Search for `material:binding` | None found |
| No topology data | Search `faceVertexCounts` | None found |
| No primvars | Search `primvars:` | None found (unless animated) |
| xformOps preserved | Search `xformOp:` | Present with timeSamples |
| skel: data preserved | Search `skel:` | Present for armature exports |

**Quick CLI check (requires pxr):**
```bash
# Check specifiers
usdcat -f usda MyAsset_anim.usd | grep -E "^(def|over) "

# Check for unwanted data
usdcat -f usda MyAsset_anim.usd | grep -E "(faceVertex|primvars:|material:binding)"
```

---

## Error Handling Best Practices

**Best practice for post-processing failures:**

1. **Fail gracefully** - warn but don't delete files that were successfully created
2. **Log the error** with context for debugging
3. **Return partial results** - if geometry exported but animation failed, keep geometry

```python
try:
    result = clean_animation_layer(anim_filepath)
    if not result["success"]:
        logger.log_warning(
            f"Animation layer post-process failed: {result.get('reason')}",
            context=start_point_context
        )
        # Files still exist, user can manually fix
except Exception as e:
    logger.log_warning(
        f"Animation layer post-process exception: {e}",
        context=start_point_context
    )
    # Don't delete the exported files
```

---

## Files to Modify Summary

| File | Changes |
|------|---------|
| `props.py` | Add 8 new properties (animation + separate layer) |
| `ui.py` | Add animation section, disable normalize when animation on |
| `ops_export.py` | Pass animation params, handle frame range, dual export |
| `usd_bake.py` | Add `animation_mode`, `rename_materials_to_looks()`, `clean_animation_layer()`, `generate_composition_file()` |
| `__init__.py` | Update version to 0.1.88 |

---

## Implementation Order

1. **REQ-EXP-023**: Materials → Looks (simplest, isolated)
   - Add `rename_materials_to_looks()` to `usd_bake.py`
   - Call after `bake_usd_geometry()` in `ops_export.py`
   - Test

2. **REQ-EXP-028**: Animation Export
   - Add properties to `props.py`
   - Add UI section to `ui.py` (with normalize conflict handling)
   - Update export params in `ops_export.py`
   - Add `animation_mode` to `bake_usd_geometry()`
   - Test with simple animation

3. **REQ-EXP-029**: Separate Animation Layer
   - Add properties to `props.py`
   - Add UI to `ui.py`
   - Implement dual-export in `ops_export.py`
   - Add `clean_animation_layer()` and `generate_composition_file()`
   - Test composition

---

## Context for Next Session

**Project**: Blender USD MultiExport Addon  
**Workspace**: `E:\SynologyDrive\9999_LocalRepo\Blender_USD_MultiExport`  
**Current Version**: v0.1.87  
**Target Version**: v0.1.88

**Key Code Locations**:
- Export params: `ops_export.py` line ~1174
- Post-process bake: `usd_bake.py` function `bake_usd_geometry()`
- Properties: `props.py` class `USDME_StartPointPropertyGroup`
- UI panels: `ui.py` class `USDME_PT_main_panel`

**Related Handoffs**:
- `99B_Handoff_20260206_Animation_Export_Feature.md` - Original animation research
- `99C_Handoff_20260206_REQ_ID_Duplicate_Fix.md` - REQ-EXP-025→030 renumbering

**Known Issues (deferred)**:
- REQ-EXP-030: Unit conversion bug (target unit ineffective when scene in mm)

---

**Handoff Created By**: Agent Session 06.02.2026  
**Ready for Implementation**: Yes  
**Start With**: REQ-EXP-023 (Materials → Looks)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 06.02.2026 | Initial consolidated handoff with REQ-EXP-023, 028, 029 |
| 1.1.0 | 06.02.2026 | **MAJOR**: Integrated second opinion research findings. Replaced `convert_to_over_opinions()` with refined `clean_animation_layer()`. Added: selective def→over (preserve SkelAnimation), property stripping, material binding removal. Added research reference section and clean layer verification checklist. See `00_Discovery.md` "Session: Animation Layer Separation Research" for full details. |
| 1.1.1 | 06.02.2026 | Added NVIDIA USDcode NIM validation. Confirmed: SkelAnimation stays `def`, all other prims (incl. Skeleton, SkelRoot, Mesh) become `over`. Added warning to preserve `skel:animationSource`. |
