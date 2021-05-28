# -*- coding: utf-8 -*-
"""Preprocess_BOVW.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j41580t3vfPx-rpkYTxPUE3ZKIr1HFb2

This notebook will preprocess the signature image dataset.

First, import libraries and set up environment and global variables.
"""

import cv2 as cv
#from google.colab import drive
#from google.colab.patches import cv2_imshow
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd
from os import sys

#ROOT_PATH = 'drive/My Drive/2021 Spring/CV/Final Project/sign_data/'
ROOT_PATH = '/usa/macbride/projects/cv_final/sign_data/'
MAX_WORDS = 500 # The number of "visual words" to keep in the "dictionary"
#LOAD_MAX_PCT = 0.25 # The percent of images to load and process
#LOAD_MAX = 320 # The number of images to load and process

#drive.mount('/content/drive')

"""Define functions for later use."""

def get_features(img, extractor):
  '''
  Return features (i.e. keypoints and descriptors) from an image using an extractor 
  (i.e. ORB).
  '''
  print("Getting features...")
  keypoints, descriptors = extractor.detectAndCompute(img, None)
  print("Features obtained.")
  return keypoints, descriptors

def get_freq_count(descriptors, algorithm):
  '''
  Return a frequency count for a given list of descriptors and a 
  clustering algorithm.
  '''
  freq_count = np.zeros(len(algorithm.cluster_centers_))
  clusters =  algorithm.predict(descriptors)
  for i in clusters:
      freq_count[i] += 1.0
  return freq_count

def prep_data():
  '''
  Return a list of CV2 image feature frequency counts and a corresponding list 
  of the image's class labels (i.e. forgery or genuine).
  '''
  # Get the class label of each image as described in unique.csv.
  file_info_path = ROOT_PATH + 'unique.csv'
  file_info = pd.read_csv(file_info_path)
  # Get a subset of files so data fits in memory
  #file_info = file_info.sample(frac=LOAD_MAX_PCT,random_state=1)
  filenames = list(file_info.iloc[:,1])
  classes = list(file_info.iloc[:,2])

  # Read each image listed in unique.csv, then extract its feature descriptors 
  # using ORB. Assign those features to the nearest "visual word" using KMeans.
  # Now each image can be described by a frequency count of the number of times 
  # each visual word appears.
  orb = cv.ORB_create(nfeatures=1800)
  kmeans = KMeans(n_clusters=MAX_WORDS)
  img_freq_counts = []
  all_descriptors = [] # Use to create KMeans clusters
  img_descriptors = [] # Use to create each image's freq_count
  for filename in filenames:
    print("Loading %s..." % filename)
    img_path = ROOT_PATH + 'sign_data/train/' + filename
    img = cv.imread(img_path, 0)
    if (img is not None):
        print("Image loaded.")
    else:
        print("Image load failed. Exiting...")
        sys.exit()
    keypoints, descriptors = get_features(img, orb)
    #if (descriptors):
    #    print("Descriptors loaded.")
    del img
    img_descriptors.append(descriptors)
    for descriptor in descriptors:
      all_descriptors.append(descriptor)
    print("Descriptors added to lists.")
  print("Images loaded. Fitting KMeans...")
  kmeans.fit(all_descriptors)
  print("KMeans fit. Getting freq_counts...")
  for desc in img_descriptors:
    freq_count = get_freq_count(desc, kmeans)
    img_freq_counts.append(freq_count)
  return filenames, img_freq_counts, classes

"""Load some test images and create an ORB extractor."""

#path = 'drive/My Drive/2021 Spring/CV/Final Project/sign_data'
#sign_img = cv.imread(path + '/train/069/12_069.png', 0)
#forg_img = cv.imread(path + '/train/069_forg/04_0111069.PNG', 0)

#orb = cv.ORB_create(nfeatures=1800)

"""Use ORB to get features from test images. See what features are detected."""

#keypoints, descriptors = get_features(sign_img, orb)
#keypoint_img = cv.drawKeypoints(sign_img, keypoints, None, color=(255, 127, 0), flags=0)
#cv2_imshow(keypoint_img)

#keypoints, descriptors = get_features(forg_img, orb)
#keypoint_img = cv.drawKeypoints(forg_img, keypoints, None, color=(255, 127, 0), flags=0)
#cv2_imshow(keypoint_img)

"""Preprocess the data by loading image files, getting their features, getting the closest "visual words" for each feature, compiling frequency counts of those words for each image, and pairing those counts with a class label (i.e. forgery or genuine)."""

# Get all image frequency counts for visual words and corresponding class labels.
filenames, img_freq_counts, classes = prep_data()
print("Counts == number of classes?")
print(len(img_freq_counts) == len(classes))

"""Write the preprocessed data to a CSV file."""

img_data = pd.DataFrame(img_freq_counts)
img_data['Class'] = classes
img_data['Filename'] = filenames
img_data_path = ROOT_PATH + 'prep_img_data.csv'
img_data.to_csv(img_data_path)

# Check that data was saved properly.
#img_data_chk = pd.read_csv(img_data_path)
#img_data_chk
