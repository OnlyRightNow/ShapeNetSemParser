#!/bin/bash
MODELS_ROOT="/media/sbeetschen/WD 1tb/data/ShapeNetSem/models_wdensity_watertight/"
OUT="/media/sbeetschen/WD 1tb/data/ShapeNetSem/models_voxelized/"
cuda_voxelizer="/local/home/sbeetschen/Documents/code/cuda_voxelizer/build/cuda_voxelizer"

echo "models root: $MODELS_ROOT"
for entry in "$MODELS_ROOT"*
do
  $cuda_voxelizer -f "$entry" -s "64" -o "binvox"
done


