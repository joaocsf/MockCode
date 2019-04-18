from .detection import Detector
from .result_processing import Processor
from .code_generation import Generator
import os
import cv2 as cv

class Pipeline():

  def __init__(self, out_folder):
    self.out_folder =out_folder
    self.detectors = []
    self.processors = []
    self.generators = []
    self.detection_results = []

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
    total = len(self.processors)    

    for i, generator in enumerate(self.generators):
      elements = generator.process(elements, self.out_folder)
      progress((i+1)/float(total), prefix='Generating', suffix='{0}/{1}'.format(i+1,total))
  
  def show_generator_results(self):
    for generator in self.generators:
      generator.show()
  
  def debug(self,tag, image, elements):
    image2 = image.copy()
    print('\nElement Count', len(elements))

    print([element['class'] for element in elements])
    print

    print(len([element['class'] for element in elements if element['class']=='Container']))

    for element in elements:
      pt1 = (int(element['x']), int(element['y']))
      pt2 = (int(element['w'] + pt1[0]), int(element['h'] + pt1[1]))
      color = (0,0,255)
      if element['class'] == 'Container':
        print(element)
        color = (0,255,0)
      cv.rectangle(image2, pt1, pt2, color, 5)

    cv.imshow(tag, image2)


  def execute(self, image):
    res = self.execute_detection(image)
    self.debug('Before', image, res)
    print('')
    res = self.execute_processors(res)
    print('')
    self.debug('After', image, res)
    self.execute_code_generators(res)
    print('Finished!')
    cv.waitKey(0)

def progress(percentage, width=50, prefix='', suffix='', fill='#', empty='-'):
  n_fill = int(width*percentage)
  t_fill = width-n_fill
  p = fill*n_fill + empty*t_fill

  print('\r{0} |{1}| {2}'.format(prefix, p, suffix), end='', flush=True)
