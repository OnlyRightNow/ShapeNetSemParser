# ShapeNetSem Parser
Loads the different files, parses them, calculates watertight meshes, volume, density and mass.

## Dependencies
- [Trimesh](https://github.com/mikedh/trimesh)
- [ManifoldPlus](https://github.com/hjwdzh/ManifoldPlus) (needs to be installed from [GitHub](https://github.com/hjwdzh/ManifoldPlus))

To directly create a new environment with the required packages run (ManifoldPlus still needs to be installed separately):
```
conda env create -f conda_env.yml
```