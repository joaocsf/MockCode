from .Detector import Detector
import os
import sys
import importlib
from PIL import Image
import cv2 as cv

WORK_DIR = os.path.dirname(__file__)


class DetectorYOLO(Detector):
  def on_create(self):
    self.work_path = os.getcwd()
    self.yolo_path = os.path.join(WORK_DIR, '../../model/keras-yolo3/')

    sys.path.append(self.yolo_path)

    yolo = importlib.import_module('model.keras-yolo3.yolo')

    os.chdir(self.yolo_path)
    self.YOLO = yolo.YOLO()
    os.chdir(self.work_path)
  
  def on_destroy(self):
    os.chdir(self.yolo_path)

    self.YOLO.close_session()

    os.chdir(self.work_path)
  
  def detect(self, image):
    os.chdir(self.yolo_path)

    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image = Image.fromarray(image)

    result = self.YOLO.detect_boxes(image)

    os.chdir(self.work_path)

    return self.to_json(result)
  
  def to_json(self, boxes):
    result = []
    for box in boxes:
      x,y,mx,my,id,c, _ = box
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