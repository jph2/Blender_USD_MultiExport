# Blender USD Stable Export - Implementation Process

**Purpose**: This document explains the step-by-step implementation process for the Blender USD Stable Export addon.

**Last Updated**: 25.11.2025

---

## Implementation Workflow

The implementation follows a structured 4-step process:

```
Step 1: Requirements Questionnaire
    ↓
Step 2: Detailed Requirements
    ↓
Step 3: Module Design
    ↓
Step 4: Implementation Plan
```

---

## Step 1: Requirements Questionnaire ✅

**File**: `01_Requirements_Questionnaire.md`  
**Status**: ✅ Created - Ready for completion

**Purpose**: Gather detailed requirements through structured questions covering:
- User profiles and context
- Endpoint definition and management
- Export functionality
- User interface design
- Error handling
- Performance requirements
- Integration needs
- And more...

**Action Required**: Complete the questionnaire with stakeholder input.

---

## Step 2: Detailed Requirements ⏳

**File**: `02_Detailed_Requirements.md`  
**Status**: ⏳ Pending - Awaiting questionnaire completion

**Purpose**: Transform questionnaire responses into:
- Functional requirements
- Non-functional requirements
- User stories
- Acceptance criteria
- Priority matrix

**Action Required**: Populate after Step 1 is complete.

---

## Step 3: Module Design ⏳

**File**: `03_Module_Design.md`  
**Status**: ⏳ Pending - Awaiting requirements completion

**Purpose**: Design the addon architecture:
- Module structure
- Class design
- Data models
- API design
- Component interactions

**Action Required**: Populate after Step 2 is complete.

---

## Step 4: Implementation Plan ⏳

**File**: `04_Implementation_Plan.md`  
**Status**: ⏳ Pending - Awaiting module design completion

**Purpose**: Create detailed implementation roadmap:
- Implementation phases
- Task breakdown
- Timeline estimates
- Testing strategy
- Milestones

**Action Required**: Populate after Step 3 is complete.

---

## Current Status

| Step | Document | Status | Next Action |
|------|----------|--------|-------------|
| 1 | Requirements Questionnaire | ✅ Created | Complete questionnaire |
| 2 | Detailed Requirements | ⏳ Pending | Wait for Step 1 |
| 3 | Module Design | ⏳ Pending | Wait for Step 2 |
| 4 | Implementation Plan | ⏳ Pending | Wait for Step 3 |

---

## Quick Start

1. **Start Here**: Open `01_Requirements_Questionnaire.md`
2. **Complete**: Fill out all relevant sections
3. **Review**: Get stakeholder approval
4. **Proceed**: Move to Step 2

---

## Notes

- Each step builds on the previous one
- Don't skip steps - they ensure thorough planning
- Update status indicators as you progress
- Document decisions and rationale

---

**Last Updated**: 25.11.2025

---

## 🔴 Expert Technical Review & Critical Risks

> **Expert Analysis**: This section contains critical technical risks and recommendations from an expert in both Blender `bpy` and Omniverse. These must be addressed in the core design to avoid workflow-breaking issues.

### Overview

This is a solid "Phase 1" plan. It correctly identifies the biggest constraint: **Blender is not a USD stage editor**. By treating Blender as a "content factory" that spits out atomic USD components (Endpoints) for downstream assembly (in Omniverse/USDView), you avoid fighting Blender's internal architecture.

However, as an expert in both Blender `bpy` and Omniverse, there are three critical technical risks that will break this workflow if not addressed in the core design *now*.

---

### 1. The "Visibility" Trap (Critical Pitfall)

The plan correctly notes that `bpy.ops.wm.usd_export` only exports **visible** objects.

**The Trap:** If you have 5 Endpoints (Props A, B, C, D, E) and you click "Export All", the operator cannot just loop and export.

*   If Prop B is hidden in the viewport, it exports an empty file.
*   If you programmatically unhide Prop B for export, you might accidentally render it in the user's active viewport or mess up their scene state.
*   **Challenge:** You need a robust **State Manager**.
    *   **Naive approach:** Select A -> Export -> Select B -> Export. (Slow, prone to errors if crash happens mid-loop).
    *   **Expert approach:** The operator must wrap the export in a `try...finally` block that caches the *exact* visibility/selection state of the scene, isolates the target Endpoint (using `view_layer.objects.active` and `object.hide_set`), performs the export, and **guarantees** state restoration.
    *   *Note:* Blender's `usd_export` operator relies on the *evaluated* scene. You cannot easily "fake" visibility without actually changing the scene data, which triggers dependency graph re-evaluation. This will be your biggest performance bottleneck.

---

### 2. Coordinate Systems & Units (The "Floating Chair" Problem)

Blender is **Z-Up / Meters**. Omniverse (and most USD stages) defaults to **Y-Up / Centimeters**.

**The Trap:** You export a chair. In Omniverse, it's lying on its back and is 100x too small (or large).

*   **Native Exporter:** Has `global_scale` and axis conversion args, but they are global.
*   **Best Practice:** Enforce a project-wide standard.
    *   **Recommendation:** Force `Z-Up` export if staying in Omniverse (Omniverse handles Z-up stages fine), OR strictly apply the transform on export.
    *   **Crucial:** If you use `root_prim_path` (e.g., `/World/Chair`), ensure the transform on that root prim matches the target stage's expectation.

---

### 3. Material Transport (USD Preview vs. MDL)

The plan relies on `export_materials=True` (USD Preview Surface).

**The Trap:** In Omniverse, USD Preview Surface looks "okay" but flat. It lacks the rich PBR fidelity of MDL.

*   **Challenge:** Native Blender export does *not* generate MDLs. It generates `UsdPreviewSurface`.
*   **Workaround:** In Phase 1, accept this. In Phase 2, you will likely need a post-export hook (using `USDHook` or a separate pass) that inserts a reference to an existing `.mdl` library or adds `kind` metadata so Omniverse allows material overrides easily.

---

## Revised Technical Recommendations

### 1. Architecture: The "Isolation Context"

Don't just write a loop. Create a Context Manager class in Python to handle the state.

```python
class ScopedIsolation:
    """
    Temporarily isolates a specific collection or object for export,
    ensuring the user's viewport state is restored afterwards.
    """
    def __init__(self, context, target_object_or_collection):
        self.context = context
        self.target = target_object_or_collection
        self._initial_selection = []
        self._initial_visibility = {}

    def __enter__(self):
        # 1. Cache current selection/visibility
        # 2. Deselect all, Hide all (efficiently)
        # 3. Unhide/Select ONLY self.target
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Restore everything explicitly
        pass
```

### 2. File Path Safety

The plan mentions `E:\...`.

*   **Best Practice:** Store paths **Relative to Blend File** (`//export/prop_a.usd`).
*   **Why:** If you move the project to another drive or share it via version control, absolute paths break immediately.
*   **Code Check:** Always resolve `bpy.path.abspath(endpoint.filepath)` before passing to the exporter.

### 3. Root Prim Naming

Native Blender export often dumps objects at the root if `root_prim_path` isn't set carefully.

*   **Recommendation:** Enforce a naming convention for the `root_prim_path`.
    *   If Endpoint name is "MyChair", default `root_prim_path` should be `/MyChair`.
    *   Without this, merging multiple USDs into one stage later results in name collisions (everything named `/Mesh`).

### 4. Validation Before Execution

Add a pre-flight check operator:

1.  Are any target collections empty?
2.  Do any file paths imply a directory that doesn't exist? (Auto-create directories).
3.  Are any objects in the endpoint disabled in the render? (Blender export uses Render visibility by default in some modes, Viewport in others).

---

## Summary of Changes to Plan

1.  **Add "State Manager" to Module Design:** Essential for batch exporting multiple endpoints safely.
2.  **Add "Relative Path Logic":** Mandatory for usable tools.
3.  **Explicitly define `root_prim_path` logic:** Don't leave it empty.
4.  **Accept the Visibility Limitation:** Document clearly that "If you hide it in the Viewport, the exporter ignores it, even if the Endpoint is active."

---

**Expert Conclusion:** This approach is sound. If you handle the visibility state management correctly, this will be a very stable tool.

