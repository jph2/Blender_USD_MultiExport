---
arys_schema_version: '1.2'
id: bd4913c5-c920-4399-9e04-b51b0c38b056
title: 'Handoff Memo: REQ-EXP-025 Duplicate ID Fix'
type: PRACTICAL
status: active
trust_level: 2
visibility: internal
created: '2026-02-17T09:42:16Z'
last_modified: '2026-02-17T09:42:16Z'
---

# Handoff Memo: REQ-EXP-025 Duplicate ID Fix

**Version**: 1.0.0 | **Date**: 06.02.2026 | **Time**: 14:30 | **GlobalID**: 20260206_1430_BlenderUSDMultiExport_REQIDFIX

**Tag block:**
#workflow_automation #export #usd_core #extension_development #blender #openusd #conversion #references #analysis #layers #composition #framework_integration #ai_coding_agents #deterministic_workflows

---

## Summary

Fixed a duplicate requirement ID issue in `02_Detailed_Requirements.md` where `REQ-EXP-025` was assigned to two different requirements.

## Issue Found

**REQ-EXP-025** was defined twice with different meanings:

| Location | Definition | Date Added | Status |
|----------|------------|------------|--------|
| Line 1486 | Correct Z-up → Y-up Bake Rotation | 02.02.2026 | Implemented |
| Line 1272 | Unit Conversion Bug - Target Unit Selection Ineffective | 05.02.2026 | BUG - Open |

## Resolution Applied

Renumbered the bug report (added later) from `REQ-EXP-025` to `REQ-EXP-030`:

- **Line 1272**: `REQ-EXP-025` → `REQ-EXP-030` (section header)
- **Line 2042**: Updated changelog reference from `REQ-EXP-025` → `REQ-EXP-030`

## Current REQ-EXP Numbering

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-EXP-020 | Y-Up Axis Conversion | - |
| REQ-EXP-021 | Object Selection for Export | - |
| REQ-EXP-022 | Collection Normalization Controls | - |
| REQ-EXP-023 | Materials Scope Renamed to "Looks" | - |
| REQ-EXP-024 | **NOT USED** (gap in numbering) | - |
| REQ-EXP-025 | Correct Z-up → Y-up Bake Rotation | Implemented |
| REQ-EXP-026 | Collection Pivot Source | - |
| REQ-EXP-027 | Object Pivot Normalization | - |
| REQ-EXP-028 | Animation Export - Baked Transform Animation | - |
| REQ-EXP-029 | Separate Animation Layer Export | - |
| REQ-EXP-030 | Unit Conversion Bug (BUG) | Open |

## Files Modified

- `02_Detailed_Requirements.md` - 2 replacements (section header + changelog)
- `04_Implementation_Plan.md` - 1 replacement (status line)
- `99B_Handoff_20260206_Animation_Export_Feature.md` - 1 replacement (known issues list)

## Follow-up Notes

- REQ-EXP-024 remains unused (numbering gap from earlier edits)
- Next new requirement should use REQ-EXP-031

---

**End of Memo**
