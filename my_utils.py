#!/usr/bin/env python3

# Python utils

# dennis(a)yurichev.com, 2017-2020

from typing import List
from typing import Any

def read_lines_from_file (fname):
    f=open(fname)
    new_ar=[item.rstrip() for item in f.readlines()]
    f.close()
    return new_ar

# reverse list:
def rvr(i:List[Any]) -> List[Any]:
    return i[::-1]

def reflect_vertically(a:List[List[Any]]) -> List[List[Any]]:
    return [rvr(row) for row in a]

def reflect_horizontally(a:List[List[Any]]) -> List[List[Any]]:
    return rvr(a)

# N.B. must work on arrays of arrays of objects, not on arrays of strings!
def rotate_rect_array_90_CCW(a_in:List[List[Any]]) -> List[List[Any]]:
    a=reflect_vertically(a_in)
    rt=[]
    # reflect diagonally:
    for row in range(len(a[0])):
        #rt.append("".join([a[col][row] for col in range(len(a))]))
        rt.append([a[col][row] for col in range(len(a))])

    return rt

# angle: 0 - leave as is; 1 - 90 CCW; 2 - 180 CCW; 3 - 270 CCW
# FIXME: slow
def rotate_rect_array(a:List[List[Any]], angle:int) -> List[List[Any]]:
    if angle==0:
        return a
    assert (angle>=1)
    assert (angle<=3)

    for i in range(angle):
        a=rotate_rect_array_90_CCW(a)
    return a

def adjacent_coords(X1:int, Y1:int, X2:int, Y2:int) -> bool:
    # return True if pair of coordinates laying adjacently: vertically/horizontally/diagonally:
    return any([X1==X2   and Y1==Y2+1,
    		X1==X2   and Y1==Y2-1,
    		X1==X2+1 and Y1==Y2,
    		X1==X2-1 and Y1==Y2,
    		X1==X2-1 and Y1==Y2-1,
    		X1==X2-1 and Y1==Y2+1,
    		X1==X2+1 and Y1==Y2-1,
    		X1==X2+1 and Y1==Y2+1])

def ANSI_set_normal_color(color):
    return '\033[%dm' % (color+31)

def ANSI_reset():
    return '\033[0m'

def partition(lst:List[Any], n:int) -> List[Any]:
    division = len(lst) / float(n)
    return [ lst[int(round(division * i)): int(round(division * (i + 1)))] for i in range(n) ]

def is_in_range_incl (v, low, high):
    if v>=low and v<=high:
        return True
    return False

def find_1st_elem_GE (array, v):
    for a in array:
        if a>=v:
            return a
    return None # not found

def find_1st_elem_LE (array, v):
    #print (array)
    for a in array[::-1]:
        if a<=v:
            return a
    return None # not found

def list_of_strings_to_list_of_ints (l):
    return list(map(lambda x: int(x), l))

# I use this to convert fucking JSON keys from strings to ints
def string_keys_to_integers(d):
    rt={}
    for k in d:
        if type(d[k]) == dict:
            rt[int(k)]=string_keys_to_integers(d[k]) # recursively
        else:
            rt[int(k)]=d[k]
    return rt

def element_in_array_is_in_range (array, low, high):
    for a in array:
        if is_in_range_incl(a, low, high):
            return True
    return False
