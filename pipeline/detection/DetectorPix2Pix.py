from .Detector import Detector
from model.pix2pix import Pix2Pix
import os
import sys
from PIL import Image
import cv2 as cv
import numpy as np

WORK_DIR = os.path.dirname(__file__)

class DetectorPix2Pix(Detector):
  def on_create(self):
    self.pix2pix = Pix2Pix(None, None)
  
  def on_destroy(self):
    pass
  
  def detect(self, image):
    img_original_h, img_original_w = image.shape[:2]
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image = Image.fromarray(image)

    result = self.pix2pix.predict_image(image)
    img_h, img_w = result.shape[:2]
    img_area = img_h*img_w
    print(img_original_w, img_original_h)

    result = np.array(result)
    result = cv.cvtColor(result, cv.COLOR_RGB2GRAY)
    result = np.uint8(result*127 + 127)
    _, thresh = cv.threshold(result, 128, 255, cv.THRESH_BINARY_INV)
    cv.imshow('RESULT', thresh)
    _, contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Debug
    debug_img = cv.cvtColor(thresh, cv.COLOR_GRAY2BGR)

    paramX = img_original_w/img_w
    paramY = img_original_h/img_h

    cv.imshow('Image', thresh)
    print('Containers', len(contours))
    containers = []
    n_contours = len(contours)
    for i, contour in enumerate(contours):
      x,y, w,h = cv.boundingRect(contour)
      area = w*h
      porpotion = area/img_area
      if(porpotion < 0.001):
        continue
      print(i+1)
      # Debug
      cv.rectangle(debug_img, (x,y), (x+w,y+h), (int(255* float(i)/n_contours),int(255*(1-float(i)/n_contours) ), 0), -1)
      container = self.get_container(x,y,w,h, paramX, paramY)
      containers.append(container)

    print('N_CONTAINERS', len(containers))
    cv.imshow('Debug', debug_img)
    cv.waitKey(0)
    return containers
  
  def get_container(self, x,y,w,h, paramX, paramY):
    x*=paramX
    w*=paramX
    y*=paramY
    h*=paramY

    return {
      'class': 'Container',
      'x': int(x),
      'y': int(y),
      'w': int(w),
      'h': int(h),
    }