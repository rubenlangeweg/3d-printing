"""Build the PAHT-CF fit revision from the accepted, unchanged source.
Run with Blender --background --python source/build_paht_fit.py.
"""
from pathlib import Path
import bpy, bmesh, json, hashlib, argparse, sys
from mathutils import Vector

PROJECT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--revision', type=int, choices=[1, 2, 3], default=3)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
REVISION = args.revision
SUFFIX = '' if REVISION == 1 else f'-v{REVISION}'
SIDE_RELIEF = {1: 0.20, 2: 0.30, 3: 0.35}[REVISION]
BALL_DIAMETER = 16.80
LEAD_IN = 0.30
bpy.ops.wm.open_mainfile(filepath=str(PROJECT/'source/holder-without-ribs.blend'))
base = bpy.data.objects['Base - rounded roots - no ribs']
ball = bpy.data.objects['Ball module - 17 mm']
original_base = [tuple(v.co) for v in base.data.vertices]
vs = [v.co.copy() for v in ball.data.vertices]
center = Vector(((min(v.x for v in vs)+max(v.x for v in vs))/2,
                 (min(v.y for v in vs)+max(v.y for v in vs))/2,
                 max(v.z for v in vs)-8.5))
leading_y = min(v.y for v in vs if v.z < 7.01)
# Retain the 3.2 mm dovetail depth and side angles. The upper 0.5 mm
# shoulder narrows to match it, blending into the unchanged neck.
for vertex in ball.data.vertices:
    p = vertex.co
    if p.z < 7.01:
        p.x -= SIDE_RELIEF if p.x > center.x else -SIDE_RELIEF
    elif p.z < 7.501:
        p.x = center.x+(p.x-center.x)*(7.5-2*SIDE_RELIEF)/7.5
    # Include the truncated sphere's bottom rings so its surface remains
    # spherical. Connecting neck faces follow those rings continuously.
    if p.z > 13.89:
        vertex.co = center+(p-center)*(BALL_DIAMETER/17.0)
mesh = bmesh.new(); mesh.from_mesh(ball.data); mesh.normal_update()
end_edges = [e for e in mesh.edges
             if all(abs(v.co.y-leading_y)<1e-4 and v.co.z<7.501 for v in e.verts)
             and e.is_manifold and e.link_faces[0].normal.dot(e.link_faces[1].normal)<0.999]
assert end_edges, 'No leading-end boundary found'
bmesh.ops.bevel(mesh, geom=end_edges, offset=LEAD_IN, segments=1,
                affect='EDGES', clamp_overlap=True)
bmesh.ops.triangulate(mesh, faces=list(mesh.faces))
bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
assert all(e.is_manifold for e in mesh.edges)
assert all(f.calc_area()>1e-9 for f in mesh.faces)
assert mesh.calc_volume(signed=True)>0
report = {'revision':f'PAHT-CF fit {REVISION}','ball_diameter_mm':BALL_DIAMETER,
          'slider_width_reduction_mm':2*SIDE_RELIEF,'slider_depth_mm':3.2,
          'lead_in_chamfer_mm':LEAD_IN,'lead_in_edge_count':len(end_edges),
          'non_manifold_edges':0,'zero_area_faces':0,
          'volume_mm3':mesh.calc_volume(),'physical_fit_verified':False,
          'main_holder_physical_fit':'Confirmed by owner 2026-11-09',
          'ball_center_mm':list(center)}
mesh.to_mesh(ball.data);mesh.free();ball.data.update()
assert [tuple(v.co) for v in base.data.vertices]==original_base
ball.name='Ball module - 16.8 mm - PAHT fit'
bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/f'source/holder-paht-fit{SUFFIX}.blend'))
bpy.ops.object.select_all(action='DESELECT');ball.select_set(True);bpy.context.view_layer.objects.active=ball
# Print the same flat back on the bed as the accepted STL.
ball.location.z=-3.8
bpy.ops.wm.stl_export(filepath=str(PROJECT/f'models/ball-module-paht-fit{SUFFIX}.stl'),export_selected_objects=True)
ball.location.z=0
# Short, full-cross-section fit coupon, cut from the revised leading end.
trial=ball.copy();trial.data=ball.data.copy();bpy.context.collection.objects.link(trial)
m=bmesh.new();m.from_mesh(trial.data)
bmesh.ops.bisect_plane(m,geom=list(m.verts)+list(m.edges)+list(m.faces),dist=1e-6,
                      plane_co=(0,0,7.5),plane_no=(0,0,1),clear_outer=True)
bmesh.ops.holes_fill(m,edges=[e for e in m.edges if e.is_boundary],sides=0)
r=bmesh.ops.bisect_plane(m,geom=list(m.verts)+list(m.edges)+list(m.faces),dist=1e-6,
                        plane_co=(0,leading_y+6,0),plane_no=(0,1,0),clear_outer=True)
boundary=[e for e in m.edges if e.is_boundary]
bmesh.ops.holes_fill(m,edges=boundary,sides=0)
bmesh.ops.triangulate(m,faces=list(m.faces));bmesh.ops.recalc_face_normals(m,faces=list(m.faces))
assert all(e.is_manifold for e in m.edges)
m.to_mesh(trial.data);m.free();trial.location.z=-3.8
bpy.ops.object.select_all(action='DESELECT');trial.select_set(True)
bpy.ops.wm.stl_export(filepath=str(PROJECT/f'models/slider-paht-fit-test{SUFFIX}.stl'),export_selected_objects=True)
report['base_stl_sha256']=hashlib.sha256((PROJECT/'models/base-front-down.stl').read_bytes()).hexdigest()
(PROJECT/f'analysis/paht-fit-checks{SUFFIX}.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
