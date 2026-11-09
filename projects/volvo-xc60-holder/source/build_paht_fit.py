"""Build the PAHT-CF fit revision from the accepted, unchanged source.
Run with Blender --background --python source/build_paht_fit.py.
"""
from pathlib import Path
import bpy, bmesh, json, hashlib, argparse, sys, math
from mathutils import Vector

PROJECT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--revision', type=int, choices=[1, 2, 3, 4, 5], default=5)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
REVISION = args.revision
SUFFIX = '' if REVISION == 1 else f'-v{REVISION}'
SIDE_RELIEF = {1: 0.20, 2: 0.30, 3: 0.35, 4: 0.35, 5: 0.35}[REVISION]
BALL_DIAMETER = 16.80
LEAD_IN = 0.30
SLIDER_LENGTH = 28.0 if REVISION >= 4 else 16.0
NECK_DIAMETER = 8.5 if REVISION >= 4 else 7.1
BALL_RISE = 6.0 if REVISION == 5 else 0.0
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
    if REVISION >= 4:
        # Extend only the trailing end. Preserve the seated stop, ball centre
        # and every sliding cross-section from the accepted v3 fit.
        if p.z < 7.501 and abs(p.y-(leading_y+16)) < 1e-4:
            p.y += SLIDER_LENGTH-16
        # Widen the existing narrow neck ring, keeping the ball surface intact.
        if abs(p.z-11.4412) < 1e-3:
            p.x = center.x+(p.x-center.x)*NECK_DIAMETER/7.1
            p.y = center.y+(p.y-center.y)*NECK_DIAMETER/7.1
    # Include the truncated sphere's bottom rings so its surface remains
    # spherical. Connecting neck faces follow those rings continuously.
    if p.z > 13.89:
        vertex.co = center+(p-center)*(BALL_DIAMETER/17.0)
if REVISION == 5:
    # Rounded rectangular sections: exponent 8 keeps broad, nearly flat sides
    # without collapsing the inherited mesh into collinear triangles.
    def rounded_rectangle(p, old_rx, old_ry, new_rx, new_ry):
        u=(p.x-center.x)/old_rx; v=(p.y-center.y)/old_ry
        r=math.hypot(u,v)
        if r>1e-8:
            c=u/r; t=v/r; factor=(abs(c)**8+abs(t)**8)**(-1/8)
            p.x=center.x+new_rx*r*c*factor
            p.y=center.y+new_ry*r*t*factor
    for vertex in ball.data.vertices:
        p=vertex.co
        if abs(p.z-7.5)<1e-4 and abs(p.y-center.y)<4:
            rounded_rectangle(p, 3.55*(7.5-2*SIDE_RELIEF)/7.5, 3.55, 3.2, 5.0)
            p.y+=BALL_RISE
        elif p.z>7.501:
            if abs(p.z-11.4412)<1e-3:
                rounded_rectangle(p, 4.25, 4.25, 4.25, 5.0)
            p.y+=BALL_RISE
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
          'slider_length_mm':SLIDER_LENGTH,'neck_width_mm':NECK_DIAMETER,
          'neck_section':'rounded rectangle' if REVISION == 5 else 'round',
          'neck_height_mm':10.0 if REVISION == 5 else NECK_DIAMETER,
          'ball_rise_mm':BALL_RISE,
          'lead_in_chamfer_mm':LEAD_IN,'lead_in_edge_count':len(end_edges),
          'non_manifold_edges':0,'zero_area_faces':0,
          'volume_mm3':mesh.calc_volume(),'physical_fit_verified':False,
          'main_holder_physical_fit':'Confirmed by owner 2026-11-09',
          'ball_center_mm':list(center+Vector((0,BALL_RISE,0)))}
mesh.to_mesh(ball.data);mesh.free();ball.data.update()
if REVISION == 5:
    # Rebuild the neck as a clean loft. Retain the exact dovetail and sphere
    # surfaces; overlap the new neck slightly into their capped solids.
    def capped_piece(name, height, keep_above):
        bm=bmesh.new(); bm.from_mesh(ball.data)
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                              dist=1e-6,plane_co=(0,0,height),plane_no=(0,0,1),
                              clear_inner=keep_above,clear_outer=not keep_above)
        bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        if not keep_above:
            bmesh.ops.dissolve_limit(bm,angle_limit=1e-5,verts=list(bm.verts),edges=list(bm.edges))
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        data=bpy.data.meshes.new(name);bm.to_mesh(data);bm.free()
        obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
        return obj
    foot=capped_piece('Temporary slider',7.5,False)
    fit_test_mesh=foot.data.copy()
    sphere=capped_piece('Temporary ball',13.95,True)
    vertices=[]; faces=[]; count=128
    # z, x radius, y radius, superellipse exponent
    for z,rx,ry,power in [(7.4,3.2,5.0,8),(11.4412,4.25,5.0,8),
                          (13.9,5.7,5.7,2),(14.3,5.7,5.7,2)]:
        for i in range(count):
            a=2*math.pi*i/count;c=math.cos(a);t=math.sin(a)
            factor=(abs(c)**power+abs(t)**power)**(-1/power)
            vertices.append((center.x+rx*c*factor,center.y+BALL_RISE+ry*t*factor,z))
    faces.append(tuple(reversed(range(count))))
    for ring in range(3):
        for i in range(count):
            j=(i+1)%count
            faces.append((ring*count+i,ring*count+j,(ring+1)*count+j,(ring+1)*count+i))
    faces.append(tuple(range(3*count,4*count)))
    data=bpy.data.meshes.new('Clean neck loft');data.from_pydata(vertices,[],faces);data.update()
    neck=bpy.data.objects.new('Temporary neck',data);bpy.context.collection.objects.link(neck)
    bm=bmesh.new();bm.from_mesh(neck.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(neck.data);bm.free()
    bpy.context.view_layer.objects.active=foot
    for obj in [neck,sphere]:
        mod=foot.modifiers.new('Joined reinforcement','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(obj,do_unlink=True)
    ball.data=foot.data.copy();bpy.data.objects.remove(foot,do_unlink=True)
    bm=bmesh.new();bm.from_mesh(ball.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    flat_edges=[e for e in bm.edges if e.is_manifold and all(abs(f.normal.z)>.999999 for f in e.link_faces)]
    bmesh.ops.dissolve_limit(bm,angle_limit=1e-5,verts=[],edges=flat_edges)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-5)
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges)
    # Boolean seams can leave positive-area triangles far below printer
    # resolution. Record those explicitly; still reject zero-area faces.
    report['minimum_triangle_area_mm2']=min(f.calc_area() for f in bm.faces)
    report['tiny_positive_seam_triangles']=sum(f.calc_area()<1e-9 for f in bm.faces)
    assert all(f.calc_area()>1e-12 for f in bm.faces)
    assert bm.calc_volume(signed=True)>0
    report['volume_mm3']=bm.calc_volume();report['neck_construction']='joined rectangular-to-circular loft'
    bm.to_mesh(ball.data);bm.free();ball.data.update()

assert [tuple(v.co) for v in base.data.vertices]==original_base
ball.name='Ball module - 16.8 mm - PAHT fit'
bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/f'source/holder-paht-fit{SUFFIX}.blend'))
bpy.ops.object.select_all(action='DESELECT');ball.select_set(True);bpy.context.view_layer.objects.active=ball
# Print the same flat back on the bed as the accepted STL.
ball.location.z=-3.8
bpy.ops.wm.stl_export(filepath=str(PROJECT/f'models/ball-module-paht-fit{SUFFIX}.stl'),export_selected_objects=True)
ball.location.z=0
# Fit coupon: short leading section for v1-v3; full-length slider for v4.
trial=ball.copy();trial.data=(fit_test_mesh.copy() if REVISION==5 else ball.data.copy());bpy.context.collection.objects.link(trial)
m=bmesh.new();m.from_mesh(trial.data)
bmesh.ops.bisect_plane(m,geom=list(m.verts)+list(m.edges)+list(m.faces),dist=1e-6,
                      plane_co=(0,0,7.5),plane_no=(0,0,1),clear_outer=True)
bmesh.ops.holes_fill(m,edges=[e for e in m.edges if e.is_boundary],sides=0)
if REVISION < 4:
    bmesh.ops.bisect_plane(m,geom=list(m.verts)+list(m.edges)+list(m.faces),dist=1e-6,
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
