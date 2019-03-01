import os
import sys
import argparse
import json
from pprint import pprint

def processFile(file, datasetDir, outputDir, classes):

  fileName = file.replace(".json","")
  imagePath = os.path.join(datasetDir, fileName+".png")
  jsonPath = os.path.join(datasetDir, file)

  if not os.path.isfile(imagePath):
    print('\nFILE NOT FOUND' + imagePath)

  annotationName = file

  boxes = []
  with open(jsonPath, 'r') as f:
    data = json.load(f)
    for elem in data:
      c = elem['class']
      x = elem['x']
      y = elem['y']
      w = elem['w']
      h = elem['h']
      classID = classes.index(c)
      xMax = float(x)+float(w)
      yMax = float(y)+float(h)

      if(x < 0): x = 0
      if(y < 0): y = 0

      boxes.append(
        "{0:0.0f},{1:0.0f},{2:0.0f},{3:0.0f},{4:0.0f}".format(x,y,xMax,yMax,classID)
      )

  entry = imagePath + " " + ' '.join(boxes)
  return entry

def parseFiles(datasetDir, outputDir, relative2Output, classes):
  print('Dataset Directory:', datasetDir)
  print('Output Directory:', outputDir)
  print('Relative to Output?', relative2Output)

  nfiles = int(len(os.listdir(datasetDir))/2)
  index = 1
  lines = []
  with open(os.path.join(outputDir, 'trainset'), 'w') as fOut:
    for file in os.listdir(datasetDir):
      if not file.endswith(".json"):
        continue

      index+=1
      print_progressbar(index/nfiles, prefix='Parsing', suffix=file )
      entry = processFile(file, datasetDir, outputDir, classes)    
      fOut.write(entry+'\n')

def print_progressbar(percentage, width=50, prefix='>', suffix='...'):
  filled = int(width*percentage)
  toFill = width-filled
  bar = '='*filled + '-'*toFill
  suffix += ' '*(20-len(suffix))
  
  print('{0} [{2}] {3:0.2f}% {1}'.format(prefix, suffix, bar, percentage), end='\r')

def createParser():
  parser = argparse.ArgumentParser(description='Generate Dataset Trainning Files')
  parser.add_argument(
    'input',
    help='Input folder',
  )
  parser.add_argument(
    '-o',
    dest='out',
    help='Output folder',
  )
  parser.add_argument(
    '-c',
    dest='classes',
    help='Classess',
  )
  parser.add_argument(
    '-r',
    action='count',
    help="Relative To Output?"
  )

  return parser

def read_classes(classfile):
  print('Classes File:', classfile)
  classes = []

  with open(classfile, 'r') as f:
    classes = f.readlines()

  classes = [ x.replace('\n','') for x in classes]
  return classes

def execute():
  parser = createParser()
  args = parser.parse_args()

  relative_path = False
  if not args.r is None:
    if args.r > 0:
      relative_path = True 
    
  if (args.classes is None):
    print('-c is required')
    return
  
  out_path = './' if args.out is None else args.out

  classes = read_classes(args.classes)

  if(len(classes) == 0):
    print('Classes Missing')
    return

  print('Classes:', classes)

  parseFiles(args.input, out_path, relative_path, classes)

if __name__ == "__main__":
  execute()