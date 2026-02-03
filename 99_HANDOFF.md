## HANDOFF — Blender USD MultiExport

### Domain / Context
- **Domain:** Blender + OpenUSD + Omniverse
- **Type:** Programming / addon dev
- **Goal:** Restore object export behavior to match `v0.1.48` (known-good), and keep collection export as a separate path using a “fake parent” empty with optional normalization.

### Required Tooling
- **Use MCPs:** `usd codeNIM` MCP and `synopgarden` MCP (both are required).
- **Environment:** Windows, Blender 5.0, pxr USD Python API used by `usd_bake.py`.

Documentation
E:\SynologyDrive\9999_LocalRepo\Blender_USD_MultiExport\02_Detailed_Requirements.md
REQ-EXP-022 - REQ-EXP-025
E:\SynologyDrive\9999_LocalRepo\Blender_USD_MultiExport\03_Module_Design.md
E:\SynologyDrive\9999_LocalRepo\Blender_USD_MultiExport\04_Implementation_Plan.md -> **Phase 14D: Collection Normalization & Pivot Controls (Planned)**

### Current State Summary
- Object export path has drifted away from `v0.1.48` and now produces **broken normals** when modifiers are enabled.
- Collection export path (decals) is partially implemented (fake parent pivot + normalization) but currently breaks and appears to leak into object export path.
- **v0.1.48** is last known working version for object export.
- Recent versions (`v0.1.53+`) show:
  - Modifiers enabled → normals broken.
  - Modifiers disabled → normals OK.
- Two USDA files were compared:
  - **Working:** `... - Normals Working v0148.usda`"D:\SPADEKAYAKS\070_RuD_Product development\Hard Goods\Boats\SP_W012_2025Shakti\010_ASS_USD\USD_Startpoint\FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002 - Normals Working v0148.usda"
  - **Broken:** `... - NORMALS BROKEN_V0153.usda`"D:\SPADEKAYAKS\070_RuD_Product development\Hard Goods\Boats\SP_W012_2025Shakti\010_ASS_USD\USD_Startpoint\FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002 - NORMALS BROKEN_V0153.usda"
  - Same topology/indices/points counts, but **normal values differ**, indicating normals are being altered.

### What Must Be Done
1. **Object export path**
   - Must exactly match behavior of `v0.1.48`.
   - Treat as fully isolated (no collection/pivot/normalization logic).
   - All post-processing (e.g., bake) should replicate `v0.1.48` pipeline. E:\SynologyDrive\9999_LocalRepo\Blender_USD_MultiExport\releases\blender_usd_multiexport_v0.1.48

2. **Collection export path**
   - Use a **fake parent empty** (Blender Empty / Plain Axes).
   - Parent should be placed based on pivot mode: world origin, custom XYZ, 3D cursor, object pivot, preserve.
   - Optional normalization (position/scale/rotation) should apply only to collection path.
   - Should not influence object export path.

### Key Files
- `blender_usd_multiexport_addon/ops_export.py`
- `blender_usd_multiexport_addon/usd_bake.py`
- `blender_usd_multiexport_addon/props.py`
- `blender_usd_multiexport_addon/state_manager.py`
- `blender_usd_multiexport_addon/ui.py`
- `80_WIP_notes.md` (latest findings)
- `releases/blender_usd_multiexport_v0.1.48` (reference baseline)

### Evidence / Notes
- **Bug reports:** see `80_WIP_notes.md`
- Modifier-enabled exports produce broken normals.
- Modifier-disabled exports look correct.

### Next Agent: Action Plan
- Diff `v0.1.48` against current for **object export path** and revert behavior.
- Split code paths so object exports bypass collection pivot/normalization.
- Re-implement collection fake-parent logic cleanly after object export is fixed.
- Ensure the bake step does not overwrite authored normals for object path.
- Verify with modifier-enabled test (same hull asset).

---

## Appendix: Collection Export Issue - Expert Consultation Prompt

**Purpose**: This prompt is designed to get an expert second opinion on our collection export implementation approach. It explains the problem, what we've tried, why we do it this way, and what's still not working.

---

### The Problem

We're building a Blender addon that exports collections to USD format. Collections in Blender don't have transforms (they're just organizational containers), but in USD we need a Scope prim with a transform to position the collection spatially. Our solution is to create a "fake parent" Empty object in Blender, parent all collection objects to it, apply optional normalization to the parent, then export.

**Current Issue**: Despite implementing what we believe is the correct workflow, exported objects appear scattered/misaligned/rotated incorrectly in the USD file, even though they look correct in Blender's viewport before export.

**Test Case**: Collection named `SHAKTI_Decals` containing 6 mesh objects (decals/logos). All objects have Shrinkwrap modifiers that need to be applied before export. Export completes successfully, but objects are misaligned in the resulting USD file.

---

### Why We Do It This Way

**1. The "Fake Parent" Concept**
- Collections in Blender have no transform - they're just organizational containers
- USD Scopes need transforms to position collections spatially
- We create a temporary Blender Empty object as a "fake parent" to provide the transform hierarchy
- This allows us to normalize position/scale/rotation at the collection level without modifying individual object geometry (which would break normals)

**2. Avoiding Geometry Manipulation**
- We learned from previous failures that directly transforming geometry in Blender before export breaks normals
- Our best practice (documented) is: "Export with Blender native, then bake transforms in USD space"
- The fake parent approach lets us manipulate transforms without touching geometry

**3. Blender USD Exporter Limitation**
- Blender's USD exporter with `selected_objects_only=True` exports objects with their **world matrices**, not respecting parent-child hierarchies
- This is why we must bake the fake parent's transform into children's world matrices before export

---

### What We've Tried (Version History)

**v0.1.60 - Initial Fake Parent Implementation**
- Created fake parent Empty object
- Parented collection objects to fake parent
- Applied normalization (position/scale/rotation) to fake parent
- **Problem**: Objects exported at wrong positions - exporter ignored parent hierarchy
- **Fix**: Added `_bake_fake_parent_transform_to_children()` to bake parent transform into children's world matrices before export

**v0.1.61 - Y-up Transform Skipping**
- **Problem**: Y-up coordinate system transform (Z-up → Y-up) was running AFTER baking, overwriting baked transforms
- **Fix**: Skip Y-up transform step for collection exports when fake parent exists

**v0.1.62 - matrix_parent_inverse Update**
- **Problem**: When fake parent is normalized (location/rotation/scale reset), Blender does NOT automatically update children's `matrix_parent_inverse` property
- **Root Cause**: `matrix_parent_inverse` defines the inverse of parent's transform at parenting time. When parent transforms change, this becomes stale, causing incorrect world matrix calculations
- **Fix**: Explicitly update `matrix_parent_inverse` for all children after normalization:
  ```python
  context.view_layer.update()  # Force update
  for child in children:
      child.matrix_parent_inverse = fake_parent.matrix_world.inverted()
  context.view_layer.update()  # Force update after changes
  ```
- **Result**: Still misaligned - "There is no difference"

---

### Current Implementation Workflow (from Implementation Plan)

Based on `22_IMPLEMENTATION_PLAN_CLEAN_Phase_14D.md`, our collection export flow is:

1. **Create fake parent** (if pivot mode != PRESERVE)
   - Blender Empty (Plain Axes) object
   - Positioned based on pivot mode (WORLD_ORIGIN, CUSTOM_XYZ, CURSOR, OBJECT, PRESERVE)

2. **Parent collection objects to fake parent**
   - All collection objects become children of fake parent
   - Store original parent relationships for restoration

3. **Apply normalization** (if enabled)
   - `normalize_position` → Reset fake parent location to (0,0,0)
   - `normalize_scale` → Reset fake parent scale to (1,1,1)
   - `normalize_rotation` → Reset fake parent rotation to (0,0,0)

4. **CRITICAL: Update `matrix_parent_inverse`** (v0.1.62)
   - After normalization, explicitly update all children's `matrix_parent_inverse`
   - Force `context.view_layer.update()` before and after

5. **Bake fake parent transform to children's world matrices**
   - Compute world matrix for each child (after parenting and normalization)
   - Unparent each child
   - Apply computed world matrix directly to child object
   - This is necessary because Blender USD exporter ignores parent hierarchies

6. **Export collection**
   - Use Blender's `bpy.ops.wm.usd_export()` with `selected_objects_only=True`
   - Objects now have correct world transforms baked in

7. **Restore original parent relationships**
   - Restore each object's original parent
   - Restore original world matrices

8. **Cleanup fake parent**
   - Delete the temporary Empty object

---

### What's Still Not Working

**Current Status (v0.1.62)**:
- Export completes successfully (no errors)
- All steps execute (fake parent created, objects parented, normalization applied, `matrix_parent_inverse` updated, transforms baked, export succeeds)
- Bug report shows all operations completed: `fake_parent_created`, `objects_parented_to_fake_parent`, `fake_parent_transform_baked`, `usd_export_success`
- **BUT**: Objects still appear scattered/misaligned/rotated incorrectly in exported USD file
- User feedback: "There is no difference" (between v0.1.61 and v0.1.62)

**Key Questions**:
1. Is our understanding of `matrix_parent_inverse` correct? Are we updating it at the right time?
2. Is our baking approach correct? Are we computing world matrices correctly after normalization?
3. Are we missing a step? Is there something Blender requires that we're not doing?
4. Is our fundamental approach flawed? Should we be doing this differently?

---

### Technical Context

**Blender Version**: 5.0.0
**Python Version**: 3.11.13
**USD API**: pxr (Pixar USD Python bindings)
**Test Collection**: `SHAKTI_Decals` (6 mesh objects with Shrinkwrap modifiers)

**Key Blender API Usage**:
- `bpy.data.objects.new()` - Create fake parent Empty
- `obj.parent = fake_parent` - Parent objects
- `obj.matrix_world` - Get world matrix
- `obj.matrix_parent_inverse` - Parent inverse matrix
- `context.view_layer.update()` - Force view layer update
- `bpy.ops.wm.usd_export()` - Export to USD

**Key Code Locations**:
- `ops_export.py` lines ~250-380: `_create_fake_parent_for_collection()`
- `ops_export.py` lines ~362-420: `_bake_fake_parent_transform_to_children()`
- `ops_export.py` lines ~423-470: `_restore_baked_transforms()`

---

### What We Need

**Expert Opinion On**:
1. Is our workflow correct? Are we missing a critical step?
2. Is our `matrix_parent_inverse` update correct? Are we doing it at the right time?
3. Is our world matrix baking approach correct? Are we computing matrices correctly?
4. Are there Blender-specific gotchas we're missing?
5. Should we be using a different approach entirely?

**Specific Technical Questions**:
- When should `matrix_parent_inverse` be updated relative to normalization?
- How do we verify that world matrices are correct before export?
- Is there a way to debug/visualize what Blender thinks the world matrices are?
- Are we correctly understanding how Blender computes world matrices from parent hierarchies?

---

**Files for Reference**:
- Implementation Plan: `22_IMPLEMENTATION_PLAN_CLEAN_Phase_14D.md`
- Quick Reference: `23_QUICK_REFERENCE_Phase_14D.md`
- Bug Report: `c:\Users\jan\AppData\Local\Temp\blender_a34232\usdme_bug_report_20260202_190302.json`
- Code: `blender_usd_multiexport_addon/ops_export.py`
- Best Practices: `Domain_Blender_Guardrails/080_Framework_RULES/best_practices/best_practices.yml`
- Anti-Patterns: `Domain_Blender_Guardrails/080_Framework_RULES/best_practices/anti_patterns.yml`
