#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from z3 import *
from operator import add
import itertools, my_utils, Z3_utils
import datetime
import sys

week_list = ["MON","TUE","WED","THU","FRI","SAT","SUN"]

if len(sys.argv)!=4:
    print("Usage: python3 makeyourday.py year month day.")
    exit(0)
year = int(sys.argv[1])
month = int(sys.argv[2])
day = int(sys.argv[3])
#weekday = datetime.date(year, month, day).weekday()  #return 0~6 for MON ~ SUN
weekday = datetime.date(year, month, day).isoweekday()  #reutrn 1~7 for MON ~ SUN

print("Output the \033[93m"+str(year)+"-"+str(month)+"-"+str(day)+","+week_list[weekday-1]+"\033[0m Solutions")


# The board
'''
+-----+-----+-----+-----+-----+-----+-----+-----+
| ^_^ | MON | TUE | WED | JAN | FEB | MAR | APR |
+-----+-----+-----+-----+-----+-----+-----+-----+
| THU | FRI | SAT | SUN | MAY | JUN | JUL | AUG |
+-----+-----+-----+-----+-----+-----+-----+-----+
|  1  |  2  |  3  |  4  | SEP | OCT | NOV | DEC |
+-----+-----+-----+-----+-----+-----+-----+-----+
|  5  |  6  |  7  |  8  |  9  |  10 |  11 |  12 |
+-----+-----+-----+-----+-----+-----+-----+-----+
|  13 |  14 |  15 |  16 |  17 |  18 |  19 |  20 |
+-----+-----+-----+-----+-----+-----+-----+-----+
|  21 |  22 |  23 |  24 |  25 |  26 |  27 |  28 |
+-----+-----+-----+-----+-----+-----+-----+-----+
|  29 |  30 |  31 |                           
+-----+-----+-----+
'''

board=[ \
    "********",
	"********",
	"********",
	"********",
	"********",
	"********",
    "***     "]

# the coordinates of "week, month ,day" on the board
week_coordinate = [(0,1),(0,2),(0,3),
                 (1,0),(1,1),(1,2),(1,3)]
month_coordinate = [(0,4),(0,5),(0,6),(0,7),
                    (1,4),(1,5),(1,6),(1,7),
                    (2,4),(2,5),(2,6),(2,7)]
day_coordinate = [(2,0),(2,1),(2,2),(2,3),
                (3,0),(3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7),
                (4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),
                (5,0),(5,1),(5,2),(5,3),(5,4),(5,5),(5,6),(5,7),
                (6,0),(6,1),(6,2)
                ]

# According to the coordinates of "week, month ,day" on the board, change "*" to " "
def generate_board(index,coordinate):
    wc = coordinate[index]
    wc_x_coord = wc[0]
    wc_y_coord = wc[1]
    board[wc_x_coord] = board[wc_x_coord][:wc_y_coord] +" "+board[wc_x_coord][wc_y_coord+1:]

generate_board(weekday-1,week_coordinate) # list start with 0, so weekday-1
generate_board(month-1,month_coordinate) # list start with 0, so month-1
generate_board(day-1,day_coordinate) # list start with 0, so day-1

# print the updated board with the target shape
for row in board:
    s=""
    for col in row:
        if col =='*':
            s = s+ "██"
        else:
            s=s+"  "
    print (s)

# 11 flat shapes
tiles=[
["***",    # P
 "** "],

["**",     # v
 "* "],

["****"],  # I

["****",   # L
 "   *"],

["***",    # l
 "  *"],

["***",    # V
 "  *",
 "  *"],

["***",    # T
 " * "],

["* *",    # U
 "***"],

["  * ",   # Y
 "****"],

["** ",    # Z
 " **"],

 ["**",    # O
  "**"]
]

board_height=len(board)
board_width=len(board[0])

TILES_TOTAL=len(tiles)

def lists_has_adjacent_cells(l1, l2):
    # enumerate all possible combinations of items from two lists:
    return any([my_utils.adjacent_coords(q[0][0], q[0][1], q[1][0], q[1][1]) for q in itertools.product(l1, l2)])

def can_be_placed(into, irow, icol, tile):
    rt=[]
    tile_height=len(tile)
    tile_width=len(tile[0])
    for prow in range(tile_height):
        for pcol in range(tile_width):
            if tile[prow][pcol]=='*':
                # tile cannot be placed if there is a hole on board:
                if into[irow+prow][icol+pcol]==' ':
                    return None
                if into[irow+prow][icol+pcol]=='*':
                    rt.append((irow+prow, icol+pcol))
    return rt

# enumerate all positions on board and try to put tile there:
def find_all_placements(_type, tile):
    tile_height=len(tile)
    tile_width=len(tile[0])
    rt=[]

    for row in range(board_height-tile_height+1):
        for col in range(board_width-tile_width+1):
            tmp=can_be_placed(board, row, col, tile)
            if tmp!=None:
                rt.append((_type, tmp))
# rt is a list of tuples, each has poly type and list of coordinates, like:
#(0, [(0, 1), (1, 1), (1, 2), (2, 1)]),
#(0, [(0, 2), (1, 2), (1, 3), (2, 2)]),
#...
#(1, [(0, 1), (0, 2), (1, 1), (1, 2), (2, 1)]),
#(1, [(0, 2), (0, 3), (1, 2), (1, 3), (2, 2)])

    return rt

def str_to_list_of_chars(lst):
    return [l for l in lst]

def find_all_placements_with_rotations(poly_type, tile):
    # we operate here with tiles encoded as list of lists of chars
    tile=[str_to_list_of_chars(tmp) for tmp in tile]
 
    # rotate tile in 4 ways.
    # also, mirror it horizontally
    # that gives us 8 versions of each tile
    # remove duplicates
    duplicates=[]
    rt=[]
    for a in range(4):

        t1=my_utils.rotate_rect_array(tile, a)
        if t1 not in duplicates:
            duplicates.append(t1)
            rt=rt+find_all_placements(poly_type, t1)

        t2=my_utils.reflect_horizontally(my_utils.rotate_rect_array(tile, a))
        if t2 not in duplicates:
            duplicates.append(t2)
            rt=rt+find_all_placements(poly_type, t2)

    return rt

# input: list of tiles, like:
# [(0, [(2, 1), (3, 0), (3, 1), (3, 2)]), 
# (1, [(0, 1), (0, 2), (0, 3), (1, 1), (1, 2)]),
# (2, [(1, 3), (2, 2), (2, 3)]), 
# (3, [(1, 0), (2, 0)])]
# each tuple has tile type + list of coordinates on board

# output: color for each tile, like: [2, 0, 1, 3]
def color_tiles(solution):
    # make a graph
    G=[]
    # enumerate all possible pair of tiles:
    for pair in itertools.combinations(solution, r=2):
        if lists_has_adjacent_cells(pair[0][1], pair[1][1]):
            # add constraint, if tiles adjacent to each other.
            # it's not a problem to add the same constraint multiple times.
            G.append((pair[0][0], pair[1][0]))

    # this is planar graph anyway, 4 colors enough:
    return Z3_utils.color_graph_using_Z3(G, total=TILES_TOTAL, limit=4)

def print_solution(solution):
    for row in range(board_height):
        s=""
        for col in range(board_width):
            if board[row][col]=='*':
                for a in range(TILES_TOTAL):
                    if (row,col) in solution[a][1]:
                        s=s+"0123456789abcdef"[a]
                        break
            else:
                # skip holes in board:
                s=s+" "
        print (s)

    print ("")

    # print colored solution:

    coloring=color_tiles(solution)

    for row in range(board_height):
        s=""
        for col in range(board_width):
            if board[row][col]=='*':
                for a in range(TILES_TOTAL):
                    if (row,col) in solution[a][1]:
                        s=s+my_utils.ANSI_set_normal_color(coloring[a])+"██"
                        break
            else:
                # skip holes in board:
                s=s+"  "
        print (s)

    print (my_utils.ANSI_reset())

init_rows=[]
for i in range(TILES_TOTAL):
    init_rows=init_rows+find_all_placements_with_rotations(i,tiles[i])

print ("len(init_rows)=", len(init_rows))

# init_rows is a list of tuples
# each tuple has poly type (num) + list of coordinates on board at which it can cover
# like:
#(2, [(1, 1), (2, 1), (2, 2)])
#(2, [(2, 1), (3, 1), (3, 2)])
#(3, [(0, 1), (1, 1)])
#(3, [(0, 3), (1, 3)])

s=Solver()

rows=[Bool('row_%d' % r) for r in range(len(init_rows))]

# make inverse tables:

inv_tbl_board={}
inv_tbl_poly={}

cur_row=0
for t in init_rows:
    poly_type=t[0]
    if poly_type not in inv_tbl_poly:
        inv_tbl_poly[poly_type]=[]
    inv_tbl_poly[poly_type].append(cur_row)
    coords=t[1]
    for coord in coords:
        if coord not in inv_tbl_board:
            inv_tbl_board[coord]=[]
        inv_tbl_board[coord].append(cur_row)
    cur_row=cur_row+1

# at this point, inv_tbl_poly is a dict, it has poly type as a key and list of rows as a value
# these are rows where specific poly type is stored

# inv_tbl_board is also a dict. key=tuple (coordinates). value=list of rows, which can cover this cell on board.

# only one row can be selected from inv_tbl_poly, meaning, each tile can be connected to only one row:
for t in inv_tbl_poly:
    tmp=[rows[q] for q in inv_tbl_poly[t]]

    # only one True must be present in tmp.
    # AtMost()/AtLeast() takes list of arguments + k.
    # we pass here a list + 1 as an arguments to functions:
    s.add(AtMost(*(tmp+[1])))
    s.add(AtLeast(*(tmp+[1])))

# only one row can be selected from inv_tbl_board, meaning, each cell on board can be connected to only one row:
for t in inv_tbl_board:
    tmp=[rows[q] for q in inv_tbl_board[t]]

    # only one True must be present in tmp:
    s.add(AtMost(*(tmp+[1])))
    s.add(AtLeast(*(tmp+[1])))

# enumerate all possible solutions:
results=[]
sol_n=1
while True:
    if s.check() == sat:
        m = s.model()

        # now after solving, we are getting a list of rows.

        solution=[]

        # which rows are True? copy them to solution[]
        for row in range(len(init_rows)):
            if is_true(m[rows[row]]):
                solution.append(init_rows[row])

        # at this point, solution[] may looks like

        #[(0, [(1, 2), (2, 2), (2, 3), (3, 2)]), 
        #(1, [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1)]), 
        #(2, [(0, 2), (0, 3), (1, 3)])
        #(3, [(0, 1), (1, 1)])]

        #These are four tiles with coordinates on board for each tile.

        print ("solution number", sol_n)
        sol_n=sol_n+1
        print_solution(solution)

        results.append(m)
        block = []
        for d in m:
            c=d()
            block.append(c != m[d])
        s.add(Or(block))
    else:
        print ("results total=", len(results))
        break