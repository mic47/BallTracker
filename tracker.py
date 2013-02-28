import cv2
import cv
from time import time

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
        

def trackBall(filename):
    count = 0
    start = time()
    fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', 'X')
    cv2.namedWindow('img')
    writer = cv2.cv.CreateVideoWriter('binary.mpg', fourcc, 25, (352, 288))
    first = None
    for image in getImagesIterable(filename):

        grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        if first == None:
            first = cv2.blur(grayscale, (10,10))
            
            continue
        _, binary = cv2.threshold(grayscale, 100, 255, cv2.THRESH_BINARY)
        cv2.imshow('img', binary)

        if cv2.waitKey() == 1048603:
            break
#        cv2.cv.WriteFrame(writer, image2something(image))
        if count ==0:
            cv2.imwrite('lala.png', binary)
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
    arg = parser.parse_args()
    trackBall(arg.video)
    
    