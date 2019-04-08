import os
import sys
import importlib
from PIL import Image
from model import merge
import webbrowser
import generator.generator as generator
import argparse
import time
import cv2 as cv

sys.path.append('./model/keras-yolo3/')

yolo = importlib.import_module('model.keras-yolo3.yolo')

YOLO = None

def s_yolo():
  os.chdir('./model/keras-yolo3/')

def e_yolo():
  os.chdir('../../')


def init_yolo():
  global YOLO, yolo
  YOLO = yolo.YOLO()

def to_json(boxes):
  result = []
  for box in boxes:
    x,y,mx,my,id,c = box
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

def detect_image(image):
  result = YOLO.detect_boxes(image)
  return to_json(result)

def arg_parse():
  parser = argparse.ArgumentParser('')
  parser.add_argument('--image', dest='image')


  return parser.parse_args()

def show_result():
  webbrowser.get('firefox').open(os.path.abspath('./index.html'))


def image(path):
  print('Opening: %s' % path)
  image = Image.open(path)
  s_yolo() 
  result = detect_image(image)
  e_yolo()

  merged = merge.merge_obj(result)
  generator.generate_code(merged)
  show_result()

def to_pil_img(img):
  img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
  return Image.fromarray(img)

def nothing(x):
  pass

def adapt_image(img):
  img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
  kernel = cv.getTrackbarPos('kernel', 'Image')
  kernel_element = cv.getTrackbarPos('kernel_e', 'Image')
  weight = cv.getTrackbarPos('weight', 'Image')
  typ = cv.getTrackbarPos('type', 'Image')
  if kernel < 1: 
    kernel = 1
    weight = 1
    kernel_element = 1
    typ = 0
  
  kernel = kernel *2 + 1
  kernel_element = kernel_element + 1

  method = cv.ADAPTIVE_THRESH_GAUSSIAN_C if typ == 0 else cv.ADAPTIVE_THRESH_MEAN_C
  thresh = cv.adaptiveThreshold(img, 256, method, cv.THRESH_BINARY, kernel, weight)
  element = cv.getStructuringElement(cv.MORPH_ELLIPSE, (kernel_element, kernel_element))
  thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, element)
  return cv.cvtColor(thresh, cv.COLOR_GRAY2BGR)

def video():
  cv.namedWindow('Image')
  cv.createTrackbar('type', 'Image', 0, 1, nothing) 
  cv.createTrackbar('kernel', 'Image', 11, 50, nothing) 
  cv.createTrackbar('weight', 'Image', 10, 50, nothing) 
  cv.createTrackbar('kernel_e', 'Image', 1, 3, nothing) 

  cam = cv.VideoCapture(0)

  while True:

    _, img = cam.read()
    key = cv.waitKey(20)

    img = adapt_image(img)

    cv.imshow('Image', img)

    if key == 27:
      break
    elif key == 32:
      cv.imshow('ScreenShot', img)
      image = to_pil_img(img)
      s_yolo() 
      result = detect_image(image)
      e_yolo()

      merged = merge.merge_obj(result)

      generator.generate_code(merged)
      show_result()
      cv.imshow('ScreenShot', img)

def main():
  global YOLO

  path = './dataset/data/image/%d.png'

  args = arg_parse()




  s_yolo() 
  init_yolo()
  e_yolo()
  i = -1

  if args.image == None:
    video()
  else:
    image(args.image)

  s_yolo()
  YOLO.close_session()
  e_yolo()

if __name__ == "__main__":
  main()