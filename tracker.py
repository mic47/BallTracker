import cv2
import cv
from time import time
import numpy
import math
import random

import argparse

def getImagesIterable(filename):
    video = cv2.VideoCapture(filename)
    print(video.get(3), video.get(4), video.get(6))
    while True:
        ret = video.read()
        if ret[0] == False:
            break
        #yield ret
        yield ret[1]


def image2something(source):
    bitmap = cv2.cv.CreateImageHeader(
        (source.shape[1], source.shape[0]),
        cv2.IPL_DEPTH_8U, 3)    
    cv2.cv.SetData(bitmap, source.tostring(), 
           source.dtype.itemsize * 3 * source.shape[1])
    return bitmap
        

def trackBall(filename, threshold, empty_frame):
    count = 0
    start = time()
    fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
    cv2.namedWindow('img')
    writer = cv2.cv.CreateVideoWriter('binary.mpg', fourcc, 25, (352, 288))
    first = None
    for image in getImagesIterable(filename):

        image *= 3

        grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        if first == None or count == empty_frame:
            first = grayscale#cv2.blur(binary, (10,10))
            firstAvg = numpy.average(first)
            count += 1
            continue
        if count < 800 or (count > 1400 and count < 4000):
            count += 1
            continue
        grayscaleAvg = numpy.average(grayscale)
        difference = cv2.subtract(
                    #first,
                    numpy.array(
                        numpy.array(
                            first, 
                            dtype=numpy.float32
                        ) * (grayscaleAvg / firstAvg),
                        dtype=grayscale.dtype
                    ),
                    grayscale,
                    #first 
                    #numpy.array(
                    #    numpy.array(
                    #        first, 
                    #        dtype=numpy.float32
                    #    ) * (grayscaleAvg / firstAvg),
                    #    dtype=grayscale.dtype
                    #),
                ) 
        I = cv2.threshold(
                difference,
                threshold,
                255,
                cv2.THRESH_BINARY
            )[1]
        II = numpy.array(I)
        contours, _ = cv2.findContours(II, cv2.cv.CV_RETR_LIST, cv2.cv.CV_CHAIN_APPROX_SIMPLE)
        newc = []
        best = None
        bestVal = 1000
        coords = []
        for contour in contours:
            area = cv2.contourArea(contour)
            points = []
            for c in contour:
                for x in c:
                    points.append(x)
            minX = min([x for x, _ in points])
            maxX = max([x for x, _ in points])
            minY = min([x for _, x in points])
            maxY = max([x for _, x in points])
            dX = maxX - minX
            dY = maxY - minY
            #print (maxX, minX, maxY, minY, contour)
            if dX == 0 or dY ==0:
                continue
            all_area = dX * dY
            expectedArea = (min(dX, dY)/2.0)**2 * math.pi
            diff_in_area = abs(area - expectedArea)
            if all_area < 50 or diff_in_area / area > 0.4 or area > 300:
                continue
            print ('lol', area, all_area, expectedArea, diff_in_area / area)
            ratio = diff_in_area / area
            if ratio < bestVal:
                bestVal = ratio
                best = len(newc)
            newc.append(contour)
            #coords.append(((minX + maxX) / 2, (minY + maxY) / 2, ratio, )) #TODO
        if len(newc) == 0:
            print('=====================================')
        contours = numpy.array(newc)
        
        #print contours
        col = 128
        cv2.drawContours(I, contours, -1, (col,col,col), -1)
        col = 200
        if best != None:
            cv2.drawContours(I, contours, best, (col,col,col), -1)
        #=======================================================================
        # for x in range(len(contours)):
        #    col = 128 + (x%16)*4
        #    cv2.drawContours(I, contours, x, (col,col,col), -1)
        # 
        #=======================================================================
        #cv2.circle(I, (100,100), 5, (200,200,200))
        #circles = cv2.HoughCircles(I, cv2.cv.CV_HOUGH_GRADIENT, 1, 1)
        #if circles != None:
        #    print(circles[0])
        #    for circle in circles[0]:
        #        radius = circle[2]
        #        center = (circle[0], circle[1])
        #        cv2.circle(I, center, radius, (200, 200, 200), 1, 8, 0)
        show = numpy.vstack([numpy.hstack([I, grayscale]), numpy.hstack([difference, II])])
        print(firstAvg, grayscaleAvg)
        cv2.imshow('img', show)
        #cv2.imshow('img2', image)
        if count % 100 >= 0:
            print(count)
            if cv2.waitKey(1) == 27:
                break
#        cv2.cv.WriteFrame(writer, image2something(image))
        if count ==0:
            cv2.imwrite('lala.png', I)
        count += 1
        if count %1000 ==0:
            #print image
            #print "ahoj"
            #print binary
            now = time()
            print(now, count, count/(now - start), now-start)
    print(count)  
    



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=str, help="input video")
    parser.add_argument('threshold', type=int, default=15)
    parser.add_argument('empty_frame', type=int, default=400)
    arg = parser.parse_args()
    trackBall(arg.video, arg.threshold, arg.empty_frame)
    
    
