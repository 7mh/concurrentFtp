#!/bin/bash
if [ -d  "../sourceComb" ]
then
    echo "Combined data dir Exists !!!!!!!"
else
    echo "Creating ../sourceComb folder"
    cur=`pwd`
    cd ..
    mkdir sourceComb
    cd sourceComb

    for ((i=1; i<=100; i++ ))
    do
        yes FOR THE LOVE OF SCIENCE | head -c 10M > ${i}M

    done
    for ((i=1; i<=10; i++ ))
    do
        yes FOR THE LOVE OF PHYSICS | head -c 1G > ${i}G

    done
    cd $cur
fi

#echo `pwd`

