import cv2
import numpy as np
import os
import shutil
import time as tm
from joblib import dump, load
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

dict = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19, 'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25}
dictRev = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z'}


def read_data(dir):

    X = []
    y = []

    for folder in os.listdir(dir):
        for file_name in os.listdir(dir+"/"+folder):
            img = np.array(cv2.imread(dir+"/"+folder+"/"+file_name, 0))

            X.append(img.flatten())
            y.append(dict[folder])

    return X, y


if __name__ == "__main__":

    dir = "./Train_Data"
    # clf = load('rbf.model')

    # for i in range(26):
    X, y = read_data(dir)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.85, random_state=42)

    clf = SVC( kernel='poly')

    # print(X_train)

    clf.fit(X_train, y_train)

    dump(clf, './models/poly2.model')

    print("prediction started")

    print(len(X_test))


    tic = tm.time()

    y_hat = clf.predict(X_test)

    toc = tm.time()


    acc = accuracy_score(y_test, y_hat)


    print(acc, toc-tic)

    # if acc != 1:
    #     print(dictRev[i] , acc)





