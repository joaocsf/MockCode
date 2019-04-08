import os
import sys
import importlib
from PIL import Image
from model import merge
import webbrowser
import generator.generator as generator
import time

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

def main():
  global YOLO

  path = './dataset/data/image/%d.png'

  s_yolo() 
  init_yolo()
  e_yolo()
  i = -1

  while i < 3:
    new_path = path%i
    print('Opening: %s' % new_path)
    image = Image.open(path % i)
    s_yolo() 
    result = detect_image(image)
    e_yolo()

    merged = merge.merge_obj(result)

    generator.generate_code(merged)
    webbrowser.get('firefox').open(os.path.abspath('./index.html'))
    i+=1
    time.sleep(0.5)

  s_yolo()
  YOLO.close_session()
  e_yolo()

if __name__ == "__main__":
  main()