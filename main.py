import csv
import os

import config
import manifold_mesh
from shapenetsemObject import ShapeNetSemObject

if __name__ == "__main__":
    file_dir = os.path.join(config.SHAPENETSEM_ROOT, "metadata.csv")

    objects = []
    with open(os.path.join(config.SHAPENETSEM_ROOT, "metadata.csv"), mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for i, row in enumerate(csv_reader):
            # skip header row
            if i == 0:
                continue
            object = ShapeNetSemObject(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[14], row[15])
            objects.append(object)
    print("number of objects: " + str(len(objects)))

    densities_dict = {}
    with open(os.path.join(config.SHAPENETSEM_ROOT, "densities.csv"), mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for i, row in enumerate(csv_reader):
            # skip header row
            if i == 0:
                continue
            densities_dict[row[0]] = float(row[1])

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
    print("number of synset categories with density: " + str(len(synset_categories_density_dict)))
    objects_w_density = []
    for object in objects:
        if object.wnsynset in synset_categories_density_dict:
            object.density = synset_categories_density_dict[object.wnsynset]
            objects_w_density.append(object)
    print("number of objects with density: " + str(len(objects_w_density)))

    # filenames = []
    # for object in objects_w_density:
    #     full_id_string = object.full_id
    #     filename = full_id_string.split(".")[1] + ".obj"
    #     filenames.append(filename)
    # print("ids length: ", str(len(filenames)))

    # models_dir = os.path.join(config.SHAPENETSEM_ROOT, "models")
    # out_dir = os.path.join(config.SHAPENETSEM_ROOT, "models_wdensity_watertight")
    # manifold_mesh.makewatertight(ids, models_dir, out_dir)

