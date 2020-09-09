import numpy as np
import os
import shutil
import time as tm
import sys

tic = tm.perf_counter()

path = "train/"
new_path = "test/"
split_size = int(sys.argv[1])


list = os.listdir(path)
np.random.shuffle(list)

os.mkdir(new_path)

for file in list[:split_size]:
	shutil.move(path + file, new_path + file)

toc = tm.perf_counter()

print("Time taken to Split = " + str(toc - tic) + "\n")