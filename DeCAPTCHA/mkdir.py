import os
import time as tm

tic = tm.perf_counter()

os.mkdir("Train_Data")

alpha = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X','Y', 'Z']

for char in alpha:
	os.mkdir("./Train_Data/" + char)

toc = tm.perf_counter()
print("Time to Make Empty Directory Structure = " + str(toc-tic) + "\n")