document.addEventListener("DOMContentLoaded", startup)

var width = 800
var height = 900
var rc = null
var randomize = true
var style = {}
var randomOffset = 10
var noisyLines = 0.3
var drawBox = false
var boxOffset = 5
var gridSize = 100
var gridSpacing = 20

class Drawable {
  constructor(x,y, w, h){
    this.rnd = () => {
      return Math.random()*0.1 + 0.8
    }
    this.x = x
    this.y = y
    this.w = w
    this.h = h
    this.min = [x,y]
    this.max = [x+w, y+h]

    this.generate()
  }

  generate(){

  }

  getBoxDims(){
    var min = this.min
    var max = this.max
    var w = max[0] - min[0]
    var h = max[1] - min[1]
    var x = min[0] - boxOffset
    var y = min[1] - boxOffset
    w += 2*boxOffset
    h += 2*boxOffset
    return [x,y,w,h]
  }

  drawBox(rc){
    var dims = this.getBoxDims()
    var color = this.color || 'green'
    rc.rectangle(dims[0], dims[1],dims[2],dims[3],{stroke:color, roughness:0})
  }

  onDraw(rc){
    for(var i in this.lines){
      var l = this.lines[i]
      strange_line(l[0], l[1], 0.3)
    }
  }

  draw(rc){
    this.onDraw(rc)

    if(drawBox)
      this.drawBox(rc)
  }

  update_min_max(points){
    for(var p in points){
      var point = points[p]
      set_min_max(this.min, this.max, point) 
    }
  }
}

class Checkbox extends Drawable
{
  generate()
  {
    this.color = 'cyan'
    var min = Math.min(this.w, this.h)
    this.w = Math.random()*0.5+0.5
    this.h = Math.random()*0.5+0.5
    this.w *= min
    this.h *= min
    
    this.max[0] = this.x + this.w
    this.max[1] = this.y + this.h

    var points = []
    points.push(
      [this.x, this.y],
      [this.x + this.w, this.y],
      [this.x + this.w, this.y + this.h],
      [this.x, this.y + this.h],
    )
    
    if(randomize)
      mutate(points, 0.1)
    
    this.lines= []
    this.lines.push(
      [points[0], points[1]],
      [points[1], points[2]],
      [points[2], points[3]],
      [points[3], points[0]],
    )

    if(randomize && Math.random() > 0.5){
      
      var left = p_mult(p_sum(points[0], points[3]), 1/2)
      var mid = p_mult(p_sum(points[0], points[2]), 1/2)
      var top = points[1].slice()
      left[0] += this.w*random(-0.5,0.2)
      left[1] += this.h*random(-0.5,0.1)
      mid[1] += this.h*random(0.2,0.5)
      top[0] += this.w*random(-0.5,0.5)
      top[1] += this.h*random(-0.5,0.3)
      var pts = [left, mid, top]
      mutate(pts, 0.2)
      this.lines.push(
        [pts[0], pts[1]],
        [pts[1], pts[2]]
      )
    }
 
  }
}

class Button extends Drawable
{
  generate() 
  {
    this.color = 'crimson'
    var points = rectPoints(this.x, this.y, this.w, this.h)
    this.lines = []
    if(randomize)
      mutate(points)

    this.lines.push(
      [points[0], points[1]],
      [points[1], points[2]],
      [points[2], points[3]],
      [points[3], points[0]],
    )
    for(var p in points){
      set_min_max(this.min, this.max, points[p])
    }
    points = []
    var nPoints = this.w/100
    nPoints *= Math.random()+2
    nPoints = Math.floor(nPoints)
    var size = 1/nPoints
    var hOffset = 0.2
    if(Math.random() > 0.5)
      nPoints = 2
    
    var direction = Math.random() > 0.5
    this.w = this.max[0] - this.min[0]
    for(var i = 0; i < nPoints; i++){
      var pt = [0,0]
      var rand = [-0.1, -0.1]
      if(i == 0){
        rand[0] =0
        rand[1] =1
      }
      
      if(i == nPoints-1){
        rand[0] =-1
        rand[1] =0
      }
      
      
      var frac = ((i/(nPoints-1)))
      var offsetX = size * random(rand[0],rand[1])
      pt[0] = this.w * (frac + offsetX)

      pt[1] = this.h * (direction ? random(0.5,0.5+hOffset) : random(0.5-hOffset,0.5))
      pt[0] += this.min[0]
      pt[1] += this.min[1]

      direction = !direction
      points.push(
        pt
      )
    }

    for(var i = 0; i < points.length - 1; i++){
      set_min_max(this.min, this.max, points[i+1])
      this.lines.push(
        [points[i], points[i+1]]
      )
    }
  }
}

class RadioButton extends Drawable
{
  generate()
  {
    this.color = 'blue'
    var min = Math.min(this.w, this.h)
    this.w = Math.random()*0.5+0.5
    this.h = Math.random()*0.5+0.5
    this.w *= min
    this.h *= min
    
    this.x += this.w/2
    this.y += this.h/2
    
    this.max[0] = this.x + this.w/2
    this.max[1] = this.y + this.h/2
  }

  onDraw(rc){
    rc.ellipse(this.x, this.y, this.w, this.h, style)    
  }
}

class TextBlock extends Drawable
{
  generate()
  {
    this.color = 'purple'
    this.lines = []
    var points = []
    var nPoints = this.w/50
    nPoints *= Math.random()+2   
    var size = 1/nPoints
    var direction = Math.random() > 0.5
    var hOffset = 0.5 
    if(Math.random() > 0.5)
      nPoints = 2
      hOffset = 0.2

    for(var i = 0; i < nPoints; i++){
      var pt = [0,0]
      pt[0] = this.w * ((i/(nPoints-1)) + size * random(-0.5,0.5) )
      pt[1] = this.h * (direction ? random(0.5,0.5+hOffset) : random(0.5-hOffset,0.5))
      pt[0] += this.x
      pt[1] += this.y
      direction = !direction

      points.push(
        pt
      )
    }

    if(randomize)
      mutate(points)
    
    this.points = points
    set_min_max(this.min, this.max, points[0])
    for(var i = 0; i < points.length - 1; i++){
      set_min_max(this.min, this.max, points[i+1])

      this.lines.push(
        [points[i], points[i+1]]
      )
    }
  }

  onDraw(rc){
    rc.curve(this.points, style)
  }
}

class Dropdown extends Drawable
{
  generate() 
  {
    this.color = 'green'
    this.rnd = () => {
      return Math.random()*0.1 + 0.8
    }
    this.lines = []
    var points = rectPoints(this.x, this.y, this.w, this.h)
    if(randomize)
      mutate(points)
    
    var m1 = p_lerp(points[0], points[1], this.rnd())
    var m2 = p_lerp(points[3], points[2], this.rnd())
    var mid_line = [m1, m2]
    if(mutate)
      mutate(mid_line, 0.5)

    this.lines.push(
      [points[0], points[1]],
      [points[1], points[2]],
      [points[2], points[3]],
      [points[3], points[0]],
      [mid_line[0], mid_line[1]],
    )

    this.update_min_max(points)
  }
}

class Textfield extends Drawable
{
  generate()
  {
    this.color ='yellow'
    this.lines = []
    var points = rectPoints(this.x, this.y, this.w, this.h)

    if(randomize)
      mutate(points)

    this.lines.push(
      [points[0], points[1]],
      [points[1], points[2]],
      [points[2], points[3]],
      [points[3], points[0]],
    )
    this.update_min_max(points)
  }
}

class Debug extends Drawable
{
  onDraw(rc){
    rc.rectangle(this.x, this.y, this.w, this.h, {fill: 'red'})
  }
}

class Picture extends Drawable
{
  generate()
  {
    this.color = 'red'
    this.lines = []
    var points = rectPoints(this.x, this.y, this.w, this.h)

    if(randomize)
      mutate(points)

    var cross = []
    cross.push(
      points[0].slice(),
      points[2].slice(),
      points[3].slice(),
      points[1].slice(),
      )

    if(randomize)
      mutate(cross)

    this.lines.push([points[0], points[1]])
    this.lines.push([points[1], points[2]])
    this.lines.push([points[2], points[3]])
    this.lines.push([points[3], points[0]])
    this.lines.push([cross[0], cross[1]])
    this.lines.push([cross[3], cross[2]])
    
    this.update_min_max(points)
  }
}

function set_min_max(min, max, value){
  min[0] = Math.min(value[0], min[0])
  min[1] = Math.min(value[1], min[1])
  max[0] = Math.max(value[0], max[0])
  max[1] = Math.max(value[1], max[1])
}

function random(min, max)
{
  var diff = max-min
  return Math.random()*diff + min
}

function p_mult(a,v){
  a[0] *= v
  a[1] *= v
  return a
}

function p_sum(a,b){
  return [a[0]+b[0], a[1]+b[1]]
}

function p_sub(a,b){
  return [a[0]-b[0], a[1]-b[1]]
}

function p_lerp(a,b,t){
  return p_sum(a, p_mult(p_sub(b,a), t))
}

function strange_line(a,b, weight){
  var qrt = p_lerp(a,b,0.25)
  var qrt_2 = p_lerp(a,b,0.45)
  var pts = [qrt, 
    qrt_2]
  mutate(pts, weight)

  var points = []
  points.push(
    a,
    pts[0],
    pts[1],
    b
  )
  rc.curve(points, style)  
}

function line(a, b){
  rc.line(a[0],a[1], b[0], b[1], style)
}

function mutate(points, value){
  var offset = randomOffset
  if(value !== undefined)
    offset*=value

  for(var i in points)
  {
    var point = points[i]
    point[0] += Math.random()*offset*2 - offset
    point[1] += Math.random()*offset*2- offset
  }
}

function rectPoints(x,y,w,h){
  var p1 = [x,y]
  var p2 = [x+w,y]
  var p3 = [x+w,y+h]
  var p4 = [x, y+h]

  return [p1,p2,p3,p4]
}

function picture(x,y,w,h){
  var ps = rectPoints(x,y,w,h)

  for(var i in ps){
    i = Number(i)
    var i1 = (i + 1)%4
    var a = ps[i]
    var b = ps[i1]
    line(a,b)
  }
  
  line(ps[0],ps[2])
  line(ps[1],ps[3])
}

function startup(){
  var canvas = document.getElementsByClassName('canvas')[0]
  canvas.width=width
  canvas.height=height
  const context = canvas.getContext('2d');
  rc = rough.canvas(canvas)
  var offset = 10
  randomizeStyle()
  $('.generate').click(()=> {
    context.clearRect(0,0, canvas.width, canvas.height)
    drawGrid([width, height], rc)
  })

  drawGrid([width, height], rc)
  // draw(rc)
  //rc.circle(width/2, height/2, 90, style)
}

function randomElement(){
  var elems = [
    {name: 'Picture'    , expand: 'a', split: 'n' },
    {name: 'Dropdown'   , expand: 'h', split: 'v' },
    {name: 'RadioButton', expand: 'v', split: 'v' },
    {name: 'Textfield'  , expand: 'h', split: 'v' },
    {name: 'Checkbox'   , expand: 'v', split: 'v' },
    {name: 'TextBlock'  , expand: 'a', split: 'v' },
    {name: 'Button'     , expand: 'a', split: 'v' },
  ]
  var index = Math.floor(Number(random(0, elems.length)))
  return elems[index]
}

function createObj(obj, x,y,w,h){
  //return new window[obj](x,y,w,h)
  //obj.name = obj.name !== 'Debug'? 'Picture': 'Debug'
  switch(obj.name){
    case 'Picture':
      return new Picture(x,y,w,h)
    case 'Dropdown':
      return new Dropdown(x,y,w,h)
    case 'RadioButton':
      return new RadioButton(x,y,w,h)
    case 'Textfield':
      return new Textfield(x,y,w,h)
    case 'Checkbox':
      return new Checkbox(x,y,w,h)
    case 'TextBlock':
      return new TextBlock(x,y,w,h)
    case 'Button':
      return new Button(x,y,w,h)
    case 'Debug':
      return new Debug(x,y,w,h)
    default:
      console.error(obj)
      break;
  }
}

function addObject(object, objs){
  var splitV = object.split === 'v'

  if(splitV){
    var hSize = random(0.4,0.5)
    var offset = random(0.001,0.1)
    var occurrences = Math.floor(object.h/(hSize+offset))
    var copy = JSON.stringify(object)

    for(var i = 0; i < occurrences; i++){
      var newObj = JSON.parse(copy)
      newObj.y += offset*i + hSize*i
      //newObj.y
      newObj.h = hSize
      objs.push(newObj)
    }
  }else
    objs.push(object)
}

function decorateGrid(gridSize){
  var gridCells = []
  var objs = []
  for(var j = 0; j < gridSize[1]; j++){
    for(var i = 0; i < gridSize[0]; i++){
      if(gridCells[i+'x'+j] === true)
        continue

      var element = randomElement()

      gridCells[i+'x'+j] = true
      var expand = element.expand
      var expandH = expand === 'a' || expand === 'h'
      var expandV = expand === 'a' || expand === 'v'
      
      expandH = Math.random() > 0.5 ? false : expandH
      expandV = Math.random() > 0.5 ? false : expandV
      
      var expandHSize = expandH ?  Math.random()* (gridSize[0] - i - 1) : 0
      var expandVSize = expandV ?  Math.random()* (gridSize[1] - j - 1) : 0
      expandHSize = Math.floor(expandHSize)
      expandVSize = Math.floor(expandVSize)
      var max = [i,j]
      var stop = false

      for(var y = 0; y <= expandVSize; y++){
        if(stop) break
        for(var x = 0; x <= expandHSize; x++){
          if(x == y && x == 0)
            continue
          
          var xi = x+i
          var yj = y+j
          
          if(gridCells[xi+'x'+yj] == true){
            var debug = {
                name:'Debug', 
                x: xi, 
                y: yj, 
                w: 1,
                h: 1
              }
            stop=true
            break
          }else
            gridCells[xi+'x'+yj] = true

          max[0] = Math.max(xi, max[0])
          max[1] = Math.max(yj, max[1])
        }
      }

      element.start = [i,j]
      element.x = i
      element.y = j
      element.size = p_sub(p_sum(max, [1,1]), element.start)

      element.w = element.size[0]
      element.h = element.size[1]

      addObject(element, objs)
      //objs.push(element)

    }
  }

  return objs
}

function drawGrid(size, rc){
  var gridS = gridSize * random(1.0,1.5)
  var offset = 10
  var cell = gridS + gridSpacing + offset/2
  var hLeftOver = size[0] % cell
  var vLeftOver = size[1] % cell

  var nH = size[0]/cell
  var nV = size[1]/cell
  nV = Math.floor(nV)
  nH = Math.floor(nH)
  var offsetX = hLeftOver*Math.random() + offset
  var offsetY = vLeftOver*Math.random() + offset

  var gridObjs = decorateGrid([nH, nV])
  var objs = []

  for(var index in gridObjs){
    var obj = gridObjs[index]
    var x = offsetX + obj.x * gridS + gridSpacing*obj.x
    var y = offsetY + obj.y * gridS + gridSpacing*obj.y

    var w = gridS*obj.w + gridSpacing*(obj.w-1)
    var h = gridS*obj.h + gridSpacing*(obj.h-1)

    var obj = createObj(obj, x, y, w, h)

    objs.push(obj)
  }

  for(var i in objs){
    objs[i].draw(rc)
  }

}

function randomizeStyle(){
  style = {
    roughness: Math.random()*0.5,
    bowing: Math.random()*10,
    strokeWidth:Math.random()*4+1,
    hachureGap: Math.random()*4
  }
}

function draw(rc){
  var objs = []
  objs.push(
    new Picture(40,40,200,100),
    new Dropdown(270, 40, 500, 40),
    new Dropdown(270, 100, 200, 30),
    new RadioButton(40,160, 40, 40),
    new Textfield(100,160, 200, 30),
    new Checkbox(350,160, 200, 50),
    new TextBlock(40, 200, 500, 50)
  )

  for(var i in objs){
    objs[i].draw(rc)
  }
}