# Blender USD Multi Export - Discovery Document

**Version**: 1.8.1 | **Date**: 02.02.2026 | **Time**: 14:01 | **GlobalID**: 20260202_1401_Blender_USD_MultiExport_Discovery

---

## Executive Summary

This document captures the problems encountered during the development and testing of the Blender USD Multi Export addon, along with the solutions implemented. It serves as a learning resource and reference for future development.

---

## Session: v0.1.52 Rotation Fix (Z-up → Y-up) + Timestamp Refresh

**Date**: 02.02.2026  
**Version**: v0.1.52

### Context
- Current exports showed wrong heading and broken normals after bake.
- A new release was prepared to address orientation.
- User requested a timestamp refresh for documentation consistency.

### Change Implemented
- `usd_bake.py`: Z-up to Y-up rotation changed to **-90° around X**.
- Release build: `blender_usd_multiexport_v0.1.52.zip`.


## Session: Modifier Export and Namespace Consistency (v0.1.10 - v0.1.12)

**Date**: 24-25 January 2026  
**Versions**: v0.1.10, v0.1.11, v0.1.12

### Context

The addon was being tested with a real production scene containing a collection of decal objects (`SHAKTI_Decals`) with various modifiers (Subdivision, Shrinkwrap). The goal was to export these objects to USD with modifiers applied (baked geometry).

### Problems Encountered

#### Problem 1: Duplicate Geometry Left Behind in Blender

**Symptoms**:
- After export, duplicate objects remained in the Blender scene
- Objects had names like `.001`, `.002` suffixes
- Scene became polluted with leftover temporary objects

**Root Cause**:
- The cleanup logic was running inside the `ScopedIsolation` context manager
- When cleanup ran, some objects were still referenced by the isolation system
- Failed cleanup left duplicates behind

**Solution (v0.1.10)**:
- Moved cleanup logic OUTSIDE the `ScopedIsolation` context
- Added `duplicated_objects_for_cleanup` list to track objects created during export
- Cleanup now runs AFTER isolation exits, ensuring all references are released

#### Problem 2: Wrong Names Exported to USD (`_dup1`, `_dup2`)

**Symptoms**:
- USD file contained prims named `SPADE_2b_Outline_Petrol_LEFT_dup1` instead of `SPADE_2b_Outline_Petrol_LEFT`
- Names in USD didn't match original Blender object names
- This breaks USD referencing workflows that rely on consistent prim paths

**Root Cause**:
- Duplicates were being renamed to `_dupN` for tracking purposes
- These renamed objects were exported with their temporary names
- No name-swap strategy was in place

**Solution (v0.1.11)**:
- Implemented **Name-Swap Strategy**:
  1. Before duplication: Rename original to `__USDME_ORIG_{name}` (hidden name)
  2. Duplicate the object (Blender gives it the original name since it's now free)
  3. Apply modifiers to duplicate
  4. Export (duplicate has clean original name)
  5. After export: Delete duplicate, rename original back to its original name
- This ensures USD prims have clean, consistent names matching the original objects

#### Problem 3: Only Some Objects Exported (4 of 6 Missing)

**Symptoms**:
- Collection had 6 objects, but only 2 appeared in USD
- Objects without SUBSURF modifiers were completely missing
- Export success was reported, but USD was incomplete

**Root Cause (First Diagnosis - Incorrect)**:
- Initial analysis assumed `.001`/`.002` objects were being incorrectly skipped
- This was wrong - the user clarified these were leftover duplicates from previous exports

**Root Cause (Correct)**:
- The export selection logic ONLY selected duplicated objects for export
- Objects that didn't need duplication (no modifiers to bake) were NOT selected
- These objects were completely excluded from the USD export

**Solution (v0.1.12)**:
- Modified export selection to include ALL mesh objects:
  1. **Duplicates** - Objects that needed modifier baking (with applied modifiers)
  2. **Originals** - Objects that DIDN'T need modifier baking (exported as-is)
- Added `objects_to_export` list that combines both categories
- All mesh objects in the collection are now exported, regardless of whether they have modifiers

#### Problem 4: Shrinkwrap Modifier Not Applied

**Symptoms**:
- Exported geometry didn't show Shrinkwrap effect
- Decals weren't "wrapped" to the target surface in USD

**Root Cause**:
- `export_modifiers` option needed to be enabled for non-SUBSURF modifiers
- Shrinkwrap target object might have been hidden during modifier application

**Solution (v0.1.11)**:
- Added logic to temporarily unhide Shrinkwrap target objects before applying
- Restore visibility after modifier application
- Modifiers are now applied in correct order (respecting modifier stack)

#### Problem 5: Leftover Prims from Previous Exports

**Symptoms**:
- USD viewer showed prims like `SPADE_2b_Outline_Petrol_LEFT_dup1` with "weird cube icons"
- These prims didn't have valid geometry
- They appeared in the referencing USD file but not in the exported file

**Root Cause**:
- Previous exports (v0.1.9 and earlier) had written prims with `_dup` names
- These prims were now orphaned references in the parent USD file
- The new export wrote different prim names, leaving old references stale

**Solution**:
- This is a USD referencing issue, not an addon bug
- Users should delete old USD files before re-exporting
- Or manually clean up stale references in the parent USD file

---

## Session: Modifier Visibility Modes Investigation (v0.1.13 IMPLEMENTED)

**Date**: 25 January 2026  
**Status**: ✅ IMPLEMENTED in v0.1.13  
**Related Issue**: Inconsistent Shrinkwrap Modifier Application  
**Implementation Plan**: See `04_Implementation_Plan.md` Phase 7

### Context

During production testing with decal objects that use Shrinkwrap modifiers, inconsistent behavior was observed. Some modifiers appeared to be applied correctly, others were partially applied, and some were not applied at all. This was particularly puzzling because all modifiers appeared to have identical configurations in Blender's UI.

### Observed Symptoms

1. **Inconsistent Shrinkwrap Application**:
   - Some decals exported with Shrinkwrap correctly applied (geometry conformed to target surface)
   - Some decals exported with Shrinkwrap partially applied (partial deformation)
   - Some decals exported with NO Shrinkwrap effect (flat, undeformed geometry)

2. **No Visible Pattern**:
   - All modifiers appeared to have the same settings in Blender's UI
   - The user could not visually identify why some modifiers worked and others didn't
   - Behavior was unpredictable and inconsistent between exports

3. **Export Code Appeared Correct**:
   - The modifier application code was applying modifiers in the correct order
   - Target objects were being temporarily unhidden for Shrinkwrap
   - No errors were logged during modifier application

### Investigation Process

The investigation involved a detailed analysis of Blender's modifier system and the four visibility toggle icons in the modifier header:

| Icon | Property | Purpose |
|------|----------|---------|
| Triangle (Edit Mode) | `show_in_editmode` | Shows modifier effect in Edit Mode |
| Cage (On Cage) | `show_on_cage` | Allows editing the mesh "as modified" |
| Monitor (Viewport) | `show_viewport` | Enables modifier in 3D Viewport display |
| Camera (Render) | `show_render` | Enables modifier for final renders |

### Root Cause Hypothesis

**The current code does NOT check modifier visibility flags before applying modifiers.**

When `bpy.ops.object.modifier_apply()` is called:
- The operator applies the modifier **based on its current evaluated state in the depsgraph**
- If `show_viewport=False`, the modifier **hasn't been evaluated** and may apply with incorrect/default geometry
- This explains why some modifiers work (viewport enabled) and others don't (viewport disabled)

**Evidence**: A grep search for `show_viewport`, `show_render`, or `show_in_editmode` in the addon codebase returned **no matches**, confirming these flags are not being checked.

### Specific Failure Scenarios

#### Scenario A: Modifier with `show_viewport=False`
```
Modifier: Shrinkwrap
  show_viewport: ❌ OFF
  show_render: ✅ ON
```
- Result: Modifier applies with unevaluated/incorrect geometry
- User sees: Flat, undeformed mesh in USD

#### Scenario B: Modifier with `show_viewport=True`
```
Modifier: Shrinkwrap
  show_viewport: ✅ ON
  show_render: ✅ ON
```
- Result: Modifier applies correctly
- User sees: Properly deformed mesh in USD

#### Scenario C: Target object hidden
```
Modifier: Shrinkwrap
  target: inner_hull
  target.hide_viewport: ✅ HIDDEN
```
- Result: Shrinkwrap cannot evaluate without visible target
- User sees: Partial or no deformation

### Planned Solution (v0.1.13)

**Approach 1: Force-Enable Viewport Visibility Before Applying**

```python
for mod in dup_obj.modifiers:
    # Temporarily enable viewport visibility to ensure proper evaluation
    original_show_viewport = mod.show_viewport
    mod.show_viewport = True
    
    # Force depsgraph update
    context.view_layer.update()
    
    # Now apply (modifier is guaranteed to be evaluated)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    # Note: No need to restore since modifier is deleted after apply
```

**Approach 2: Respect User Settings (Skip Disabled Modifiers)**

```python
for mod in dup_obj.modifiers:
    # Only apply if modifier is enabled in viewport
    if not mod.show_viewport:
        logger.log_warning(
            f"Skipping modifier '{mod.name}' - not enabled in viewport",
            context=start point_context
        )
        continue
    # ... apply modifier ...
```

**Recommended Approach**: Use Approach 1 (force-enable) because:
- Users expect "export with modifiers" to apply ALL modifiers regardless of UI state
- The export is a "bake" operation that should capture final geometry
- Users who want to exclude a modifier can delete it before export

**Additional Changes for v0.1.13**:

1. **Force-enable `show_viewport` on all modifiers before applying**
2. **Expand target object visibility handling to all modifier types**:
   - `SHRINKWRAP` → `mod.target`
   - `LATTICE` → `mod.object`
   - `MESH_DEFORM` → `mod.object`
   - `SURFACE_DEFORM` → `mod.target`
   - `CURVE` → `mod.object`
   - `BOOLEAN` → `mod.object`
   - `ARMATURE` → `mod.object`
3. **Force depsgraph update** after visibility changes
4. **Add logging** to show which modifiers had visibility issues

### Testing Plan

1. Create test scene with modifiers in various visibility states:
   - Modifier with `show_viewport=False`, `show_render=True`
   - Modifier with `show_viewport=True`, `show_render=False`
   - Modifier with both enabled
   - Modifier with both disabled
   - Modifier with hidden target object

2. Export and verify:
   - All modifiers with `export_modifiers=True` should be applied
   - Logged warnings should show which modifiers had visibility overrides
   - USD geometry should match expected results

### Validation Criteria

- [ ] Modifiers with `show_viewport=False` are correctly applied after force-enable
- [ ] Target objects for all modifier types are temporarily unhidden
- [ ] Depsgraph is updated before modifier application
- [ ] Logging shows visibility overrides
- [ ] No regressions in existing modifier export functionality

---

## Requirements Discovered

### REQ-MOD-001: Complete Modifier Export Support

**Priority**: Critical  
**Status**: Implemented in v0.1.11

**Requirement**: The addon MUST support exporting ALL modifier types, not just Subdivision.

**Functional Requirements**:
- Apply SUBSURF modifiers when `export_subdivision` is enabled
- Apply ALL other modifiers (Shrinkwrap, Array, Mirror, etc.) when `export_modifiers` is enabled
- Handle modifiers with target objects (e.g., Shrinkwrap) by ensuring targets are visible
- Apply modifiers in correct stack order
- Preserve original objects and modifiers (non-destructive workflow)

### REQ-MOD-002: Modifier Visibility Mode Handling

**Priority**: High  
**Status**: ✅ Implemented in v0.1.13  
**Discovery Reference**: See "Session: Modifier Visibility Modes Investigation" above

**Requirement**: The addon MUST correctly apply modifiers regardless of their visibility toggle states.

**Functional Requirements**:
- Force-enable `show_viewport` on all modifiers before applying (for proper depsgraph evaluation)
- Handle target objects for ALL modifier types with targets (not just Shrinkwrap)
- Force depsgraph update after visibility changes
- Log which modifiers had visibility overrides applied
- Restore original visibility state on error (for modifiers that weren't applied yet)

**Technical Requirements**:
- Check and set `mod.show_viewport = True` before `modifier_apply()`
- Call `context.view_layer.update()` after visibility changes
- Handle target objects: Shrinkwrap, Lattice, Mesh Deform, Surface Deform, Curve, Boolean, Armature

### REQ-NAME-001: Consistent USD Namespace

**Priority**: Critical  
**Status**: Implemented in v0.1.11

**Requirement**: Exported USD prims MUST have the same names as the original Blender objects.

**Functional Requirements**:
- USD prim names must match Blender object names (sanitized for USD)
- No `_dup`, `.001`, or other temporary suffixes in USD
- Consistent names enable reliable USD referencing and variant switching
- Name sanitization for USD-invalid characters (spaces, special chars → underscores)

### REQ-EXPORT-ALL: Export All Collection Objects

**Priority**: Critical  
**Status**: Implemented in v0.1.12

**Requirement**: ALL mesh objects in a collection MUST be exported, regardless of whether they have modifiers.

**Functional Requirements**:
- Objects WITH modifiers: Duplicate, apply modifiers, export duplicate
- Objects WITHOUT modifiers: Export original directly
- No objects should be silently skipped
- Logging must show which objects are processed and how

### REQ-CLEANUP-001: Robust Cleanup and State Restoration

**Priority**: High  
**Status**: Implemented in v0.1.11

**Requirement**: After export, the Blender scene MUST be in exactly the same state as before export.

**Functional Requirements**:
- No duplicate objects left behind
- All object names restored to originals
- Object visibility restored
- Object selection restored
- Works even if export fails mid-way (rollback on error)

---

## Lessons Learned

### 1. Non-Destructive Workflow is Critical

Applying modifiers permanently changes mesh data. Always duplicate first, apply to the duplicate, export, then delete the duplicate. This keeps the original scene intact.

### 2. Name Consistency Matters for USD Pipelines

USD relies on stable prim paths for referencing and composition. Changing names between exports breaks references. Use name-swap strategy to ensure exported names match originals.

### 3. Test with Real Production Scenes

Initial testing with simple scenes missed the complexity of:
- Objects with multiple modifier types
- Modifiers with target objects
- Mixed collections (some objects with modifiers, some without)

### 4. Cleanup Must Be Robust

Cleanup logic must run even if errors occur during export. Use try/finally blocks and track all temporary objects for cleanup.

### 5. Log Everything for Debugging

The comprehensive logging system was essential for diagnosing issues. Each step (gather, duplicate, apply, export, cleanup) should be logged with object names and counts.

---

## Session: Mesh Data Name Consistency (v0.1.14 IMPLEMENTED)

**Date**: 25 January 2026  
**Status**: ✅ IMPLEMENTED in v0.1.14  
**Related Issue**: Mesh prim names incrementing on each export  
**Discovery Reference**: Bug report `usdme_bug_report_20260125_135648.json`

### Problem

While v0.1.13 fixed the modifier visibility issues and the Shrinkwrap modifier worked correctly, a new issue was discovered:

**Mesh data block names were incrementing on each export**, resulting in different mesh prim names in USD each time:
- First export: `Plane_005` (original mesh), `Plane_011` (duplicate mesh)
- Second export: `Plane_005` (original mesh), `Plane_014` (duplicate mesh)
- Third export: `Plane_005` (original mesh), `Plane_016` (duplicate mesh)

### Root Cause

When duplicating an object in Blender:
1. Blender also duplicates the **mesh data block**
2. The duplicated mesh gets an auto-generated name (e.g., `Plane.005` → `Plane.011`)
3. These incrementing mesh names are exported to USD as mesh prim names
4. This breaks USD referencing workflows that rely on consistent prim paths

### Solution (v0.1.14)

Applied the **name-swap strategy to mesh data blocks**, not just objects:

1. **Before duplication**: Save original mesh data name (e.g., `Plane.005`)
2. **After duplication**: Rename original mesh data to hidden name (`__USDME_MESH_Plane.005`)
3. **Rename duplicate mesh data** to original name (`Plane.005`)
4. **Export**: USD mesh prims now have consistent names
5. **Cleanup**: Delete duplicate object AND mesh data, restore original mesh name

### Code Changes

Added to `ops_export.py`:
- `mesh_swaps` dictionary to track mesh data name swaps
- `mesh_swaps_for_cleanup` to persist swaps through isolation context
- Mesh data name restoration in cleanup phase
- Logging for mesh data name operations

---

## Session: Disabled Modifier Skipping (v0.1.15 IMPLEMENTED)

### Problem

After adding the "Edit Modifiers" button, modifiers were being exported even when they were completely disabled (all visibility toggles off). This caused issues because:

1. Users intentionally disable modifiers by turning off all visibility modes
2. The addon was still applying these disabled modifiers during export
3. This violated user intent - disabled modifiers should not affect the export

### Blender Modifier Visibility Toggles

Blender has 4 visibility toggles for each modifier:

| Property | Icon | Purpose |
|----------|------|---------|
| `show_in_editmode` | Triangle/verts | Show modifier effect in Edit Mode |
| `show_on_cage` | Box-with-verts | Edit the cage using modifier result |
| `show_viewport` | Monitor | Show modifier in 3D Viewport |
| `show_render` | Camera | Include modifier in final renders |

### Root Cause

The v0.1.13 fix forced `show_viewport=True` on all modifiers before applying, but it didn't check if the modifier was intentionally disabled. If a user had turned off both `show_viewport` AND `show_render`, the modifier should be skipped entirely.

### Solution (v0.1.15)

Added `should_apply_modifier()` helper function that checks if a modifier is intentionally disabled:

- **Skip if BOTH `show_render` AND `show_viewport` are False** - Modifier is intentionally disabled
- **Apply if EITHER `show_render` OR `show_viewport` is True** - User wants modifier visible somewhere

This check is added at the beginning of all 4 modifier application loops (OBJECT/COLLECTION × SUBSURF/other modifiers).

### Code Changes

Added to `ops_export.py`:
- `should_apply_modifier(mod, logger, start point_context)` - Returns `False` if modifier should be skipped
- Updated all 4 modifier loops to check `should_apply_modifier()` before applying
- Logs skipped modifiers with reason: "Both show_render and show_viewport are False"

### Testing

- ✅ Modifiers with all toggles off are skipped
- ✅ Modifiers with only `show_viewport=True` are applied
- ✅ Modifiers with only `show_render=True` are applied
- ✅ Modifiers with both enabled are applied
- ✅ Skipped modifiers are logged for user visibility

---

## Session: Unified Modifier Export (v0.1.16 IMPLEMENTED)

### Problem

After adding the "Export Modifiers" checkbox, there was a logical inconsistency:

1. Subdivision (SUBSURF) is a modifier type
2. There were two separate checkboxes:
   - "Export Subdivision" (legacy)
   - "Export Modifiers" (new)
3. If user unchecked "Export Subdivision" but checked "Export Modifiers", subdivisions were NOT exported
4. This violated the principle that "Export Modifiers" should include ALL modifiers, including subdivision

### Root Cause

The `export_subdivision` checkbox was a legacy feature from before unified modifier export was implemented. Subdivision was treated as a special case separate from other modifiers, creating confusion and inconsistent behavior.

### Solution (v0.1.16)

**Removed the legacy `export_subdivision` checkbox** and unified all modifier export under the single "Export Modifiers" checkbox:

- **Removed**: `export_subdivision` property from `props.py`
- **Removed**: "Export Subdivision" UI checkbox from `ui.py`
- **Updated**: All logic to use `export_modifiers` for ALL modifiers (including SUBSURF)
- **Unified**: SUBSURF modifiers are now treated as part of the general modifier export
- **Order**: SUBSURF modifiers are still applied first (as they're usually at the bottom of the stack), then other modifiers

### Code Changes

**Removed from `props.py`:**
- `export_subdivision: BoolProperty(...)` - Legacy property removed

**Removed from `ui.py`:**
- "Export Subdivision (Baked)" checkbox UI element

**Updated in `ops_export.py`:**
- Replaced `if start point.export_subdivision:` with `if start point.export_modifiers:` for SUBSURF handling
- Combined SUBSURF and other modifiers into unified application logic
- Removed `subdivision_modifiers_applied` tracking (now uses unified `modifiers_applied`)
- Updated logging to reflect unified modifier export

### Behavior After Fix

- ✅ "Export Modifiers" checkbox controls ALL modifiers (Subdivision, Shrinkwrap, Array, etc.)
- ✅ When checked, subdivisions are automatically included
- ✅ Cleaner, more intuitive UI with single checkbox
- ✅ No confusion about which modifiers are exported

---

## Session: Leftover Duplicate Objects (v0.1.17 IMPLEMENTED)

**Problem**: After failed exports, duplicate objects with `_dup1` suffixes were left behind in the scene. The original object was renamed to `__USDME_ORIG_*` but never restored.

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

**Code Changes**:
- Updated OBJECT type duplication to use name-swap strategy (same as COLLECTION)
- Added `leftover_objects_cleaned` check at export start
- Added `name_swaps_for_cleanup` tracking for both OBJECT and COLLECTION types

**Testing**: 
- ✅ Duplicates now always have original names (not `_dup1`)
- ✅ Leftover objects from previous failed exports are cleaned up automatically
- ✅ Both OBJECT and COLLECTION types use consistent duplication logic

---

## Session: Modifier Stack Order (v0.1.18 IMPLEMENTED)

**Problem**: Modifiers were being applied in the wrong order. The code applied SUBSURF modifiers first, then other modifiers, breaking the modifier stack order. This caused incorrect geometry results (e.g., Mirror modifier applied after Subdivision, causing gaps at center line).

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

**Code Changes**:
- Removed `subsurf_modifiers` and `other_modifiers` separation
- Changed to single loop: `for mod in list(dup_obj.modifiers):`
- Applied to both OBJECT and COLLECTION type start points

**Testing**: 
- ✅ Mirror modifier (top of stack) now applies before Subdivision (below Mirror)
- ✅ Modifier stack order is respected
- ✅ Geometry results match Blender viewport

**Known Issue - Unresolved**: 
- ⚠️ **Selection and Mask Issues**: During testing, there were issues with selections and masks of selections that may affect modifier application. This issue is unresolved and should be investigated if similar problems occur in the future. The modifier stack order fix resolved the immediate problem, but selection/mask issues may need separate attention.

---

## Session: Unit Conversion and Y-Up Axis (v0.1.19-v0.1.20 IMPLEMENTED)

**Date**: 26 January 2026  
**Status**: ✅ IMPLEMENTED in v0.1.20  
**Related Issue**: Need for unit scaling and Y-up conversion for Omniverse compatibility

### Context

Users needed the ability to:
1. Convert between metric units (mm → m, mm → cm, etc.) during export
2. Convert from Blender's Z-up coordinate system to Y-up for Omniverse compatibility

### Solution (v0.1.20)

**1. Unit Conversion System**

Added per-start point unit conversion with source and target unit selection:

```python
# In props.py
source_unit: EnumProperty(
    name="Source Unit",
    items=[
        ('MILLIMETERS', "Millimeters (mm)", "..."),
        ('CENTIMETERS', "Centimeters (cm)", "..."),
        ('METERS', "Meters (m)", "..."),
        ('KILOMETERS', "Kilometers (km)", "..."),
    ],
    default='MILLIMETERS',
)

target_unit: EnumProperty(
    name="Target Unit",
    items=[...same as above...],
    default='METERS',
)

def get_scale_factor(self) -> float:
    """Calculate scale factor from source_unit to target_unit conversion."""
    unit_factors = {
        'MILLIMETERS': 0.001,   # 1mm = 0.001m
        'CENTIMETERS': 0.01,    # 1cm = 0.01m
        'METERS': 1.0,          # 1m = 1m
        'KILOMETERS': 1000.0,   # 1km = 1000m
    }
    source_factor = unit_factors.get(self.source_unit, 1.0)
    target_factor = unit_factors.get(self.target_unit, 1.0)
    return source_factor / target_factor
```

Auto-detection of source unit from Blender scene settings via `detect_source_unit()`.

**2. Y-Up Axis Conversion**

Added `y_is_up` checkbox for Omniverse compatibility:

```python
y_is_up: BoolProperty(
    name="Y is Up",
    description=(
        "Convert from Blender's Z-up to Y-up (for Omniverse compatibility). "
        "Rotates scene -90° around X axis during export."
    ),
    default=False,
)
```

The Y-up conversion applies:
- Location transform: `(x, y, z) → (x, z, -y)`
- Rotation: -90° around X axis

**Key Design Decision**: Scale factor is applied ONLY to `obj.location`, NOT to `obj.scale`. This ensures `xformOp:scale` in USD remains `(1,1,1)`.

---

## Session: Unit Label UI Fix (v0.1.21 IMPLEMENTED)

**Date**: 26 January 2026  
**Status**: ✅ IMPLEMENTED in v0.1.21

### Problem

UI labels showed confusing unit abbreviations (e.g., "mi" for millimeters instead of "mm").

### Solution

Updated `ui.py` to use standard metric abbreviations:
- `mm` for millimeters
- `cm` for centimeters  
- `m` for meters
- `km` for kilometers

---

## Session: xformOp:scale Fix (v0.1.22 IMPLEMENTED)

**Date**: 26 January 2026  
**Status**: ✅ IMPLEMENTED in v0.1.22  
**Related Issue**: `xformOp:scale = (0.001, 0.001, 0.001)` in exported USD when it should be `(1,1,1)`

### Problem

The scale factor was being applied to `obj.scale`, causing the exported USD to have `xformOp:scale = (0.001, 0.001, 0.001)` instead of `(1,1,1)`.

### Root Cause

The export logic was modifying both `obj.location` AND `obj.scale` with the unit conversion factor.

### Solution

Changed the export logic to apply scale factor ONLY to `obj.location`:

```python
# CORRECT: Apply scale factor only to location
scale_factor = start point.get_scale_factor()
obj.location = (
    obj.location.x * scale_factor,
    obj.location.y * scale_factor,
    obj.location.z * scale_factor
)
# obj.scale remains unchanged → xformOp:scale = (1,1,1) in USD
```

This ensures geometry is scaled through position, but the object's internal scale remains at 1.0.

---

## Session: Collection Normalization & Pivot Strategy (Planned)

**Date**: 02 February 2026  
**Status**: 🟡 PLANNED  
**Related Issue**: Inconsistent Collection vs Object export behavior during USD bake

### Context

Persistent inconsistencies were observed between OBJECT exports (hull) and COLLECTION exports (decals) when applying the two-step USD bake approach. The hull could be corrected with the bake pipeline, but decals frequently lost spatial context, rotations, or scale due to messy Blender transforms and collection-level pivot ambiguity.

### Problem Summary

- Collection exports share code with object exports, but behave differently in practice.
- Decal collections often contain objects with non-unit scale, unapplied rotations, and inconsistent origins.
- Baking in USD cannot reliably recover these inconsistencies if the Blender source transforms are not normalized.

### Decision

Add a **Blender-side normalization pass** for COLLECTION exports before USD export:

1. **Normalize Scale** (apply scale to 1.0)
2. **Normalize Rotation** (optional, bake rotation into geometry)
3. **Normalize Position** (optional, bake translation into geometry)
4. **Collection Pivot Selection**:
   - World Origin (0,0,0)
   - Custom XYZ
   - 3D Cursor
   - Fake Parent (reference another object's pivot, e.g., the hull)

These options will be exposed in the Collection export UI to let users preserve messy authoring workflows while still generating consistent USD output.

### Expected Outcome

- Collection decals maintain correct spatial relationships after export.
- Unified post-process bake logic for both OBJECT and COLLECTION start points.
- Reduced iteration loops caused by collection-specific transform anomalies.

### When to Use Collections vs Objects

- **Use Collection** when exporting multiple related objects in bulk (e.g., decals). Collection exports need an explicit pivot selection to keep alignment consistent.
- **Use Object** when exporting a single asset that already has a clear, deliberate transform and pivot in Blender.
- **Performance Tip**: Normalizing position/scale to a single pivot (world or fake parent) reduces transform complexity downstream, but may not be desirable if you want to preserve authoring transforms.

---

## Session: OBJECT Type Export - Selection Bug (v0.1.23-v0.1.27 IMPLEMENTED)

**Date**: 26 January 2026  
**Status**: ✅ IMPLEMENTED in v0.1.27  
**Related Issue**: OBJECT type start points exported empty USD files (no geometry)

### Problem

After the unit conversion feature was added, OBJECT type start point exports produced USD files with no geometry. Collection exports worked, but single object exports were empty.

### Investigation Process

Multiple debugging iterations revealed:
1. Transforms were being applied correctly
2. Objects were being processed correctly  
3. But `selected_objects_count=0` in the export logs - Blender's USD exporter was seeing no selected objects

### Root Cause Analysis

The selection logic was failing because:

1. **v0.1.23-v0.1.25**: Objects were being hidden BEFORE selection, which caused `select_set(True)` to fail silently
2. **v0.1.26**: Object references became stale after `context.view_layer.update()` was called
3. The fundamental problem: you cannot select hidden objects in Blender

### Failed Approaches

**Approach 1 (v0.1.23)**: Added object to `objects_to_export` list - still failed
**Approach 2 (v0.1.24)**: Moved transform application before selection - still failed
**Approach 3 (v0.1.25)**: Fetch fresh object references by name - still failed
**Approach 4 (v0.1.26)**: Capture names as strings early - still failed

All approaches failed because the core issue was the ORDER of operations.

### Solution (v0.1.27) - Complete Selection Logic Rewrite

The key insight: **Objects must be visible to be selected.**

New selection logic order:
1. **Deselect all objects** (while they are still visible)
2. **Ensure target objects are visible and selected** (unhide, set active, select)
3. **Force view layer update**
4. **THEN hide all non-target objects** (after selection is complete)

```python
# v0.1.27 WORKING SELECTION LOGIC

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
        # Ensure object is visible
        view_layer_obj.hide_viewport = False
        view_layer_obj.hide_set(False)  # Also unhide in outliner
        # Set as active object first (required for selection to work reliably)
        if not first_obj_set:
            context.view_layer.objects.active = view_layer_obj
            first_obj_set = True
        # Now select it
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

### Key Lessons Learned

1. **Blender selection requires visibility**: `select_set(True)` silently fails on hidden objects
2. **Order matters**: Deselect → unhide/select targets → update → hide others
3. **Use object names, not references**: Object references can become stale after `view_layer.update()`
4. **Set active object before selecting**: Some operations require an active object to be set first
5. **Verify selection before export**: Added `selection_verification` logging step to confirm selection state

### Acceptance Criteria

- [x] OBJECT type start points export geometry correctly
- [x] Selection logic works reliably with hidden objects
- [x] Unit conversion applies correctly to object location
- [x] Y-up axis conversion works correctly
- [x] No `xformOp:scale` issues in USD output
- [x] Selection verification logging added for debugging

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v0.1.10 | 24.01.2026 | Initial attempt at modifier export with duplicate preservation |
| v0.1.11 | 25.01.2026 | Name-swap strategy, all modifiers support, robust cleanup |
| v0.1.12 | 25.01.2026 | Export ALL objects (not just duplicated ones) |
| v0.1.13 | 25.01.2026 | Modifier visibility mode handling (force-enable `show_viewport`, expand target handling) |
| v0.1.14 | 25.01.2026 | Mesh data name consistency (name-swap for mesh data blocks) |
| v0.1.15 | 25.01.2026 | Skip intentionally disabled modifiers (both show_render and show_viewport False) |
| v0.1.16 | 25.01.2026 | Unified modifier export - removed legacy export_subdivision checkbox, subdivisions now included in export_modifiers |
| v0.1.17 | 25.01.2026 | Unified OBJECT/COLLECTION duplication strategy, automatic leftover cleanup |
| v0.1.18 | 25.01.2026 | Fixed modifier stack order - apply modifiers top-to-bottom as they appear in stack |
| v0.1.19 | 26.01.2026 | Added unit conversion system (source/target units) and Y-up axis conversion |
| v0.1.20 | 26.01.2026 | Implemented unit conversion with auto-detection from scene settings |
| v0.1.21 | 26.01.2026 | Fixed UI unit labels (mm, cm, m, km) |
| v0.1.22 | 26.01.2026 | Fixed xformOp:scale issue - scale factor applied only to location, not obj.scale |
| v0.1.23 | 26.01.2026 | Fixed OBJECT type export - added object to export list, corrected Y-up transforms |
| v0.1.24 | 26.01.2026 | Moved transform application before selection setup |
| v0.1.25 | 26.01.2026 | Refined selection with fresh object references by name |
| v0.1.26 | 26.01.2026 | Captured object names as strings early to prevent stale references |
| v0.1.27 | 26.01.2026 | **FIXED**: Complete selection logic rewrite - deselect first, then hide non-targets after selection |

---

Here’s the blunt second opinion: your **core idea (temporary parent → normalize → bake → export → restore)** is viable, but two things in your current plan are very likely sabotaging you:

1. **You’re treating `matrix_parent_inverse` as “stale state that must be updated”** after normalization, but in Blender it’s *part of the relationship* and whether it “should change” depends on your intent.
2. You may be **baking from non-evaluated matrices** (or otherwise not forcing depsgraph evaluation at the right points), so the matrices you bake/export are not the ones you’re seeing in the viewport.

Below are the actionable details.

---

## 0) Quick USD correction: Scope can’t carry a transform

A **USD `Scope` is organizational and “guaranteed no-op transform”**: it **cannot** have its own transform ops; it only passes ancestors’ transforms to children. If you need a container with a transform, you want a **`UsdGeomXform`** (or any `Xformable`). ([docs.omniverse.nvidia.com][1])

So if any part of your pipeline expects “Scope prim with a transform”, that expectation is mismatched with USD semantics.

---

## 1) Your `matrix_parent_inverse` understanding is half-right — but the *timing/intent* is the trap

### What `matrix_parent_inverse` is actually doing

When you parent in the UI with “keep transform”, Blender compensates so the child doesn’t jump: it stores an offset (parent inverse) between parent and child. The “correct” value depends on whether you want the child to **stay put** or **move with the parent**. ([surf-visualization.github.io][2])

### Why your v0.1.62 change can produce “no difference”

Your implementation plan currently treats “update `matrix_parent_inverse` after normalization” as critical. 
But if your normalization sets the fake parent to identity (location 0 / rot 0 / scale 1), then:

* `fake_parent.matrix_world.invertity**
* Setting every child’s `matrix_parent_inverse` to identity **removes the compensation offset**
* That very often results in the group behaving like it *did before* (i.e., the normalization effect is canceled), which matches the user feedback “no difference”.

**Key point:**

* If normalization is meant to **move the whole collection** (group transform), you generally **do NOT** want to “fix” parent inverse after moving the parent. Leaving the existing relationship intact is what makes children inherit the parent’s new transform.
* You only update parent inverse *after a parent change* if your goal is “parent changed but child must visually stay where it is”.

So: your plan’s “always update parent inverse after normalization” is only correct for the “keep children fixed” intent — not for “normalize the group”. That’s the conceptual mismatch. 

---

## 2) `view_layer.update()` is often not enough — use depsgraph evaluation for matrices you bake/export

There’s a recurring Blfreshly created objects and post-op transforms can have **matrix_world values that aren’t fully evaluated** until the depsgraph updates.

A common fix pattern is explicitly updating the evaluated depsgraph before reading matrices (and especially before using them for parenting math). ([Blender Stack Exchange][3])

### What I would change immediately

When you bake, do **not** trust raw `obj.matrix_world` unless you’re sure it’s evaluated.

Use:

```python
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()

M = obj.evaluated_get(depsgraph).matrix_world.copy()
```

Then bake/export based on `M`.

This matters even more with your decals case because shrinkwrap + “what you see in viewport” vs “what exporter evaluates” can diverge unless you’re explicitly consistent about evaluation mode.

---

## 3) Your baking approach is conceptually fine, but fragile in Blender’s parenting model

The “compute world → unparent → set world” idea can work, but watch these Blender-specific footguns:

### A) How you parent/unparent matters

* `obj.parent = fake_parent` alone is **not** the same as UI parenting (“keep transform”). You need the parent inverse set correctly *at parenting time*, using evaluated parent world. ([Blender Stack Exchange][3])
* When clearing parent, prefer a “clear parent keep transform” equivalent (operator or correct matrix bookkeeping). If you clear the parent in a way that changes `matrix_basis` unexpectedly, you can get subtle rotation/scale drift.

### B) Exporter transform representation can change rotations

Blender’s USD exporter can author transforms as TRS vs Quaternion vs full Matrix. If any of your objects end up with **non-uniform scale + rotation** (very common once you start doing group normalization math), decomposing to TRS can yield different rotation results than your original 4×4.

Set exporter transform mode to **Matrix** (`xform_op_mode='MAT'`) for debugging (and often for production if you care about exactness). ([docs.omniverse.nvidia.com][4])

### C) Double axis conversion is easy to do

You already found the Y-up conversion ordering issue. Make sure you’re not *also* enabling the exporter’s `convert_orientation` while doing your own conversion/baking. The operator exposes `convert_orientation` and axis selections. ([UPBGE][5])

---

## 4) The simplest fix: stop parenting entirely; bake a single “group normalization” matrix into each child

This is the approach I’d use to eliminate `matrix_parent_inverse` from the equation:

1. Capture each object’s evaluated world matrix `W_i`.
2. Compute one group transform `G` you want to apply (based on pivot mode + normalization).
3. Set `obj.matrix_world = G @ W_i` for each object (on *temporary duplicates* if you want zero side effects).
4. Export selected objects only.
5. Restore.

No parent. No parent inverse. No unparenting surprises.

If your “normalize to origin” intent is “pretend the collection pivot is the world origin”, then **`G` is typically the inverse of the pivot transform** you would have put on the fake parent.

Even if you keep your existing fake-parent pipeline, you can still *compute* `G` from the fake parent’s evaluated matrix at the moment before you “normalize it away”.

---

## 5) You may not need `selected_objects_only` at all — exporter supports `collection=...`

Your own rationale says you must use `selected_objects_only=True`, but `bpy.ops.wm.usd_export` has a `collection` argument (string) specifically for exporting a collection (and its children). That can simplify selection/state juggling and may change how parents/transforms are handled. ([UPBGE][5])

I’d try a branch where you export using `collection=collection.name` and **also** test exporting with the fake parent included (selected or as a parent) to see if your “exporter ignores hierarchy” assumption holds in your exact Blender 5.0 setup.

---

## 6) How to *prove* what’s wrong (fast, deterministic debugging)

### A) Log evaluated matrices at 4 checkpoints

For each object, record:

* `W0`: original evaluated world
* `W1`: after parenting
* `W2`: after normalization
* `W3`: right before export (after bake/unparent)

If your workflow is correct, `W3` should match what you *think* you baked.

### B) Compare to what USD actually contains

Export ASCII `.usda` and inspect, or use pxr to compute world transforms and diff them against `W3`.

For world transforms in USD, use an `UsdGeom.XformCache` and compare matrices prim-by-prim.

This immediately tells you whether the error is:

* Blender side baking (bad `W3`), or
* USD export settings / transform authoring, or
* USD viewer interpretation (axis/units), etc.

---

## What I think is your *most likely* root cause

Given the symptom “v0.1.62 made no difference” and your plan’s step 4, I’d bet on this combination:

* **Updating `matrix_parent_inverse` after normalization is canceling the normalization effect**, so you’re not actually baking the transform you think you are (or you’re baking a transform computed from a stale/non-evaluated matrix). 
* **You’re reading `obj.matrix_world` instead of evaluated depsgraph matrices** at one of the critical points (right after creating/normalizing the parent, or right before baking). ([Blender Stack Exchange][3])
* Second-order: exporter writing TRS instead of matrix is introducing rotation differences; switch to `xform_op_mode='MAT'` to confirm. ([docs.omniverse.nvidia.com][4])

---

If you want one concrete “next code change” without re-architecting:

1. Replace `context.view_layer.update()` with depsgraph updates + evaluated matrices when baking. ([Blender Stack Exchange][3])
2. Remove the “update children `matrter normalization” step **unless your goal is explicitly ‘keep children fixed while parent changes’**. ([surf-visualization.github.io][2])
3. Export with `xform_op_mode='MAT'` and `convert_orientation=False` while debugging. ([UPBGE][5])

(And separately: don’t plan on a transformable `Scope`; use an `Xform` container in USD. ([docs.omniverse.nvidia.com][1]))

Your implementation plan and quick reference are well structured for isolating paths, but this specific “parent inverse after normalization” rule is likely backwards for the normalization behavior you actually want. 



[1]: https://docs.omniverse.nvidia.com/dang/latest/guide/usd/usd-fundamentals.html?utm_source=chatgpt.com "USD Fundamentals — Data Aggregation and Navigation ..."
[2]: https://surf-visualization.github.io/blender-course/api/parenting/ "Parenting - Introduction to Scientific Visualization with Blender"
[3]: https://blender.stackexchange.com/questions/152781/how-to-make-object-a-a-parentkeep-transform-of-object-b-via-blenders-python-a "How to make object A a parent(keep_transform) of object B via Blender's Python API? - Blender Stack Exchange"
[4]: https://docs.omniverse.nvidia.com/connect/latest/blender/manual.html "User Manual — Omniverse Connect"
[5]: https://upbge.org/docs/latest/api/bpy.ops.wm.html?utm_source=chatgpt.com "Wm Operators — UPBGE/Blender Python API"





---


## Related Documents

- `02_Detailed_Requirements.md` - Updated with new requirements
- `04_Implementation_Plan.md` - Updated with implementation details
- `Domain_Blender_Guardrails/080_Framework_RULES/best_practices/` - Best practices documentation

