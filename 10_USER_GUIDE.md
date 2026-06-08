---
arys_schema_version: '1.2'
id: 7083457c-477f-4a6d-ba2a-a2796f463ec7
title: Blender USD Multi Export - User Guide
type: PRACTICAL
status: active
trust_level: 2
visibility: internal
created: '2026-02-17T09:42:16Z'
last_modified: '2026-02-17T09:42:16Z'
---

# Blender USD Multi Export - User Guide

**Version**: v0.1.3 (MVP Release)  
**Date**: 23.12.2025  
**Last Updated**: 03.02.2026 23:27  
**Target Platform**: Blender 5.0+
**Tag block:**
#blender #framework_integration #best_practices #export #conversion #troubleshooting #collections #list_operations #openusd #usd_core #omniverse #hybrid #references #analysis #workflow_automation #quality_assurance #validation #deterministic_workflows

---

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [UI Overview](#ui-overview)
- [Step-by-Step Workflows](#step-by-step-workflows)
- [Common Scenarios](#common-scenarios)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [FAQ](#faq)
- [Limitations & Known Issues](#limitations--known-issues)

---

## Overview

**Blender USD Multi Export v0.1.3** is a Blender addon that enables you to define multiple export StartPoints (collections or objects) in a single Blender scene and export them as separate USD files in batch operations. This is particularly useful for workflows where you need to export different parts of a scene separately, such as for use in NVIDIA Omniverse or other USD-based pipelines.

### Key Features (MVP v0.1.3)

- ✅ **StartPoint-Based Export**: Define collections as export StartPoints
- ✅ **Batch Export**: Export multiple StartPoints in a single operation
- ✅ **Scene State Safety**: Non-destructive export with automatic state restoration
- ✅ **Cross-Platform Paths**: Relative path storage with automatic resolution
- ✅ **Comprehensive Logging**: Verbose mode and automated bug reports
- ✅ **User-Friendly UI**: Integrated panel in Scene Properties

---

## Installation

### Prerequisites

- **Blender 5.0+** (officially released November 18, 2025)
- **Python 3.11+** (bundled with Blender 5.0)
- **USD Support**: Blender's built-in USD exporter (included with Blender 5.0+)

### Installation Steps

#### Method 1: Install from Local Repository (Recommended for Testing)

If you already have the repository locally:

1. **Open Blender 5.0+**
2. **Go to `Edit > Preferences > Add-ons`**
3. **Click `Install...`**
4. **Navigate to your local repository** (`Blender_USD_MultiExport`) and select the `addon` folder
   - **Important**: Select the `addon` folder, not the repository root
   - The path should be: `Blender_USD_MultiExport/addon/`
5. **Enable the addon** by checking the box next to "USD Multi Export"
6. **Click `Save Preferences`**

#### Method 2: Install from GitHub

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jph2/Blender_USD_MultiExport.git
   cd Blender_USD_MultiExport
   ```

2. **Follow Method 1 steps 1-6** above to install in Blender

### Verify Installation

After installation, you should see:

- ✅ "USD Multi Export" addon listed in `Edit > Preferences > Add-ons` (enabled)
- ✅ "USD Multi Export" panel in the Scene Properties tab (right-side panel)
- ✅ No error messages in Blender's console

**If you see errors**: Check Blender's console (`Window > Toggle System Console` on Windows) for error messages. Common issues:
- Wrong folder selected (must select `addon` folder, not repository root)
- Blender version too old (requires 5.0+)
- Missing dependencies (should not occur with Blender 5.0+)

---

## Getting Started

### Quick Start (5 Minutes)

1. **Prepare Your Scene**:
   - Open a Blender scene with organized collections
   - Ensure collections are properly named (e.g., "Characters", "Props", "Vehicles")
   - **Important**: Collection names are case-sensitive and must match exactly

2. **Access the Addon**:
   - Go to the **Scene Properties** tab (icon with a sphere)
   - Scroll down to find the **"USD Multi Export"** panel
     - **important** -> some plugins 'occupy' the scene porperties and Prevent the MultiExport to be shown.
       - Bonsai (a BIM plugin)

3. **Create Your First StartPoint**:
   - Click **"Add"** button in the StartPoints section
   - A new StartPoint will appear in the list
   - Click on the StartPoint name field and rename it (e.g., "Characters")
   - Enter the collection name in the collection field (must match exactly)
   - Click the folder icon to set the filepath (e.g., `//export/characters.usd`)

4. **Export**:
   - Ensure the StartPoint is enabled (checkbox checked)
   - Click **"Export StartPoints"** button
   - Check Blender's console or the export location for results

### Understanding StartPoints

An **StartPoint** is a definition that tells the addon:
- **What** to export (which collection)
- **Where** to export it (filepath)
- **How** to name it (StartPoint name becomes root prim path)

**Example**:
- StartPoint Name: `Characters`
- Collection: `Characters` (must match existing collection)
- Filepath: `//export/characters.usd`
- Result: Exports the "Characters" collection to `export/characters.usd` with root prim `/Characters`

---
### Understanding Filepaths: How to Make the Right Relative Path

Blender-relative paths start with `//`.
This means: **start from the folder where the current `.blend` file is saved**.

Example project structure:

```text
ProjectFolder/
├── 000_SOURCE/
├── 010_ASS_USD/
├── 020_BASE_LYR/
├── 030_SIM_LYR/
└── 040_DATA_LYRs/
```

If your `.blend` file is saved inside:

```text
ProjectFolder/000_SOURCE/
```

and you want to export to:

```text
ProjectFolder/010_ASS_USD/USD_Startpoint/
```

then you need to go **one folder up** from `000_SOURCE`, and then into `010_ASS_USD/USD_Startpoint`.

Use this filepath:

```text
../010_ASS_USD/USD_Startpoint/Neubau einer Montagehalle 2. - BA III.usd
```

Path logic:

```text
            = start at the .blend file location
../         = go one folder up
010_ASS_USD = go into the USD export folder
USD_Startpoint = go into the Startpoint folder
filename.usd = exported USD file
```

Important:

```text
//../010_ASS_USD/USD_Startpoint/your_file_name.usd
```

Use forward slashes `/`, also on Windows. Make sure folder names match exactly, including spelling and capitalization. Avoid double file endings like `..usd`; use only `.usd`.


---

## UI Overview

The **USD Multi Export** panel is located in **Scene Properties** (right-side panel, icon with a sphere).

### Why Scene Properties?

This addon uses **Scene Properties** because:

- ✅ **Follows Blender Conventions**: Blender's built-in USD exporter also uses Scene Properties
- ✅ **Scene-Level Operations**: USD export affects entire scenes, not individual objects
- ✅ **Persistent Access**: Panel remains visible while you work, without interrupting your workflow
- ✅ **Professional Integration**: Uses standard Blender UI patterns that users expect

> **Best Practice Reference**: For detailed UI/UX placement guidance, see [Building for Blender - UI/UX Placement Best Practices](../../OV_Dev/OV_USD_Scripts/best_practise_Blender%20Extensions_addons/building_for_Blender.md#uiux-placement-best-practices).

### Panel Layout

```
┌─────────────────────────────────────┐
│ USD Multi Export                    │
├─────────────────────────────────────┤
│ StartPoints                            │
│ [Add] [Remove]                       │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ ☑ StartPoint Name | Collection    │ │
│ │ ☑ StartPoint 2    | Props         │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ☐ Verbose Logging                   │
│                                     │
│ [Export StartPoints]                  │
│                                     │
│ [Generate Bug Report]              │
└─────────────────────────────────────┘
```

### UI Elements

#### StartPoints Section

- **Add Button**: Creates a new StartPoint with default name "StartPoint N"
- **Remove Button**: Removes the last StartPoint in the list
- **StartPoint List**: Shows all defined StartPoints with:
  - **Checkbox**: Enable/disable this StartPoint for export
  - **Name Field**: StartPoint name (used as root prim path)
  - **Collection Field**: Collection name (must match existing collection exactly)

#### Settings

- **Verbose Logging**: Enable detailed console output for debugging
  - **When to use**: When troubleshooting export issues or developing workflows
  - **Output**: Detailed step-by-step logs in Blender's console

#### Actions

- **Export StartPoints**: Batch export all enabled StartPoints
  - **Icon**: Export icon (box with arrow)
  - **Behavior**: Exports all enabled StartPoints sequentially
  - **Feedback**: Success/failure messages in Blender's info area

- **Generate Bug Report**: Create a comprehensive bug report JSON file
  - **When to use**: When encountering errors or unexpected behavior
  - **Output**: JSON file with system info, scene state, and operation logs
  - **Location**: Saved to Blender's temp directory with timestamp

---

## Step-by-Step Workflows

### Workflow 1: Basic Single StartPoint Export

**Goal**: Export one collection as a USD file

1. **Prepare Scene**:
   - Ensure you have a collection named "Props" (or your desired name)
   - Ensure the collection contains objects you want to export

2. **Create StartPoint**:
   - Open Scene Properties → USD Multi Export panel
   - Click **"Add"**
   - Set StartPoint name: `Props`
   - Set collection name: `Props` (must match exactly)
   - Set filepath: `//export/props.usd` (or click folder icon to browse)

3. **Export**:
   - Ensure StartPoint is enabled (checkbox checked)
   - Click **"Export StartPoints"**
   - Check console for success message
   - Verify file exists at `export/props.usd` (relative to your .blend file)

### Workflow 2: Batch Export Multiple Collections

**Goal**: Export multiple collections as separate USD files

1. **Prepare Scene**:
   - Organize scene into collections: "Characters", "Props", "Vehicles"
   - Ensure each collection has content

2. **Create Multiple StartPoints**:
   - Click **"Add"** three times (or once per collection)
   - Configure each StartPoint:
     - StartPoint 1: Name=`Characters`, Collection=`Characters`, Filepath=`//export/characters.usd`
     - StartPoint 2: Name=`Props`, Collection=`Props`, Filepath=`//export/props.usd`
     - StartPoint 3: Name=`Vehicles`, Collection=`Vehicles`, Filepath=`//export/vehicles.usd`

3. **Export All**:
   - Ensure all StartPoints are enabled
   - Click **"Export StartPoints"**
   - All enabled StartPoints will export sequentially
   - Check console for individual success/failure messages

### Workflow 3: Selective Export (Enable/Disable)

**Goal**: Export only specific StartPoints from a larger set

1. **Create All StartPoints** (as in Workflow 2)

2. **Disable Unwanted StartPoints**:
   - Uncheck the checkbox next to StartPoints you don't want to export
   - Only enabled StartPoints will be exported

3. **Export**:
   - Click **"Export StartPoints"**
   - Only enabled StartPoints will export

### Workflow 4: Debugging with Verbose Logging

**Goal**: Troubleshoot export issues

1. **Enable Verbose Logging**:
   - Check **"Verbose Logging"** checkbox in the panel

2. **Open Console**:
   - Windows: `Window > Toggle System Console`
   - macOS/Linux: Launch Blender from terminal

3. **Perform Export**:
   - Export as normal
   - Watch console for detailed step-by-step logs

4. **Generate Bug Report** (if needed):
   - Click **"Generate Bug Report"**
   - Bug report JSON will be saved with system info and logs
   - Attach to bug reports or review for troubleshooting

---

## Common Scenarios

### Scenario 1: Exporting for Omniverse

**Use Case**: Export Blender assets for use in NVIDIA Omniverse

**Steps**:
1. Organize Blender scene into collections (e.g., "Characters", "Props", "Set")
2. Create StartPoints for each collection
3. Use relative paths: `//export/characters.usd`
4. Export all StartPoints
5. Import USD files into Omniverse using references

**Important Notes**:
- Avoid using "Environment" as a collection name (conflicts with Omniverse's `/environment` lighting)
- Use descriptive names: "Props", "Set", "Location", "SceneElements"
- Root prim path will be `/StartPointName` (e.g., `/Characters`)

### Scenario 2: Creating Asset Library

**Use Case**: Create a USD asset library from a Blender scene

**Steps**:
1. Organize scene into logical asset groups (collections)
2. Create StartPoints for each asset group
3. Use consistent naming: `//assets/asset_name.usd`
4. Export all StartPoints
5. Result: Organized USD asset library

### Scenario 3: Exporting Different LODs

**Use Case**: Export multiple levels of detail for the same asset

**Current Limitation**: MVP v0.1.3 exports collections as-is. For LOD workflows:
- Create separate collections for each LOD (e.g., "Character_LOD0", "Character_LOD1")
- Create separate StartPoints for each LOD collection
- Export all LOD StartPoints

**Future Enhancement**: Per-StartPoint export options (planned for v0.2.0+)

---

## Troubleshooting

### Problem: "Collection not found" Error

**Symptoms**: Export fails with error about collection not existing

**Causes**:
- Collection name doesn't match exactly (case-sensitive)
- Collection was renamed or deleted
- Typo in collection name field

**Solutions**:
1. Check collection name in Blender's Outliner
2. Ensure StartPoint collection name matches exactly (case-sensitive)
3. Verify collection exists and contains objects

### Problem: Export Fails Silently

**Symptoms**: Click "Export StartPoints" but nothing happens, no error message

**Solutions**:
1. **Enable Verbose Logging**: Check "Verbose Logging" and check console
2. **Check Console**: Look for error messages in Blender's console
3. **Verify StartPoints**: Ensure at least one StartPoint is enabled
4. **Check Filepath**: Ensure filepath is valid and writable
5. **Generate Bug Report**: Use "Generate Bug Report" to capture system state

### Problem: Filepath Issues

**Symptoms**: Export fails with filepath-related errors

**Common Issues**:
- **Relative paths not resolving**: Use `//` prefix for Blender-relative paths
- **Directory doesn't exist**: Addon will create directories automatically
- **Permission errors**: Ensure export directory is writable
- **Invalid characters**: Avoid special characters in filenames

**Solutions**:
1. Use Blender-relative paths: `//export/filename.usd`
2. Ensure parent directory exists or is writable
3. Use forward slashes in paths (addon handles conversion)
4. Avoid special characters: `<>:"|?*`

### Problem: Scene State Not Restored

**Symptoms**: After export, scene visibility or state is changed

**Expected Behavior**: Scene state should be automatically restored

**Solutions**:
1. **Report as Bug**: This should not happen - generate bug report
2. **Manual Restore**: Use Blender's undo (Ctrl+Z) if needed
3. **Check Logs**: Enable verbose logging to see state restoration steps

### Problem: Addon Not Appearing

**Symptoms**: "USD Multi Export" panel doesn't appear in Scene Properties

**Solutions**:
1. **Verify Installation**: Check `Edit > Preferences > Add-ons` for "USD Multi Export"
2. **Check Enable Status**: Ensure addon is enabled (checkbox checked)
3. **Check Blender Version**: Requires Blender 5.0+ (check version in splash screen)
4. **Check Console**: Look for import errors in console
5. **Reinstall**: Try removing and reinstalling the addon

---

## Best Practices

### Collection Organization

✅ **Do**:
- Use descriptive, clear collection names
- Organize logically (by asset type, by LOD, by purpose)
- Keep collection names consistent across scenes
- Use PascalCase or snake_case (avoid spaces)

❌ **Don't**:
- Use "Environment" as collection name (Omniverse conflict)
- Use special characters in collection names
- Create overly nested collections (keep it simple)
- Use reserved names (e.g., "World", "Scene")

### Filepath Management

✅ **Do**:
- Use Blender-relative paths (`//export/filename.usd`)
- Organize exports in subdirectories (`//export/characters/hero.usd`)
- Use consistent naming conventions
- Keep paths relative to .blend file location

❌ **Don't**:
- Use absolute paths (breaks portability)
- Use spaces in filenames (use underscores or hyphens)
- Export to system directories (use project directories)
- Overwrite important files without backups

### StartPoint Configuration

✅ **Do**:
- Use meaningful StartPoint names (becomes root prim path)
- Match collection names exactly (case-sensitive)
- Enable/disable StartPoints as needed for selective export
- Test StartPoints individually before batch export

❌ **Don't**:
- Use generic names like "StartPoint 1" (use descriptive names)
- Create StartPoints for non-existent collections
- Leave StartPoints enabled if you don't want them exported
- Create duplicate StartPoints (one per collection)

### Workflow Optimization

✅ **Do**:
- Save .blend file before first export (StartPoints are saved with scene)
- Use verbose logging during development/testing
- Generate bug reports when encountering issues
- Test with simple scenes before complex scenes

❌ **Don't**:
- Export unsaved scenes without understanding relative paths
- Export without checking console for errors
- Ignore error messages (they contain useful information)
- Export large scenes without testing performance

---

## FAQ

### Q: Can I export individual objects instead of collections?

**A**: MVP v0.1.3 supports collections only. For individual objects:
- Create a collection containing the object(s)
- Export the collection
- **Future Enhancement**: Direct object export (planned for v0.2.0+)

### Q: Can I customize export settings per StartPoint?

**A**: MVP v0.1.3 uses default export settings for all StartPoints:
- Materials: Enabled
- UV Maps: Enabled
- Normals: Enabled
- Animation: Disabled

**Future Enhancement**: Per-StartPoint export options (planned for v0.2.0+)

### Q: How do I export animations?

**A**: MVP v0.1.3 exports static geometry only (animation disabled). For animated exports:
- Use Blender's native USD export (`File > Export > USD`)
- **Future Enhancement**: Animation support per StartPoint (planned for v0.2.0+)

### Q: Can I use this with Blender 4.x?

**A**: No. This addon requires Blender 5.0+ due to USD export API changes. Blender 4.x is not supported.

### Q: Where are exported files saved?

**A**: Files are saved relative to your .blend file location:
- If .blend file is at: `C:\Projects\MyScene.blend`
- And filepath is: `//export/characters.usd`
- Exported file will be at: `C:\Projects\export\characters.usd`

### Q: Can I export to absolute paths?

**A**: Yes, but not recommended. Use absolute paths only if necessary:
- Breaks portability (paths won't work on other machines)
- Use relative paths (`//export/filename.usd`) for best practice

### Q: What happens if an export fails?

**A**: The addon will:
- Log the error with details
- Continue with remaining StartPoints (if batch export)
- Report success/failure count at the end
- Preserve scene state (no permanent changes)

### Q: How do I report bugs?

**A**: 
1. Enable "Verbose Logging"
2. Reproduce the issue
3. Click "Generate Bug Report"
4. Create a GitHub issue and attach the bug report JSON file

### Q: Can I use this addon in production?

**A**: MVP v0.1.3 is released for **testing and evaluation**. It provides core functionality but:
- Some features are planned for future versions
- Thorough testing recommended before production use
- Report issues and feedback to help improve the addon

---

## Limitations & Known Issues

### MVP v0.1.3 Limitations

- **Collections Only**: Individual object export not supported (use collections)
- **Fixed Export Settings**: All StartPoints use same export settings (no per-StartPoint options)
- **No Animation**: Static geometry only (animation disabled)
- **No Validation**: Pre-flight validation not implemented (planned for v0.2.0+)
- **No Progress Indicators**: No progress bar for batch exports
- **No Presets**: Export presets not available (planned for v0.2.0+)

### Known Issues

- **Remove Button**: Removes last StartPoint only (not selected StartPoint)
  - **Workaround**: Remove StartPoints in reverse order
  - **Future Fix**: Select-and-remove functionality (planned for v0.2.0+)

- **No StartPoint Reordering**: StartPoints cannot be reordered in UI
  - **Workaround**: Remove and recreate in desired order
  - **Future Fix**: Drag-and-drop reordering (planned for v0.2.0+)

### Planned Enhancements (v0.2.0+)

- Per-StartPoint export options (materials, UVs, normals, animation)
- Pre-flight validation (collection existence, filepath validation)
- Progress indicators for batch exports
- Export presets (common configurations)
- Individual object export (not just collections)
- Root prim path customization (beyond StartPoint name)
- ASWF USD compliance features

---

## Additional Resources

- **Project README**: [README.md](README.md) - Project overview and status
- **Testing Plan**: [05_Testing_Plan.md](05_Testing_Plan.md) - Testing procedures
- **Implementation Plan**: [04_Implementation_Plan.md](04_Implementation_Plan.md) - Development roadmap
- **Naming Conventions**: [NAMING_CONVENTIONS.md](NAMING_CONVENTIONS.md) - Collection naming guidelines
- **Project Progress**: [PROJECT_PROGRESS_LOG.md](PROJECT_PROGRESS_LOG.md) - Development history

---

**Last Updated**: December 23, 2025  
**Version**: v0.1.3 (MVP Release)
