# Naming Conventions for Blender USD Stable Export

**Version**: v0.1.3  
**Last Updated**: 03.02.2026 23:27  
**Purpose**: This document defines naming conventions and best practices for collection and endpoint names to avoid conflicts with USD/Omniverse reserved names and ensure smooth integration.
**Tag block:**
#blender #framework_integration #best_practices #gaming #export #conversion #collections #omniverse #aas_integration #prim #openusd #usd_core #hybrid #semantic_governance #references #analysis #workflow_automation #deterministic_workflows

**Last Updated**: 25.11.2025

---

## ⚠️ Reserved Names to Avoid

### Omniverse-Specific Reserved Names

#### `/environment` (Root Level)
- **What it is**: A reserved root-level prim in Omniverse for scene-specific lighting setup
- **Structure**: `/World` (default prim) and `/environment` are siblings at the root level:
  ```
  / (root)
  ├── /World (default prim)
  │   ├── /World/characters
  │   ├── /World/props
  │   └── ...
  └── /environment (reserved for lighting, sibling to World)
  ```
- **Why avoid**: 
  - Using "Environment" as a collection name creates confusion and potential conflicts
  - `/environment` at root level is reserved for Omniverse's lighting system
  - When a USD file is referenced, only content under the default prim (`/World`) is imported
  - `/environment` at root level is NOT imported when referencing, which is intentional for Omniverse
- **Impact**: 
  - Collections named "Environment" may conflict with Omniverse's reserved `/environment` prim
  - If exported as `/World/environment`, it becomes part of the default prim (imported on reference)
  - If exported as `/environment`, it conflicts with Omniverse's reserved location
- **Alternative**: Use "Props", "Set", "Location", "SceneElements", or descriptive names

#### `/World` (Default Prim)
- **What it is**: The default prim in USD/Omniverse scenes
- **Structure**: `/World` is the default prim, and all referenced content should be under it
- **Why avoid**: Using "World" as a collection name conflicts with USD's default prim concept
- **Impact**: May cause confusion about what is the default prim vs. a collection
- **Important**: When exporting endpoints, they should be under `/World` (or the configured default prim) to be imported when the file is referenced
- **Alternative**: Use "Scene", "Root", "Main", or avoid entirely

---

## ✅ Recommended Naming Patterns

### Generic Collection Names

For collections that don't have specific content types:

- **Props** - General scene objects and decorations
- **Set** - Film/TV industry term for scene elements
- **Location** - Geographic or spatial elements
- **SceneElements** - Generic scene components
- **Assets** - Generic asset collection
- **Geometry** - Pure geometry without specific purpose

### Content-Specific Names

Use descriptive names based on content:

- **Characters** - Character models and rigs
- **Vehicles** - Vehicle models
- **Buildings** - Architectural elements
- **Vegetation** - Plants, trees, foliage
- **Furniture** - Furniture and interior elements
- **Lighting** - Light fixtures (not scene lighting setup)
- **Cameras** - Camera objects
- **Effects** - Visual effects elements

### Industry-Specific Patterns

- **Film/TV**: Use "Set", "Props", "Background", "Foreground"
- **Games**: Use "Level", "Assets", "Characters", "Weapons"
- **Architecture**: Use "Building", "Interior", "Exterior", "Landscape"
- **Automotive**: Use "Vehicles", "Environment" (if not importing to Omniverse), "Roads"

---

## 📋 Naming Best Practices

### 1. Be Descriptive
✅ **Good**: "CityBuildings", "CharacterRigs", "VehicleFleet"  
❌ **Bad**: "Collection1", "Stuff", "Things"

### 2. Use Consistent Conventions
- Choose a naming style and stick with it:
  - **PascalCase**: `CharacterModels`, `VehicleAssets`
  - **snake_case**: `character_models`, `vehicle_assets`
  - **kebab-case**: `character-models`, `vehicle-assets`

### 3. Avoid Reserved Terms
- ❌ "Environment" (conflicts with `/World/environment`)
- ❌ "World" (conflicts with default prim)
- ❌ "Root" (may conflict with root prim concepts)
- ✅ Use alternatives listed above

### 4. Consider USD Prim Paths
- Collection names may become prim paths in USD
- Ensure names are valid USD identifiers
- Avoid special characters that aren't valid in USD paths

### 5. Document Your Conventions
- If working in a team, document your naming conventions
- Create a style guide for your project
- Use consistent naming across all endpoints

---

## 🔍 USD/Omniverse Integration Considerations

### Default Prim (`/World`)
- USD files typically have a default prim (often `/World`)
- Your exported endpoints should be under this default prim to be imported when the file is referenced
- Collection names become prim names in the USD hierarchy under the default prim
- **Critical**: Only content under the default prim is imported when a USD file is referenced
- `/environment` at root level (sibling to `/World`) is NOT imported on reference - this is intentional for Omniverse's lighting system

### Omniverse Scene Structure
```
/ (root)
├── /World (default prim)
│   ├── /World/characters
│   ├── /World/props
│   ├── /World/vehicles
│   └── ... (all content under default prim)
└── /environment (reserved for lighting, sibling to World, NOT imported on reference)
```

**Important Notes:**
- `/World` is the default prim - content under it is imported when the file is referenced
- `/environment` is a sibling to `/World` at root level - it's NOT imported when referencing (by design)
- All exported endpoints should be under `/World` (or the configured default prim) to ensure they're imported on reference

### Best Practice
- Export collections with names that make sense in this hierarchy
- Avoid names that conflict with Omniverse's reserved locations
- Use descriptive names that indicate content type

---

## 📝 Examples

### ✅ Good Examples

**Scene Organization:**
```
Collections:
├── Characters
│   ├── Hero
│   └── NPCs
├── Props
│   ├── Furniture
│   └── Decorations
├── Vehicles
└── SetElements
```

**Exported USD Files:**
- `characters.usd` → `/World/characters`
- `props.usd` → `/World/props`
- `vehicles.usd` → `/World/vehicles`
- `set_elements.usd` → `/World/set_elements`

### ❌ Bad Examples

**Avoid These:**
```
Collections:
├── Environment  ❌ (conflicts with /World/environment)
├── World        ❌ (conflicts with default prim)
├── Root         ❌ (may cause confusion)
└── Collection1  ❌ (not descriptive)
```

---

## 🎯 Quick Reference

| Avoid | Use Instead | Reason |
|-------|-------------|--------|
| Environment | Props, Set, Location | Conflicts with `/World/environment` |
| World | Scene, Main, Root | Conflicts with default prim |
| Root | Main, Base, Primary | May cause confusion |
| Generic names | Descriptive names | Better organization |

---

## 📚 Related Documentation

- [Blender USD Stable Export Research](Blender_USD_StableExport_RESEARCH.md)
- [USD Composition Best Practices](https://openusd.org/release/api/usd_page_front.html)
- [Omniverse Documentation](https://docs.omniverse.nvidia.com/)

---

**Last Updated**: 25.11.2025
