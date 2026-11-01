"""Rebuild the organizer in generated/organizer. Geometry only, Blender 5.0.

Derived from the authored October 2026 rounded-body and folded-clip pipeline.
The accepted print STL in models/ is kept separate from generated output.
"""
import bpy, bmesh, math, json, struct, pathlib
from mathutils.bvhtree import BVHTree
from mathutils import Vector
from math import pi, sin, cos
PROJECT = pathlib.Path(__file__).resolve().parents[1]
out = PROJECT / 'generated' / 'organizer'
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections):
    if col.name!='Collection': bpy.data.collections.remove(col)
product=bpy.data.collections.new('PRODUCT | Leander 752020-72'); bpy.context.scene.collection.children.link(product)
studio=bpy.data.collections.new('STUDIO | preview only'); bpy.context.scene.collection.children.link(studio)
base=bpy.data.collections.get('Collection')

def move(obj,col):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)

def mat(name,color,rough=.36,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m
charcoal=mat('ABS | charcoal grey',(.043,.044,.053),.34)
mid=mat('ABS | dusty grey',(.205,.207,.197),.34)
light=mat('ABS | pale grey',(.48,.49,.48),.33)
alum=mat('Aluminium | satin grey',(.31,.32,.31),.32,.65)
clipmat=mat('ABS | grey hooks',(.28,.29,.28),.35)
white=mat('Studio | warm white',(.78,.765,.73),.67)

def finish(name,verts,faces,material,col=product):
    me=bpy.data.meshes.new(name+' mesh'); me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new(name,me); col.objects.link(o); o.data.materials.append(material)
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(me); bm.free(); o.select_set(False)
    for p in me.polygons: p.use_smooth=True
    return o

def rr(w,d,r,n=16):
    p=[]
    for cx,cy,start in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,pi/2),(-w/2+r,-d/2+r,pi),(w/2-r,-d/2+r,3*pi/2)]:
        for j in range(n):
            a=start+(j/(n-1))*pi/2
            p.append((cx+r*cos(a),cy+r*sin(a)))
    return p

def bin_body(name,x,material):
    # Every profile is a ring. Outer wall, rolled top lip, inner wall and floor form one closed solid.
    specs=[]
    # Soft 6 mm transition from flat base to drafted side wall.
    for j in range(9):
        a=j*pi/16
        specs.append((.130-.012+.012*sin(a),.098-.012+.012*sin(a),.011-.006+.006*sin(a),.006*(1-cos(a))))
    for z in [.012,.025,.05,.075,.095,.1075]:
        t=(z-.006)/(.1075-.006)
        specs.append((.130+.010*t,.098+.010*t,.011+.003*t,z))
    # Half-round rim, 2.5 mm wall thickness.
    for j in range(1,9):
        a=j*pi/8
        offset=.00125*(1-cos(a)); z=.1075+.00125*sin(a)
        specs.append((.140-2*offset,.108-2*offset,.014-offset,z))
    for z in [.095,.075,.05,.025,.012,.009]:
        t=(z-.006)/(.1075-.006)
        specs.append((.130+.010*t-.005,.098+.010*t-.005,.011+.003*t-.0025,z))
    for j in range(1,9):
        a=j*pi/16
        specs.append((.125-.010*(1-cos(a)),.093-.010*(1-cos(a)),.0085-.005*(1-cos(a)),.009-.005*sin(a)))
    verts=[]; faces=[]; N=64
    for w,d,r,z in specs:
        verts += [(xx+x,yy-.059,z) for xx,yy in rr(w,d,r)]
    for k in range(len(specs)-1):
        for j in range(N):
            q=(j+1)%N; faces.append((k*N+j,k*N+q,(k+1)*N+q,(k+1)*N+j))
    faces.append(tuple(reversed(range(N))))
    faces.append(tuple((len(specs)-1)*N+j for j in range(N)))
    o=finish(name,verts,faces,material)
    o['dimensions_basis']='Bin 140 x 108 x 109 mm body; photograph estimate, rear hanger included in 120 mm set depth.'
    return o

def cube(name,loc,scale,material,bevel=.0015,col=product):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); move(o,col); o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Soft moulded edges','BEVEL'); mod.width=bevel; mod.segments=5
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in o.data.polygons:p.use_smooth=True
    mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); mod.keep_sharp=True
    return o

def yz_solid(name,profile,width,x,material,bevel=.001):
    v=[(x-width/2,y,z) for y,z in profile]+[(x+width/2,y,z) for y,z in profile]
    n=len(profile); f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=finish(name,v,f,material)
    if bevel:
        m=o.modifiers.new('Rounded clip edges','BEVEL');m.width=bevel;m.segments=4
        bpy.context.view_layer.objects.active=o; o.select_set(True);bpy.ops.object.modifier_apply(modifier=m.name);o.select_set(False)
    m=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
    return o

for m,c in [(charcoal,(.06,.053,.046)),(mid,(.24,.224,.196)),(light,(.48,.456,.411))]:
    m.diffuse_color=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1)
# Enlarge only the two front corner radii, opposite the rear mounting flange.
# Both outer and inner rings receive the same increment to preserve wall thickness.
def rr(w,d,r,n=16):
    points=[]
    for sx,sy,start in [(1,1,0),(-1,1,math.pi/2),(-1,-1,math.pi),(1,-1,3*math.pi/2)]:
        radius=r+.004 if sy<0 else r*.2
        cx=sx*(w/2-radius);cy=sy*(d/2-radius)
        for j in range(n):
            angle=start+j/(n-1)*math.pi/2
            points.append((cx+radius*math.cos(angle),cy+radius*math.sin(angle)))
    return points
body=bin_body('Container 1 | full-width folded rear lip',0,charcoal)
for v in body.data.vertices:
    original_y=v.co.y+.059
    original_z=v.co.z
    v.co.y=original_y*(.100/.108)-.0075
    v.co.z=original_z*(.110/.10875)
    # Flatten the rear rim where it joins the flange. Smoothly retain the rolled
    # front and side rim without leaving a shelf inside the container.
    if original_z>=.1075-1e-8:
        t=max(0,min(1,(original_y-.030)/.015));weight=t*t*(3-2*t)
        v.co.z=v.co.z*(1-weight)+.110*weight
body.data.update()
# Photo shows an uninterrupted flat rear flange with a downturned outer edge.
# Its 15 mm extension is included in the user's total 115 mm depth.
profile=[(.0402,.110),(.0575,.110),(.0575,.089),(.055,.089),(.055,.1075),(.0402,.1075)]
lip=yz_solid('Full-width mounting flange',profile,.140,0,charcoal,.00045)
bpy.context.view_layer.objects.active=body
mod=body.modifiers.new('Fuse full-width flange','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=lip
bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(lip,do_unlink=True)
bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
bmesh.ops.dissolve_limit(bm,angle_limit=1e-6,verts=list(bm.verts),edges=list(bm.edges))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
bm.to_mesh(body.data);bm.free();body.data.update()

o=body; o.name='Organizer | 140 x 115 x 110 mm'
bpy.context.view_layer.objects.active=o; o.select_set(True)
old_count=len(o.data.vertices)
# Remove the small ledge at the flange end by following the body's side draft.
# Its front end used to remain at X=70 mm while the wall below tapers inward.
for v in o.data.vertices:
    p=v.co
    if p.y>.0398 and p.z>.087:
        wall_half=.065+.005*max(0,min(1,(p.z-.006068)/(.110-.006068)))
        if abs(p.x)>wall_half:p.x=math.copysign(wall_half,p.x)
o.data.update()
# Rebuild the joined surface at 0.25 mm resolution and round the remaining tiny
# seam geometrically. This changes the STL surface, not just display normals.
o.data.remesh_voxel_size=.00025;o.data.remesh_voxel_adaptivity=0
bpy.ops.object.voxel_remesh()
m=o.modifiers.new('Blend lip seam and soften small print edges','SMOOTH');m.factor=.55;m.iterations=5
bpy.ops.object.modifier_apply(modifier=m.name)
# Reduce triangles while retaining an export resolution finer than typical layers.
m=o.modifiers.new('Compact printable surface','DECIMATE');m.decimate_type='COLLAPSE';m.ratio=.16
bpy.ops.object.modifier_apply(modifier=m.name)
# Restore the exact nominal envelope and a flat base on the build plate.
lo=[min(v.co[j] for v in o.data.vertices) for j in range(3)];hi=[max(v.co[j] for v in o.data.vertices) for j in range(3)]
for v in o.data.vertices:
    v.co.x=(v.co.x-(lo[0]+hi[0])/2)*.140/(hi[0]-lo[0])
    v.co.y=(v.co.y-(lo[1]+hi[1])/2)*.115/(hi[1]-lo[1])
    v.co.z=(v.co.z-lo[2])*.110/(hi[2]-lo[2])
    if v.co.z<.00015:v.co.z=0
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
assert all(e.is_manifold for e in bm.edges)
assert len({v for f in bm.faces for v in f.verts})==len(bm.verts)
bm.to_mesh(o.data);bm.free();o.data.update()
for f in o.data.polygons:f.use_smooth=True
# Verify thickness and hanging clearance by rays through actual mesh surfaces.
bvh=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get())
def hit(origin,direction):
    result=bvh.ray_cast(Vector(origin),Vector(direction));assert result[0] is not None;return result[0]
body_rear=hit((0,.05,.098),(0,-1,0)).y
flange_inner=hit((0,.05,.098),(0,1,0)).y
flange_outer=hit((0,.07,.098),(0,-1,0)).y
rear_inside=hit((0,.035,.098),(0,1,0)).y
side_outer=hit((.08,0,.07),(-1,0,0)).x
side_inner=hit((.05,0,.07),(1,0,0)).x
roof_top=hit((0,.05,.12),(0,0,-1)).z
roof_bottom=hit((0,.05,.10),(0,0,1)).z
checks={'vertices':len(o.data.vertices),'gap_mm':(flange_inner-body_rear)*1000,'rear_wall_mm':(body_rear-rear_inside)*1000,'flange_wall_mm':(flange_outer-flange_inner)*1000,'side_wall_mm':(side_outer-side_inner)*1000,'flange_roof_mm':(roof_top-roof_bottom)*1000,'dimensions_mm':[140,115,110]}
assert checks['gap_mm']>=12.3
assert all(checks[k]>2 for k in ('rear_wall_mm','flange_wall_mm','side_wall_mm','flange_roof_mm'))
o['surface_update']='Removed flange end ledge, physically blended mesh seam, softened small edges'
o['mounting_gap_mm_measured']=checks['gap_mm']
o['geometry_validation']='Closed manifold mesh; sampled wall and lip thickness above 2 mm'
# True STL surface, in millimetres.
me=o.data;me.calc_loop_triangles()
with (out/'leander-container-mm.stl').open('wb') as f:
    f.write(b'Blender container | softened lip join | H110 W140 D115 mm'.ljust(80,b' '));f.write(struct.pack('<I',len(me.loop_triangles)))
    for t in me.loop_triangles:
        vv=[me.vertices[j].co*1000 for j in t.vertices];n=(vv[1]-vv[0]).cross(vv[2]-vv[0]).normalized();f.write(struct.pack('<12fH',*n,*vv[0],*vv[1],*vv[2],0))
# Save the deliverable with exactly one mesh object.
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
scene.unit_settings.length_unit='MILLIMETERS'; scene.render.filepath='//preview.png'
scene['source_reference']='Photo-derived accessory inspired by Leander organizer 752020-72; independently modeled mounting flange'
for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.texts):
    for block in list(collection):
        if block.users == 0: collection.remove(block)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'leander-container.blend'))
(out/'geometry-checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks),flush=True)
