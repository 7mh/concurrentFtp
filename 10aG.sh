#!/bin/bash
if [ -d  "./sourceG" ]
then
    echo "10 Gb data dir Exists !!!!!!!"
else
    echo "Creating ./sourceG folder"
    mkdir sourceG
fi

cd sourceG
for ((i=1; i<=10; i++ ))
do
    yes FOR THE LOVE OF PHYSICS | head -c 1G > ${i}G

done

