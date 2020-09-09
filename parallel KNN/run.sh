echo "creating live host files"
./livehosts.sh

echo "Compiling src"
make

filenamecsv="./cse/data1/data1.csv"
touch $filenamecsv
truncate -s 0 $filenamecsv

for (( i = 1; i <= 10; i++ ))
do
    for (( j = 1; j <= 5; j++ ))
    do
        filename="./cse/data1/output_"$i".txt"
        touch $filename
        truncate -s 0 $filename

        # ./x no_of_timestep max_no_of_points max_no_of_clusters data_file_path write_cluster_file_path write_csv_file_path
        mpiexec --hostfile ipaddresses -np $i ./src.x 17 65000 100 "./data1/" $filename $filenamecsv

    done
done

# path_to_data_file, path_to_save_plot repetations
python3 plot.py ./cse/data1/data1.csv ./cse/data1/ 5



filenamecsv="./cse/data2/data2.csv"
touch $filenamecsv
truncate -s 0 $filenamecsv
for (( i = 1; i <= 10; i++ ))
do
    for (( j = 1; j <= 5; j++ ))
    do
        filename="./cse/data2/output_"$i".txt"
        touch $filename
        truncate -s 0 $filename

        # ./x no_of_timestep max_no_of_points max_no_of_clusters data_file_path write_cluster_file_path write_csv_file_path
        mpiexec --hostfile ipaddresses -np $i ./src.x 16 1640000 100 "./data2/" $filename $filenamecsv

    done
done

# path_to_data_file, path_to_save_plot repetations
python3 plot.py ./cse/data2/data2.csv ./cse/data2/ 5