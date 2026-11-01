# Rendering

Start with [Make product renders and animations](../docs/product-renders-and-animations.md). It covers scene preparation, soft lighting, materials, camera moves, previews and video export using the settings from the finished Linea media.

The portable [Codex skill](../skills/product-rendering/SKILL.md) bundles copies of `apply_style.py`, `encode_mp4.swift`, `presets/*.json` and the Linea `scene-recipe.json`. Keep those copies in sync when updating the shared files. Keep `presets/` beside the bundled style script so it also works outside this repository.

The shared presets change named product materials while preserving geometry and camera motion. Complete Leander scenes stay local because they contain the licensed Linea table model. The public gallery contains the finished mounted views.

## Styles

| Preset | Use |
| --- | --- |
| `warm-ivory` | Soft ivory accessories with warm neutral surroundings |
| `neutral-technical` | Neutral satin material for geometry comparisons |
| `black` | Black satin plastic, used for the Volvo XC60 holder |
| `graphite` | Satin graphite holder on a warm grey ground |

Presets use Blender linear RGB input values and AgX. Lighting, exposure and scale still affect the result. Keep the actual host product visible in published accessory images and animations.

## Apply a style locally

Use Blender 5.0. From the repository root, replace the example scene paths and material name with those from your local scene:

```sh
blender -b /path/to/linea-scene.blend \
  --python rendering/apply_style.py -- \
  --preset warm-ivory \
  --material 'Accessory material name' \
  --output /path/to/linea-styled.blend
```

Repeat `--material` for more accessory materials. Add `--floor-material 'Material name'` for the floor and `--world` for the background. The script saves a new scene and refuses to overwrite its input or an existing output.

Render the styled scene directly:

```sh
blender -b /path/to/linea-styled.blend -o //rendered-frames/ -F PNG -a
```

Check a still before rendering the sequence. The [Linea rendering notes](../projects/leander-linea/rendering/README.md) list the clip lengths and original table asset.

## Encode on macOS

The shared [Swift encoder](encode_mp4.swift) reads numbered JPEG or PNG frames and writes H.264 at the specified frame rate, without audio. It verifies the decoded frame count and duration. For a six-second clip at 24 fps:

```sh
swift rendering/encode_mp4.swift /path/to/rendered-frames /path/to/shelf-v4.mp4 144 24
```

Use 144 frames for the shelf and organizer clips, or 192 for the eight-second combination. Keep the frame directory and output video outside the repository while working. The encoder preserves an existing video and writes validation details beside the frame directory.

Add a fifth numeric argument for the target bitrate in Mbps. The default is `8`; the final organizer clip used `20` to retain fine wood texture. For example: `swift rendering/encode_mp4.swift /path/to/frames /path/to/organizer.mp4 144 24 20`.

## Keep reference scenes local

Publish only source files whose redistribution is allowed. A hidden reference object can still leave its mesh or packed textures in a saved Blender file. Keep restricted furniture assets and complete scenes outside the public repository, even when finished images and videos may be shared. Credit the asset creator in the project notes.
