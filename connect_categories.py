import csv
import json

if __name__ == "__main__":
    object_ids = []
    with open("/local/home/sbeetschen/Documents/code/BSP-NET-pytorch/data/data_per_category/03001627_chair/03001627_vox256_img_train.txt", mode="r") as f:
        for line in f:
            object_ids.append(line.split("/")[1].strip("\n"))
    print(str(len(object_ids)))

    n = 0
    matched_object_ids_dict = {"matched_object_ids": []}
    with open("metadata_full_wunit3.csv", mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for i, row in enumerate(csv_reader):
            # skip header row
            if i == 0:
                continue
            full_id = row[0]
            if full_id in object_ids:
                print(full_id)
                matched_object_ids_dict["matched_object_ids"].append(full_id)
                n += 1
    print(n)
    with open("matched_object_ids.json", "w", encoding="utf-8") as f:
        json.dump(matched_object_ids_dict, f, ensure_ascii=False, indent=4)