import bpy,bmesh,json,argparse,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--revision',type=int,choices=[1,2,3,4,5],default=5)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
suffix='' if args.revision==1 else f'-v{args.revision}'
bpy.ops.wm.open_mainfile(filepath=str(P/f'source/holder-paht-fit{suffix}.blend'))
base=bpy.data.objects['Base - rounded roots - no ribs'];ball=bpy.data.objects['Ball module - 16.8 mm - PAHT fit'];values=[]
for y in [42,35,28,21,14,7,0]:
 ball.location.y=y;bpy.context.view_layer.update()
 test=base.copy();test.data=base.data.copy();bpy.context.collection.objects.link(test)
 mod=test.modifiers.new('Check collision','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=ball
 dg=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(test.evaluated_get(dg));bm=bmesh.new();bm.from_mesh(mesh);vol=abs(bm.calc_volume());bm.free();bpy.data.meshes.remove(mesh);bpy.data.objects.remove(test,do_unlink=True)
 assert vol<1e-5,(y,vol);values.append({'offset_y_mm':y,'intersection_mm3':vol})
report=json.loads((P/f'analysis/paht-fit-checks{suffix}.json').read_text());report['insertion_path']=values
for name in ['ball-module-paht-fit','slider-paht-fit-test']:
 name+=suffix
 bpy.ops.wm.stl_import(filepath=str(P/'models'/f'{name}.stl'));o=bpy.context.object;bm=bmesh.new();bm.from_mesh(o.data)
 remaining=set(bm.verts);components=0
 while remaining:
  todo=[remaining.pop()];components+=1
  while todo:
   v=todo.pop()
   for e in v.link_edges:
    w=e.other_vert(v)
    if w in remaining:remaining.remove(w);todo.append(w)
 assert components==1
 assert all(e.is_manifold for e in bm.edges)
 assert all(f.calc_area()>(1e-12 if args.revision==5 else 1e-9) for f in bm.faces)
 assert bm.calc_volume(signed=True)>0
 report[name]={'connected_solids':components,'manifold':True,'volume_mm3':bm.calc_volume()};bm.free()
(P/f'analysis/paht-fit-checks{suffix}.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
