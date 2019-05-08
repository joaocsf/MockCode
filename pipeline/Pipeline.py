from .detection import Detector
from .result_processing import Processor
from .code_generation import Generator
import os
import cv2 as cv
import time

class Pipeline():

  def __init__(self, out_folder):
    self.out_folder =out_folder
    self.detectors = []
    self.processors = []
    self.generators = []
    self.detection_results = []
    self.ommit = {}
    self.stats = {
      'DETECTION': [],
      'PROCESSING': [],
      'GENERATION': [],
    }
  def add_detection(self, detection):
    assert isinstance(detection, Detector)
    self.detectors.append(detection)
  
  def add_processing(self, processor):
    assert isinstance(processor, Processor)
    self.processors.append(processor)
  
  def add_generator(self, generator):
    assert isinstance(generator, Generator)
    self.generators.append(generator)

  def execute_detection(self, image):
    results = []
    total = len(self.detectors)
    for i, detector in enumerate(self.detectors):
      results += detector.detect(image)
      progress((i+1)/float(total), prefix='Detection', suffix='{0}/{1}'.format(i+1,total))
    return results
  
  def execute_processors(self, elements):
    total = len(self.processors)    

    for i, processor in enumerate(self.processors):
      elements = processor.process(elements)
      progress((i+1)/float(total), prefix='Processing', suffix='{0}/{1}'.format(i+1,total))

    return elements

  def execute_code_generators(self, elements):
    total = len(self.generators)    

    for i, generator in enumerate(self.generators):
      generator.process(elements, self.out_folder)
      progress((i+1)/float(total), prefix='Generating', suffix='{0}/{1}'.format(i+1,total))
  
  def show_generator_results(self):
    for generator in self.generators:
      generator.show()
  
  def ommit_process(self, process, objects):
    self.ommit[process] = objects

  def log_time(self, process, start_time):
    end = time.time()
    elapsed = end-start_time
    self.stats[process].append(elapsed)

  def debug_aux(self, image, elements, deep=0):
    for element in elements:
      pt1 = (int(element['x']), int(element['y']))
      pt2 = (int(element['w'] + pt1[0]), int(element['h'] + pt1[1]))
      color = (0,0,255)
      if element['class'] == 'Container':
        color = (255*(1-deep/5.0),255*deep/5.0,0)
        if element.__contains__('childs'):
          self.debug_aux(image, element['childs'], deep+1)
      cv.rectangle(image, pt1, pt2, color, 5)



  def debug(self,tag, image, elements):
    image2 = image.copy()
    self.debug_aux(image2, elements)
    cv.imshow(tag, image2)
    cv.waitKey(1)

  def log_stats(self):
    print('Statistics:', flush=True)
    for stat in self.stats:
      mean = sum(self.stats[stat])/len(self.stats[stat])
      log = '\t{0}: {1:0.3f}'.format(stat, mean)
      print(log, flush=True)

  def execute(self, image):
    res = []

    start = time.time()
    if self.ommit.__contains__('detection'):
      res = self.ommit['detection']
    else:
      res = self.execute_detection(image)
    self.log_time('DETECTION', start)
    self.debug('Before', image, res)
    print('')

    start = time.time()
    res = self.execute_processors(res)
    self.log_time('PROCESSING', start)
    self.debug('After', image, res)
    print('')

    start = time.time()
    self.execute_code_generators(res)
    self.log_time('GENERATION', start)
    print('\nFinished Processing Pipeline')

    self.log_stats()

def progress(percentage, width=50, prefix='', suffix='', fill='\033[92m#\033[0m', empty='-'):
  n_fill = int(width*percentage)
  t_fill = width-n_fill
  p = fill*n_fill + empty*t_fill

  print('\r{0} |{1}| {2}'.format(prefix, p, suffix), end='', flush=True)
