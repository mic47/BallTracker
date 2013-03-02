import cv2
import time
import numpy
import math
import random
import sys

import argparse

def L2(x, y):
    return math.sqrt(sum([(a-b)**2 for a, b in zip(x, y)]))


class GlobalParameters:
    imageMult = 3
    ballRatioThres = 0.4
    ballMinVolume = 50
    ballMaxVolume = 300
    frameCount = -1
    captureDevice = None
    binaryThreshold = 70
    trackerMinLivespan = 20
    trackerMaxDistance = 10
    trackerMaxFrameMissing = 20
    speed = 10
    
glob = GlobalParameters()


class ObjectTracker:
    
    def __init__(self):
        self.archived = []
        self.objects = []
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
                       (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    
    
    def archiveObjects(self, frame):
        # Archive objects
        global glob
        for i in range(len(self.objects)):
            if frame - self.objects[i][-1][2] < glob.trackerMaxFrameMissing:
                continue
            if len(self.objects[i]) >= glob.trackerMinLivespan:
                self.archived.append(self.objects[i])
            self.objects[i] = None
        self.objects = [x for x in self.objects if x != None]
    
    
    def addObject(self, point, radius, frame, time):
        global glob
        if len(self.objects) > 0:
            nearest = min(
                [(L2(point, self.objects[i][-1][0]), i) 
                 for i in range(len(self.objects))]
            )
            if nearest[0] > glob.trackerMaxDistance:
                nearest = None
        else:
            nearest = None
        
        hist = (point, radius, frame, time)
        
        if nearest != None:
            index = nearest[1]
            _, _, fr, _ = self.objects[index][-1]
            if frame - fr > glob.trackerMaxFrameMissing:
                nearest = None
            else:
                self.objects[index].append(hist)
        if nearest == None:
            self.objects.append([hist])
        
        
    def drawObjects(self, Image, frame):
        while len(self.objects) > len(self.colors):
            self.colors.append((
                random.randint(0, 255), 
                random.randint(0, 255),
                random.randint(0, 255),
            ))
        index = -1
        for obj in self.objects:
            index += 1
            if obj[-1][2] != frame:
                continue
            point = obj[-1][0]
            radius = obj[-1][1]
            for f, t in zip(obj, obj[1:]):
                cv2.line(Image, f[0], t[0], self.colors[index])
            cv2.circle(Image, point, radius, self.colors[index], 2, 8, 0)
            

def getImagesIterable(captureDevice):
    while True:
        ret = captureDevice.read()
        if ret[0] == False:
            break
        #yield ret
        yield ret[1]


def changeThreshold(x):
    global glob
    glob.binaryThreshold = x
    
    
def changeImageMultiplication(x):
    global glob
    if x > 0:
        glob.imageMult = float(x) / 10
    
        
def changeBallRatioThresh(x):
    global glob
    glob.ballRatioThres = float(x) / 100
    
    
def changeBallMinVolume(x):
    global glob
    glob.ballMinVolume = x


def changeBallMaxVolume(x):
    global glob
    glob.ballMaxVolume = x


def changeTrackerMissingFrames(x):
    global glob
    glob.trackerMaxFrameMissing = x


def changeTrackerMaxDistace(x):
    global glob
    glob.trackerMaxDistance = x

    
def changeTrackerMinLivespan(x):
    global globs
    glob.trackerMinLivespan = x

    
def changeSpeed(x):
    global globs
    glob.speed = x


def createGUI(single_window_mode):
    global glob
    cv2.namedWindow('img')
    settings_window = 'img'
    if not single_window_mode:
        cv2.namedWindow('settings',  cv2.cv.CV_WINDOW_NORMAL)
        cv2.cv.ResizeWindow('settings', 800, 200)
        settings_window = 'settings'
    cv2.cv.CreateTrackbar('Frame #', 'img', 0, glob.frameCount,
                          lambda _: None)
    cv2.cv.CreateTrackbar('Time per frame (in ms)', 'img', glob.speed,
                          1000, changeSpeed)
    cv2.cv.CreateTrackbar('Threshold', settings_window, 
                          glob.binaryThreshold, 255, changeThreshold)
    cv2.cv.CreateTrackbar('Image multiplication', settings_window, 
                          int(glob.imageMult*10), 100,
                          changeImageMultiplication)
    cv2.cv.CreateTrackbar('Circle detect ratio (%)', settings_window, 
                          int(glob.ballRatioThres*100),
                          100, changeBallRatioThresh)
    cv2.cv.CreateTrackbar('Circle min volume (pixels)', settings_window,
                          glob.ballMinVolume, 10000, changeBallMinVolume)
    cv2.cv.CreateTrackbar('Circle max volume (pixels)', settings_window,
                          glob.ballMaxVolume, 10000, changeBallMaxVolume)
    cv2.cv.CreateTrackbar('Max missing frames', settings_window,
                          glob.trackerMaxFrameMissing, 1000,
                          changeTrackerMissingFrames)
    cv2.cv.CreateTrackbar('Max distance to match (pixels)',
                          settings_window, glob.trackerMaxDistance,
                          100, changeTrackerMaxDistace)
    cv2.cv.CreateTrackbar('Min livespan of object (in captured frames)',
                          settings_window, glob.trackerMinLivespan,
                          1000, changeTrackerMinLivespan)


def shouldSkip(position, skip):
    for f, t in skip:
        if f <= position and position < t:
            return True
    return False


def getFrame(filename, frame_number):
    video = cv2.VideoCapture(filename)
    while frame_number > video.get(cv2.cv.CV_CAP_PROP_POS_FRAMES):
        video.grab()
    return video.read()
    video.release()


def trackBall(filename, output_file, skip, empty_frame, 
              single_window_mode=False, noGUI=False):
    global glob
    start = time.time()
    
    _, first = getFrame(filename, empty_frame)
    first = cv2.cvtColor(first, cv2.COLOR_RGB2GRAY)
    firstAvg = numpy.average(first)
    print('Grabbed first frame in {time} seconds.'.format(
        time=time.time() - start))
    
    start = time.time()
    video = cv2.VideoCapture(filename)
    glob.frameCount = int(video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    glob.captureDevice = video
    iterable = getImagesIterable(video)
    
    if not noGUI:
        createGUI(single_window_mode)
    time.clock()
    lastTime = time.clock()
    
    tracker = ObjectTracker()
    nextFrameTime = glob.captureDevice.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
    nextFrame = int(glob.captureDevice.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))
    for image in iterable:
        
        currentFrame = nextFrame
        currentFrameTime = nextFrameTime
        nextFrame = int(glob.captureDevice.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))
        nextFrameTime = glob.captureDevice.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
        
        if not noGUI:
            cv2.setTrackbarPos('Frame #', 'img', currentFrame)
        image *= glob.imageMult

        grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
       
        if shouldSkip(currentFrame, skip):
            continue
        grayscaleAvg = numpy.average(grayscale)
        difference = cv2.subtract(
                    numpy.array(
                        numpy.array(
                            first, 
                            dtype=numpy.float32
                        ) * (grayscaleAvg / firstAvg),
                        dtype=grayscale.dtype
                    ),
                    grayscale,
                ) 
        I = cv2.threshold(
                difference,
                glob.binaryThreshold,
                255,
                cv2.THRESH_BINARY
            )[1]
        II = numpy.array(I)
        contours, _ = cv2.findContours(II, cv2.cv.CV_RETR_LIST, 
                                       cv2.cv.CV_CHAIN_APPROX_SIMPLE)
        newc = []
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
            if dX == 0 or dY ==0:
                continue
            all_area = dX * dY
            expectedArea = (min(dX, dY)/2.0)**2 * math.pi
            diff_in_area = abs(area - expectedArea)
            if area == 0:
                area = 0.000001
            if all_area < glob.ballMinVolume or \
               diff_in_area / area > glob.ballRatioThres or \
               area > glob.ballMaxVolume:
                continue
            newc.append(contour)
            tracker.addObject(((maxX + minX)/2, (maxY + minY)/2), min(dX, dY)/2,
                              currentFrame, currentFrameTime)
        contours = numpy.array(newc)
        tracker.archiveObjects(currentFrame)
        if not noGUI:
            col = 128
            cv2.drawContours(I, contours, -1, (col,col,col), -1)
            col = 200
            
            grayscale = cv2.cvtColor(grayscale, cv2.COLOR_GRAY2RGB)
            I = cv2.cvtColor(I, cv2.COLOR_GRAY2RGB)
            difference = cv2.cvtColor(difference, cv2.COLOR_GRAY2RGB)
            first2 = cv2.cvtColor(first, cv2.COLOR_GRAY2RGB)
            tracker.drawObjects(I, currentFrame)
            tracker.drawObjects(grayscale, currentFrame)
            show = numpy.vstack([
                numpy.hstack([I, grayscale]),
                numpy.hstack([difference, first2])
            ])
            cv2.imshow('img', show)
     
            actTime = time.clock()
            deltaTime = int((actTime - lastTime) * 1000)
            waitTime = glob.speed - deltaTime
            lastTime = actTime
            if waitTime < 1:
                waitTime = 1  
            if cv2.waitKey(waitTime) == 27:
                break
            
        if currentFrame % 1000 == 0 and currentFrame > 0:
            now = time.time()
            print('{progress:3}% done in {time} seconds, should finish ' + \
                  'in {estimate} seconds.'.format(
                progress=100 * currentFrame / glob.frameCount, 
                time=now - start,
                estimate = (glob.frameCount - currentFrame) * (now - start) / 
                    currentFrame
            ))
    



if __name__ == "__main__":
    #TODO: umoznit skipovat
    #TODO: ked skonci program, vypis command-linove parametre
    #TODO: ukladanie do suboru
    #TODO: zapametanie si casu framu
    parser = argparse.ArgumentParser()
    parser.add_argument('video', type=str, help="input video")
    parser.add_argument('output', type=str, help="output file")
    parser.add_argument('--binaryThreshold', type=int, default=70, 
                        help='Anything with color less than threshold will ' + 
                        'be black, other will be white.')
    parser.add_argument('--emptyFrame', type=int, default=400, 
                        help='Index of frame that is empty.')
    parser.add_argument('--imageMult', type=int, default=3, 
                        help='How much to brighten image.')
    parser.add_argument('--ballRatioThreshold', type=float, default=0.4, 
                        help='Allowed deviation of volume from circle for ' +
                        'detected object (0 = perfect circle).')
    parser.add_argument('--ballMinVolume', type=int, default=50, 
                        help='Objects with volume less than this will be ' + 
                        'discarded.') 
    parser.add_argument('--ballMaxVolume', type=int, default=300, 
                        help='Objects with volume more than this will be ' +
                        'discarded.')
    parser.add_argument('--trackerMinLivespan', type=int, default=20, 
                        help='Objects with shorter history that provided ' +
                        'value will be discarded (not saved to the output).')
    parser.add_argument('--trackerMaxDistance', type=int, default=10, 
                        help='If object will move more than this from his ' +
                        'last detected frame, consider it as new object.')
    parser.add_argument('--trackerMaxMissingFrames', type=int, default=20, 
                        help='If object will not be detected for more than' +
                        ' this number of frames, it will be considered dead.')
    parser.add_argument('--speed', type=int, default=10, help='Delay in ' +
                        'milliseconds between showing next frame.')
    parser.add_argument('--singleWindow', action="store_true", 
                        help='Settings will be in the same window as image ' +
                        '(good for tall monitors).')
    parser.add_argument('--noGUI', action='store_true', 
                        help='Just process file and provide output.')
    parser.add_argument('--skip', nargs='+', default=[], 
                        help='Even number of arguments -- intervals of ' +
                        'frames that can be skipped')
    arg = parser.parse_args()
    skip = []
    if len(arg.skip) % 2 != 0:
        sys.stderr.write('Skip must have even number of arguments.')
        exit(1)
    for x in range(0, len(arg.skip), 2):
        skip.append((int(arg.skip[x]), int(arg.skip[x + 1])))
    glob.binaryThreshold = arg.binaryThreshold
    glob.imageMult = arg.imageMult
    ballRatioThres = arg.ballRatioThreshold
    ballMinVolume = arg.ballMinVolume
    ballMaxVolume = arg.ballMaxVolume
    trackerMinLivespan = arg.trackerMinLivespan
    trackerMaxDistance = arg.trackerMaxDistance
    trackerMaxFrameMissing = arg.trackerMaxMissingFrames
    speed = arg.speed
    trackBall(
        arg.video,
        arg.output,
        skip,
        arg.emptyFrame,
        arg.singleWindow,
        arg.noGUI
    )