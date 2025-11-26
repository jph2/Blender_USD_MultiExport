# GitHub Repository Rename Guide

**Date**: 25.11.2025  
**Status**: Decision Guide

---

## Question: Should We Rename the GitHub Repository?

**Current Name**: `Blender_USD_StableExport`  
**Proposed Name**: `Blender_USD_MultiExport`

---

## GitHub's Automatic Redirect Feature

**Good News**: GitHub automatically redirects repository URLs when you rename a repository. This means:

✅ **What Still Works**:
- Old repository URLs (`https://github.com/jph2/Blender_USD_StableExport`) → Automatically redirect to new name
- Old links in documentation, issues, pull requests → Still work
- Old bookmarks → Still work
- Old references in other repositories → Still work

⚠️ **What Needs Updates**:
- Git clone URLs (users need to update their remotes)
- CI/CD configurations (if any)
- External integrations
- Local git remotes on developer machines

---

## Recommendation: **Rename Now** (Early Stage)

### Why Rename Now:

1. **Early Stage**: Project is still in planning/requirements phase
   - Fewer people have cloned/forked it
   - Less disruption
   - Cleaner history

2. **Consistency**: Repository name matches project name
   - Better discoverability
   - Clearer branding
   - Professional appearance

3. **GitHub Redirects**: Old links will still work
   - No broken links
   - Smooth transition
   - Users can update at their own pace

4. **Better Name**: "MultiExport" is clearer than "StableExport"
   - Avoids confusion about Blender's export stability
   - Better describes functionality

### Why Wait:

1. **If Many People Have Cloned**: More disruption
2. **If External Integrations**: Need coordination
3. **If Already Published**: More users affected

**Current Status**: ✅ **Perfect Time to Rename** - Project is early stage, minimal disruption

---

## How to Rename GitHub Repository

### Step 1: Rename on GitHub

1. Go to repository: `https://github.com/jph2/Blender_USD_StableExport`
2. Click **Settings** (top right)
3. Scroll down to **Repository name** section
4. Change name to: `Blender_USD_MultiExport`
5. Click **Rename**

**GitHub will automatically**:
- Redirect old URLs to new name
- Update repository URL
- Keep all issues, PRs, and history

### Step 2: Update Local Repository

After renaming on GitHub, update your local repository:

```bash
# Check current remote
git remote -v

# Update remote URL
git remote set-url origin https://github.com/jph2/Blender_USD_MultiExport.git

# Verify
git remote -v
```

### Step 3: Update All References

After renaming, update references in:

1. **README.md**: All GitHub links
2. **Documentation**: Any repository references
3. **Issue Templates**: Repository URLs
4. **CONTRIBUTING.md**: Repository links
5. **Any External Documentation**: Blog posts, tutorials, etc.

---

## What Happens to Old Links?

### Automatic Redirects (Still Work):

✅ `https://github.com/jph2/Blender_USD_StableExport` → Redirects to new name  
✅ `https://github.com/jph2/Blender_USD_StableExport/issues` → Still works  
✅ `https://github.com/jph2/Blender_USD_StableExport/pulls` → Still works  
✅ `https://github.com/jph2/Blender_USD_StableExport/releases` → Still works  

### What Needs Manual Updates:

⚠️ Git clone URLs (users need to update):
- Old: `git clone https://github.com/jph2/Blender_USD_StableExport.git`
- New: `git clone https://github.com/jph2/Blender_USD_MultiExport.git`

⚠️ Local git remotes (developers need to update):
```bash
git remote set-url origin https://github.com/jph2/Blender_USD_MultiExport.git
```

---

## Best Practice: Add a Note in README

After renaming, add a note in README for users who might have old links:

```markdown
> **Note**: This repository was renamed from `Blender_USD_StableExport` to `Blender_USD_MultiExport`. 
> Old links still work thanks to GitHub's automatic redirects, but if you're cloning the repository, 
> use the new name: `git clone https://github.com/jph2/Blender_USD_MultiExport.git`
```

---

## Decision Matrix

| Factor | Rename Now | Keep Old Name |
|--------|-----------|---------------|
| **Project Stage** | ✅ Early (perfect time) | ❌ Later (more disruption) |
| **Link Breaking** | ✅ GitHub redirects (no break) | N/A |
| **Consistency** | ✅ Matches project name | ❌ Confusing |
| **User Impact** | ✅ Minimal (early stage) | N/A |
| **Professional** | ✅ Better branding | ❌ Less clear |

**Recommendation**: ✅ **Rename Now** - Early stage, GitHub handles redirects, better consistency

---

## Action Plan

If you decide to rename:

1. ✅ **Rename Repository on GitHub** (Settings → Repository name)
2. ✅ **Update Local Remote** (`git remote set-url`)
3. ✅ **Update All Documentation** (README, docs, templates)
4. ✅ **Add Note in README** (for users with old links)
5. ✅ **Test Old Links** (verify redirects work)
6. ✅ **Commit & Push** (all documentation updates)

---

## Alternative: Keep Repository Name, Update Display Name

If you prefer not to rename the repository:

- Keep repository URL: `Blender_USD_StableExport`
- Update display name in README: "Blender USD Multi Export"
- Add explanation about naming

**Pros**: No git remote updates needed  
**Cons**: Confusing URL vs. display name, less professional

---

**Status**: Awaiting decision  
**Last Updated**: 25.11.2025

