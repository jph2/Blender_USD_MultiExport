# Blender USD Multi Export - Feature Roadmap

**Date Created**: 2025-12-28  
**Version**: 1.0.0  
**Status**: Initial Evaluation - For Planning & Prioritization  
**Current MVP**: v0.1.3 (Complete)  
**Last Updated**: 03.02.2026 23:27  
**Target Platform**: Blender 5.0+

---

## 📋 Executive Summary

This roadmap defines the requirements and implementation plan for expanding the Blender USD Multi Export add-on with comprehensive export options. The roadmap is based on:

- **Current MVP State** (v0.1.3): Basic endpoint-based export with minimal options
- **NVIDIA Best Practices**: Patterns from official Omniverse Blender add-ons
- **Blender USD Export Options**: All available parameters from Blender 5.0 USD exporter
- **User Requirements**: Export functionality visible in Blender USD export dialog

**Scope**: This roadmap focuses on **export functionality only**. Nucleus connectivity and related features are explicitly excluded.

**System Architecture: Push vs Pull Workflows**

**MVP Architecture: One-Way Push Model**

The MVP focuses on a **one-way push model** for ComfyUI integration:

**Push Phase (Blender Side)**:
- **Blender** exports USD files to predefined destinations via export endpoints
- Export happens independently in Blender (user-initiated or scripted)
- USD files are written to specified file paths
- **No ComfyUI involvement** in the export process

**Pull Phase (ComfyUI Side)**:
- **ComfyUI** reads the export path from endpoint definitions stored in .blend file
- ComfyUI nodes (e.g., BlenderToUSD) load pre-generated USD files from specified locations
- **Passive file loading** - ComfyUI does not trigger Blender exports
- USD files are consumed downstream in ComfyUI workflows

**Key Clarification**:
- ❌ **NOT MVP**: Bidirectional execution (ComfyUI driving Blender exports)
- ✅ **MVP**: One-way push (Blender exports → ComfyUI reads paths → ComfyUI loads files)
- 🔮 **Future**: Bidirectional execution could be added as enhancement

---

## 🎯 Roadmap Overview

### Current State (v0.1.3 MVP)
- ✅ Basic endpoint-based export (Collection/Object)
- ✅ Minimal export options (materials, UVs, normals - hardcoded)
- ✅ Subdivision export (NVIDIA pattern with `single_user=True`)
- ✅ Origin metadata tracking
- ✅ Light exclusion (always `export_lights=False`)

### Target State (v0.2.0+)
- ✅ Per-endpoint export settings
- ✅ Comprehensive export options matching Blender's native USD exporter
- ✅ Export presets for common workflows
- ✅ Advanced geometry, material, and animation options
- ✅ Rigging and particle export support

---

## 📊 Feature Categories & Priority

### Priority 1: Core Export Options (v0.2.0)
**Goal**: Enable per-endpoint control over essential export parameters

1. **General Export Settings**
2. **Stage Configuration**
3. **Export Type Selection**
4. **Basic Geometry Options**

### Priority 2: Advanced Geometry & Materials (v0.3.0)
**Goal**: Full control over geometry processing and material export

1. **Advanced Geometry Options**
2. **Material Export Options**
3. **Texture Export Settings**

### Priority 3: Animation & Rigging (v0.4.0)
**Goal**: Support for animated exports and rigging workflows

1. **Animation Export**
2. **Rigging Support**
3. **Particles & Instancing**

### Priority 4: Workflow Enhancements (v0.5.0+)
**Goal**: Productivity features and advanced workflows

1. **Export Presets**
2. **Batch Operations**
3. **Validation & Pre-flight Checks**

---

## 🔧 Detailed Feature Requirements

## 1. General Export Settings

### 1.1 Forward Axis & Up Axis
**Priority**: High (v0.2.0)  
**Category**: General

**Requirements**:
- Per-endpoint selection of Forward Axis (X, Y, Z, -X, -Y, -Z)
- Per-endpoint selection of Up Axis (X, Y, Z, -X, -Y, -Z)
- Default: Y Forward, Z Up (Blender standard)
- Validation: Forward and Up axes must be different

**Implementation**:
- Add `forward_axis` EnumProperty to `USDME_Endpoint` (props.py)
- Add `up_axis` EnumProperty to `USDME_Endpoint` (props.py)
- Add UI dropdowns in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `forward_axis` and `up_axis` parameters
- Validate axis combination in pre-flight checks

**Blender API**:
```python
export_params = {
    "forward_axis": "Y",  # X, Y, Z, -X, -Y, -Z
    "up_axis": "Z",       # X, Y, Z, -X, -Y, -Z
}
```

**Dependencies**: None  
**Estimated Effort**: 2-3 hours

---

### 1.2 Selection Only / Visible Only
**Priority**: High (v0.2.0)  
**Category**: General

**Requirements**:
- Per-endpoint toggle: Export only selected objects (within endpoint)
- Per-endpoint toggle: Export only visible objects (within endpoint)
- Default: Visible Only = True, Selection Only = False
- Note: Endpoint isolation already handles this, but user control is valuable

**Implementation**:
- Add `selection_only` BoolProperty to `USDME_Endpoint` (props.py)
- Add `visible_only` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkboxes in endpoint settings panel (ui.py)
- Filter objects in `ScopedIsolation` based on these flags
- Pass to `bpy.ops.wm.usd_export()` as `selected_objects_only` and `visible_objects_only`

**Blender API**:
```python
export_params = {
    "selected_objects_only": False,
    "visible_objects_only": True,
}
```

**Dependencies**: State manager enhancement  
**Estimated Effort**: 2-3 hours

---

### 1.3 Convert Orientation
**Priority**: Medium (v0.2.0)  
**Category**: General

**Requirements**:
- Per-endpoint toggle: Convert object orientations during export
- Default: True (recommended for USD compatibility)
- Applies coordinate system transformations

**Implementation**:
- Add `convert_orientation` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `convert_orientation`

**Blender API**:
```python
export_params = {
    "convert_orientation": True,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

### 1.4 External Items Options
**Priority**: Medium (v0.2.0)  
**Category**: General

**Requirements**:
- **Create ARKit Asset**: Per-endpoint toggle for ARKit-compatible USDZ export
- **Relative Paths**: Per-endpoint toggle for relative vs absolute paths (default: True)
- **Export As Overs**: Per-endpoint toggle for USD Over composition
- **Merge Transform and Shape**: Per-endpoint toggle to merge transform and shape prims (default: True)
- **Xform Ops**: Per-endpoint selection of transform operation order (Scale, Rotate, Translate)

**Implementation**:
- Add BoolProperty for each option to `USDME_Endpoint` (props.py)
- Add EnumProperty for Xform Ops order (props.py)
- Add UI controls in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` with appropriate parameter names

**Blender API**:
```python
export_params = {
    "create_arkit_asset": False,
    "relative_paths": True,
    "export_as_overs": False,
    "merge_transform_and_shape": True,
    "xform_ops": "Srt",  # Scale, Rotate, Translate
}
```

**Dependencies**: None  
**Estimated Effort**: 2-3 hours

---

### 1.5 Unit System Control
**Priority**: High (v0.2.0)  
**Category**: General  
**Reference**: REQ-EXP-012

**Requirements**:
- Per-endpoint unit system selection:
  - **Use Scene Units** (default): Export using Blender scene's current unit system
  - **Force Centimeters**: Convert all measurements to centimeters regardless of scene units
  - **Force Meters**: Convert all measurements to meters regardless of scene units
- Unit conversion applies to object transforms, geometry dimensions, light intensity, camera settings
- Global default unit system option in addon preferences (optional)
- Preset-based unit selection (e.g., "Omniverse" preset uses centimeters, "VFX Pipeline" uses meters)

**Implementation**:
- Add `unit_system` EnumProperty to `USDME_Endpoint` (props.py) with options: `SCENE_UNITS`, `FORCE_CENTIMETERS`, `FORCE_METERS`
- Add dropdown in endpoint settings panel (ui.py)
- For scene units: Query `bpy.context.scene.unit_settings.system` and `bpy.context.scene.unit_settings.scale_length`
- For forced centimeters: Pass `convert_to_centimeters=True` to `bpy.ops.wm.usd_export()`
- For forced meters: May require post-processing or scale factor application (verify Blender API support)
- Integration with export presets (v0.5.0+) for preset-based unit selection

**Blender API**:
```python
export_params = {
    "convert_to_centimeters": True,  # When unit_system == FORCE_CENTIMETERS
    # Note: Blender may not have direct "force meters" option
    # May require post-processing or scale factor application
}
```

**Use Cases**:
- **Omniverse Workflows**: Typically require centimeters (FORCE_CENTIMETERS)
- **VFX Pipelines**: Often use meters (FORCE_METERS)
- **General Use**: Use scene units for flexibility (SCENE_UNITS)
- **Preset-Based**: Apply unit system based on selected export preset

**Dependencies**: None  
**Estimated Effort**: 2-3 hours

---

## 2. Stage Configuration

### 2.1 Default Prim Path
**Priority**: High (v0.2.0)  
**Category**: Stage

**Requirements**:
- Per-endpoint specification of default prim path (e.g., `/root`, `/World`)
- Default: `/root` (current implementation uses sanitized endpoint name)
- Validation: Must be valid USD prim path (start with `/`, valid characters)
- Used as root prim path for exported USD stage

**Implementation**:
- Add `default_prim_path` StringProperty to `USDME_Endpoint` (props.py)
- Add text input in endpoint settings panel (ui.py)
- Validate prim path format in pre-flight checks
- Pass to `bpy.ops.wm.usd_export()` as `default_prim_path` and `root_prim_path`

**Blender API**:
```python
export_params = {
    "default_prim_path": "/root",
    "root_prim_path": "/root",
}
```

**Dependencies**: Path validation utility  
**Estimated Effort**: 2 hours

---

### 2.2 Material Prim Path
**Priority**: Medium (v0.2.0)  
**Category**: Stage

**Requirements**:
- Per-endpoint specification of material prim path (e.g., `/root/materials`, `/World/materials`)
- Default: `/root/materials` (or based on default prim path)
- Used to organize material prims in exported USD

**Implementation**:
- Add `material_prim_path` StringProperty to `USDME_Endpoint` (props.py)
- Add text input in endpoint settings panel (ui.py)
- Auto-suggest based on default prim path (e.g., `{default_prim_path}/materials`)
- Pass to `bpy.ops.wm.usd_export()` as `material_prim_path`

**Blender API**:
```python
export_params = {
    "material_prim_path": "/root/materials",
}
```

**Dependencies**: Default prim path (2.1)  
**Estimated Effort**: 1-2 hours

---

### 2.3 Default Prim Kind
**Priority**: Low (v0.3.0)  
**Category**: Stage

**Requirements**:
- Per-endpoint selection of default prim kind (None, component, assembly, group, subcomponent)
- Default: None
- Used for USD kind metadata on root prim

**Implementation**:
- Add `default_prim_kind` EnumProperty to `USDME_Endpoint` (props.py)
- Add dropdown in endpoint settings panel (ui.py)
- Apply kind metadata to root prim after export (post-processing)

**Blender API**:
```python
# Note: Blender's USD exporter may not support this directly
# May require post-processing with USD Python API
default_prim_kind = "component"  # None, component, assembly, group, subcomponent
```

**Dependencies**: USD Python API for post-processing  
**Estimated Effort**: 3-4 hours (requires USD API integration)

---

## 3. Export Type Selection

### 3.1 Export Types Toggle
**Priority**: High (v0.2.0)  
**Category**: Export Types

**Requirements**:
- Per-endpoint toggles for each export type:
  - **Transforms**: Export object transforms (default: True)
  - **Meshes**: Export mesh geometry (default: True)
  - **Materials**: Export materials (default: True)
  - **Lights**: Export lights (default: False - current behavior)
  - **Cameras**: Export cameras (default: False)
  - **Curves**: Export curve objects (default: False)

**Implementation**:
- Add BoolProperty for each export type to `USDME_Endpoint` (props.py)
- Add checkboxes in endpoint settings panel (ui.py)
- Filter objects in `ScopedIsolation` based on type flags
- Pass to `bpy.ops.wm.usd_export()` with appropriate parameters

**Blender API**:
```python
export_params = {
    "export_transforms": True,
    "export_meshes": True,
    "export_materials": True,
    "export_lights": False,
    "export_cameras": False,
    "export_curves": False,
}
```

**Dependencies**: State manager enhancement  
**Estimated Effort**: 3-4 hours

---

## 4. Geometry Options

### 4.1 Subdivision Scheme
**Priority**: Medium (v0.2.0)  
**Category**: Geometry

**Requirements**:
- Per-endpoint selection of subdivision scheme (None, Catmull-Clark, Loop, Bilinear, Best Match)
- Default: Best Match (current: baked via modifier application)
- **Note**: Current implementation applies subdivision modifiers before export. This option controls USD subdivision prim export (if Blender supports it).

**Implementation**:
- Add `subdivision_scheme` EnumProperty to `USDME_Endpoint` (props.py)
- Add dropdown in endpoint settings panel (ui.py)
- **Current behavior**: Subdivision is baked via modifier application (NVIDIA pattern)
- **Future enhancement**: Support USD subdivision prims if Blender 5.0+ supports it
- Pass to `bpy.ops.wm.usd_export()` as `subdivision_scheme` (if supported)

**Blender API**:
```python
export_params = {
    "subdivision_scheme": "BEST_MATCH",  # NONE, CATMULL_CLARK, LOOP, BILINEAR, BEST_MATCH
}
```

**Dependencies**: Verify Blender 5.0 USD exporter subdivision support  
**Estimated Effort**: 2-3 hours (research + implementation)

---

### 4.2 Color Attributes
**Priority**: Medium (v0.2.0)  
**Category**: Geometry

**Requirements**:
- Per-endpoint toggle: Export vertex color attributes
- Default: True
- Exports Blender color attributes as USD color primvars

**Implementation**:
- Add `export_color_attributes` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `export_color_attributes`

**Blender API**:
```python
export_params = {
    "export_color_attributes": True,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

### 4.3 Mesh Attributes
**Priority**: Medium (v0.2.0)  
**Category**: Geometry

**Requirements**:
- Per-endpoint toggle: Export custom mesh attributes
- Default: True
- Exports Blender custom attributes as USD primvars

**Implementation**:
- Add `export_mesh_attributes` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `export_mesh_attributes`

**Blender API**:
```python
export_params = {
    "export_mesh_attributes": True,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

### 4.4 Normals Export
**Priority**: Medium (v0.2.0)  
**Category**: Geometry

**Requirements**:
- Per-endpoint toggle: Export vertex normals
- Default: True (current implementation)
- Exports Blender normals as USD normal primvars

**Implementation**:
- Add `export_normals` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `export_normals`
- **Note**: Currently hardcoded to True in ops_export.py

**Blender API**:
```python
export_params = {
    "export_normals": True,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

### 4.5 UV Maps Export
**Priority**: High (v0.2.0)  
**Category**: Geometry

**Requirements**:
- Per-endpoint toggle: Export UV maps
- Default: True (current implementation)
- Exports Blender UV maps as USD UV primvars

**Implementation**:
- Add `export_uvmaps` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `export_uvmaps`
- **Note**: Currently hardcoded to True in ops_export.py

**Blender API**:
```python
export_params = {
    "export_uvmaps": True,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

### 4.6 Convert UV to ST
**Priority**: Low (v0.3.0)  
**Category**: Geometry

**Requirements**:
- Per-endpoint toggle: Convert UV coordinates to ST (texture coordinates)
- Default: True
- USD convention uses ST instead of UV for texture coordinates

**Implementation**:
- Add `convert_uv_to_st` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `convert_uv_to_st`

**Blender API**:
```python
export_params = {
    "convert_uv_to_st": True,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

### 4.7 Triangulate Meshes
**Priority**: Medium (v0.2.0)  
**Category**: Geometry

**Requirements**:
- Per-endpoint toggle: Triangulate meshes before export
- Default: False
- Converts quads and n-gons to triangles

**Implementation**:
- Add `triangulate_meshes` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Apply triangulation modifier before export (or use Blender's export option if available)
- Pass to `bpy.ops.wm.usd_export()` as `triangulate_meshes` (if supported)

**Blender API**:
```python
export_params = {
    "triangulate_meshes": False,
}
```

**Dependencies**: Verify Blender 5.0 USD exporter triangulation support  
**Estimated Effort**: 2-3 hours

---

### 4.8 Quad Method & N-gon Method
**Priority**: Low (v0.3.0)  
**Category**: Geometry

**Requirements**:
- Per-endpoint selection of quad triangulation method (Shortest Diagonal, Longest Diagonal, Fixed, Fixed Alternate, Beauty)
- Per-endpoint selection of n-gon triangulation method (Beauty, Clip)
- Default: Shortest Diagonal (quads), Beauty (n-gons)
- Used when triangulating meshes

**Implementation**:
- Add `quad_method` EnumProperty to `USDME_Endpoint` (props.py)
- Add `ngon_method` EnumProperty to `USDME_Endpoint` (props.py)
- Add dropdowns in endpoint settings panel (ui.py)
- Apply during triangulation (if triangulate_meshes is enabled)

**Blender API**:
```python
# Applied via bpy.ops.mesh.quads_convert_to_tris() or similar
quad_method = "SHORTEST_DIAGONAL"  # SHORTEST_DIAGONAL, LONGEST_DIAGONAL, FIXED, FIXED_ALTERNATE, BEAUTY
ngon_method = "BEAUTY"  # BEAUTY, CLIP
```

**Dependencies**: Triangulate Meshes (4.7)  
**Estimated Effort**: 2-3 hours

---

## 5. Material Export Options

### 5.1 Convert to USD Preview Surface
**Priority**: High (v0.2.0)  
**Category**: Materials

**Requirements**:
- Per-endpoint toggle: Convert Blender materials to USD Preview Surface
- Default: True
- Converts Blender shader nodes to USD Preview Surface material

**Implementation**:
- Add `generate_preview_surface` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `generate_preview_surface`

**Blender API**:
```python
export_params = {
    "generate_preview_surface": True,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

### 5.2 Export Cycles Shaders
**Priority**: Low (v0.3.0)  
**Category**: Materials

**Requirements**:
- Per-endpoint toggle: Export Cycles shader nodes (advanced)
- Default: False
- Exports Blender Cycles shader networks as USD shader prims

**Implementation**:
- Add `export_cycles_shaders` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `export_cycles_shaders`

**Blender API**:
```python
export_params = {
    "export_cycles_shaders": False,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

### 5.3 Convert to MDL
**Priority**: Low (v0.3.0)  
**Category**: Materials

**Requirements**:
- Per-endpoint toggle: Convert materials to MDL (Material Definition Language)
- Default: False
- Converts Blender materials to NVIDIA MDL format for Omniverse

**Implementation**:
- Add `convert_to_mdl` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `convert_to_mdl`

**Blender API**:
```python
export_params = {
    "convert_to_mdl": False,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

### 5.4 Texture Export Options
**Priority**: Medium (v0.2.0)  
**Category**: Materials

**Requirements**:
- **Export Textures**: Per-endpoint toggle to export texture images
- **Overwrite Textures**: Per-endpoint toggle to overwrite existing texture files
- **Use Original Paths**: Per-endpoint toggle to use original texture file paths
- Default: Export Textures = True, Overwrite = False, Use Original Paths = False

**Implementation**:
- Add BoolProperty for each option to `USDME_Endpoint` (props.py)
- Add checkboxes in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` with appropriate parameters

**Blender API**:
```python
export_params = {
    "export_textures": True,
    "overwrite_textures": False,
    "use_original_texture_paths": False,
}
```

**Dependencies**: None  
**Estimated Effort**: 2 hours

---

### 5.5 USDZ Texture Options
**Priority**: Low (v0.3.0)  
**Category**: Materials

**Requirements**:
- **USDZ Texture Downscale**: Per-endpoint selection (Keep, 1/2, 1/4, 1/8)
- **USDZ Custom Downscale**: Per-endpoint custom downscale value (integer, default: 128)
- Default: Keep (no downscaling)
- Used for USDZ/ARKit asset optimization

**Implementation**:
- Add `usdz_texture_downscale` EnumProperty to `USDME_Endpoint` (props.py)
- Add `usdz_custom_downscale` IntProperty to `USDME_Endpoint` (props.py)
- Add UI controls in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` with appropriate parameters

**Blender API**:
```python
export_params = {
    "usdz_texture_downscale": "KEEP",  # KEEP, HALF, QUARTER, EIGHTH
    "usdz_custom_downscale": 128,
}
```

**Dependencies**: Create ARKit Asset (1.4)  
**Estimated Effort**: 2 hours

---

## 6. Light Export Options

### 6.1 Light Intensity Scale
**Priority**: Medium (v0.2.0)  
**Category**: Lights

**Requirements**:
- Per-endpoint light intensity scale factor (float, default: 1.0)
- Multiplies light intensity values during export
- Used for unit conversion or artistic control

**Implementation**:
- Add `light_intensity_scale` FloatProperty to `USDME_Endpoint` (props.py)
- Add number input in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `light_intensity_scale`

**Blender API**:
```python
export_params = {
    "light_intensity_scale": 1.0,
}
```

**Dependencies**: Export Lights (3.1)  
**Estimated Effort**: 1 hour

---

### 6.2 Convert Light Units to Nits
**Priority**: Low (v0.3.0)  
**Category**: Lights

**Requirements**:
- Per-endpoint toggle: Convert light units to nits (candela per square meter)
- Default: True
- Converts Blender light units to physical nits for accurate lighting

**Implementation**:
- Add `convert_light_units_to_nits` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `convert_light_units_to_nits`

**Blender API**:
```python
export_params = {
    "convert_light_units_to_nits": True,
}
```

**Dependencies**: Export Lights (3.1)  
**Estimated Effort**: 1 hour

---

### 6.3 Scale Light Radius
**Priority**: Low (v0.3.0)  
**Category**: Lights

**Requirements**:
- Per-endpoint toggle: Scale light radius during export
- Default: True
- Applies scaling to area light radius values

**Implementation**:
- Add `scale_light_radius` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `scale_light_radius`

**Blender API**:
```python
export_params = {
    "scale_light_radius": True,
}
```

**Dependencies**: Export Lights (3.1)  
**Estimated Effort**: 1 hour

---

### 6.4 Convert World Material
**Priority**: Low (v0.3.0)  
**Category**: Lights

**Requirements**:
- Per-endpoint toggle: Convert Blender world material to USD
- Default: True
- Exports Blender world shader as USD dome light or environment map

**Implementation**:
- Add `convert_world_material` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `convert_world_material`

**Blender API**:
```python
export_params = {
    "convert_world_material": True,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

## 7. Rigging Export Options

### 7.1 Armatures Export
**Priority**: Medium (v0.4.0)  
**Category**: Rigging

**Requirements**:
- Per-endpoint toggle: Export armatures (skeletons)
- Default: True
- Exports Blender armatures as USD skeleton prims

**Implementation**:
- Add `export_armatures` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `export_armatures`

**Blender API**:
```python
export_params = {
    "export_armatures": True,
}
```

**Dependencies**: Verify Blender 5.0 USD exporter armature support  
**Estimated Effort**: 2-3 hours

---

### 7.2 Only Deform Bones
**Priority**: Low (v0.4.0)  
**Category**: Rigging

**Requirements**:
- Per-endpoint toggle: Export only deform bones (skip control bones)
- Default: False
- Filters armature bones to only export deformation bones

**Implementation**:
- Add `only_deform_bones` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Filter bones before export (or use Blender's export option if available)
- Pass to `bpy.ops.wm.usd_export()` as `only_deform_bones` (if supported)

**Blender API**:
```python
export_params = {
    "only_deform_bones": False,
}
```

**Dependencies**: Armatures Export (7.1)  
**Estimated Effort**: 2 hours

---

### 7.3 Shape Keys Export
**Priority**: Medium (v0.4.0)  
**Category**: Rigging

**Requirements**:
- Per-endpoint toggle: Export shape keys (blend shapes)
- Default: True
- Exports Blender shape keys as USD blend shape prims

**Implementation**:
- Add `export_shape_keys` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- **Note**: Current implementation removes shape keys before subdivision export. This option controls shape key export when subdivision is disabled.
- Pass to `bpy.ops.wm.usd_export()` as `export_shape_keys`

**Blender API**:
```python
export_params = {
    "export_shape_keys": True,
}
```

**Dependencies**: Verify Blender 5.0 USD exporter shape key support  
**Estimated Effort**: 2-3 hours

---

## 8. Animation Export Options

### 8.1 Animation Export Toggle
**Priority**: High (v0.4.0)  
**Category**: Animation

**Requirements**:
- Per-endpoint toggle: Export animation
- Default: False (current behavior)
- Enables/disables animation export for the endpoint

**Implementation**:
- Add `export_animation` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `export_animation`
- **Note**: Currently hardcoded to False in ops_export.py

**Blender API**:
```python
export_params = {
    "export_animation": False,
}
```

**Dependencies**: None  
**Estimated Effort**: 1 hour

---

### 8.2 Animation Frame Range
**Priority**: High (v0.4.0)  
**Category**: Animation

**Requirements**:
- Per-endpoint specification of animation frame range:
  - **Start Frame**: Integer (default: 1)
  - **End Frame**: Integer (default: 250)
  - **Frame Step**: Float (default: 1.0)
- Validation: Start Frame < End Frame, Frame Step > 0

**Implementation**:
- Add `animation_start_frame` IntProperty to `USDME_Endpoint` (props.py)
- Add `animation_end_frame` IntProperty to `USDME_Endpoint` (props.py)
- Add `animation_frame_step` FloatProperty to `USDME_Endpoint` (props.py)
- Add number inputs in endpoint settings panel (ui.py)
- Validate frame range in pre-flight checks
- Pass to `bpy.ops.wm.usd_export()` with appropriate parameters

**Blender API**:
```python
export_params = {
    "export_animation": True,
    "start_frame": 1,
    "end_frame": 250,
    "frame_step": 1.0,
}
```

**Dependencies**: Animation Export Toggle (8.1)  
**Estimated Effort**: 2-3 hours

---

## 9. Particles & Instancing Export Options

### 9.1 Particles Export
**Priority**: Medium (v0.4.0)  
**Category**: Particles & Instancing

**Requirements**:
- Per-endpoint toggle: Export particle systems
- Default: True
- Exports Blender particle systems as USD point instancers or geometry

**Implementation**:
- Add `export_particles` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `export_particles`

**Blender API**:
```python
export_params = {
    "export_particles": True,
}
```

**Dependencies**: Verify Blender 5.0 USD exporter particle support  
**Estimated Effort**: 2-3 hours

---

### 9.2 Hair Export
**Priority**: Medium (v0.4.0)  
**Category**: Particles & Instancing

**Requirements**:
- Per-endpoint toggle: Export hair particle systems
- Default: True
- Exports Blender hair particles as USD curves or geometry

**Implementation**:
- Add `export_hair` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `export_hair`

**Blender API**:
```python
export_params = {
    "export_hair": True,
}
```

**Dependencies**: Particles Export (9.1)  
**Estimated Effort**: 1-2 hours

---

### 9.3 Export Child Particles
**Priority**: Low (v0.4.0)  
**Category**: Particles & Instancing

**Requirements**:
- Per-endpoint toggle: Export child particles (particle children)
- Default: False
- Exports child particles in addition to parent particles

**Implementation**:
- Add `export_child_particles` BoolProperty to `USDME_Endpoint` (props.py)
- Add checkbox in endpoint settings panel (ui.py)
- Pass to `bpy.ops.wm.usd_export()` as `export_child_particles`

**Blender API**:
```python
export_params = {
    "export_child_particles": False,
}
```

**Dependencies**: Particles Export (9.1)  
**Estimated Effort**: 1 hour

---

## 10. Export Presets System

### 10.1 Export Presets
**Priority**: Medium (v0.5.0)  
**Category**: Workflow Enhancements

**Requirements**:
- Predefined export presets for common workflows:
  - **Default**: Balanced settings for general use
  - **Omniverse**: Optimized for NVIDIA Omniverse
  - **ARKit/USDZ**: Optimized for ARKit/USDZ export
  - **VFX Pipeline**: ASWF-compliant settings
  - **Game Engine**: Optimized for game engines
- Per-endpoint preset selection
- Ability to save custom presets
- Preset inheritance: Endpoints can override preset values

**Implementation**:
- Create `USDME_Preset` PropertyGroup (props.py)
- Create preset storage system (addon preferences or scene properties)
- Add preset dropdown in endpoint settings panel (ui.py)
- Apply preset values to endpoint when selected
- Allow per-endpoint overrides after preset application
- Save/load presets from JSON or YAML files

**Dependencies**: All export options (1-9)  
**Estimated Effort**: 8-10 hours

---

### 10.2 Preset Management UI
**Priority**: Low (v0.5.0)  
**Category**: Workflow Enhancements

**Requirements**:
- UI for managing export presets:
  - Create new preset from current endpoint settings
  - Edit existing presets
  - Delete presets
  - Import/export presets as files
- Preset validation and error handling

**Implementation**:
- Add preset management operators (ops_presets.py)
- Add preset management UI panel (ui.py)
- Implement preset CRUD operations
- Add preset import/export functionality

**Dependencies**: Export Presets (10.1)  
**Estimated Effort**: 4-6 hours

---

## 11. Implementation Plan Summary

### Phase 1: Core Export Options (v0.2.0)
**Timeline**: 2-3 weeks  
**Goal**: Enable per-endpoint control over essential export parameters

**Features**:
1. General Export Settings (1.1-1.5) - Includes new Unit System Control (1.5)
2. Stage Configuration (2.1-2.2)
3. Export Type Selection (3.1)
4. Basic Geometry Options (4.1-4.5)
5. Material Export Options (5.1, 5.4)

**Estimated Effort**: 20-25 hours

**Implementation Steps**:
1. **Week 1**: Version-aware compatibility layer (CRITICAL FIRST STEP)
   - **Implement version-aware USD export wrapper** (see Section 12.1)
   - Query Blender 5.0 USD exporter RNA properties to get valid parameter names
   - Build parameter filtering and rename mapping system
   - Test wrapper with minimal parameters to verify it works
   - Document any discovered parameter name differences

2. **Week 1-2**: Property definitions and UI layout
   - Add all BoolProperty, EnumProperty, StringProperty to `USDME_Endpoint` (props.py)
   - Create collapsible UI sections in endpoint settings panel (ui.py)
   - Implement property validation functions

3. **Week 2**: Export integration
   - Update `USDME_OT_export_endpoints` to use version-aware wrapper (ops_export.py)
   - Build export parameters using compatibility layer
   - Test each export option individually to verify parameter names
   - Enable verbose logging to catch unsupported parameters

4. **Week 3**: Testing and refinement
   - Test all export options with real Blender 5.0 scenes
   - Build parameter rename map based on discovered differences
   - Fix any parameter name mismatches
   - Verify exported USD files open correctly in target applications
   - Update documentation

---

### Phase 2: Advanced Geometry & Materials (v0.3.0)
**Timeline**: 1-2 weeks  
**Goal**: Full control over geometry processing and material export

**Features**:
1. Advanced Geometry Options (4.6-4.8)
2. Material Export Options (5.2-5.3, 5.5)
3. Light Export Options (6.1-6.4)

**Estimated Effort**: 12-15 hours

**Implementation Steps**:
1. Add remaining geometry and material properties
2. Implement triangulation and quad/ngon method handling
3. Add MDL and Cycles shader export support
4. Add light export options
5. Testing and validation

---

### Phase 3: Animation & Rigging (v0.4.0)
**Timeline**: 2-3 weeks  
**Goal**: Support for animated exports and rigging workflows

**Features**:
1. Animation Export (8.1-8.2)
2. Rigging Support (7.1-7.3)
3. Particles & Instancing (9.1-9.3)

**Estimated Effort**: 15-20 hours

**Implementation Steps**:
1. Research Blender 5.0 USD exporter animation/rigging support
2. Implement animation frame range controls
3. Add armature and shape key export support
4. Add particle system export support
5. Testing with animated and rigged scenes

---

### Phase 4: Workflow Enhancements (v0.5.0+)
**Timeline**: 2-3 weeks  
**Goal**: Productivity features and advanced workflows

**Features**:
1. Export Presets (10.1-10.2)
2. Enhanced validation and pre-flight checks
3. Batch operations improvements

**Estimated Effort**: 15-20 hours

**Implementation Steps**:
1. Design preset system architecture
2. Implement preset storage and management
3. Create preset UI and operators
4. Add preset import/export functionality
5. Testing and documentation

---

## 12. Technical Considerations

### 12.1 Blender API Compatibility & Version-Aware Wrapper
**Challenge**: Blender 5.0 changed Python API aspects and USD exporter options were renamed/removed. Treating Blender 2.8-4.x examples as drop-in compatible is risky and may trigger `TypeError: keyword not recognized` in 5.0.

**Key Changes in Blender 5.0**:
- Some Alembic/USD exporter options were removed or renamed as part of cleanup of deprecated export operator properties
- Old examples that pass many keyword arguments to `bpy.ops.wm.usd_export` may now fail in 5.0
- The exporter still lives under `bpy.ops.wm.usd_export` but exact RNA property names must match
- USDHook extension points provide a more stable extension surface than operator-parameter spelunking

**Solution**: Implement a version-aware compatibility wrapper that:
- Uses `bpy.app.version` to branch between pre-5.0 and 5.0+ behavior
- Builds the argument dict in one place, filtering out keys not present in current operator's RNA
- Maps old parameter names to new ones via lookup table
- Provides safe fallbacks instead of failing hard
- Optionally uses USDHook for more stable extension points

**Implementation Pattern**:
```python
# In ops_export.py - Version-aware USD export wrapper
import bpy
from typing import Dict, Any, Set

def _get_usd_export_properties() -> Set[str]:
    """Get set of valid property identifiers for current Blender version's USD exporter."""
    try:
        op_type = bpy.ops.wm.usd_export.get_rna_type()
        return {prop.identifier for prop in op_type.properties if prop.identifier != 'rna_type'}
    except (AttributeError, TypeError):
        # Fallback: return empty set if unable to query
        return set()

def _get_parameter_rename_map() -> Dict[str, str]:
    """Map old parameter names to new ones for Blender 5.0 compatibility."""
    # Add mappings as discovered during testing
    # Example: {"old_name": "new_name"}
    return {
        # "export_selected": "selected_objects_only",  # Example mapping
        # Add more mappings as needed based on actual Blender 5.0 changes
    }

def build_usd_export_params(endpoint, logger) -> Dict[str, Any]:
    """
    Build USD export parameters dict with version-aware compatibility.
    
    Filters out unsupported parameters and maps old names to new ones.
    Logs warnings for ignored parameters instead of crashing.
    """
    # Get valid properties for current Blender version
    valid_props = _get_usd_export_properties()
    rename_map = _get_parameter_rename_map()
    
    # Build parameter dict from endpoint settings
    endpoint_params = {
        # Map endpoint properties to export parameter names
        "filepath": filepath,  # Required
        "export_materials": endpoint.export_materials if hasattr(endpoint, 'export_materials') else True,
        "export_uvmaps": endpoint.export_uvmaps if hasattr(endpoint, 'export_uvmaps') else True,
        "export_normals": endpoint.export_normals if hasattr(endpoint, 'export_normals') else True,
        "export_animation": endpoint.export_animation if hasattr(endpoint, 'export_animation') else False,
        "export_lights": endpoint.export_lights if hasattr(endpoint, 'export_lights') else False,
        "root_prim_path": endpoint.root_prim_path if hasattr(endpoint, 'root_prim_path') else f"/{sanitized_name}",
        # Add all other endpoint properties here...
    }
    
    # Filter and rename parameters
    filtered_params = {}
    for key, value in endpoint_params.items():
        # Apply rename mapping
        mapped_key = rename_map.get(key, key)
        
        # Only include if parameter exists in current Blender version
        if mapped_key in valid_props:
            filtered_params[mapped_key] = value
        else:
            # Log warning but don't crash
            logger.warning(
                f"USD export parameter '{key}' (mapped: '{mapped_key}') not supported "
                f"in Blender {bpy.app.version_string}. Ignoring."
            )
    
    return filtered_params

def export_usd_safe(filepath: str, endpoint, logger, **user_opts) -> Dict[str, Any]:
    """
    Safe USD export wrapper with version compatibility.
    
    Args:
        filepath: Output USD file path
        endpoint: USDME_Endpoint instance with export settings
        logger: Logger instance for warnings
        **user_opts: Additional export options (optional)
    
    Returns:
        Result dict from bpy.ops.wm.usd_export()
    """
    # Build base parameters from endpoint
    export_params = build_usd_export_params(endpoint, logger)
    
    # Add filepath (required)
    export_params["filepath"] = filepath
    
    # Merge user-provided options (with same filtering)
    valid_props = _get_usd_export_properties()
    rename_map = _get_parameter_rename_map()
    
    for key, value in user_opts.items():
        mapped_key = rename_map.get(key, key)
        if mapped_key in valid_props:
            export_params[mapped_key] = value
        else:
            logger.warning(f"Ignoring unsupported user option: {key}")
    
    # Execute export with filtered parameters
    try:
        result = bpy.ops.wm.usd_export(**export_params)
        return result
    except TypeError as e:
        # Catch any remaining parameter errors
        logger.error(f"USD export failed: {e}")
        logger.error(f"Attempted parameters: {list(export_params.keys())}")
        raise

# Usage in USDME_OT_export_endpoints.execute():
# result = export_usd_safe(filepath, endpoint, logger)
```

**Version Detection**:
```python
# Check Blender version for conditional behavior
if bpy.app.version >= (5, 0, 0):
    # Blender 5.0+ behavior
    use_strict_parameter_validation = True
else:
    # Pre-5.0 behavior (if supporting older versions)
    use_strict_parameter_validation = False
```

**USDHook Extension Points** (Future Enhancement):
- Blender exposes `USDHook` and related contexts for extending USD export/import
- Hooks like `USDMaterialExportContext.get_stage()` and `export_texture` provide more stable extension surface
- Reduces breakage across 4.x → 5.0 transitions compared to operator-parameter spelunking
- Consider using USDHook for advanced features like custom metadata or post-processing

**Migration Strategy**:
1. Start from Blender 5.0 manual's USD export options list as "source of truth" for parameter names
2. Run add-on on Blender 5.0 with verbose logging to identify dropped/renamed parameters
3. Build parameter rename map based on discovered changes
4. Test each export option individually to verify parameter names
5. Document any parameter name differences for future reference

**Testing Approach**:
- Test with Blender 5.0+ only (add-on targets 5.0+)
- Enable verbose logging to catch unsupported parameters
- Test each export option individually before integration
- Verify exported USD files open correctly in target applications

---

### 12.2 Property Storage & Performance
**Challenge**: Storing many properties per endpoint may impact performance and memory.

**Solution**:
- Use efficient PropertyGroup storage (already implemented)
- Lazy-load export settings only when needed
- Cache export parameter dictionaries
- Minimize property update callbacks

**Implementation**:
- Current `USDME_Endpoint` PropertyGroup is efficient
- Consider grouping related properties into sub-groups if needed
- Use property update callbacks sparingly (only for dependent properties)

---

### 12.3 UI Complexity Management
**Challenge**: Many export options may overwhelm users in the UI.

**Solution**:
- Organize options into collapsible sections (General, Stage, Geometry, Materials, etc.)
- Use preset system to hide complexity for common workflows
- Provide tooltips and help text for each option
- Show only relevant options based on endpoint type

**Implementation**:
```python
# In ui.py - Collapsible sections
layout.prop(endpoint, "export_materials")
if endpoint.export_materials:
    box = layout.box()
    box.prop(endpoint, "generate_preview_surface")
    box.prop(endpoint, "export_textures")
    # ... more material options
```

---

### 12.4 Backward Compatibility
**Challenge**: Existing endpoints (v0.1.3) don't have new export properties.

**Solution**:
- Provide default values for all new properties
- Use property defaults that match current hardcoded behavior
- Migration function to update existing endpoints (if needed)

**Implementation**:
- All new properties have sensible defaults
- Existing endpoints will use defaults automatically
- No migration needed (Blender handles missing properties gracefully)

---

## 13. Testing Strategy

### 13.1 Unit Testing
- Test property definitions and defaults
- Test export parameter building
- Test validation functions

### 13.2 Integration Testing
- Test each export option individually
- Test combinations of export options
- Test with various endpoint types (Collection/Object)

### 13.3 User Testing
- Test with real Blender scenes
- Test with various USD-consuming applications (Omniverse, USD View, etc.)
- Gather feedback on UI organization and usability

---

## 14. Documentation Requirements

### 14.1 User Documentation
- Update README.md with new export options
- Create export options reference guide
- Add preset documentation

### 14.2 Developer Documentation
- Document property definitions and defaults
- Document export parameter mapping
- Update implementation plan with completed features

---

## 15. Success Criteria

### Phase 1 (v0.2.0) Success Criteria
- ✅ All Priority 1 features implemented and tested
- ✅ Per-endpoint export settings working correctly
- ✅ UI organized and user-friendly
- ✅ Documentation updated

### Phase 2 (v0.3.0) Success Criteria
- ✅ All Priority 2 features implemented and tested
- ✅ Advanced geometry and material options working
- ✅ Light export options functional

### Phase 3 (v0.4.0) Success Criteria
- ✅ Animation export working correctly
- ✅ Rigging export functional
- ✅ Particle export supported

### Phase 4 (v0.5.0) Success Criteria
- ✅ Preset system implemented and tested
- ✅ User workflow improved with presets
- ✅ All export options accessible via presets

---

## 16. Risk Assessment

### High Risk
- **Blender API Changes**: Blender 5.0 changed USD exporter parameter names/removed options. Old 2.8-4.x examples may trigger `TypeError: keyword not recognized` in 5.0
  - **Mitigation**: 
    - Implement version-aware compatibility wrapper (see Section 12.1)
    - Filter parameters against current operator's RNA properties
    - Map old parameter names to new ones via lookup table
    - Use USDHook extension points for stable features where possible
    - Test all parameters individually on Blender 5.0 before integration
    - Enable verbose logging to catch unsupported parameters during development

### Medium Risk
- **UI Complexity**: Too many options may overwhelm users
  - **Mitigation**: Use presets, collapsible sections, and good organization

### Low Risk
- **Performance**: Many properties per endpoint
  - **Mitigation**: Efficient storage, lazy loading, caching

---

## 17. Dependencies & Prerequisites

### External Dependencies
- **Blender 5.0+**: Required for USD export functionality
- **USD Python API**: May be needed for post-processing (Default Prim Kind)

### Internal Dependencies
- **Current MVP (v0.1.3)**: All features build on existing architecture
- **State Manager**: May need enhancements for selection/visibility filtering
- **Path Resolver**: No changes needed

---

## 18. Future Considerations

### Potential Enhancements (Post-v0.5.0)
- **USD Composition**: Support for layers, variants, references (requires Blender API support)
- **Custom Metadata**: User-defined metadata per endpoint
- **Export Templates**: Template-based export configuration
- **Batch Preset Application**: Apply presets to multiple endpoints
- **Export Validation**: Pre-flight checks for export readiness
- **Export History**: Track export history and settings

---

## 19. Notes & Assumptions

### Assumptions
- Blender 5.0 USD exporter supports all listed parameters (to be verified)
- Users want per-endpoint control over export options
- Preset system will reduce UI complexity for common workflows

### Exclusions
- **Nucleus Connectivity**: Explicitly excluded from this roadmap
- **USD Composition Arcs**: Not supported by Blender's USD exporter
- **Custom USD Schemas**: Out of scope for this add-on

### Open Questions
1. Does Blender 5.0 USD exporter support all listed parameters?
2. Should some options be global (addon preferences) vs per-endpoint?
3. What are the most common export workflows (for preset design)?

---

## 20. Conclusion

This roadmap provides a comprehensive plan for expanding the Blender USD Multi Export add-on with full export option support. The phased approach allows for incremental development and testing, ensuring each phase is stable before moving to the next.

**Next Steps**:
1. Review and prioritize features based on user needs
2. Verify Blender 5.0 USD exporter parameter support
3. Begin Phase 1 implementation (Core Export Options)
4. Gather user feedback after each phase

**Status**: Ready for evaluation and prioritization

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-12-28  
**Author**: AI Agent (based on HANDOFF.md, NVIDIA best practices, and Blender USD export options)

