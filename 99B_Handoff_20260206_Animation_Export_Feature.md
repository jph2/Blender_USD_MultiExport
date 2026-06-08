---
arys_schema_version: '1.2'
id: defd9db1-bf36-44ed-b9e2-0d4d2d884930
title: 'Handoff: Animation Export Feature Implementation'
type: PRACTICAL
status: active
trust_level: 2
visibility: internal
created: '2026-02-17T09:42:16Z'
last_modified: '2026-02-17T09:42:16Z'
---

# Handoff: Animation Export Feature Implementation

**Version**: 1.2.0 | **Date**: 06.02.2026 | **Time**: 17:30 | **GlobalID**: 20260206_1730_BlenderUSDME_AnimationExport_Handoff

**Tag block:**
#workflow_automation #export #usd_core #extension_development #blender #openusd #conversion #layers #composition #framework_integration #ai_coding_agents #analysis #case_study #deterministic_workflows

---

## 📋 Executive Summary

This handoff covers the implementation of **animation export support** for the Blender USD MultiExport addon. Two new requirements have been researched and documented, ready for implementation.

| Requirement | Priority | Status | Description |
|-------------|----------|--------|-------------|
| **REQ-EXP-028** | Medium | ✅ Ready for Implementation | Full Animation Export - All Blender-supported types |
| **REQ-EXP-029** | Low | ✅ Ready for Implementation | Separate Animation Layer Export |

---

## 🔬 Research Complete: Blender 5.0 Native USD Animation Support

**Key Finding**: Blender's native USD exporter supports ALL the following animation types. The addon implementation is a **pass-through** - we expose the parameters and let Blender handle the export.

### Supported Animation Types (Blender 5.0)

| Animation Type | USD Type | Parameter | Notes |
|----------------|----------|-----------|-------|
| **Transform (loc/rot/scale)** | `xformOp` time-samples | `export_animation=True` | Baked per-frame |
| **Deforming meshes** | Animated points | `export_animation=True` | Cloth, soft-body |
| **Topology-changing meshes** | Animated topology | `export_animation=True` | Fluid sims |
| **Armatures (skeletal)** | UsdSkel | `export_armatures=True` | Blender 4.0+ |
| **Shape keys (morph)** | USD BlendShapes | `export_shapekeys=True` | Relative only |
| **Animated volumes** | VDB time-samples | `export_animation=True` | OpenVDB |
| **Cameras** | UsdGeomCamera | `export_animation=True` | FOV, transform |
| **Lights** | UsdLux | `export_animation=True` | Intensity, transform |
| **Visibility** | `visibility` attr | `export_animation=True` | Auto when animated |

### Blender Native Limitations

- **No animation curves** - USD uses baked per-frame samples, not bezier curves
- **Invisible objects not exported**
- **No custom frame range parameters** - uses `scene.frame_start` / `scene.frame_end`
- **Absolute shape keys not supported** (relative only)
- **Bendy bones not supported**

---

## 🎯 Implementation Goals

### Goal 1: REQ-EXP-028 - Full Animation Export

Enable users to export **all animation types supported by Blender's native USD exporter** - not just transforms, but also armatures (UsdSkel), shape keys (BlendShapes), deforming meshes, volumes, cameras, and lights.

**Current State**: Animation is disabled (`export_animation=False` hardcoded at `ops_export.py` line 1174).

**Target State**: Users can enable animation export per start point, with:
- All Blender-supported animation types
- Optional custom frame range
- Armature/shape key controls

### Goal 2: REQ-EXP-029 - Separate Animation Layer Export

Enable users to export animation to a **separate USD file** that can be composed with geometry using USD sublayers.

**Current State**: Not implemented.

**Target State**: Users can choose to export geometry and animation as separate files, with optional composition root generation.

---

## 📁 Key Files to Modify

| File | Purpose | Changes Needed |
|------|---------|----------------|
| `blender_usd_multiexport_addon/props.py` | Property definitions | Add animation properties to StartPointProperties |
| `blender_usd_multiexport_addon/ui.py` | UI panels | Add animation export UI section |
| `blender_usd_multiexport_addon/ops_export.py` | Export logic | Pass animation params, implement dual-export |
| `blender_usd_multiexport_addon/usd_bake.py` | Post-processing | Handle time-sampled data preservation |

---

## 📝 Implementation Tasks

### Phase 1: Basic Animation Export (REQ-EXP-028)

#### Task 1.1: Add Animation Properties (`props.py`)

Add to `StartPointProperties` class:

```python
# Animation Export Properties
export_animation: bpy.props.BoolProperty(
    name="Export Animation",
    description="Export animation (baked per-frame) - includes transforms, armatures, shape keys",
    default=False,
)

animation_frame_range: bpy.props.EnumProperty(
    name="Frame Range",
    description="Which frames to export",
    items=[
        ('SCENE', "Scene Range", "Use scene start/end frames"),
        ('CUSTOM', "Custom Range", "Specify custom frame range"),
    ],
    default='SCENE',
)

animation_frame_start: bpy.props.IntProperty(
    name="Start Frame",
    description="First frame to export",
    default=1,
    min=0,
)

animation_frame_end: bpy.props.IntProperty(
    name="End Frame",
    description="Last frame to export",
    default=250,
    min=1,
)

# Additional animation options (pass-through to Blender's exporter)
export_armatures: bpy.props.BoolProperty(
    name="Export Armatures",
    description="Export armatures as UsdSkel skeletons",
    default=True,
)

export_shapekeys: bpy.props.BoolProperty(
    name="Export Shape Keys",
    description="Export shape keys as USD blend shapes",
    default=True,
)

only_deform_bones: bpy.props.BoolProperty(
    name="Only Deform Bones",
    description="Only export bones marked as deforming",
    default=False,
)
```

#### Task 1.2: Add Animation UI Section (`ui.py`)

Add to the start point settings panel (after export options):

```python
# Animation Export Section
box = layout.box()
row = box.row()
row.prop(start_point, "export_animation", text="Export Animation")

if start_point.export_animation:
    col = box.column(align=True)
    
    # Frame range options
    col.prop(start_point, "animation_frame_range", text="Frame Range")
    if start_point.animation_frame_range == 'CUSTOM':
        row = col.row(align=True)
        row.prop(start_point, "animation_frame_start", text="Start")
        row.prop(start_point, "animation_frame_end", text="End")
    
    col.separator()
    
    # Armature/Shape Key options
    col.prop(start_point, "export_armatures", text="Export Armatures (UsdSkel)")
    if start_point.export_armatures:
        sub = col.row()
        sub.enabled = start_point.export_armatures
        sub.prop(start_point, "only_deform_bones", text="Only Deform Bones")
    
    col.prop(start_point, "export_shapekeys", text="Export Shape Keys")
```

#### Task 1.3: Modify Export Logic (`ops_export.py`)

Around line 1174, change from hardcoded to dynamic with all animation parameters:

```python
# Current (hardcoded):
"export_animation": False,

# New (dynamic with all animation parameters):
"export_animation": start_point.export_animation,
"export_armatures": start_point.export_armatures if start_point.export_animation else True,
"export_shapekeys": start_point.export_shapekeys if start_point.export_animation else True,
"only_deform_bones": start_point.only_deform_bones if start_point.export_animation else False,
```

**Frame Range Handling** - Blender's USD exporter uses `scene.frame_start`/`scene.frame_end` directly (no custom parameters). We must temporarily modify scene settings:

```python
# Handle animation frame range
original_frame_start = None
original_frame_end = None

if start_point.export_animation and start_point.animation_frame_range == 'CUSTOM':
    # Store original
    original_frame_start = context.scene.frame_start
    original_frame_end = context.scene.frame_end
    # Set custom range
    context.scene.frame_start = start_point.animation_frame_start
    context.scene.frame_end = start_point.animation_frame_end
    logger.log_step("frame_range_override", {
        **start_point_context,
        "original": (original_frame_start, original_frame_end),
        "custom": (start_point.animation_frame_start, start_point.animation_frame_end),
    })

try:
    # ... export code ...
finally:
    # Restore original frame range
    if original_frame_start is not None:
        context.scene.frame_start = original_frame_start
        context.scene.frame_end = original_frame_end
        logger.log_step("frame_range_restored", start_point_context)
```

#### Task 1.4: Handle Time-Sampled Data in Post-Process (`usd_bake.py`)

**Critical**: When animation is enabled, the post-process bake step must NOT bake transforms into mesh points, as this would destroy time-sampled animation.

Current behavior (line ~98-99):
```python
if scale_factor != 1.0:
    local_bake_matrix.SetScale(Gf.Vec3d(scale_factor, scale_factor, scale_factor))
```

This applies scale to mesh points. With animation, we need to either:
1. Skip mesh point baking entirely when animation is present
2. Only bake scale into mesh points at frame 0, preserving time-samples

**Recommended approach**: Add `animation_mode` parameter to `bake_usd_geometry()`:

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
```

When `animation_mode=True`:
- Set stage metadata (`metersPerUnit`, `upAxis`)
- Set default prim rotation for Y-up
- Do NOT bake transforms into mesh points
- Preserve all `xformOp.timeSamples`

---

### Phase 2: Separate Animation Layer Export (REQ-EXP-029)

#### Task 2.1: Add Separate Layer Properties (`props.py`)

```python
export_animation_separate_layer: bpy.props.BoolProperty(
    name="Export as Separate Layer",
    description="Export animation to a separate USD file for composition",
    default=False,
)

animation_layer_suffix: bpy.props.StringProperty(
    name="Animation Layer Suffix",
    description="Suffix for animation layer filename",
    default="_anim",
)

generate_composition_root: bpy.props.BoolProperty(
    name="Generate Composition Root",
    description="Create a USD file that combines geometry and animation layers",
    default=True,
)
```

#### Task 2.2: Update UI for Separate Layer

```python
if start_point.export_animation:
    # ... frame range UI ...
    
    col.separator()
    col.prop(start_point, "export_animation_separate_layer", text="Separate Animation Layer")
    
    if start_point.export_animation_separate_layer:
        col.prop(start_point, "animation_layer_suffix", text="Suffix")
        col.prop(start_point, "generate_composition_root", text="Generate Composition")
```

#### Task 2.3: Implement Dual Export (`ops_export.py`)

When `export_animation_separate_layer=True`, perform TWO exports:

```python
if start_point.export_animation and start_point.export_animation_separate_layer:
    # Export 1: Geometry only (current frame)
    geometry_filepath = filepath  # e.g., "MyAsset.usd"
    geometry_params = {
        **export_params,
        "export_animation": False,
    }
    bpy.ops.wm.usd_export(**geometry_params)
    
    # Export 2: Animation (full frame range)
    base, ext = os.path.splitext(filepath)
    anim_filepath = f"{base}{start_point.animation_layer_suffix}{ext}"
    anim_params = {
        **export_params,
        "filepath": anim_filepath,
        "export_animation": True,
    }
    bpy.ops.wm.usd_export(**anim_params)
    
    # Post-process animation file to use 'over' specifiers
    convert_to_over_opinions(anim_filepath)
    
    # Generate composition root if requested
    if start_point.generate_composition_root:
        comp_filepath = f"{base}_composed{ext}"
        generate_composition_file(comp_filepath, geometry_filepath, anim_filepath)
```

#### Task 2.4: Convert to 'over' Opinions (New Function)

Create function to post-process animation file:

```python
def convert_to_over_opinions(filepath: str) -> bool:
    """Convert 'def' prims to 'over' in animation layer."""
    from pxr import Usd, Sdf
    
    stage = Usd.Stage.Open(filepath)
    if not stage:
        return False
    
    # Get the layer for editing
    layer = stage.GetRootLayer()
    
    # Traverse and convert 'def' to 'over'
    for prim_spec in layer.rootPrims:
        _convert_prim_to_over(prim_spec)
    
    layer.Save()
    return True

def _convert_prim_to_over(prim_spec):
    """Recursively convert prim specifier from 'def' to 'over'."""
    if prim_spec.specifier == Sdf.SpecifierDef:
        prim_spec.specifier = Sdf.SpecifierOver
    
    for child in prim_spec.nameChildren:
        _convert_prim_to_over(child)
```

#### Task 2.5: Generate Composition Root (New Function)

```python
def generate_composition_file(
    comp_filepath: str,
    geometry_filepath: str,
    anim_filepath: str
) -> bool:
    """Generate USD file that sublayers geometry and animation."""
    from pxr import Usd, Sdf
    
    # Create new stage
    stage = Usd.Stage.CreateNew(comp_filepath)
    
    # Get root layer
    root_layer = stage.GetRootLayer()
    
    # Add sublayers (animation first = stronger)
    root_layer.subLayerPaths.append(os.path.basename(anim_filepath))
    root_layer.subLayerPaths.append(os.path.basename(geometry_filepath))
    
    stage.Save()
    return True
```

---

## 🧪 Testing Checklist

### Basic Animation Export (REQ-EXP-028)

**Transform Animation**:
- [ ] Create cube with location keyframes (frame 1→24)
- [ ] Enable "Export Animation" on start point
- [ ] Export to USD - verify `xformOp` has time-samples
- [ ] Open in usdview - verify animation plays
- [ ] Open in Omniverse - verify animation plays
- [ ] Test with rotation and scale keyframes
- [ ] Test with custom frame range (verify scene range is restored)

**Armature Animation (UsdSkel)**:
- [ ] Create rigged character with bone animation
- [ ] Enable "Export Animation" + "Export Armatures"
- [ ] Export to USD - verify UsdSkel structure exists
- [ ] Open in usdview/Omniverse - verify skeletal animation plays
- [ ] Test "Only Deform Bones" option

**Shape Keys (BlendShapes)**:
- [ ] Create mesh with animated shape keys
- [ ] Enable "Export Animation" + "Export Shape Keys"
- [ ] Export to USD - verify BlendShapes exist
- [ ] Open in usdview/Omniverse - verify morph animation plays

**Deforming Meshes**:
- [ ] Create cloth simulation or soft-body
- [ ] Enable "Export Animation"
- [ ] Export to USD - verify animated mesh points
- [ ] Verify animation plays in viewers

**Static Export**:
- [ ] Verify static export still works when animation disabled

### Separate Animation Layer (REQ-EXP-029)

- [ ] Enable "Export as Separate Layer"
- [ ] Verify two files generated: geometry + animation
- [ ] Verify animation file uses 'over' specifiers
- [ ] Verify composition root sublayers both files
- [ ] Open composed file in usdview - animation plays
- [ ] Open composed file in Omniverse - animation plays
- [ ] Test editing geometry file independently
- [ ] Test swapping different animation files

---

## ⚠️ Known Challenges

### CRITICAL: Animation vs. Transform Normalization Conflict

**Animation and transform normalization are MUTUALLY EXCLUSIVE.**

The current `usd_bake.py` bakes transforms into mesh point data for normalization. When animation is enabled, USD stores `xformOp` time-samples. Baking transforms into mesh points destroys these time-samples.

**Solution**: When `export_animation = True`:
- Disable/grey-out: `normalize_position`, `normalize_scale`, `normalize_rotation`
- Skip mesh point baking in `usd_bake.py` (only set stage metadata)
- The UI must enforce this either/or constraint

**See `99D_Handoff_20260206_Animation_And_Looks_Implementation.md` for full implementation details.**

---

### Other Challenges

1. **Post-Process Bake Conflict**: Current `usd_bake.py` bakes transforms into mesh points. With animation, we must preserve time-sampled xformOps. Need to add `animation_mode` flag to skip mesh baking.

2. **Frame Range Handling**: Blender's USD exporter has NO custom frame range parameters - it uses `scene.frame_start`/`scene.frame_end` directly. For custom ranges, we must temporarily modify scene settings and restore in a `finally` block.

3. **Material Bindings in Animation Layer**: The animation layer should NOT include materials or geometry data - only transform overrides. Converting `def` → `over` should be sufficient since `over` prims don't define new geometry.

4. **Prim Path Matching**: Animation layer prim paths MUST match geometry layer paths exactly for composition to work.

5. **UsdSkel Compatibility**: Armature export uses UsdSkel schema. Ensure post-processing doesn't break skeleton bindings or joint hierarchies.

---

## 📚 Reference Documents

| Document | Location | Content |
|----------|----------|---------|
| Discovery | `00_Discovery.md` | "Session: Animation Export Research" - Full research notes |
| Requirements | `02_Detailed_Requirements.md` | REQ-EXP-028, REQ-EXP-029 with acceptance criteria |
| Implementation Plan | `04_Implementation_Plan.md` | "Animation Export Support" section with task breakdown |
| Blender USD Docs | [Blender Manual](https://docs.blender.org/manual/en/latest/files/import_export/usd.html) | Animation export parameters |
| USD Sublayers | [NVIDIA Learn OpenUSD](https://docs.nvidia.com/learn-openusd/latest/creating-composition-arcs/sublayers/what-are-sublayers.html) | Composition arc documentation |

---

## 🚀 Recommended Implementation Order

1. **Start with REQ-EXP-028 Phase 1** (basic animation export)
   - Fastest path to working animation
   - Lower complexity than separate layers
   
2. **Test thoroughly** before proceeding to Phase 2

3. **Implement REQ-EXP-029 Phase 2** (separate layers)
   - Builds on Phase 1 foundation
   - More complex post-processing

---

## 📞 Context for Next Agent

**Project**: Blender USD MultiExport Addon  
**Workspace**: `E:\SynologyDrive\9999_LocalRepo\Blender_USD_MultiExport`  
**Current Version**: v0.1.87  
**Target Version**: v0.1.88 (with animation support)

**Key Code Locations**:
- Export params: `ops_export.py` line ~1174 (`export_animation: False`)
- Post-process bake: `usd_bake.py` function `bake_usd_geometry()`
- Start point properties: `props.py` class `StartPointProperties`
- UI panels: `ui.py`

**Other Open Issues** (can be addressed separately):
- REQ-EXP-030: Unit conversion bug (target unit ineffective when scene in mm)

**Note**: REQ-EXP-023 (Materials → Looks) is now FIRST in implementation order. See consolidated handoff.

---

---

## 📝 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 06.02.2026 02:30 | Initial handoff - basic research |
| 1.1.0 | 06.02.2026 14:00 | Expanded scope based on Blender 5.0 research: added armature (UsdSkel), shape keys (BlendShapes), deforming meshes, volumes, cameras, lights support |
| 1.2.0 | 06.02.2026 17:30 | Added critical animation vs normalization conflict; referenced consolidated handoff |

---

## 🔗 Superseded By

**This handoff has been consolidated into:**

`99D_Handoff_20260206_Animation_And_Looks_Implementation.md`

The consolidated handoff includes:
- REQ-EXP-023 (Materials → Looks) - **Do first**
- REQ-EXP-028 (Animation Export) - This requirement
- REQ-EXP-029 (Separate Animation Layer)
- Animation vs. normalization conflict resolution
- Implementation order and complete code examples

---

**Handoff Created By**: Agent Session 06.02.2026  
**Ready for Implementation**: ✅ Yes (see consolidated handoff)  
**Research Status**: ✅ Complete - All Blender-supported animation types documented
