"""Create editable Blender scenes from the accepted print meshes.

Run with Blender 5.0 in background mode. Files go into generated/editable/.
The shelf is returned to its installed orientation; the organizer stays upright.
"""
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / 'generated' / 'editable'
OUT.mkdir(parents=True, exist_ok=True)

for name in ('shelf-v4', 'organizer'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .001
    scene.unit_settings.length_unit = 'MILLIMETERS'
    bpy.ops.wm.stl_import(filepath=str(PROJECT / 'models' / f'{name}.stl'),
                          use_scene_unit=False)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f'{name}-editable-mesh'
    if name == 'shelf-v4':
        for vert in obj.data.vertices:
            vert.co.y = -vert.co.y
            vert.co.z = 12 - vert.co.z
        focus = Vector((0, 40, -20))
        eye = Vector((310, 400, 260))
    else:
        focus = Vector((0, 0, 55))
        eye = Vector((220, -280, 240))
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(edge.is_manifold for edge in bm.edges)
    assert bm.calc_volume(signed=True) > 0
    bm.to_mesh(obj.data)
    bm.free()
    for face in obj.data.polygons:
        face.use_smooth = True
    mat = bpy.data.materials.new('Warm ivory')
    mat.diffuse_color = (.78, .73, .64, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = mat.diffuse_color
    shader.inputs['Roughness'].default_value = .38
    obj.data.materials.append(mat)
    obj['canonical_mesh'] = f'models/{name}.stl'
    obj['geometry_note'] = 'Editable copy of the accepted print mesh; units millimetres'
    scene.render.filepath = '//preview.png'
    scene['asset_scope'] = 'Accessory mesh and procedural material only'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                view = area.spaces.active
                view.clip_start = .1
                view.clip_end = 10000
                view.shading.color_type = 'MATERIAL'
                view.region_3d.view_location = focus
                view.region_3d.view_distance = 340
                view.region_3d.view_rotation = (focus-eye).to_track_quat('-Z', 'Y')
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f'{name}.blend'))
    print(f'Created {name}.blend: {len(obj.data.vertices)} editable vertices')
