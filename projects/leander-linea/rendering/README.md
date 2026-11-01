# Render the accessories on the Linea

All product images and animations show the accessories mounted on the Leander Linea table. The full-table hero gives the context; closer shelf and organizer views show their position and mounting details.

The [local gallery](../index.html) brings the three clips together. The sequences use 24 fps and no audio.

All three clips were fully decoded and their first, middle and last frames visually checked. [Media checks](media-checks.json) records the output hashes, frame counts and dimensions. The accepted print meshes are unchanged.

| Clip | Frames | Duration |
| --- | ---: | ---: |
| [Shelf on the Linea](../animations/shelf-v4.mp4) | 144 | 6 seconds |
| [Organizer on the Linea](../animations/organizer.mp4) | 144 | 6 seconds |
| [Both accessories on the Linea](../animations/combination.mp4) | 192 | 8 seconds |

## Scene files

Complete Blender scenes are saved locally. They contain the [Linea table asset by Shopot on 3dsky](https://3dsky.org/3dmodels/show/pielienal_nyi_stolik_i_komod_ot_leander), whose redistribution terms prevent including its 3D geometry and textures here. The repository contains the finished images and videos, our editable accessory meshes, model generators and shared styling tools.

To assemble a matching scene, obtain the table asset separately under its licence and combine it locally with the [accepted accessory models](../models/). Keep the full scene outside the public repository. Use the actual table for both the full view and detail shots.

## Style and output

Use Blender 5.0 and the [shared warm ivory preset](../../../rendering/README.md) as a starting point. Apply material changes to the accessories while keeping their mounting position and geometry unchanged. The table lighting and materials remain part of the local scene.

Render a still first to check the visible table, mounting position, framing and shadows. Then render the camera sequence and encode it as H.264 at 24 fps. Keep numbered frame sequences and scene copies local; share only the finished media and source files that may be redistributed.
