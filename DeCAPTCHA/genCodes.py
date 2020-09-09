import os
import time as tm

tic = tm.perf_counter()

path = "./test/"
files = os.listdir(path)

f = open("codes.txt", 'w')

for i in range(len(files)):
	curFile = files[i][:-4]
	f.write(curFile + "\n")

f.close()	

toc = tm.perf_counter()
print("Time for Storing True-Label of Test_Data = " + str(toc - tic) + "\n")