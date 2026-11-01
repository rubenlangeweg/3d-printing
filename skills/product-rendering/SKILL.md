---
name: product-rendering
description: Create or refine product images and short camera animations from approved 3D models in Blender, with warm minimal styling, reproducible lighting and checked video exports. Use for STL, CAD or Blender product presentation work.
---

# Product rendering

Make the approved model look clear, tactile and credible. Use the existing design and assembly as the source of truth.

## Start from the actual product

Inspect the model, units, assembly and existing media before changing the scene. Identify the accepted print file and preserve its geometry and mounting transforms. Save render work to a separate scene. A render request does not authorize redesigning the print model or publishing files.

Use the user's visual direction. If none is given, start with warm matte materials, soft light, a quiet background and a slow camera move. For accessories, use the real host or assembly when that context matters. Keep contact points visible and props relevant to the product.

For Leander Linea work, read [the project notes](references/leander-linea.md). That project requires the actual table in every product image and animation. Its exact lighting and motion recipe is included, without the licensed furniture asset.

## Build and check the scene

Read [the rendering workflow](references/workflow.md) for setup, copyable commands and export checks. Use the parts relevant to the request; a still does not need an animation pipeline.

- Match material, light and camera scale to the model's coordinates. Blender's unit display alone does not rescale a scene.
- Keep the original mesh. Rounded appearance should come from the approved geometry and lighting, not added render-only geometry that misrepresents the print.
- Preview the main shot before a full render. For animation, check the first, middle and last frames plus any low-angle section.
- Keep previews and complete frame sequences in separate directories. Check decoded video as well as source frames.

## Included tools

Resolve paths relative to this skill folder, not the current working directory. The helper scripts were tested with Blender 5.0.1 and macOS Swift/AVFoundation.

- [scripts/apply_style.py](scripts/apply_style.py) applies a named palette to explicitly selected Principled materials and saves a new `.blend`. Keep its adjacent `presets/` directory intact. It preserves geometry, transforms, cameras and lights. World changes require `--world`; contrast, exposure and lighting are separate.
- [scripts/encode_mp4.swift](scripts/encode_mp4.swift) encodes numbered PNG/JPEG frames to H.264 on macOS and fully decodes the result to verify frame count and duration. On other systems, use an available encoder with equivalent checks. Do not install one solely because this script is macOS-specific.

## Deliver the useful files

Provide the requested stills or video, the permitted editable scene, and enough settings to repeat the work. Keep frame sequences and verification reports local unless requested. Reports can contain absolute file paths.

Check asset rights before distributing source scenes. Hiding a reference object does not remove its mesh or packed textures. Keep restricted reference geometry and textures local; follow their terms for finished images and videos. Obtain missing assets separately when needed rather than substituting a different product without agreement.

This skill comes from [rubenlangeweg/3d-printing](https://github.com/rubenlangeweg/3d-printing). Copyright 2026 Ruben Langeweg. Instructions and the Linea recipe use [CC BY-NC 4.0](licenses/CC-BY-NC-4.0.txt); scripts and material presets use [MIT](licenses/MIT.txt). These licenses grant no rights to third-party reference models.
