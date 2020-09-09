import cv2
import numpy as np
import os
import time as tm
from joblib import load

dilatation_size = 1
dilatation_type = 0
element = cv2.getStructuringElement(dilatation_type, (2 * dilatation_size + 1, 2 * dilatation_size + 1),
                                       (dilatation_size, dilatation_size))

width = 20
height = 20
dim = (width, height)


def get_seperate_char(img):

    proj = np.sum(img, axis=0)
    proj = np.clip(proj, 0, 255).astype(np.int)

    new_proj = [int(proj[i]-proj[i+1]) for i in range(len(proj)-1)]
    new_proj = np.array(new_proj).nonzero()[0]

    chars = []

    for i in range(0,len(new_proj),2):
        resized = cv2.resize(img[:, new_proj[i]:new_proj[i+1]], dim, interpolation = cv2.INTER_AREA)
        chars.append(resized.flatten())

    return chars

def process_image(img_rgb):

    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(img_hsv)
    _, s_thr = cv2.threshold(s, 100, 255, cv2.THRESH_BINARY)


    cv2.imshow("s_thr",s_thr)
    img = np.bitwise_and(s_thr, v)
    cv2.imshow("anded",img)


    cv2.waitKey(0)
    non_zeros = img.nonzero()
    img_nz = img[non_zeros]
    avg = np.average(img_nz)
    _, pre_final = cv2.threshold(img, avg, 255, cv2.THRESH_BINARY)
    final = cv2.erode(pre_final, element)

    return final

def predict_char(model, chars):
    yhat = model.predict(chars)
    yhat = [chr(num+65)for num in yhat]
    return yhat


if __name__ == "__main__":

    images_dir = "../train"
    model = load('./models/poly2.model')

    test_images_name = os.listdir(images_dir)

    tic = tm.time()

    for img_name in test_images_name:

        img = cv2.imread(images_dir + "/" + img_name)

        th_img = process_image(img)
        chars = get_seperate_char(th_img)

        y_pred = predict_char(model, chars)

        s = str()
        s = s.join(y_pred)

        if(s != img_name.split(".")[0]):
            print(img_name)

    toc = tm.time()

    print("prediction time: ", toc-tic)