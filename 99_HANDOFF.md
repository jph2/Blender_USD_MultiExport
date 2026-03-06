## HANDOFF — Blender USD MultiExport

**Version**: 0.1.3  
**Date**: 03.02.2026  
**Time**: 23:27  
**Goal:** Hand off current state after **Z to Y for Omniverse** UI rename and default.
**Tag block:**
#blender #framework_integration #conversion #stage #omniverse #openusd #export #cleanup #usd_core #hybrid #references #analysis #workflow_automation #quality_assurance #validation #workflow_optimization #deterministic_workflows #isaac_sim

---

### Domain / Context

- **Domain:** Blender + OpenUSD + Omniverse
- **Type:** Addon dev (Blender USD Multi Export)
- **Environment:** Windows, Blender 5.0, pxr USD Python API (`usd_bake.py`)

---

### Current State Summary (v0.1.88)

- **Normalize translate:** Fixed; documented in implementation plan and discovery.
- **Normalize Scale / Normalize Rotation:** Grayed out in UI, forced `False` in export (upcoming feature). Root cause and fix path in `04_Implementation_Plan.md` and `00_Discovery.md`.
- **USDME_Logger:** Temp-file cleanup on save failure no longer crashes (`log_info`/`log_warning` → `info`/`warning`, `context=` → `extra=` in `usd_bake.py` and `ops_export.py`).
- **Z to Y for Omniverse (v0.1.89):** Option renamed to "Z to Y for Omniverse" (description: "Z to Y is up for Omniverse (conversion)"), default **True**. Conversion is applied in post-export bake only (Option A): -90° X on default prim, upAxis=Y, per exported scene. Manual check in Omniverse still recommended.

Full version-by-version history: **`80_WIP_notes.md`** (chronological: oldest first, newest last).

---

### Next step: Verify in Omniverse

Axis conversion (Z-up → Y-up) is implemented in the **post-export bake** (Option A): -90° X on default prim, `upAxis` = Y. The UI option is **"Z to Y for Omniverse"**, default ON. **Please test** in Omniverse (e.g. SHAKTI_Decals or hull) and confirm orientation is correct. Optional automated checks: `05_Testing_Plan.md` section "Automated testing (Z-up / Y-up)". This corresponds to Blender’s **Convert Orientation** export behavior.

**Authority:** **`00_Discovery.md`** — section **“Session: NVIDIA Omniverse — Convert Orientation and Axis Conversion (Reference)”** (approx. lines 673–767).

Summary from Discovery:

1. **Convert Orientation is not just metadata.** USD’s `upAxis` alone does not rotate authored transforms. You must apply a real axis-conversion transform (e.g. Blender’s Z-up → USD Y-up).
2. **Blender’s mechanism:** `bpy_extras.io_utils.axis_conversion(from_forward, from_up, to_forward, to_up)`; Blender native is Forward=+Y, Up=+Z. For Z-up→Y-up the conversion matrix is effectively **+90° about X** (e.g. `x′=x, y′=z, z′=−y`). Exporters typically **pre-multiply** object transforms with this matrix.
3. **Single place for conversion:** If the addon bakes transforms and also does axis conversion, do it in **one** place only (either in Blender export options or in our bake logic), not both, to avoid double-rotation.
4. **Omniverse-friendly setting (common):** Up=Y, Forward=-Z, Convert Orientation=ON. See Discovery for Isaac Sim / SimReady notes.

**Reference:** `00_Discovery.md` lines 673–767 (Convert Orientation and Axis Conversion). Use that section for the exact matrix, Blender API references, and “Option A vs Option B” (disable Blender convert_orientation and do conversion in our bake, or keep Blender’s and don’t add a second conversion).

---

### Key Files

| Purpose | Path |
|--------|------|
| WIP / version history | `80_WIP_notes.md` |
| Convert Orientation reference | `00_Discovery.md` (lines 673–767) |
| Implementation plan | `04_Implementation_Plan.md` |
| Export operator | `blender_usd_multiexport_addon/ops_export.py` |
| USD post-export bake | `blender_usd_multiexport_addon/usd_bake.py` |
| Props / UI | `blender_usd_multiexport_addon/props.py`, `ui.py` |
| Latest release zip | `releases/blender_usd_multiexport_v0.1.88.zip` (bump to 0.1.89 when releasing) |

---

### Next agent (if needed)

1. If Omniverse test shows wrong orientation: re-read `00_Discovery.md` lines 673–767 and `usd_bake.py` (default prim -90° X, upAxis); consider whether to bake rotation into geometry vs. root only.
2. To add automated tests: use `05_Testing_Plan.md` "Automated testing (Z-up / Y-up)" as a checklist (open USDA, assert upAxis and default prim rotation).

---

### Evidence / Notes

- **Bug reports / logs:** see `80_WIP_notes.md`.
- **File locked on save:** If `stage.Save()` fails (e.g. “Access is denied” with Omniverse open), user should close the app locking the file and re-export; temp-file cleanup now runs without crashing (v0.1.88 logger fix).

---

*End of handoff.*