# Troubleshooting Guide - Blender USD Multi Export

This guide covers troubleshooting for the Blender USD Multi Export add-on, including installation issues, debugging, and common problems.

**Version**: v0.1.3  
**Last Updated**: 03.02.2026 23:27

## Quick Checks

### 1. Check Blender Console for Errors

**How to view console:**
- **Windows**: 
  - **Option 1**: Blender's System Console (within Blender):
    - In Blender, go to **Window → Toggle System Console**
    - This opens a separate console window showing Python output
  - **Option 2**: Run Blender from Command Prompt (CMD):
    ```cmd
    # Navigate to Blender installation directory
    cd "C:\Program Files\Blender Foundation\Blender 5.0"
    # Run Blender (console output will appear in CMD window)
    blender.exe
    ```
  - **Option 3**: Run Blender from Windows Terminal/PowerShell:
    ```powershell
    # Navigate to Blender installation directory
    cd "C:\Program Files\Blender Foundation\Blender 5.0"
    # Run Blender (console output will appear in Terminal)
    .\blender.exe
    ```
- **macOS**: 
  - Run Blender from Terminal:
    ```bash
    # Run Blender from Applications
    /Applications/Blender.app/Contents/MacOS/Blender
    ```
- **Linux**: 
  - Run Blender from terminal:
    ```bash
    # If installed via package manager
    blender
    # Or if installed manually
    /path/to/blender/blender
    ```

**Look for:**
- `ERROR: Failed to register USD Multi Export addon: ...`
- `Starting USD Multi Export addon registration`
- `USD Multi Export addon registered successfully`
- Import errors
- Syntax errors
- Missing module errors

### 2. Verify Add-on is Installed

1. Go to **Edit → Preferences → Extensions**
2. In the search box, type: **"USD Multi"** or **"Multi Export"**
3. Check if the add-on appears in the list
4. If it appears but is **disabled**, click the checkbox to enable it

### 3. Check Installation Location

**Blender 5.0+ Extensions location:**
- **Windows**: `%APPDATA%\Blender Foundation\Blender\5.0\scripts\extensions\`
- **macOS**: `~/Library/Application Support/Blender/5.0/scripts/extensions/`
- **Linux**: `~/.config/blender/5.0/scripts/extensions/`

**Verify the folder exists:**
```
extensions/
└── blender_usd_multiexport/
    ├── __init__.py
    ├── logging_utils.py
    └── ...
```

### 4. Verify Zip Structure

The zip file should have this structure:
```
blender_usd_multiexport.zip
└── blender_usd_multiexport/
    ├── __init__.py          ← MUST EXIST
    ├── logging_utils.py
    ├── props.py
    ├── ui.py
    ├── ops_export.py
    └── ...
```

**Common Issue**: If the zip contains files directly (not in a folder), Blender won't recognize it.

### 5. Check Blender Version

The add-on requires **Blender 5.0 or later**.

**Check your version:**
- Help → About Blender
- Or in Python console: `bpy.app.version`

If you're using Blender 4.x, the add-on won't work. Upgrade to Blender 5.0+.

### 6. Manual Installation Test

If zip installation doesn't work, try manual installation:

1. Extract the zip file
2. Copy the `blender_usd_multiexport` folder to:
   - **Windows**: `%APPDATA%\Blender Foundation\Blender\5.0\scripts\addons\`
   - **macOS**: `~/Library/Application Support/Blender/5.0/scripts/addons/`
   - **Linux**: `~/.config/blender/5.0/scripts/addons/`
3. Restart Blender
4. Go to **Edit → Preferences → Extensions**
5. Search for "USD Multi Export"
6. Enable the add-on

## Common Issues & Solutions

### Issue: Updating the Add-on (Uninstall & Reinstall)

**When updating to a new version:**

1. **Uninstall the old version**:
   - Go to **Edit → Preferences → Extensions**
   - Find "USD Multi Export" in the list
   - Click **"Uninstall"** button
2. **Restart Blender** (important - ensures old code is cleared from memory)
3. **Install the new zip file**:
   - Go to **Edit → Preferences → Extensions**
   - Click dropdown (top right) → **Install from Disk**
   - Select the new `dist/blender_usd_multiexport.zip` file
4. **Restart Blender again** (to load the new version)

> **Important**: Restarting Blender after uninstalling and reinstalling is **required**. Blender caches Python modules in memory, and a restart ensures the old code is fully cleared and the new version loads correctly. If you experience issues after updating, always restart Blender.

### Issue: Add-on doesn't appear in list

**Quick Fix:**
1. Go to **Edit → Preferences → Extensions**
2. **Search for "USD Multi"** in the search box (top of Extensions panel)
3. **Find "USD Multi Export"** in the results
4. **Click the checkbox** to enable it (if unchecked)

**If it still doesn't appear:**

**Possible causes:**
1. **Missing `__init__.py`** - The zip doesn't contain `__init__.py`
2. **Wrong zip structure** - Files are at root level instead of in a folder
3. **Import error** - `__init__.py` has errors preventing registration
4. **Blender version mismatch** - Using Blender 4.x instead of 5.0+

**Solution:**
- Check console for errors (see "Check Blender Console for Errors" above)
- Verify zip structure (see "Verify Zip Structure" above)
- Check Blender version (see "Check Blender Version" above)
- Try manual installation (see "Manual Installation Test" above)

### Issue: Panel doesn't appear in Scene Properties

**Check:**
1. **Is the add-on enabled?**
   - Go to **Edit → Preferences → Extensions**
   - Search for "USD Multi Export"
   - Verify checkbox is checked

2. **Check Scene Properties panel:**
   - Open **Scene Properties** (right sidebar, cone icon)
   - Look for **"USD Multi Export"** panel
   - If not visible, try collapsing/expanding other panels

3. **Check console for errors:**
   - Open Blender console (Window → Toggle System Console)
   - Look for registration errors or import errors

### Issue: Export fails or produces errors

**Debugging steps:**

1. **Check console output:**
   - Open Blender console (Window → Toggle System Console)
   - Look for error messages during export
   - Check for Python tracebacks

2. **Check log file:**
   - Log files are stored in: `{Blender Temp Directory}/blender_usd_logs/blender_usd_multiexport.log`
   - On Windows: `%TEMP%\blender_usd_logs\blender_usd_multiexport.log`
   - On macOS: `~/Library/Application Support/Blender/5.0/temp/blender_usd_logs/blender_usd_multiexport.log`
   - On Linux: `~/.config/blender/5.0/temp/blender_usd_logs/blender_usd_multiexport.log`

3. **Enable verbose logging:**
   - Go to **Edit → Preferences → Extensions**
   - Find "USD Multi Export" → Click **Preferences**
   - Set **Console Log Level** to **DEBUG**
   - Try export again and check console

4. **Check endpoint configuration:**
   - Verify endpoint paths are valid
   - Check that target collections/objects exist
   - Verify export directory is writable

5. **Generate bug report:**
   - In the USD Multi Export panel, click **"Generate Bug Report"**
   - This creates a JSON file with system info and recent logs
   - Share this file when reporting issues

### Issue: Log level preference doesn't work

**If changing log level in preferences doesn't affect console output:**

1. **Check that preference is saved:**
   - Make sure you click outside the preference panel after changing
   - Blender should auto-save preferences

2. **Restart Blender:**
   - Some preference changes require a restart
   - Close and reopen Blender

3. **Check console for log level messages:**
   - With DEBUG level, you should see: `Console log level set to: DEBUG`
   - If you don't see this, the preference update may not be working

4. **Verify preference is connected:**
   - Check console for: `Applied log level preference: {level}`
   - This should appear during addon registration

### Issue: File paths not resolving correctly

**Common path issues:**

1. **Relative paths not working:**
   - Ensure blend file is saved (relative paths need a saved file)
   - Check that `//` prefix is used for Blender-relative paths
   - Verify path exists relative to blend file location

2. **Absolute paths not working:**
   - Check path doesn't contain invalid characters
   - Verify directory exists and is writable
   - On Windows, check for long path issues (>260 characters)

3. **Export directory not created:**
   - Check parent directory permissions
   - Verify disk space is available
   - Check console for permission errors

### Issue: Scene state issues after export

**If objects or collections are missing or modified after export:**

1. **This should not happen** - the addon uses scene state isolation
2. **If it does occur:**
   - Check console for state restoration errors
   - Verify `state_manager.py` is working correctly
   - Report as a bug with bug report file

3. **Workaround:**
   - Save your blend file before exporting
   - Use Blender's undo (Ctrl+Z) if something goes wrong

## Debugging Procedures

### Enable Debug Logging

1. **Via Preferences:**
   - Edit → Preferences → Extensions
   - Find "USD Multi Export" → Preferences
   - Set Console Log Level to **DEBUG**

2. **Check log file:**
   - Log file location: `{Blender Temp}/blender_usd_logs/blender_usd_multiexport.log`
   - Open in text editor to see detailed logs

### Generate Bug Report

1. **Via UI:**
   - Open Scene Properties → USD Multi Export panel
   - Click **"Generate Bug Report"** button
   - File will be saved to Blender temp directory

2. **Via Python Console:**
   ```python
   from blender_usd_multiexport import logging_utils
   logging_utils.log_bug_report()
   ```

### Check Registration Status

**In Python Console:**
```python
# Check if addon is registered
import bpy
addon_name = "blender_usd_multiexport"
if addon_name in bpy.context.preferences.addons:
    print("Addon is registered and enabled")
    prefs = bpy.context.preferences.addons[addon_name].preferences
    print(f"Log level: {prefs.log_level}")
else:
    print("Addon is not registered or not enabled")
```

### Verify Module Imports

**In Python Console:**
```python
# Test imports
try:
    from blender_usd_multiexport import logging_utils
    from blender_usd_multiexport import props
    from blender_usd_multiexport import ui
    from blender_usd_multiexport import ops_export
    print("All modules imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
```

## Performance Issues

### Export is slow

1. **Check scene complexity:**
   - Large scenes with many objects take longer
   - Complex geometry increases export time

2. **Enable performance timers:**
   - Set log level to DEBUG
   - Check log file for timer information
   - Look for operations taking excessive time

3. **Optimize endpoints:**
   - Export fewer endpoints at once
   - Use smaller collections for endpoints

### Memory issues

1. **Check available RAM:**
   - Large scenes require significant memory
   - Close other applications if needed

2. **Reduce scene complexity:**
   - Export endpoints separately
   - Use simpler geometry for testing

## Getting Help

### Before Reporting Issues

1. **Check this troubleshooting guide** - Many issues are covered here
2. **Check console output** - Look for error messages
3. **Generate bug report** - Use the bug report feature in the UI
4. **Check Blender version** - Must be 5.0 or later
5. **Try clean installation** - Uninstall and reinstall the addon

### Reporting Issues

When reporting issues, include:

1. **Blender version** - Help → About Blender
2. **Addon version** - Check `__init__.py` or README
3. **Console output** - Copy error messages from console
4. **Bug report file** - Generated via UI or Python console
5. **Steps to reproduce** - What you did before the issue occurred
6. **Expected behavior** - What should have happened
7. **Actual behavior** - What actually happened

### Log File Location

Log files are stored in:
- **Windows**: `%TEMP%\blender_usd_logs\blender_usd_multiexport.log`
- **macOS**: `~/Library/Application Support/Blender/5.0/temp/blender_usd_logs/blender_usd_multiexport.log`
- **Linux**: `~/.config/blender/5.0/temp/blender_usd_logs/blender_usd_multiexport.log`

You can also find the temp directory in Blender:
- Python Console: `bpy.app.tempdir`
- Or check: Edit → Preferences → System → Temporary Files

---

**For more information, see:**
- `README.md` - User guide and installation instructions
- `HANDOFF.md` - Technical details and implementation notes
- `docs/archive/LEARNINGS_FROM_FAKE_REFERENCES.md` - Cross-project learnings and improvements (Archived - learnings implemented)


