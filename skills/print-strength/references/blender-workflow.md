# Fixed-support studies in Blender

## Environment

Use the external [VoxelSim FEA](https://github.com/RandomLambda/VoxelSim-FEA) extension. The original studies used version 2.5.6 at commit `cc9f7b2252ceda0730f4f331408de9e6b276ddfd` with Blender 5.0.1. Obtain it from upstream and follow its installation instructions. Confirm its registered settings before automation. In that version they are at `bpy.context.scene.blendfea`, and the sidebar is View3D, N panel, VoxelSim FEA.

The pinned implementation reads raw world coordinates as metres. It does not multiply by Blender's Unit Scale. Normalize evaluated world vertices into actual metre coordinates in an analysis copy. Setting Unit Scale without moving the coordinates does not perform this conversion. A 180 mm part should span 0.18 raw units in the analysis scene.

## Prepare the model

Keep the accepted mesh and its file unchanged. Inspect dimensions, watertightness, normals, separate components and minimum wall thickness. Join only geometry that is actually bonded. A disconnected island can be removed by some solver paths, so inspect and report any removed volume.

Model the part in its installed orientation, with a consistent gravity vector. For a fixed-support screen, place closed helper meshes over the real supported region and the finite load footprint. The add-on distributes force over selected nodes, so keep the load selector shallow enough to select the intended surface layer. Preview the selected nodes when precision matters. At coarse resolution a small selector can miss every node.

The helper accepts an existing scene containing mesh objects for the part, support and load region. The explicit conversion factor is metres per raw world unit. Use `0.001` only if one raw unit really represents one millimetre, or `1` for metre coordinates. The helper evaluates modifiers and writes a separate scene containing only the selected meshes. It uses all-axis fixed support and one imposed load.

```sh
STRENGTH_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/print-strength"
blender -b local/assembly.blend --python "$STRENGTH_SKILL/scripts/prepare_blender_study.py" -- \
  --part Shelf --support RailBearing --load-object FrontPatch \
  --metres-per-unit 0.001 --mass-kg 0.3 --youngs-gpa 2.06 --poisson 0.35 \
  --resolution 64 --output local/shelf-fixed-300g.blend
```

The mass is converted to total force using 9.80665 m/s². A 300 g added mass is 2.941995 N and 2 kg is 19.6133 N. The default direction is world negative Z. Pass `--direction X Y Z` for another installed orientation. The helper normalizes this direction.

Choose the material values for the actual study. The numbers above reproduce a historical reference, not a validated PLA Matte print. Yield strength defaults to zero so the setup does not assign an unsupported safety factor.

## Solve and inspect

Open the prepared file with the extension enabled. Check Part, Supports and Loads in the VoxelSim panel. Confirm that each selector intersects the intended region. Change per-axis support locks when a roller or sliding constraint is appropriate. Use the Custom material slot, verify E in GPa and Poisson ratio, and start with CPU and four threads.

Resolution is voxels along the longest edge, not voxel pitch in millimetres. Estimate pitch from the physical extent and inspect thin walls. A two-voxel wall may reproduce displacement reasonably while its stress peaks remain poorly resolved. Refine critical cases and compare movement, volume and stress away from support singularities.

Run FEA from Blender's panel. In the pinned add-on this uses `blendfea.run` with a modal UI timer. A background invocation cannot be treated as a completed solve. Wait for completion and inspect the status and log. For unattended solving, use the documented worker/core path described in [mounting and validation](mounting-and-validation.md).

Use the Displacement and Von Mises Stress views and the Results collection. Save the scene after the solve. Show a support/load view beside the heatmap. Include a legend in mm or MPa and any magnification. The add-on's viewport legend is drawn by a UI handler, so confirm it appears in the exported image or add a figure legend explicitly.

The stock fixed-support workflow applies the specified forces and does not automatically add the part's weight. Rail separation, friction and wood flexibility require a different model. Record that scope in the output.
