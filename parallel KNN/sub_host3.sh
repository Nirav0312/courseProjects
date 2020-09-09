
#! /bin/bash
#PBS -N job_host3
#PBS -q courses
#PBS -l nodes=3:ppn=4
#PBS -l walltime=01:59:59
#merge output and error into a single job_name.number_of_job_in_queue.
#PBS -j oe
#export fabric infiniband related variables
export I_MPI_FABRICS=shm:tmi
export I_MPI_DEVICE=rdma:OpenIB-cma
#change directory to where the job has been submitted from
cd $PBS_O_WORKDIR
#source paths
source /opt/software/intel17_update4/initpaths intel64
#sort hostnames
sort $PBS_NODEFILE > hostfile
#run the job on required number of cores

filenamecsv="./hpc/data2/data2_host3.csv"
touch $filenamecsv
truncate -s 0 $filenamecsv
for (( i = 8; i <= 10; i++ ))
do
    for (( j = 1; j <= 5; j++ ))
    do
        filename="./hpc/data2/output_"$i".txt"
        touch $filename
        truncate -s 0 $filename

        # ./x no_of_timestep max_no_of_points max_no_of_clusters data_file_path write_cluster_file_path write_csv_file_path
        mpirun -machinefile hostfile -np $i ./src.x 16 1640000 100 "./data2/" $filename $filenamecsv

    done
done


filenamecsv="./hpc/data1/data1_host3.csv"
touch $filenamecsv
truncate -s 0 $filenamecsv
for (( i = 8; i <= 10; i++ ))
do
    for (( j = 1; j <= 5; j++ ))
    do
        filename="./hpc/data1/output_"$i".txt"
        touch $filename
        truncate -s 0 $filename

        # ./x no_of_timestep max_no_of_points max_no_of_clusters data_file_path write_cluster_file_path write_csv_file_path
        mpirun -machinefile hostfile -np $i ./src.x 17 65000 100 "./data1/" $filename $filenamecsv

    done
done
