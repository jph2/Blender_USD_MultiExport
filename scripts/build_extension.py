#!/usr/bin/env python3
"""
Build script for Blender USD Multi Export Extension/Add-on

Creates a .zip file ready for installation in Blender 5.0+ via:
Edit → Preferences → Extensions → Install from Disk

Usage:
    python build_extension.py
"""

import zipfile
import re
from pathlib import Path

# Configuration
# Script is in scripts/ subdirectory, so go up one level to repo root
REPO_ROOT = Path(__file__).parent.parent
ADDON_DIR = REPO_ROOT / "blender_usd_multiexport_addon"
OUTPUT_DIR = REPO_ROOT / "releases"

def get_version():
    """Extract version from __init__.py."""
    init_file = ADDON_DIR / "__init__.py"
    if not init_file.exists():
        return None
    
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Look for version tuple like (0, 1, 9)
        match = re.search(r'"version":\s*\((\d+),\s*(\d+),\s*(\d+)\)', content)
        if match:
            return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
    return None

# Files/directories to exclude from the zip
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".git",
    ".gitignore",
    "*.md",
    "test_assets",
    "docs",
    "dist",
    "*.zip",
    "tests",  # Exclude test files from distribution
]

def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from the zip."""
    path_str = str(path)
    
    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str or path.name.startswith('.'):
            return True
    
    # Exclude test files
    if 'test' in path_str.lower() and path.suffix == '.py':
        return True
    
    return False

def build_extension_zip():
    """Build the extension zip file."""
    print("Building Blender USD Multi Export Extension...")
    print(f"Source: {ADDON_DIR}")
    
    # Verify addon directory exists
    if not ADDON_DIR.exists():
        print(f"ERROR: Addon directory not found: {ADDON_DIR}")
        return False
    
    # Verify __init__.py exists and get version
    init_file = ADDON_DIR / "__init__.py"
    if not init_file.exists():
        print(f"ERROR: __init__.py not found in {ADDON_DIR}")
        return False
    
    # Get version from __init__.py
    version = get_version()
    if not version:
        print("WARNING: Could not extract version from __init__.py, using 'unknown'")
        version = "unknown"
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Create versioned zip filename
    zip_name = f"blender_usd_multiexport_v{version}.zip"
    zip_path = OUTPUT_DIR / zip_name
    print(f"Output: {zip_path}")
    
    # Handle existing zip file
    if zip_path.exists():
        print(f"Existing zip found: {zip_path}")
        try:
            zip_path.unlink()
            print("Removed existing zip")
        except PermissionError:
            print(f"WARNING: Could not remove existing zip (file may be locked)")
            return False
    
    # Create zip file
    print("\nPackaging files...")
    files_added = 0
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from addon directory
        # ZIP root should be "blender_usd_multiexport_addon/" to match the module name
        for file_path in ADDON_DIR.rglob('*'):
            if file_path.is_file() and not should_exclude(file_path):
                # Get relative path for zip - preserve the directory name
                arcname = file_path.relative_to(ADDON_DIR.parent)
                zipf.write(file_path, arcname)
                files_added += 1
                print(f"  Added: {arcname}")
    
    # Get zip file size
    zip_size = zip_path.stat().st_size
    zip_size_mb = zip_size / (1024 * 1024)
    
    print(f"\n[SUCCESS] Extension built successfully!")
    print(f"   File: {zip_path}")
    print(f"   Size: {zip_size_mb:.2f} MB ({zip_size:,} bytes)")
    print(f"   Files: {files_added}")
    print(f"\n[INSTALL] Installation:")
    print(f"   1. Open Blender 5.0+")
    print(f"   2. Edit > Preferences > Extensions")
    print(f"   3. Click dropdown (top right) > Install from Disk")
    print(f"   4. Select: {zip_path}")
    print(f"   5. Extension will be installed and available")
    
    return True

if __name__ == "__main__":
    success = build_extension_zip()
    exit(0 if success else 1)

