# Quick Reference - Object/Collection Export Fix

**Version**: 1.1.0 | **Date**: 02.02.2026 | **Time**: 19:30 | **GlobalID**: 20260202_1930_Blender_USD_MultiExport_QUICKREF

---

## 🎯 The Problem (One Sentence)

Object export path broke after v0.1.48 because collection export logic leaked into it, causing broken normals when modifiers are enabled.

---

## ✅ The Solution (One Sentence)

Restore object export to exact v0.1.48 behavior (isolated), and implement collection export as completely separate path with fake parent + normalization.

---

## 🔑 Key Insight

**Two completely separate code paths:**
1. **Object Export** → Simple, matches v0.1.48 exactly
2. **Collection Export** → New feature, uses fake parent + optional normalization

**They must NEVER touch each other.**

---

## 📋 What to Do (3 Steps)

### Step 1: Fix Object Export
- Copy v0.1.48 object export logic
- Remove all collection/normalization/pivot logic from object path
- Fix normal handling in bake step (preserve authored normals)

### Step 2: Build Collection Export
- Create fake parent (Blender Empty)
- Implement pivot modes (world origin, custom, cursor, object, preserve)
- Add optional normalization (position/scale/rotation)
- **CRITICAL**: Do NOT update `matrix_parent_inverse` after normalization (cancels effect)
- **CRITICAL**: Use evaluated depsgraph matrices when baking transforms
- Export collection with `xform_op_mode='MAT'` and `convert_orientation=False`
- Export collection, then cleanup
- **Alternative**: Consider direct matrix multiplication approach (simpler, no parenting)

### Step 3: Verify Isolation
- Test object export → should match v0.1.48 exactly
- Test collection export → should work independently
- Test both together → should not interfere

---

## 🚨 Critical Rules

1. **Object export = v0.1.48 behavior** (no changes, no collection logic)
2. **Collection export = new separate path** (fake parent + normalization)
3. **Zero cross-contamination** (early returns, separate functions, clean state)
4. **Do NOT update `matrix_parent_inverse` after normalization** (cancels normalization effect)
5. **Use evaluated depsgraph matrices** when reading `matrix_world` for baking
6. **Export settings**: `xform_op_mode='MAT'`, `convert_orientation=False` for debugging

---

## 📁 Key Files

- **`ops_export.py`** - Separate `_export_object()` and `_export_collection()`
- **`usd_bake.py`** - Restore v0.1.48 normal handling for object path
- **`state_manager.py`** - Ensure clean state separation

---

## 🧪 Test Cases

1. **Object + Modifiers Enabled** → Normals should match v0.1.48 exactly
2. **Object + Modifiers Disabled** → Should still work
3. **Collection + Fake Parent** → Should export correctly
4. **Collection + Normalization** → Should normalize correctly
5. **Both Together** → Should not interfere

---

## 🔍 Expert Second Opinion Key Points

1. **`matrix_parent_inverse` update is BACKWARDS** - Removing this step fixes "no difference" bug
2. **Use evaluated depsgraph** - Pattern: `depsgraph = bpy.context.evaluated_depsgraph_get()`, `obj.evaluated_get(depsgraph).matrix_world`
3. **Export settings** - `xform_op_mode='MAT'` preserves exact transforms, `convert_orientation=False` avoids double conversion
4. **Simpler alternative** - Direct matrix multiplication: `obj.matrix_world = G @ W_i` (no parenting needed)

## 📚 Full Details

See `22_IMPLEMENTATION_PLAN_CLEAN_Phase_14D.md` for complete plan.
See `80_WIP_notes.md` for expert second opinion analysis.

---

**Start Here**: Compare v0.1.48 `ops_export.py` and `usd_bake.py` with current versions to identify differences. Then apply expert corrections to collection export implementation.
