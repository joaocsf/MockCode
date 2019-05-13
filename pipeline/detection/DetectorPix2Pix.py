from .Detector import Detector
from model.pix2pix import Pix2Pix
import os
import sys
from PIL import Image
import cv2 as cv
import numpy as np
import importlib

WORK_DIR = os.path.dirname(__file__)

class DetectorPix2Pix(Detector):
  def on_create(self):
    self.pix2pix = Pix2Pix(None, None)
    yolo = importlib.import_module('model.keras-yolo3.yolo')

    yolo_config = {
        "model_path": os.path.join(WORK_DIR, '../../model/keras-yolo3/model_data/container_weights.h5'),
        "classes_path": os.path.join(WORK_DIR, '../../model/keras-yolo3/model_data/container_classes.txt')
      }
    self.YOLO = yolo.YOLO(**yolo_config)
  
  def on_destroy(self):
    pass
  
  def result_to_image(self, result):
    result = np.uint8(result*127 + 127)
    image = Image.fromarray(result)
    return image

  def on_detect(self, image):
    img_original_h, img_original_w = image.shape[:2]
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image = Image.fromarray(image)

    result = self.pix2pix.predict_image(image)
    image = self.result_to_image(result)
    image_h, image_w = result.shape[:2]
    result = self.YOLO.detect_boxes(image)

    fx = img_original_w/float(image_w)
    fy = img_original_h/float(image_h)
    return self.to_json(result, fx, fy)
  
  def to_json(self, boxes, fx, fy):
    result = []
    for box in boxes:
      x,y,mx,my,id,c, _ = box
      x  *= fx
      y  *= fy
      mx *= fx
      my *= fy
      result.append(
        {
          'class': c,
          'x': x,
          'y': y,
          'w': mx-x,
          'h': my-y,
        }
      )
    return result