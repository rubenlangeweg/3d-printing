"""Package the revised small part using the GUI-verified PAHT-CF preset."""
from pathlib import Path
import struct,zipfile,xml.etree.ElementTree as E, argparse
P=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--revision',type=int,choices=[1,2,3,4],default=4)
revision=parser.parse_args().revision
suffix='' if revision==1 else f'-v{revision}'
M='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PR='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
E.register_namespace('',M);E.register_namespace('p',PR)
ns={'m':M};q=lambda n:'{'+M+'}'+n
for stem,title in [('ball-module-paht-fit','XC60 ball 16.8 mm PAHT fit'),('slider-paht-fit-test','XC60 slider fit test')]:
 stem+=suffix
 title+=f' revision {revision}'
 E.register_namespace('',M)
 raw=(P/'models'/f'{stem}.stl').read_bytes();count=struct.unpack_from('<I',raw,80)[0];vertices=[];faces=[];lookup={}
 for i in range(count):
  v=struct.unpack_from('<12fH',raw,84+i*50);face=[]
  for j in (3,6,9):
   xyz=tuple(v[j:j+3])
   if xyz not in lookup:lookup[xyz]=len(vertices);vertices.append(xyz)
   face.append(lookup[xyz])
  faces.append(face)
 with zipfile.ZipFile(P/'models/holder-without-ribs.3mf') as src:
  data={n:src.read(n) for n in src.namelist()}
 child=E.fromstring(data['3D/Objects/object_1.model']);mesh=child.find('.//m:mesh',ns);mesh.clear()
 vv=E.SubElement(mesh,q('vertices'));tt=E.SubElement(mesh,q('triangles'))
 for xyz in vertices:E.SubElement(vv,q('vertex'),dict(zip(('x','y','z'),map(lambda v:format(v,'.9g'),xyz))))
 for face in faces:E.SubElement(tt,q('triangle'),dict(zip(('v1','v2','v3'),map(str,face))))
 data['3D/Objects/object_1.model']=E.tostring(child,encoding='utf-8',xml_declaration=True)
 root=E.fromstring(data['3D/3dmodel.model']);res=root.find('m:resources',ns);res.remove(res.find('m:object[@id="4"]',ns))
 build=root.find('m:build',ns);build.remove(build.find('m:item[@objectid="4"]',ns));build[0].set('transform','1 0 0 0 1 0 0 0 1 128 128 0')
 for md in list(root.findall('m:metadata',ns)):
  if md.get('name','').startswith('Thumbnail'):root.remove(md)
  elif md.get('name')=='Title':md.text=title
 data['3D/3dmodel.model']=E.tostring(root,encoding='utf-8',xml_declaration=True)
 cfg=E.fromstring(data['Metadata/model_settings.config']);cfg.remove(cfg.find('object[@id="4"]'));cfg.remove(cfg.find('assemble'))
 for md in cfg.findall('.//metadata'):
  k=md.get('key')
  if k=='name':md.set('value',title)
  if k=='source_file':md.set('value',stem+'.stl')
  if k in ('thumbnail_file','thumbnail_no_light_file','top_file','pick_file'):md.set('value','')
  if md.get('face_count'):md.set('face_count',str(count))
 cfg.find('.//mesh_stat').set('face_count',str(count))
 plate=cfg.find('plate')
 for inst in list(plate.findall('model_instance')):
  if inst.find('metadata[@key="object_id"]').get('value')=='4':plate.remove(inst)
 data['Metadata/model_settings.config']=E.tostring(cfg,encoding='utf-8',xml_declaration=True)
 for name in ['3D/_rels/3dmodel.model.rels','_rels/.rels']:
  rel=E.fromstring(data[name])
  for r in list(rel):
   if 'object_2.model' in r.get('Target','') or r.get('Target','').endswith('.png'):rel.remove(r)
  E.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/relationships')
  data[name]=E.tostring(rel,encoding='utf-8',xml_declaration=True)
 with zipfile.ZipFile(P/'models'/f'{stem}.3mf','w',zipfile.ZIP_DEFLATED) as dst:
  for name,content in data.items():
   if name=='3D/Objects/object_2.model' or name.endswith('.png') or name=='Metadata/cut_information.xml':continue
   dst.writestr(name,content)
 print(stem,'triangles',count,'bounds',[(min(v[k] for v in vertices),max(v[k] for v in vertices)) for k in range(3)])
