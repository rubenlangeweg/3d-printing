# Strength studies

These results compare small static loads under stated assumptions. They do not establish a safe load for a printed accessory.

## View the results

Open these pages in a browser after cloning or downloading the repository. They load bundled data locally, with no server or external libraries.

| Study | Versions and assumptions | Controls |
| --- | --- | --- |
| [Latest shelf comparison](shelf/index.html) | V3 and selected V4, snug rail contact with self-weight | 300 g or 2 kg summary charts |
| [Earlier shelf 3D study](shelf/earlier/index.html) | V2 and V3, fixed bonded mount, added load only | Rotate, material stiffness, load position, movement, stress and magnification |
| [Organizer 3D study](organizer/index.html) | Original organizer, fixed lip with self-weight | 300 g or 2 kg, rotate, movement and stress |

The earlier shelf page also includes the separate V3 contact mounting table and a load-transfer diagram. Its top controls do not change that table. There is no V4 interactive 3D heatmap in this package. Red in a heatmap marks the upper end of the selected colour scale, not failure.

Full results are in [organizer/results.json](organizer/results.json) and [shelf-v3-v4-comparison.json](shelf-v3-v4-comparison.json). The numerical fields are copied from the original studies without new solves or changes.

The earlier shelf data is preserved in [earlier/results.json](shelf/earlier/results.json), [mount-results.json](shelf/earlier/mount-results.json) and [mount-context.json](shelf/earlier/mount-context.json). The 1 mm V2/V3 heatmaps scale verified linear solutions for the selected force and uniform material stiffness. They exclude shelf self-weight and model a bonded backplate, so their movement values differ from the later contact studies.

## Shelf mounting

The shelf comparison uses a rigid 13 mm rail tilted 26° from vertical. Contact can carry compression, with no friction or adhesion. The clip can separate from the rail where contact pressure drops to zero. Self-weight is included.

This represents how force passes through the shelf and clip into a snug rail. It does not model clearance, wood flexibility, the table joints or the floor. The 13 mm opening was retained because the printed fit was reported as good; the downloaded table mesh was not used as a thickness measurement.

| Added load | V3 front | V4 front | V3 corner | V4 corner |
| --- | ---: | ---: | ---: | ---: |
| 300 g | 0.071 mm | 0.103 mm | 0.099 mm | 0.142 mm |
| 2 kg | 0.406 mm | 0.582 mm | 0.600 mm | 0.856 mm |

Values are maximum movement including self-weight. The matched comparison uses 2 mm voxels. V4 has about 2.65% less solid volume and about 43% more movement than V3 in these cases. A separate finer-grid check was performed for V3, but not for V4. The reduced volume is not a prediction of sliced filament use.

## Organizer mounting

The organizer's top lip is held fixed in every direction. The body is rotated into its mounted orientation. A distributed load on the inner floor represents low contents, including imposed floor shear with no sliding. Self-weight is included.

The final viewer uses 1 mm voxels. Maximum total movement is about 0.150 mm with 300 g of contents and 0.250 mm with 2 kg. Refining the mesh from 1.25 mm to 1 mm changed those maxima by about 3–6%. Thin-wall stress peaks remain sensitive to the mesh.

This fixed lip can be stiffer than the actual attachment. It does not simulate the shelf's separate rail contact, a tall bottle pushing against a wall or loose contents sliding. The two studies cannot be compared as load ratings.

## Material and solver

Both studies use solid, homogeneous, isotropic PLA with E = 2.06 GPa, ν = 0.35 and density 1,240 kg/m³. The reference is the [Bambu PLA Basic technical data sheet](https://store.bblcdn.com/s7/default/b189de92249a4b9ebed28b8ea1f080f0/Bambu_PLA_Basic_Technical_Data_Sheet.pdf). Its specimens used 100% infill and were annealed and dried at 55 °C for eight hours. These values do not represent every PLA print.

Print orientation, layer bonding, infill, creep, fracture, impact and wood movement are absent. Physical testing is needed before assigning a capacity.

The solver was [VoxelSim FEA 2.5.6](https://github.com/RandomLambda/VoxelSim-FEA), pinned to commit [`cc9f7b2252ceda0730f4f331408de9e6b276ddfd`](https://github.com/RandomLambda/VoxelSim-FEA/tree/cc9f7b2252ceda0730f4f331408de9e6b276ddfd), using fully integrated Hex8 linear elasticity. This folder contains the results and local viewer, not a solver installation. Solver code, third-party dependencies and raw calculation caches are not bundled.
