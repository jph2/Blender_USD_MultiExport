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

    v0.1.76: NORMALIZE/FLATTEN approach - bake rotation INTO children, identity on default prim.
    
    This ensures when the file is referenced, it already appears in Y-up orientation
    without needing any rotation on the reference.
    
    Steps:
    1. Build combined transform matrix (scale + rotation if y_is_up)
    2. Apply to all mesh points and normals
    3. Apply to all child translate xformOps
    4. Set default prim to IDENTITY transform
    5. Set stage metadata (metersPerUnit, upAxis)
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
        "xforms_updated": 0,
        "transform_normalized": False,
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

    # v0.1.76: Build combined bake matrix (rotation + scale)
    # This will be applied to ALL geometry and translate xformOps
    rotation_matrix = Gf.Matrix4d(1.0)
    if y_is_up:
        # -90° around X axis: Z-up → Y-up
        rotation = Gf.Rotation(Gf.Vec3d(1, 0, 0), -90.0)
        rotation_matrix.SetRotate(rotation)

    scale_matrix = Gf.Matrix4d(1.0)
    if scale_factor != 1.0:
        scale_matrix.SetScale(Gf.Vec3d(scale_factor, scale_factor, scale_factor))

    # Combined: first rotate, then scale
    bake_matrix = scale_matrix * rotation_matrix
    
    # For normals: rotation only (no scale), use inverse transpose
    normal_rotation_matrix = Gf.Matrix3d(
        rotation_matrix.GetRow(0)[0], rotation_matrix.GetRow(0)[1], rotation_matrix.GetRow(0)[2],
        rotation_matrix.GetRow(1)[0], rotation_matrix.GetRow(1)[1], rotation_matrix.GetRow(1)[2],
        rotation_matrix.GetRow(2)[0], rotation_matrix.GetRow(2)[1], rotation_matrix.GetRow(2)[2],
    )
    try:
        normal_matrix = normal_rotation_matrix.GetInverse().GetTranspose()
    except Exception:
        normal_matrix = normal_rotation_matrix

    # v0.1.76: Set default prim to IDENTITY transform (rotation is baked into children)
    default_prim = stage.GetDefaultPrim()
    if default_prim and default_prim.IsValid():
        xformable = UsdGeom.Xformable(default_prim)
        if xformable:
            # Clear existing and set identity
            xformable.ClearXformOpOrder()
            translate_op = xformable.AddTranslateOp()
            translate_op.Set(Gf.Vec3d(0, 0, 0))
            rotate_op = xformable.AddRotateXYZOp()
            rotate_op.Set(Gf.Vec3f(0, 0, 0))  # IDENTITY - rotation baked into children
            scale_op = xformable.AddScaleOp()
            scale_op.Set(Gf.Vec3f(1, 1, 1))
            result["transform_normalized"] = True

    xform_prims_processed = set()

    # v0.1.76: Apply bake_matrix to ALL mesh geometry
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Mesh):
            mesh = UsdGeom.Mesh(prim)
            
            # Transform points by combined matrix (rotation + scale)
            points_attr = mesh.GetPointsAttr()
            points = points_attr.Get()
            if points:
                baked_points = []
                for point in points:
                    # Transform point by bake_matrix
                    p = Gf.Vec3d(point[0], point[1], point[2])
                    p_transformed = bake_matrix.Transform(p)
                    baked_points.append(Gf.Vec3f(p_transformed[0], p_transformed[1], p_transformed[2]))
                points_attr.Set(baked_points)
                result["points_baked"] += len(baked_points)

            # Transform normals by rotation only (inverse transpose)
            normals_attr = mesh.GetNormalsAttr()
            normals = normals_attr.Get()
            if normals:
                baked_normals = []
                for normal in normals:
                    n = Gf.Vec3d(normal[0], normal[1], normal[2])
                    n_transformed = normal_matrix * n
                    n_final = Gf.Vec3f(n_transformed[0], n_transformed[1], n_transformed[2])
                    try:
                        n_final.Normalize()
                    except Exception:
                        pass
                    baked_normals.append(n_final)
                normals_attr.Set(baked_normals)
                result["normals_baked"] += len(baked_normals)

            result["meshes_processed"] += 1
        
        # v0.1.76: Transform translate xformOps on ALL prims (not just mesh ancestors)
        if prim not in xform_prims_processed:
            xformable = UsdGeom.Xformable(prim)
            if xformable and prim != default_prim:  # Don't modify default prim again
                _update_xform_ops(xformable, bake_matrix, Gf)
                xform_prims_processed.add(prim)
                result["xforms_updated"] += 1

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


def _update_xform_ops(xformable, bake_matrix, Gf) -> None:
    """Update xformOp translate values by applying the bake matrix.
    
    v0.1.76: Transform translate values by the full bake matrix (rotation + scale).
    This "normalizes" the transforms so geometry appears correct when referenced.
    """
    xform_ops = xformable.GetOrderedXformOps()
    
    for op in xform_ops:
        op_type = op.GetOpType()
        
        # Transform translate values by bake_matrix
        if op_type == op.TypeTranslate:
            translate = op.Get()
            if translate is not None:
                t = Gf.Vec3d(translate[0], translate[1], translate[2])
                t_transformed = bake_matrix.Transform(t)
                op.Set(Gf.Vec3d(t_transformed[0], t_transformed[1], t_transformed[2]))
        
        # For matrix transforms, transform the translation component
        elif op_type == op.TypeTransform:
            matrix = op.Get()
            if matrix is not None:
                trans = matrix.ExtractTranslation()
                t = Gf.Vec3d(trans[0], trans[1], trans[2])
                t_transformed = bake_matrix.Transform(t)
                new_matrix = Gf.Matrix4d(matrix)
                new_matrix.SetTranslateOnly(Gf.Vec3d(t_transformed[0], t_transformed[1], t_transformed[2]))
                op.Set(new_matrix)
        
        # Leave scale, rotation, orient unchanged - they work correctly
        # relative to the now-transformed geometry


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
