
# Blender 3.5.1.

import bpy
import mathutils
import bmesh

def select_activate_only(objects=[]):
    for obj in bpy.data.objects:
        obj.select_set(False)
    bpy.context.view_layer.objects.active = None 
    for obj in objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

def copy_obj(obj):
    obj_cpy = obj.copy()
    obj_cpy.data = obj.data.copy()
    obj_cpy.animation_data_clear()
    bpy.context.collection.objects.link(obj_cpy)
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

def convert_mesh_to_curve(mesh_obj, curve_bevel_depth=0.01, curve_n_subdiv=0):
    select_activate_only([mesh_obj])
    bpy.ops.object.convert(target='CURVE') # creates POLY by default
    curve = bpy.context.selected_objects[0]
    curve.data.bevel_depth = curve_bevel_depth
    bpy.ops.object.editmode_toggle()
    if curve_n_subdiv > 0:
        bpy.ops.curve.subdivide(number_cuts=curve_n_subdiv)
    bpy.ops.object.editmode_toggle()
    return curve

def create_edge_mesh_from_polygon(base_obj: bpy.types.Object, polygon: bpy.types.MeshPolygon):
    """
        Take mesh object and its polygon, create mesh containing only polygon edges.
        Polygon: https://docs.blender.org/api/current/bpy.types.MeshPolygon.html#bpy.types.MeshPolygon
    """
    # Fetch info on base object.
    base_obj_vertices = base_obj.data.vertices
    bm = bmesh.new()
    for poly_edge_key in polygon.edge_keys:
        bmv1 = bm.verts.new(base_obj_vertices[poly_edge_key[0]].co)
        bmv2 = bm.verts.new(base_obj_vertices[poly_edge_key[1]].co)
        bm.edges.new((bmv1, bmv2))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    mesh = bpy.data.meshes.new("mesh")
    obj_mesh = bpy.data.objects.new("obj", mesh)
    bpy.context.collection.objects.link(obj_mesh)
    bm.to_mesh(mesh)
    bm.free()
    return obj_mesh

def main():
    """
        Given collection of mesh objects, this script for each mesh,
        creates displaced splines around each mesh polygon.
    """
    # Apply on all objects in collection.
    for base_obj in bpy.data.collections['bobj'].all_objects:
        # For each base object face create spline.
        for polygon in base_obj.data.polygons:
            # For each polygon create mesh containing the same edges.
            polygon_edges_mesh_obj = create_edge_mesh_from_polygon(base_obj, polygon)
            # For each created polygon edges, create curve.
            for i in range(1):
                edges_cpy = copy_obj(polygon_edges_mesh_obj)
                # Convert created mesh to curve.
                curve = convert_mesh_to_curve(edges_cpy, curve_bevel_depth=0.01, curve_n_subdiv=10) # TODO: randomize
                # Pertub curve.
                perturb_curve(curve, perturb_scale=5.0, perturb_strength=0.2, n_octaves=1, amplitude_scale=0.3, frequency_scale=1.0)

#
# Script entry point.
#
if __name__ == "__main__":
    main()




    

    









