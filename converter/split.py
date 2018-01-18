
# coding: utf-8

# In[1]:


import cv2
import os
import numpy as np
import sys


# In[45]:


# This split the mp4 into a lot of small frames
def split(root, file, stop=None):
    clear(root)
    print('split', file)
    if not os.path.isdir(root + '/frames/'):
        os.mkdir(root + '/frames/')
    vc = cv2.VideoCapture(root + '/video/' + file)
    c = 0
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        sys.exit('Couldn\'t open video file')
    while rval:
        rval, frame = vc.read()
        # boole = cv2.imwrite('../frames2/' + str(c) + '.png', frame)
        boole = cv2.imwrite(root + '/frames/' + file + str(c) + '.png', frame)
        c += 1
        cv2.waitKey(1)
        if stop and c == stop:
            break
    vc.release


def forward_split(root, file):
    clear(root)
    print('forwardsplit', file)
    if not os.path.isdir(root + '/frames/'):
        os.mkdir(root + '/frames/')
    vc = cv2.VideoCapture(root + '/video/' + file)
    c = 0
    if vc.isOpened():
        maxFrames = vc.get(cv2.CAP_PROP_FRAME_COUNT)
        for x in range(48):
            if x * 50 < maxFrames:
                vc.set(cv2.CAP_PROP_POS_FRAMES, 50 * x)
                rval, frame = vc.read()
                cv2.imwrite(root + '/frames/' + str(50 * x) + '.png', frame)
    else:
        sys.exit('Couldn\'t open video file')
    vc.release()
    return ''


def backward_split(root, file):
    clear(root)
    print('backwardsplit', file)
    if not os.path.isdir(root + '/frames/'):
        os.mkdir(root + '/frames/')
    vc = cv2.VideoCapture(root + '/video/' + file)
    if vc.isOpened():
        maxFrames = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        for x in range(48):
            if maxFrames - x * 50 > 0:
                vc.set(cv2.CAP_PROP_POS_FRAMES, maxFrames - 50 * x)
                rval, frame = vc.read()
                cv2.imwrite(root + '/frames/' +
                            str(maxFrames - 50 * x) + '.png', frame)
    else:
        print("couldn't open vid file")
    vc.release()
    return ''


def split_1(root, file, init):
    clear(root)
    vc = cv2.VideoCapture(root + '/video/' + file)
    init = int(init)
    if vc.isOpened():
        vc.set(cv2.CAP_PROP_POS_FRAMES, init)
        rval, frame = vc.read()
        cv2.imwrite(root + '/frames/' +
                    str(0) + '.png', frame)
    else:
        print("couldn't open vid file")
    vc.release()
    return ''


def mid_split(root, file, init):
    clear(root)
    print('midsplit',file)
    vc = cv2.VideoCapture(root + '/video/' + file)
    init = int(init)
    maxFrames = vc.get(cv2.CAP_PROP_FRAME_COUNT)
    if vc.isOpened():
        if not init == 0:
            vc.set(cv2.CAP_PROP_POS_FRAMES, init - 50)
            init -= 60
        for x in range(24):
            if x * 5 < maxFrames:
                vc.set(cv2.CAP_PROP_POS_FRAMES, init + 5 * x)
                rval, frame = vc.read()
                cv2.imwrite(root + '/frames/' +
                            str(init + 5 * x) + '.png', frame)
        else:
            maxFrames = vc.get(cv2.CAP_PROP_FRAME_COUNT)
    vc.release()
    return ''


def clear(root):
    filelist = [f for f in os.listdir(root + '/frames/') if f.endswith('.png')]
    for f in filelist:
        if f.endswith('.png'):
            os.remove(os.path.join(root + '/frames/', f))
