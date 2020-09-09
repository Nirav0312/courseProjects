import cv2
import numpy as np
import os
import time as tm

alpha = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0, 'I': 0, 'J': 0, 'K': 0, 'L': 0, 'M': 0, 'N': 0, 'O': 0, 'P': 0, 'Q': 0, 'R': 0, 'S': 0, 'T': 0, 'U': 0, 'V': 0, 'W': 0, 'X': 0,'Y': 0, 'Z': 0}

def get_count(img, filename):
    width = 20
    height = 20
    dim = (width, height)

    proj = np.sum(img, axis=0)
    proj = np.clip(proj, 0, 255)

    new_proj = [proj[i]-proj[i+1] for i in range(len(proj)-1)]
    new_proj = np.array(new_proj).nonzero()[0]

    for i in range(0,len(new_proj),2):
        resized = cv2.resize(img[:, new_proj[i]:new_proj[i+1]], dim, interpolation = cv2.INTER_AREA)
        name = filename[i//2]
        path = "./Train_data/"+name+"/"+str(alpha[name])+".png"
        alpha[name] += 1
        cv2.imwrite(path, resized)

    return len(new_proj)/2


if __name__ == "__main__":

    folder_path = "../train/"
    file_names = os.listdir(folder_path)
    
    dilatation_size = 1
    dilatation_type = 0
    element = cv2.getStructuringElement(dilatation_type, (2 * dilatation_size + 1, 2 * dilatation_size + 1),
                                       (dilatation_size, dilatation_size))
    
    # i = 0
    tic = tm.perf_counter()
    for file_name in file_names:

        img_rgb = cv2.imread(folder_path+file_name)
        img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

        h, s, v = cv2.split(img_hsv)

        _, s_thr = cv2.threshold(s, 100, 255, cv2.THRESH_BINARY)

        img = np.bitwise_and(s_thr, v)
        non_zeros = img.nonzero()
        img_nz = img[non_zeros]
        avg = np.average(img_nz)

        _, pre_final = cv2.threshold(img, avg, 255, cv2.THRESH_BINARY)

        final = cv2.erode(pre_final, element)
    
        char_count = get_count(final, file_name.split(".")[0])

        if char_count != len(file_name.split(".")[0]):
            print("----------------------" + file_name + "----------------------")

        # i += 1
        # print("Image " + str(i) + " done!!!")

    toc = tm.perf_counter()
    print("Time for storing Training Images = " + str(toc-tic) + "\n")
