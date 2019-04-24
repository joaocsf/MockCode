import os
import sys
import importlib
from PIL import Image
from model import merge
import argparse
import time
import cv2 as cv
from pipeline import pipeline as PipeLine
import json

class MockCode:
  def __init__(self, pipeline):
    self.pipeline=pipeline
    cv.namedWindow('Image')
    cv.createTrackbar('type', 'Image', 0, 1, nothing) 
    cv.createTrackbar('kernel', 'Image', 11, 50, nothing) 
    cv.createTrackbar('weight', 'Image', 10, 50, nothing) 
    cv.createTrackbar('kernel_e', 'Image', 0, 3, nothing) 
  
  def video(self):
    print('Processing Video')
    cam = cv.VideoCapture(0)

    while True:
      _, img = cam.read()
      key = cv.waitKey(20)
      cv.imshow('Image', img)

      if key == 27:
        break
      elif key == 32:
        cv.imshow('ScreenShot', img)
        self.__run_pipeline__(img)
  
  def image(self, image_path):
    print('Processing Image')
    image = cv.imread(image_path)
    cv.imshow('Input', image)
    self.__run_pipeline__(image)
  
  def __run_pipeline__(self, image):
    image = self.adapt_image(image)
    self.pipeline.execute(image)
    self.pipeline.show_generator_results()

  def adapt_image(self, img):
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
    #element = cv.getStructuringElement(cv.MORPH_ELLIPSE, (kernel_element, kernel_element))
    #thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, element)
    return cv.cvtColor(thresh, cv.COLOR_GRAY2BGR)


def arg_parse():
  parser = argparse.ArgumentParser('')
  parser.add_argument('-i', '--image')
  parser.add_argument('-o', '--out', default='generated/')
  parser.add_argument('-a', '--alternative')
  parser.add_argument('-dg', '--debuggen')
  return parser.parse_args()

def nothing(x):
  pass

def setup_dnn_pipeline(pipeline):
  yolo = PipeLine.detection.DetectorYOLO()
  pix2pix = PipeLine.detection.DetectorPix2Pix()
  pipeline.add_detection(yolo)
  pipeline.add_detection(pix2pix)

  merger = PipeLine.result_processing.ProcessorMerger()
  pipeline.add_processing(merger)

  html_generator = PipeLine.code_generation.GeneratorHTML()
  pipeline.add_generator(html_generator)

def setup_cnn_pipeline(pipeline, classes_path):
  cnn = PipeLine.detection.DetectorCNN(classes_path)
  pipeline.add_detection(cnn)

  merger = PipeLine.result_processing.ProcessorMerger()
  pipeline.add_processing(merger)

  html_generator = PipeLine.code_generation.GeneratorHTML()
  pipeline.add_generator(html_generator)

def setup_debug_gen_pipeline(pipeline, annotation_file):

  objs = {}
  with open(annotation_file, 'r') as file:
    objs = json.load(file)
  pipeline.ommit_process('detection', objs)

  merger = PipeLine.result_processing.ProcessorMerger()
  pipeline.add_processing(merger)

  html_generator = PipeLine.code_generation.GeneratorHTML()
  pipeline.add_generator(html_generator)

def main():
  args = arg_parse()
  pipeline = PipeLine.Pipeline(args.out)

  if not args.debuggen is None:
    setup_debug_gen_pipeline(pipeline, args.debuggen)
  elif not args.alternative is None:
    setup_cnn_pipeline(pipeline, args.alternative)
  else:
    setup_dnn_pipeline(pipeline)
  
  mockcode = MockCode(pipeline)

  if args.image == None:
    mockcode.video()
  else:
    mockcode.image(args.image)
  
  cv.waitKey(0)

if __name__ == "__main__":
  main()