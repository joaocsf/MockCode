
document.addEventListener("DOMContentLoaded", startup)

module.exports = {
  generate_image(canvass, roughCanvas, text, boxes){
    onlyBoxes = boxes
    useText = text
    canvas = canvass
    canvas.width=width
    canvas.height=height
    context = canvas.getContext('2d');
    rc = roughCanvas.canvas(canvas)
    clear()
    randomizeStyle()
    drawGrid([width, height], rc)
    return lastObjs
  },

  regenerate_image(canvass, roughCanvas, text, boxes, lastObjss){
    onlyBoxes = boxes
    useText = text
    lastObjs = lastObjss
    style.stroke = onlyBoxes? 'white':'black'
    canvas = canvass
    context = canvas.getContext('2d');
    rc = roughCanvas.canvas(canvas)
    clear()
    redraw()
 
  },

  generateJSON(objects){
    return generateJSONFile(objects)
  }

}

var width = 800
var height = 900
var rc = null
var randomize = true
var style = {}
var randomOffset = 10
var noisyLines = 0.3
var drawBox = false
var useText = true
var boxOffset = 5
var gridSize = 100
var gridSpacing = 40
var currentGridSize = 100
var currentGridSpacing = 100
var context = undefined
var canvas = undefined
var lastObjs = []
var onlyBoxes = false

var fileName = "mock"
var fileIndex = 0

var caus = [0.2,0.4]
var currentCaus

function randomElement(){
  var elems = [
    {name: 'Picture'    , expand: 'a', split: 'n' },
    {name: 'Dropdown'   , expand: 'h', split: 'v', targetH: () => random(40,70)},
    {name: 'RadioButton', expand: 'v', split: 'v', targetH: () => random(30,50), addText: true},
    {name: 'Textfield'  , expand: 'h', split: 'v', targetH: () => random(40,70)},
    {name: 'Checkbox'   , expand: 'v', split: 'v', targetH: () => random(30,50), addText: true},
    {name: 'TextBlock'  , expand: 'a', split: 'v', targetH: () => random(40,70)},
    {name: 'Button'     , expand: 'a', split: 'v', targetH: () => random(40,70)},
    {name: 'Component'  , expand: 'n', split: 'n',},
    {name: 'Expand'     , expand: 'n', split: 'n',},
  ]

  var index = Math.floor(Number(random(0, elems.length)))
  return elems[index]
}
var buildObject = {
    Picture: (x,y,w,h) => new Picture(x,y,w,h),
    Dropdown: (x,y,w,h) => new Dropdown(x,y,w,h),
    RadioButton: (x,y,w,h) => new RadioButton(x,y,w,h),
    Textfield: (x,y,w,h) => new Textfield(x,y,w,h),
    Checkbox: (x,y,w,h) => new Checkbox(x,y,w,h),
    TextBlock: (x,y,w,h) => new TextBlock(x,y,w,h),
    Button: (x,y,w,h) => new Button(x,y,w,h),
    Debug: (x,y,w,h) => new Debug(x,y,w,h),
    Container: (x,y,w,h) => new Container(x,y,w,h),
    Component: (x,y,w,h) => new Component(x,y,w,h),
    Expand: (x,y,w,h) => new Expand(x,y,w,h),
}

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

  getAnnotation(){
    var name = this.constructor.name
    var dims = this.getBoxDims()
    return {
      class: name,
      x: dims[0],
      y: dims[1],
      w: dims[2],
      h: dims[3],
    }
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
    rc.rectangle(dims[0], dims[1],dims[2],dims[3],{stroke:color, roughness:0, strokeWidth:5})
  }

  onDraw(rc){
    for(var i in this.lines){
      var l = this.lines[i]
      strange_line(l[0], l[1], currentCaus)
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

class Component extends Drawable
{
  generate()
  {
    this.color = 'black'
    var points = rectPoints(this.x, this.y, this.w, this.h)
    this.w*=random(0.5,1.0)
    this.h*=random(0.5,1.0)

    var yOffset = 0.15
    var xOffset = 0.15
    var width = this.w*random(0.4,0.6)
    var height = this.h*random(0.4,0.6)
    this.centerA = 
    [this.x + this.w/2-width*random(0.2,0.4), this.y + this.h *random(0.5-yOffset,0.5+yOffset),
      width, height
    ]

    var width = this.w*random(0.4,0.6)
    var height = this.h*random(0.4,0.6)
    this.centerB = 
    [this.x + this.w/2+width*random(0.2,0.4), this.y + this.h *random(0.5-yOffset,0.5+yOffset),
      width, height
    ]

    this.min = [this.x,this.y]
    this.max = [this.x+this.w, this.y+this.h]
  }

  onDraw(rc){
    var stl = JSON.parse(JSON.stringify(style))
    var ellipse = this.centerA
    rc.ellipse(ellipse[0], ellipse[1], ellipse[2], ellipse[3], stl)
    var ellipse = this.centerB
    rc.ellipse(ellipse[0], ellipse[1], ellipse[2], ellipse[3], stl)
  }
}

class Expand extends Drawable
{
  generate()
  {
    this.color = 'red'
    this.w*=random(0.3,1.0)
    this.h*=random(0.3,1.0)

    this.lines = []
    var midY = this.y + this.h/2
    var midX = this.x + this.w/2

    var ptA = [midX, this.y + this.h]
    var ptA2 = [midX, this.y + this.h]
    var ptB = [this.x, midY]
    var ptC = [midX, this.y]
    var ptC2 = [midX, this.y]
    var ptD = [this.x + this.w, midY]

    var points = []
    points.push(ptA, ptB, ptB, ptC)
    points.push(ptA, ptC)
    points.push(ptA2, ptD, ptD, ptC2)

    if(randomize)
      mutate(points, 0.1)

    this.lines = []
    for(var p = 0; p < points.length-1; p+=2){
      var pA = points[p]
      var pB = points[p+1]
      this.lines.push([pA,pB])
    }
    this.min = [ptA[0], ptA[1]]
    this.max = [ptA[0], ptA[1]]
    this.update_min_max(points)
  }
}

class Container extends Drawable
{
  generate()
  {
    this.color = 'black'
    var points = rectPoints(this.x, this.y, this.w, this.h)

    this.lines = []
    if(randomize)
      mutate(points, 0.1)

    this.lines.push(
      [points[0], points[1]],
      [points[1], points[2]],
      [points[2], points[3]],
      [points[3], points[0]],
    )
    this.update_min_max(points)
  }

  onDraw(rc){
    var stl = JSON.parse(JSON.stringify(style))
    stl.stroke='black'
    for(var i in this.lines){
      var l = this.lines[i]
      strange_line(l[0], l[1], currentCaus, stl)
    }
  }
  
  //getAnnotation(){
    //return undefined
  //}
  drawBox(){

  }
}

class Checkbox extends Drawable
{
  generate()
  {
    this.color = '#006064'
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
      mutate(pts, 0.1)
      this.lines.push(
        [pts[0], pts[1]],
        [pts[1], pts[2]]
      )
    }
 
  }

  onDraw(rc){
    for(var i in this.lines){
      var l = this.lines[i]
      strange_line(l[0], l[1], random(0.0,0.2))
    }
  }
}

class Button extends Drawable
{
  generate() 
  {
    this.color = '#6D4C41'
    var points = rectPoints(this.x, this.y, this.w, this.h)
    this.lines = []
    if(randomize)
      mutate(points,0.5)

    this.lines.push(
      [points[0], points[1]],
      [points[1], points[2]],
      [points[2], points[3]],
      [points[3], points[0]],
    )
    for(var p in points){
      set_min_max(this.min, this.max, points[p])
    }

    this.hasText = useText? Math.random() > 0.5 : false

    if(this.hasText){
      var width = this.max[0] - this.min[0]
      var characters = width/20
      characters*=random(0.6,1.0)
      characters = Math.floor(characters)
      this.text = randomText(characters)
    }else{
      points = []
      var nPoints = this.w/50
      nPoints *= Math.random()/2+2
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
          rand[1] =2
        }
        
        if(i == nPoints-1){
          rand[0] =-2
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
    }

    for(var i = 0; i < points.length - 1; i++){
      set_min_max(this.min, this.max, points[i+1])
      this.lines.push(
        [points[i], points[i+1]]
      )
    }
  }

  onDraw(rc){
    super.onDraw()
    if(!this.hasText || onlyBoxes) return
    drawText(this.text,this.min,this.max)
  }
}

class RadioButton extends Drawable
{
  generate()
  {
    this.color = '#1565C0'
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
    this.color = '#6A1B9A'
    this.lines = []
    var points = []
    var nPoints = this.w/50
    nPoints *= Math.random()+2   
    var size = 1/(nPoints)
    size/=2
    var direction = Math.random() > 0.5
    var hOffset = 0.5 
    if(Math.random() > 0.5 || nPoints < 2){
      nPoints = 2
    }
    hOffset = 0.2

    nPoints = Math.floor(nPoints)

    this.hasText = useText? Math.random() > 0.5 : false
    //this.hasText = this.h < 30? false : this.hasText

    if(this.hasText && useText){
      var width = this.max[0] - this.min[0]
      var height = this.max[1] - this.min[1]

      if(this.h < 30){
        this.min[1]-=random(1.0,1 + 1/this.h)*(30-this.h)
        this.max[1]+=random(1.0,1 + 1/this.h)*(30-this.h)
        //rc.rectangle(this.x, this.y, this.w, this.h, {fill:'red'})
      }
      this.min[1]-=height*random(0,0.1)
      this.max[1]+=height*random(0,0.1)
      var characters = width/20
      characters*=random(0.6,1.0)
      characters = Math.floor(characters)
      this.text = randomText(characters)
    }else{

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
  }

  onDraw(rc){
    if(!this.hasText)
      rc.curve(this.points, style)
    else if(!onlyBoxes){
      drawText(this.text, this.min, this.max)
    }
  }
}

class Dropdown extends Drawable
{
  generate() 
  {
    this.color = '#558B2F'
    this.rnd = () => {
      return Math.random()*0.1 + 0.8
    }
    this.lines = []
    var points = rectPoints(this.x, this.y, this.w, this.h)
    if(randomize)
      mutate(points,0.5)
    
    var m1 = p_lerp(points[0], points[1], this.rnd())
    var m2 = p_lerp(points[3], points[2], this.rnd())
    var mid_line = [m1, m2]
    if(mutate)
      mutate(mid_line, 0.2)

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
    this.color ='#EF6C00'
    this.lines = []
    var points = rectPoints(this.x, this.y, this.w, this.h)

    if(randomize)
      mutate(points,0.6)

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
    this.color = '#D50000'
    this.lines = []
    var points = rectPoints(this.x, this.y, this.w, this.h)

    if(randomize)
      mutate(points)

    var cross = []
    cross.push(
      p_lerp(points[0],points[2], random(0.0, 0.3)),
      p_lerp(points[2],points[0], random(0.0, 0.3)),
      p_lerp(points[1],points[3], random(0.0, 0.3)),
      p_lerp(points[3],points[1], random(0.0, 0.3))
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

function clamp(v, min, max)
{
  return v < min? min : v > max? max : v
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

function strange_line(a,b, weight, stl){
  stl = stl || style
  var qrt = p_lerp(a,b,0.25)
  var mid = p_lerp(a,b,0.5)
  var qrt_2 = p_lerp(a,b,0.75)
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
  rc.curve(points, stl)  
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


//################
//# Initialize ###
//################

function startup(){
  canvas = document.getElementsByClassName('canvas')[0]
  canvas.width=width
  canvas.height=height
  context = canvas.getContext('2d');
  rc = rough.canvas(canvas)
  var offset = 10
  randomizeStyle()

  $('#debug').click(function(){
    drawBox = $(this).prop('checked') 
    clear()
    redraw()
  })
  $('#boxes').click(function(){
    onlyBoxes = $(this).prop('checked') 
    style.stroke = onlyBoxes? 'white':'black'
    clear()
    redraw()
  })
  $('#text').click(function(){
    useText = $(this).prop('checked') 
  })

  $('.generate').click(function (){
    drawBox = $('#debug').prop('checked') 
    clear()
    randomizeStyle()
    drawGrid([width, height], rc)

  })

  $('.save').mousedown(function (){
    var content = generateJSONFile(lastObjs)
    var fname = fileName+ ($('#text').prop('checked')? 'text': '')+fileIndex
    save(content, fname+".json", 'application/text')
    saveIMG(fname+".png")
    fileIndex+=1
  }).mouseup(function(){
  })
  drawGrid([width, height], rc)
  // draw(rc)
  //rc.circle(width/2, height/2, 90, style)
}



function createObj(obj, x,y,w,h){
  //return new window[obj](x,y,w,h)
  //obj.name = obj.name !== 'Debug'? 'Picture': 'Debug'
  if(! obj.name in buildObject){
    console.error(obj)
    return null
  }

  return buildObject[obj.name](x,y,w,h)
}

function addObject(object, objs){
  var splitV = object.split === 'v'

  if(splitV){
    var availabelHeight = object.h*(currentGridSize-currentGridSpacing/2)
    var targetHeight = object.targetH()
    
    
    var hSize = targetHeight / availabelHeight
    var hLeftOver = (availabelHeight% targetHeight)/2
    var offset = random(5,15)
    var hOffset = offset/availabelHeight
    var occurrences = Math.floor(availabelHeight/(targetHeight+offset))
    var startH = hLeftOver/availabelHeight *object.h

    var debug = {
      type: object.name,
      a_height: availabelHeight,
      t_height: targetHeight,
      hSize: hSize,
      hOffset: hOffset,
      occur: occurrences,
    }
    var addText = object.addText === true

    var copy = JSON.stringify(object)

    for(var i = 0; i < occurrences; i++){
      var newObj = JSON.parse(copy)
      newObj.y += startH + hOffset*object.h*i + hSize*object.h*i
      newObj.h = hSize*object.h
      objs.push(newObj)
      if(addText){
        var x = newObj.x + newObj.h *0.7
        var y = newObj.y
        var w = object.w - newObj.h*1.1
        var h = newObj.h
        objs.push(
          createObjHandler('TextBlock', x,y,w,h)
        )
      }

    }
  }else
    objs.push(object)
}

function createObjHandler(object, x,y,w,h){
  return {
    name:object,
    x:x,
    y:y,
    w:w,
    h:h
  }
}

function createDebugObj(x,y,w,h){
  return createObjHandler('Debug', x,y,w,h)
}

function populateGrid(gridSize){
  var grid = 1
  var gridCells = []
  var debugObjs = []
  for(var j = 0; j < gridSize[1]; j++){
    for(var i = 0; i < gridSize[0]; i++){
      grid+=1
      var cell = gridCells[i+'x'+j]
      
      if(cell !== undefined && cell.grid > 0)
        continue
      var expandH = Math.random() > 0.5
      var expandV = Math.random() > 0.5
    
      
      var expandHSize = expandH ?  Math.random()* (gridSize[0] - i - 1) : 0
      var expandVSize = expandV ?  Math.random()* (gridSize[1] - j - 1) : 0

      if(expandHSize+expandVSize < 2)
        expandHSize = expandVSize = 0

      var max = [i,j]
      
      var stop = false
      

      for(var y = 0; y <= expandVSize; y++){
        if(stop) break
        for(var x = 0; x <= expandHSize; x++){
          
          var xi = x+i
          var yj = y+j
          
          var near = gridCells[xi+'x'+yj]

          if(near !== undefined && near.grid > 0){
            max = [xi-1, yj]
            stop=true
            break
          }else
            gridCells[xi+'x'+yj] = {used: false, grid:grid}

          max[0] = Math.max(xi, max[0])
          max[1] = Math.max(yj, max[1])
        }
      }

      if(max[1] == j && max[0] == i){
        gridCells[i+'x'+j] = {used: false, grid:0}
        continue
      }
      var obj = createObjHandler('Container',i,j,max[0]-i+1, max[1]-j+1)
      debugObjs.push(obj)
    }
  }
  return [gridCells, debugObjs]
}


function decorateGrid(gridSize){
  var result = populateGrid(gridSize)
  var gridCells = result[0]
  var objs = result[1]
  for(var j = 0; j < gridSize[1]; j++){
    for(var i = 0; i < gridSize[0]; i++){
      var cell = gridCells[i+'x'+j]

      if(cell.used === true){
        continue
      }
      
      var grid = cell.grid

      var element = randomElement()

      cell.used = true
      var expand = element.expand
      var expandH = expand === 'a' || expand === 'h'
      var expandV = expand === 'a' || expand === 'v'
      
      expandH = Math.random() > 0.2 ? false : expandH
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
          
          var near = gridCells[xi+'x'+yj]
          if(near.used == true || near.grid != grid){
            max[0] = clamp(xi-1, i, gridSize[0])
            max[1] = clamp(yj-1, j, gridSize[1])
            stop=true
            break
          }else

          max[0] = Math.max(xi, max[0])
          max[1] = Math.max(yj, max[1])
        }
      }

      for(var y = j; y <= max[1]; y++){
        for(var x = i; x <= max[0]; x++){
          gridCells[x+'x'+y].used = true
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
  currentGridSize = gridSize * random(1.0,1.5)
  currentGridSpacing = gridSpacing * random(0.5,1.0)

  var offset = random(10,20)
  var cell = currentGridSize + currentGridSpacing + offset/2
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
    var x = offsetX + obj.x * currentGridSize + currentGridSpacing * obj.x
    var y = offsetY + obj.y * currentGridSize + currentGridSpacing * obj.y

    var w = currentGridSize * obj.w + currentGridSpacing * (obj.w-1)
    var h = currentGridSize * obj.h + currentGridSpacing * (obj.h-1)
    if(obj.name == 'Container'){
      var spacing = currentGridSpacing*random(0.4,0.8)
      x-=spacing/2
      y-=spacing/2
      w+=spacing
      h+=spacing
    }

    var obj = createObj(obj, x, y, w, h)

    objs.push(obj)
  }

  for(var i in objs){
    objs[i].draw(rc)
  }

  lastObjs = objs
}

function redraw() {
  for(var i in lastObjs)
    lastObjs[i].draw(rc)
}

function clear(){
  context.fillStyle = 'white'
  context.fillRect(0,0, canvas.width, canvas.height)
}

function randomizeStyle(){

  currentCaus = random(caus[0], caus[1])
  style = {
    stroke: onlyBoxes? 'white': 'black',
    roughness: Math.random()*0.5,
    bowing: Math.random()*10,
    strokeWidth:Math.random()*4+1,
    hachureGap: Math.random()*4
  }
}

function randomText(chars){
  var text = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  var res = ''

  for(var i = 0; i < chars; i++){
    res+=text.charAt(Math.floor(Math.random()*text.length))
  }

  return res;
}

function drawText(text, min, max){
  var height = max[1] - min[1]
  var width =  max[0] - min[0]

  context.font=height+"px Daniel font"

  var textWidth = context.measureText(text).width
  var textHeight = context.measureText(text).height

  var realHeight = height
  var leftOver = width-textWidth
  var leftOverH = height-textHeight

  if(textWidth>width){

    var finalWidth = width*random(0.6,1.0)
    leftOver = width - finalWidth

    realHeight = height * finalWidth / textWidth
  }

  if(textHeight>height){
      realHeight = height*random(0.6,1.0)
  }
  realHeight *=random(0.8,1.0)
  leftOverH = height-realHeight
  
  context.font=realHeight+"px Daniel font"
  var x = min[0] + leftOver*Math.random()
  var y = max[1] - leftOverH*Math.random()

  context.fillStyle="#000"
  context.fillText(text, x, y)
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

function save(content, fileName, contentType){
  $("<a/>",
  {
    download: fileName,
    href: "data:"+contentType+"," + content
  }
  ).appendTo('body').click(function(){
    $(this).remove()
  })[0].click()
}

function saveIMG(fileName){
  var url = canvas.toDataURL("image/png");
  var win = window.open(url)
  win.close()

  $("<a/>",
  {
    download: fileName,
    href: url
  }
  ).appendTo('body').click(function(){
    $(this).remove()
  })[0].click()
}

function generateJSONFile(objects){
  var json = [
  ]
  
  for(var index in objects){
    var obj = objects[index]
    var result = obj.getAnnotation()
    if(result != undefined)
      json.push(result)
  }
  return JSON.stringify(json)
}