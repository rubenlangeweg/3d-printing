"""Build the selected V4 shelf in generated/shelf-v4; pass -- --render for previews."""
import bpy, bmesh, math, pathlib, struct, json, sys
from mathutils import Vector

PROJECT = pathlib.Path(__file__).resolve().parents[1]
OUT = PROJECT / 'generated' / 'shelf-v4'
WORK = OUT / 'work'
RENDER = '--render' in sys.argv and '--geometry-only' not in sys.argv
OUT.mkdir(parents=True,exist_ok=True)
WORK.mkdir(parents=True,exist_ok=True)
W, DEPTH, GAP, ANGLE = 180.,150.,13.,116.
WALL, PLATE, LEG, HOOK, TOP = 4.5,6.,70.,30.,12.
EDGE, REAR, ROOT_RADIUS, PLAN = 1.25,3.,6.,12.
theta=math.radians(26)
u=Vector((math.sin(theta),math.cos(theta)))
n=Vector((math.cos(theta),-math.sin(theta)))
def p(t,q): return tuple(u*t+n*q)
def bezier(points,t):
    degree=len(points)-1
    return tuple(sum(math.comb(degree,i)*(1-t)**(degree-i)*t**i*points[i][axis] for i in range(degree+1)) for axis in range(2))

bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=.001
scene.unit_settings.length_unit='MILLIMETERS'
def material(name,color,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough
    return m
grey=material('Warm soft grey',(.36,.395,.38),.38)
def solid(name,verts,faces):
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()
    ob=bpy.data.objects.new(name,mesh); scene.collection.objects.link(ob); ob.data.materials.append(grey)
    return ob
def profile(name,points,width,x=0):
    count=len(points)
    verts=[(x-width/2,y,z) for y,z in points]+[(x+width/2,y,z) for y,z in points]
    faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    return solid(name,verts,faces)
def boolean(ob,tool,operation):
    bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new(operation,'BOOLEAN'); mod.operation=operation; mod.solver='EXACT'; mod.object=tool
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool,do_unlink=True)
def arc(cy,cz,r,start,end,count=48):
    return [(cy+r*math.cos(math.radians(start+(end-start)*i/count)),cz+r*math.sin(math.radians(start+(end-start)*i/count))) for i in range(count+1)]

# One continuous cross section removes the old vertical ledge. Both contact
# planes and the cap of the 13 mm mounting cavity retain their original position.
root_cz=TOP-PLATE-ROOT_RADIUS
root_cy=(WALL+ROOT_RADIUS-n.y*root_cz)/n.x
rear_cz=TOP-REAR
rear_cy=(-GAP-WALL+REAR-n.y*rear_cz)/n.x
cross=[p(-LEG,0),p(-LEG,WALL)]
cross+=arc(root_cy,root_cz,ROOT_RADIUS,154,90)
cross += [(DEPTH,TOP-PLATE),(DEPTH,TOP)]
cross += arc(rear_cy,rear_cz,REAR,90,154)
cross += [p(-HOOK,-GAP-WALL),p(-HOOK,-GAP),p(0,-GAP),p(0,0)]
shelf=profile('Leander shelf V4 | deeper inset curved ribs | 180 x 150 mm',cross,W)

# Quintic plan corners have zero curvature at their tangent-to-straight joins.
r=PLAN
corner=[(W/2,DEPTH-r),(W/2,DEPTH-r+.22*r),(W/2,DEPTH-r+.62*r),
        (W/2-r+.62*r,DEPTH),(W/2-r+.22*r,DEPTH),(W/2-r,DEPTH)]
right=[bezier(corner,i/64) for i in range(65)]
left=[(-x,y) for x,y in reversed(right)]
ring=[(-W/2,-200),(W/2,-200)]+right+left
count=len(ring)
verts=[(x,y,z) for z in [-150,30] for x,y in ring]
faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]
faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
boolean(shelf,solid('Continuous corner outline',verts,faces),'INTERSECT')

# Apply real edge rolls to exposed longitudinal seams, while explicitly
# excluding the inner mounting surfaces and their junctions from the operation.
bm=bmesh.new(); bm.from_mesh(shelf.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6)
bmesh.ops.dissolve_limit(bm,angle_limit=1e-5,verts=list(bm.verts),edges=list(bm.edges),use_dissolve_boundaries=False)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.normal_update()
print('Before bevel nonmanifold',sum(not e.is_manifold for e in bm.edges),flush=True)
bm.to_mesh(shelf.data)
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'unbeveled.blend'))
def in_contact(face):
    qs=[n.x*v.co.y+n.y*v.co.z for v in face.verts]
    ts=[u.x*v.co.y+u.y*v.co.z for v in face.verts]
    return ((max(abs(q) for q in qs)<.001 and min(ts)<.001)
      or (max(abs(q+GAP) for q in qs)<.001 and min(ts)<.001)
      or (max(abs(t) for t in ts)<.001 and min(qs)>=-GAP-.001 and max(qs)<=.001))
chosen=[]
for e in bm.edges:
    if not e.is_manifold or any(in_contact(f) for f in e.link_faces):continue
    if e.calc_face_angle() > math.radians(20):chosen.append(e)
print('Edge finishing',len(chosen),'selected of',len(bm.edges),flush=True)
result=bmesh.ops.bevel(bm,geom=chosen,offset=EDGE,segments=8,affect='EDGES',clamp_overlap=False,
                       loop_slide=True,profile=.5,miter_outer='SHARP',miter_inner='SHARP')
print('Immediately after bevel nonmanifold',sum(not e.is_manifold for e in bm.edges),flush=True)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(shelf.data);bm.free()

# A pronounced concave quintic joins the inclined back and level platform.
# V4 intentionally removes a modest further amount of rib material relative to V3; strength must be reassessed.
start=Vector(p(-LEG+.5,WALL-1.5)); h=22.
# Extend both tangent ends inside the surrounding solids so the union has
# finite thickness instead of a zero-thickness tangential contact.
controls=[tuple(start),tuple(start+u*h),tuple(start+u*2*h),(81.6,7.),(111.6,7.),(131.6,7.)]
curve=[bezier(controls,i/160) for i in range(161)]
old_a=p(-67,3.5); old_d=(138.,7.)
deltas=[]
for y,z in [bezier(controls,i/10000) for i in range(10001)]:
    if old_a[0]<=y<=135.6:
        oldz=old_a[1]+(y-old_a[0])*(old_d[1]-old_a[1])/(old_d[0]-old_a[0])
        deltas.append(z-oldz)
# These signed distances document the intentional scoop; no preserved-strength assertion.
(WORK/'rib-profile.json').write_text(json.dumps({
    'coordinates':'Local Blender Y,Z in mm; upright shelf has deck top Z=12',
    'degree':5,'control_points_yz_mm':controls,
    'sampled_profile_yz_mm':curve,
    'start_parameter_t_mm':-LEG+.5,'start_parameter_q_mm':WALL-1.5,
    'start_tangent_control_spacing_mm':h,
    'rib_center_x_mm':[-65.,0.,65.], 'rib_width_mm':5.,
    'edge_roll_radius_mm':EDGE,
    'note':'V4 deliberately scoops material from V3 ribs and sets exposed tips about 15 mm farther inward; unchanged strength is not claimed.'
},indent=2))
# Analytic quarter-round sweeps keep a true 1.25 mm edge radius, independent
# of tiny Boolean junction edges. The ends terminate inside the solid shell.
derivative=[tuple(5*(Vector(controls[i+1])-Vector(controls[i]))) for i in range(5)]
stations=[]
for i in range(13):
    angle=math.pi/2*(12-i)/12
    stations.append((-1.25-EDGE*math.sin(angle),EDGE*(1-math.cos(angle))))
for i in range(13):
    angle=math.pi/2*i/12
    stations.append((1.25+EDGE*math.sin(angle),EDGE*(1-math.cos(angle))))
for x in [-65.,0.,65.]:
    loops=[]
    for dx,inset in stations:
        points=[]
        for i,c in enumerate(curve):
            tangent=Vector(bezier(derivative,i/160)).normalized()
            normal=Vector((-tangent.y,tangent.x))
            point=Vector(c)+inset*normal
            points.append((x+dx,*point))
        points += [(x+dx,controls[-1][0],10.),(x+dx,5.,10.),(x+dx,*p(0,.5)),(x+dx,*p(-LEG+.5,.5))]
        loops.append(points)
    count=len(loops[0]);verts=[v for loop in loops for v in loop]
    faces=[tuple(reversed(range(count))),tuple(range((len(loops)-1)*count,len(loops)*count))]
    for j in range(len(loops)-1):
        for i in range(count):
            faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
    rib=solid('Rounded curved support rib',verts,faces)
    boolean(shelf,rib,'UNION')

def metrics(ob):
    bm=bmesh.new();bm.from_mesh(ob.data)
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    todo=set(bm.verts);components=0
    while todo:
        stack=[todo.pop()];components+=1
        while stack:
            v=stack.pop()
            for e in v.link_edges:
                other=e.other_vert(v)
                if other in todo:todo.remove(other);stack.append(other)
    volume=bm.calc_volume(signed=True)
    bm.free()
    return {'non_manifold_edges':nonmanifold,'connected_components':components,'volume_cm3':volume/1000}
check=metrics(shelf); print('PRE CHECK',check,flush=True)
assert check['non_manifold_edges']==0 and check['connected_components']==1 and check['volume_cm3']>0,check

bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'beveled.blend'))
wall=profile('13 mm mounting clearance test', [p(-130,-GAP+.001),p(-.001,-GAP+.001),p(-.001,-.001),p(-130,-.001)],W+4)
test=shelf.copy();test.data=shelf.data.copy();scene.collection.objects.link(test)
boolean(test,wall,'INTERSECT')
bm=bmesh.new();bm.from_mesh(test.data);collision=abs(bm.calc_volume());print('Collision faces',len(bm.faces),'nonmanifold',sum(not e.is_manifold for e in bm.edges),flush=True);bm.free()
bpy.data.objects.remove(test,do_unlink=True)
assert collision<.01,collision

bm=bmesh.new();bm.from_mesh(shelf.data)
bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
assert all(e.is_manifold for e in bm.edges)
bm.to_mesh(shelf.data);bm.free()
# Smooth only curved surfaces; preserve planar tops and contact surfaces.
for poly in shelf.data.polygons:poly.use_smooth=True
for e in shelf.data.edges:e.use_edge_sharp=False
bm=bmesh.new();bm.from_mesh(shelf.data)
for e in bm.edges:
    e.smooth=e.is_manifold and e.calc_face_angle()<math.radians(35)
bm.to_mesh(shelf.data);bm.free()

properties={'surface_width_mm':W,'usable_projection_mm':DEPTH,'mounting_gap_mm':GAP,
    'mounting_angle_degrees':ANGLE,'platform_thickness_mm':PLATE,'backplate_length_mm':LEG,
    'rib_count':3,'rib_core_thickness_mm':5.,'edge_roll_radius_mm':EDGE,
    'rear_top_radius_mm':REAR,'underside_root_radius_mm':ROOT_RADIUS,
    'front_corner_extent_mm':PLAN,'front_corner_type':'Quintic with zero-curvature straight joins',
    'rib_profile':'Concave quintic with rounded lower edges; ends embedded in surrounding shell',
    'status':'Prototype; physical fit and load testing of this revision outstanding'}
for key,value in properties.items():shelf[key]=value
shelf.data.calc_loop_triangles()
stl=WORK/'validated-shelf.stl'
with stl.open('wb') as f:
    f.write(b'Leander shelf V4 deeper inset ribs | millimetres | top face on bed'.ljust(80,b' '))
    f.write(struct.pack('<I',len(shelf.data.loop_triangles)))
    for tri in shelf.data.loop_triangles:
        vv=[Vector((shelf.data.vertices[i].co.x,-shelf.data.vertices[i].co.y,TOP-shelf.data.vertices[i].co.z)) for i in tri.vertices]
        cross=(vv[1]-vv[0]).cross(vv[2]-vv[0]);assert cross.length>1e-12, ('Degenerate', [tuple(v) for v in vv])
        f.write(struct.pack('<12fH',*cross.normalized(),*vv[0],*vv[1],*vv[2],0))
stl.replace(OUT/'leander-shelf-180x150-curved-v4-mm.stl')
visible_tip_candidates=[]
for face in shelf.data.polygons:
    vv=[shelf.data.vertices[i].co for i in face.vertices]
    if min(v.z for v in vv)<TOP-PLATE-1e-5:
        visible_tip_candidates += [v.y for v in vv if abs(v.z-(TOP-PLATE))<1e-5 and abs(v.x)<=2.50001 and v.y>25]
assert visible_tip_candidates
visible_tip=max(visible_tip_candidates)
assert 111.5<visible_tip<112.5, visible_tip
check.update({'actual_exposed_tip_y_mm':visible_tip,'actual_outer_edge_setback_mm':DEPTH-visible_tip,
              'v3_actual_exposed_tip_y_mm':127.01587677001953,
              'additional_tip_setback_vs_v3_mm':127.01587677001953-visible_tip})
check.update(properties)
check.update({'reference_overlap_mm3':collision,'clearance_test_boundary_inset_mm':.001,
              'original_straight_rib_signed_delta_range_mm':[min(deltas),max(deltas)],
              'v3_volume_cm3':308.2731635830785,
              'rib_volume_removed_vs_v3_cm3':308.2731635830785-check['volume_cm3'],
              'rib_control_points_yz_mm':controls,
              'profile_envelope_check':'Before exposed edge rolling','triangles':len(shelf.data.loop_triangles),
              'stl_orientation':'Top face down on bed; dimensions in mm'})
(WORK/'geometry-checks.json').write_text(json.dumps(check,indent=2))
print(json.dumps(check),flush=True)

def camera(name,loc,target,scale):
    bpy.ops.object.camera_add(location=loc);cam=bpy.context.object;cam.name=name
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO';cam.data.ortho_scale=scale;cam.data.clip_start=.1;cam.data.clip_end=10000
    return cam
underside=camera('Underside overview',(310,400,-260),(0,40,-20),300)
side=camera('Side profile',(500,45,-20),(0,45,-22),235)
top=camera('Top three quarter',(300,390,290),(0,40,-20),310)
detail=camera('Mount to platform transition',(400,5,-65),(56,10,-3),80)
for loc,power,size in [((80,180,-320),2300000,280),((-250,50,200),2500000,300),((50,-300,220),3000000,350)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object
    light.data.energy=power;light.data.size=size
    light.rotation_euler=(Vector((0,40,-20))-light.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.2,.2,.2)
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.camera=underside
bpy.ops.object.select_all(action='DESELECT');shelf.select_set(True);bpy.context.view_layer.objects.active=shelf
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.clip_start=.1;space.clip_end=10000
            space.region_3d.view_location=Vector((0,40,-20));space.region_3d.view_distance=340
            space.region_3d.view_rotation=underside.rotation_euler.to_quaternion();space.shading.color_type='MATERIAL'
bpy.context.preferences.filepaths.save_version=0
scene.render.filepath = '//preview.png'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'leander-shelf-curved-v4.blend'))
if RENDER:
    for cam,name in [(underside,'01-curved-underside.png'),(side,'02-curved-side.png')]:
        scene.camera=cam;scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
    print('V4 candidate complete',flush=True)
