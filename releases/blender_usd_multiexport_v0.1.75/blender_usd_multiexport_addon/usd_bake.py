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

    v0.1.70: Fixed to preserve spatial positions for collections.
    
    This is a post-process step that:
    - Applies rotation (Z-up -> Y-up) and scale directly to mesh points (LOCAL coords only)
    - Rotates normals only (no scaling), then normalizes
    - Updates xformOp values (scale translate, rotate orientation) instead of clearing them
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
        "xforms_updated": 0,
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

    # v0.1.75: Add -90° X rotation to DEFAULT PRIM for Z-up → Y-up conversion
    # This is the key fix! The rotation must be on the root/default prim,
    # not baked into geometry or applied to child xformOps.
    default_prim = stage.GetDefaultPrim()
    if default_prim and default_prim.IsValid() and y_is_up:
        xformable = UsdGeom.Xformable(default_prim)
        if xformable:
            # Clear any existing xformOps and add our own
            xformable.ClearXformOpOrder()
            
            # Add translate, rotate, scale ops in standard order
            translate_op = xformable.AddTranslateOp()
            translate_op.Set(Gf.Vec3d(0, 0, 0))
            
            rotate_op = xformable.AddRotateXYZOp()
            rotate_op.Set(Gf.Vec3f(-90, 0, 0))  # Z-up → Y-up conversion
            
            scale_op = xformable.AddScaleOp()
            scale_op.Set(Gf.Vec3f(1, 1, 1))
            
            result["default_prim_rotation_added"] = True

    # v0.1.75: Only scale geometry for unit conversion (meters → centimeters)
    # NO rotation here - the default prim rotation handles coordinate conversion
    local_bake_matrix = Gf.Matrix4d(1.0)
    if scale_factor != 1.0:
        local_bake_matrix.SetScale(Gf.Vec3d(scale_factor, scale_factor, scale_factor))

    xform_prims_processed = set()

    for prim in stage.Traverse():
        if not prim.IsA(UsdGeom.Mesh):
            continue

        mesh = UsdGeom.Mesh(prim)
        
        # v0.1.70: Only bake rotation into LOCAL points (not world transform)
        # The scale will be applied to xformOps to preserve positions
        points_attr = mesh.GetPointsAttr()
        points = points_attr.Get()
        if points:
            baked_points = []
            for point in points:
                p4 = Gf.Vec4d(point[0], point[1], point[2], 1.0)
                p4_baked = local_bake_matrix * p4
                baked_points.append(
                    Gf.Vec3f(p4_baked[0], p4_baked[1], p4_baked[2])
                )
            points_attr.Set(baked_points)
            result["points_baked"] += len(baked_points)

        normals_attr = mesh.GetNormalsAttr()
        normals = normals_attr.Get()
        if normals:
            row0 = local_bake_matrix.GetRow(0)
            row1 = local_bake_matrix.GetRow(1)
            row2 = local_bake_matrix.GetRow(2)
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
        
        # v0.1.70: Update xformOps on ancestors instead of clearing them
        ancestor = prim
        while ancestor and not ancestor.IsPseudoRoot():
            if ancestor not in xform_prims_processed:
                xformable = UsdGeom.Xformable(ancestor)
                if xformable:
                    _update_xform_ops(xformable, scale_factor, y_is_up, Gf)
                    xform_prims_processed.add(ancestor)
                    result["xforms_updated"] += 1
            ancestor = ancestor.GetParent()

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


def _update_xform_ops(xformable, scale_factor: float, y_is_up: bool, Gf) -> None:
    """Update xformOp values for unit scaling ONLY.
    
    v0.1.74: ULTRA-SIMPLIFIED - NO coordinate conversion!
    
    Let Blender's exporter and USD upAxis metadata handle coordinate conversion.
    We ONLY multiply translate values by scale_factor for unit conversion (m→cm).
    Everything else passes through completely unchanged.
    """
    if scale_factor == 1.0:
        return  # Nothing to do
    
    xform_ops = xformable.GetOrderedXformOps()
    
    for op in xform_ops:
        op_type = op.GetOpType()
        
        # Only scale translate values (for unit conversion)
        if op_type == op.TypeTranslate:
            translate = op.Get()
            if translate is not None:
                x, y, z = translate[0], translate[1], translate[2]
                # Just scale - NO coordinate swapping!
                op.Set(Gf.Vec3d(x * scale_factor, y * scale_factor, z * scale_factor))
        
        # For matrix transforms, only scale the translation part
        elif op_type == op.TypeTransform:
            matrix = op.Get()
            if matrix is not None:
                trans = matrix.ExtractTranslation()
                x, y, z = trans[0], trans[1], trans[2]
                new_matrix = Gf.Matrix4d(matrix)
                new_matrix.SetTranslateOnly(Gf.Vec3d(x * scale_factor, y * scale_factor, z * scale_factor))
                op.Set(new_matrix)
        
        # Leave scale, rotation, orient COMPLETELY unchanged


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
