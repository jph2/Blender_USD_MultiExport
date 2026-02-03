from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional


def bake_usd_geometry(
    filepath: str,
    scale_factor: float,
    y_is_up: bool,
    meters_per_unit: float,
    logger=None,
    start_point_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Bake scale/rotation into USD mesh geometry and set stage metadata.

    This is a post-process step that:
    - Applies rotation (Z-up -> Y-up) and scale directly to mesh points
    - Rotates normals only (no scaling), then normalizes
    - Clears xformOps in the mesh ancestry to keep files clean
    - Sets metersPerUnit and upAxis to match baked geometry
    """
    context = start_point_context or {}
    result: Dict[str, Any] = {
        "success": False,
        "scale_factor": scale_factor,
        "y_is_up": y_is_up,
        "meters_per_unit": meters_per_unit,
        "meshes_processed": 0,
        "points_baked": 0,
        "normals_baked": 0,
        "xforms_cleared": 0,
    }

    try:
        from pxr import Usd, UsdGeom, Gf
    except ImportError:
        if logger:
            logger.log_warning(
                "USD Python API (pxr) not available. Bake step skipped.",
                context=context,
            )
        result["reason"] = "pxr_unavailable"
        return result

    stage = Usd.Stage.Open(filepath)
    if not stage:
        if logger:
            logger.log_warning(
                f"Could not open USD stage for baking: {filepath}",
                context=context,
            )
        result["reason"] = "stage_open_failed"
        return result

    # Build global bake matrices (Y-up + unit scale)
    rotation_matrix = Gf.Matrix4d(1.0)
    if y_is_up:
        rotation = Gf.Rotation(Gf.Vec3d(1.0, 0.0, 0.0), 90.0)
        rotation_matrix.SetRotate(rotation)

    scale_matrix = Gf.Matrix4d(1.0)
    if scale_factor != 1.0:
        scale_matrix.SetScale(
            Gf.Vec3d(scale_factor, scale_factor, scale_factor)
        )

    # Apply rotation first, then scale
    global_bake_matrix = scale_matrix * rotation_matrix

    baked_mesh_prims = []
    xform_prims_to_clear = set()
    xform_cache = UsdGeom.XformCache()

    for prim in stage.Traverse():
        if not prim.IsA(UsdGeom.Mesh):
            continue

        mesh = UsdGeom.Mesh(prim)
        local_to_world = xform_cache.GetLocalToWorldTransform(prim)
        bake_matrix = global_bake_matrix * local_to_world

        points_attr = mesh.GetPointsAttr()
        points = points_attr.Get()
        if points:
            baked_points = []
            for point in points:
                p4 = Gf.Vec4d(point[0], point[1], point[2], 1.0)
                p4_baked = bake_matrix * p4
                baked_points.append(
                    Gf.Vec3f(p4_baked[0], p4_baked[1], p4_baked[2])
                )
            points_attr.Set(baked_points)
            result["points_baked"] += len(baked_points)

        normals_attr = mesh.GetNormalsAttr()
        normals = normals_attr.Get()
        if normals:
            row0 = bake_matrix.GetRow(0)
            row1 = bake_matrix.GetRow(1)
            row2 = bake_matrix.GetRow(2)
            normal_matrix = Gf.Matrix3d(
                row0[0], row0[1], row0[2],
                row1[0], row1[1], row1[2],
                row2[0], row2[1], row2[2],
            )
            try:
                normal_matrix = normal_matrix.GetInverse().GetTranspose()
            except Exception:
                pass
            baked_normals = []
            for normal in normals:
                n3 = Gf.Vec3d(normal[0], normal[1], normal[2])
                n3 = normal_matrix * n3
                n3 = Gf.Vec3f(n3[0], n3[1], n3[2])
                try:
                    n3.Normalize()
                except Exception:
                    pass
                baked_normals.append(n3)
            normals_attr.Set(baked_normals)
            result["normals_baked"] += len(baked_normals)

        result["meshes_processed"] += 1
        baked_mesh_prims.append(prim)
        ancestor = prim
        while ancestor and not ancestor.IsPseudoRoot():
            xformable = UsdGeom.Xformable(ancestor)
            if xformable:
                xform_order_attr = xformable.GetXformOpOrderAttr()
                if xform_order_attr and xform_order_attr.HasAuthoredValueOpinion():
                    xform_prims_to_clear.add(ancestor)
            ancestor = ancestor.GetParent()

    for prim in xform_prims_to_clear:
        xformable = UsdGeom.Xformable(prim)
        xformable.ClearXformOpOrder()
        result["xforms_cleared"] += 1

    UsdGeom.SetStageMetersPerUnit(stage, meters_per_unit)
    UsdGeom.SetStageUpAxis(
        stage, UsdGeom.Tokens.y if y_is_up else UsdGeom.Tokens.z
    )

    try:
        stage.Save()
    except Exception as exc:
        result["reason"] = "stage_save_failed"
        result["exception"] = str(exc)
        if logger:
            logger.log_warning(
                "USD bake failed to save stage. File may be locked.",
                context={**context, "exception": str(exc), "filepath": filepath},
            )
        _cleanup_temp_usd_file(str(exc), logger, context)
        return result

    result["success"] = True
    return result


def _cleanup_temp_usd_file(message: str, logger, context: Dict[str, Any]) -> None:
    match = re.search(r"temporary file '([^']+)' to", message)
    if not match:
        return
    temp_path = match.group(1)
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            if logger:
                logger.log_info(
                    "Removed temporary USD file after save failure.",
                    context={**context, "temp_path": temp_path},
                )
    except Exception as exc:
        if logger:
            logger.log_warning(
                "Failed to remove temporary USD file.",
                context={
                    **context,
                    "temp_path": temp_path,
                    "exception": str(exc),
                },
            )
