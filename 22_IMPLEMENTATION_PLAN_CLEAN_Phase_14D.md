---
arys_schema_version: '1.2'
id: 9081fa62-ba01-4ecb-a07b-13c69b2b157b
title: Clean Implementation Plan - Object/Collection Export Path Isolation
type: TECHNICAL
status: active
trust_level: 2
visibility: internal
created: '2026-02-17T09:42:16Z'
last_modified: '2026-02-17T09:42:16Z'
---

# Clean Implementation Plan - Object/Collection Export Path Isolation

**Version**: 1.2.0 | **Date**: 03.02.2026 | **Time**: 17:20 | **GlobalID**: 20260203_1720_Blender_USD_MultiExport_22

**Purpose**: Clear, actionable plan to restore object export to v0.1.48 behavior and isolate collection export path.

**Tag block:**
#workflow_automation #export #usd_core #extension_development #blender #openusd #conversion #references #analysis #deterministic_workflows

---

## 🎯 Core Problem Statement

**Current State:**
- Object export path produces **broken normals** when modifiers are enabled (v0.1.53+)
- Collection export path (fake parent + normalization) is partially implemented but **leaking into object export**
- v0.1.48 is the last known-good version for object export

**Goal:**
- Restore object export to **exact v0.1.48 behavior** (isolated, no collection logic)
- Implement collection export as **completely separate path** (fake parent + optional normalization)
- Ensure **zero cross-contamination** between paths

---

## 📋 Implementation Strategy

### Phase 1: Establish Baseline (v0.1.48 Reference)

**Objective**: Understand exactly what v0.1.48 does for object export.

**Tasks:**
1. ✅ Extract v0.1.48 from `releases/blender_usd_multiexport_v0.1.48/`
2. ✅ Compare key files:
   - `ops_export.py` - Export orchestration
   - `usd_bake.py` - Normal transformation logic
   - `state_manager.py` - State handling
3. ✅ Document v0.1.48 object export flow:
   - How objects are selected/duplicated
   - How modifiers are applied
   - How mesh data is extracted
   - How normals are handled in bake step
   - How cleanup happens

**Deliverable**: Baseline comparison document showing v0.1.48 vs current differences.

---

### Phase 2: Isolate Object Export Path

**Objective**: Restore object export to v0.1.48 behavior, completely isolated from collection logic.

**Tasks:**

#### 2.1 Code Path Separation
- [ ] Identify all code branches that handle `OBJECT` vs `COLLECTION` start point types
- [ ] Create explicit early returns/guards for object export path
- [ ] Remove any collection-specific logic from object export flow
- [ ] Ensure object export **never** touches:
  - Fake parent creation
  - Collection normalization (position/scale/rotation)
  - Pivot mode logic
  - Collection-specific transforms

#### 2.2 Restore v0.1.48 Object Export Logic
- [ ] Copy object export flow from v0.1.48 `ops_export.py`
- [ ] Restore v0.1.48 `usd_bake.py` normal handling for object path
- [ ] Verify modifier application matches v0.1.48 exactly
- [ ] Ensure mesh data extraction matches v0.1.48

#### 2.3 Normal Handling Fix
- [ ] Review v0.1.48 normal transformation in `usd_bake.py`
- [ ] Compare with current broken behavior (v0.1.53+)
- [ ] Restore v0.1.48 normal transformation logic:
  - How normals are extracted from Blender
  - How normals are transformed (rotation only, no scaling)
  - How normals are normalized
  - When normals are recomputed vs preserved
- [ ] Ensure bake step **preserves authored normals** correctly

**Deliverable**: Object export path restored to v0.1.48 behavior, verified with modifier-enabled test.

---

### Phase 3: Implement Clean Collection Export Path

**Objective**: Build collection export path as completely separate implementation.

**Tasks:**

#### 3.0 Quick-Fix: Use Blender Apply + Set Origin (Collection Only)
**Status**: Proposed (fast path)  
**Rationale**: Normalization checkboxes exist in UI/props but the collection normalization pipeline is currently disabled in code. This quick-fix uses Blender's built-in apply transforms + set origin to make the toggles functional without re-enabling the fake-parent system.

**Scope**:
- Collection start points only.
- Object start points remain untouched.
- Works with existing UI toggles:
  - `normalize_position`
  - `normalize_rotation`
  - `normalize_scale`
  - `collection_pivot_source` (WORLD/CUSTOM/CURSOR/OBJECT)
  - `collection_pivot_only`

**Implementation Notes**:
- Use **temporary duplicates** of export objects to avoid destructive edits.
- Operate only inside the export isolation context.
- Always restore scene state and delete duplicates after export.
- Use Blender ops for apply/transform and origin setting (fast, reliable).

**Step-by-step plan (resume-friendly)**:
1. **Locate collection export entry point**  
   - File: `blender_usd_multiexport_addon/ops_export.py`  
   - Find the collection export path and insert a guarded block for normalization.
2. **Collect collection export objects (duplicates only)**  
   - Ensure we work on duplicated objects (current export already duplicates for modifiers).  
   - Build a list `export_objects` that represents exactly what will be exported.
3. **Resolve pivot target**  
   - WORLD: `(0,0,0)`  
   - CUSTOM: `start_point.collection_pivot_xyz`  
   - CURSOR: `context.scene.cursor.location`  
   - OBJECT: `start_point.collection_pivot_object.matrix_world.to_translation()`  
4. **Set origin (pivot)**  
   - Select `export_objects`, set active object.  
   - Use `bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')`  
   - For WORLD/CUSTOM/OBJECT: move 3D cursor to pivot, set origin to cursor.  
5. **Apply transforms**  
   - If `collection_pivot_only` is True: skip apply.  
   - Else apply based on checkboxes:  
     - `bpy.ops.object.transform_apply(location=normalize_position, rotation=normalize_rotation, scale=normalize_scale)`  
6. **Restore cursor**  
   - Save and restore the 3D cursor position to avoid user disruption.  
7. **Export**  
   - Use existing export selection logic; no changes to object export path.  
8. **Cleanup**  
   - Delete duplicates, restore selection/visibility states.

**Logging**:
- Add log steps for: pivot source, cursor move, origin set, apply transforms, and cleanup.

**Potential pitfalls**:
- Applying transforms is destructive: must be done only on duplicates.
- Ensure objects are in OBJECT mode before calling ops.
- Avoid applying transforms when `collection_pivot_only=True`.

**Deliverable**: Collection normalization checkboxes produce visible transform changes in exported USD without re-enabling fake-parent logic.

#### 3.1 Fake Parent Creation
- [ ] Create Blender Empty (Plain Axes) as fake parent
- [ ] Implement pivot mode logic:
  - `WORLD_ORIGIN` - Place at (0,0,0)
  - `CUSTOM_XYZ` - Place at custom coordinates
  - `CURSOR` - Place at 3D cursor location
  - `OBJECT` - Place at object pivot location
  - `PRESERVE` - Don't create fake parent (or place at collection origin)
- [ ] Parent all collection objects to fake parent
- [ ] Store fake parent reference for cleanup

#### 3.2 Optional Normalization
- [ ] Implement normalization only when enabled:
  - `normalize_position` - Reset fake parent location to origin
  - `normalize_scale` - Reset fake parent scale to (1,1,1)
  - `normalize_rotation` - Reset fake parent rotation to (0,0,0)
- [ ] **CRITICAL**: Do NOT update `matrix_parent_inverse` after normalization
  - Updating `matrix_parent_inverse` after normalization CANCELS the normalization effect
  - When fake parent is normalized to identity, setting `matrix_parent_inverse` to identity removes compensation offset
  - Result: normalization effect is canceled, children behave as before (explains "no difference" bug)
  - Only update `matrix_parent_inverse` if goal is "keep children fixed while parent changes" (NOT our use case)
- [ ] Apply normalization **before** export (Blender-side transform)
- [ ] Ensure normalization only affects fake parent, not individual objects
- [ ] **CRITICAL**: Use evaluated depsgraph matrices when reading `matrix_world`
  - `context.view_layer.update()` is often not enough
  - Use: `depsgraph = bpy.context.evaluated_depsgraph_get()`, `depsgraph.update()`, `obj.evaluated_get(depsgraph).matrix_world`
  - This ensures matrices are fully evaluated before baking

#### 3.3 Collection Export Flow

**Approach A: Fake Parent (Current)**
- [ ] Create separate export function for collections
- [ ] Flow:
  1. Create fake parent (if pivot mode != PRESERVE)
  2. Parent collection objects to fake parent (with correct `matrix_parent_inverse` at parenting time)
  3. Apply normalization (if enabled) - **DO NOT update `matrix_parent_inverse` after**
  4. **CRITICAL**: Use evaluated depsgraph to get world matrices before baking
  5. Bake fake parent transform to children's world matrices (due to Blender USD exporter limitation)
  6. Export collection (using Blender's collection export with `selected_objects_only=True` OR `collection=collection.name`)
  7. Restore original parent relationships
  8. Cleanup fake parent
- [ ] **CRITICAL**: Blender's USD exporter with `selected_objects_only=True` exports objects with world matrices, NOT respecting parent hierarchies
  - Must bake parent transform into children's world matrices before export
  - This is why we need `_bake_fake_parent_transform_to_children()` function
- [ ] **CRITICAL**: Export settings for debugging:
  - Use `xform_op_mode='MAT'` (matrix mode) to preserve exact transforms without TRS decomposition
  - Use `convert_orientation=False` to avoid double axis conversion
  - These settings help identify if rotation differences are from decomposition vs actual transform errors

**Approach B: Direct Matrix Multiplication (Simpler Alternative)**
- [ ] **Consider**: Simpler approach without parenting/unparenting:
  1. Capture each object's evaluated world matrix `W_i` using depsgraph
  2. Compute group transform `G` (based on pivot mode + normalization)
  3. Set `obj.matrix_world = G @ W_i` for each object (on temporary duplicates)
  4. Export selected objects only
  5. Restore
- [ ] Benefits: No parent, no parent inverse, no unparenting surprises
- [ ] `G` is typically the inverse of the pivot transform you would have put on fake parent

- [ ] Ensure collection export **never** touches object export logic

**Deliverable**: Collection export path working independently, verified with decals test.

---

### Phase 4: Verification & Testing

**Objective**: Verify both paths work correctly and are isolated.

**Tasks:**

#### 4.1 Object Export Verification
- [ ] Test object export with modifiers **enabled**:
  - Use test asset: `FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002`
  - Compare normals with v0.1.48 output
  - Verify normals match exactly
- [ ] Test object export with modifiers **disabled**:
  - Verify still works correctly
- [ ] Verify object export **ignores** collection settings:
  - Collection normalization settings should not affect object export
  - Collection pivot settings should not affect object export

#### 4.2 Collection Export Verification
- [ ] Test collection export (decals):
  - Use test asset: `SHAKTI_Decals` collection
  - Verify fake parent is created correctly
  - Verify normalization works when enabled
  - Verify pivot modes work correctly
- [ ] Verify collection export **does not affect** object export:
  - Export collection, then export object
  - Object export should be unaffected

#### 4.3 Cross-Contamination Tests
- [ ] Export object with collection settings visible in UI
- [ ] Export collection with object settings visible in UI
- [ ] Verify settings don't leak between paths
- [ ] Verify state cleanup doesn't affect other path

**Deliverable**: Both paths verified working independently, no cross-contamination.

---

## 🔍 Key Files to Modify

### Primary Files
1. **`blender_usd_multiexport_addon/ops_export.py`**
   - Separate `_export_object()` and `_export_collection()` functions
   - Add early returns/guards to prevent cross-contamination
   - Restore v0.1.48 object export logic

2. **`blender_usd_multiexport_addon/usd_bake.py`**
   - Restore v0.1.48 normal handling for object path
   - Ensure normals are preserved correctly when authored
   - Separate normal handling for collection path (if needed)

3. **`blender_usd_multiexport_addon/state_manager.py`**
   - Ensure state cleanup doesn't affect other export type
   - Separate state tracking for object vs collection

### Reference Files
- **`releases/blender_usd_multiexport_v0.1.48/`** - Baseline reference
- **`80_WIP_notes.md`** - Bug reports and findings
- **`02_Detailed_Requirements.md`** - REQ-EXP-022 to REQ-EXP-025

---

## 🚨 Critical Rules

1. **Object Export Path:**
   - Must match v0.1.48 **exactly**
   - No collection logic allowed
   - No normalization logic allowed
   - No fake parent logic allowed

2. **Collection Export Path:**
   - Completely separate implementation
   - Uses fake parent + optional normalization
   - Does not modify object export behavior
   - **CRITICAL**: Do NOT update `matrix_parent_inverse` after normalization (cancels effect)
   - **CRITICAL**: Use evaluated depsgraph matrices when reading `matrix_world`
   - **CRITICAL**: Export with `xform_op_mode='MAT'` and `convert_orientation=False` for debugging

3. **Isolation:**
   - Early returns/guards at function entry
   - Separate functions for each path
   - No shared state that could leak
   - Clean state management

4. **Normal Handling:**
   - Preserve authored normals (don't recompute)
   - Transform normals correctly (rotation only)
   - Normalize transformed normals
   - Match v0.1.48 behavior exactly

5. **Matrix Evaluation:**
   - Always use evaluated depsgraph when reading matrices for baking
   - `context.view_layer.update()` is often not enough
   - Pattern: `depsgraph = bpy.context.evaluated_depsgraph_get()`, `depsgraph.update()`, `obj.evaluated_get(depsgraph).matrix_world`

---

## 📝 Implementation Checklist

### Phase 1: Baseline
- [ ] Extract and review v0.1.48 code
- [ ] Document v0.1.48 object export flow
- [ ] Compare with current implementation
- [ ] Identify differences causing broken normals

### Phase 2: Object Export Fix
- [ ] Separate object/collection code paths
- [ ] Restore v0.1.48 object export logic
- [ ] Fix normal handling in bake step
- [ ] Test with modifier-enabled export
- [ ] Verify normals match v0.1.48

### Phase 3: Collection Export
- [ ] Implement fake parent creation
- [ ] Implement pivot mode logic
- [ ] Implement optional normalization (without updating `matrix_parent_inverse` after)
- [ ] Use evaluated depsgraph matrices when baking
- [ ] Set export settings: `xform_op_mode='MAT'`, `convert_orientation=False`
- [ ] Create separate collection export function
- [ ] Test collection export independently
- [ ] **Optional**: Consider simpler approach (direct matrix multiplication without parenting)

### Phase 4: Verification
- [ ] Test object export (modifiers enabled/disabled)
- [ ] Test collection export (all pivot modes)
- [ ] Test cross-contamination scenarios
- [ ] Verify state cleanup
- [ ] Create test release (v0.1.56)

---

## 🎯 Success Criteria

1. ✅ Object export with modifiers enabled produces **identical normals** to v0.1.48
2. ✅ Object export path has **zero collection logic**
3. ✅ Collection export path works independently with fake parent + normalization
4. ✅ No cross-contamination between paths
5. ✅ Both paths can be used in same session without interference

---

## 📚 Reference Materials

- **Baseline**: `releases/blender_usd_multiexport_v0.1.48/`
- **Requirements**: `02_Detailed_Requirements.md` (REQ-EXP-022 to REQ-EXP-025)
- **Design**: `03_Module_Design.md`
- **Implementation Plan**: `04_Implementation_Plan.md` (Phase 14D)
- **Bug Reports**: `80_WIP_notes.md` (includes expert second opinion analysis)
- **Handoff**: `99_HANDOFF.md`

## 🔍 Expert Second Opinion Findings

**Key Corrections Based on Expert Analysis:**
1. **`matrix_parent_inverse` update is BACKWARDS** - Updating after normalization cancels the effect
2. **Use evaluated depsgraph matrices** - `matrix_world` may not be fully evaluated
3. **Export settings matter** - Use `xform_op_mode='MAT'` and `convert_orientation=False` for debugging
4. **Simpler alternative exists** - Direct matrix multiplication without parenting/unparenting
5. **Collection export parameter** - Try `collection=collection.name` instead of `selected_objects_only=True`

See `80_WIP_notes.md` section "Expert Second Opinion: Root Cause Analysis" for full details.

---

**Next Steps**: Start with Phase 1 - establish baseline by comparing v0.1.48 with current implementation. Then apply expert corrections to Phase 3 collection export implementation.
