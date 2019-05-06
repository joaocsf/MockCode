global.document = {
  addEventListener: (a,b) => { return false;}
}
const { createCanvas, registerFont } = require('canvas')
const rough = require('roughjs')
const drawer = require('./js/app.js')
const fs = require('fs')

registerFont('./src/sass/fonts/Daniel-Regular.otf', { family: 'Daniel font' })
const canvas = createCanvas(800, 900)

var dir= "../data/"
var index = 0
var text = false
var numFiles = 12000

mkdir(dir + "image")
mkdir(dir + "annotation")
mkdir(dir + "mask")

var startTime = process.hrtime();
var elapsedTime = 0

for(var i = 0; i < numFiles; i++){

  elapsedTime += process.hrtime(startTime)[1]/1000000
  var perFile = elapsedTime/i
  var toFinish = (numFiles - i)*perFile

  generateMockup(dir, text, index)
  index++
  //text=!text 
  progressbar((i+1)/ numFiles, 50, "Generating", formatDate(toFinish)+ "  Mock"+index)
}

function formatDate(ms){
  var minutes = Math.floor(ms / 60000)
  var seconds = Math.floor( (ms/1000)%60 ).toFixed(0)
  var hours = Math.floor(minutes/60)
  minutes = Math.floor(minutes%60)
  return hours+":"+fixedString(minutes,2,"0")+":"+fixedString(seconds,2,"0")
}

function fixedString(string, size, char){
  char = char || ' '
  return (char.repeat(size) + string).slice(-size)
}

function progressbar(percentage, size, prefix, suffix){
  var fill = Math.floor(percentage*size)
  var toFill = size - fill

  fill = "=".repeat(fill)
  toFill = "-".repeat(toFill)
  
  percentage = fixedString(Math.floor(percentage*100), 3)
  suffix = fixedString(suffix, 20)
  print(prefix+"[" + fill + toFill + "] " + percentage + "% " + suffix + "\r")

}

function print(text){
  process.stdout.write(text)
}

function mkdir(dir){
  if (!fs.existsSync(dir)){
    fs.mkdirSync(dir);
  }
}

function generateMockup(dir, text, index){
  normalName = dir + '/image/'    + index + '.png'
  boxesName  = dir + '/mask/'     + index + '.png'
  objsName   = dir + 'annotation/'+ index + '.json' 
  
  objs = drawer.generate_image(canvas, rough, text, false)
  var normalImage = canvas.toBuffer()
  fs.writeFileSync(normalName, normalImage)

  fs.writeFileSync(objsName, drawer.generateJSON(objs))

  drawer.regenerate_image(canvas, rough, text, true, objs)
  var boxesOnly = canvas.toBuffer()
  fs.writeFileSync(boxesName, boxesOnly)
}




