import csv
import datetime
import os

import trimesh

import config
from shapenetsemObject import ShapeNetSemObject

if __name__ == "__main__":
    # file_dir = os.path.join(config.SHAPENETSEM_ROOT, "metadata.csv")
    models_dir = os.path.join(config.SHAPENETSEM_ROOT, "models")
    models_watertight_dir = os.path.join(config.SHAPENETSEM_ROOT, "models_wdensity_watertight")

    fail_file = open("errors.txt", mode="a")
    fail_file.write("====main.py run of " + datetime.datetime.now().strftime('%m-%d-%H:%M:%S') + "====\n")

    objects = []
    with open(os.path.join(config.SHAPENETSEM_ROOT, "metadata.csv"), mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for i, row in enumerate(csv_reader):
            # skip header row
            if i == 0:
                continue
            object = ShapeNetSemObject(row[0].split(".")[1], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[14], row[15])
            objects.append(object)
    print("number of objects: " + str(len(objects)))

    densities_dict = {}
    with open(os.path.join(config.SHAPENETSEM_ROOT, "densities.csv"), mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for i, row in enumerate(csv_reader):
            # skip header row
            if i == 0:
                continue
            # get density in SI units (kg/m^3)
            densities_dict[row[0]] = float(row[1]) * 1000

    categories_density_dict = {}
    with open(os.path.join(config.SHAPENETSEM_ROOT, "materials.csv"), mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for i, row in enumerate(csv_reader):
            # skip header row
            if i == 0:
                continue
            category = row[0]
            material = row[1]
            fraction = float(row[2])
            if category in categories_density_dict:
                categories_density_dict[category] = categories_density_dict[category] + densities_dict[material]*fraction
            else:
                categories_density_dict[category] = densities_dict[material]*fraction
    print("number of categories with density: " + str(len(categories_density_dict)))

    synset_categories_density_dict = {}
    synset_categories_names = {}
    with open(os.path.join(config.SHAPENETSEM_ROOT, "categories.synset.csv"), mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for i, row in enumerate(csv_reader):
            # skip header row
            if i == 0:
                continue
            category = row[0]
            synset_cat = row[2]
            if category in categories_density_dict:
                synset_categories_density_dict[synset_cat] = categories_density_dict[category]
            synset_categories_names[synset_cat] = category
    print("number of synset categories with density: " + str(len(synset_categories_density_dict)))
    objects_w_density = []
    for object in objects:
        if object.wnsynset in synset_categories_density_dict:
            object.density = synset_categories_density_dict[object.wnsynset]
            objects_w_density.append(object)
    print("number of objects with density: " + str(len(objects_w_density)))

    with open("metadata_full_wunit3_tmp.csv", mode="w") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",")
        csv_writer.writerow(["full_id", "category", "wnsynset", "synset category name", "wnlemmas", "up", "front", "unit", "aligned.dims", "volume[m^3]",
                             "average density[kg/m^3]", "mass[kg]", "name", "tags"])
        filenames = []
        list = objects_w_density
        full_objects = []
        for i, object in enumerate(list):
            print(str(i) + "/" + str(len(list)))
            filename = object.full_id + ".obj"
            filenames.append(filename)
            try:
                mesh = trimesh.load(os.path.join(models_watertight_dir, filename), process=False, force="mesh")
            except Exception as e:
                # if there was a problem reading the mesh file, then it was probably not possible to calculate
                # the watertight mesh correctly. So skip this object
                print(e)
                continue
            if object.unit != "":
                mesh.apply_scale(float(object.unit))
            else:
                print("object without unit")
                continue
            volume = mesh.volume
            object.volume = volume
            mass = volume * object.density
            object.mass = mass
            # if the mass of the object is 0 or lower, something went wrong
            if mass <= 0:
                fail_file.write(datetime.datetime.now().strftime('%m-%d-%H:%M:%S') + " " + str(filename) +
                                " has mass value: " + str(mass) + "\n")
                print("error: file " + filename + " has mass: " + str(mass))
                continue
            full_objects.append(object)
            csv_writer.writerow([object.full_id, object.category, object.wnsynset, synset_categories_names[object.wnsynset], object.wnlemmas, object.up, object.front, object.unit,
                                 object.aligned_dims, object.volume, object.density, object.mass, object.name, object.tags])

    fail_file.close()
    print("number of final objects: ", str(len(full_objects)))


    # manifold_mesh.makewatertight(ids, models_dir, out_dir)

