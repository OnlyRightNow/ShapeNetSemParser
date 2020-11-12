import datetime
import os
import subprocess

shapenetsem_root = "/local/home/sbeetschen/Documents/data/ShapeNetSem"


def makewatertight(filelist, models_dir, out_dir):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    fail_file = open("errors.txt", mode="a")
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
    models_dir = os.path.join(shapenetsem_root, "models")
    out_dir = os.path.join(shapenetsem_root, "models_watertight")
    makewatertight(os.listdir(models_dir), models_dir, out_dir)



