#!/bin/bash
arr=()
FILE=ipaddresses     
if [ -f $FILE ]; then
    rm $FILE
fi
prefix="172.27.19."

#for (( i=3; i<=100; i++ ))
j=0
for i in 6 7 8 9 10 21 22 23 24 25 37 38 39 40 51 52 53 54 55 67 68 69 70 71 83 84 85 86 98 99 100 101 102 113 114 115 116
do
   arr[$j]="$prefix$i"
   j=`expr $j + 1`
done

j=0
#for (( i=3; i<=100; i++ ))
for i in 6 7 8 9 10 21 22 23 24 25 37 38 39 40 51 52 53 54 55 67 68 69 70 71 83 84 85 86 98 99 100 101 102 113 114 115 116
do  
    # echo $i
    command=$(ping ${arr[j]} -c 1 -w 1 | grep "100% packet loss\|Host Unreachable" | wc -l) 
    # echo "${arr[j]}"
    result=${command}
    if [ $result -eq 0 ]
    then
	echo "${arr[j]}:4" >> ipaddresses
    fi
    j=`expr $j + 1`	
done