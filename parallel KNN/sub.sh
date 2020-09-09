echo "compiling file"
mpiicc -std=c99 src.c -o src.x -lm

echo "Submitting Jobs"
qsub sub_host1.sh
qsub sub_host2.sh
qsub sub_host3.sh
