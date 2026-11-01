"""Create the 12 fps README preview. Requires Pillow. Run after rendering."""
from pathlib import Path
from PIL import Image
import sys

project = Path(__file__).resolve().parents[1]
name = sys.argv[1] if len(sys.argv)>1 else 'assembly'
folder, count = {'assembly':('frames',144),'orbit':('orbit-frames',288)}[name]
paths = sorted((project / 'generated' / folder).glob('*.png'))
if len(paths) != count:
    raise SystemExit(f'Expected {count} frames, found {len(paths)}')
frames = []
size = 480 if name == 'orbit' else 600
for path in paths[::2]:
    with Image.open(path) as image:
        frames.append(image.convert('RGB').resize((size, size), Image.Resampling.LANCZOS))
# Use one shared palette so the static background stays visually stable.
palette_source = Image.new('RGB', (size * 3, size))
for i, index in enumerate((0, len(frames)//2, len(frames)-1)):
    palette_source.paste(frames[index], (i * size, 0))
palette = palette_source.quantize(colors=128)
frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
# GIF stores durations in centiseconds. Alternate 80/80/90 ms for 12 fps.
frames[0].save(project / 'animations' / f'{name}.gif', save_all=True,
               append_images=frames[1:], duration=[80, 80, 90] * (len(frames)//3),
               loop=0, optimize=True, disposal=1)
