"""Create the 12 fps README preview. Requires Pillow. Run after rendering."""
from pathlib import Path
from PIL import Image
import sys

project = Path(__file__).resolve().parents[1]
name = sys.argv[1] if len(sys.argv)>1 else 'assembly'
count = {'assembly':144,'orbit':288,'mous-attachment':240}[name]
paths = sorted((project / 'generated' / name / 'frames').glob('*.png'))
if [p.name for p in paths] != [f'{i:04d}.png' for i in range(1,count+1)]:
    raise SystemExit('Missing, extra or incorrectly numbered frames')
frames = []
size = 480 if name == 'orbit' else 600
for path in paths[::2]:
    with Image.open(path) as image:
        height=round(size*image.height/image.width)
        frames.append(image.convert('RGB').resize((size, height), Image.Resampling.LANCZOS))
# Use one shared palette so the static background stays visually stable.
palette_source = Image.new('RGB', (size * 3, height))
for i, index in enumerate((0, len(frames)//2, len(frames)-1)):
    palette_source.paste(frames[index], (i * size, 0))
palette = palette_source.quantize(colors=128)
frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
# GIF stores durations in centiseconds. Alternate 80/80/90 ms for 12 fps.
frames[0].save(project / 'animations' / f'{name}.gif', save_all=True,
               append_images=frames[1:], duration=[80, 80, 90] * (len(frames)//3),
               loop=0, optimize=True, disposal=1)
