# WIP Notes

## 2026-02-03 v0.1.87 – Gray out Normalize Scale / Normalize Rotation (upcoming feature)

**Context:** Normalize Scale and Normalize Rotation still caused broken decals (wrong position/scale/rotation). User requested to gray them out, label “Upcoming feature”, and document in the implementation plan with notes on why it breaks.

**Changes:**
- **UI (`ui.py`):** Normalize Scale and Normalize Rotation are in a disabled row (grayed out). Added row “Upcoming feature — 04_Implementation_Plan.md”.
- **Props (`props.py`):** Descriptions for both options note they are disabled (upcoming) and reference 04_Implementation_Plan.md.
- **Export (`ops_export.py`):** In `_apply_collection_normalization_quickfix`, `normalize_rotation` and `normalize_scale` are forced to `False`. In the bake call, `normalize_child_xforms` is always `False` (no post-export child-xform normalization until the feature is fixed).
- **Implementation plan (`04_Implementation_Plan.md`):** New section “🔮 Upcoming: Normalize Scale / Normalize Rotation” with: why it breaks (Blender-side + USD post-pass), what needs to be done (Blender-side consistency, USD bake logic, testing, re-enable steps), and links to Discovery/WIP.
- **Discovery / WIP:** Updated known limitation and added link to 04_Implementation_Plan.md.

**Result:** Users see the options grayed out with “Upcoming feature”; export never uses Normalize Scale/Rotation; implementation plan documents root cause and fix path.

**Fix (no version bump):** v0.1.86 was missing the transform on the default prim. An attempt to only add xform when `default_prim.IsA(UsdGeom.Xformable)` was reverted: it caused both object and collection default prims to lose their transform (everything 100× too small). Restored original logic: always use `UsdGeom.Xformable(default_prim)` and add translate/rotate/scale when the wrapper is valid.

---

## 2026-02-03 v0.1.86 – Disable USD child-xform normalization for COLLECTION exports

**Context:** After v0.1.85, enabling **Normalize Scale** and **Normalize Rotation** for a collection (e.g. SHAKTI_Decals) still produced wrong decals: same broken position/rotation/scale (e.g. scale ~-0.3, tiny translate). The post-export bake no longer crashes but its result is incorrect for collection children.

**Change:** In `ops_export.py`, when the start point is **COLLECTION**, `normalize_child_xforms` is now forced to `False` before calling `bake_usd_geometry()`. **OBJECT** exports are unchanged: they still use normalize rotation/scale to drive the USD post-pass when the user enables those options.

**Result:** Collection exports no longer run the problematic USD child-xform normalization; decals rely on Blender’s pre-export `transform_apply` only. Object exports keep post-export normalization. Documented in WIP and (if present) discovery as a known limitation until the bake logic for collection hierarchies is fixed.

**Follow-up (v0.1.87):** Normalize Scale and Normalize Rotation are grayed out in the UI and forced off in export logic (upcoming feature). Rationale and implementation plan: **04_Implementation_Plan.md** → section “🔮 Upcoming: Normalize Scale / Normalize Rotation”.

---

## 2026-02-03 v0.1.85 – GetDescendants crash (Blender USD) + collection scale

**Context:** With all normalize options on for SHAKTI_Decals (collection), export crashed with `AttributeError: 'Prim' object has no attribute 'GetDescendants'`. The bake step never completed, so: (1) collection file was never saved with default-prim xform or scale → decals appeared 100× too small; (2) normalize rotation/scale in USD never ran.

**Cause:** Blender 5.0’s bundled USD does not provide `Usd.Prim.GetDescendants()` (that API exists in newer USD only).

**Fix (v0.1.85):**
- **usd_bake.py:** Replaced all use of `prim.GetDescendants()` with a recursive helper `_iter_prim_descendants(prim)` that uses only `GetChildren()` so it works with Blender’s USD.
- `_has_mesh_descendant` and `_get_descendant_meshes` now use `_iter_prim_descendants`.

**Result:** Bake completes for collection exports; default prim gets translate/rotate/scale; mesh points get scale_factor; when Normalize Rotation/Scale are on, child prim xforms are normalized in USD. Decals should match boat scale when both use the same target units (e.g. CENTIMETERS).

---

## 2026-02-03 v0.1.84 – Post-export USD xform normalization

**Context:** User reported that in Omniverse, exported child prims (e.g. `SPADE_2b_Outline_Petrol_LEFT`) showed non-zero rotation and non-unit scale (e.g. scale ~-0.30119), even when “normalize” was expected. Translate had a tiny rounding error (acceptable).

**Cause:** Normalization ran only in Blender (`transform_apply` on the export set before USD export). If **Normalize Rotation** or **Normalize Scale** were unchecked, or apply was skipped, the USD kept original transforms. The post-export bake only set the **default prim**; it did not reset **child** prim xforms.

**Changes (v0.1.84):**

1. **Post-export USD normalization** (`usd_bake.py`):
   - New parameter `normalize_child_xforms=False` on `bake_usd_geometry()`.
   - When True (driven by start point **Normalize Rotation** or **Normalize Scale**): after the existing bake, traverse all non-default Xformable prims that have mesh descendants (post-order); for each, get local transform, bake it into descendant mesh points/normals, then set that prim’s xform to identity (translate 0, rotate 0, scale 1).
   - Helpers: `_has_mesh_descendant`, `_get_descendant_meshes`, `_bake_matrix_into_mesh`, `_collect_xformable_with_mesh_descendants_postorder`.

2. **Export operator** (`ops_export.py`):
   - When calling `bake_usd_geometry()`, pass `normalize_child_xforms = (normalize_rotation or normalize_scale)` from the start point.

3. **Docs and UI:**
   - **00_Discovery.md:** New subsection “Why rotation/scale can look non-normalized in USD (Omniverse)” – user must enable Normalize Rotation and Normalize Scale for identity in USD; v0.1.84 adds post-export bake so child prims get identity when those options are on.
   - **props.py:** Normalize Scale and Normalize Rotation descriptions updated to mention post-export bake (child prim scale/rotation set in USD).

**Build:** `releases/blender_usd_multiexport_v0.1.84.zip` (8 files, ~52 KB).

**Usage:** Enable **Normalize Rotation** and **Normalize Scale** (and **Normalize Position** if desired) on the start point; re-export. In Omniverse, child prims should show Rotate (0,0,0) and Scale (1,1,1).

---

## 2026-02-03 Pivot Reset Script (Omniverse Kit) – BEP Notes

**Context:** Standalone script `SANDBOX SCRIPTS/normalize_pivot_reset.py` to “reset” the default prim to identity while keeping children visually correct (wrapper trick: move children into a temp Xform, zero default prim, set wrapper to -90° X, copy children back with world transform baked). Script is run **inside Omniverse Kit** (Script Editor). Same overall goal as addon bake (default prim at identity, decals correct); this script is for testing/post-process on existing USDA.

**Goal:** After edits, default prim has identity transform; each child’s local transform = its previous world transform (so scene looks unchanged). No manual Euler composition—use full 4x4 or hierarchy trick.

### Approaches tried and why they failed (Kit)

1. **Iterate `default_prim.GetChildren()` then copy/remove in a loop**  
   **Why it failed:** After the first `_remove_prim(stage, src)`, the stage changed and remaining `child_prim` references from the initial `GetChildren()` became invalid. Next use raised `RuntimeError: Accessed invalid expired 'Xform' prim`.  
   **Lesson:** Collect only **names** (or paths) before any edits; never hold `UsdPrim` references across stage/layer edits in a loop.

2. **Use `UsdGeom.XformCache(TimeCode).GetLocalToWorldTransform(prim)` on the edited stage**  
   **Why it failed:** In Kit, after edits and `stage.Reload()`, calling the cache (or passing prims from `GetChildren()`/`GetPrimAtPath`) caused `RuntimeError: Accessed invalid null prim`.  
   **Lesson:** In Kit, XformCache and “get world transform” on the **edited** stage can hit invalid/null prims; avoid using the stage for transform **queries** after heavy edits.

3. **Export layer to temp file, open as read-only stage, run XformCache there**  
   **Why it failed:** Same “Accessed invalid null prim” when calling `GetLocalToWorldTransform(prim)` on the **read-only** stage opened from the temp file. Kit’s USD stack appears to throw for that API in this context.  
   **Lesson:** In this environment, avoid relying on XformCache / `ComputeLocalToWorldTransform` for this workflow.

4. **Use `UsdGeom.Xformable(prim).GetLocalTransformation(time)` on the edited stage**  
   **Why it failed:** Still “Accessed invalid null prim”. Any use of the stage to get a prim at a path (after Reload) and then call UsdGeom on it could trigger the error.  
   **Lesson:** For **reading** transforms in this script, don’t use the stage at all after the hierarchy has been rewritten.

5. **Use `Usd.NamespaceEditor(stage).DeletePrimAtPath(path)` for all removals**  
   **Why it failed:** After layer edits (e.g. `Sdf.CopySpec`, setting xform on the layer), the stage considered the prim at that path “not a valid prim”. NamespaceEditor reported: “Failed to apply edits to the stage because of the following errors: The prim to edit is not a valid prim”.  
   **Lesson:** For **removing** prims after mixed stage/layer edits in Kit, don’t use NamespaceEditor; remove via the **layer** only.

### Approach that works (Kit-safe)

- **Step 5 (snapshot world transforms):**  
  - Do **not** re-query child list from the stage after `Reload()`. Reuse the list of child **names** saved in step 2 (`moved_child_names`).  
  - Do **not** use the stage or UsdGeom to read transforms. Read each child’s **local** transform from the **Sdf layer** only (`_local_transform_from_layer(layer, child_path)`), then compute `world = wrapper_matrix * local` (wrapper_matrix = -90° X).  
  - Write the new child transform on the **layer** only (`_set_xform_to_matrix_on_layer(layer, dst, world_xform)`).

- **All prim removals:**  
  - Do **not** use `Usd.NamespaceEditor`. Remove prims via the **layer** only: `_remove_prim_via_layer(layer, path)` using `parent_spec.RemoveNameChild(child_name)`.

**Summary:** In Omniverse Kit, after editing the layer (CopySpec, authoring xforms), the stage can hand out invalid prims and NamespaceEditor can refuse to delete “the prim to edit”. For this script, **all post–Reload reads and writes of transforms, and all prim removals, go through the Sdf layer only**; the stage is used only for opening the file, reading the default prim and its children once, and defining the wrapper Xform (steps 1–4). No XformCache, no GetLocalToWorldTransform, no GetLocalTransformation on the edited stage, no NamespaceEditor for delete.

---

## 2026-02-02 Export Test (v0.1.51)

### User Report (Visual)
- Object (hull) points the wrong way.
- Normals still broken.
- Decals were not normalized for this run.

### Log File
- Bug report: `c:\Users\jan\AppData\Local\Temp\blender_a39736\usdme_bug_report_20260202_133623.json`
- Export summary from log:
  - Start points: `SHAKTI_Decals` (COLLECTION), `FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002` (OBJECT).
  - Scene/Addon: Blender 5.0.0, USD Multi Export `0.1.51`.
  - Target settings (both):
    - `source_unit=METERS`, `target_unit=CENTIMETERS`, `y_is_up=True`
    - `scale_factor=100.0`, `meters_per_unit=0.01`, `up_axis=Y`
  - Collection normalization (decals):
    - `normalize_position=False`, `normalize_scale=False`, `normalize_rotation=False`
    - `pivot_only=True`, `pivot_source=OBJECT`
  - Bake results:
    - Decals: `meshes_processed=6`, `points_baked=22696`, `normals_baked=75461`, `xforms_cleared=6`
    - Hull: `meshes_processed=1`, `points_baked=48707`, `normals_baked=194080`, `xforms_cleared=0`
  - Export sizes:
    - `SHAKTI_Decals.usda`: `6,284,712` bytes
    - `FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002.usda`: `29,919,473` bytes

### USDA Metadata (no points/verts)
Files reviewed:
- `d:\SPADEKAYAKS\070_RuD_Product development\Hard Goods\Boats\SP_W012_2025Shakti\010_ASS_USD\USD_Startpoint\FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002.usda`
- `d:\SPADEKAYAKS\070_RuD_Product development\Hard Goods\Boats\SP_W012_2025Shakti\010_ASS_USD\USD_Startpoint\SHAKTI_Decals.usda`
- `d:\SPADEKAYAKS\070_RuD_Product development\Hard Goods\Boats\SP_W012_2025Shakti\010_ASS_USD\USD_Startpoint\SHAKTI_ROOT TEST.usda`

#### `FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002.usda`
- Header:
  - `defaultPrim = "FULL_HOUSE_SMALL_SP_W012_v07_270x68_002_PRODUCTION251207_SHAKTI_002"`
  - `doc = "Blender v5.0.0"`
  - `metersPerUnit = 0.01`
  - `upAxis = "Y"`
- Root prim:
  - `def Xform "FULL_HOUSE_SMALL_SP_W012_v07_270x68_002_PRODUCTION251207_SHAKTI_002"`
  - `customData` includes `dictionary Blender { bool generated = 1 }`
  - `custom string usdme:export_timestamp = "2026-02-02T13:36:14.781623"`
- `xformOpOrder` not found via `rg` (may be absent or defined deeper in file).

#### `SHAKTI_Decals.usda`
- Header:
  - `defaultPrim = "SHAKTI_Decals"`
  - `doc = "Blender v5.0.0"`
  - `metersPerUnit = 0.01`
  - `upAxis = "Y"`
- Example prim (Shakti_ImageLogo):
  - `custom string userProperties:blender:object_name = "Shakti_ImageLogo"`
  - `xformOp:rotateXYZ = (0, -0, -179.99997)`
  - `xformOp:scale = (1, 1, 1)`
  - `xformOp:translate = (-8.922879324302357e-9, 1.071718454360962, 0.2915722727775574)`
  - `xformOpOrder = []`

#### `SHAKTI_ROOT TEST.usda`
- Header:
  - `defaultPrim = "World"`
  - `metersPerUnit = 0.009999999776482582`
  - `upAxis = "Y"`
- Root prim `World`:
  - Contains `Mesh "Cube"` with `xformOp` translate/rotate/scale.
  - References:
    - `Xform "SHAKTI_Decals"` -> `@./SHAKTI_Decals.usda@`
    - `Xform "SHAKTI_002"` -> `@./FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002.usda@`
  - Both referenced Xforms carry identity rotate/scale/translate with `xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]`.

## 2026-02-02 Export Test (v0.1.51) - Normalize Enabled

### User Report (Visual)
- Result looks totally similar to the non-normalized run.

### Log File
- Bug report: `c:\Users\jan\AppData\Local\Temp\blender_a39736\usdme_bug_report_20260202_135058.json`
- Collection normalization settings (decals):
  - `normalize_position=True`, `normalize_scale=True`, `normalize_rotation=True`
  - `pivot_only=True`, `pivot_source=OBJECT`
- Other key settings and bake results match the earlier run (same units, `scale_factor=100.0`, `y_is_up=True`, same meshes/points/normals counts).

### Note
- Because `pivot_only=True`, normalization toggles may be effectively bypassed in the Blender-side pre-pass (per current logic), which could explain the unchanged output.

## 2026-02-02 14:01 - v0.1.52 Prep

- Updated bake rotation to -90° around X for Z-up → Y-up conversion.
- Built release: `releases/blender_usd_multiexport_v0.1.52.zip`.
- Documentation timestamps refreshed per user request.

## 2026-02-02 Export Test (v0.1.52)

### User Report (Visual)
- Hull rotation correct.
- Normals broken.

### Log File
- Bug report: `c:\Users\jan\AppData\Local\Temp\blender_a44568\usdme_bug_report_20260202_140906.json`
- Summary:
  - Start points: `SHAKTI_Decals` (COLLECTION), `FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002` (OBJECT)
  - Scene/Addon: Blender 5.0.0, USD Multi Export `0.1.52`
  - Target settings: `source_unit=METERS`, `target_unit=CENTIMETERS`, `y_is_up=True`, `scale_factor=100.0`

### Baseline Reference
- User provided unzipped `releases/blender_usd_multiexport_v0.1.48` as last known working version.

## 2026-02-02 Export Test (v0.1.53) - Modifiers Enabled

### User Report (Visual)
- Exporting with modifiers enabled produces broken normals.

### Log File
- Bug report: `c:\Users\jan\AppData\Local\Temp\blender_a37280\usdme_bug_report_20260202_144135.json`
- Summary:
  - Start points enabled: 1 (OBJECT: `FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002`)
  - Scene/Addon: Blender 5.0.0, USD Multi Export `0.1.53`
  - Modifiers: `Mirror`, `Subdivision` (`export_modifiers_enabled=True`)
  - Target settings: `source_unit=METERS`, `target_unit=CENTIMETERS`, `y_is_up=True`, `scale_factor=100.0`
  - Bake results: `meshes_processed=1`, `points_baked=48707`, `normals_baked=194080`, `xforms_cleared=0`

### USDA Provided
- `d:\SPADEKAYAKS\070_RuD_Product development\Hard Goods\Boats\SP_W012_2025Shakti\010_ASS_USD\USD_Startpoint\FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002.usda`

## 2026-02-02 v0.1.56-0.1.59 - Object Export Restoration

### Problem
- Object export with modifiers enabled produced broken normals (v0.1.53+)
- User reported visual artifacts and versioning discrepancies

### Solution
- Restored object export behavior to match v0.1.48 (known-good version)
- Fixed normal transformation: restored correct inverse transpose matrix application
- Fixed rotation direction for Z-up → Y-up conversion
- Ensured collection export logic doesn't leak into object export path
- Updated version tracking in `__init__.py` to match actual version

### Key Changes
- `usd_bake.py`: Restored correct normal transformation matching v0.1.48
- `ops_export.py`: Isolated object export path from collection export logic
- Version updates: 0.1.56 → 0.1.57 → 0.1.58 → 0.1.59

### Documentation
- Updated `best_practices.yml` with "USD Export: Two-Step Transform Approach (v0.1.48+)"
- Updated `anti_patterns.yml` with:
  - Anti-pattern #10: "Transforming Geometry in Blender Before Export"
  - Anti-pattern #11: "Complex Normal Inversion Detection and Recomputation"
  - Anti-pattern #12: "Using Wrong Rotation Direction for Z-up → Y-up Conversion"
  - Anti-pattern #13: "Leaking Collection Logic into Object Export Path"

### Note
- Omniverse viewer may require restart after loading USD files to display correctly (known viewer quirk)

## 2026-02-02 v0.1.60 - Collection Export Fix

### Problem
- Collection export with fake parent approach produced scattered/misaligned objects
- User report: "Apart from the scale, everything is wrong. As if our whole approach to set the fake parent and create a transform matrix for the collection inside Blender just didn't work."
- Bug report: `c:\Users\jan\AppData\Local\Temp\blender_a46568\usdme_bug_report_20260202_182303.json`

### Root Cause
- Blender's USD exporter doesn't respect parent hierarchies when exporting with `selected_objects_only=True`
- Exporter writes each object's world matrix, not its local matrix relative to parent
- Fake parent transform was not being applied to exported objects

### Solution
- Added `_bake_fake_parent_transform_to_children()`: Bakes fake parent's transform into each child's world transform before export
- Added `_restore_baked_transforms()`: Restores original parent relationships after export
- Integration: Baking happens after fake parent creation, restoration happens before cleanup

### Key Changes
- `ops_export.py`:
  - New function: `_bake_fake_parent_transform_to_children()` - computes world matrix for each child, clears parent, applies world matrix directly
  - New function: `_restore_baked_transforms()` - restores parent relationships
  - Updated `_cleanup_fake_parent()` - fixed error handling to use string names instead of object references
  - Integrated baking/restoration into export flow (normal and exception paths)

### ZIP Packaging Fix
- Fixed ZIP structure: `__init__.py` must be inside `blender_usd_multiexport_addon/` directory, not at root
- Excluded `__pycache__` directories from release zip
- Updated zip creation to compress from parent directory to preserve directory structure

### Version
- Updated to v0.1.60
- Release: `releases/blender_usd_multiexport_v0.1.60.zip`

### USDA Mesh Notes (Normals)
- File is only 38 lines; mesh data is packed into oversized single-line arrays.
- Mesh block: `def Mesh "__USDME_MESH___USDME_MESH_FULL_HOUSE_SMALL_SP_W012_v07_270x68__004"`.
- Readable attributes inside mesh block:
  - `uniform bool doubleSided = 1`
  - `float3[] extent = [(-0.33993986, -1.2883986, -0.008121874), (0.3399398, 1.4162335, 0.42633197)]`
  - `rel material:binding = </FULL_HOUSE_SMALL_SP_W012_v07_270x68_002_PRODUCTION251207_SHAKTI_002/_materials/Orange_Plastic_035>`
- The `points`/`faceVertex*`/`normals` arrays appear to be authored as single-line attributes that exceed the read limit, so their contents can't be displayed here; normals are therefore authored in the file (not computed on load).

## 2026-02-02 USDA Comparison (Normals)

### Files
- Broken normals: `FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002 - NORMALS BROKEN_V0153.usda`
- Working normals: `FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002 - Normals Working v0148.usda`

### Findings
- `points` count: `48707` (both)
- `faceVertexCounts` count: `48520` (both)
- `faceVertexIndices` count: `194080` (both)
- `normals` count: `194080` (both)
- `normals:interpolation` not authored in either file; by count it matches `faceVertexIndices` (likely faceVarying).
- Sample normals differ between files even though counts match.

## 2026-02-02 v0.1.54 - Normals Fix Attempt

### Finding
- `NORMALS BROKEN_V0153` and `Normals Working v0148` have identical topology and counts, but different normal values.

### Adjustment
- Bake now preserves authored normals (transform + normalize) and only recomputes normals if none are authored.

## 2026-02-02 v0.1.55 - Normals Flip Detection

### Adjustment
- After transforming authored faceVarying normals, sample dot products vs computed face normals.
- If the average dot is negative (global inversion), flip all normals.

## 2026-02-02 Export Test (v0.1.53) - Modifiers Disabled

### User Report (Visual)
- When modifiers are not exported, normals look OK.

### Log File
- Bug report: `c:\Users\jan\AppData\Local\Temp\blender_a37280\usdme_bug_report_20260202_144553.json`
- Summary:
  - Start points enabled: 1 (OBJECT: `FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002`)
  - Scene/Addon: Blender 5.0.0, USD Multi Export `0.1.53`
  - Modifiers: disabled (`export_modifiers_enabled=False`)
  - Target settings: `source_unit=METERS`, `target_unit=CENTIMETERS`, `y_is_up=True`, `scale_factor=100.0`
  - Bake results: `meshes_processed=1`, `points_baked=3034`, `normals_baked=0`, `xforms_cleared=0`

### USDA Provided
- `d:\SPADEKAYAKS\070_RuD_Product development\Hard Goods\Boats\SP_W012_2025Shakti\010_ASS_USD\USD_Startpoint\FULL HOUSE_SMALL_SP W012_v07 270x68.002_PRODUCTION251207_SHAKTI.002.usda`

## 2026-02-02 v0.1.62 - Partial Success: Position Works, Scale/Rotation Don't

### Problem
- Collection export with fake parent approach produces partially correct results
- **What WORKS**: Position (translate) is correct - objects maintain spatial relationships, parent prim transform preserves positions
- **What DOESN'T WORK**: Scale is always (1,1,1) - scale is lost, Rotation values are present but incorrect

### Analysis of Exported USD File Structure

**Root Xform "SHAKTI_Decals":**
- Has `xformOp:rotateXYZ = (-90, 0, 0)` - This is the Y-up coordinate conversion
- `xformOpOrder = ["xformOp:rotateXYZ"]` - Only rotation, no translate/scale

**Child Xforms (e.g., "Shakti_WordLogo__RIGHT"):**
- `xformOp:translate = (-0.19599999487400055, 0.8750000596046448, 0.27000001072883606)` ✅ **CORRECT**
- `xformOp:rotateXYZ = (26, -1.5000006, -102.00001)` ❌ **INCORRECT**
- `xformOp:scale = (1, 1, 1)` ❌ **INCORRECT** (should preserve original scale)
- `xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]`

### Root Cause: Matrix Decomposition Issue

**Current Approach (v0.1.62):**
```python
# Get world matrix (includes parent transform)
world_matrix = obj_ref.matrix_world.copy()

# Clear parent
obj_ref.parent = None

# Apply world matrix directly to object
obj_ref.matrix_world = world_matrix  # ⚠️ PROBLEM HERE
```

**The Problem:**
When setting `obj_ref.matrix_world = world_matrix` directly, Blender automatically decomposes the matrix into:
- `location` (translate) ✅ Works correctly
- `rotation_euler` (rotation) ❌ Decomposition can be ambiguous (gimbal lock, multiple solutions)
- `scale` ❌ Can be lost or normalized to (1,1,1) if combined with rotation

**Why Scale is Lost:**
- Matrix decomposition with rotation can produce scale values that Blender normalizes
- Non-uniform scale combined with rotation is particularly problematic
- Blender's decomposition algorithm may prioritize rotation over scale

**Why Rotation is Wrong:**
- Matrix-to-Euler decomposition is ambiguous (gimbal lock)
- Multiple Euler angle solutions exist for the same rotation matrix
- Blender may choose a different solution than expected

### Comparison with USD codeNIM MCP Approach

**USD codeNIM MCP Suggested:**
```python
world_matrix = child.matrix_world.copy()
child.parent = None
inverse_fake_parent_matrix = fake_parent.matrix_world.inverted()
child.matrix_world = world_matrix * inverse_fake_parent_matrix  # ⚠️ WRONG for our use case
```

**Why MCP Approach is Wrong:**
- Multiplying by inverse would REMOVE the fake parent's transform
- We want to KEEP the parent transform in the child's world matrix
- This would make objects export at wrong positions

**However, MCP's suggestion highlights:**
- We might need to decompose the matrix ourselves instead of letting Blender do it
- We might need to preserve scale and rotation separately before decomposition

### Key Learnings

1. **Position Works Because:**
   - Translate is the most straightforward component of matrix decomposition
   - Blender correctly extracts translation from world matrix
   - Spatial relationships are preserved because translate values are correct

2. **Scale Fails Because:**
   - Setting `matrix_world` directly causes Blender to decompose, which can lose scale
   - Scale combined with rotation in a matrix is difficult to decompose accurately
   - Blender may normalize scale to (1,1,1) when decomposition is ambiguous

3. **Rotation Fails Because:**
   - Matrix-to-Euler decomposition is ambiguous (gimbal lock)
   - Multiple Euler solutions exist for the same rotation matrix
   - Blender may choose a different solution than what we expect

4. **The Solution May Be:**
   - Decompose the matrix ourselves using a more robust method
   - Preserve scale and rotation separately before setting matrix_world
   - Or use `matrix_local` instead of `matrix_world` if we can compute it correctly
   - Or export the matrix directly as a `matrix4d xformOp:transform` instead of decomposed xformOps

### Next Steps

1. **Investigate Matrix Decomposition:**
   - Use `mathutils.Matrix.decompose()` to manually decompose the matrix
   - Compare with Blender's automatic decomposition
   - Test if manual decomposition preserves scale and rotation better

2. **Alternative: Use matrix4d Transform:**
   - Instead of decomposed xformOps (translate, rotate, scale), use `matrix4d xformOp:transform`
   - This would preserve the exact transform without decomposition ambiguity
   - But requires post-processing the USD file after export

3. **Alternative: Compute Local Matrix:**
   - Instead of world matrix, compute local matrix relative to fake parent
   - Export with parent hierarchy intact (but Blender exporter doesn't respect this)
   - Or compute local matrix and apply it differently

### Version
- Current: v0.1.62
- Bug Report: `c:\Users\jan\AppData\Local\Temp\blender_a47192\usdme_bug_report_20260202_191721.json`
- USD File: `d:\SPADEKAYAKS\070_RuD_Product development\Hard Goods\Boats\SP_W012_2025Shakti\010_ASS_USD\USD_Startpoint\SHAKTI_Decals.usda`

## 2026-02-02 - Expert Second Opinion: Root Cause Analysis

### Source
- Expert consultation via prompt in `99_HANDOFF.md` Appendix
- Consultation focused on collection export matrix decomposition issues

### Key Findings

#### 1. **CRITICAL: `matrix_parent_inverse` Update is BACKWARDS**

**The Problem:**
- Our v0.1.62 approach updates `matrix_parent_inverse` after normalization
- **This CANCELS the normalization effect**, explaining "no difference" feedback
- When fake parent is normalized to identity (location 0, rot 0, scale 1):
  - `fake_parent.matrix_world.inverted()` = identity matrix
  - Setting children's `matrix_parent_inverse` to identity **removes the compensation offset**
  - Result: normalization effect is canceled, children behave as before

**Correct Understanding:**
- `matrix_parent_inverse` is part of the parent-child relationship
- If normalization is meant to **move the whole collection** (group transform), you **do NOT** want to "fix" parent inverse after moving the parent
- Leaving existing relationship intact makes children inherit parent's new transform
- Only update parent inverse if goal is "parent changed but child must visually stay where it is"

**Action:** Remove the "update `matrix_parent_inverse` after normalization" step unless explicitly trying to keep children fixed while parent changes.

#### 2. **Depsgraph Evaluation Issue**

**The Problem:**
- We're reading `obj.matrix_world` directly, which may not be fully evaluated
- Freshly created objects and post-op transforms can have non-evaluated matrices
- `context.view_layer.update()` is often not enough

**Correct Approach:**
```python
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()

M = obj.evaluated_get(depsgraph).matrix_world.copy()
```

**Action:** Replace all `matrix_world` reads during baking with evaluated depsgraph matrices.

#### 3. **Simpler Alternative: No Parenting Needed**

**Expert Recommendation:**
Instead of parenting/unparenting, bake a single "group normalization" matrix directly:

1. Capture each object's evaluated world matrix `W_i`
2. Compute group transform `G` (based on pivot mode + normalization)
3. Set `obj.matrix_world = G @ W_i` for each object (on temporary duplicates)
4. Export selected objects only
5. Restore

**Benefits:**
- No parent
- No parent inverse
- No unparenting surprises
- `G` is typically the inverse of the pivot transform you would have put on fake parent

#### 4. **USD Export Settings**

**Issues:**
- Exporter can author transforms as TRS vs Quaternion vs full Matrix
- Non-uniform scale + rotation decomposing to TRS can yield different rotation results
- Double axis conversion possible if enabling exporter's `convert_orientation` while doing own conversion

**Action:**
- Set exporter transform mode to **Matrix** (`xform_op_mode='MAT'`) for debugging
- Ensure `convert_orientation=False` when doing own conversion

#### 5. **Collection Export Parameter**

**Finding:**
- `bpy.ops.wm.usd_export` has a `collection` argument (string) for exporting collections
- May simplify selection/state juggling
- May change how parents/transforms are handled

**Action:** Test exporting with `collection=collection.name` instead of `selected_objects_only=True`

#### 6. **USD Scope vs Xform**

**Correction:**
- USD `Scope` cannot carry transforms (organizational only, "guaranteed no-op transform")
- If you need a container with transform, use `UsdGeomXform` (or any `Xformable`)
- We're already using Xform (correct), but good to remember

### Most Likely Root Cause (Expert Assessment)

Given "v0.1.62 made no difference" symptom:

1. **Updating `matrix_parent_inverse` after normalization is canceling normalization effect**
2. **Reading non-evaluated `matrix_world` instead of evaluated depsgraph matrices**
3. **Exporter writing TRS instead of matrix** introducing rotation differences

### Immediate Action Items (Without Re-architecting)

1. **Replace `context.view_layer.update()` with depsgraph updates + evaluated matrices when baking**
2. **Remove the "update children `matrix_parent_inverse` after normalization" step** (unless explicitly keeping children fixed)
3. **Export with `xform_op_mode='MAT'` and `convert_orientation=False`** while debugging

### Debugging Strategy

**Log evaluated matrices at 4 checkpoints:**
- `W0`: original evaluated world
- `W1`: after parenting
- `W2`: after normalization
- `W3`: right before export (after bake/unparent)

**Compare to USD:**
- Export ASCII `.usda` and inspect
- Use pxr `UsdGeom.XformCache` to compute world transforms
- Diff against `W3` to identify where error occurs:
  - Blender side baking (bad `W3`), or
  - USD export settings / transform authoring, or
  - USD viewer interpretation (axis/units)

### Expert Verdict

**Core idea (temporary parent → normalize → bake → export → restore) is viable**, but:
- `matrix_parent_inverse` timing/intent is the trap
- Non-evaluated matrices are likely causing incorrect bakes
- Simpler approach (direct matrix multiplication) eliminates parenting complexity

### References
- Expert consultation prompt: `99_HANDOFF.md` Appendix
- USD Fundamentals: https://docs.omniverse.nvidia.com/dang/latest/guide/usd/usd-fundamentals.html
- Blender Parenting: https://surf-visualization.github.io/blender-course/api/parenting/
- Blender Stack Exchange: https://blender.stackexchange.com/questions/152781/
- Omniverse Connect Manual: https://docs.omniverse.nvidia.com/connect/latest/blender/manual.html

## 2026-02-02 v0.1.63 - Expert Corrections Applied

### Changes Based on Expert Second Opinion

**1. Removed `matrix_parent_inverse` Update After Normalization**
- **File**: `ops_export.py` → `_create_fake_parent_for_collection()`
- **Before**: After normalization, we updated `matrix_parent_inverse` for all children
- **After**: Removed this step entirely
- **Reason**: Updating `matrix_parent_inverse` after normalization CANCELS the normalization effect
  - When fake parent is normalized to identity, `inverted()` gives identity matrix
  - Setting children's `matrix_parent_inverse` to identity removes compensation offset
  - This was the root cause of the "no difference" bug in v0.1.62

**2. Switched to Evaluated Depsgraph Matrices**
- **File**: `ops_export.py` → `_bake_fake_parent_transform_to_children()`
- **Before**: Used `obj_ref.matrix_world.copy()` directly
- **After**: Use `evaluated_depsgraph_get()` and `evaluated_get()`:
  ```python
  depsgraph = context.evaluated_depsgraph_get()
  depsgraph.update()
  evaluated_obj = obj_ref.evaluated_get(depsgraph)
  world_matrix = evaluated_obj.matrix_world.copy()
  ```
- **Reason**: `context.view_layer.update()` is often not enough - freshly created objects and post-op transforms may have non-evaluated `matrix_world` values

### Code Changes Summary

**`ops_export.py`:**
1. `_create_fake_parent_for_collection()` (lines ~347-377):
   - Removed the block that updated `matrix_parent_inverse` after normalization
   - Added explanatory comment about why this was removed
   - Now only calls `context.view_layer.update()` after normalization

2. `_bake_fake_parent_transform_to_children()` (lines ~382-470):
   - Added depsgraph evaluation before the baking loop
   - Changed from `obj_ref.matrix_world.copy()` to `obj.evaluated_get(depsgraph).matrix_world.copy()`
   - Added `evaluated_depsgraph: True` to logging for verification
   - Updated docstring to explain the expert correction

### Version
- Updated to v0.1.63
- Release: `releases/blender_usd_multiexport_v0.1.63.zip`

### Next Steps (If This Doesn't Work)
1. **Try simpler approach**: Direct matrix multiplication without parenting (see expert recommendation)
2. **Try collection export parameter**: `collection=collection.name` instead of `selected_objects_only=True`
3. **Debug with export settings**: `xform_op_mode='MAT'`, `convert_orientation=False`
4. **Log matrices at 4 checkpoints**: W0 (original), W1 (after parenting), W2 (after normalization), W3 (before export)

## 2026-02-02 v0.1.64 - CRITICAL Parenting Bug Fix

### Root Cause Identified

**The REAL bug was in the parenting logic in `_create_fake_parent_for_collection()` (lines 325-326).**

The code was:
```python
obj_ref.parent = fake_parent
obj_ref.matrix_parent_inverse = fake_parent.matrix_world.inverted()  # BUG!
```

**Why this is wrong:**
- Setting `matrix_parent_inverse` to just the parent's inverse does NOT preserve the child's visual position
- This formula loses the child's original world transform
- The effective world transform becomes: `parent.world @ parent.world.inverted() @ matrix_local = matrix_local`
- This means the child's visual position changes based on its local matrix, not its original world position

### Correct Approach

**To preserve visual position when parenting:**
```python
orig_world_matrix = obj_ref.matrix_world.copy()
obj_ref.parent = fake_parent
obj_ref.matrix_world = orig_world_matrix  # Blender recomputes matrix_local to achieve this
```

Setting `matrix_world` after parenting causes Blender to recompute `matrix_local` such that the desired world position is achieved given the current parent relationship.

### Why Previous Versions Showed "Same Problem"

- v0.1.62: Fixed `matrix_parent_inverse` update after normalization, but the INITIAL parenting was already broken
- v0.1.63: Used evaluated depsgraph for baking, but baking from corrupted transforms = corrupted output
- The original transform data was lost at parenting time, not at baking or export time

### Code Changes

**`ops_export.py` - `_create_fake_parent_for_collection()` (lines ~308-330):**
```python
# v0.1.64 FIX: Ensure fake_parent's matrix_world is fully evaluated before parenting
context.view_layer.update()

# ... inside loop ...

# v0.1.64 FIX: CRITICAL - Preserve visual position when parenting
# The bug was: setting matrix_parent_inverse = fake_parent.matrix_world.inverted()
# doesn't preserve the child's visual position - it loses the original position!
orig_world_matrix = obj_ref.matrix_world.copy()
obj_ref.parent = fake_parent
obj_ref.matrix_world = orig_world_matrix
```

### Version
- Updated to v0.1.64
- Release: `releases/blender_usd_multiexport_v0.1.64.zip`

### Verification

This fix should result in:
1. Objects maintaining their visual positions after parenting to fake parent
2. Normalization correctly shifting objects relative to the (normalized) fake parent origin
3. USD export containing correct world-space geometry after baking

## 2026-02-02 v0.1.65 - Fake Parent Machinery DISABLED

### Rationale

After multiple attempts (v0.1.58-0.1.64), the fake parent approach continues to produce scattered/rotated objects. 
User confirmed that **v0.1.39** (which has NO fake parent logic) works better - position is preserved correctly, 
only scale/rotation have issues.

The fake parent machinery introduced complexity that caused more problems than it solved:
- `matrix_parent_inverse` handling is complex and error-prone
- Multiple transform steps (parenting → normalization → baking → export → USD bake) multiply chances for bugs
- The simpler v0.1.39 approach works better for the core use case

### Changes

**`_create_fake_parent_for_collection()` - COMPLETELY DISABLED:**
```python
# v0.1.65: DISABLED - Fake parent machinery has persistent bugs
logger.log_step("fake_parent_disabled", {...})
return None, {}  # Always return no fake parent
```

### Behavior Change

Collection exports now behave like v0.1.39:
- No fake parent created
- No parenting operations
- No baking of parent transforms
- Objects exported directly with their world transforms
- USD bake handles Y-up/scale conversion

### Known Limitations

This disables pivot and normalization features for collection exports. These features need
to be re-implemented using a different approach (expert's "direct matrix multiplication"
suggestion instead of Blender parenting).

### Version
- Updated to v0.1.65
- Release: `releases/blender_usd_multiexport_v0.1.65.zip`

## 2026-02-02 v0.1.66 - USD Bake DISABLED for Collections

### Root Cause

v0.1.39 (which worked for position) did **NOT** have `usd_bake.py` at all. The usd_bake module was added 
later and is causing the scale/position issues for collection exports because:
1. It bakes transforms into geometry (including the object's local-to-world transform)
2. It then clears xformOps
3. This double-transforms the geometry when combined with Blender's already-applied export transforms

### Changes

**`ops_export.py` line ~1891:**
```python
# v0.1.66: SKIP bake step for COLLECTION exports
if start_point.start_point_type == 'OBJECT':
    self._apply_stage_metadata(filepath, start_point, logger, start_point_context)
else:
    logger.log_step("stage_bake_skipped", {...})
```

### Cumulative Changes (v0.1.65 + v0.1.66)

1. **Fake parent machinery DISABLED** (v0.1.65)
2. **USD bake step DISABLED for collections** (v0.1.66)

This should bring collection export behavior back to v0.1.39 style:
- Direct export without fake parent manipulation
- No post-export baking of transforms into geometry

### Version
- Updated to v0.1.66
- Release: `releases/blender_usd_multiexport_v0.1.66.zip`

## 2026-02-02 v0.1.67 - Collection Root Transforms

### Root Cause Analysis

v0.1.66 skipped the bake step entirely for collections, which meant:
- Geometry stayed in METERS (Blender's native unit)
- No scale factor applied (was 1.0, should be 100.0 for meters→cm)
- No Y-up rotation applied
- Result: 100x too small, wrong rotation

### Solution

Instead of baking transforms INTO geometry (which caused position issues), we now apply 
transforms TO the USD root prim via xformOps:

**New method: `_apply_collection_root_transforms()`**
1. Opens the exported USD stage
2. Finds the root prim (collection Scope)
3. Applies scale transform (e.g., 100x for meters→cm)
4. Applies rotation transform (-90° X for Y-up)
5. Sets stage metersPerUnit and upAxis metadata

This approach:
- **Preserves** original geometry positions (no baking into vertices)
- **Applies** correct scale via xformOp:scale on root prim
- **Applies** Y-up rotation via xformOp:rotateXYZ on root prim
- **Sets** correct stage metadata

### Different Approaches for OBJECT vs COLLECTION

| Type | Approach | Why |
|------|----------|-----|
| OBJECT | Bake into geometry | Works correctly, no position issues |
| COLLECTION | Root prim xformOps | Preserves relative positions of multiple objects |

### Code Changes

**`ops_export.py`:**
- Added `_apply_collection_root_transforms()` method (~90 lines)
- Updated export logic to call new method for COLLECTION exports

### Version
- Updated to v0.1.67
- Release: `releases/blender_usd_multiexport_v0.1.67.zip`

## 2026-02-02 v0.1.68 - Fix Collection Root Transform Bugs

### Bugs Fixed

1. **`AttributeError: '_sanitize_name'`** - Method didn't exist. Fixed by using `stage.GetDefaultPrim()` directly.

2. **`scale_factor: 1.0` instead of 100.0** - The `get_scale_factor()` method returns the Blender object scale,
   not the unit conversion factor. Fixed by calculating the conversion directly from source/target units.

### Code Changes

**`_apply_collection_root_transforms()`:**
```python
# OLD (broken):
scale_factor = start_point.get_scale_factor()  # Returns 1.0 (object scale)
root_prim_path = f"/{self._sanitize_name(...)}"  # _sanitize_name doesn't exist!

# NEW (fixed):
# Calculate unit conversion directly
unit_scale = {
    'MILLIMETERS': 1000.0,
    'CENTIMETERS': 100.0,
    'METERS': 1.0,
    'KILOMETERS': 0.001,
}
scale_factor = target_scale / source_scale  # e.g., 100.0 / 1.0 = 100.0

# Use default prim directly
root_prim = stage.GetDefaultPrim()
```

### Version
- Updated to v0.1.68
- Release: `releases/blender_usd_multiexport_v0.1.68.zip`

## 2026-02-02 v0.1.69 - Unified Bake for Objects AND Collections

### Problem

v0.1.67-68 used different approaches for OBJECT vs COLLECTION exports:
- **OBJECT**: Bake transforms INTO geometry (no xformOps on root prim)
- **COLLECTION**: Apply transforms TO root prim (xformOps added)

When both are referenced into the same parent scene, they don't align because:
- Object geometry is already in centimeters (baked)
- Collection geometry is in meters + root prim has scale(100,100,100)

### Solution

Use the **SAME bake approach for BOTH**:
```python
# v0.1.69: Use same bake for both OBJECT and COLLECTION
self._apply_stage_metadata(filepath, start_point, logger, start_point_context)
```

This ensures:
- Both have metersPerUnit=0.01, upAxis=Y
- Both have geometry baked to centimeters
- Both have NO xformOps on root prim
- Both align correctly when referenced together

### Note on Origin Metadata

The user reported that origin metadata works for decals but not for SHAKTI_002. This might be a
file locking issue - the error log showed "Access is denied" when trying to save the boat's USD file.

### Version
- Updated to v0.1.69
- Release: `releases/blender_usd_multiexport_v0.1.69.zip`

## 2026-02-02 v0.1.70 - FIX: Preserve Spatial Context for Collections

### Problem

v0.1.69 baked transforms into geometry but **CLEARED all xformOps** (`xforms_cleared: 6`).

For single object export, this is fine (object is at origin).  
For **collection export with multiple objects**, clearing xformOps **destroys the relative positions**!

The bug report showed:
```json
"bake_result": {
    "xforms_cleared": 6  // <-- THIS DESTROYED SPATIAL POSITIONS!
}
```

Result: All decals clustered at origin instead of spread across the boat surface.

### Root Cause

The old `usd_bake.py` logic:
1. Baked `global_bake_matrix * local_to_world` into points (including world position)
2. **Cleared ALL xformOps**

This worked for single objects but broke collections because:
- Each mesh had xformOps positioning it in world space
- Clearing those lost the spatial arrangement

### Solution (v0.1.70)

Rewrote `usd_bake.py` to **update xformOps instead of clearing them**:

1. **Geometry baking**: Only apply ROTATION (Z-up → Y-up) to LOCAL points
2. **xformOp updating**: Transform translate/rotate/orient values for coord conversion AND scale
3. **Preserve hierarchy**: Don't clear xformOps, just update their values

Key changes in `usd_bake.py`:
```python
# v0.1.70: Only rotation for geometry (LOCAL coords)
local_bake_matrix = rotation_matrix  # No scale, no world transform

# v0.1.70: Update xformOps instead of clearing
_update_xform_ops(xformable, scale_factor, y_is_up, Gf)
```

New `_update_xform_ops()` function handles:
- **Translate**: (x, y, z) Z-up → (x*s, z*s, -y*s) Y-up (with scale)
- **RotateXYZ**: Swap Y/Z rotation axes
- **Orient (quaternion)**: Convert quaternion between coordinate systems
- **Transform (matrix4d)**: Full matrix conversion

### Expected Result

- Scale: 100x (meters → centimeters) ✓
- Y-up: Correct orientation ✓  
- **Spatial positions: Preserved** ✓ (decals positioned on boat surface)

### Version
- Updated to v0.1.70
- Release: `releases/blender_usd_multiexport_v0.1.70.zip`

## 2026-02-02 v0.1.71 - FIX: Scale Geometry + Correct Rotation Direction

### Problem

v0.1.70 user feedback:
- **Boat**: 100x too small + upside down (needed manual scale 100 + rotate 180°)
- **Decals**: Correct POSITION, but geometry 100x too small + negatively flipped (mirrored)

### Root Cause

Two bugs in v0.1.70:

1. **Missing geometry scale**: I only applied rotation to local geometry, intending to put scale on xformOps.
   But the geometry itself needs to be scaled to centimeters!
   
2. **Wrong rotation direction**: Used -90° around X which caused mirroring/flipping.
   Correct is +90° around X for Z-up → Y-up conversion.

### Solution (v0.1.71)

Fixed `usd_bake.py`:

```python
# v0.1.71: Apply BOTH scale AND rotation to geometry
rotation = Gf.Rotation(Gf.Vec3d(1.0, 0.0, 0.0), 90.0)  # +90° not -90°!
rotation_matrix.SetRotate(rotation)

scale_matrix = Gf.Matrix4d(1.0)
scale_matrix.SetScale(Gf.Vec3d(scale_factor, scale_factor, scale_factor))

# Apply rotation first, then scale
local_bake_matrix = scale_matrix * rotation_matrix
```

Also fixed `_update_xform_ops()` to use +90° for consistency.

### Expected Result

- Geometry: Scaled to centimeters (100x) ✓
- Geometry: Rotated +90° around X (Z→Y up) ✓
- No flipping/mirroring ✓
- xformOps: Positions converted and scaled ✓

### Version
- Updated to v0.1.71
- Release: `releases/blender_usd_multiexport_v0.1.71.zip`

## 2026-02-02 v0.1.72 - FIX: Scale Axis Swap Without Negation

### Problem

v0.1.71 user feedback - almost correct, but scale values were wrong:

**Blender (Z-up):** Scale X=-0.301, Y=0.301, Z=0.301
**USD (Y-up):** Scale -0.30119, **-0.30119**, **-0.30119** (all negative!)

The Y and Z scale values were being negated when they shouldn't be.

### Root Cause

Missing `TypeScale` handling in `_update_xform_ops()`. Scale values need Y↔Z axis swap
but **NO negation** (scale is magnitude, not direction).

### Solution (v0.1.72)

Added explicit scale handling:

```python
elif op_type == op.TypeScale:
    scale = op.Get()
    if scale is not None and y_is_up:
        sx, sy, sz = scale[0], scale[1], scale[2]
        # Swap Y and Z scale values (NO negation!)
        # Z-up (sx, sy, sz) -> Y-up (sx, sz, sy)
        op.Set(Gf.Vec3f(sx, sz, sy))
```

### Expected Result

- Blender scale (-0.301, 0.301, 0.301) → USD scale (-0.301, 0.301, 0.301)
- Only X remains negative (as intended for mirroring)
- Y and Z swap but keep their positive values

### Version
- Updated to v0.1.72
- Release: `releases/blender_usd_multiexport_v0.1.72.zip`

## 2026-02-02 v0.1.73 - SIMPLIFIED: Only Convert Translate, Leave Scale/Rotate Unchanged

### Problem

v0.1.72 still showed wrong scale values. The conversions for scale and rotation were overcomplicating things.

### Key Insight

The **geometry is already rotated** by the bake step! The mesh vertices are already in Y-up orientation.

Therefore:
- **Scale ops**: Operate on already-rotated geometry → **NO CONVERSION NEEDED**
- **Rotate ops**: Operate on already-rotated geometry → **NO CONVERSION NEEDED**
- **Translate ops**: Position object in WORLD space which changed → **MUST CONVERT**

### Solution (v0.1.73)

Drastically simplified `_update_xform_ops()`:

```python
# ONLY modify translate
if op_type == op.TypeTranslate:
    # World space Z-up → Y-up: (x, y, z) → (x*s, z*s, -y*s)
    ...

# Leave ALL other ops UNCHANGED!
# Scale, rotation, orient operate on already-rotated geometry
```

### Expected Result

- Blender scale (-0.301, 0.301, 0.301) passes through UNCHANGED to USD
- Translate gets proper coordinate conversion
- No more corrupted scale/rotation values

### Version
- Updated to v0.1.73
- Release: `releases/blender_usd_multiexport_v0.1.73.zip`

## 2026-02-02 v0.1.74 - ULTRA-SIMPLIFIED: Scale Only, NO Rotation/Coord Conversion

### Problem

v0.1.73 still produced incorrect orientations. The rotation baking and coordinate
conversion attempts were causing more problems than they solved.

### Key Insight

Blender's USD exporter + USD upAxis metadata should handle coordinate conversion.
We should NOT be doing it in post-processing!

### Solution (v0.1.74)

**REMOVED all coordinate conversion from usd_bake.py:**

1. **Geometry baking**: ONLY scale (100x for m→cm), NO rotation
   ```python
   local_bake_matrix = Gf.Matrix4d(1.0)
   if scale_factor != 1.0:
       local_bake_matrix.SetScale(Gf.Vec3d(scale_factor, scale_factor, scale_factor))
   ```

2. **xformOps**: ONLY scale translate values, NO axis swapping
   ```python
   # Just scale - NO coordinate swapping!
   op.Set(Gf.Vec3d(x * scale_factor, y * scale_factor, z * scale_factor))
   ```

3. **Stage metadata**: Still set metersPerUnit and upAxis

### Expected Result

- Geometry scaled to centimeters ✓
- Translate positions scaled to centimeters ✓
- All rotations/scales pass through unchanged from Blender ✓
- USD upAxis=Y tells viewers how to interpret the coordinate system

### Version
- Updated to v0.1.74
- Release: `releases/blender_usd_multiexport_v0.1.74.zip`

## 2026-02-02 v0.1.75 - THE FIX: Add -90° Rotation to Default Prim

### Problem

All previous attempts (v0.1.69-74) tried to:
- Bake rotation into geometry
- Convert xformOps on child prims
- Swap coordinate axes in various ways

None of these worked correctly because the transforms weren't being applied at the right level!

### Root Cause Discovery

User manually fixed the issue by adding `-90° X rotation` to the **reference Xforms** in the root USD file.
This revealed that the exported USD files had **no xformOps on their default prims**.

The coordinate conversion needs to happen at the **default prim level**, not in the geometry or child xformOps.

### Solution (v0.1.75)

Add -90° X rotation xformOps to the **default prim** after export:

```python
default_prim = stage.GetDefaultPrim()
if default_prim and default_prim.IsValid() and y_is_up:
    xformable = UsdGeom.Xformable(default_prim)
    if xformable:
        xformable.ClearXformOpOrder()
        
        translate_op = xformable.AddTranslateOp()
        translate_op.Set(Gf.Vec3d(0, 0, 0))
        
        rotate_op = xformable.AddRotateXYZOp()
        rotate_op.Set(Gf.Vec3f(-90, 0, 0))  # Z-up → Y-up!
        
        scale_op = xformable.AddScaleOp()
        scale_op.Set(Gf.Vec3f(1, 1, 1))
```

### Why This Works

1. Blender exports geometry in Z-up orientation
2. The -90° X rotation on the default prim rotates the ENTIRE hierarchy to Y-up
3. All child transforms remain relative and work correctly
4. Geometry only needs unit scaling (m→cm), no rotation
5. Child translate values only need unit scaling, no coordinate swapping

### Version
- Updated to v0.1.75
- Release: `releases/blender_usd_multiexport_v0.1.75.zip`

## 2026-02-02 v0.1.76 - NORMALIZE: Bake Rotation INTO Children, Identity Default Prim

### Problem

v0.1.75 added -90° rotation to the default prim. This works when opening the file directly,
but when **referenced** into another USD file, the rotation on the default prim isn't applied
the same way - the geometry appears vertical again.

### Solution: Normalize/Flatten Transform

Instead of leaving the rotation on the default prim, we **bake it INTO all children**:

1. **Mesh geometry**: Points transformed by `bake_matrix` (rotation + scale)
2. **Mesh normals**: Transformed by rotation matrix (inverse transpose)
3. **Child translate xformOps**: Transformed by `bake_matrix`
4. **Default prim**: Set to **IDENTITY** transform (0,0,0 rotation)

```python
# Build combined bake matrix
rotation = Gf.Rotation(Gf.Vec3d(1, 0, 0), -90.0)  # Z-up → Y-up
rotation_matrix.SetRotate(rotation)
scale_matrix.SetScale(Gf.Vec3d(scale_factor, scale_factor, scale_factor))
bake_matrix = scale_matrix * rotation_matrix

# Apply to all mesh points
p_transformed = bake_matrix.Transform(point)

# Apply to all translate xformOps
t_transformed = bake_matrix.Transform(translate)

# Default prim gets IDENTITY (rotation already baked into children)
rotate_op.Set(Gf.Vec3f(0, 0, 0))
```

### Why This Works

When the file is referenced, the geometry is ALREADY in Y-up orientation with correct scale.
No additional rotation needed on the reference. The reference can have identity transform
and everything aligns correctly.

### Version
- Updated to v0.1.76
- Release: `releases/blender_usd_multiexport_v0.1.76.zip`

## 2026-02-02 v0.1.77 - CORRECT FLATTEN: Per USD NIM Guidance

### Problem

v0.1.76 rotated each mesh's LOCAL points around its own pivot, causing objects to
scatter incorrectly. It also corrupted normals by transforming them improperly.

### USD NIM Guidance

Consulted NVIDIA USD NIM which explained the CORRECT approach:
1. **DON'T rotate mesh points** - geometry stays in local space
2. **Rotate child TRANSLATES** around parent's pivot (0,0,0)
3. **COMBINE parent rotation WITH child rotation** xformOps
4. **Reset parent** to identity

### Solution (v0.1.77)

```python
# 1. Scale mesh points ONLY (no rotation!)
scaled_points.append(Gf.Vec3f(
    point[0] * scale_factor,
    point[1] * scale_factor,
    point[2] * scale_factor
))

# 2. Rotate child's WORLD POSITION around origin
scaled_translate = Gf.Vec3d(child_translate * scale_factor)
rotated_translate = rotation_matrix.Transform(scaled_translate)

# 3. Combine rotations (parent + child)
combined_rotation = Gf.Vec3f(
    -90.0 + child_rotation[0],  # Add parent's X rotation
    child_rotation[1],
    child_rotation[2]
)

# 4. Reset default prim to identity
r_op.Set(Gf.Vec3f(0, 0, 0))
```

### Why This Is Correct

- Geometry points are in LOCAL space - rotating them would rotate around local pivot
- Child POSITIONS are in WORLD space - rotating them rotates around world origin (0,0,0)
- Child ROTATIONS need to include the parent's rotation to maintain correct orientation
- Parent becomes identity since its transform is now "absorbed" by children

### Version
- Updated to v0.1.77
- Release: `releases/blender_usd_multiexport_v0.1.77.zip`

## 2026-02-02 v0.1.77 Issues Analysis - Collection Export Still Failing

### Problem

Object export (boat) works correctly, but collection export (decals) still fails.
When referenced into another USD file, the decals have incorrect orientation and position.

### Findings from Code Analysis

**Bug Report (v0.1.77):**
- Bug report: `c:\Users\jan\AppData\Local\Temp\blender_a15376\usdme_bug_report_20260202_234139.json`
- `fake_parent_disabled` log shows fake parent machinery was disabled in v0.1.65
- `bake_result` shows: `meshes_processed=6`, `translates_rotated=6`, `rotations_combined=6`, `transform_flattened=True`
- Final USDA shows default prim with identity transform `(0, 0, 0)` rotation

**Issue 1: `_flatten_nested_children` Never Called**

The function `_flatten_nested_children()` is defined (lines 204-233) but **never invoked** in `bake_usd_geometry()`. This means:
- Only direct children of the default prim are processed
- Grandchildren (meshes inside Xform containers) are not transformed
- Nested hierarchy transforms are incorrect

**Issue 2: Incorrect Euler Rotation Composition**

Current code uses simple Euler angle addition:
```python
combined_rotation = Gf.Vec3f(
    -90.0 + child_rotation[0],  # Just adding numbers!
    child_rotation[1],
    child_rotation[2]
)
```

This is mathematically **WRONG** for 3D rotations! Euler angles don't compose by addition.

Example failure case:
- Child has rotation `(26°, -1.5°, 102°)` (complex orientation)
- Simple addition gives `(-64°, -1.5°, 102°)`
- Correct composition requires matrix multiplication or quaternion composition

**Issue 3: Objects vs Collections Difference**

Why objects work but collections fail:
- **Objects**: Single mesh, simple hierarchy, rotation composition happens to work for identity/simple cases
- **Collections**: Multiple objects with complex existing rotations, Euler addition corrupts these

### Correct Algorithm (for v0.1.78)

Per USD NIM guidance, the proper way to flatten a parent rotation onto children:

1. **Build parent rotation matrix** (not Euler angles):
   ```python
   parent_rotation = Gf.Rotation(Gf.Vec3d(1, 0, 0), -90.0)
   parent_rot_matrix = Gf.Matrix4d(1.0)
   parent_rot_matrix.SetRotate(parent_rotation)
   ```

2. **For each child, compose rotations via matrices**:
   ```python
   # Get child's existing rotation as matrix
   child_euler = child_rotation  # (rx, ry, rz)
   child_rot = Gf.Rotation(Gf.Vec3d(0, 0, 1), child_euler[2]) * \
               Gf.Rotation(Gf.Vec3d(0, 1, 0), child_euler[1]) * \
               Gf.Rotation(Gf.Vec3d(1, 0, 0), child_euler[0])
   
   # Compose: parent @ child
   combined_rot = parent_rotation * child_rot
   
   # Convert back to Euler if needed for xformOps
   combined_euler = combined_rot.GetQuat().GetEulerAngles()
   ```

3. **Transform child positions around world origin (0,0,0)**:
   ```python
   rotated_translate = parent_rot_matrix.Transform(scaled_translate)
   ```

4. **Reset parent to identity**

### Key Insight

The v0.1.77 approach of adding `-90` to child X rotation only works for children with identity or simple rotations. For children with complex 3D orientations (like the decal logos with `(26°, -1.5°, 102°)`), this produces completely wrong results.

### Next Steps (v0.1.78)

1. Fix rotation composition to use proper matrix/quaternion math
2. Call `_flatten_nested_children()` for nested hierarchies
3. Consider using `UsdGeom.XformCommonAPI` for cleaner transform handling
4. Test with objects that have complex initial rotations

## 2026-02-02 v0.1.78 - PROPER Rotation Composition Using Matrices

### Problem

v0.1.77 used simple Euler angle addition which is mathematically incorrect:
```python
combined_rotation = Gf.Vec3f(
    -90.0 + child_rotation[0],  # WRONG!
    child_rotation[1],
    child_rotation[2]
)
```

### Solution (v0.1.78)

Implemented proper rotation composition using matrices/quaternions:

**1. New helper function `_compose_rotations_xyz()`:**
```python
def _compose_rotations_xyz(parent_rotation, child_euler, Gf):
    # Convert child Euler XYZ to rotation
    rx, ry, rz = child_euler[0], child_euler[1], child_euler[2]
    
    child_rot_x = Gf.Rotation(Gf.Vec3d(1, 0, 0), rx)
    child_rot_y = Gf.Rotation(Gf.Vec3d(0, 1, 0), ry)
    child_rot_z = Gf.Rotation(Gf.Vec3d(0, 0, 1), rz)
    
    # Compose in XYZ order: R = Rz * Ry * Rx
    child_rotation = child_rot_z * child_rot_y * child_rot_x
    
    # Compose parent with child
    combined_rotation = parent_rotation * child_rotation
    
    # Convert back to Euler XYZ
    combined_euler = _rotation_to_euler_xyz(combined_rotation, Gf)
    return Gf.Vec3f(combined_euler[0], combined_euler[1], combined_euler[2])
```

**2. New helper function `_rotation_to_euler_xyz()`:**
- Converts rotation matrix back to Euler XYZ angles
- Handles gimbal lock cases
- Uses standard matrix decomposition

**3. Fixed `_flatten_nested_children()` integration:**
- Now actually called from `bake_usd_geometry()`
- Recursively processes grandchildren and deeper nested prims
- Result tracking: `nested_children_processed` counter added

**4. Refactored `_flatten_child_transform()`:**
- Separated direct child processing into its own function
- Uses proper rotation composition
- Preserves child scale values

### Why Matrix Composition Works

Euler angles are NOT linear - you cannot simply add them:
- Child rotation `(26°, -1.5°, 102°)` + parent `(-90°, 0, 0)`
- ≠ `(-64°, -1.5°, 102°)` (simple addition)
- = Proper matrix multiplication result (different values)

The correct approach:
1. Convert both rotations to matrices/quaternions
2. Multiply: `combined = parent @ child`
3. Convert result back to Euler if needed

### Version
- Updated to v0.1.78
- Release: `releases/blender_usd_multiexport_v0.1.78.zip`

## 2026-02-02 v0.1.79 - Fixed Euler Rotation Composition Order

### Problem

v0.1.78 used the wrong order for composing Euler XYZ rotations:
```python
# v0.1.78 BUG - extrinsic order (WRONG for USD!)
child_rotation = child_rot_z * child_rot_y * child_rot_x
```

This is the **extrinsic** convention (rotations around fixed world axes), but USD's
`xformOp:rotateXYZ` uses **intrinsic** Euler angles (each rotation is around the NEW
local axis after the previous rotation).

### Evidence from Testing

- **Objects with pure single-axis rotations worked** (e.g., `Shakti_ImageLogo` with `(0, 0, 180)`)
  - Because for single-axis, both orders give the same result
- **Objects with complex multi-axis rotations failed** (e.g., decals with `(26°, -1.5°, 102°)`)
  - The wrong order produced completely different combined rotations
  - Objects appeared rotated around their own origin instead of the collection's origin

### Solution (v0.1.79)

Fixed the rotation composition order in `_compose_rotations_xyz()`:
```python
# v0.1.79 FIX - intrinsic order (CORRECT for USD!)
# For intrinsic XYZ: first X, then Y around NEW axis, then Z around NEW axis
# Matrix form: R = Rx * Ry * Rz (multiply in order of application)
child_rotation = child_rot_x * child_rot_y * child_rot_z
```

### Key Insight

For **intrinsic Euler angles** (USD, Blender):
- Rotations are applied X → Y → Z around successively rotated local axes
- Matrix multiplication: `R = Rx * Ry * Rz`

For **extrinsic Euler angles**:
- Rotations are applied X → Y → Z around fixed world axes
- Matrix multiplication: `R = Rz * Ry * Rx` (reversed order)

The confusion arose because many textbooks show `Rz * Ry * Rx` for "XYZ order" but
that's for extrinsic convention. USD/Blender use intrinsic convention.

### Version
- Updated to v0.1.79
- Release: `releases/blender_usd_multiexport_v0.1.79.zip`

## 2026-02-03 v0.1.80 - SIMPLIFIED: Back to v0.1.75 Approach with Normalization

### Problem

v0.1.76-v0.1.79 all tried to COMPOSE child rotations with the parent -90° X rotation.
This is fundamentally wrong! The child rotations should be LEFT UNCHANGED.

User insight:
> "Let's say I've got a cone pointing Y-up. I rotate it by 90° around X to point Z.
> Then I want to reset the pivot to (0,0,0) while the cone stays horizontal."

This is a NORMALIZATION operation, not rotation composition!

### Solution (v0.1.80)

Return to v0.1.75 philosophy but add the missing normalization step:

1. **Scale mesh points** for unit conversion (meters → centimeters)
2. **Rotate child TRANSLATES** by -90° X around world origin (0,0,0)
3. **DO NOT touch child rotations** - leave them exactly as-is
4. **Set default prim to identity** (0,0,0) rotation

```python
# Scale translate, then rotate around origin
scaled_translate = Gf.Vec3d(t[0] * scale_factor, t[1] * scale_factor, t[2] * scale_factor)
rotated_translate = rotation_matrix.Transform(scaled_translate)

# Rebuild xformOps with new translate but UNCHANGED rotation
child_xformable.ClearXformOpOrder()
new_translate_op.Set(rotated_translate)
new_rotate_op.Set(child_rotation)  # UNCHANGED - this is the key!
new_scale_op.Set(child_scale)      # UNCHANGED
```

### Why This Works

The child objects' rotations are in their LOCAL coordinate system. When we:
1. Rotate their POSITIONS around the world origin (0,0,0)
2. Set the parent (default prim) to identity

The children end up in the correct Y-up world positions, and their local rotations
are still correct relative to their new positions. No rotation composition needed!

### What Previous Versions Got Wrong

- v0.1.76: Tried to bake rotation into mesh points (wrong - corrupted normals)
- v0.1.77: Tried simple Euler addition (wrong - math doesn't work that way)
- v0.1.78: Tried matrix composition with wrong order (Rz*Ry*Rx)
- v0.1.79: Fixed order to Rx*Ry*Rz but still wrong approach

The fundamental error was trying to MODIFY child rotations at all.

### Version
- Updated to v0.1.80
- Release: `releases/blender_usd_multiexport_v0.1.80.zip`

## 2026-02-03 v0.1.81

- Created v0.1.81 following v0.1.80.
- Difference from v0.1.80 was not documented at the time.

### Pivot-reset script (same timeframe – feeds into bigger picture)

During this period we worked on the **standalone pivot-reset script** (`SANDBOX SCRIPTS/normalize_pivot_reset.py`), run inside **Omniverse Kit** (Script Editor). It implements the same goal as the addon bake—default prim at identity, children visually unchanged—via a “wrapper trick” on already-exported USDA.

- **Purpose:** Post-process USDA so the default prim has identity transform while baking the previous root transform into each child’s local transform (no manual Euler composition).
- **Where it fits:** The script is a testbed for the same normalization we want in the addon (default prim identity after collection export). Learnings from the script (especially Kit-safe, layer-only reads/writes and prim removal) are captured in the **BEP notes at the top of this file** (section “2026-02-03 Pivot Reset Script (Omniverse Kit) – BEP Notes”).
- **When:** Script work and v0.1.81 both fall in the 2026-02-03 timeframe; the script informs how we might implement or validate the same behavior in the addon pipeline.

### Attempts (nodes) – what we tried, why it failed, what we do now

**Attempt 1 – Iterate `GetChildren()`, copy/remove in a loop**  
→ **Failed:** After the first remove, remaining prim refs from `GetChildren()` became invalid; next use raised “Accessed invalid expired Xform prim”.  
→ **Lesson:** Collect only names/paths before any edits; never hold `UsdPrim` refs across stage/layer edits.

**Attempt 2 – Use `XformCache.GetLocalToWorldTransform(prim)` on the edited stage**  
→ **Failed:** In Kit, after edits and `Reload()`, the cache hit “Accessed invalid null prim”.  
→ **Lesson:** Don’t use the edited stage for transform queries after heavy edits.

**Attempt 3 – Export layer to temp file, open as read-only stage, run XformCache there**  
→ **Failed:** Same “invalid null prim” on the read-only stage. Kit’s USD stack threw for that API in this context.  
→ **Lesson:** In this environment, avoid XformCache / `ComputeLocalToWorldTransform` for this workflow.

**Attempt 4 – Use `UsdGeom.Xformable(prim).GetLocalTransformation(time)` on the edited stage**  
→ **Failed:** Still “invalid null prim”. Any stage-based prim + UsdGeom after Reload could trigger it.  
→ **Lesson:** For reading transforms after hierarchy rewrite, don’t use the stage at all.

**Attempt 5 – Use `Usd.NamespaceEditor(stage).DeletePrimAtPath(path)` for all removals**  
→ **Failed:** After layer edits (CopySpec, setting xform on layer), the stage considered the prim “not a valid prim”; NamespaceEditor refused: “The prim to edit is not a valid prim”.  
→ **Lesson:** For removing prims after mixed stage/layer edits in Kit, remove via the **layer** only (`RemoveNameChild`), not NamespaceEditor.

**What we do now – Simplified hack (wrapper Xform, copy, rotate, copy back, all layer-only in Kit):**

1. Create a wrapper **Xform** under the default prim (`__pivot_reset_wrapper__`).
2. **Copy** all children of the default prim into the wrapper (`Sdf.CopySpec`); **remove** originals from the layer (`parent_spec.RemoveNameChild`), not via stage.
3. Set **default prim to identity** (0°, 0°, 0°).
4. Set **wrapper to -90° X** so children still see the same net -90°.
5. For each child under the wrapper: read **local** transform from the **layer** only (`_local_transform_from_layer`); compute **world = wrapper_matrix × local**; **copy** child back under default prim (`Sdf.CopySpec`); **remove** from wrapper via layer; **set** new child’s transform on the **layer** only (`_set_xform_to_matrix_on_layer`) to that world matrix.
6. **Delete the wrapper** via the layer (`_remove_prim_via_layer`).

No stage/UsdGeom for step 5 (no XformCache, no GetLocalToWorldTransform, no GetLocalTransformation). No NamespaceEditor for any remove. Child list for step 5 is the **saved** list from step 2 (`moved_child_names`), not re-queried from the stage. This runs in Omniverse Kit without “invalid null prim” or “prim to edit is not valid”.
