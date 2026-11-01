# Holder product renders

This setup follows the repository's [product-rendering skill](../../../skills/product-rendering/SKILL.md). It uses the accepted holder assembly, black matte plastic, a warm cream ground, broad soft lighting and a slow camera move. The print geometry and seated part positions are unchanged.

The views show the holder assembly itself. They do not demonstrate vehicle fit. Mounted views still need an accurate XC60 vent or dashboard model; the rejected approximate vent is not used.

## Render from the repository

Use Blender 5.0.1. Paths resolve relative to the script, with the shared `black-warm-matte` preset loaded by default.

```sh
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- preview
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- orbit --preview-motion
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- animation --preview-motion
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- stills
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- animation
blender -b --python projects/volvo-xc60-holder/rendering/render.py -- orbit
```

Preview images stay separate from the complete sequences. Each clip has its own `generated/<clip>/previews`, `frames` and `encoded-checks` folders. Render commands replace their own previous outputs. Use `--preset /path/to/preset.json` to run outside the repository or choose another palette.

## Appearance and camera

| Setting | Value |
| --- | --- |
| Part colour | Linear RGB `(0.004, 0.004, 0.004)` |
| Part roughness / specular | `0.56` / `0.28` |
| Ground colour / roughness | `(0.72, 0.665, 0.575)` / `0.82` |
| World colour / strength | `(0.90, 0.855, 0.76)` / `0.18` |
| Colour management | AgX, Medium High Contrast, exposure `+0.2`, gamma `1.0` |
| Lighting | Three large area lights, warm key and rim, weaker fill |
| Render engine | EEVEE, ray tracing off, shadow jitter off |
| Still output | 2000 × 1500 PNG, 128 samples |
| Video output | 1280 × 960, 24 fps, 64 samples |

The script converts the source's millimetres to metres once. Its light powers are for that metre-sized scene. No bevels, displacement or extra product geometry are added. The black finish is a presentation material, not a simulation of individual print layers.

The 12-second camera arc contains 288 frames. It moves from +35° to −35° across the front, lowers slightly and tightens the framing. Position and framing follow `e = t*t*(3-2*t)` for a gentle start and finish. The assembled holder remains fixed. The rear still shows the inner root reinforcement.

The six-second assembly clip contains 144 frames. The ball module slides 42 mm down the Y axis into its accepted seated position, with a pause before and after insertion.

Both `orbit.blend` and `assembly.blend` are self-contained rendering scenes. To preserve manual scene edits, render the saved scene directly instead of rebuilding it with the script.

## Encode and check

Use the shared encoder, which is also bundled with the skill. Choose fresh video filenames because the encoder preserves existing outputs.

```sh
swift rendering/encode_mp4.swift projects/volvo-xc60-holder/generated/orbit/frames local/orbit-new.mp4 288 24 8
swift rendering/encode_mp4.swift projects/volvo-xc60-holder/generated/assembly/frames local/assembly-new.mp4 144 24 8
python3 projects/volvo-xc60-holder/rendering/encode_gif.py orbit
python3 projects/volvo-xc60-holder/rendering/encode_gif.py assembly
```

The GIF script requires Pillow and preserves the video's aspect ratio. Its previews run at 12 fps; the MP4s retain 24 fps.

Before encoding, check sequential frame names and consistent dimensions. The encoder fully decodes the result and verifies duration and frame count. Inspect the decoded first, middle and last frames and play the full clips. Keep frame sequences, scene backups and verification reports local. Publish the checked final media and permitted editable scenes.
