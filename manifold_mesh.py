import datetime
import os
import subprocess

import config


def makewatertight(filelist, models_dir, out_dir):
    """
    runs ManifoldPlus (https://github.com/hjwdzh/ManifoldPlus) to convert meshes to watertight meshes
    :param filelist: list of name of the files (not full path) e.g. [file0.obj, file1.obj]
    :param models_dir: path to directory of model meshes
    :param out_dir: path to out directory where watertight meshes as stored
    :return:
    """
    # create out directory if it doesn't exist yet
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    # open fail file with append mode to add files of meshes that were not converted successfully
    fail_file = open("errors_run.txt", mode="a")
    fail_file.write("====run of " + datetime.datetime.now().strftime('%m-%d-%H:%M:%S') + "====")
    # iterate over whole filelist and try to convert the mesh
    number_items = len(filelist)
    for i, file in enumerate(filelist):
            print(str(i) + "/" + str(number_items))
            try:
                subprocess.run(["/local/home/sbeetschen/Documents/code/ManifoldPlus/build/manifold", "--input",
                                os.path.join(models_dir, file),
                                "--output",
                                os.path.join(out_dir, file)],
                               check=True)
            except Exception as e:
                print(e)
                fail_file.write(datetime.datetime.now().strftime('%m-%d-%H:%M:%S') + " " + str(file) + "\n")
    fail_file.close()


if __name__ == "__main__":
    # runs ManifoldPLus to convert ShapeNetSem.obj files to watertight meshes
    # makes use of: https://github.com/hjwdzh/ManifoldPlus
    models_dir = os.path.join(config.SHAPENETSEM_ROOT, "models")
    out_dir = os.path.join(config.SHAPENETSEM_ROOT, "models_watertight")
    makewatertight(os.listdir(models_dir), models_dir, out_dir)



