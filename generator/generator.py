import os
import json
import argparse

containerStack = []

ignoreList = [
  'Component', 'Expand'
]

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
      <style>.container{ 
        display: grid; border: 2px solid #000;
        grid-template-columns: repeat(11, 1wr);
        grid-template-rows: repeat(11, 1wr);
        grid-gap: 10px;
        }
        .border1{
          border: 2px solid #000;
        }
        .img {
          background-image: url('https://i.imgur.com/dfpkiFP.png');
          background-position: center;
          background-size: 100% 100%;
          display: block;
          max-width: 100%;
          max-height: 100%;
        }
      </style>
    </head>
    <body>
      <div class="container">
    """

def getElement(tag, attributes="", content="", obj=None):
  attributes = " ".join(attributes)
  return "<{0} {1} {3} > {2}</{0}>".format(tag,attributes, content, getElementSpanGridString(obj))

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
  return clamp(int(a/b*11)+1,1,12)

def getElementSpanString(obj):
  return 'class="col-md-{0}"'.format(getElementSpan(obj))

def getElementSpanGridString(obj):
  grid = getElementGridPosition(obj)
  return """
    style=" 
      grid-column: {0}/{1} ;
      grid-row: {2}/{3} ;
      "
    "
  """.format(grid[0], grid[1], grid[2], grid[3])

def getElementGridPosition(obj):
  if obj == None: return [0,0,0,0]
  container = containerStack[-1]
  xMin = container['x']
  xMax = xMin + container['w']
  yMin = container['y']
  yMax = yMin + container['h']

  oXMin = obj['x']
  oXMax = oXMin + obj['w']
  oYMin = obj['y']
  oYMax = oYMin + obj['h']
  xm = getSpan(xMin,xMax, oXMin)
  xM = getSpan(xMin,xMax, oXMax)
  ym = getSpan(yMin,yMax, oYMin)
  yM = getSpan(yMin,yMax, oYMax)

  return [xm, xM, ym, yM]

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

  return clamp( int(wO/wC * 11)+1, 1, 12) 
  #return span

def closeBody():
  return '</div></body></html>\n'

def wIMG(o):
  return getElement('div', ['class="img"'], obj=o)

def wTF(o):
  return getElement('input', ['type="text"'], obj=o)

def wTB(o):
  return getElement('p', content="Some Text.....", obj=o)

def wB(o):
  return getElement('Button', content="Button", obj=o)

def wCB(o):
  return getElement('input', ['type="checkbox"'], obj=o)

def wE(o):
  return getElement('b', content='UNKNOWN {0}'.format(o['class']), obj=o)

def wD(o):
  return getElement('select', ['type="select"'], obj=o)

def wRB(o):
  return getElement('input', ['type="radio"'], obj=o)

def beginContainer(o):
  span = getElementGridPosition(o)
  return """
    <div class="border1 container"
      style=" 
      grid-column: {0}/{1} ;
      grid-row: {2}/{3} ;
      ">
      """.format(span[0], span[1], span[2], span[3])

def endContainer(o):
  return """
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
  if(ignoreList.__contains__(obj['class'])):
    return

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
    size = 1
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
  #objs = sorted(objs, key=lambda obj: (obj['y'], obj['x']))
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