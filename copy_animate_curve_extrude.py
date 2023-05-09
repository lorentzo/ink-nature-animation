
# Blender 3.5.1.

import bpy
import mathutils
import bmesh

# Interpolate [a,b] using factor t.
def lerp(t, a, b):
    return (1.0 - t) * a + t * b

def copy_obj(obj):
    obj_cpy = obj.copy()
    obj_cpy.data = obj.data.copy()
    obj_cpy.animation_data_clear()
    bpy.context.collection.objects.link(obj_cpy) # TODO: link to user-specified collection
    return obj_cpy

def animate_curve_growth(curve, frame_start, frame_end, growth_factor_end):
    curve.data.bevel_factor_end = 0
    curve.data.bevel_factor_start = 0
    curve.data.keyframe_insert(data_path="bevel_factor_end", frame=frame_start)
    curve.data.keyframe_insert(data_path="bevel_factor_start", frame=frame_start)
    curve.data.bevel_factor_start = growth_factor_end
    curve.data.keyframe_insert(data_path="bevel_factor_start", frame=frame_end)

def animate_curve_extrusion(curve, frame_start, frame_end, bevel_min, bevel_max):
    curve.data.extrude = 0.0
    curve.data.keyframe_insert(data_path="extrude", frame=frame_start)
    curve.data.extrude = lerp(mathutils.noise.random(), bevel_min, bevel_max)
    curve.data.keyframe_insert(data_path="extrude", frame=frame_end)

def main():
    """
        Given collection of curve objects, this script for each curve,
        creates randomized instances and animates their growth.
    """
    # Apply on all objects in collection.
    n_copies_per_base_curve = 100
    translation_factor = 4
    scale_factor = 2
    frame_start = 0
    frame_end = 200
    curve_extrude_min_max = [0.01, 0.1]
    target_collection = "grass2_guides"
    for base_curve in bpy.data.collections[target_collection].all_objects:
        for i in range(n_copies_per_base_curve):
            # Create a copy.
            curve_cpy = copy_obj(base_curve)
            # Random rotation around Z axis.
            curve_cpy.rotation_euler[2] = mathutils.noise.random() * 360.0
            # Random translation in XY around base curve.
            # NOTE: base curve must not have translation applied!
            curve_cpy.location[0] = base_curve.location[0] + mathutils.noise.random() * translation_factor - translation_factor / 2
            curve_cpy.location[1] = base_curve.location[1] + mathutils.noise.random() * translation_factor - translation_factor / 2
            # Random scaling (XYZ).
            rand_scale = mathutils.noise.random() * scale_factor
            curve_cpy.scale[0] = rand_scale
            curve_cpy.scale[1] = rand_scale
            curve_cpy.scale[2] = rand_scale
            # Animate curve growth.
            animate_curve_growth(curve_cpy, frame_start, frame_end, 1.0)
            # Animate curve extrusion.
            animate_curve_extrusion(curve_cpy, frame_start, frame_end, curve_extrude_min_max[0], curve_extrude_min_max[1])
            
#
# Script entry point.
#
if __name__ == "__main__":
    main()
