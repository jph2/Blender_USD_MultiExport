---
arys_schema_version: '1.2'
id: fa80dbe1-3fc2-4c68-aefc-805e57591020
title: Building Blender USD Multi Export Add-on
type: TECHNICAL
status: active
trust_level: 2
created: '2026-02-17T09:42:16Z'
last_modified: '2026-02-17T09:42:16Z'
---

# Building Blender USD Multi Export Add-on

**Version**: 0.1.3  
**Date**: 18.01.2026  
**Last Updated**: 03.02.2026 23:27  
**Purpose**: Step-by-step guide for building the Blender USD Multi Export add-on from source
**Tag block:**
#blender #framework_integration #export #conversion #construction #troubleshooting #vscode #extensionui #openusd #usd_core #references #analysis #workflow_automation #quality_assurance #validation #best_practices #deterministic_workflows

---

## 📖 Table of Contents

- [What is Building?](#what-is-building)
- [Prerequisites](#prerequisites)
- [Step-by-Step Build Instructions](#step-by-step-build-instructions)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## What is Building?

**What is a package?** A package (`.zip` file) is a compressed archive containing all the add-on files. Blender uses ZIP files to install add-ons easily.

**What is building?** Building means creating the `.zip` package file from the source code. This package can then be installed in Blender via the Extensions system (Edit → Preferences → Extensions → Install from Disk).

**Why build from source?** You might want to build from source if:
- You've made changes to the code
- You want to test the latest version
- You want to customize the add-on
- The pre-built package isn't available

---

## Prerequisites

Before building, you need to install the required tools:

### Python 3.7+

**What is Python?** Python is a programming language. Blender includes Python, but you need Python installed on your system to run the build script.

**Check if Python is installed**:

1. Open a terminal/command prompt
2. Type: `python --version`
3. ✅ **Success**: Shows version (e.g., "Python 3.9.0")
4. ❌ **Failed**: Shows "command not found"

**If Python is not found**:
- **Windows**: Python might be installed but not in PATH. Try `py --version` instead
- **Mac**: Install Python from python.org or use Homebrew: `brew install python3`
- **Linux**: Install via package manager: `sudo apt install python3` (Ubuntu/Debian)

**Note**: Blender add-ons are built using standard Python (not Blender's bundled Python). Any Python 3.7+ installation will work.

---

## Step-by-Step Build Instructions

### Quick Start (Copy & Paste Ready)

**Windows (PowerShell)**:
```powershell
cd E:\SynologyDrive\9999_LocalRepo\Blender_USD_MultiExport
python scripts\build_extension.py
```

**Windows (Command Prompt)**:
```cmd
cd E:\SynologyDrive\9999_LocalRepo\Blender_USD_MultiExport
python scripts\build_extension.py
```

**Mac/Linux**:
```bash
cd /path/to/Blender_USD_MultiExport
python3 scripts/build_extension.py
```

---

### Detailed Steps

#### Step 1: Open Terminal/Command Prompt

**What is a terminal?** A terminal (also called command prompt or PowerShell) is a text-based interface where you type commands.

**How to open**:
- **Windows**: Press `Win + R`, type `cmd` or `powershell`, press Enter
- **Mac**: Press `Cmd + Space`, type "Terminal", press Enter
- **Linux**: Press `Ctrl + Alt + T` (most distributions)

#### Step 2: Navigate to Repository Folder

**What is navigating?** Navigating means changing to the folder where the project files are located.

**Command**:
```bash
cd E:\SynologyDrive\9999_LocalRepo\Blender_USD_MultiExport
```

**⚠️ Important**: Replace the path with your actual repository location.

**What you'll see**:
- ✅ **Success**: Prompt changes to show the folder path
- ❌ **Failed**: Shows "The system cannot find the path specified" (Windows) or "No such file or directory" (Mac/Linux)

**If navigation fails**:
- Check that the path is correct
- Use quotes if path has spaces: `cd "E:\My Folder\Blender_USD_MultiExport"`
- On Mac/Linux, use forward slashes: `/Users/username/path/to/Blender_USD_MultiExport`

#### Step 3: Run Build Script

**What is the build script?** `scripts/build_extension.py` is a Python script that automates the build process. It packages all add-on files into a ZIP file ready for installation.

**Command**:
```bash
python scripts/build_extension.py
```

**⚠️ Note**: On Mac/Linux, you might need `python3` instead of `python`.

**What happens**:
1. Script checks if the add-on directory exists
2. Script verifies `__init__.py` exists in the add-on folder
3. Script creates `dist/` folder (if it doesn't exist)
4. Script packages all add-on files into a ZIP file
5. Script excludes unnecessary files (tests, docs, cache files)
6. Script shows success message with file location

**What you'll see**:
```
Building Blender USD Multi Export Extension...
Source: E:\...\Blender_USD_MultiExport\blender_usd_multiexport_addon
Output: E:\...\Blender_USD_MultiExport\dist\blender_usd_multiexport.zip

Packaging files...
  Added: blender_usd_multiexport_addon/__init__.py
  Added: blender_usd_multiexport_addon/ops_export.py
  ...

[SUCCESS] Extension built successfully!
   File: E:\...\Blender_USD_MultiExport\dist\blender_usd_multiexport.zip
   Size: 0.05 MB (52,123 bytes)
   Files: 8

[INSTALL] Installation:
   1. Open Blender 5.0+
   2. Edit > Preferences > Extensions
   3. Click dropdown (top right) > Install from Disk
   4. Select: E:\...\Blender_USD_MultiExport\dist\blender_usd_multiexport.zip
   5. Extension will be installed and available
```

**If build fails**:
- See [Troubleshooting](#troubleshooting) section below
- Check that Python is installed correctly
- Verify you're in the correct folder
- Check that `blender_usd_multiexport_addon/` folder exists

---

### Alternative: Manual Build (Advanced)

If the build script doesn't work, you can build manually:

**Step 1**: Navigate to repository folder (same as above)

**Step 2**: Create a ZIP file manually:
```bash
# Windows (PowerShell)
Compress-Archive -Path blender_usd_multiexport_addon\* -DestinationPath dist\blender_usd_multiexport.zip

# Mac/Linux
cd blender_usd_multiexport_addon
zip -r ../dist/blender_usd_multiexport.zip .
cd ..
```

**⚠️ Important**: The ZIP file must contain the `blender_usd_multiexport_addon` folder (not just its contents). Blender expects the add-on folder name to match the module name.

---

## Verification

After building, verify the package was created:

### Method 1: Check File Exists

**Windows**:
```powershell
Test-Path dist\blender_usd_multiexport.zip
# Should return: True
```

**Mac/Linux**:
```bash
ls dist/blender_usd_multiexport.zip
# Should show the file
```

### Method 2: Check File Size

The package should be several KB in size (typically 10-100 KB depending on content).

**Windows**:
```powershell
(Get-Item dist\blender_usd_multiexport.zip).Length
```

**Mac/Linux**:
```bash
ls -lh dist/blender_usd_multiexport.zip
```

### Method 3: Visual Check

1. Open File Explorer (Windows) or Finder (Mac)
2. Navigate to `dist/` folder
3. Look for `blender_usd_multiexport.zip`
4. ✅ **Success**: File exists and has a reasonable size
5. ❌ **Failed**: File doesn't exist or is 0 bytes

### Method 4: Verify ZIP Contents

**Windows**: Right-click the ZIP file → "Extract All" → Check that `blender_usd_multiexport_addon` folder exists inside

**Mac/Linux**:
```bash
unzip -l dist/blender_usd_multiexport.zip | head -20
# Should show files starting with "blender_usd_multiexport_addon/"
```

---

## Troubleshooting

### Problem: "Python not found" or "python: command not found"

**What this means**: The terminal can't find Python.

**Solutions**:

1. **Try `python3` instead**:
   ```bash
   python3 scripts/build_extension.py
   ```

2. **Windows: Try `py` command**:
   ```cmd
   py scripts\build_extension.py
   ```

3. **Check Python installation**:
   - Verify Python is installed: `python --version`
   - Reinstall Python if needed
   - Make sure Python is added to your PATH during installation

### Problem: "The system cannot find the path specified" (Windows)

**What this means**: The folder path doesn't exist or is incorrect.

**Solutions**:

1. **Check the path**:
   - Verify the repository folder exists
   - Copy the path from File Explorer

2. **Use quotes for paths with spaces**:
   ```cmd
   cd "E:\My Folder\Blender_USD_MultiExport"
   ```

3. **Navigate step by step**:
   ```cmd
   cd E:\
   cd SynologyDrive
   cd 9999_LocalRepo
   cd Blender_USD_MultiExport
   ```

### Problem: "ERROR: Addon directory not found"

**What this means**: The build script can't find the `blender_usd_multiexport_addon` folder.

**Solutions**:

1. **Check folder name**:
   - Verify `blender_usd_multiexport_addon/` folder exists in repository root
   - Check spelling (must match exactly)

2. **Check you're in the right directory**:
   - Make sure you're in the repository root (where `README.md` is located)
   - The `scripts/` folder should be visible

3. **Verify folder structure**:
   - Repository root should contain: `blender_usd_multiexport_addon/`, `scripts/`, `README.md`

### Problem: "ERROR: __init__.py not found"

**What this means**: The add-on folder exists but doesn't have `__init__.py` file.

**Solutions**:

1. **Check `__init__.py` exists**:
   - Navigate to `blender_usd_multiexport_addon/` folder
   - Verify `__init__.py` file exists
   - Check file is not corrupted

2. **Verify add-on structure**:
   - The `__init__.py` file must be in the add-on folder root
   - It should contain `bl_info` dictionary with add-on metadata

### Problem: "PermissionError" or "File is locked"

**What this means**: The ZIP file is open in another program (likely Blender).

**Solutions**:

1. **Close Blender**:
   - If Blender is open, close it completely
   - The build script will create a new ZIP with a timestamp if the file is locked

2. **Wait and retry**:
   - Wait a few seconds and run the build script again
   - The script will automatically create a new file with a timestamp

3. **Manually delete old ZIP**:
   - Navigate to `dist/` folder
   - Delete `blender_usd_multiexport.zip` manually
   - Run build script again

### Problem: "Build succeeds but ZIP is empty or too small"

**What this means**: The build script ran but didn't package files correctly.

**Solutions**:

1. **Check ZIP contents**:
   - Extract the ZIP file and verify files are inside
   - Check that `blender_usd_multiexport_addon/` folder structure is preserved

2. **Verify add-on folder**:
   - Check that `blender_usd_multiexport_addon/` contains Python files
   - Verify `__init__.py` and other module files exist

3. **Check exclude patterns**:
   - The build script excludes test files, docs, and cache files
   - This is normal - only production files should be in the ZIP

---

## Next Steps

After building successfully:

1. **Install Add-on**: See [`10_USER_GUIDE.md`](10_USER_GUIDE.md) for installation instructions
2. **Test Add-on**: Install in Blender 5.0+ and test functionality
3. **Report Issues**: If build fails, check error messages and verify prerequisites

---

**For user installation instructions, see [`10_USER_GUIDE.md`](10_USER_GUIDE.md).**  
**For usage instructions, see [`10_USER_GUIDE.md`](10_USER_GUIDE.md).**