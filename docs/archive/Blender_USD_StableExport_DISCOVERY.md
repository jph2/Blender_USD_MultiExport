---
arys_schema_version: '1.2'
id: d1fc3960-b2e3-451b-a9ff-57d49b229b6b
title: __init__.py
type: STRATEGIC
status: active
trust_level: 2
visibility: internal
created: '2025-11-25T19:31:49Z'
last_modified: '2025-11-25T19:31:49Z'
---

**⚠️ IMPORTANT: This document targets Blender 5.0+ only (officially released November 18, 2025). Blender 4.x versions are not supported.**

---

To build an export Python script for Blender focused on exporting parts of the scene (e.g., certain parts of the scene tree) as USD files, you first need to be familiar with Blender's Python API (bpy) and the process of creating Blender add-ons (plugins). The typical steps include writing a Python class inheriting from Blender's bpy.types (usually bpy.types.Operator for actions), registering and unregistering your plugin, and exporting functionality using bpy's API for scene and object access.

Key points to get started:

- Set up Blender with the Scripting workspace to write and test Python scripts.
- Develop the plugin by creating classes such as an operator class that performs export functions.
- Register your plugin so Blender recognizes it as an add-on, allowing installation through Blender's preferences.
- Use bpy to navigate and manipulate the scene tree. Although Blender does not use "stage tree" terminology like USD, you can access the scene hierarchy and define specific objects or collections as export endpoints.
- Export endpoints can be identified by selecting specific objects or collections to export as USD files using Blender's USD export capabilities.
- For missing features like composition arcs in Blender USD, you can define multiple export points and save separate USD files accordingly.

To build a research document and project plan:

1. Familiarize yourself with Blender's Python API (bpy) and its USD exporter.
2. Understand plugin structure and lifecycle: class definition, registration, UI integration, execution.
3. Define the scope: exporting selected scene graph nodes to USD files, defining export endpoints by object or collection selection, no composition arcs support.
4. Define out of scope: advanced USD composition, UI customization beyond basics, non-USD export.
5. Research Python packages or Blender modules to assist with USD exporting if needed.
6. Outline development steps: initial script setup, operator creation, selection mechanism for export endpoints, the export logic using bpy.ops.wm.usd_export or similar API, testing, packaging as add-on.

References marked:
- Blender Python plugin development involves writing classes that inherit from bpy.types, registration functions, and saving the script as a .py file to load it as an add-on in Blender's preferences.[1]
- The bpy API allows you to access and manipulate the scene and objects, which you need to define export endpoints (objects or collections).[1]
- Exporting to USD in Blender can be done using Blender's built-in USD exporter accessible via bpy.ops.wm.usd_export with specific parameters [general Blender docs knowledge].
- Plugin lifecycle requires loading, registering, and unregistering to manage the add-on properly.[1]

This should help start your export plugin project for Blender focusing on USD export from specific scene parts and create your initial research document and project scoping.

[1](https://hemaks.org/posts/developing-plugins-for-blender-with-python-a-step-by-step-guide/)
[2](https://www.youtube.com/watch?v=L5SpBdotarI)
[3](https://stackoverflow.com/questions/11161901/how-to-install-python-modules-in-blender)
[4](https://community.osarch.org/discussion/759/blender-create-your-first-blender-add-on)
[5](https://www.youtube.com/watch?v=k1gCIezKA8E)
[6](https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html)
[7](https://docs.blender.org/api/current/info_quickstart.html)
[8](https://www.reddit.com/r/blender/comments/x2lteh/all_you_need_to_know_to_start_coding_with_the/)
[9](https://blenderartists.org/t/blender-addon-development/1160488)
[10](https://vagon.io/blog/using-python-in-blender)






Here’s a first pass at what you asked for **already done** in this reply:

1. A **research document** you can drop into
   `E:\SynologyDrive\9999_LocalRepo\Blender_USD_StableExport`
2. A first **definition of steps / scope / out-of-scope** for the add-on.

You can copy-paste the markdown below into e.g.:

`E:\SynologyDrive\9999_LocalRepo\Blender_USD_StableExport\docs\01_Research_Blender_USD_StableExport.md`

(or whatever filename you prefer).

---

## 📄 Research Document: Blender USD Stable Export Add-on

**Project root:**
`E:\SynologyDrive\9999_LocalRepo\Blender_USD_StableExport`

**Working name:**
**Blender USD StableExport** – a Blender add-on that exports specific parts of the scene tree as USD files via “endpoints”.

---

### 1. Target Environment & Versions

**Blender**

* Use a **modern LTS** as the baseline:
  → **Blender 5.0+** (officially released November 18, 2025). ([Blender][1])
* Blender includes **built-in USD import/export** (File → Import/Export → Universal Scene Description). ([Blender Documentation][2])

**Python**

* Blender bundles its own Python (3.x, version depends on Blender build).
* Add-ons use **Blender’s embedded Python**, via the `bpy` module. ([Blender Documentation][3])

**USD**

* Blender’s USD exporter is accessible as the operator
  `bpy.ops.wm.usd_export(...)`, with many parameters for filtering objects, collections, animation, etc. ([UPBGE][4])
* Exporter design is documented in Blender’s USD dev docs; it uses an abstract hierarchy iterator to traverse the Blender scene and build a USD hierarchy. ([Blender Developer][5])
* USD extension points are available via `bpy.types.USDHook` for custom import/export behavior. ([Blender Documentation][6])

For now, this project will **leverage the built-in exporter** instead of reimplementing USD export logic.

---

### 2. Blender Add-on Architecture – Essentials

Official resources:

* **Add-on tutorial (official manual)** ([Blender Documentation][7])
* **Add-on guidelines & style guide (developer docs)** ([Blender Developer][8])
* **Python API overview** ([Blender Documentation][3])

#### 2.1 Basic Structure of an Add-on

A Blender add-on is essentially a Python package with:

* A top-level `__init__.py` that contains:

  * `bl_info` dict (name, author, version, Blender version compatibility, category, description)
  * `register()` / `unregister()` functions
  * Class registrations (Operators, Panels, PropertyGroups, etc.)

Example skeleton (simplified):

```python
# __init__.py
bl_info = {
    "name": "USD Stable Export",
    "author": "Your Name",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),  # Blender 5.0+ required (released November 18, 2025)
    "location": "Properties > Scene / 3D Viewport > N-Panel",
    "description": "Export selected parts of the scene as USD via endpoints.",
    "category": "Import-Export",
}

import bpy

classes = []

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
```

You typically split the code into modules (e.g. `ops_export.py`, `ui.py`, `props.py`) and import/register their classes in `__init__.py`.

#### 2.2 Key Blender Python Types

From the official API: ([Blender Documentation][3])

* `bpy.types.Operator`

  * Implements actions (e.g. “Export endpoints as USD”).
  * Has `execute`, `invoke`, `poll` methods.
* `bpy.types.Panel`

  * UI panel (e.g. in N-Panel or Scene properties).
* `bpy.types.PropertyGroup`

  * Structured custom data (e.g. an “Endpoint” with name, collection, filepath).
* `bpy.props.*`

  * Property definitions (StringProperty, BoolProperty, PointerProperty, CollectionProperty, etc.)

Operators are invoked via:

* UI buttons, menus
* Or directly from Python: `bpy.ops.my_addon.export_endpoints()`

The operator system is described under `bpy.ops` and `bpy.types.Operator`. ([Blender Documentation][9])

---

### 3. Installing / Loading Add-ons in Blender

User-facing installation (for you / artists):

1. In Blender: **Edit → Preferences → Add-ons**. ([Blender Documentation][10])
2. Click **Install…**, select the `.zip` containing the add-on (Blender expects a zip with a folder containing `__init__.py`). ([Blender Documentation][11])
3. Search for the add-on by name, enable the checkbox.
4. Optionally click **Save Preferences**.

Developer workflow:

* While developing, you can:

  * Put the add-on folder into Blender’s scripts/addons directory and enable it.
  * Use **“Reload Scripts”** (and/or disable+enable the add-on) to reload code.
* For rapid iteration, it’s common to:

  * Use the Scripting workspace.
  * Run modules via `import importlib; importlib.reload(my_addon_module)`.

Gotchas:

* Changes in property definitions often require a restart or manual cleanup,
  because Blender stores property data in the .blend file.
* Renaming classes or properties can leave stale data; plan naming early.

---

### 4. Scene Graph Basics in Blender (for “Endpoints”)

What you called “stage tree” (USD) maps roughly to:

* **Scene** (`bpy.types.Scene`)
* **Collections** (`bpy.types.Collection`)
* **Objects** (`bpy.types.Object`)

Hierarchy is shown in the **Outliner**. Essential relationships:

* Scene → top-level collections (Scene.collection / Scene.collection.children)
* Collections contain **links** to objects
* Objects can be parented to other objects (object-mode hierarchy)

For your use case, “endpoint” candidates:

* **Collections** (good for logical groupings; easily mapped to a USD subtree)
* **Objects** (root objects; children included by parenting)
* Potentially **View Layers** or per-collection visibility flags for advanced control.

---

### 5. USD Export via Python

The built-in USD exporter operator signature (current API snapshot, abbreviated): ([UPBGE][4])

```python
bpy.ops.wm.usd_export(
    filepath='',
    selected_objects_only=False,
    collection='',
    export_animation=False,
    export_hair=False,
    export_uvmaps=True,
    export_mesh_colors=True,
    export_normals=True,
    export_materials=True,
    export_subdivision='BEST_MATCH',
    export_armatures=True,
    only_deform_bones=False,
    export_shapekeys=True,
    use_instancing=False,
    evaluation_mode='RENDER',
    root_prim_path='/root',
    export_custom_properties=True,
    custom_properties_namespace='userProperties',
    # ... many more options omitted ...
)
```

Important parameters for this project:

* `filepath` – path to `.usd` / `.usda` / `.usdc` / `.usdz`.
* `selected_objects_only` – export only current selection.
* `collection` – export only a specific collection (string ID).
* `evaluation_mode` – `'RENDER'` vs `'VIEWPORT'`.
* `root_prim_path` – root prim path in USD stage.
* `export_custom_properties` / `custom_properties_namespace` – we can propagate endpoint metadata into USD if needed.

Typical usage:

```python
import bpy

bpy.ops.wm.usd_export(
    filepath="C:/tmp/test.usda",
    selected_objects_only=True,
    export_animation=False,
    export_materials=True,
)
```

Note: some options and exact defaults may change subtly between Blender releases, so we should:

* **Develop against Blender 5.0+** (officially released November 18, 2025).
* Optionally, query defaults via `bpy.ops.wm.usd_export.get_rna_type().properties` in the Python console.

---

### 6. Extending USD Export (USDHook)

Blender provides `bpy.types.USDHook` as an extension mechanism for the USD importer/exporter. ([Blender Documentation][6])

* You can subclass `USDHook` and implement callback methods to:

  * Customize prim paths.
  * Inject custom attributes.
  * Modify export or import behavior.

For **v1 of this add-on**, we likely don’t need `USDHook`.
But it’s useful for future iterations (e.g. custom composition arcs / metadata).

---

### 7. Plugin Design Considerations for “Endpoints”

Goal: From a Blender scene, specify **one or more endpoints** that each produce a USD file.
Because Blender’s exporter doesn’t expose full OpenUSD composition graph editing, we treat each endpoint as an independent export, with some potential composition built later.

#### 7.1 What is an “Endpoint” in this context?

Conceptual design:

* An **Endpoint** is a configuration that says:

  * “Export *this subset of the scene* to *this filepath* using *these usd_export options*.”

Minimum fields per endpoint:

* Identifier / name (string).
* Target **collection or object** (PointerProperty to `Collection` or `Object`).
* Export filepath (string; plus optional pattern, e.g. with tokens).
* Export mode:

  * `BY_COLLECTION` – use usd_export’s `collection` argument.
  * `BY_SELECTION` – temporarily select objects under a root and use `selected_objects_only=True`.
* Flags like:

  * Include animation?
  * Include materials?
  * Use instancing?
  * Root prim path override?

Implementation-wise, this maps nicely to a `PropertyGroup` plus a `CollectionProperty` on `Scene`.

#### 7.2 How to implement endpoints technically

Possible approach:

* Define:

  ```python
  class USDStableExportEndpoint(bpy.types.PropertyGroup):
      name: StringProperty()
      collection: PointerProperty(type=bpy.types.Collection)
      root_object: PointerProperty(type=bpy.types.Object)
      filepath: StringProperty(subtype="FILE_PATH")
      export_animation: BoolProperty()
      # ... additional options ...
  ```

* Attach a `CollectionProperty` to Scene:

  ```python
  bpy.types.Scene.usd_stable_export_endpoints = CollectionProperty(
      type=USDStableExportEndpoint
  )
  bpy.types.Scene.usd_stable_export_index = IntProperty()
  ```

* Add a UI Panel (e.g. in **Scene Properties** or **N-Panel**) to manage the list:

  * Add / remove endpoints.
  * Choose collection or root object.
  * Set filepath and export flags.

* Implement an operator:

  * `USDStableExport_OT_export_all_endpoints`
  * Loops over endpoints and calls `bpy.ops.wm.usd_export(...)` for each one.

---

### 8. Pitfalls & Things to Watch Out For

1. **Context sensitivity of operators**

   * `bpy.ops.wm.usd_export` may require a valid window / context.
   * For headless / batch export, run Blender with `blender -b -P script.py` and ensure context is correct (or use context override).

2. **Scene vs collection visibility**

   * USD exporter respects visibility settings (view layer, collections).
   * When exporting endpoints by collection, ensure the relevant collections are visible in the current view layer.

3. **Performance considerations**

   * Multiple endpoints = multiple USD exports.
   * Avoid heavy operations in `draw()` methods of panels. Keep them light.

4. **File path handling**

   * Legal characters on Windows paths (you’re on `E:\...`).
   * Possibly support relative paths based on the `.blend` file or project root.

5. **Version differences**

   * If installed on different Blender versions, some usd_export arguments might not exist or may be renamed.
   * Strategy: develop and support Blender 5.0+; add version-guards for future versions (5.1+, 6.0+).

---

## 🧭 Initial Project Plan, Scope & Out-of-Scope

### 1. High-Level Steps

**Step 1 – Environment & Repo**

* Use **Blender 5.0+** as dev target (officially released November 18, 2025).
* Create repo layout under:

  ```text
  E:\SynologyDrive\9999_LocalRepo\Blender_USD_StableExport\
      addon\
          blender_usd_stableexport\
              __init__.py
              ops_export.py
              props.py
              ui.py
      docs\
          01_Research_Blender_USD_StableExport.md
          02_Spec_Blender_USD_StableExport.md
      tests\
          (optional) test scripts
  ```

**Step 2 – Add-on Skeleton**

* Implement `bl_info`, `register/unregister`, empty Panel + Operator.
* Make sure the add-on installs and appears in Preferences → Add-ons.

**Step 3 – Data Model for Endpoints**

* Create `PropertyGroup` for an endpoint.
* Add `CollectionProperty` of endpoints on Scene.
* Add UI to manage endpoints (list UI, add/remove, reorder).

**Step 4 – Export Logic**

* Implement operator that:

  * For each endpoint, resolves its target (collection or object).
  * Builds an export call using `bpy.ops.wm.usd_export`.
  * Handles selection/visibility if using `selected_objects_only`.
  * Writes to the chosen filepath.
  * Logs success/failure in Info or in a simple report popup.

**Step 5 – UX Polish**

* Allow single-endpoint export (e.g. “Export Active Endpoint” button).
* Provide global defaults (e.g. default root prim path, default export options).
* Optionally store defaults in add-on preferences.

**Step 6 – Validation & Testing**

* Test with:

  * Simple scenes (few objects, simple collections).
  * Nested collections and parented hierarchies.
  * Scenes with animation, materials, instancing.
* Verify USD outputs with:

  * USDView / Omniverse / other USD tools, depending on your pipeline.

**Step 7 – Packaging**

* Package as a `.zip` add-on for distribution.
* Add docs in `docs/` on how to install and how to use endpoints.

---

### 2. In-Scope (for v1)

* **Blender add-on** written in Python, compatible with Blender 5.0+ (officially released November 18, 2025).
* Ability to define **multiple endpoints** on a per-scene basis:

  * Each endpoint targets either a collection or a root object.
  * Each endpoint defines a USD filepath and basic export options.
* Export operators:

  * Export all endpoints.
  * Export selected/active endpoint.
* Optional:

  * Expose a few critical `usd_export` parameters per endpoint (e.g. animation, materials, root prim path).
  * Simple logging / report view.

---

### 3. Out-of-Scope (for v1)

* **Authoring arbitrary USD composition arcs** (complex references, payloads, variant sets, etc.) beyond what Blender’s exporter natively supports.
* Full **USD stage management** inside Blender (no custom USDStage editing or Hydra viewport).
* Non-USD export formats.
* Deep customization of `USDHook` behavior (may be considered for v2+).
* Cross-version compatibility beyond tested Blender versions (we'll focus on Blender 5.0+ first, with version guards for future versions).

---

If you like, in the **next step** I can:

* Turn this into a more formal **spec document** (`02_Spec_*.md`) with:

  * Precise data structures (`PropertyGroup` definitions),
  * Proposed UI layout (where panels live, how endpoint list looks),
  * And a first-draft code skeleton of the add-on (`__init__.py`, `props.py`, `ops_export.py`, `ui.py`) that you can drop directly into `addon/blender_usd_stableexport`.

[1]: https://www.blender.org/download/releases/5-0/ "Blender 5.0"
[2]: https://docs.blender.org/manual/en/latest/files/import_export/usd.html?utm_source=chatgpt.com "Universal Scene Description - Blender 5.0 Manual"
[3]: https://docs.blender.org/api/current/index.html?utm_source=chatgpt.com "Blender Python API"
[4]: https://upbge.org/docs/latest/api/bpy.ops.wm.html?utm_source=chatgpt.com "Wm Operators — UPBGE/Blender Python API"
[5]: https://developer.blender.org/docs/features/objects/io/usd/?utm_source=chatgpt.com "USD - Blender Developer Documentation"
[6]: https://docs.blender.org/api/current/bpy.types.USDHook.html?utm_source=chatgpt.com "USDHook(bpy_struct) - Blender Python API"
[7]: https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html?utm_source=chatgpt.com "Add-on Tutorial - Blender 5.0 Manual"
[8]: https://developer.blender.org/docs/handbook/extensions/addon_guidelines/?utm_source=chatgpt.com "Add-on Guidelines - Blender Developer Documentation"
[9]: https://docs.blender.org/api/current/bpy.ops.html?utm_source=chatgpt.com "Operators (bpy.ops) - Blender Python API"
[10]: https://docs.blender.org/manual/en/latest/editors/preferences/addons.html?utm_source=chatgpt.com "Add-ons - Blender 5.0 Manual"
[11]: https://docs.blender.org/manual/en/latest/addons/index.html?utm_source=chatgpt.com "Add-ons - Blender 5.0 Manual"




Blender 5.0, officially released November 18, 2025, introduces several important updates affecting your USD export plugin project:

- The USD exporter workflow is simplified: all visible, supported objects in the scene are exported, optionally limited by selection. Blender currently does not support exporting invisible objects, USD layers, variants, or composition arcs directly in the export process.
- Supported exported data types have been expanded and now include meshes, cameras (perspective only), curves, text (as meshes), lights, hair (as curves, limited to parent strands), point clouds, metaballs (animated meshes), volumes, and armatures.
- Export options include controls like root prim path, selection-only export, visibility filter, animation range export, custom properties export, UV maps and normals inclusion, merge parent transforms, triangulation, and texture export paths.
- Some improvements include better material handling via USD Preview Surface shaders with color, metallic, and roughness supported, and experimental instancing support for objects and collections, including partial support for geometry node point instances.
- Limitations remain such as no full support for nested USD composition mechanisms, absolute shape keys are unsupported in shape animation export, and no support yet for bendy bones in armatures.
- Blender 5.0 also updates color management with HDR and wide-gamut support, which may indirectly affect how materials appear when exported to USD.
- Add-on/plugin development should verify changes in Python API especially around import/export operators and scene graph traversal.

For your project to build a Blender 5.0 export plugin for USD:
- Focus on defining export endpoints as visible objects or collections marked via custom properties or panel UI.
- Use the built-in USD export operator bpy.ops.wm.usd_export with relevant arguments for inclusion, animation, and custom properties.
- Keep in mind current exporter limitations (no invisible objects, no composition arcs).
- Plan to use or extend support for instancing experimental features cautiously.
- Review Blender 5.0 Python API docs for updates on bpy.ops, property definitions, and UI API to ensure plugin compatibility.

This knowledge aligns well with your plan to deprecate 4.0 and adopt 5.0 exclusively for your plugin, ensuring you cover the simplified export flow and new data type support without expecting complete USD composition editing inside Blender at this time.

**References:**
- [Blender 5.0 USD Documentation](https://docs.blender.org/manual/en/latest/files/import_export/usd.html)
- [Blender 5.0 Release](https://www.blender.org/download/releases/5-0/)
- [Blender 5.0 New Features](https://cgcookie.com/posts/everything-new-in-blender-5-0)
- [Blender 5.0 Overview](https://www.cgchannel.com/2025/11/blender-5-0-is-out-check-out-its-5-key-features/)

---

## 📋 Blender 5.0 USD Export - Detailed Research

**Note:** The following section provides detailed Blender 5.0-specific information for USD export plugin development.

### Blender 5.0 USD Export - Comprehensive Overview

**Project root**
`E:\SynologyDrive\9999_LocalRepo\Blender_USD_StableExport`

**Working name**
**Blender USD StableExport** – a Blender 5.0 add-on to export specific parts of the scene as USD files via “endpoints”.

---

### 1. Baseline: Blender 5.0 & USD

* **Blender 5.0 final release:** 18 November 2025. ([Blender][1])
* Includes:

  * Improved Vulkan viewport support and HDR / wide-gamut workflows. ([Vagon][2])
  * Updated color management that affects how materials look, including in USD workflows (important for visual match between Blender and downstream USD tools). ([Vagon][2])

**USD support context**

* Blender supports **USD import/export natively** (File → Import/Export → Universal Scene Description). ([Blender Developers][3])
* Manual (5.x “latest”) still describes the same fundamental design:
  **“All visible, supported objects” are exported, optionally limited by selection.** ([Blender Documentation][4])

This is exactly aligned with what you wrote:

> The USD exporter workflow is simplified: all visible, supported objects in the scene are exported, optionally limited by selection. Blender currently does not support exporting invisible objects, USD layers, variants, or composition arcs directly in the export process.

We treat that as authoritative for this project.

---

### 2. Supported / Unsupported USD Features in Blender 5.0

#### 2.1 Supported exported data (Blender 5.0 USD exporter)

From current docs and 5.x coverage plus your notes, the USD exporter exports (as long as they’re visible): ([Blender Documentation][4])

* **Meshes**
* **Cameras** (perspective)
* **Curves**
* **Text** (converted to meshes)
* **Lights**
* **Hair** (as curves, limited to parent strands)
* **Point clouds**
* **Metaballs** (as animated meshes)
* **Volumes**
* **Armatures** (with limitations)
* Instancing (experimental):

  * Object & collection instances
  * Partial support for geometry nodes point instances (still evolving)

Material handling:

* Focus on **USD Preview Surface** shading:

  * Color
  * Metallic
  * Roughness
    (Useful for predictable PBR in downstream DCCs and renderers.)

#### 2.2 Known limitations (relevant to plugin design)

Still **not** supported (or very limited) in the export pipeline: ([Blender Documentation][4])

* Export of **invisible** objects (no “export hidden” mode).
* Authoring **USD layers**, **variants**, or full **composition arcs** directly during export.
* Some animation / rigging features:

  * No absolute shape key animation.
  * No **bendy bones** export for armatures.
* Instancing is not feature-complete; treat geometry-node-based instancing as **experimental**.

For this project, we explicitly **assume**:

> **No direct composition authoring in Blender.**
> The add-on orchestrates USD exports of subsets of a scene, but complex `reference`, `payload`, or `variantSet` networks are authored downstream (e.g., in USD editing tools).

---

### 3. Blender 5.0 Add-on Fundamentals (Python)

Even in 5.0, the add-on structure is the same as previous 4.x versions; the main risk is minor API changes and Python version bumps. Official docs: ([GitHub][5])

#### 3.1 Add-on file structure

We’ll use:

```text
Blender_USD_StableExport/
  addon/
    blender_usd_stableexport/
      __init__.py
      ops_export.py
      props.py
      ui.py
  docs/
    01_Research_Blender_USD_StableExport.md
    02_Spec_Blender_USD_StableExport.md
```

`__init__.py` will contain:

* `bl_info` with Blender version `(5, 0, 0)` as minimum.
* Registration boilerplate for the classes defined in other modules.

Skeleton:

```python
# addon/blender_usd_stableexport/__init__.py

bl_info = {
    "name": "USD Stable Export",
    "author": "Your Name / Studio",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "Scene Properties / 3D Viewport > N-Panel",
    "description": "Export selected parts of the scene to USD via endpoints.",
    "category": "Import-Export",
}

import bpy

from . import props, ops_export, ui  # to be implemented

classes = (
    *props.classes,
    *ops_export.classes,
    *ui.classes,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    props.register_props()

def unregister():
    from bpy.utils import unregister_class
    props.unregister_props()
    for cls in reversed(classes):
        unregister_class(cls)
```

#### 3.2 Key APIs we depend on

* **Scene / Collection / Object** access via `bpy.data`, `bpy.context.scene`, `Scene.collection`, `Collection.children`, `Object.children`. ([GitHub][5])
* **Custom properties & PropertyGroups**:

  * `bpy.types.PropertyGroup`
  * `bpy.props.StringProperty`, `BoolProperty`, `PointerProperty`, `CollectionProperty`, `IntProperty` ([GitHub][5])
* **Operators**:

  * `bpy.types.Operator` subclasses for exporting endpoints.
  * `bpy.ops.wm.usd_export` operator for actual USD writes. ([Blender Stack Exchange][6])
* **Panels / UI**:

  * `bpy.types.Panel` to appear in:

    * Scene Properties, or
    * A dedicated N-Panel tab in the 3D Viewport.

Python version: Blender 5.0 embeds Python 3.11+. We shouldn't rely on external pip packages unless they're vendored or we document install steps; for v1 we'll **stick to `bpy` and standard library**.

---

### 4. USD Export API Shape in 5.0

The exact signature changes slightly with releases, but the **conceptual set of options** for `bpy.ops.wm.usd_export` in 5.x is:

* **Scene subset control:**

  * `filepath` – target `.usd/.usda/.usdc/.usdz`.
  * `selected_objects_only` – limit to selection.
  * Internal design: always “all visible supported objects in the scene or in selection.” ([Blender Documentation][4])
* **Hierarchy / root prim:**

  * `root_prim_path` – root prim in the exported stage.
  * `merge_transform` / “merge parent transforms” style options.
* **Geometry & shading:**

  * Include/exclude UV maps.
  * Include normals.
  * Triangulation (on export).
  * Material export as **USD Preview Surface** (color, metallic, roughness).
* **Animation:**

  * Export animation on a given frame range.
* **Metadata:**

  * Export **custom properties** (Blender’s custom props to USD attributes under a namespace).
* **Texture export paths**, image writing.

Because we don’t have the full callable signature text (manual is CDN-protected), we’ll design the plugin to:

* Expose a subset of options per endpoint (our own datamodel).
* Map them onto `bpy.ops.wm.usd_export` arguments inside code.
* Be prepared to introspect defaults inside Blender using:

  ```python
  bpy.ops.wm.usd_export.get_rna_type().properties
  ```

for debugging when you’re at the machine.

---

### 5. “Endpoint” Concept in Blender 5.0

Blender doesn’t have a USD “stage tree”; instead we have:

* Scenes (`bpy.types.Scene`)
* Collections (`bpy.types.Collection`)
* Objects (`bpy.types.Object`)
* View layers & visibility state (determining what is “visible” for USD export).

Given Blender 5.0’s exporter rule **“visible only”**, our endpoint concept becomes:

> An **Endpoint** = configuration that:
>
> * Identifies a **root** (collection OR object) within the scene,
> * Ensures that this root’s contents are visible and properly filtered,
> * Calls `bpy.ops.wm.usd_export()` to export to a specific filepath with specific options.

Because we **can’t export invisible objects** or author composition arcs directly, endpoints are essentially:

* “Punch out USD segment X from the visible scene”
  rather than “build a fully composed USD stage graph.”

We’ll let downstream tools handle composition (e.g. referencing endpoint USDs into a master stage).

---

### 6. Design Direction for the Add-on (Blender 5.0)

#### 6.1 Endpoint data model

Define a `PropertyGroup` (pseudo-code) in `props.py`:

```python
class USDStableExportEndpoint(bpy.types.PropertyGroup):
    name: StringProperty(
        name="Endpoint Name",
        description="Logical name for this USD export endpoint",
    )

    mode: EnumProperty(
        name="Mode",
        items=[
            ('COLLECTION', "Collection", "Use a collection as the root"),
            ('OBJECT', "Object", "Use an object (and children) as the root"),
        ],
        default='COLLECTION',
    )

    collection: PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
    )

    root_object: PointerProperty(
        name="Root Object",
        type=bpy.types.Object,
    )

    filepath: StringProperty(
        name="USD File",
        subtype="FILE_PATH",
    )

    export_animation: BoolProperty(
        name="Export Animation",
        default=False,
    )

    export_materials: BoolProperty(
        name="Export Materials",
        default=True,
    )

    export_custom_props: BoolProperty(
        name="Export Custom Properties",
        default=True,
    )

    root_prim_path: StringProperty(
        name="Root Prim Path",
        default="/World",
    )

    selection_only: BoolProperty(
        name="Selection Only",
        description="Export only selected objects (filtered by this endpoint)",
        default=False,
    )

    # Future: UVs, normals, triangulation, texture paths, etc.
```

Attach this to Scene:

```python
bpy.types.Scene.usd_stable_export_endpoints = CollectionProperty(
    type=USDStableExportEndpoint
)
bpy.types.Scene.usd_stable_export_index = IntProperty(default=0)
```

Endpoints live **per scene**, so different scenes can have different export recipes.

#### 6.2 Endpoint UI

Panel (e.g. in Scene properties):

* **List UI** of endpoints:

  * Add / Remove buttons.
  * Move up/down.
* For the active endpoint:

  * Name.
  * Mode (Collection/Object).
  * Collection or Object picker (depending on mode).
  * Filepath.
  * Animation toggle.
  * Materials toggle.
  * Custom props toggle.
  * Root prim path.
  * “Selection only” checkbox.

Buttons:

* **Export Active Endpoint**
* **Export All Endpoints**

#### 6.3 Export behavior in 5.0 constraints

Implementation idea for `Export Active`:

1. Identify active endpoint.
2. Ensure its target (collection/object) is valid.
3. Temporarily adjust selection / visibility if needed:

   * If `selection_only`:

     * Deselect everything.
     * Select all objects under the endpoint root.
   * If not:

     * It might be enough to rely on collection filtering:

       * Possibly configure exporter’s `collection` parameter, if still available.
4. Call `bpy.ops.wm.usd_export()` with:

   * `filepath` from endpoint.
   * `selected_objects_only` according to the endpoint.
   * `export_animation`, `export_materials`, `export_custom_properties` etc.

We must **not** try to export hidden objects or treat hidden collections as included; that’s impossible in 5.0’s exporter design.

#### 6.4 Limitations we must embrace explicitly

* No “author USD layers/variants/composition arcs” inside Blender.
* No export of hidden objects; the add-on should:

  * Maybe show a warning if the endpoint’s target collection or root object is hidden / disabled in viewport and therefore won’t export.
* Experimental instancing:

  * We can add a global option like “Respect instances (experimental)” but should label it clearly as such in UI and docs.

---

### 7. Scope & Out-of-Scope (Updated for Blender 5.0)

#### 7.1 In-scope (v1, Blender 5.0 only)

* **Target: Blender 5.0+ only.**

  * `blender` field in `bl_info` set accordingly.
* Define multiple **per-scene endpoints**, each:

  * References a collection or object root.
  * Writes a USD file via `bpy.ops.wm.usd_export`.
  * Has basic per-endpoint options:

    * Filepath
    * Animation on/off
    * Materials on/off
    * Custom props on/off
    * Root prim path
    * Selection-only toggle
* UI to manage endpoints (add/remove/reorder) and run:

  * “Export Active Endpoint”
  * “Export All Endpoints”
* Respect **Blender 5.0 visibility rules** for USD export:

  * Only visible objects export.
* Provide **basic logging** (Info, report popup).

#### 7.2 Out-of-scope (for v1)

* Supporting Blender 4.x or earlier.
* Exporting hidden objects, or hacking around 5.0’s design to force invisibles.
* Authoring:

  * USD layers
  * Variant sets
  * References / payload graphs
    (These are handled downstream in dedicated USD tools.)
* Deep use of `USDHook` or custom USD manipulation beyond calling the exporter.
* Robust handling of all experimental instancing edge cases; we’ll simply “pass through” Blender’s behavior.

---

### 8. Next Document: Implementation Spec

For the **next step** you requested (“define the steps, define what’s in scope and out of scope, define what this plugin is supposed to do”), we’re basically there conceptually.

If you want, I can now draft:

`E:\SynologyDrive\9999_LocalRepo\Blender_USD_StableExport\docs\02_Spec_Blender_USD_StableExport.md`

containing:

* Precise `PropertyGroup` definitions (ready-to-paste code shapes).
* Operator signatures (`EXPORT_OT_active_endpoint`, `EXPORT_OT_all_endpoints`).
* Panel layout sketches (which properties live where).
* And a minimal **first working code skeleton** for:

  * `__init__.py`
  * `props.py`
  * `ops_export.py`
  * `ui.py`

that you can drop directly into `addon/blender_usd_stableexport` and start testing in Blender 5.0.

[1]: https://www.blender.org/download/releases/5-0/?utm_source=chatgpt.com "5.0 — Blender"
[2]: https://vagon.io/blog/what-s-new-in-blender-5-0-real-improvements-that-actually-change-your-workflow?utm_source=chatgpt.com "What's New in Blender 5.0: Real Improvements That ..."
[3]: https://developer.blender.org/docs/release_notes/2.82/import_%26_export/?utm_source=chatgpt.com "Import & Export - Blender Developer Documentation"
[4]: https://docs.blender.org/manual/en/latest/files/import_export/usd.html?utm_source=chatgpt.com "Universal Scene Description - Blender 5.0 Manual"
[5]: https://github.com/robmcrosby/BlenderUSDZ?utm_source=chatgpt.com "Simple USDZ file exporter plugin for Blender3D"
[6]: https://blender.stackexchange.com/questions/173240/is-it-possible-to-export-as-usd-using-python?utm_source=chatgpt.com "Is it possible to export as USD using python?"
[7]: https://en.wikipedia.org/wiki/Blender_%28software%29?utm_source=chatgpt.com "Blender (software)"




usd-wg-assets guidelinesusd-wg-assets guidelines
https://lf-aswf.atlassian.net/wiki/spaces/WGUSD/pages/11273723/Guidelines+for+Structuring+USD+Assets
vfx intent project
https://github.com/usd-wg/assets/tree/main/intent-vfx