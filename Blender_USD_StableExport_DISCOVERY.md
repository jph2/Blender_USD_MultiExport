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
  → **Blender 4.2 LTS** (current long-term support series). ([Blender][1])
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
    "blender": (4, 2, 0),
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

* **Develop against a fixed Blender LTS version** (4.2).
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
   * Strategy: develop and support 4.2 LTS first; optionally add version-guards later.

---

## 🧭 Initial Project Plan, Scope & Out-of-Scope

### 1. High-Level Steps

**Step 1 – Environment & Repo**

* Use **Blender 4.2 LTS** as dev target.
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

* **Blender add-on** written in Python, compatible with Blender 4.2 LTS.
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
* Cross-version compatibility beyond tested Blender versions (we’ll focus on 4.2 LTS first).

---

If you like, in the **next step** I can:

* Turn this into a more formal **spec document** (`02_Spec_*.md`) with:

  * Precise data structures (`PropertyGroup` definitions),
  * Proposed UI layout (where panels live, how endpoint list looks),
  * And a first-draft code skeleton of the add-on (`__init__.py`, `props.py`, `ops_export.py`, `ui.py`) that you can drop directly into `addon/blender_usd_stableexport`.

[1]: https://www.blender.org/download/lts/4-2/?utm_source=chatgpt.com "Blender 4.2 LTS"
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
