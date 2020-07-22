#!/bin/bash

./100Mdata.sh
#./1Gdata.sh
#./combineData.sh

if [ -d  "./dest" ]
then
    echo "destination dir Exists !!!!!!!"
else
    echo "Creating ./dest folder"
    mkdir dest

fi

rm dest/*
echo "All data directories prepared !"

