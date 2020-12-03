import numpy as np
import binvox_rw
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import is_inside_mesh
import open3d as o3d
import trimesh


def plot_voxels(voxel_matrix):
    fig = plt.figure()
    ax = fig.gca(projection="3d")
    ax.voxels(voxel_matrix)
    plt.show()


def sample_uniform_points(number_points):
    """
    samples randomly points in the cube within [-0.5, 0.5]^3
    :param number_points: number of points to be sampled
    :return: numpy list in shape (number_points, 4) where the forth coordinate is 1
    """
    points = np.random.uniform(-0.5, 0.5, (number_points, 4))
    points[:, 3] = 1
    return points


if __name__ == "__main__":
    number_points = 4096
    data_points = sample_uniform_points(number_points)
    # load voxelized model
    with open("models/non-solid/1022fe7dd03f6a4d4d5ad9f13ac9f4e7.obj_64.binvox", "rb") as f:
        model = binvox_rw.read_as_3d_array(f)
    # plot voxels
    plot_voxels(model.data)

    mesh_o3d = o3d.io.read_triangle_mesh("models/non-solid/1022fe7dd03f6a4d4d5ad9f13ac9f4e7.obj")
    mesh_o3d.compute_vertex_normals()
    # mesh_trimesh = trimesh.load_mesh("models/1022fe7dd03f6a4d4d5ad9f13ac9f4e7.obj")
    # create 1,1,1 box
    cube = o3d.geometry.TriangleMesh.create_box()
    # move center of it to the origin so that box is from [-0.5, 0.5]^3
    cube.translate(-cube.get_center())
    unit_box = cube.get_axis_aligned_bounding_box()
    origin = o3d.geometry.TriangleMesh.create_coordinate_frame()
    # get axis aligned bounding box
    bbox = mesh_o3d.get_axis_aligned_bounding_box()
    # scale mesh down to unit bounding box
    mesh_o3d.scale(1/bbox.get_max_extent(), mesh_o3d.get_center())
    # move it to origin
    mesh_o3d.translate(-mesh_o3d.get_axis_aligned_bounding_box().get_center())
    # calculate signed distance function for all sampled points
    mesh_trimesh = trimesh.Trimesh(np.asarray(mesh_o3d.vertices), np.asarray(mesh_o3d.triangles), vertex_normals=np.asarray(mesh_o3d.vertex_normals))
    sdf = trimesh.proximity.signed_distance(mesh_trimesh, data_points[:, 0:3])

    # sampled pointcloud for visualization
    pc = o3d.geometry.PointCloud()
    pc.points = o3d.utility.Vector3dVector(data_points[:, 0:3])

    pc.paint_uniform_color([0, 0, 0])
    colors = np.asarray(pc.colors)
    number_sampled_points_inside = 0
    data_values = []
    for i, sdf_value in enumerate(sdf):
        if sdf_value > 0:
            colors[i] = [1, 0, 0]
            number_sampled_points_inside += 1
            data_values.append(1)
        else:
            data_values.append(0)

    pc.colors = o3d.utility.Vector3dVector(colors)

    print("number sampled points inside: ", number_sampled_points_inside)

    o3d.visualization.draw_geometries([origin, unit_box, pc])