#!/bin/bash

test_size="400"

#Split the data according to test_size parameter
python Split.py $test_size

#Make Directory to hold Training Images
python mkdir.py

#Store the Training Images
python -W ignore genTrain.py

#Store the True-Label for Test data
python genCodes.py

#Start Prediction & Store the predicted label in model.txt
python -W ignore predict.py

#Get the metric values (as given in the Assignment Package)
python ./check/eval.py $test_size

#Restore the state of the folder
python clean.py