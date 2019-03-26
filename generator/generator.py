import os
import json
import argparse

containerStack = []

def getHeader():
  return """
  <!doctype html>
  <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
      <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
      <title>Hello, world!</title>
      <style>body > div.container{border: 2px none #000;} </style>
      <style>.container{border: 2px solid #000;} </style>
    </head>
    <body>
      <div class="container">
        <div class="row">
    """

def getElement(tag, attributes="", content="", obj=None):
  attributes = " ".join(attributes)
  return "<{0} {1} {3} > {2}</{0}>".format(tag,attributes, content, getElementSpanString(obj))

def clamp(value, a, b):
  if value < a:
    return a
  elif value > b:
    return b
  return value

def getSpan(xMin, xMax, Value):
  b = xMax-xMin
  a = Value-xMin
  a = clamp(a, 0, b)
  return int(a/b*12)

def getElementSpanString(obj):
  return 'class="col-md-{0}"'.format(getElementSpan(obj))

def getElementSpan(obj):
  if obj == None: return ''
  container = containerStack[-1]
  xMin = container['x']
  xMax = xMin + container['w']

  oXMin = obj['x']
  oXMax = oXMin + obj['w']
  s1 = getSpan(xMin,xMax, oXMin)
  s2 = getSpan(xMin,xMax, oXMax)

  span = s2-s1 + 1
  wC = container['w']
  wO = obj['w']

  return clamp( int(wO/wC * 12), 1, 12) 
  #return span

def closeBody():
  return '</div></body></html>\n'

def wIMG(o):
  return getElement('img', ['src="https://i.imgur.com/bzmZlgD.png"'], obj=o)

def wTF(o):
  return getElement('input', ['type="text"'], obj=o)

def wTB(o):
  return getElement('p', content="Some Text.....", obj=o)

def wB(o):
  return getElement('Button', content="Button", obj=o)

def wCB(o):
  return getElement('input', ['type="checkbox"'], obj=o)

def wE(o):
  return getElement('b', content='UNKNOWN {0}'.format(o['class']))

def wD(o):
  return getElement('select', ['type="select"'], obj=o)

def wRB(o):
  return getElement('input', ['type="radio"'], obj=o)

def beginContainer(o):
  return """
    <div class="container col-md-{0}">
      <div class="row">
      """.format(getElementSpan(o))

def endContainer(o):
  return """
    </div>
      </div>"""

def writeObj(file, obj):
  switch = {
    'Textfield': wTF,
    'Picture': wIMG,
    'Button': wB,
    'TextBlock': wTB,
    'Checkbox': wCB,
    'RadioButton': wRB,
    'Dropdown': wD,
  }

  option = wE
  if switch.__contains__(obj['class']):
    option = switch[obj['class']]

  file.write(option(obj))

def snap(value, base):
  return int(value/base)

def snapToGrid(objs):
  for obj in objs:
    x = obj['x']
    y = obj['y']
    xMax = x + obj['w']
    yMax = y + obj['h']
    size = 30
    x = snap(x, size)
    y = snap(y, size)
    xMax = snap(xMax, size)
    yMax = snap(yMax, size)
    obj['x'] = x
    obj['y'] = y
    obj['w'] = xMax - x
    obj['h'] = yMax - y

def parseContainer(file, objs):
  snapToGrid(objs)
  parent = containerStack[-1]
  objs = sorted(objs, key=lambda obj: (obj['y'], obj['x']))
  print([ [x['class'], x['x'], x['w']] for x in objs])
  for obj in objs:
    if obj['class'] == 'Container':
      file.write(beginContainer(obj))
      containerStack.append(obj)
      parseContainer(file, obj['childs'])
      containerStack.pop()
      file.write(endContainer(obj))
    else:
      writeObj(file, obj)

def parse(inputFile):
  with open('index.html', 'w') as indexFile:
    with open(inputFile, 'r') as file:
      indexFile.write(getHeader())
      objs = json.load(file)

      maxW = max(objs, key=lambda o: o['x']+o['w'])
      maxW = maxW['x']+maxW['w']
      maxH = max(objs, key=lambda o: o['y']+o['h'])
      maxH = maxH['y']+maxH['h']
      containerStack.append(
        {
          'x':0,
          'y':0,
          'w': maxW,
          'h': maxH
        }
      )
      snapToGrid(containerStack)

      parseContainer(indexFile, objs)

      indexFile.write(closeBody())

def main():
  parser = argparse.ArgumentParser(description='Parse To HTML')
  parser.add_argument('input')

  args = parser.parse_args()

  inputFile = args.input

  parse(inputFile)


if __name__ == "__main__":
    main()