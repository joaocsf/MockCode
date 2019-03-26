import cv2 as cv
import numpy as np
import argparse
import random

def segment(path):
  print(path)
  image = cv.imread(path, cv.IMREAD_GRAYSCALE)
  _, thresh_img = cv.threshold(image, 128, 256, cv.THRESH_BINARY_INV)

  dst = cv.distanceTransform(thresh_img, cv.DIST_C, 0)
  cv.normalize(dst, dst, 0, 1.0, cv.NORM_MINMAX)

  color = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
  color2 = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
  color2[::] = (0,0,0)
  color3 = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
  color3[::] = (0,0,0)

  cv.imshow('Thresh', thresh_img)
  cv.imshow('Dst', dst)
  cv.waitKey()

  im2, contours, hierarchy = cv.findContours(thresh_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
  size = len(contours)

  levels = {}
  currLevel = 0

  for (a,b,c,d) in hierarchy[0]:
    if levels.__contains__(str(d)):
      continue
    else:
      levels[str(d)]=currLevel
      currLevel+=1

  maxLevel = currLevel-1

  for index, contour in enumerate(contours):
    idx = hierarchy[0][index][3]
    print(idx)
    level = levels[str(idx)]+1

    epsilon = 0.001*cv.arcLength(contour,True)
    contour = cv.approxPolyDP(contour,epsilon,True)
    if len(contour) > 200: continue
    clr = lerpColor(
      (0, 0, 0), (255, 255, 255),
      level/float(maxLevel+1)
    )
    print(maxLevel)
    cv.drawContours(color, [contour], -1, clr, -1)

    clr = (
      random.randint(0,256),
      random.randint(0,256),
      random.randint(0,256)
    )
    cv.drawContours(color2, [contour], -1, clr, -1)

    x,y,w,h = cv.boundingRect(contour)
    cv.rectangle(color3, (x,y), (x+w, y+h), clr, -1)

  cv.imshow('Hierarchy', color)
  cv.imshow('Elements', color2)
  cv.imshow('Rects', color3)


  cv.waitKey()

def lerpColor(a,b,l):
  r = (
    l*b[0] + (1-l)*a[0],
    l*b[1] + (1-l)*a[1],
    l*b[2] + (1-l)*a[2]
  )
  return r


def main():
  parser = argparse.ArgumentParser(description="Segmentation Test")
  parser.add_argument('path')

  args = parser.parse_args()

  segment(args.path)


if __name__ == "__main__":
    main()


