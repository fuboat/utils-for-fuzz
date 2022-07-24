from bisect import bisect_left
import re
import shelve
from contextlib import closing
import pprint
from statistics import median
from turtle import color
from typing import List, Tuple
from matplotlib.axes import Axes, SubplotBase
import numpy as np 
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib
import numpy as np
import scipy.stats as st

X = Y1 = Y2 = Y = Y_MIN = Y_MAX = List

def point_convert_for_fill_between_get_avg(x1: List, y1: List, x2: List, y2: List, y1_weight: int, y2_weight: int) -> Tuple [X, Y]:
    
    (x3, y31, y32) = point_convert_for_fill_between_get_both(x1, y1, x2, y2)
    y3 = []

    assert len(y31) == len(y32)

    for i in range(len(y31)):
        y3.append((y31[i] * y1_weight + y32[i] * y2_weight) / (y1_weight + y2_weight))

    return (x3, y3)
    

def point_convert_for_fill_between_get_max(x1: List, y1: List, x2: List, y2: List) -> Tuple [X, Y]:

    (x3, y31, y32) = point_convert_for_fill_between_get_both(x1, y1, x2, y2)
    y3 = []

    assert len(y31) == len(y32)

    for i in range(len(y31)):
        y3.append(max(y31[i], y32[i]))
    
    return (x3, y3)


def point_convert_for_fill_between_get_min(x1: List, y1: List, x2: List, y2: List) -> Tuple [X, Y]:
    (x3, y31, y32) = point_convert_for_fill_between_get_both(x1, y1, x2, y2)
    y3 = []

    assert len(y31) == len(y32)

    for i in range(len(y31)):
        y3.append(min(y31[i], y32[i]))

    return (x3, y3)

def point_convert_for_fill_between_get_both(x1: List, y1: List, x2: List, y2: List) -> Tuple [X, Y1, Y2]:

    x3 = []
    y31 = []
    y32 = []

    i1 = 0
    i2 = 0

    while i1 < len(x1) and i2 < len(x2):

        if x1[i1] == x2[i2]:
            x3.append(x1[i1])
            y31.append(y1[i1])
            y32.append(y2[i2])
            i1 += 1
            i2 += 1

        elif x1[i1] < x2[i2]:

            if 0 <= i2 - 1:
                x3.append(x1[i1])
                y31.append(y1[i1])
                y32.append(y2[i2 - 1] + (y2[i2] - y2[i2 - 1]) / (x2[i2] - x2[i2 - 1]) * (x1[i1] - x2[i2 - 1]))
            
            i1 += 1
        
        elif x2[i2] < x1[i1]:
            
            if 0 <= i1 - 1:
                x3.append(x2[i2])
                y31.append(y1[i1 - 1] + (y1[i1] - y1[i1 - 1]) / (x1[i1] - x1[i1 - 1]) * (x2[i2] - x1[i1 - 1]))
                y32.append(y2[i2])
            
            i2 += 1

        else:
            assert False
    
    return (x3, y31, y32)

def point_convert_for_fill_between(x1: List, y_min: List, y_max: List, x2: List, y2: List) -> Tuple[X, Y_MIN, Y_MAX]:

    x_out = []
    y1_out = []
    y2_out = []

    for i1 in range(len(x1)):
        i2 = bisect_left(x2, x1[i1])

        if 1 <= i2 and i2 < len(x2):
            pass

def draw_line(x_data, y_data, line_label, ax: Axes):
    ax.plot(x_data, y_data, label=line_label)

class PointConvertForFillBetween:

    def __init__(self):

        self.x = []
        self.y_min = []
        self.y_max = []
        self.y_avg = []
        self.weight = 0
        self.ys = []

    def add_plot(self, x: List, y: List):
        
        if self.weight == 0:
            self.x = x
            self.y_min = self.y_max = self.y_avg = y
        else:
            (_, y_min) = point_convert_for_fill_between_get_min(self.x, self.y_min, x, y)
            (_, y_max) = point_convert_for_fill_between_get_max(self.x, self.y_max, x, y)
            (_, y_avg) = point_convert_for_fill_between_get_avg(self.x, self.y_avg, x, y, self.weight, 1)

            self.x = _
            self.y_min = y_min
            self.y_max = y_max
            self.y_avg = y_avg
        
        self.weight += 1


class PointConvertForFillBetweenV2:

    def __init__(self):
        self.xs = []
        self.ys = []
        self.x = []
        self.ys_format = []
        self.y_min = []
        self.y_max = []
        self.y_avg = []
        self.y_median = []
        self.y_95confidence_interval_min = []
        self.y_95confidence_interval_max = []

    def add_plot(self, x: List, y: List):
        self.xs.append(x)
        self.ys.append(y)
    
    def format_data(self):

        self.x = []
        self.ys_format = []
        self.y_min = []
        self.y_max = []
        self.y_avg = []
        self.y_median = []

        x_all = []

        for x in self.xs:
            x_all += x
        
        x_unique = sorted(set(x_all))

        x_range_l = max(x[0]  for x in self.xs)
        x_range_r = min(x[-1] for x in self.xs)

        for x_v in x_unique:
            if x_range_l <= x_v and x_v <= x_range_r:
                self.x.append(x_v)

        for x, y in zip(self.xs, self.ys):
            (_, y_new, _) = point_convert_for_fill_between_get_both(x, y, self.x, [0] * len(self.x))
            assert len(y_new) == len(self.x)
            self.ys_format.append(y_new)
        
        last_median = None

        for index in range(len(self.x)):
            data = [y[index] for y in self.ys_format]
            self.y_min.append(min(data))
            self.y_max.append(max(data))
            self.y_avg.append(sum(data) / len(data))
            self.y_median.append(median(data))

            if len(self.y_median) > 1:
                assert self.y_median[-1] >= self.y_median[-2]

            (min_v, max_v) = st.t.interval(alpha=0.95, df=len(data)-1, loc=np.mean(data), scale=st.sem(data))
            self.y_95confidence_interval_min.append(min_v)
            self.y_95confidence_interval_max.append(max_v)

if __name__ == '__main__':
    fig = plt.figure(figsize=(9, 7))
    ax: Axes = fig.add_subplot(1, 1, 1)

    x1 = [1, 2, 3, 4]
    y1 = [5, 8, 12, 14]

    x2 = [1.5, 2.5, 3.5, 4.5]
    y2 = [4, 7, 16, 20]

    x3 = [0.7, 1.7, 2.7, 3.7, 4.7]
    y3 = [3, 9, 10, 18, 28]

    # draw_line([1, 2, 3, 4], [5, 8, 12, 14], 'fuck', ax)
    # draw_line([1.5, 2.5, 3.5, 4.5], [4, 7, 9, 15], 'fuck', ax)

    p = PointConvertForFillBetweenV2()
    p.add_plot(x1, y1)
    p.add_plot(x2, y2)
    p.add_plot(x3, y3)
    p.format_data()

    # ax.plot(x1, y1)
    # ax.plot(x2, y2)
    ax.plot(p.x, p.y_avg)
    ax.fill_between(p.x, p.y_min, p.y_max, alpha=0.2)

    # ax.plot(x1, y1)
    # ax.fill_between([1, 2, 3, 4], [5, 8, 12, 14], [4, 7, 9, 15], color='#00000077')
    plt.savefig("show.png")
