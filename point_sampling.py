import glob
import os

import h5py
import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d
import trimesh

import binvox_rw
import config


def plot_voxels(voxel_matrix):
    """
    plot voxels with matplotlib
    :param voxel_matrix: voxel grid as matrix form
    :return:
    """
    fig = plt.figure()
    ax = fig.gca(projection="3d")
    ax.voxels(voxel_matrix)
    plt.show()


def sample_uniform_points(number_points, seed=None):
    """
    samples randomly points in the cube within [-0.5, 0.5]^3
    :param number_points: number of points to be sampled
    :param seed: random seed
    :return: numpy list in shape (number_points, 4) where the forth coordinate is 1
    """
    np.random.seed(seed)
    points = np.random.uniform(-0.5, 0.5, (number_points, 4))
    points[:, 3] = 1
    return points


if __name__ == "__main__":
    number_points = 4096
    visualization = False
    dataset_name = "shapenetsem_train"

    data_voxels_list = []
    data_points_list = []
    data_values_list = []
    text_file = open(os.path.join("out", dataset_name + ".txt"), "w")
    voxel_files_path = np.asarray(glob.glob(os.path.join(*[config.SHAPENETSEM_ROOT, "models_voxelized", "*.binvox"])))
    voxel_files_path = voxel_files_path[0: int(0.8*len(voxel_files_path))]#[15, 16, 17, 20]]#int(0.8*len(voxel_files_path))]0, 1, 2, 5, 6, 7, 8, 9, 10, 11, 12,
    for i, voxel_file_path in enumerate(voxel_files_path):
        try:
            # load voxelized model
            with open(voxel_file_path, "rb") as f:
                voxels = binvox_rw.read_as_3d_array(f)
            data_voxels_list.append(voxels.data)

            object_id = voxel_file_path.split("/")[-1].split(".")[0]
            # write object id to textfile
            text_file.write(object_id + "\n")
            mesh_o3d = o3d.io.read_triangle_mesh(
                os.path.join(*[config.SHAPENETSEM_ROOT, "models_wdensity_watertight", object_id + ".obj"]))
            mesh_trimesh = trimesh.load_mesh(
                os.path.join(*[config.SHAPENETSEM_ROOT, "models_wdensity_watertight", object_id + ".obj"]),
                process=False)
            data_points = sample_uniform_points(number_points)
            data_points_list.append(data_points)
            if visualization:
                # plot voxels
                plot_voxels(voxels.data)
                mesh_o3d.compute_vertex_normals()
                # create 1,1,1 box
                cube = o3d.geometry.TriangleMesh.create_box()
                # move center of it to the origin so that box is from [-0.5, 0.5]^3
                cube.translate(-cube.get_center())
                unit_box = cube.get_axis_aligned_bounding_box()
                origin = o3d.geometry.TriangleMesh.create_coordinate_frame()
                # sampled pointcloud for visualization
                pc = o3d.geometry.PointCloud()
                pc.points = o3d.utility.Vector3dVector(data_points[:, 0:3])
                pc.paint_uniform_color([0, 0, 0])
                colors = np.asarray(pc.colors)

            # get axis aligned bounding box
            bbox = mesh_o3d.get_axis_aligned_bounding_box()
            # scale mesh down to unit bounding box
            mesh_o3d.scale(1 / bbox.get_max_extent(), mesh_o3d.get_center())
            # move it to origin
            mesh_o3d.translate(-mesh_o3d.get_axis_aligned_bounding_box().get_center())

            # scale it down
            max_extent = np.max(mesh_trimesh.extents)
            mesh_trimesh.apply_scale(1 / max_extent)
            # center it at origin
            # mesh_trimesh.apply_transform(mesh_trimesh.apply_obb())
            mesh_trimesh.apply_translation(-mesh_trimesh.bounding_box.center_mass)

            cube = o3d.geometry.TriangleMesh.create_box()
            # move center of it to the origin so that box is from [-0.5, 0.5]^3
            cube.translate(-cube.get_center())
            unit_box_trimesh = trimesh.Trimesh(np.asarray(cube.vertices), np.asarray(cube.triangles),
                                               vertex_normals=np.asarray(cube.vertex_normals))
            # trimesh.scene.Scene([mesh_trimesh, mesh_trimesh.bounding_box, unit_box_trimesh.bounding_box]).show()

            # calculate signed distance function for all sampled points
            mesh_trimesh2 = trimesh.Trimesh(np.asarray(mesh_o3d.vertices), np.asarray(mesh_o3d.triangles),
                                            vertex_normals=np.asarray(mesh_o3d.vertex_normals))
            sdf = trimesh.proximity.signed_distance(mesh_trimesh, data_points[:, 0:3])

            data_values = []
            number_sampled_points_inside = 0
            for j, sdf_value in enumerate(sdf):
                if sdf_value > 0:
                    data_values.append([1])
                    number_sampled_points_inside += 1
                    if visualization:
                        colors[j] = [1, 0, 0]
                else:
                    data_values.append([0])
            data_values_list.append(data_values)

            print(str(i) + "/" + str(len(voxel_files_path)) + " " + object_id + " sampled points inside: " + str(
                number_sampled_points_inside))

            if visualization:
                pc.colors = o3d.utility.Vector3dVector(colors)
                o3d.visualization.draw_geometries([origin, unit_box, pc])
        except Exception as e:
            print(str(i) + "/" + str(len(voxel_files_path)) + " " + object_id + " ERROR: " + str(e))

    # close text file
    text_file.close()
    # write data to hdf5 file
    number_objects = len(voxel_files_path)
    with h5py.File(os.path.join("out", dataset_name + ".hdf5"), "w") as f:
        f.create_dataset("voxels_64", (number_objects, 1, 64, 64, 64), dtype="uint8", data=np.asarray([data_voxels_list]))
        f.create_dataset("points_16", (number_objects, number_points, 4), dtype="float32", data=np.asarray(data_points_list))
        f.create_dataset("values_16", (number_objects, number_points, 1), dtype="float32", data=np.asarray(data_values_list))
