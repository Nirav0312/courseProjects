import os
import shutil
import time as tm

tic = tm.perf_counter()
os.remove("codes.txt")
os.remove("model.txt")
shutil.rmtree("Train_Data")

path = "test/"
new_path = "train/"

list = os.listdir(path)

for file in list:
	shutil.move(path + file, new_path + file)

os.rmdir("test")
toc = tm.perf_counter()
print("Time to Clean the temp files = " + str(toc-tic))