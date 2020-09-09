import cv2 as cv
import numpy as np
import os
import shutil
import time as tm
from sklearn.neighbors import KNeighborsClassifier

dict = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25}
dictRev = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z'}

def show(img):
	cv.imshow("Image", img)
	cv.waitKey(0)
	cv.destroyAllWindows()

def store(folder, size, filename):
	y_test = []

	files_path = [folder + "%d.png" % i for i in range(size)]

	testPoint = cv.imread(files_path[0])
	X_test = testPoint.flatten()
	y_test.append(dict[filename[0]])
	
	for i in range(1, size):
		testPoint = cv.imread(files_path[i])
		temp = testPoint.flatten()
		X_test = np.vstack((X_test, temp))
		y_test.append(dict[filename[i]])
	
	y_test = np.array(y_test)
	
	return X_test, y_test

def split_image(img, filename):
	proj = np.sum(img, axis=0)
	proj = np.clip(proj, 0, 255)

	new_proj = [proj[i]-proj[i+1] for i in range(len(proj)-1)]
	new_proj = np.array(new_proj).nonzero()[0]

	os.mkdir("runtime_data")
	path = "./runtime_data/"

	for i in range(0,len(new_proj),2):
		width = 28
		height = 28
		dim = (width, height)
		resized = cv.resize(img[:, new_proj[i]:new_proj[i+1]], dim, interpolation = cv.INTER_AREA)
		cv.imwrite(path + str(i//2) + ".png", resized)
	
	X_test, y_test = store(path, len(new_proj)//2, filename)
	
	shutil.rmtree("runtime_data")
	
	return X_test, y_test

def test(knn):
	path = "./test/"
	files = os.listdir(path)
	
	i = 0
	dilatation_size = 1
	dilatation_type = 0
	element = cv.getStructuringElement(dilatation_type, (2 * dilatation_size + 1, 2 * dilatation_size + 1), (dilatation_size, dilatation_size))
	
	for file in files:
		img_rgb = cv.imread(path + file)
		img_hsv = cv.cvtColor(img_rgb, cv.COLOR_RGB2HSV)
	
		h, s, v = cv.split(img_hsv)
		_, s_thr = cv.threshold(s, 100, 255, cv.THRESH_BINARY)
	
		img = np.bitwise_and(s_thr, v)
		non_zeros = img.nonzero()
		img_nz = img[non_zeros]
		avg = np.average(img_nz)
	
		_, pre_final = cv.threshold(img, avg, 255, cv.THRESH_BINARY)
		final = cv.erode(pre_final, element)

		X_test, y_test = split_image(final, file[:-4])
	
		knn_predictions = knn.predict(X_test)
		
		f = open("model.txt", "a")
		for j in range(knn_predictions.shape[0]):
			f.write(dictRev[knn_predictions[j]])
		f.write("\n")
		f.close()

		i += 1
		# print(str(i) + " Images predicted!!!")


def train():
	char = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

	y_train = []
	X_train = np.array([]).reshape(0, 28*28*3)

	for i in range(len(char)):
		path = "./Train_Data/" + char[i] + "/"
		files = os.listdir(path)
		if(len(files) == 0):
			continue
		img = cv.imread(path + files[0])
		x = img.flatten()
		y_train.append(i)

		for j in range(1, len(files)):
			img = cv.imread(path + files[j])
			temp = img.flatten()
			x = np.vstack((x, temp))
			y_train.append(i)
		
		# if i == 0:
		# 	X_train = x
		# else:
		# 	X_train = np.vstack((X_train, x))

		if not X_train.shape[0]:
			X_train = x
		else:
			X_train = np.vstack((X_train, x))
	
	y_train = np.array(y_train)

	knn = KNeighborsClassifier(n_neighbors = 1).fit(X_train, y_train)

	return knn

if __name__ == "__main__":
	tic = tm.perf_counter()
	knn = train()
	toc = tm.perf_counter()
	print("Time to Train the Model = " + str(toc - tic) + "\n")


	tic = tm.perf_counter()
	test(knn)
	toc = tm.perf_counter()
	print("Time for Prediction = " + str(toc - tic) + "\n")