
# coding: utf-8

# # SETUP

# In[1]:


import os, os.path
import pandas as pd
import numpy as np
## This is disabled for now, enable it for debugging in anaconda
#import matplotlib.pyplot as plt
import abc
import cv2
from abc import ABCMeta, abstractmethod
from collections import namedtuple
### Below is only for debugging, remove if exporting to script


# # METHODS

# In[2]:


def detectChange(im1, im2, show = False):
    '''
    Detects the potential changes (in the form of blue circles) from im1 to im2.
    show=True shows all the potential detected circles
    '''
    pix = []
    found = []
    ret = []
    contained = False
    
    ### Make thresholded derivative and pad both images
    # Derivative is a combination of only blue pixels and all changed pixel
    # If the deriv > 20k, assume it's a page turn
    isDiff = (np.sqrt(np.mean((im2.astype(float) - im1)**2, axis=2)) > 100)
    if np.sum(isDiff) > 20000:
        return 'turn'
    isBlue = (np.sqrt(np.sum((im2.astype(float) - [0,158,233])**2, axis=2)) < 100)
    changed = isDiff & isBlue
    pim2 = np.lib.pad(im2, ((20,20),(20,20),(0,0)), 'constant', constant_values=0)
    changed = np.lib.pad(changed, 20, 'constant', constant_values=0)

        
    ### Detect non-black pixels, ignoring the top, left, and right 50 pixels
    y, x = np.where(changed[50:,50:-50]>0)
    x = x + 50
    y = y + 50
    
    ### Generate potential matches fom non-black pixels. Attempts to get rid of dupes
    for cd in range(len(x)):
        temp = estimate(changed, x[cd], y[cd])
        if temp[2] < 5:
            continue
        if not found:
            found.append(temp)
        else:
            for f in found:
                if f[0]-f[2]*3<=x[cd]<=f[0]+f[2]*3 and f[1]-f[2]*3<=y[cd]<=f[1]+f[2]*3:
                    contained = True
                    break
            if not contained:
                found.append(temp)
            contained = False
   
   
    ### Filter the potential matches
    for f in found:
        temp = match(pim2, f[1], f[0], f[2], changed, show)
        if temp < 100:
            f.append(temp)
            ret.append(f)
        
    ### Convert return to named tuple.
    Point = namedtuple('point', 'x y rad err')
    nt = []
    for point in ret:
        ntp = Point(int(point[0]), int(point[1]), int(point[2]), int(point[3]))
        nt.append(ntp)
    
    return nt

def estimate(im, xc, yc):
    '''
    Estimates the radius and x+y coordinate of a circle given the image and the x and y coordinates
    '''
    box = im[yc-25:yc+25, xc-25:xc+25]
    # Creates an array of increasing numbers from the top left corner, which is then weighted to find the 'center'
    y, x = np.mgrid[0:box.shape[0], 0:box.shape[1]]
    rxc = np.sum(x * box) / np.sum(box)
    ryc = np.sum(y * box) / np.sum(box)
    rad = 2 * np.sqrt(np.sum(((y - ryc) * box) ** 2) / np.sum(box))
    
    return [xc-25+rxc, yc-25+ryc, rad]
    

import math
def match(im, yc, xc, radius, change, show=False):
    '''
    Given an image, x and y coordinates, radius, and derivative, calculates the error
    Can the matched circle (default is False, shows nothing. 1 shows only those > 100 error, True shows all)
    '''
    # Throw away anything with lower than the minimum radius
    row = math.floor(yc - radius - 2)
    col = math.floor(xc - radius - 2)
    side = max(math.ceil(xc + radius + 2) - col, math.ceil(yc + radius + 2) - row) 
    # snip the box from the image, handle edge cases here
    box = im[row:row+side, col:col+side]
    # get the blue color we're matching, I guessed at this
    blue = np.array([0,158,223])
    # compute the difference to the blue color
    diff = np.sqrt(np.sum((box - blue)**2, axis=2))
    # create the mask
    x = np.arange(side) + col
    y = np.arange(side) + row
    y.shape = (-1,1)
    r = np.sqrt((x - xc)**2 + (y - yc)**2)
    mask = np.clip(radius - r, -1, 1) / 2 + 0.5
    # the error is sum normalized by the square of the number of 1's in the mask, a hack
    c = change[row:row+side, col:col+side]
    # Throw away anything with less than 5% white pixels
    if (np.sum(c)/(side**2))*100 < 5:
        return 1000000
    err = np.sum(diff * mask * c) / np.sum(c * mask)
    if show:
        print(err, xc, yc, radius)
        fig = plt.figure()
        plt.subplot(151)
        plt.imshow(box)
        plt.subplot(152)
        plt.imshow(diff, cmap='gray')
        plt.subplot(153)
        plt.imshow(mask, cmap='gray')
        plt.subplot(154)
        plt.imshow(diff * mask * c, cmap='gray')
        plt.subplot(155)
        plt.imshow(c)
        plt.show()

    return err




# # CLASSES

# In[3]:


### Really messy, but it works...

class Data(abc.ABC):
    __metaclass__ = ABCMeta
    
    
    def __init__(self):
        self.data = {}
        
    def __len__(self):
        return len(self.data)
    
    @abstractmethod
    def getData(self, subset = None): 
        if type(subset) == int:
            return self.data[subset]
        else:
            return self.data
        
    @abstractmethod
    def append(self): pass

    @abstractmethod
    def __str__(self): pass
    
    @abstractmethod
    def toList(self): pass
    
    
    def isEmpty(self):
        return not bool(len(self.data))

    def perror(self, good, bad):
        raise ValueError('Incorrect Parameter passed')   
    
class VideoData(Data):
   
    dataType = 'Page'
    basepath = ''

    def __init__(self, name = None, ftdims = None, fpdims = None, init = None, end = None):
        super().__init__()
        self.name = name
        self.fpdims = fpdims
        self.ftdims = ftdims
        self.pdims = [229, 619, 33, 415]
        self.tdims = [180, 661, 410, 460]
        self.frames = []
        if not init == None:
            self.init = int(init)
        else:
            self.init = 0
        self.end = int(end)

        
    def split(self):
        # It's hard coded for now, I'll fix it later
        vc = cv2.VideoCapture('app/static/temp/video/'+self.name)
        if vc.isOpened():
            rval, frame = vc.read()
        else:
            print('failed to open video using opencv (mp4-con)')
            rval = False
            return
        vc.set(cv2.CAP_PROP_POS_FRAMES, self.init)
        c = 0
        while c < self.end-self.init:
            rval, frame = vc.read()
            if type(frame) == np.ndarray:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frames.append(frame)
            c+=1
        vc.release
        return self.frames
    
    def setFrames(self, frames):
        # Only for debugging purposes
        self.frames = frames
        
    def extractFrames(self):
        page = PageData()
        for x in range(len(self.frames) - 1):
            im1 = self.frames[x]
            im2 = self.frames[x+1]
            temp = detectChange(im1, im2)
            if type(temp) == str:
                if len(page) >= 5:
                    self.append(page)
                    page = PageData()
            else:
                page.append(temp, x+1)
        self.append(page)
    
    def setData(self, data):
        # Only for debugging purposes
        self.data = data
        
        
        
    def extractCSV(self):
        csv = pd.read_csv('path'+self.csv)
        
        for page in csv.Page.unique():
            a = csv[csv.Page == page].itertuples()
            r = next(a)
            # Correspond as such: left right top bottom : pic = 7 8 9 10   ;  text = 11 12 13 14
            self.csvPDims[r.Page] = [[r._7, r._9, 1], [r._8, r._9, 1], [r._7, r._10, 1], [r._8, r._10, 1]]
            self.csvTDims[r.Page] = [[r._11, r._13, 1], [r._12, r._13, 1], [r._11, r._14, 1], [r._12, r._14, 1]]
        self.convertDims()
    
    def convertDims(self):
        # This is the pixel dimensions of the picture for the first slide. Only used to calculate the conversion
        pdim = self.pdims
        # Pixel coordinates for top left, top right, bottom left, bottom right respectively
        PD = [[pdim[0],pdim[2]], [pdim[1],pdim[2]], [pdim[0],pdim[3]], [pdim[1],pdim[3]]]
        
        XY = self.csvPDims[1]
        sol = np.linalg.lstsq(XY, PD)
        
        for d in self.csvPDims:
            self.pixPDims[d] = (np.dot(self.csvPDims[d], sol[0])).astype(int)
        for d in self.csvTDims:
            self.pixTDims[d] = (np.dot(self.csvTDims[d], sol[0])).astype(int)
            
    def getFrames(self, subset = None):
        if type(subset) == int:
            return self.frames[subset]
        else:
            return self.frames
        
    def getData(self, subset = None):
        return super().getData(subset)
    
    def append(self, data):
        if type(data) != PageData:
            perror(self, data)
        else:
            self.data[len(self)] = data 
   
    
    def __str__(self):
        a = ""
        for key in self.data:
            b = str(self.dataType+str(key)) + '\n'
            c = str(self.data[key])
            a += (b + c + '\n')
        return str(a)
    

        
    def toList(self):
        ret = []
        for page in range(len(self.data)):
            if page == 0:
                pdim = self.fpdims
                tdim = self.ftdims
            else:
                pdim = self.pdims
                tdim = self.tdims
            temp = self.data[page].toList(page, pdim, tdim)
            ret.extend(temp)
        return ret
            
    
class PageData(Data):

    dataType = '        Frame'
    
    
    def getData(self, subset = None):
        return super().getData(subset)
        
    def append(self, data, frame):
        if type(data) != list or type(frame) != int:
            raise ValueError('Incorrect Parameter passed: %s vs list or %s vs int' 
                             %(str(type(data), str(type(frame)))))
        if frame in self.data:
            self.data[frame].append(data)
        else:
            self.data[frame] = data

    def extend(self, other):
        if type(other) != PageData:
            perror(self, other)
        odata = other.getData()
        for frame in odata:
            self.append(odata[frame], frame)
    
    def __str__(self):
        a = ""
        for key in self.data:
            if len(self.data[key]) == 0:
                continue
            b = str(self.dataType+str(key))
            c = str(self.data[key])
            a += (b + c + '\n')
        return str(a)
 
    def toList(self, page, pdim, tdim):
        ret = []
        for dkey in self.data:
            temp = self.data[dkey]
            num = len(temp)
            if num == 0:
                continue
            framelen = 100/num
            count = 0
            for point in temp:
                if pdim[0]<=point.x<=pdim[1] and pdim[2]<=point.y<=pdim[3]:
                    loc = 1
                elif tdim[0]<=point.x<=tdim[1] and tdim[2]<=point.y<=tdim[3]:
                    loc = 2
                else:
                    loc = 0
                #print(pdim, tdim)
                ret.append([page + 1, 100*dkey + count*framelen, point.x, point.y, pdim[0], pdim[1], pdim[2], pdim[3], 
                            tdim[0], tdim[1], tdim[2], tdim[3], loc])
                count += 1
        return ret


# In[5]:


def convert(*args):
   # args should be in this order
    # name, fpdims, ftdims
    print('THREAD STARTED')
    vid = VideoData(args[0],args[1],args[2],args[3], args[4])
    print('STUFF INSERTED')
    vid.split()
    print('VID SPLIT')
    vid.extractFrames()
    print('FRAMES EXTRACTED')
    df = pd.DataFrame(vid.toList())
    print('LIST MADE')
    df.columns = ['Page', 'Time', 'X', 'Y', 'Picture Left', 'Picture Right', 'Picture Top', 'Picture Bottom', 'Text Left', 'Text Right', 'Text Top', 'Text Bottom', 'Gaze Location(0=out, 1=pic, 2=txt)']
    print('CSV MADE')
    #df.to_csv('~/res/current/'+str(args[0])+'.csv')
    return df.to_csv()
    #print('SAVED THE CSV')
    #return''

