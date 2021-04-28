import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # To hide tensorflow warning's
import tensorflow as tf
import matplotlib.pyplot as plt
import cv2 as cv
import pandas as pd

# Charger le dataset
# utilisation de FER-2013 comme datasets
