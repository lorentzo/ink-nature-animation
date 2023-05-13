
# Blender 3.5.1.

import bpy
import mathutils
import bmesh

# Interpolate [a,b] using factor t.
def lerp(t, a, b):
    return (1.0 - t) * a + t * b

# https://blender.stackexchange.com/questions/220072/check-using-name-if-a-collection-exists-in-blend-is-linked-to-scene
def create_collection_if_not_exists(collection_name):
    if collection_name not in bpy.data.collections:
        new_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(new_collection) #Creates a new collection

def add_object_to_collection(base_object, collection_name="collection"):
    create_collection_if_not_exists(collection_name)
    bpy.data.collections[collection_name].objects.link(base_object)

def copy_obj(obj, collection_name):
    obj_cpy = obj.copy()
    obj_cpy.data = obj.data.copy()
    obj_cpy.animation_data_clear()
    if collection_name == None:
        bpy.context.collection.objects.link(obj_cpy)
    else:
        add_object_to_collection(obj_cpy, collection_name)
    return obj_cpy

def animate_curve_growth(curve, frame_start, frame_end, growth_factor_end, start_growth):
    curve.data.bevel_factor_end = 0
    curve.data.bevel_factor_start = start_growth
    curve.data.keyframe_insert(data_path="bevel_factor_end", frame=frame_start)
    curve.data.keyframe_insert(data_path="bevel_factor_start", frame=frame_start)
    curve.data.bevel_factor_start = growth_factor_end
    curve.data.keyframe_insert(data_path="bevel_factor_start", frame=frame_end)

def animate_curve_extrusion(curve, frame_start, frame_end, extrude_min, extrude_max, start_extrusion=0.0):
    curve.data.extrude = start_extrusion
    curve.data.keyframe_insert(data_path="extrude", frame=frame_start)
    curve.data.extrude = lerp(mathutils.noise.random(), extrude_min, extrude_max)
    curve.data.keyframe_insert(data_path="extrude", frame=frame_end)

# https://behreajj.medium.com/scripting-curves-in-blender-with-python-c487097efd13
def set_animation_fcurve(base_object, option='LINEAR'):
    fcurves = base_object.data.animation_data.action.fcurves
    for fcurve in fcurves:
        for kf in fcurve.keyframe_points:
            # Options: ['CONSTANT', 'LINEAR', 'BEZIER', 'SINE',
            # 'QUAD', 'CUBIC', 'QUART', 'QUINT', 'EXPO', 'CIRC',
            # 'BACK', 'BOUNCE', 'ELASTIC']
            kf.interpolation = option
            # Options: ['AUTO', 'EASE_IN', 'EASE_OUT', 'EASE_IN_OUT']
            kf.easing = 'AUTO'

def main():
    """
        Given collection of curve objects, this script for each curve,
        creates randomized instances and animates their growth.
    """
    # Apply on all objects in collection.
    n_copies_per_base_curve = 100
    translation_factor = 10
    scale_factor = 3
    frame_start = 0
    frame_end = 200
    curve_extrude_min_max = [0.01, 0.2]
    target_collection = "grass2_guides"
    dest_collection = "grass2_generated"
    start_extrusion = 0.01
    start_growth = 0.1
    for base_curve in bpy.data.collections[target_collection].all_objects:
        for i in range(n_copies_per_base_curve):
            # Create a copy.
            curve_cpy = copy_obj(base_curve, dest_collection)
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
            growth_factor_end = 1.0
            animate_curve_growth(curve_cpy, frame_start, frame_end, growth_factor_end, start_growth)
            # Animate curve extrusion.
            animate_curve_extrusion(curve_cpy, frame_start, frame_end, curve_extrude_min_max[0], curve_extrude_min_max[1], start_extrusion)
            # Interpolation.
            # Interpolation.
            set_animation_fcurve(curve_cpy)
#
# Script entry point.
#
if __name__ == "__main__":
    main()
