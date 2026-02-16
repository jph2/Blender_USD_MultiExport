# Blender USD Multi Export - Complete Implementation Plan

**Version**: 2.12.3 | **Date**: 05.02.2026 | **Time**: 00:35 | **GlobalID**: 20260205_0035_Blender_USD_MultiExport_01
**Status**: ✅ MVP Complete - v0.1.3 Released (Perspective: start point as pipeline origin)
**Date Created**: 25.11.2025
**Last Updated**: 03.02.2026
**Target Platform**: Blender 5.0+ (officially released November 18, 2025)
**MVP Release**: v0.1.3 - December 23, 2025

---

## 📋 Executive Summary

**Blender USD Multi Export v0.1.3** is a functional MVP (Minimum Viable Product) that provides the core **start point**-based USD export workflow. Start points are the stable DCC origins for downstream USD pipeline and composition arcs. This version establishes the fundamental architecture and proves the concept works, while deferring advanced features for future iterations based on testing feedback and user needs.

**Perspective: Start Point (Pipeline Origin)**  
The addon defines **start points** in the DCC—the stable origins for the USD pipeline. Exported USD files are the **beginning** of further pipelining (composition arcs, references, layers), not the terminus. Naming (start point, USD_StartPoint folder) reflects this pipeline-origin perspective.

**System Architecture: Push vs Pull Workflows (Following Rhino Plan Approach)**

**MVP Architecture: One-Way Push Model** (Aligned with Rhino USD Multi Export v1.1.0)

Following the proven approach from the Rhino USD Multi Export plan, the MVP focuses on a **one-way push model** for ComfyUI integration:

**Push Phase (Blender Side)**:
- **Blender** exports USD files to predefined destinations via **start point** definitions (pipeline origins)
- Export happens independently in Blender (user-initiated or scripted)
- User defines file paths and naming conventions upfront
- USD files are written to specified file paths with consistent naming
- **No ComfyUI involvement** in the export process

**Pull Phase (ComfyUI Side)**:
- **ComfyUI** reads the export path from **start point** definitions stored in .blend file
- ComfyUI nodes (e.g., BlenderToUSD) load pre-generated USD files from specified locations
- **Passive file loading** - ComfyUI does not trigger Blender exports
- USD files are consumed downstream in ComfyUI workflows

**Key Clarification (Following Rhino Plan)**:
- ❌ **NOT MVP**: Bidirectional execution (ComfyUI driving Blender exports) - Out of scope for MVP per Rhino plan
- ✅ **MVP**: One-way push (define paths → Blender exports → ComfyUI reads paths → ComfyUI loads files)
- 🔮 **Future**: Bidirectional execution added as enhancement in v0.4.0+ (following Rhino Phase 3 approach)

**MVP Workflow (Push Model)**:
1. User defines export **start points** with file paths and naming
2. User initiates export in Blender (push operation)
3. Blender exports USD files to predefined locations
4. ComfyUI reads **start point** definitions and loads pre-generated USD files
5. No ComfyUI involvement in export triggering (pure push model)

**Benefits of Push Model** (Validated in Rhino Plan):
- Simple, focused architecture validated by Rhino implementation
- No complex API integration required
- Clear separation of concerns
- Reliable file-based communication
- Easy to debug and validate
- Consistent with VFX pipeline workflows (export then consume)

**Reference**: This approach mirrors the Rhino USD Multi Export plan (see `Rhino_USD_MultiExport/04_Implementation_Plan.md` Section "Out of Scope (MVP): ComfyUI bidirectional integration (MVP: push-only)")

**MVP Scope Delivered:**
- ✅ **Core Workflow**: Define export start points and export multiple USD files
- ✅ **Safety**: Scene state protection and automatic restoration
- ✅ **Usability**: Functional UI with start point management
- ✅ **Reliability**: Comprehensive error handling and logging
- ✅ **Standards**: Cross-platform path handling and basic USD export

**Key Achievements:**
- ✅ Complete working addon (6 functional modules, ~650 lines)
- ✅ State management system preventing scene corruption
- ✅ Comprehensive logging and automated bug reporting
- ✅ Critical runtime error fixes from peer review
- ✅ Detailed testing plan and MVP validation procedures

---

## 🎯 Implementation Overview

### Approach
This implementation follows a **MVP-first strategy** focusing on core functionality validation before investing in advanced features. The addon provides start point-based USD export without attempting USD composition arcs, staying within Blender's architectural constraints.

### Development Phases
1. **Phase 0**: Repository Analysis & Planning (Planning → Implementation transition)
2. **Phase 1**: MVP Core Functionality (State management, export logic, UI)
3. **Phase 2**: Quality Assurance & Testing (Bug fixes, testing framework)
4. **Phase 3**: Future Enhancements (Advanced features post-MVP validation, including ComfyUI pull capabilities for bidirectional execution)

### Timeline
- **Planning**: November 25-30, 2025 (Research and requirements gathering)
- **Implementation**: December 23, 2025 (Single-session MVP development)
- **MVP Release**: December 23, 2025 (v0.1.3)
- **Future**: v0.2.0+ Advanced features (Post-MVP validation)

---

## 📅 Detailed Implementation Timeline

### Phase 0: Repository Analysis & Planning (Completed)
**Date**: December 23, 2025
**Objective**: Transform planning documents into functional code
**Activities**:
- ✅ Analyzed existing repository structure (comprehensive planning docs, no code)
- ✅ Reviewed research documents and requirements
- ✅ Identified gaps between planning and implementation
- ✅ Assessed technical feasibility for Blender 5.0+ targeting

**Key Findings**:
- Repository contained comprehensive planning documents but no actual code
- Well-structured requirements and research existed
- Clear Blender 5.0+ targeting with USD export limitations understood
- Project needed transformation from documentation to implementation

### Phase 1: Core Addon Implementation (Completed)
**Date**: December 23, 2025
**Objective**: Create functional Blender addon skeleton with MVP features

#### Technical Implementation Details

**1. Addon Registration (`__init__.py`)** - ✅ **IMPLEMENTED**
```python
bl_info = {
    "name": "USD Multi Export",
    "author": "Blender USD Multi Export Project",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),  # Blender 5.0+ required
    "location": "Scene Properties; 3D Viewport > N-Panel",
    "description": "Export multiple USD component assets from Blender scenes using start point definitions.",
    "category": "Import-Export",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/jph2/Blender_USD_MultiExport",
    "tracker_url": "https://github.com/jph2/Blender_USD_MultiExport/issues",
}
```
- ✅ Includes addon preferences (`USDMultiExportPreferences`)
- ✅ Log level control in preferences
- ✅ Default export settings in preferences

**2. Data Model (`props.py`)** - ✅ **IMPLEMENTED**
- ✅ `USDME_Start pointPropertyGroup`: Start point definition with:
  - `name`, `start point_type`, `collection_name`, `object_name`
  - `include_subcollections`, `create_subfolder`, `include_origin_metadata`
  - `export_subdivision`, `filepath`, `enabled`
  - Auto-naming callbacks (`_update_name_and_filepath`)
- ✅ `USDME_SceneProperties`: Scene-level container for start points collection
- ✅ Proper Blender property system integration with validation
- ✅ Property update callbacks for auto-naming and filepath generation

**3. State Management (`state_manager.py`)** - ✅ **IMPLEMENTED**
- ✅ `ScopedIsolation`: Context manager for safe scene isolation during export
  - Supports Collection and Object types
  - Recursive collection inclusion option
  - Object hierarchy traversal
  - Guaranteed state restoration
- ✅ `StateManager`: Comprehensive scene state backup/restore system
  - `safe_batch_operation()` context manager
  - Multiple backup support
  - Scene integrity validation
  - Automatic rollback on exceptions
- ✅ Protection against scene corruption and crash recovery

**4. Logging System (`logging_utils.py`)** - ✅ **IMPLEMENTED**
- ✅ `USDME_Logger`: Centralized logging with timestamps and context
  - File rotation (5MB max, 3 backups)
  - Console handler with configurable log levels
  - Context stack for nested operations
  - Performance timers
- ✅ Verbose mode toggle for detailed debugging
- ✅ JSON bug report generation with system/scene information
  - System info, Blender info, addon info, scene info
  - Recent log entries and errors
- ✅ Operation tracking with duration metrics

**5. User Interface (`ui.py`)** - ✅ **IMPLEMENTED**
- ✅ Main panel in Scene Properties (`USDME_PT_main_panel`)
  - Start point list with inline editing
  - Type selector with visual indicators (icons)
  - Conditional UI based on start point type
  - Filepath editing with adequate space for long names
  - Subfolder creation toggle
  - Origin metadata toggle
  - Subdivision export toggle
  - Selection tracking button per start point
- ✅ Start point management:
  - `USDME_OT_add_start point` - Auto-detects collection/object from context
  - `USDME_OT_remove_start point` - Removes last start point (⚠️ no dropdown selection)
  - `USDME_OT_select_start point_target` - Selects start point target in viewport
- ✅ Export controls:
  - Export Start points button
  - Verbose logging toggle
- ✅ Bug report generation button (`USDME_OT_generate_bug_report`)

**6. Export Operations (`ops_export.py`)** - ✅ **IMPLEMENTED**
- ✅ Batch export logic with start point iteration
  - Pre-flight validation before export
  - Type-specific validation (Collection vs Object)
  - Enabled start point filtering
- ✅ Integration with state management and logging
  - Uses `ScopedIsolation` for safe isolation
  - Uses `StateManager.safe_batch_operation()` for batch safety
  - Comprehensive logging at each step
- ✅ Error handling and user feedback
  - Type-specific error messages
  - Invalid start point detection and reporting
  - Export success/failure reporting
- ✅ Subdivision export with duplicate preservation
  - Duplicates objects before applying modifiers
  - Cleans up duplicates after export
- ✅ Origin metadata injection (if enabled)
- ✅ Light exclusion (automatic)
- ⚠️ **LIMITATION**: Hardcoded export parameters (no per-start point overrides)
- ❌ **NOT IMPLEMENTED**: Overwrite confirmation dialog

### Phase 2: Repository Organization & Quality Assurance (Completed)
**Date**: December 23, 2025
**Objective**: Ensure correct project structure and code quality
- ✅ Identified files were created in wrong repository (`OV_USD_OminGuardR`)
- ✅ Moved all addon files to correct location (`Blender_USD_MultiExport/addon/`)
- ✅ Moved testing plan documentation
- ✅ Cleaned up incorrect repository
- ✅ Verified file integrity and paths

### Phase 3: Critical Issue Resolution (Completed)
**Date**: December 23, 2025
**Objective**: Address runtime errors identified in peer code review

**Specific Fixes Applied:**

**Issue 1: Invalid Blender API Calls**
```python
# BEFORE (broken):
bpy.ops.wm.report_message(type='ERROR', message=message)

# AFTER (fixed):
print(f"[USDME ERROR] {message}")
```

**Issue 2: Collection Attribute Error**
```python
# BEFORE (broken):
"collection_objects": len(collection.objects.all)

# AFTER (fixed):
"collection_objects": len(collection.objects)
```

**Issue 3: PropertyGroup Access Error**
```python
# BEFORE (broken):
len(getattr(scene, 'usdme_settings', {}).get('start points', []))

# AFTER (fixed):
len(scene.usdme_settings.start points) if hasattr(scene, 'usdme_settings') else 0
```

### Phase 4: Testing Framework & Documentation (Completed)
**Date**: December 23, 2025
**Objective**: Create comprehensive testing and validation framework
- ✅ Created detailed `05_Testing_Plan.md` with 6-phase testing approach
- ✅ Defined success criteria and performance benchmarks
- ✅ Documented bug reporting procedures and JSON format
- ✅ Created test data requirements and checklists
- ✅ Integrated testing plan into project documentation

### Phase 5: Subdivision Export Fix (Completed)
**Date**: December 28, 2025
**Objective**: Fix subdivision export to preserve original objects and modifiers

**Issue**: Subdivision modifiers were being applied directly to original objects, permanently modifying them. Scene state restoration only handled selection/visibility, not mesh data or modifiers.

**Solution Implemented**:
- Duplicate objects before applying subdivision modifiers
- Apply modifiers only to duplicates
- Export duplicates (which have baked subdivision geometry)
- Clean up duplicates after export to restore scene state
- Works for both OBJECT and COLLECTION start point types

**Key Changes**:
- Added duplicate tracking system (`duplicated_objects` list)
- Modified subdivision application logic to duplicate first
- Added cleanup logic to remove duplicates after export
- Ensured duplicates are visible and selected for export
- Added comprehensive error handling for cleanup

**Result**: Original objects and their modifiers are now preserved, like CTRL+Z after export. Exported USD files contain the subdivided geometry while the Blender scene remains unchanged.

### Phase 6: Complete Modifier Export & Namespace Consistency (v0.1.11-v0.1.12)
**Date**: January 24-25, 2026
**Objective**: Fix critical issues discovered during production testing with SHAKTI_Decals scene

**Issues Identified**:
1. **Wrong names in USD**: Exported prims had `_dup1`, `_dup2` suffixes instead of original names
2. **Incomplete export**: Only 2 of 6 objects exported (objects without SUBSURF skipped)
3. **Leftover duplicates**: Temporary objects not properly cleaned up
4. **Shrinkwrap not applied**: Non-SUBSURF modifiers not being baked

**Solution Implemented (v0.1.11) - Name-Swap Strategy**:

```python
# For each object that needs modifier baking:
# 1. Rename original to hidden name
hidden_name = f"__USDME_ORIG_{original_name}"
obj.name = hidden_name

# 2. Duplicate (gets original name since it's now free)
bpy.ops.object.duplicate(linked=False)
dup_obj.name = original_name  # Force original name

# 3. Apply modifiers to duplicate
for mod in dup_obj.modifiers:
    bpy.ops.object.modifier_apply(modifier=mod.name)

# 4. Export (duplicate has clean name)
# 5. Cleanup: Delete duplicate, rename original back
obj.name = original_name
```

**Key Changes (v0.1.11)**:
- Implemented name-swap strategy for clean USD prim names
- Added support for ALL modifier types (Shrinkwrap, Array, Mirror, etc.)
- Handle Shrinkwrap targets by temporarily unhiding them
- Moved cleanup OUTSIDE ScopedIsolation context
- Track name swaps for proper rollback
- Emergency name restoration in exception handlers

**Solution Implemented (v0.1.12) - Export All Objects**:

```python
# Build list of ALL objects to export:
objects_to_export = []

# 1. Add duplicates (objects with baked modifiers)
for dup_info in duplicated_objects:
    objects_to_export.append(dup_info["duplicate"])

# 2. Add originals that weren't duplicated (no modifiers)
for obj in mesh_objects:
    if obj.name not in duplicated_original_names:
        objects_to_export.append(obj)

# 3. Select and show only objects to export
for obj in objects_to_export:
    obj.hide_viewport = False
    obj.select_set(True)
```

**Key Changes (v0.1.12)**:
- Initialize `mesh_objects` list at function level (scope fix)
- Build `objects_to_export` including BOTH duplicates AND non-duplicated originals
- Ensure ALL mesh objects in collection are exported
- Added logging for export object preparation

**Result**:
- ✅ All 6 mesh objects in collection now exported
- ✅ USD prims have clean names matching Blender objects
- ✅ Shrinkwrap and all other modifiers correctly applied
- ✅ No leftover duplicates in Blender scene
- ✅ Original objects and names fully preserved

### Phase 7: Modifier Visibility Mode Handling (v0.1.13 - IMPLEMENTED)
**Status**: ✅ IMPLEMENTED  
**Date**: 25 January 2026  
**Discovery Reference**: See `00_Discovery.md` - "Session: Modifier Visibility Modes Investigation"

**Problem Identified**:

During production testing, inconsistent modifier application was observed:
- Some Shrinkwrap modifiers applied correctly
- Some were partially applied (partial deformation)
- Some were not applied at all (flat geometry)
- No visible pattern to explain the inconsistency

**Root Cause Analysis**:

Blender modifiers have **four visibility toggle flags** in the modifier header:

| Icon | Property | Description |
|------|----------|-------------|
| Triangle | `show_in_editmode` | Shows modifier in Edit Mode |
| Cage | `show_on_cage` | Edit mesh "as modified" |
| Monitor | `show_viewport` | **Enables modifier in 3D Viewport** |
| Camera | `show_render` | Enables modifier for final renders |

**Critical Finding**: The current code **does NOT check `show_viewport`** before applying modifiers.

When `bpy.ops.object.modifier_apply()` is called:
- The modifier is applied based on its **current evaluated state in the depsgraph**
- If `show_viewport=False`, the modifier **hasn't been evaluated**
- Result: Modifier applies with incorrect/unevaluated geometry

**Evidence**: Grep search for `show_viewport`, `show_render`, `show_in_editmode` returned **no matches** in the addon codebase.

**Planned Solution (v0.1.13)**:

**1. Force-Enable Viewport Visibility Before Applying**

```python
def apply_modifier_with_visibility_fix(context, obj, mod):
    """Apply modifier with forced viewport visibility."""
    
    # Force-enable viewport visibility for proper depsgraph evaluation
    original_show_viewport = mod.show_viewport
    if not mod.show_viewport:
        mod.show_viewport = True
        logger.log_step("modifier_visibility_forced", {
            "modifier_name": mod.name,
            "modifier_type": mod.type,
            "original_show_viewport": original_show_viewport
        })
    
    # Force depsgraph update after visibility change
    context.view_layer.update()
    
    # Now apply (modifier is guaranteed to be evaluated)
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name, single_user=True)
    # Note: No need to restore since modifier is deleted after apply
```

**2. Expand Target Object Visibility Handling**

Currently only Shrinkwrap targets are handled. Expand to ALL modifier types with targets:

```python
# Modifier types and their target properties
MODIFIER_TARGET_PROPERTIES = {
    'SHRINKWRAP': 'target',
    'LATTICE': 'object',
    'MESH_DEFORM': 'object',
    'SURFACE_DEFORM': 'target',
    'CURVE': 'object',
    'BOOLEAN': 'object',
    'ARMATURE': 'object',
    'HOOK': 'object',
    'WARP': ['object_from', 'object_to'],
    'CAST': 'object',
    'WAVE': 'start_position_object',
}

def ensure_modifier_target_visible(context, mod, visibility_backups):
    """Temporarily unhide target objects for modifier evaluation."""
    mod_type = mod.type
    if mod_type not in MODIFIER_TARGET_PROPERTIES:
        return
    
    target_props = MODIFIER_TARGET_PROPERTIES[mod_type]
    if isinstance(target_props, str):
        target_props = [target_props]
    
    for prop_name in target_props:
        target_obj = getattr(mod, prop_name, None)
        if target_obj and target_obj.name in context.view_layer.objects:
            if target_obj.hide_viewport:
                visibility_backups[target_obj.name] = True
                target_obj.hide_viewport = False
```

**3. Updated Modifier Application Loop**

```python
# Before applying modifiers
visibility_backups = {}

for mod in list(dup_obj.modifiers):
    # 1. Ensure target objects are visible
    ensure_modifier_target_visible(context, mod, visibility_backups)
    
    # 2. Force-enable modifier viewport visibility
    if not mod.show_viewport:
        mod.show_viewport = True
        logger.log_warning(
            f"Modifier '{mod.name}' had show_viewport=False, forced to True for export",
            context=start point_context
        )
    
    # 3. Force depsgraph update
    context.view_layer.update()
    
    # 4. Apply modifier
    apply_modifier_with_visibility_fix(context, dup_obj, mod)

# Restore target visibility
for obj_name, was_hidden in visibility_backups.items():
    if obj_name in context.view_layer.objects:
        context.view_layer.objects[obj_name].hide_viewport = was_hidden
```

**Acceptance Criteria**:
- [ ] Modifiers with `show_viewport=False` are correctly applied after force-enable
- [ ] Target objects for ALL modifier types are temporarily unhidden
- [ ] Depsgraph is updated after visibility changes
- [ ] Logging shows which modifiers had visibility overrides
- [ ] No regressions in existing modifier export functionality
- [ ] Test with modifiers in all 4 visibility state combinations

**Estimated Effort**: 2-3 hours

---

### Phase 8: Mesh Data Name Consistency (v0.1.14 - IMPLEMENTED)
**Status**: ✅ IMPLEMENTED  
**Date**: 25 January 2026  
**Discovery Reference**: See `00_Discovery.md` - "Session: Mesh Data Name Consistency"

**Problem Identified**:

After v0.1.13 successfully fixed modifier application, a new issue was discovered:
- Mesh prim names in USD were incrementing on each export (e.g., `Plane_011`, `Plane_014`, `Plane_016`)
- This broke USD referencing workflows that rely on consistent prim paths

**Root Cause Analysis**:

When duplicating an object in Blender:
1. Blender also duplicates the **mesh data block** (not just the object)
2. The duplicated mesh gets an auto-generated name (e.g., `Plane.005` → `Plane.011`)
3. These incrementing mesh names are exported to USD as mesh prim names
4. Each export creates new mesh data blocks with new names

**Planned Solution**:

Apply the same name-swap strategy used for objects to mesh data blocks:

1. Save original mesh data name before duplication
2. After duplication: rename original mesh data to hidden name
3. Rename duplicate's mesh data to original name
4. Export (mesh prims now have consistent names)
5. Cleanup: restore original mesh data names

**Code Implementation**:

```python
# v0.1.14: Get original mesh data name BEFORE duplication
original_mesh_name = None
original_mesh = None
if obj.data and hasattr(obj.data, 'name'):
    original_mesh = obj.data
    original_mesh_name = obj.data.name

# ... duplicate object ...

# v0.1.14: MESH DATA NAME-SWAP STRATEGY
if original_mesh_name and dup_obj.data and dup_obj.data != original_mesh:
    dup_mesh = dup_obj.data
    
    # Rename original mesh data to hidden name
    hidden_mesh_name = f"__USDME_MESH_{original_mesh_name}"
    original_mesh.name = hidden_mesh_name
    
    # Rename duplicate mesh data to original name
    dup_mesh.name = original_mesh_name
    
    # Track for cleanup
    mesh_swaps[hidden_mesh_name] = {
        'original_name': original_mesh_name,
        'original_mesh': original_mesh,
        'dup_mesh': dup_mesh
    }
```

**Cleanup Implementation**:

```python
# v0.1.14: Restore mesh data names during cleanup
for hidden_mesh_name, swap_info in mesh_swaps_for_cleanup.items():
    original_mesh_name = swap_info.get('original_name')
    mesh_ref = bpy.data.meshes.get(hidden_mesh_name)
    if mesh_ref:
        mesh_ref.name = original_mesh_name
```

**Acceptance Criteria**:
- [x] Mesh prim names remain consistent across multiple exports
- [x] No incrementing suffixes on mesh prims
- [x] Original mesh data names preserved in Blender after export
- [x] Cleanup restores mesh data names correctly
- [x] Works with all modifier types

**Estimated Effort**: 1-2 hours

---

### Phase 9: Disabled Modifier Skipping (v0.1.15 - IMPLEMENTED)
**Status**: ✅ IMPLEMENTED  
**Date**: 25 January 2026  
**Discovery Reference**: See `00_Discovery.md` - "Session: Disabled Modifier Skipping"

**Problem Identified**:

After adding the "Edit Modifiers" button, modifiers were being exported even when they were completely disabled (all visibility toggles off). This violated user intent - disabled modifiers should not affect the export.

**Root Cause**:

The v0.1.13 fix forced `show_viewport=True` on all modifiers before applying, but it didn't check if the modifier was intentionally disabled. If a user had turned off both `show_viewport` AND `show_render`, the modifier should be skipped entirely.

**Blender Modifier Visibility Toggles**:

| Property | Icon | Purpose |
|----------|------|---------|
| `show_in_editmode` | Triangle/verts | Show modifier effect in Edit Mode |
| `show_on_cage` | Box-with-verts | Edit the cage using modifier result |
| `show_viewport` | Monitor | Show modifier in 3D Viewport |
| `show_render` | Camera | Include modifier in final renders |

**Solution**:

Added `should_apply_modifier()` helper function that checks modifier visibility state:
- **Skip if BOTH `show_render` AND `show_viewport` are False** - Modifier is intentionally disabled
- **Apply if EITHER `show_render` OR `show_viewport` is True** - User wants modifier visible somewhere

**Implementation**:

```python
def should_apply_modifier(mod, logger=None, start point_context=None):
    """Check if modifier should be applied during export.
    
    v0.1.15: Skip modifiers that are intentionally disabled.
    A modifier is considered disabled if BOTH show_render AND show_viewport are False.
    """
    if not mod.show_render and not mod.show_viewport:
        # Log skipped modifier
        logger.log_step("modifier_skipped_disabled", {
            "modifier_name": mod.name,
            "modifier_type": mod.type,
            "reason": "Both show_render and show_viewport are False"
        })
        return False
    return True
```

**Updated All 4 Modifier Loops**:

```python
for mod in list(dup_obj.modifiers):
    if mod.type == 'SUBSURF':
        # v0.1.15: Skip intentionally disabled modifiers
        if not should_apply_modifier(mod, logger, start point_context):
            continue
        
        # Existing v0.1.13 logic: force visibility for modifiers we ARE applying
        ensure_modifier_visibility(mod, logger, start point_context)
        # ... apply modifier
```

**Acceptance Criteria**:
- [x] Modifiers with both `show_render=False` and `show_viewport=False` are skipped
- [x] Modifiers with only `show_viewport=True` are applied
- [x] Modifiers with only `show_render=True` are applied
- [x] Modifiers with both enabled are applied
- [x] Skipped modifiers are logged with reason
- [x] Works for all modifier types (SUBSURF, SHRINKWRAP, ARRAY, etc.)

**Estimated Effort**: 1 hour

---

### Phase 10: Unified Modifier Export (v0.1.16 - IMPLEMENTED)
**Status**: ✅ IMPLEMENTED  
**Date**: 25 January 2026  
**Discovery Reference**: See `00_Discovery.md` - "Session: Unified Modifier Export"

**Problem Identified**:

After adding the "Export Modifiers" checkbox, there was a logical inconsistency:
- Subdivision (SUBSURF) is a modifier type
- Two separate checkboxes existed: "Export Subdivision" (legacy) and "Export Modifiers" (new)
- If user unchecked "Export Subdivision" but checked "Export Modifiers", subdivisions were NOT exported
- This violated the principle that "Export Modifiers" should include ALL modifiers

**Root Cause**:

The `export_subdivision` checkbox was a legacy feature from before unified modifier export was implemented. Subdivision was treated as a special case separate from other modifiers, creating confusion and inconsistent behavior.

**Solution**:

Removed the legacy `export_subdivision` checkbox and unified all modifier export under the single "Export Modifiers" checkbox:

1. **Removed** `export_subdivision` property from `props.py`
2. **Removed** "Export Subdivision" UI checkbox from `ui.py`
3. **Updated** all logic to use `export_modifiers` for ALL modifiers (including SUBSURF)
4. **Unified** SUBSURF modifiers as part of general modifier export
5. **Maintained** order: SUBSURF modifiers applied first (bottom of stack), then other modifiers

**Implementation**:

```python
# Before (v0.1.15): Separate checks
if start point.export_subdivision:
    # Apply SUBSURF modifiers
if start point.export_modifiers:
    # Apply other modifiers

# After (v0.1.16): Unified check
if start point.export_modifiers:
    # Apply ALL modifiers (SUBSURF first, then others)
    subsurf_modifiers = [mod for mod in dup_obj.modifiers if mod.type == 'SUBSURF']
    other_modifiers = [mod for mod in dup_obj.modifiers if mod.type != 'SUBSURF']
    
    # Apply SUBSURF first, then others
    for mod in list(subsurf_modifiers):
        # ... apply modifier
    for mod in list(other_modifiers):
        # ... apply modifier
```

**Acceptance Criteria**:
- [x] "Export Subdivision" checkbox removed from UI
- [x] `export_subdivision` property removed from props
- [x] When "Export Modifiers" is checked, subdivisions are exported
- [x] All modifier types (including SUBSURF) handled by single checkbox
- [x] No confusion about which modifiers are exported
- [x] Cleaner, more intuitive UI

**Estimated Effort**: 1 hour

---

### Phase 11: Unified OBJECT/COLLECTION Duplication Strategy (v0.1.17 - IMPLEMENTED)
**Status**: ✅ IMPLEMENTED  
**Date**: 25 January 2026  
**Discovery Reference**: See `00_Discovery.md` - "Session: Leftover Duplicate Objects"

**Problem Identified**:

After failed exports, duplicate objects with `_dup1` suffixes were left behind in the scene. The original object was renamed to `__USDME_ORIG_*` but never restored.

**Root Cause**:
- OBJECT type start points used a different duplication strategy than COLLECTION type
- OBJECT type created duplicates with `_dup1` suffixes instead of using name-swap
- If export failed before cleanup, duplicates remained with `_dup1` names
- Original objects remained renamed to `__USDME_ORIG_*`

**Solution**:
- Unified OBJECT and COLLECTION types to use the same name-swap strategy
- OBJECT type now renames original to `__USDME_ORIG_*` first, then duplicate gets original name
- Added automatic cleanup of leftover objects at export start
- Restores any `__USDME_ORIG_*` objects from previous failed exports
- Deletes any leftover `_dup*` objects from old versions

**Implementation Details**:

1. **Updated OBJECT Type Duplication** (`ops_export.py`):
   ```python
   # Before: Created duplicates with _dup1 suffix
   sanitized_dup_name = self._build_duplicate_name(obj.name, duplicate_counter)
   dup_obj.name = sanitized_dup_name
   
   # After: Use name-swap strategy (same as COLLECTION)
   original_name = obj.name
   hidden_name = f"__USDME_ORIG_{original_name}"
   obj.name = hidden_name  # Free up original name
   bpy.ops.object.duplicate(linked=False)
   dup_obj = context.view_layer.objects.active
   dup_obj.name = original_name  # Duplicate gets original name
   ```

2. **Added Leftover Cleanup** (`ops_export.py`):
   ```python
   # Clean up any leftover objects from previous failed exports
   for obj_name in list(bpy.data.objects.keys()):
       if obj_name.startswith("__USDME_ORIG_"):
           # Try to restore original name
           original_name = obj_name.replace("__USDME_ORIG_", "", 1)
           if original_name not in bpy.data.objects:
               obj.name = original_name
   
   # Also clean up any _dup* objects
   for obj_name in list(bpy.data.objects.keys()):
       if "_dup" in obj_name and obj_name.endswith(("_dup1", "_dup2", ...)):
           bpy.data.objects.remove(obj)
   ```

3. **Added Name Swaps Tracking**:
   - Added `name_swaps_for_cleanup` dictionary
   - Store name swaps for cleanup after isolation context exits
   - Track both OBJECT and COLLECTION type name swaps

**Acceptance Criteria**:
- [x] OBJECT type uses name-swap strategy (same as COLLECTION)
- [x] Duplicates have original names (not `_dup1` suffixes)
- [x] Leftover objects from failed exports are cleaned up automatically
- [x] Both OBJECT and COLLECTION types use consistent duplication logic
- [x] No leftover `_dup*` objects remain after export

**Estimated Effort**: 2 hours

---

### Phase 12: Modifier Stack Order Preservation (v0.1.18 - IMPLEMENTED)
**Status**: ✅ IMPLEMENTED  
**Date**: 25 January 2026  
**Discovery Reference**: See `00_Discovery.md` - "Session: Modifier Stack Order"

**Problem Identified**:

Modifiers were being applied in the wrong order. The code applied SUBSURF modifiers first, then other modifiers, breaking the modifier stack order. This caused incorrect geometry results (e.g., Mirror modifier applied after Subdivision, causing gaps at center line).

**Root Cause**:
- Code separated modifiers by type (SUBSURF vs others)
- Applied SUBSURF modifiers first, then others
- This ignored the modifier stack order, which is critical in Blender
- Modifiers must be applied top-to-bottom as they appear in the stack

**Solution**:
- Changed modifier application to respect stack order
- Iterate through `dup_obj.modifiers` directly (gives modifiers in stack order)
- Apply modifiers in the order they appear (top to bottom)
- Removed type-based separation logic

**Implementation Details**:

1. **Updated Modifier Application** (`ops_export.py` - OBJECT type):
   ```python
   # Before: Applied SUBSURF first, then others (WRONG ORDER)
   subsurf_modifiers = [mod for mod in dup_obj.modifiers if mod.type == 'SUBSURF']
   other_modifiers = [mod for mod in dup_obj.modifiers if mod.type != 'SUBSURF']
   
   for mod in list(subsurf_modifiers):
       bpy.ops.object.modifier_apply(modifier=mod.name)
   for mod in list(other_modifiers):
       bpy.ops.object.modifier_apply(modifier=mod.name)
   
   # After: Apply in stack order (top to bottom)
   for mod in list(dup_obj.modifiers):  # Stack order preserved
       if not should_apply_modifier(mod, logger, start point_context):
           continue
       # ... apply modifier ...
   ```

2. **Same Fix for COLLECTION Type**:
   - Applied identical change to COLLECTION type modifier application
   - Both types now respect stack order

**Acceptance Criteria**:
- [x] Modifiers applied in stack order (top to bottom)
- [x] No type-based reordering
- [x] Mirror modifier (top) applies before Subdivision (below)
- [x] Geometry results match Blender viewport
- [x] Works for both OBJECT and COLLECTION types

**Known Issues**:
- ⚠️ **Selection and Mask Issues**: During testing, there were issues with selections and masks of selections that may affect modifier application. This issue is unresolved and should be investigated if similar problems occur in the future. The modifier stack order fix resolved the immediate problem, but selection/mask issues may need separate attention.

**Estimated Effort**: 1 hour

---

### Phase 13: Unit Conversion and Y-Up Axis (v0.1.19-v0.1.22 - IMPLEMENTED)
**Status**: ✅ IMPLEMENTED  
**Date**: 26 January 2026  
**Discovery Reference**: See `00_Discovery.md` - "Session: Unit Conversion and Y-Up Axis"

**Problem Identified**:

Users needed ability to:
1. Convert between metric units (mm → m, mm → cm, etc.) during export
2. Convert from Blender's Z-up coordinate system to Y-up for Omniverse compatibility

**Solution Implemented (v0.1.19-v0.1.20)**:

**1. Unit Conversion System** (`props.py`):
- Added `source_unit` EnumProperty (MILLIMETERS, CENTIMETERS, METERS, KILOMETERS)
- Added `target_unit` EnumProperty (same options)
- Added `detect_source_unit(context)` method for auto-detection from Blender scene settings
- Added `get_scale_factor()` method for unit conversion calculation

**2. Y-Up Axis Conversion** (`props.py`):
- Added `y_is_up` BoolProperty for Omniverse compatibility
- When enabled, applies -90° X rotation and transforms locations: `(x, y, z) → (x, z, -y)`

**3. Export Integration** (`ops_export.py`):
- Unit scale factor applied to `obj.location` only (not `obj.scale`)
- Y-up transformation applied to location and rotation matrices

**UI Updates (v0.1.21)**:
- Fixed unit labels to use standard abbreviations (mm, cm, m, km)

**xformOp:scale Fix (v0.1.22)**:
- Fixed issue where `xformOp:scale` was being set to `(0.001, 0.001, 0.001)` instead of `(1,1,1)`
- Root cause: Scale factor was incorrectly applied to `obj.scale`
- Solution: Scale factor applied ONLY to `obj.location`

**Acceptance Criteria**:
- [x] Unit conversion from source to target unit works correctly
- [x] Auto-detection of source unit from Blender scene settings
- [x] Y-up axis conversion transforms objects correctly
- [x] `xformOp:scale` remains `(1,1,1)` in exported USD
- [x] UI shows correct unit abbreviations

**Estimated Effort**: 3 hours

---

### Phase 14: Two-Step USD Bake Pipeline (Planned)
**Status**: 🟡 PLANNED  
**Date**: 03 February 2026  
**Discovery Reference**: See `99_HANDOFF.md` - "CRITICAL: USD Unit/Axis Conversion Challenge"

**Problem Identified**:

We need a deterministic pipeline that produces USD files with:
1. Correct scale (meters → cm/mm/km as chosen)
2. Correct up-axis (Z-up → Y-up for Omniverse)
3. **No Omniverse Resolve transforms** (clean files)

Current xformOp approaches do not consistently apply in Omniverse, so transforms must be baked into geometry.

**Strategy Overview (Two-Step Approach)**:

**Step 1 - Clean Blender Export (Baseline)**:
- Export USD from Blender as-is (meters, Z-up)
- No pre-export scale or rotation in Blender
- Preserve Blender scene state

**Step 2 - Post-Process USD Bake (Outside Blender)**:
- Apply scale + rotation directly to mesh point data
- Rotate normals only (do not scale), normalize after rotation
- Set `metersPerUnit` and `upAxis` to match baked geometry
- Clear xformOps on affected prims to keep file clean

**Implementation Plan**:

**Phase 14A: Minimal Bake Prototype (Single Mesh)**
1. Create a standalone Python script using `pxr` (Usd, UsdGeom, Gf).
2. Inputs: USD file, target unit, target up-axis.
3. Compute bake matrix:
   - Rotation: -90 degrees around X (Z-up → Y-up)
   - Scale: based on source/target unit conversion
4. Apply bake matrix to:
   - `UsdGeom.Mesh.points`
   - `UsdGeom.Mesh.normals` (rotation only)
5. Set stage metadata:
   - `UsdGeom.SetStageMetersPerUnit(stage, target_meters_per_unit)`
   - `UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)`
6. Save a new USD file (do not overwrite yet).

**Phase 14B: Full Bake Function (Multi-Mesh + Safety)**
1. Traverse stage and process all mesh prims.
2. Handle shared mesh data or instancing (duplicate data as needed).
3. Handle time-sampled points/normals (if authored).
4. Recompute or clear `extent` if present.
5. Clear xformOps on processed prims (and/or root prim).
6. Add logging and error reporting for each processed prim.

**Phase 14C: Integration Path Decision**
Choose one of:
1. **External Post-Process Script**:
   - Export USD from Blender, run bake script, write baked file.
   - Safer, avoids Blender dependencies, easier to test.
2. **Addon Post-Export Step**:
   - Call bake function from `ops_export.py` after export.
   - Keep output path behavior consistent in UI.

**Phase 14D: Collection Normalization & Pivot Controls (Planned)**
1. Add Collection-only normalization options:
   - Normalize Position (bake translation into geometry)
   - Normalize Scale (apply scale to 1.0)
   - Normalize Rotation (apply rotation to 0; bake into geometry)
2. Add Collection pivot source selection:
   - World Origin (0,0,0)
   - Custom XYZ
   - 3D Cursor
   - Object Pivot (Fake Parent reference)
3. Implement a non-destructive pre-export normalization pass:
   - Apply normalization in a temporary export context
   - Restore scene state after export (success or failure)
4. Keep USD bake pipeline identical for OBJECT and COLLECTION:
   - Blender export produces consistent transforms
   - Post-process bake runs uniformly on all start points
5. Update UI with clear tooltips and dependency rules:
   - Show XYZ fields only for Custom XYZ
   - Show object picker only for Object Pivot
6. Add pivot-only mode for Collections:
   - Allow pivot definition without normalization
   - Preserve transforms relative to pivot for external bake
7. Add Object pivot normalization toggle (off by default):
   - Normalize object pivot to origin when enabled
   - Keep non-destructive state restoration
8. Add usage guidance tooltips:
   - Collections = bulk export with pivot selection
   - Objects = single explicit asset export

**Quick-Fix (Immediate Path)**:
- Use Blender's built-in **Apply Transform** + **Set Origin** tools on **temporary duplicates** during export.
- This makes the existing UI toggles (`normalize_position`, `normalize_scale`, `normalize_rotation`, and pivot source) functional without re-enabling the fake-parent system.
- Full step-by-step implementation lives in `22_IMPLEMENTATION_PLAN_CLEAN_Phase_14D.md` (Phase 3.0).

**Acceptance Criteria**:
- [ ] Omniverse shows **no Resolve transforms** (ScaleunitsResolve/RotateunitsResolve = 0)
- [ ] Geometry size matches target units
- [ ] Orientation is correct in Y-up
- [ ] Object positions are preserved (no world-space drift)
- [ ] Normals render correctly (no shading artifacts)
- [ ] No xformOps needed for final USD files

**Estimated Effort**:
- Phase 14A: 2-3 hours
- Phase 14B: 4-6 hours
- Phase 14C: 2 hours

**Phase 14E: Bake Rotation Fix (v0.1.52)**
1. Update USD bake rotation to -90° around X for Z-up → Y-up conversion.
2. Rebuild extension and verify orientation/normals in Omniverse.
3. Refresh documentation timestamps and notes for v0.1.52.

---

### Phase 15: OBJECT Export Selection Fix (v0.1.23-v0.1.27 - IMPLEMENTED)
**Status**: ✅ IMPLEMENTED  
**Date**: 26 January 2026  
**Discovery Reference**: See `00_Discovery.md` - "Session: OBJECT Type Export - Selection Bug"

**Problem Identified**:

After adding unit conversion (v0.1.20), OBJECT type start point exports produced USD files with no geometry. The bug reports showed `selected_objects_count=0` - Blender's USD exporter was not seeing any selected objects.

**Root Cause Analysis**:

Multiple iterations revealed the core issue: **Objects must be visible to be selected in Blender.**

The original selection logic was:
1. Hide all objects
2. Show and select target objects
3. Export

This failed because `select_set(True)` silently fails on hidden objects.

**Solution Implemented (v0.1.27) - Complete Selection Logic Rewrite**:

New selection logic order:
1. **Deselect all objects** (while they are still visible)
2. **Ensure target objects are visible and selected** (unhide, set active, select)
3. **Force view layer update**
4. **THEN hide all non-target objects** (after selection is complete)

```python
# Step 1: Deselect all objects (while they're still visible)
for obj in context.view_layer.objects:
    try:
        obj.select_set(False)
    except:
        pass

# Step 2: Ensure target objects are visible, selected, and one is active
first_obj_set = False
for obj_name in object_names_to_export:
    if obj_name in context.view_layer.objects:
        view_layer_obj = context.view_layer.objects[obj_name]
        view_layer_obj.hide_viewport = False
        view_layer_obj.hide_set(False)
        if not first_obj_set:
            context.view_layer.objects.active = view_layer_obj
            first_obj_set = True
        view_layer_obj.select_set(True)

# Step 3: Force view layer update
context.view_layer.update()

# Step 4: NOW hide all other objects (after selection is done)
for obj in context.view_layer.objects:
    if obj.name not in object_names_to_export:
        try:
            obj.hide_viewport = True
        except:
            pass
```

**Key Changes**:
- Complete rewrite of selection logic in `ops_export.py`
- Added `selection_verification` log step for debugging
- Objects are now deselected first (while visible), then targets are unhidden and selected, then non-targets are hidden

**Acceptance Criteria**:
- [x] OBJECT type start points export geometry correctly
- [x] Selection logic works reliably with previously hidden objects
- [x] Unit conversion applies correctly to object location
- [x] Y-up axis conversion works correctly
- [x] Selection verification logging added for debugging

**Estimated Effort**: 4 hours (multiple debugging iterations)

---

## 🏗️ Architecture & Technical Decisions

### Core Design Principles

1. **Non-Intrusive**: Addon doesn't modify global Blender settings
2. **Safe State Management**: All scene modifications are temporary and reversible
3. **Comprehensive Error Handling**: Graceful failure with actionable user feedback
4. **Blender API Compliance**: Strict adherence to Blender 5.0+ conventions
5. **Extensible Architecture**: Modular design allowing future enhancements

### Key Technical Components

#### State Isolation System
```python
# Core pattern for safe exports
with ScopedIsolation(context, target_collection) as isolation:
    # Export operations here
    # State automatically restored on exit
    pass
```

#### Logging Integration
```python
# Comprehensive operation tracking
logger.start_operation("batch_export", context)
# ... operations ...
logger.end_operation(success=True, result_info)
```

#### Error Recovery
```python
# Safe batch operations with rollback
with state_mgr.safe_batch_operation():
    # Operations that might fail
    # Automatic rollback on exceptions
```

### Blender API Integration
- **Property System**: Uses `bpy.props` for type-safe data storage
- **Operator System**: Proper `bl_idname` registration and poll methods
- **UI System**: Panel integration with proper context and layout
- **State Management**: Scene data persistence across sessions

---

## 📊 Code Quality Metrics

### Files Created/Modified
- **New Files**: 6 Python modules (650+ lines total)
- **Documentation**: 1 comprehensive testing plan (475 lines)
- **Integration**: Updated README.md with testing plan reference

### Code Quality Standards
- ✅ **Python Type Hints**: Comprehensive type annotations
- ✅ **Error Handling**: Try/catch blocks with proper exception types
- ✅ **Documentation**: Docstrings for all classes and methods
- ✅ **Linting**: All files pass Python linting checks
- ✅ **Modular Design**: Single responsibility principle followed

### Testing Readiness
- ✅ **Unit Testable**: Modular functions with clear interfaces
- ✅ **Logging Coverage**: All operations tracked with timestamps
- ✅ **Error Scenarios**: Known failure modes documented
- ✅ **Bug Reports**: Automated JSON generation with full context

---

## 🎯 Project Status & Next Steps

### Current Status (v0.1.3 MVP)
**Development Phase**: ✅ **MVP COMPLETE - Ready for Initial Testing**
- Functional addon with core start point-based export workflow
- Safe scene state management and automatic restoration
- Comprehensive error handling and logging system
- Cross-platform path resolution and validation
- Automated bug report generation for debugging
- Testing framework and procedures documented

### MVP Approach Decision
**Why MVP for v0.1.3**: Focus on validating the core concept before investing in advanced features
- **Risk Mitigation**: Prove basic functionality works before adding complexity
- **User Feedback**: Get real-world testing feedback to guide feature priorities
- **Incremental Development**: Build confidence with working core, then enhance based on needs
- **Quality Focus**: Ensure solid foundation before adding advanced USD manipulation features

### Completed in v0.1.3 MVP ✅
1. **Start point Management**: Add/remove start points with basic properties
   - ✅ Add start point with auto-detection (collection/object from context)
   - ⚠️ Remove start point (removes last only, no dropdown selection)
2. **State Management**: ScopedIsolation + StateManager for safe exports
   - ✅ `ScopedIsolation` context manager implemented
   - ✅ `StateManager` with batch operation support
3. **Basic USD Export**: Functional export using Blender's native exporter
   - ✅ Hardcoded export parameters (materials, uvmaps, normals, animation, lights)
   - ✅ Root prim path generation (sanitized from start point name)
   - ⚠️ No per-start point export option overrides
4. **Path Resolution**: Cross-platform PathResolver for file handling
   - ✅ Full `PathResolver` class implementation
   - ✅ Relative/absolute path conversion
   - ✅ Directory auto-creation
5. **Logging System**: Comprehensive logging with verbose mode & bug reports
   - ✅ `USDME_Logger` class with file rotation
   - ✅ Bug report generation (JSON format)
   - ✅ Performance timers and context tracking
6. **UI Framework**: Functional panel with export controls
   - ✅ Main panel in Scene Properties
   - ✅ Start point list with inline editing
   - ✅ Type selector (Collection/Object) with visual indicators
   - ✅ Selection tracking button per start point
   - ✅ Verbose logging toggle
7. **Error Handling**: Critical runtime fixes from peer review
   - ✅ Pre-flight validation before export
   - ✅ Type-specific error messages
   - ✅ Comprehensive error logging
8. **Testing Framework**: Complete testing plan and procedures
   - ✅ `05_Testing_Plan.md` created
9. **Subdivision Export**: NVIDIA pattern with duplicate preservation (fix applied 2025-12-28)
   - ✅ Duplicate objects before applying modifiers
   - ✅ Clean up duplicates after export
   - ✅ Works for both Collection and Object types
10. **Origin Metadata**: Custom attributes tracking export origin
    - ✅ `usdme:origin_file`, `usdme:origin_filename`, `usdme:origin_username`, `usdme:origin_computer`, `usdme:export_timestamp`
    - ✅ Graceful handling if pxr API unavailable
11. **Light Exclusion**: Automatic light exclusion from exports
    - ✅ `export_lights=False` in export parameters
    - ✅ Additional deselection of lights before export
12. **Auto-Naming**: Start point names automatically match collection/object names
13. **Subfolder Creation**: Auto-create USD_Start point subfolder with target name
14. **Addon Preferences**: Log level control and default export settings

### Planned for Future Versions (NOT in v0.1.3) 🔄
**Reference**: See `09_Roadmap.md` for comprehensive feature breakdown and implementation phases.
**Cross-Platform Pattern Reference**: `Master_Rules/080_Framework_RULES/documentation/usd_multiexport_uix_pattern.md`
**Architecture Alignment**: Future versions should follow the Rhino USD Multi Export plan's phased approach for bidirectional capabilities.

**v0.2.0 - Cross-Platform UI Pattern Alignment + Core Export Options** (Priority 0 - NEXT):
Per `Master_Rules/080_Framework_RULES/documentation/usd_multiexport_uix_pattern.md`, the following features are required:

| Feature | Current Status | Priority | Implementation |
|---------|---------------|----------|----------------|
| Selective Export | ✅ Implemented | - | Enable/disable checkbox + Export Start points |
| Unit Conversion | ✅ Implemented (v0.1.20) | - | Source/target unit selection |
| Y-Up Axis | ✅ Implemented (v0.1.20) | - | Y-is-up checkbox |
| OBJECT Export | ✅ Implemented (v0.1.27) | - | Selection fix |
| Progress Bar | ❌ Missing | HIGH | Add progress feedback during export |
| Remove Selection-Based | ⚠️ Last only | MEDIUM | Change to remove selected start point |
| Export Results Summary | ❌ Missing | MEDIUM | Add summary popup after export |
| Keyboard Shortcuts | ❌ Missing | LOW | Add key handlers (v0.2.0+) |

**Note**: Selective export is already implemented via the enable/disable checkbox per start point. Users enable the start points they want to export and click "Export Start points".

**Tasks for v0.2.0**:
1. **Add progress bar during export** (`ops_export.py`, `ui.py`)
   - [ ] Use Blender's `wm.progress_begin()` / `wm.progress_update()` / `wm.progress_end()`
   - [ ] Show "Exporting start point X of Y..." in status bar
   - [ ] Update progress per start point completion

2. **Fix Remove to work on selection** (`ui.py`)
   - [ ] Add `active_start point_index` property to scene settings
   - [ ] Change Remove operator to use active index (not last)
   - [ ] Add selection highlighting to start point list
   - [ ] Update `USDME_OT_remove_start point` to remove at active index

3. **Add export results summary** (`ops_export.py`)
   - [ ] Collect export results (success/failure per start point)
   - [ ] Show summary popup after batch export completes
   - [ ] Display: start points exported, files created, errors encountered

4. **Version-Aware Compatibility Wrapper** - CRITICAL FIRST STEP for Blender 5.0 API compatibility

**Acceptance Criteria (v0.2.0)**:
- [ ] Progress bar visible during export
- [ ] Remove works on selected start point (not just last)
- [ ] Export results summary shown after completion
- [ ] Version-aware wrapper for export parameters

**Estimated Time**: 5-6 hours

---

**v0.2.1+ - Core Export Options** (Priority 1 - Following Rhino Plan Phases):
1. **General Export Settings** - Forward/Up Axis, Selection/Visible Only, Convert Orientation, External Items
3. **Stage Configuration** - Default Prim Path, Material Prim Path
4. **Export Type Selection** - Transforms, Meshes, Materials, Lights, Cameras, Curves
5. **Basic Geometry Options** - Subdivision Scheme, Color Attributes, Mesh Attributes, Normals, UV Maps
6. **Material Export Options** - USD Preview Surface, Texture Export Options

**v0.3.0 - Advanced Geometry & Materials** (Priority 2):
1. **Advanced Geometry Options** - Convert UV to ST, Triangulate Meshes, Quad/N-gon Methods
2. **Material Export Options** - Cycles Shaders, MDL Conversion, USDZ Texture Options
3. **Light Export Options** - Intensity Scale, Unit Conversion, Radius Scaling, World Material

**v0.4.0 - Animation & Rigging + ComfyUI Pull Capabilities** (Priority 3 - Following Rhino Plan Phase 3):
1. **Animation Export** - Frame Range Controls, Animation Toggle
2. **Rigging Support** - Armatures, Deform Bones, Shape Keys
3. **Particles & Instancing** - Particles, Hair, Child Particles
4. **ComfyUI Pull Capabilities** (Bidirectional Execution) - **NEW: Following Rhino Plan approach**
   - Enable ComfyUI to trigger Blender exports dynamically
   - Move beyond MVP push model to full bidirectional integration
   - ComfyUI nodes can execute Blender in background mode with addon enabled
   - Export start points based on ComfyUI workflow parameters
   - Real-time export status monitoring and feedback
   - Export option overrides from ComfyUI workflow

**v0.5.0+ - Workflow Enhancements** (Priority 4):
1. **Export Presets** - Predefined and user-defined presets
2. **Preset Management UI** - Create, edit, delete, import/export presets
3. **Enhanced Validation** - Pre-flight checks and warnings
4. **Batch Operations** - Improved batch export with progress tracking

**Future ComfyUI Bidirectional Integration** (Following Rhino Plan Phase 3):
The Rhino plan defines a comprehensive approach for bidirectional ComfyUI integration that should be adapted for Blender:

**1. Blender Command-Line Execution Integration**
- ComfyUI node executes Blender in background mode with addon enabled
- Use Blender `--background` flag for headless execution
- Enable addon via command-line or Python script
- Pass start point selection and export options as parameters
- Handle Blender execution timeout and capture output for debugging

**2. Start point-Based Export Execution from ComfyUI**
- ComfyUI node reads start point definitions from .blend file
- Dynamic start point selection based on workflow logic
- Export status monitoring with progress feedback
- Error handling and reporting to ComfyUI
- Automatic loading of exported USD files into ComfyUI workflow

**3. Export Options Integration**
- Override per-start point export settings from ComfyUI
- Support export preset selection from ComfyUI
- Pass export parameters as workflow inputs
- Maintain consistency with Blender's native export options

**Benefits of Bidirectional Approach** (As defined in Rhino Plan):
- **Workflow-Driven Exports**: ComfyUI workflows can trigger exports based on conditions
- **Automated Pipelines**: End-to-end automation from export to processing
- **Dynamic Selection**: Export different start points based on workflow state
- **Tight Integration**: Seamless integration between Blender and ComfyUI

**Reference**: See `Rhino_USD_MultiExport/04_Implementation_Plan.md` Section "Phase 3: ComfyUI Bidirectional Integration" for detailed implementation approach

### Risk Assessment
- **Low Risk**: Core architecture stable and well-tested
- **High Risk**: Blender 5.0 USD export API parameter changes - **Mitigation**: Version-aware compatibility wrapper (see Roadmap Section 12.1)
- **Low Risk**: State management thoroughly implemented and tested
- **Low Risk**: Error handling comprehensive with actionable feedback
- **Medium Risk**: UI complexity with many export options - **Mitigation**: Presets, collapsible sections (see Roadmap Section 12.3)

---

## 📈 Success Metrics

### Technical Achievements
- **0 Runtime Errors**: All critical issues from peer review resolved
- **100% API Compliance**: Proper Blender operator and property usage
- **Complete State Safety**: No permanent scene modifications
- **Comprehensive Logging**: Full operation traceability

### Quality Assurance
- **6-Phase Testing Plan**: Complete validation procedures documented
- **Automated Bug Reports**: JSON format with all debugging context
- **Peer Review Integration**: Critical issues identified and fixed
- **Documentation Complete**: All components thoroughly documented

### Development Velocity
- **Single Session**: Complete transformation from planning to functional addon
- **Zero Breaking Changes**: All fixes backward compatible
- **Immediate Testability**: Addon ready for Blender 5.0 testing

---

## 🔗 References & Dependencies

### Project Documentation
- `01_Requirements_Questionnaire.md` - Original requirements gathering (Active reference)
- `02_Detailed_Requirements.md` - Detailed specifications (Active reference)
- `03_Module_Design.md` - Architecture documentation (Active reference)
- `05_Testing_Plan.md` - Testing procedures and validation
- `09_Roadmap.md` - Comprehensive feature roadmap for v0.2.0+ (Active reference)

### External Dependencies
- **Blender 5.0+**: Core platform and USD export functionality
- **Python 3.11+**: Runtime environment (bundled with Blender)
- **ASWF USD Guidelines**: Compliance target for USD structure

### Development Tools
- **fake-bpy-module**: IDE support for Blender API completion
- **Python Linting**: Code quality validation
- **Blender Text Editor**: Development and testing environment

---

## 📅 Future Development Phases (v0.2.0+)

### Phase 1: Core Export Options (v0.2.0)
**Timeline**: 2-3 weeks  
**Goal**: Enable per-start point control over essential export parameters  
**Reference**: `09_Roadmap.md` Section 11 - Phase 1

**Critical First Step**: Version-aware compatibility wrapper (Week 1)
- Implement version-aware USD export wrapper
- Query Blender 5.0 USD exporter RNA properties
- Build parameter filtering and rename mapping system
- Test wrapper with minimal parameters

**Features**:
1. General Export Settings (Forward/Up Axis, Selection/Visible Only, Convert Orientation, External Items)
2. Stage Configuration (Default Prim Path, Material Prim Path)
3. Export Type Selection (Transforms, Meshes, Materials, Lights, Cameras, Curves)
4. Basic Geometry Options (Subdivision Scheme, Color Attributes, Mesh Attributes, Normals, UV Maps)
5. Material Export Options (USD Preview Surface, Texture Export)

**Estimated Effort**: 20-25 hours

### Phase 2: Advanced Geometry & Materials (v0.3.0)
**Timeline**: 1-2 weeks  
**Goal**: Full control over geometry processing and material export  
**Reference**: `09_Roadmap.md` Section 11 - Phase 2

**Features**:
1. Advanced Geometry Options (Convert UV to ST, Triangulate Meshes, Quad/N-gon Methods)
2. Material Export Options (Cycles Shaders, MDL Conversion, USDZ Texture Options)
3. Light Export Options (Intensity Scale, Unit Conversion, Radius Scaling, World Material)

**Estimated Effort**: 12-15 hours

### Phase 3: Animation & Rigging + ComfyUI Pull Capabilities (v0.4.0)
**Timeline**: 2-3 weeks  
**Goal**: Support for animated exports, rigging workflows, and bidirectional ComfyUI integration  
**Reference**: `09_Roadmap.md` Section 11 - Phase 3

**Features**:
1. Animation Export (Frame Range Controls, Animation Toggle)
2. Rigging Support (Armatures, Deform Bones, Shape Keys)
3. Particles & Instancing (Particles, Hair, Child Particles)
4. **ComfyUI Pull Capabilities** (Bidirectional Execution) - See details below

**Estimated Effort**: 15-20 hours (Animation/Rigging) + 10-15 hours (ComfyUI Pull) = **25-35 hours total**

#### ComfyUI Pull Capabilities (Bidirectional Execution)

**Objective**: Enable ComfyUI to trigger Blender exports dynamically, moving beyond the MVP push model to full bidirectional integration.

**Current MVP State**:
- ✅ **Push Model**: Blender exports USD files independently, ComfyUI reads paths and loads files
- ❌ **Pull Model**: ComfyUI cannot trigger Blender exports (reserved for future)

**Future Pull Capabilities**:

**1. Blender Command-Line Execution Integration**
- **Requirement**: ComfyUI node executes Blender in background mode with addon enabled
- **Implementation**:
  - Use Blender `--background` flag for headless execution
  - Enable addon via command-line or Python script
  - Pass start point selection to export script
  - Use addon export operator: `bpy.ops.usdme.export_start points()`
  - Handle Blender execution timeout (5+ minutes for large exports)
  - Capture Blender output for debugging
- **Technical Details**:
  - Execute Blender with script: `blender --background --python export_script.py`
  - Script enables addon and calls export operator
  - Pass start point IDs/names as command-line arguments or via JSON file
  - Return export results (success/failure, file paths) to ComfyUI node
- **Estimated Effort**: 6-8 hours

**2. Start point-Based Export Execution from ComfyUI**
- **Requirement**: ComfyUI node triggers Blender exports using start point definitions
- **Implementation**:
  - Node reads start point definitions from .blend file
  - Node filters/selects start points based on workflow logic
  - Node triggers Blender export via command-line execution
  - Node waits for export completion
  - Node loads exported USD files into ComfyUI workflow
- **Use Cases**:
  - Conditional batch export based on workflow parameters
  - Dynamic start point selection based on ComfyUI workflow state
  - Automated export-then-process workflows
- **Estimated Effort**: 4-6 hours

**3. Export Status Monitoring & Feedback**
- **Requirement**: ComfyUI node monitors export progress and provides feedback
- **Implementation**:
  - Real-time export progress reporting
  - Export status tracking (Queued / Running / Success / Failed)
  - Error handling and reporting to ComfyUI
  - Export completion notification
- **Estimated Effort**: 2-3 hours

**4. Export Options Integration**
- **Requirement**: ComfyUI node can override export options when triggering exports
- **Implementation**:
  - Pass export options as parameters to Blender export script
  - Override per-start point export settings from ComfyUI
  - Support export preset selection from ComfyUI
- **Estimated Effort**: 2-3 hours

**Benefits of Pull Capabilities**:
- ✅ **Workflow-Driven Exports**: ComfyUI workflows can trigger exports based on conditions
- ✅ **Automated Pipelines**: End-to-end automation from export to processing
- ✅ **Dynamic Selection**: Export different start points based on workflow state
- ✅ **Tight Integration**: Seamless integration between Blender and ComfyUI

**Technical Challenges**:
- **Blender Execution**: Requires Blender installation accessible from ComfyUI environment
- **Addon Availability**: Addon must be installed and enabled in Blender
- **Path Resolution**: Export paths must be resolvable from ComfyUI context
- **Error Handling**: Robust error handling for Blender execution failures
- **Performance**: Export execution time may impact ComfyUI workflow responsiveness

**Dependencies**:
- Blender 5.0+ installation accessible from ComfyUI
- Addon installed and enabled in Blender
- Command-line access to Blender executable
- Python script execution capability

**Acceptance Criteria**:
- [ ] ComfyUI node can trigger Blender exports via command-line
- [ ] Start point selection works correctly from ComfyUI
- [ ] Export options can be overridden from ComfyUI
- [ ] Export progress is reported to ComfyUI
- [ ] Error handling works gracefully
- [ ] Exported files are automatically loaded into ComfyUI workflow

### Phase 4: Workflow Enhancements (v0.5.0+)
**Timeline**: 2-3 weeks  
**Goal**: Productivity features and advanced workflows  
**Reference**: `09_Roadmap.md` Section 11 - Phase 4

**Features**:
1. Export Presets (Predefined and user-defined presets)
2. Preset Management UI (Create, edit, delete, import/export)
3. Enhanced Validation (Pre-flight checks and warnings)
4. Batch Operations (Improved batch export with progress tracking)

**Estimated Effort**: 15-20 hours

---

**Consolidated Implementation Plan - Version 2.5.3**
**Date Created**: 25.11.2025
**Last Updated**: 06.02.2026 02:15 (Added REQ-EXP-028/029 Animation Export)
**Next Update**: After v0.2.0 completion

**Status**: ✅ **MVP Complete (v0.1.27)** | 🟡 **v0.2.0 Cross-Platform Alignment Pending** | 🐛 **REQ-EXP-030 Unit Bug Open** | 🔬 **Animation Export Planned**
**Cross-Platform Pattern Reference**: `Master_Rules/080_Framework_RULES/documentation/usd_multiexport_uix_pattern.md`
**Roadmap Reference**: See `09_Roadmap.md` for comprehensive feature requirements and implementation details
**Architecture Reference**: Aligned with `Rhino_USD_MultiExport/04_Implementation_Plan.md` for future bidirectional capabilities

---

## Cross-Platform UI Pattern Alignment Checklist

Per `Master_Rules/080_Framework_RULES/documentation/usd_multiexport_uix_pattern.md`:

| Pattern Requirement | Current Status | Target Version | Notes |
|---------------------|----------------|----------------|-------|
| Single Enable Checkbox | ✅ Implemented | v0.1.3 | Aligned |
| Type Icon | ✅ Implemented | v0.1.3 | Collection/Object icons |
| Status Icon | ✅ Implemented | v0.1.3 | Check/Error icons |
| Context-Aware Add | ✅ Implemented | v0.1.3 | Auto-detect from selection |
| Select Target Button | ✅ Implemented | v0.1.3 | Per-start point select |
| Export All Enabled | ✅ Implemented | v0.1.3 | Main export button |
| Selective Export | ✅ Implemented | v0.1.3 | Via enable/disable checkbox |
| **Unit Conversion** | 🐛 BUG | **v0.1.88+** | mm/cm/m/km - target unit ineffective (REQ-EXP-025) |
| **Y-Up Axis** | ✅ Implemented | **v0.1.20** | Omniverse compatibility |
| **OBJECT Export** | ✅ Implemented | **v0.1.27** | Selection bug fixed |
| **Progress Bar** | ❌ Missing | **v0.2.0** | **HIGH PRIORITY** |
| **Remove Selection-Based** | ⚠️ Last only | **v0.2.0** | Change to selected |
| **Export Results Summary** | ❌ Missing | **v0.2.0** | Add summary popup |
| **Materials→Looks Scope** | ❌ Missing | **v0.2.0** | Omniverse convention (REQ-EXP-023) |
| **Animation Export** | 🔬 Research | **v0.2.x** | REQ-EXP-028 baked per-frame |
| **Animation Layer** | 🔬 Research | **v0.2.x** | REQ-EXP-029 separate USD layer |
| Keyboard Shortcuts | ❌ Missing | v0.2.1+ | Optional |
| Cancel Export | ❌ Missing | v0.2.1+ | Future |

**Note**: Selective export is implemented via the enable/disable checkbox per start point. Users enable the start points they want to export and click "Export Start points".

---

**Implementation Review Summary (26.01.2026)**:
- ✅ Core functionality implemented and working
- ✅ State management system fully functional
- ✅ Logging and error handling comprehensive
- ✅ **Architecture Alignment**: Push model approach validated against Rhino plan
- ✅ **v0.1.11**: Name-swap strategy for consistent USD prim names
- ✅ **v0.1.11**: Complete modifier support (Shrinkwrap, Array, etc., not just Subdivision)
- ✅ **v0.1.11**: Robust cleanup with name restoration
- ✅ **v0.1.12**: Export ALL mesh objects (fixed missing objects bug)
- ✅ **v0.1.13**: Modifier visibility mode handling (force-enable `show_viewport`, expand target handling)
- ✅ **v0.1.14**: Mesh data name consistency (name-swap strategy for mesh data blocks)
- ✅ **v0.1.19-v0.1.20**: Unit conversion system (mm, cm, m, km) with auto-detection
- ✅ **v0.1.19-v0.1.20**: Y-up axis conversion for Omniverse compatibility
- ✅ **v0.1.22**: xformOp:scale fix (scale=1,1,1 in USD)
- ✅ **v0.1.27**: OBJECT export selection bug fix (complete rewrite of selection logic)
- ✅ **Selective Export**: Enable/disable checkbox per start point works correctly
- ⚠️ Remove start point: Basic implementation (removes last only, no dropdown selection) → **Fix in v0.2.0**
- ❌ Progress bar: NOT implemented → **Add in v0.2.0**
- ❌ Export results summary: NOT implemented → **Add in v0.2.0**
- ❌ Overwrite confirmation: NOT implemented (files overwritten silently)
- ⚠️ Export options: Hardcoded defaults only (per-start point options NOT implemented)
- ✅ All documented MVP features working as expected
- ✅ **Future Path**: ComfyUI bidirectional integration planned following Rhino Phase 3 approach
- 🟡 **Cross-Platform Pattern**: v0.2.0 will align with universal UI/UX specification

**Critical Fixes in v0.1.11-v0.1.12**:
- Fixed: Wrong names exported to USD (`_dup1` suffix issue)
- Fixed: Only some objects exported (4 of 6 missing)
- Fixed: Leftover duplicates in Blender after export
- Fixed: Shrinkwrap and other modifiers not applied
- See `00_Discovery.md` for detailed problem/solution documentation

**Fixes in v0.1.13** (Implemented):
- Fixed: Inconsistent Shrinkwrap application (sometimes works, sometimes doesn't)
- Root cause: Modifier visibility modes (`show_viewport`) not being checked before apply
- Solution: Force-enable `show_viewport` on all modifiers before applying
- Solution: Expand target object visibility handling to ALL modifier types with targets (13+ types)
- Added helper functions: `ensure_modifier_visibility()`, `ensure_modifier_target_visibility()`, `restore_target_visibility()`
- Added `MODIFIER_TARGET_PROPERTIES` constant for all modifier types with targets
- See `00_Discovery.md` - "Session: Modifier Visibility Modes Investigation" for details

**Fixes in v0.1.14** (Implemented):
- Fixed: Mesh prim names incrementing on each export (Plane_011, Plane_014, etc.)
- Root cause: Blender duplicates mesh data blocks with auto-incrementing names
- Solution: Apply name-swap strategy to mesh data blocks (not just objects)
- Added `mesh_swaps` dictionary to track mesh data name swaps during processing
- Added `mesh_swaps_for_cleanup` to persist swaps through isolation context
- Added mesh data name restoration in cleanup phase
- See `00_Discovery.md` - "Session: Mesh Data Name Consistency" for details

**Fixes in v0.1.15** (Implemented):
- Fixed: Disabled modifiers being exported despite all visibility toggles off
- Root cause: v0.1.13 forced `show_viewport=True` but didn't check if modifier was intentionally disabled
- Solution: Skip modifiers where both `show_render` AND `show_viewport` are False
- Added `should_apply_modifier()` helper function to check modifier visibility state
- Updated all 4 modifier application loops to check before applying
- Logs skipped modifiers with reason for user visibility
- See `00_Discovery.md` - "Session: Disabled Modifier Skipping" for details

**Fixes in v0.1.16** (Implemented):
- Fixed: Logical inconsistency - "Export Modifiers" didn't include subdivisions when "Export Subdivision" was unchecked
- Root cause: Legacy `export_subdivision` checkbox treated subdivision as separate from other modifiers
- Solution: Removed `export_subdivision` property and UI checkbox, unified all modifiers under `export_modifiers`
- Subdivision (SUBSURF) is now treated as just another modifier type
- When "Export Modifiers" is checked, ALL modifiers (including subdivision) are exported
- Cleaner, more intuitive UI with single checkbox
- See `00_Discovery.md` - "Session: Unified Modifier Export" for details

**Fixes in v0.1.17** (Implemented):
- Fixed: Leftover duplicate objects with `_dup1` suffixes after failed exports
- Root cause: OBJECT type used different duplication strategy than COLLECTION type, creating duplicates with `_dup1` names
- Solution: Unified OBJECT and COLLECTION types to use same name-swap strategy
- OBJECT type now renames original to `__USDME_ORIG_*` first, then duplicate gets original name
- Added automatic cleanup of leftover objects at export start
- See `00_Discovery.md` - "Session: Leftover Duplicate Objects" for details

**Fixes in v0.1.18** (Implemented):
- Fixed: Modifiers applied in wrong order (SUBSURF first, then others) breaking stack order
- Root cause: Code separated modifiers by type and applied SUBSURF first, ignoring stack order
- Solution: Changed to apply modifiers in stack order (top to bottom) as they appear
- Iterate through `dup_obj.modifiers` directly (gives modifiers in stack order)
- Removed type-based separation logic
- See `00_Discovery.md` - "Session: Modifier Stack Order" for details

**Fixes in v0.1.19-v0.1.22** (Implemented):
- **v0.1.19-v0.1.20**: Added unit conversion system (mm, cm, m, km) with auto-detection from scene settings
- **v0.1.19-v0.1.20**: Added Y-up axis conversion for Omniverse compatibility
- **v0.1.21**: Fixed UI unit labels to use standard abbreviations
- **v0.1.22**: Fixed xformOp:scale issue - scale factor applied only to location, not obj.scale
- See `00_Discovery.md` - "Session: Unit Conversion and Y-Up Axis" for details

**Fixes in v0.1.23-v0.1.27** (Implemented):
- Fixed: OBJECT type start points exported empty USD files (no geometry)
- Root cause: Objects were being hidden BEFORE selection, causing `select_set(True)` to fail silently
- Solution (v0.1.27): Complete rewrite of selection logic
  - Deselect all objects first (while visible)
  - Unhide and select target objects
  - Force view layer update
  - THEN hide non-target objects (after selection is complete)
- Added `selection_verification` log step for debugging
- See `00_Discovery.md` - "Session: OBJECT Type Export - Selection Bug" for details

**Architecture Alignment Notes**:
- **MVP Scope**: Push-only model (define paths → export → ComfyUI reads) matches Rhino plan exactly
- **Future Vision**: Bidirectional capabilities (ComfyUI triggering Blender exports) planned for v0.4.0+
- **Implementation Strategy**: Follow Rhino plan's Phase 3 approach for ComfyUI integration
- **Benefits**: Leverages proven architecture pattern from Rhino implementation

---

## 🔮 Upcoming: Normalize Scale / Normalize Rotation (disabled in UI as of v0.1.87)

**Status**: 🟡 Upcoming — UI options grayed out; export logic treats both as off.  
**Reference**: Discovery `00_Discovery.md` (Session: Collection Normalization & Pivot Strategy); WIP `80_WIP_notes.md` (v0.1.86, v0.1.85, v0.1.84).

### Why these options are disabled

Enabling **Normalize Scale** or **Normalize Rotation** for collection exports (e.g. decals) currently **breaks** the result:

1. **Symptom**: In Omniverse, child prims show wrong transform — e.g. scale ~−0.3, non-zero rotation, tiny or wrong translate. Decals appear ~100× too small or in the wrong place/orientation.
2. **Blender-side**: Pre-export `transform_apply(rotation=..., scale=...)` on the export set runs, but collection hierarchy / pivot handling can still produce inconsistent local transforms that then get written into USD.
3. **USD post-export bake**: The addon runs a post-export pass (`usd_bake.py`) that bakes each child prim’s local transform into its mesh and sets the prim’s xform to identity. For collection exports this pass produces **incorrect** results:
   - The “local” matrix used for baking may not match the actual hierarchy (e.g. default-prim scale/rotation vs child prims).
   - Mesh points may already have been scaled by `scale_factor` (unit conversion); baking again with the wrong matrix leads to double transform or wrong scale/rotation.
   - Order of operations (default-prim xform, then child xforms) and coordinate spaces (Blender vs USD, Y-up, etc.) are easy to get wrong for collection roots with many children.

So both the **Blender-side** normalize and the **USD post-pass** can contribute to the broken decals. Disabling Normalize Scale and Normalize Rotation in the UI and in export logic avoids the broken behaviour until the pipeline is fixed.

### What needs to be done (implementation plan)

- **Blender-side**: Ensure collection normalization (transform_apply with pivot/origin) produces consistent local transforms for all objects in the collection before USD export; validate with a multi-object collection (e.g. decals).
- **USD post-pass**: Revisit `usd_bake.py` child-xform normalization:
  - Compute each child prim’s local-to-world (or local) transform in the **same** space as the mesh points (after default-prim and scale_factor are applied).
  - Bake that transform into mesh points/normals, then set the prim’s xform to identity, without double-applying scale_factor or parent xform.
- **Testing**: Re-enable the UI options behind a flag or branch; test COLLECTION exports (decals) and OBJECT exports; verify in Omniverse that scale, rotation, and position match expectations.
- **Re-enable**: Once the above is validated, remove the forced `normalize_rotation = False` / `normalize_scale = False` in `_apply_collection_normalization_quickfix`, restore `normalize_child_xforms` from start point options in the bake call, and un-gray the Normalize Scale / Normalize Rotation UI.

**Links**: `00_Discovery.md` (Why Rotation/Scale Can Look Non-Normalized; Known limitation v0.1.86), `80_WIP_notes.md` (v0.1.86, v0.1.85, v0.1.84).

---

## 🎬 Animation Export Support (REQ-EXP-028, REQ-EXP-029)

**Status**: 🔬 **Research Complete / Ready for Implementation**  
**Priority**: Medium  
**Date Added**: 06.02.2026  
**Updated**: 06.02.2026 (expanded scope based on Blender 5.0 native support research)  
**Target Version**: v0.2.x+

### Overview

Animation export enables users to export animations into USD files. Two distinct capabilities are planned:

1. **REQ-EXP-028: Basic Animation Export** - Export all animation types supported by Blender's native USD exporter
2. **REQ-EXP-029: Separate Animation Layer** - Export animation to a separate USD file for composition

### Blender 5.0 Native USD Animation Support (Research Complete)

**Supported Animation Types** (pass-through to Blender's exporter):

| Animation Type | USD Type | Blender Parameter | Notes |
|----------------|----------|-------------------|-------|
| Transform (loc/rot/scale) | `xformOp` time-samples | `export_animation=True` | Baked per-frame |
| Deforming meshes | Animated points | `export_animation=True` | Cloth, soft-body |
| Topology-changing meshes | Animated topology | `export_animation=True` | Fluid sims |
| Armatures (skeletal) | UsdSkel | `export_armatures=True` | Blender 4.0+ |
| Shape keys (morph) | USD BlendShapes | `export_shapekeys=True` | Relative only |
| Animated volumes | VDB time-samples | `export_animation=True` | OpenVDB |
| Cameras | UsdGeomCamera | `export_animation=True` | FOV, transform |
| Lights | UsdLux | `export_animation=True` | Intensity, transform |
| Visibility | `visibility` attr | `export_animation=True` | Auto when animated |

**Key Finding**: Blender does NOT have parameters for custom frame range. It uses `scene.frame_start` / `scene.frame_end` directly. We must temporarily modify scene settings.

### Phase 1: Basic Animation Export (REQ-EXP-028)

**Goal**: Enable export of all animation types supported by Blender's native USD exporter.

**Implementation Tasks**:

| Task | File(s) | Description |
|------|---------|-------------|
| 1.1 | `props.py` | Add `export_animation` BoolProperty (default: `False`) |
| 1.2 | `props.py` | Add `animation_frame_range` EnumProperty (`SCENE`, `CUSTOM`) |
| 1.3 | `props.py` | Add `animation_frame_start`, `animation_frame_end` IntProperty |
| 1.4 | `props.py` | Add `export_armatures` BoolProperty (default: `True`) |
| 1.5 | `props.py` | Add `export_shapekeys` BoolProperty (default: `True`) |
| 1.6 | `props.py` | Add `only_deform_bones` BoolProperty (default: `False`) |
| 1.7 | `ui.py` | Add animation export UI section with all options |
| 1.8 | `ops_export.py` | Pass animation parameters to `bpy.ops.wm.usd_export()` |
| 1.9 | `ops_export.py` | Handle custom frame range (temp scene modification + restore) |
| 1.10 | `usd_bake.py` | Add `animation_mode` flag - skip mesh point baking when True |
| 1.11 | Test | Verify all animation types play back in Omniverse/usdview |

**Technical Considerations**:
1. **Post-process bake conflict**: When animation is enabled, `usd_bake.py` must NOT bake transforms into mesh points (destroys time-sampled animation). Add `animation_mode=True` flag.
2. **Frame range handling**: Temporarily set `scene.frame_start`/`scene.frame_end` before export, restore in `finally` block.
3. **Parameter pass-through**: Simply pass `export_armatures`, `export_shapekeys`, `only_deform_bones` to Blender's exporter.

### Phase 2: Separate Animation Layer Export (REQ-EXP-029)

**Goal**: Export animation to a separate USD file for non-destructive composition.

**Implementation Tasks**:

| Task | File(s) | Description |
|------|---------|-------------|
| 2.1 | `props.py` | Add `export_animation_separate_layer` BoolProperty |
| 2.2 | `props.py` | Add `animation_layer_suffix` StringProperty (default: `_anim`) |
| 2.3 | `props.py` | Add `generate_composition_root` BoolProperty (default: `True`) |
| 2.4 | `ops_export.py` | Implement dual-export: geometry file + animation file |
| 2.5 | `usd_bake.py` or new | Post-process animation file to use `over` specifiers |
| 2.6 | New function | Generate composition root file with sublayers |
| 2.7 | Test | Verify composed scene plays animation correctly |

**USD Pattern**:
```usda
# geometry.usd - Static geometry
def Xform "MyAsset" { ... }

# geometry_anim.usd - Animation overrides
over "MyAsset" {
    double3 xformOp:translate.timeSamples = { 1: (0,0,0), 24: (10,0,0) }
}

# geometry_composed.usd - Composition root
(
    subLayers = [ @./geometry_anim.usd@, @./geometry.usd@ ]
)
```

### Research Findings (Complete - 06.02.2026)

**Blender 5.0 Native USD Animation Support**:
- `export_animation=True` exports entire scene frame range as time-samples (not curves)
- Frame range uses `scene.frame_start` / `scene.frame_end` (no custom parameters)
- `export_armatures=True` exports armatures as UsdSkel (Blender 4.0+)
- `export_shapekeys=True` exports shape keys as USD BlendShapes
- `only_deform_bones=False` controls which bones are exported
- Supports: transform animation, deforming meshes, topology-changing meshes, volumes, cameras, lights, visibility

**Limitations** (Blender native):
- No animation curve export (baked samples only)
- Invisible objects not exported
- Absolute shape keys not supported (relative only)
- Bendy bones not supported

**Implementation Approach**: Pass-through to Blender's native exporter for all animation types. The addon only needs to:
1. Expose the relevant parameters in the UI
2. Handle custom frame range via temporary scene modification
3. Skip mesh baking in post-process when animation is enabled

**References**: See `00_Discovery.md` - "Session: Animation Export Research" for full research notes.

---

## 🐛 BUG FIX: Unit Conversion - Target Unit Selection Ineffective (REQ-EXP-025)

**Status**: 🔴 **BUG - Open**  
**Priority**: High  
**Date Reported**: 05.02.2026  
**Target Fix**: v0.1.88+

### Problem Description

When a Blender scene is set to millimeters (or other non-meter units), selecting different Target Unit options in the addon has no effect on the exported USD scale. The export always produces the same scale regardless of what target unit is chosen.

### Root Cause Analysis

Investigation (05.02.2026) identified the following issues:

1. **`source_unit` property not auto-synced with scene settings**:
   - The `source_unit` property (default: `MILLIMETERS`) is stored per start point
   - It is NOT automatically updated when the Blender scene unit changes
   - Users must manually click the "Detect" button to sync with scene settings
   - If `source_unit` is wrong, the `get_scale_factor()` calculation is incorrect

2. **Potential double-scaling conflict**:
   - Blender's built-in USD exporter (`bpy.ops.wm.usd_export()`) reads `scene.unit_settings.scale_length` and may already convert geometry to meters internally
   - Our post-process bake step (`usd_bake.py`) applies `scale_factor` to mesh points
   - If Blender already handled conversion, our additional scaling causes incorrect results

3. **Scale factor flow**:
   - `props.py`: `get_scale_factor()` returns `source_factor / target_factor`
   - `ops_export.py` line 2870-2871: `scale_factor = start_point.get_scale_factor()`
   - `usd_bake.py` line 98-99: `local_bake_matrix.SetScale(Gf.Vec3d(scale_factor, scale_factor, scale_factor))`

### Implementation Tasks

**Task 1: Add Auto-Detection at Export Time**
- **File**: `ops_export.py` (around line 2869-2871)
- **Change**: Before calling `start_point.get_scale_factor()`, auto-detect and update `source_unit`:
  ```python
  # Auto-detect source unit from scene settings at export time
  detected_unit = start_point.detect_source_unit(context)
  if detected_unit != start_point.source_unit:
      logger.log_step("source_unit_auto_corrected", {
          **start_point_context,
          "stored_value": start_point.source_unit,
          "detected_value": detected_unit,
      })
      start_point.source_unit = detected_unit
  
  scale_factor = start_point.get_scale_factor()
  ```

**Task 2: Investigate Blender USD Exporter Unit Handling**
- Determine if `bpy.ops.wm.usd_export()` already converts to meters
- If yes: Adjust our scale_factor calculation to avoid double-scaling
- If no: Our current approach should work once source_unit is correct

**Task 3: Add Logging for Debug Visibility**
- Log the actual scale_factor being applied during export
- Log detected vs stored source_unit
- Log scene's `unit_settings.scale_length` value

**Task 4: UI Warning for Mismatched Units**
- Add visual indicator in UI when `source_unit` doesn't match detected scene unit
- Consider auto-updating `source_unit` when scene units change (via `update` callback or poll)

### Acceptance Criteria

- [ ] Changing target unit produces correctly scaled USD output
- [ ] Works correctly when Blender scene is in mm, cm, m, or km
- [ ] No double-scaling occurs between Blender's exporter and our post-process
- [ ] Source unit auto-detection runs at export time
- [ ] Export logs show scale_factor being applied

### References

- **Requirement**: `02_Detailed_Requirements.md` → REQ-EXP-025
- **Code Locations**:
  - `props.py`: `detect_source_unit()`, `get_scale_factor()`, `source_unit`, `target_unit`
  - `ops_export.py`: Line ~2869-2871 (scale_factor retrieval)
  - `usd_bake.py`: Line ~98-99 (scale matrix application)

