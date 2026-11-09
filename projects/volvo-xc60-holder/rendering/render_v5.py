from pathlib import Path
P=Path(__file__).resolve().parents[1]
# Reuse the repository's camera, materials and lighting without changing
# the accepted rendering script or any printable geometry.
code=(P/'rendering/render.py').read_text().split("if mode in ('stills','preview'):")[0]
code=code.replace("'source/holder-without-ribs.blend'", "'source/holder-paht-fit-v5.blend'")
code=code.replace("'Ball module - 17 mm'", "'Ball module - 16.8 mm - PAHT fit'")
exec(compile(code,__file__,'exec'))
base.hide_render=True
# Smooth the sampled curved neck surfaces; keep the dovetail faces crisp.
for face in ball.data.polygons:
    if all(ball.data.vertices[i].co.z > .007501 for i in face.vertices):
        face.use_smooth=True
floor.location.y=-.008056
view((65,40,80),(0,6,14),48,1200,1000)
scene.eevee.taa_render_samples=64
scene.render.resolution_percentage=100
scene.render.filepath='//../renders/ball-module-paht-fit-v5.png'
bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/'rendering/paht-fit-v5.blend'))
bpy.ops.render.render(write_still=True)
