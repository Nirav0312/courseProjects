import numpy as np 
import matplotlib as mpl
mpl.use('agg') 
import matplotlib.pyplot as plt
import csv 
import numpy as np
import sys

def read_data(file_name):
    data_list = []
    with open(file_name,'rt')as f:
        data = csv.reader(f)
        for row in data:
            data_list.append(float(row[2]))
    
    return data_list

def get_box_plot(process_data, ax, color, label):

    # transpose data and convert it to float
    process_data = np.transpose(np.array(process_data)).astype(np.float)
    
    # get 1st column that is bandwidth and rearrange for plotting
    # 5 observations for each of 10 different data size
    # plot data

    print(process_data.shape)
    boxplot = ax.boxplot(process_data, widths = 0.2, showfliers=False, patch_artist = True)

    for patch in boxplot['boxes']:
        patch.set(facecolor=color)
    
    # connect medians of box
    x = []
    y = []
    # 5 boxes for 5 different data size
    for i in range(10):
        x.append(np.mean(boxplot['medians'][i].get_xdata()))        
        y.append(np.mean(boxplot['medians'][i].get_ydata()))        

    ax.plot(x,y,color=color, label = label)
    # ax.gca().legend(label)

if __name__ == "__main__":
    
    file_name = sys.argv[1]
    save_folder = sys.argv[2]
    repetation = int(sys.argv[3])
    no_of_processes = 10

    plotName = save_folder+'plot.png'

    data = read_data(file_name)

    # processes X repear X time(APP,AP,TT)
    data = np.array(data).reshape((no_of_processes,repetation,3))

    pre_process_time = []
    cluster_time = []
    total_time = []
    x_labels = []

    for i in range(no_of_processes):
        cluster_time.append(data[i].T[0])
        pre_process_time.append(data[i].T[1])
        total_time.append(data[i].T[2])
        x_labels.append(str(i+1))

    # get figure
    fig = plt.figure(1, figsize=(18, 12))

    # Create an axes instance
    ax = fig.add_subplot(111)

    get_box_plot(total_time,ax,'red','total time')
    get_box_plot(cluster_time,ax,'green','average process time')
    get_box_plot(pre_process_time,ax,'black','average pre process time')

    
    ax.set_xticklabels(x_labels)
    
    ax.set_ylabel('Time (seconds)')
    ax.set_xlabel('Processes')
    ax.legend(loc='upper right')

    fig.savefig(plotName, bbox_inches='tight')