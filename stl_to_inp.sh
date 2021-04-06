#!/bin/bash

printf "Merge '$1';\nSurface Loop(1) = {1};\nVolume(1) = {1};" >$1.temp.geo
gmsh $1.temp.geo -3 -o $1.msh -format msh2
rm $1.temp.geo
./gmshtoucd.py $1.msh
rm $1.msh
name=${1%%.*}
mv $1.inp $name.inp
