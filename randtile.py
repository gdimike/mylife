#!/usr/bin/env python

"""
randtile.py

generate a random X by Y size tile for mylife.

"""

__author__= "Mike Goldberg"
__date__ = "Thu Aug  6 11:15:54 CDT 2009"
__version__ = "$Id: randtile.py,v 1.2 2009/08/10 16:09:08 mikey Exp mikey $"

import random, os, sys
from optparse import OptionParser

def makeCA_MATRIX(XMAX, YMAX):
    temp_matrix = []
    line = ['.'] * YMAX
    for i in range(XMAX):
        temp_matrix.append(line[:]) #deep copy!
    return temp_matrix

def getOptions():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="Filename of start tile. Default: random.cells",
                      default='random.cells',metavar="FILE")
    parser.add_option("-x", type="int", dest="xdim", default=20, 
                      help="X dimension (width) of tile.")
    parser.add_option("-y", type="int", dest="ydim", default=20,
                      help="Y dimension (height) of tile.")
    parser.add_option("-r", "--random", type=float, 
                      dest = "rand_pct", default=0.35,
                      help="Percentage chance a square is live.")
    options, args = parser.parse_args()
    return options, args

def printCA_MATRIX(ca_matrix):
    for row in ca_matrix:
        #print row
        line = "".join(row)
        print line

def writeCA_MATRIX(ca_matrix):
    try:
        fullname = os.path.join('lifeforms', options.filename)
        fout = open(fullname, "w")
    except IOError:
        print "Error! Cannot open file"
        print
        sys.exit(1)
                
    fout.write('! Created by randtile.py\n')
    fout.write('! rows = ' +  str(options.xdim)+'\n')
    fout.write('! columns = ' +  str(options.ydim)+'\n')
    fout.write('! probability of life = '  + str(options.rand_pct)+'\n')
    for row in ca_matrix:
        line = "".join(row)
        fout.write(line + '\n')
    fout.close()

def main():
    global options
    options, args = getOptions()
    #print '! rows = ', options.ydim
    #print '! columns = ', options.xdim
    #print '! probablility of life = ', options.rand_pct
    
    # Since we are printing out the file one row (y) at a time
    # to create the plaintext (.sells) file, each row is the y
    # dimension and each column is the xdimension
    # so we use ca_matrix[y][x]... 
    ca_matrix = makeCA_MATRIX(options.ydim, options.xdim)
    for row in range(options.ydim):
        for col in range(options.xdim):
            n = random.random()
            if n < options.rand_pct:
                ca_matrix[row][col] = '0'
    
    writeCA_MATRIX(ca_matrix)

if __name__ == '__main__': 
    main() 
