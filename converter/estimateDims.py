import sys
from scipy import misc


def estimate(fpath):
    im = misc.imread(fpath)
    tdims = {'xmin': sys.maxsize, 'ymin': sys.maxsize,
             'xmax': -sys.maxsize, 'ymax': -sys.maxsize}
    pdims = {'xmin': sys.maxsize, 'ymin': sys.maxsize,
             'xmax': -sys.maxsize, 'ymax': -sys.maxsize}
    # range to detect text in
    for x in range(223, 653):
        for y in range(49, 138):
            if (im[y, x] != [255, 255, 255]).all():
                if x < tdims['xmin']:
                    tdims['xmin'] = x
                if x > tdims['xmax']:
                    tdims['xmax'] = x
                if y < tdims['ymin']:
                    tdims['ymin'] = y
                if y > tdims['ymax']:
                    tdims['ymax'] = y
    # range to detect picture in
    for x in range(169, 688):
        for y in range(197, 504):
            if (im[y, x] != [255, 255, 255]).all():
                if x < pdims['xmin']:
                    pdims['xmin'] = x
                if x > pdims['xmax']:
                    pdims['xmax'] = x
                if y < pdims['ymin']:
                    pdims['ymin'] = y
                if y > pdims['ymax']:
                    pdims['ymax'] = y
    return tdims, pdims
