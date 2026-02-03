from pxr import Usd, UsdGeom, Gf


def reset_default_prim_rotation_keep_children(stage_path: str, out_path: str):
    """Set default prim rotation to (0,0,0) while keeping children in place."""
    stage = Usd.Stage.Open(stage_path)
    if not stage:
        print(f"ERROR: Could not open: {stage_path}")
        return

    default_prim = stage.GetDefaultPrim()
    if not default_prim or not default_prim.IsValid():
        print("ERROR: No valid default prim")
        return

    default_path = default_prim.GetPath()
    children = [p for p in default_prim.GetChildren()]

    # Snapshot each child's world transform before changing parent
    cache = UsdGeom.XformCache()
    world_by_child = {}
    for child in children:
        world_by_child[child.GetPath()] = cache.GetLocalToWorldTransform(child)

    # Reset default prim rotation to identity (0,0,0)
    default_xform = UsdGeom.Xformable(default_prim)
    default_xform.ClearXformOpOrder()
    default_xform.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0))
    default_xform.AddRotateXYZOp().Set(Gf.Vec3f(0, 0, 0))
    default_xform.AddScaleOp().Set(Gf.Vec3f(1, 1, 1))
    print("Default prim set to 0° (identity)")

    # Recompute each child's local to preserve its world transform
    cache = UsdGeom.XformCache()  # reset cache after parent edit
    parent_world = cache.GetLocalToWorldTransform(default_prim)
    parent_world_inv = parent_world.GetInverse()

    for child in children:
        child_path = child.GetPath()
        world_xform = world_by_child.get(child_path)
        if world_xform is None:
            continue
        # USD composes transforms with parent * local (column-vector style).
        # Use parent^-1 * world to solve for local.
        new_local = parent_world_inv * world_xform
        _set_child_xform_trs(child, new_local)
        print(f"Preserved world for {child.GetName()}")

    stage.GetRootLayer().Export(out_path)
    print(f"Saved: {out_path}")


def _set_child_xform_trs(child_prim, local_matrix):
    """Write child local as TRS; fallback to transform matrix if decomposition fails."""
    xformable = UsdGeom.Xformable(child_prim)
    if not xformable:
        return
    # Decompose matrix to TRS
    trs = _decompose_matrix_to_trs(local_matrix)
    xformable.ClearXformOpOrder()
    if trs:
        t, r, s = trs
        xformable.AddTranslateOp().Set(t)
        xformable.AddRotateXYZOp().Set(r)
        xformable.AddScaleOp().Set(s)
    else:
        xformable.AddTransformOp().Set(local_matrix)


def _decompose_matrix_to_trs(world_matrix):
    """Decompose 4x4 to translate, rotateXYZ (degrees), scale for USD xform ops."""
    try:
        from pxr import UsdSkel
        t, quat, s = UsdSkel.DecomposeTransform(world_matrix)
        rot = Gf.Rotation(quat)
        euler = rot.Decompose(Gf.Vec3d(1, 0, 0), Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1))
        return (Gf.Vec3d(t[0], t[1], t[2]), Gf.Vec3f(euler[0], euler[1], euler[2]), Gf.Vec3f(s[0], s[1], s[2]))
    except Exception:
        return None


# ---- run ----
reset_default_prim_rotation_keep_children(
    r"D:\SPADEKAYAKS\070_RuD_Product development\Hard Goods\Boats\SP_W012_2025Shakti\010_ASS_USD\USD_Startpoint\SHAKTI_Decals.usda",
    r"D:\SPADEKAYAKS\070_RuD_Product development\Hard Goods\Boats\SP_W012_2025Shakti\010_ASS_USD\USD_Startpoint\SHAKTI_Decals_OUT.usda"
)