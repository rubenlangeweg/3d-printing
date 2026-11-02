---
name: print-strength
description: Set up and verify static strength studies of 3D printed parts from Blender or STL models using VoxelSim FEA. Use for displacement, stress, load-path and geometry comparisons, including fixed supports and clip or rail mounting.
---

# Print strength

Calculate how the accepted part moves and transfers load through its mounting. Start with the actual assembly, then select the simplest support model that answers the user's question.

## Define the study

Inspect the accepted mesh, dimensions and installed orientation. Record the model hash, coordinate system, material, print orientation, load footprint, mass, gravity direction, mounting and requested comparisons. Ask only for missing information that changes the calculation. If print settings are undecided, run a clearly labelled solid-material sensitivity study and keep those assumptions visible.

Use [the Blender workflow](references/blender-workflow.md) for a fixed-support screen and viewport heatmaps. Use [mounting and numerical checks](references/mounting-and-validation.md) for rail contact, self-weight, headless solves and accepting results. Read [the Linea precedent](references/leander-linea.md) only when revisiting those accessories.

## Select the right model

- Fixed supports represent a rigid attachment. Show which translations are restrained. A larger fixed region can suppress hook bending and make the result too stiff.
- Clip, hook and rail mounting can require separating contact. Use compression-only contact when the part can lift away. Include clearance only when measured or explicitly varied.
- Include self-weight when material volume or mounting changes affect the comparison. Solve gravity separately when reporting additional movement due to contents.
- Use a finite load footprint and distribute the requested total force over it. Check the force resultant and its moment about the mounting.

Use homogeneous isotropic properties only as the stated reference model. A bulk PLA modulus does not represent sparse infill, layer strength, creep or a warped print. Do not derive a printed load rating from a red heatmap or the add-on's default yield strength.

## Tools and reproducibility

The prior studies used external VoxelSim FEA 2.5.6, commit `cc9f7b2252ceda0730f4f331408de9e6b276ddfd`. Inspect the installed version and API before running another version. The add-on and its dependencies retain their licenses and are obtained separately from [the upstream project](https://github.com/RandomLambda/VoxelSim-FEA). They are not bundled in this skill.

- [scripts/prepare_blender_study.py](scripts/prepare_blender_study.py) creates a separate, metre-coordinate Blender scene with a part, support selector meshes, a load selector and named VoxelSim properties. Run it inside Blender with the add-on enabled. It prepares a fixed-support, added-load-only study. It does not execute the modal solver or implement contact or self-weight.
- [scripts/check_solver.py](scripts/check_solver.py) checks the external solver against a two-resolution cantilever calculation. Run this before trusting a new solver environment or changing physical-unit handling.

Resolve resources relative to this skill directory. Keep working meshes, voxel caches and result arrays with a case manifest. Include source mesh hash, solver revision, physical units, resolution, loads, boundary conditions and convergence evidence in cache identity. Reuse a cached solve only when these match.

## Show and report the result

Check force and moment balance, true residual, support reactions, mesh sensitivity and a simple analytical comparison before presenting conclusions. Stop a failed solve, retain its log, identify the failed check and correct the setup before retrying. Begin coarse, then refine the cases that matter.

Show displacement in mm and stress in MPa, with a labelled colour range and any deformation magnification. Use a shared scale for comparisons. Keep numerical values visible beside heatmaps. The red end of a relative scale means the largest plotted value. State any clipped stress range and report the unclipped peak separately.

Deliver a concise result summary, setup scene, case settings, result data and requested views. Separate earlier fixed-support studies from later contact studies. Preserve source-asset rights when distributing Blender scenes. The original files in this skill are by Ruben Langeweg, with instructions under [CC BY-NC 4.0](licenses/CC-BY-NC-4.0.txt) and helper code under [MIT](licenses/MIT.txt).
