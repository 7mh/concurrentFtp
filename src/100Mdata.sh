#!/bin/bash
if [ -d  "../sourceM" ]
then
    echo "100 Mb data dir Exists !!!!!!!"
else
    echo "Creating ../sourceM folder"
    cur=`pwd`
    cd ..
    mkdir sourceM
    cd sourceM

    for ((i=1; i<=100; i++ ))
    do
        yes FOR THE LOVE OF SCIENCE | head -c 10M > ${i}M

    done
    cd $cur
fi

#echo `pwd`

