
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

def perturb_curve(curve_obj, perturb_scale=1.0, perturb_strength=1.0, n_octaves=1, amplitude_scale=1.0, frequency_scale=1.0):
    curve_type = curve_obj.data.splines[0].type
    points = []
    if curve_type == "BEZIER":
        points = curve_obj.data.splines[0].bezier_points
    if curve_type == "POLY" or curve_type == "NURBS":
        points = curve_obj.data.splines[0].points
    for point in points:
        point_co = mathutils.Vector((point.co[0], point.co[1], point.co[2]))       
        trans_vec = mathutils.noise.turbulence_vector(
            point_co * perturb_scale * mathutils.noise.random(), 
            n_octaves,
            False, #hard
            noise_basis='PERLIN_ORIGINAL',
            amplitude_scale=amplitude_scale,
            frequency_scale=frequency_scale) * perturb_strength
        new_point_co = point_co + trans_vec
        if curve_type == "BEZIER":
            point.co = (new_point_co[0], new_point_co[1], new_point_co[2])
        if curve_type == "POLY" or curve_type == "NURBS":
            point.co = (new_point_co[0], new_point_co[1], new_point_co[2], point.co[3]) # Note: https://blender.stackexchange.com/questions/220812/what-is-the-4th-coordinate-of-spline-points
    return curve_obj

def animate_curve_growth(curve, frame_start, frame_end, growth_factor_end, start_growth):
    curve.data.bevel_factor_end = start_growth
    curve.data.bevel_factor_start = 0
    curve.data.keyframe_insert(data_path="bevel_factor_end", frame=frame_start)
    curve.data.keyframe_insert(data_path="bevel_factor_end", frame=frame_start)
    curve.data.bevel_factor_end = growth_factor_end
    curve.data.keyframe_insert(data_path="bevel_factor_end", frame=frame_end)

def animate_curve_thickness(curve, frame_start, frame_end, thickness_min, thickness_max, start_thickness=0.0):
    curve.data.bevel_depth = start_thickness
    curve.data.keyframe_insert(data_path="bevel_depth", frame=frame_start)
    curve.data.bevel_depth = lerp(mathutils.noise.random(), thickness_min, thickness_max)
    curve.data.keyframe_insert(data_path="bevel_depth", frame=frame_end)

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
    src_collection = "pillar_grow_curve_guide"
    dest_collection = "pillar_grow_curve_generated"
    start_thickness = 0.01
    start_growth = 0.1
    n_copies_per_base_curve = 10
    frame_start = 0
    frame_end = 200
    curve_thickness_min_max = [0.1, 0.2]
    start_thickness = 0.01
    for base_curve in bpy.data.collections[src_collection].all_objects:
        for i in range(n_copies_per_base_curve):
            # Create a copy.
            curve_cpy = copy_obj(base_curve, dest_collection)
            # Add bevel.
            curve_cpy.data.bevel_depth = mathutils.noise.random() * 0.2
            # Perturb.
            curve_cpy = perturb_curve(curve_cpy, perturb_scale=2.0, perturb_strength=3.0, n_octaves=1, amplitude_scale=2.0, frequency_scale=2.0)
            # Animate curve growth.
            growth_factor_end = 1.0
            animate_curve_growth(curve_cpy, frame_start, frame_end, growth_factor_end, start_growth)
            # Animate curve thickness.
            animate_curve_thickness(curve_cpy, frame_start, frame_end, curve_thickness_min_max[0], curve_thickness_min_max[1], start_thickness=start_thickness)

#
# Script entry point.
#
if __name__ == "__main__":
    main()
