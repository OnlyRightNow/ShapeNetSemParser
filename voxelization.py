import glob
import os

import open3d as o3d
import numpy as np

import config

if __name__ == "__main__":
    voxel_res = 32
    meshes_dir = os.path.join(config.SHAPENETSEM_ROOT, "models_wdensity_watertight")
    out_dir = os.path.join(config.SHAPENETSEM_ROOT, "models_voxelized")
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    for i, file_path in enumerate(sorted(glob.glob(meshes_dir + "/*.obj"))[0:3]):
        print("voxelization " + str(i) + "/" + str(len(glob.glob(meshes_dir + "/*.obj")[0:3])))
        mesh = o3d.io.read_triangle_mesh(file_path)
        # fit to unit cube
        mesh.scale(1 / np.max(mesh.get_max_bound() - mesh.get_min_bound()), center=mesh.get_center())
        mesh.translate(-mesh.get_center())
        voxel_grid = o3d.geometry.VoxelGrid.create_from_triangle_mesh(mesh, voxel_size=1/voxel_res)
        o3d.io.write_voxel_grid(os.path.join(out_dir, file_path.split("/")[-1].split(".")[0] + ".ply"), voxel_grid)

