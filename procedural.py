
import bpy
import mathutils
import bmesh

def deselect_all():
    for obj in bpy.data.objects:
        obj.select_set(False)
    bpy.context.view_layer.objects.active = None 

def select_activate_only(objects=[]):
    for obj in bpy.data.objects:
        obj.select_set(False)
    bpy.context.view_layer.objects.active = None 
    for obj in objects:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

def create_bezier_curve(n_cuts):
    deselect_all()
    bpy.ops.curve.primitive_bezier_curve_add(radius=1, enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    if n_cuts > 0:
        bpy.ops.curve.subdivide(number_cuts=n_cuts)
    bpy.ops.object.editmode_toggle()
    curve_obj = bpy.context.selected_objects[0]
    curve_obj.data.bevel_depth = 0.01
    return curve_obj

def create_nurbs_curve(n_cuts):
    deselect_all()
    bpy.ops.curve.primitive_nurbs_path_add(radius=1, enter_editmode=True, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    if n_cuts > 0:
        bpy.ops.curve.subdivide(number_cuts=n_cuts)
    bpy.ops.object.editmode_toggle()
    created_curve = bpy.context.selected_objects[0]
    created_curve.data.bevel_depth = 0.01
    return created_curve

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
            point_co * perturb_scale, 
            n_octaves,
            False, #hard
            noise_basis='PERLIN_ORIGINAL',
            amplitude_scale=amplitude_scale,
            frequency_scale=frequency_scale) * perturb_strength
        new_point_co = point_co + trans_vec
        if curve_type == "BEZIER":
            point.co = (new_point_co[0], new_point_co[1], new_point_co[2])
        if curve_type == "POLY" or curve_type == "NURBS":
            point.co = (new_point_co[0], new_point_co[1], new_point_co[2], point.co[3])
    return curve_obj


# Get cube on which splines will be created
base_obj = bpy.context.selected_objects[0]
base_obj_vertices = base_obj.data.vertices

# For each base_obj face create spline
for polygon in base_obj.data.polygons:
    # For each polygon create mesh containing edges.
    bm = bmesh.new()
    for poly_edge_key in polygon.edge_keys:
        bmv1 = bm.verts.new(base_obj_vertices[poly_edge_key[0]].co)
        bmv2 = bm.verts.new(base_obj_vertices[poly_edge_key[1]].co)
        bm.edges.new((bmv1, bmv2))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    mesh = bpy.data.meshes.new("mesh")
    obj = bpy.data.objects.new("obj", mesh)
    bpy.context.collection.objects.link(obj)
    bm.to_mesh(mesh)
    bm.free()
    # Convert created mesh to curve, subdivide, displace.
    #for i in range(int(mathutils.noise.random()*10)):
    select_activate_only([obj])
    bpy.ops.object.convert(target='CURVE')
    curve = bpy.context.selected_objects[0]
    curve.data.bevel_depth = 0.01
    bpy.ops.object.editmode_toggle()
    bpy.ops.curve.subdivide(number_cuts=10)
    bpy.ops.object.editmode_toggle()
    perturb_curve(curve, perturb_scale=mathutils.noise.random()*5.0, perturb_strength=0.2, n_octaves=1, amplitude_scale=0.3, frequency_scale=1.0)







    

    









