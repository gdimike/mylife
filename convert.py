#!/usr/bin/env python

"""
convert.py

Convert a Life 1.06 file to a plantext (.cells) for mylife.

"""

__author__= "Mike Goldberg"
__date__ = " Thu Aug  6 13:12:14 CDT 2009"
__version__ = "$Id: convert.py,v 1.2 2009/08/10 16:25:32 mikey Exp mikey $"

import os, sys
from optparse import OptionParser

def makeCA_MATRIX(XMAX, YMAX):
    temp_matrix = []
    line = ['.'] * YMAX
    for i in range(XMAX):
        temp_matrix.append(line[:]) #deep copy!
    return temp_matrix

def getOptions():
    parser = OptionParser()
    parser.add_option("-i", "--input-file", dest="input_filename",
                      default='snapshot.lif',
                      help="Name of Life 1.06 (.lif) format input file. \
                      Default: snapshot.lif",
                      metavar="FILE")
    parser.add_option("-o", "--output-file", dest="output_filename",
                      default='snapshot.cells',
                      help="Name of plaintext format (.cells) output file. \
                      Default: snapshot.cells",
                      metavar="FILE")
    options, args = parser.parse_args()
    return options, args

def getData(filename):
    # open file for input
    try:
        fullname = os.path.join('lifeforms', filename)
        fin = open(fullname, "r")
    except IOError:
        print "file not found"
        print
        sys.exit(1)
 
    datapoints = []
    for line in fin:
        if line[0] == '#' or line == []:
            pass
        else:
            point = line.split()
            datapoints.append((int(point[0]), int(point[1])))

    rowmax = -10000
    rowmin = 10000
    colmin = 10000
    colmax = -10000

    for point in datapoints:
        if point[0] > rowmax: rowmax = point[0]
        if point[0] < rowmin: rowmin = point[0]
        if point[1] > colmax: colmax = point[1]
        if point[1] < colmin: colmin = point[1]

    width = rowmax - rowmin
    height = colmax - colmin

    plotpoints = []
    for point in datapoints:
        plotpoints.append((point[0] - rowmin, point[1] - colmin))
    
    plaintext_matrix = []
    temp_row = ['.'] * (width+1)
    for row in range(height+1):
        plaintext_matrix.append(temp_row[:])    
    
    for point in plotpoints:
        plaintext_matrix[point[1]][point[0]] = '0'
    return plaintext_matrix

def printCA_MATRIX(ca_matrix):
    for row in ca_matrix:
        line = "".join(row)
        print line

def writeCA_MATRIX(ca_matrix):
    try:
        fullname = os.path.join('lifeforms', options.output_filename)
        fout = open(fullname, "w")
    except IOError:
        print "Error! Cannot open file"
        print
        sys.exit(1)
                
    fout.write('! Created by convert.py\n')
    for row in ca_matrix:
        line = "".join(row)
        fout.write(line + '\n')
    fout.close()

def main():
    global options
    options, args = getOptions()
    matrix = getData(options.input_filename)
    writeCA_MATRIX(matrix)

if __name__ == '__main__': 
    main() 
