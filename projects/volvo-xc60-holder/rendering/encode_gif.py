"""Create the 12 fps README preview. Requires Pillow. Run after rendering."""
from pathlib import Path
from PIL import Image

project = Path(__file__).resolve().parents[1]
paths = sorted((project / 'generated/frames').glob('*.png'))
if len(paths) != 144:
    raise SystemExit(f'Expected 144 frames, found {len(paths)}')
frames = []
for path in paths[::2]:
    with Image.open(path) as image:
        frames.append(image.convert('RGB').resize((600, 600), Image.Resampling.LANCZOS))
# Use one shared palette so the static background stays visually stable.
palette_source = Image.new('RGB', (600 * 3, 600))
for i, index in enumerate((0, 36, 71)):
    palette_source.paste(frames[index], (i * 600, 0))
palette = palette_source.quantize(colors=128)
frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
# GIF stores durations in centiseconds. Alternate 80/80/90 ms for 6 seconds.
frames[0].save(project / 'animations/assembly.gif', save_all=True,
               append_images=frames[1:], duration=[80, 80, 90] * 24,
               loop=0, optimize=True, disposal=1)
