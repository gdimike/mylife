#!/usr/bin/env python
"""
mylife.py

An implementation of John Conway's game of life.

See http://en.wikipedia.org/wiki/Conway%27s_Game_of_Life for more
information.

Options:
-r  start with a random cell arrangement.
-f  filename of start cell pattern, located in the ./lifeforms directory.
-x  initial x location of start cell pattern
-y  initial y location of start cell pattern

Michael Goldberg Sat Jul 18 20:23:43 CDT 2009
gdimike-at-yahoo-com

Copyright (C) 2009 Michael Lee Goldberg 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

__author__ = "Mike Goldberg"
__date__ = "Jul 18 20:23:43 CDT 2009"
__version__ = "$Id: mylife.py,v 1.55 2009/10/28 01:39:18 mikey Exp mikey $"

#Import Modules
import os, sys, pygame, random
from pygame.locals import * #IGNORE:W06
from optparse import OptionParser

def writeDefaultConfig():
    # open a file for output
    try:
        fout = open('.myliferc', "w")
    except IOError:
        print "Error! Cannot open file"
        print
        sys.exit(1)

    # write a default .myliferc file
    fout.write('# Automagically generated .myliferc configuration file.\n')
    fout.write('# valid XRES, YRES pairs 640x480, 1024x768\n')

    fout.write('XRES  1024\n')
    fout.write('YRES  768\n')
    fout.write('# valid BLOCK_SIZE values  4, 6, 8, 10, 12, 16, 18, 20 ... 36\n')
    fout.write('# "best values" if XMAX % BLOCKSIZE == 0 and YMAX % BLOCKSIZE == 0.\n')

    fout.write('BLOCK_SIZE  4\n')
    fout.write('# min DELTA_T = 50\n')
    fout.write('DELTA_T 250\n')

    fout.write('#FCOLOR = foreground color R G B, values from 0 - 255\n')
    fout.write('#BCOLOR = background color R G B, values from 0 - 255\n ')
    fout.write('FCOLOR 0   255   0\n')
    fout.write('BCOLOR 0     0   0\n')

    fout.close()

def getConfig():
    params = [''] * 6
    try:
        fin = open('.myliferc', "r")
        rcfound = True
    except IOError:
        rcfound = False
        print "Config file '.myliferc not found."
        print "Using these default values:"
        print "XRES  1024"
        print "YRES  768"
        print "BLOCK_SIZE  8"
        print "DELTA_T 250"
        print "FCOLOR 0   255 0"
        print "BCOLOR 0   0   0"
        params = [1024, 768, 8, 250, (0, 255, 0), (0, 0, 0)]
        
        print
        print 'Writing a default .myliferc config file.'
        writeDefaultConfig()

    
    if rcfound: 
        for line in fin:
            line = line.split()
            if line == [] or line[0] == '#':
                pass
            else:
                if line[0] == 'XRES':
                    params[0] = int(line[1])
                elif line[0] == 'YRES':
                    params[1] = int(line[1])
                elif line[0] == 'BLOCK_SIZE':
                    params[2] = int(line[1])
                elif line[0] == 'DELTA_T':
                    params[3] = int(line[1])
                elif line[0] == 'FCOLOR':
                    params[4] = (int(line[1]), int(line[2]), int(line[3]))
                elif line[0] == 'BCOLOR':
                    params[5] = (int(line[1]), int(line[2]), int(line[3]))
                else:
                    pass
        fin.close()
    return params

class Usage(Exception):
    def __init__(self, msg): #IGNORE:W0231
        self.msg = msg

def getData(filename, XMAX, YMAX):
    '''
    Input: data file for mylife
    Output: a list of lists "matrix" of the starting pattern
    '''
    # open a file for input
    try:
        fullname = os.path.join('lifeforms', filename)
        fin = open(fullname, "r")
    except IOError:
        print "file not found"
        print
        sys.exit(1)
        
    startx = XMAX / 2
    starty = YMAX / 2
    indata = []
    tempdata = []

    # determine file format (as far as possible) from extension
    file_format = 'unknown'
    if filename[-4:] == '.rle':
        file_format = 'rle'
        rle_string_list = []
    if filename[-6:] == '.cells':
        file_format = 'plaintext'
        string_list = []


    for line in fin:
        if line[0] == '#' or line[0] == "!" or line == '\n': 
            if line[1:10] == 'Life 1.05':
                file_format = 'l105'
            if file_format == 'l105' and line[1] == 'N':
                pass   # "normal" Life; Conway's life
            if file_format == 'l105' and line[1] == 'R':
                print
                print "Only Conway's Life (or #R 23/3) \
                is currently supported"
                print 
                sys.exit(1)
            if file_format == 'l105' and line[1] == 'P':
                temp3 = line.split()
                startx = int(temp3[1])
                starty = int(temp3[2])
                # correct location coordinates
                startx += XMAX / 2
                starty += YMAX / 2
            if line[1:10] == 'Life 1.06':
                file_format = 'l106'
                startx = 0
                starty = 0
        else:
            if file_format == 'unknown':
                print 'Unknown file format.'
                sys.exit(-1)
            elif file_format == 'plaintext':
                string_list.append(line.strip())
            elif file_format == 'l106':
                t = line.split()
                x = int(t[1]) + XMAX / 2
                y = int(t[0]) + YMAX /2
                tempdata.append((x, y))    
            elif file_format == 'rle':
                if line[0] == 'x':
                    txy = line.split()
                    sx = txy[2]
                    sy = txy[5]
                    xdim =(int(sx[:-1]))
                    ydim =(int(sy[:-1]))
                else:
                    rle_string_list.append(line.strip())
            else:
                tempdata.append(line.rstrip()) 

    if file_format == 'l105':
        # get size of figure
        rows = len(tempdata)
        cols = max(map(len,tempdata)) #IGNORE:W0141
        indata = makeCA_MATRIX(cols, rows)
        for r in range(rows):
            for c in range(len(tempdata[r])):
                if tempdata[r][c] == '*':
                    indata[r][c] = 1
                else:
                    indata[r][c] = 0
        print 'File read: ', filename
        print 'Life 1.05 format file.'
        print 'FIXME: Life 1.05 format only partially implemented.'

    if file_format == 'l106':
        indata = makeCA_MATRIX(XMAX, YMAX)
        startx = 0
        starty = 0
        for point in tempdata:
            indata[point[1]][point[0]] = 1
        print 'File read: ', filename
        print 'Life 1.06 format file.'

    if file_format == 'rle':
        # process rle_string list
        startx = XMAX / 2 - xdim / 2
        starty = YMAX / 2 - ydim / 2
        rletemp =  ''.join(rle_string_list)
        rle_list = rletemp.split('$')
        rle_list[-1] = rle_list[-1][:-1]
        # make a blank pattern
        indata = makeCA_MATRIX(xdim, ydim)
        trow = []
        digits = []
        n = 0
        y = 0
        for line in rle_list:
            for char in range(len(line)):
                if line[char] == 'b' or line[char] == 'o':
                    if digits != []:
                        n = int(''.join(digits))
                    if n == 0:
                        n = 1
                    if line[char] == 'o':
                        splat = 1
                    else:
                        splat = 0
                    trow = trow + [splat] * n
                    digits = []
                    n = 0
                else:
                    digits.append(line[char])
            for x in range(len(trow)):
                indata[y][x] = trow[x]
            trow = []
            y += 1
        print 'File read:', filename
        print 'RLE format file.'

    if file_format == 'plaintext':
        rowmax = len(string_list)
        colmax = 0
        for col in string_list:
            line_length = len(col)
            if line_length > colmax:
                colmax = line_length
        startx -= colmax / 2
        starty -= rowmax / 2
        
        fullscreen = False
        if colmax == XMAX and rowmax == YMAX:
            fullscreen = True
        
        print fullscreen
        indata = makeCA_MATRIX(XMAX, YMAX)
        row = 0
        for line in string_list:
            for col in range(len(line)):
                if line[col] == '0' or \
                   line[col] == 'O' or \
                   line[col] == 'o':
                    if fullscreen:
                        #print row, col
                        indata[row][col] = 1
                    if not fullscreen:
                        indata[row][col] = 1
            row += 1
        print 'File read:', filename
        print 'Plaintext format file.'

    fin.close()
    return indata, startx, starty

def loadStart(filename, x, y, XMAX, YMAX, BLOCK_SIZE):
    blocks = []
    ca_matrix = makeCA_MATRIX(XMAX, YMAX)
    data, x, y = getData(filename, XMAX, YMAX)
    ysize = len(data)
    xsize = len(data[0])
    for r in range(ysize):
        for c in range(xsize):
            if data[r][c] == 1:
                ca_matrix[r+y][c+x] = 1

    for x in range(XMAX):
        for y in range(YMAX):
            if ca_matrix[y][x] == 1:
                blocks.append((x * BLOCK_SIZE, y * BLOCK_SIZE))
                
    return blocks, ca_matrix

def randomStart(XMAX, YMAX, BLOCK_SIZE):
    blocks = []
    ca_matrix = makeCA_MATRIX(XMAX, YMAX)

    for x in range(XMAX):
        for y in range(YMAX):
            pct = random.random()
            if pct < 0.375:
                blocks.append((x * BLOCK_SIZE, y * BLOCK_SIZE))
                ca_matrix[y-1][x-1] = 1
            else:
                ca_matrix[y-1][x-1] = 0    
    return blocks, ca_matrix
    
def countNeighbors(row, col, ca_matrix):
    '''Determine the number of neighbors a cell has.'''
    total = 0
    
    if col - 1 < 0:
        badcol = True
    else:
        badcol = False
    
    if row - 1 < 0:
        badrow = True
    else:
        badrow = False    
        
    try:
        if badcol or badrow:
            pass
        elif ca_matrix[row-1][col-1] == 1:
            total += 1
    except IndexError: #IGNORE:W0704
        pass
    
    try:
        if badcol:
            pass
        elif ca_matrix[row][col-1] == 1:
            total += 1
    except IndexError: #IGNORE:W0704
        pass
    
    try:
        if badcol:
            pass
        elif ca_matrix[row+1][col-1] == 1:
            total += 1
    except IndexError: #IGNORE:W0704
        pass

    try:
        if badrow:
            pass
        elif ca_matrix[row-1][col] == 1:
            total += 1
    except IndexError: #IGNORE:W0704
        pass
    
    try:
        if ca_matrix[row+1][col] == 1:
            total += 1
    except IndexError: #IGNORE:W0704
        pass
    
    try:
        if badrow:
            pass
        elif ca_matrix[row-1][col+1] == 1:
            total += 1
    except IndexError: #IGNORE:W0704
        pass
    
    try:
        if ca_matrix[row][col+1] == 1:
            total += 1
    except IndexError: #IGNORE:W0704
        pass
    
    try:
        if ca_matrix[row+1][col+1] == 1:
            total += 1
    except IndexError: #IGNORE:W0704
        pass
    return ca_matrix[row][col], total

def cellNextgen(row, col, ca_matrix, ruleset):
    cell, neighbors = countNeighbors(row, col, ca_matrix)
    if cell == 0:
        if ruleset[0][neighbors] == 1:
            life = 1
        else:
            life = 0
    elif cell == 1:
        if ruleset[1][neighbors] == 1:
            life = 1    
        else:
            life = 0
    else:
        life = 0
    return life

def updateCA_MATRIX(ca_matrix, XMAX, YMAX, ruleset):
    tarray = makeCA_MATRIX(XMAX, YMAX)
    for row in range(YMAX):
        for col in range(XMAX):
            tarray[row][col] = cellNextgen(row, col, ca_matrix, ruleset) 
    return tarray

def updateDisplay(ca_matrix, XMAX, YMAX, BLOCK_SIZE):
    tblocks = []
    for row in range(YMAX):
        for col in range(XMAX):
            if ca_matrix[row][col] == 1:
                tblocks.append((col * BLOCK_SIZE, row * BLOCK_SIZE))
    return tblocks

def makeCA_MATRIX(XMAX, YMAX):
    tmatrix = []
    line = [0] * XMAX
    for row in range(YMAX): #IGNORE:W0612
        tmatrix.append(line[:]) #deep copy!
    return tmatrix

def seticon(iconname):
    """
    give an iconname, a bitmap sized 32x32 pixels, black (0,0,0) will 
    be alpha channel
    
    the windowicon will be set to the bitmap, but the black pixels will
    be full alpha channel
     
    can only be called once after pygame.init() and before somewindow =
    pygame.display.set_mode()
    """
    # from an anonymous commentator to pygame docs site.
    icon=pygame.Surface((32,32))
    icon.set_colorkey((0,0,0))#and call that color transparant
    rawicon=pygame.image.load(iconname)#must be 32x32, black is transparant
    for i in range(0,32):
        for j in range(0,32):
            icon.set_at((i,j), rawicon.get_at((i,j)))
    pygame.display.set_icon(icon)#set wind

def getOptions():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="Filename of start tile", metavar="FILE")
    parser.add_option("-x", type="int", dest="startx", 
                      help="Initial x location of input tile")
    parser.add_option("-y", type="int", dest="starty", 
                      help="Initial y location of input tile")
    parser.add_option("-r", "--random", action="store_true", 
                      dest = "random", default=False,
                      help="Create a random full screen start pattern")
    parser.add_option("-s", "--sstep", action="store_true", 
                      dest = "sstep", default=False,
                      help="Single step mode")

    parser.add_option("-R", "--ruleset", type="string", dest="ruleset", 
                      help="Cellular Automation rule set, e.g. B3/S23")
    parser.add_option("-d", "--directory", action = "store_true",
                      dest = "directory", 
                      default = False, help = "List available lifeforms")

    options, args = parser.parse_args()
    return options, args

def printLifeformsDir():
    print 'Lifeforms available:'
    #cmd = 'ls lifeforms/*.* | sed "s/lifeforms\///"'
    cmd = 'ls lifeforms -C'
    os.system(cmd)

def createRuleset(rset):
    states = [[0] * 9, [0] * 9]
    temp = rset.split('/')
    b_str = temp[0][1:]
    s_str = temp[1][1:]

    for digit in range(len(b_str)):
        states[0][int(b_str[digit])] = 1

    for digit in range(len(s_str)):
        states[1][int(s_str[digit])] = 1

    return states

def rulesetName(rset_string):
    ruleset_string = rset_string.upper()
    if ruleset_string == 'B3/S23':
        ruleset_name = "Conway's life"
    elif ruleset_string == 'B36/S23':
        ruleset_name = 'Highlife'
    elif ruleset_string == "B3678/S34678":
        ruleset_name = 'Day & Night'
    elif ruleset_string == "B3/S012345678":
        ruleset_name = 'Life without Death'
    elif ruleset_string == "B1357/S1displayInit(display)357":
        ruleset_name = 'Replicator'
    elif ruleset_string == "B1/S1":
        ruleset_name = 'Gnarl'
    elif ruleset_string == "B2/S":
        ruleset_name = 'Seeds'
    elif ruleset_string == "B3/S12345":
        ruleset_name = 'Maze'
    elif ruleset_string == "B234/S":
        ruleset_name = 'Serviettes'
    elif ruleset_string == "B345/S5":
        ruleset_name = 'Long life'
    else:
        ruleset_name = ''
    
    return ruleset_name

class CellularAutomation:
    def __init__(self, display=False):
        self.XRES = 1024
        self.YRES = 768
        self.BLOCK_SIZE = 8
        self.DELTA_T = 250
        self.FCOLOR = (0, 255, 0)
        self.BCOLOR = (0, 0, 0)
        self.options = None
        self.args = None
        self.getConfig()   
        self.XMAX = self.XRES / self.BLOCK_SIZE
        self.YMAX = self.YRES / self.BLOCK_SIZE
        self.ruleset_string = 'B3/S23'
        self.states = [[0] * 9, [0] * 9]        # birth,survive
        self.getOptions()
        self.createRuleset()
        # attributes for display
        self.display = display
        self.screen = None
        self.background = None
        self.white_block = None
        self.displayInit(display)
        
    def getConfig(self):
#        params = [''] * 6
        try:
            fin = open('.myliferc', "r")
            rcfound = True
        except IOError:
            rcfound = False
            print "Config file '.myliferc not found."
            print "Using these default values:"
            print "XRES  1024"
            print "YRES  768"            #params = [1024, 768, 8, 250, (0, 255, 0), (0, 0, 0)]
#            self.XRES = 1024
#            self.YRES = 768
#            self.BLOCK_SIZE = 8
#            self.DELTA_T = 250
#            self.FCOLOR = (0, 255, 0)
#            self.BCOLOR = (0, 0, 0)
            print "BLOCK_SIZE  8"
            print "DELTA_T 250"
            print "FCOLOR 0   255 0"
            print "BCOLOR 0   0   0"
            print
            print 'Writing a default .myliferc config file.'
            self.writeDefaultConfig()
       
        if rcfound: 
            for line in fin:
                line = line.split()
                if line == [] or line[0] == '#':
                    pass
                else:
                    if line[0] == 'XRES':
                        self.XRES = int(line[1])
                    elif line[0] == 'YRES':
                        self.YRES = int(line[1])
                    elif line[0] == 'BLOCK_SIZE':
                        self.BLOCK_SIZE = int(line[1])
                    elif line[0] == 'DELTA_T':
                        self.DELTA_T = int(line[1])
                    elif line[0] == 'FCOLOR':
                        self.FCOLOR = (int(line[1]), int(line[2]), int(line[3]))
                    elif line[0] == 'BCOLOR':
                        self.BCOLOR = (int(line[1]), int(line[2]), int(line[3]))
                    else:
                        pass
            fin.close()
  
    def writeDefaultConfig(self):
        # open a file for output
        try:
            fout = open('.myliferc', "w")
        except IOError:
            print "Error! Cannot open file"
            print
            sys.exit(1)
    
        # write a default .myliferc file
        fout.write('# Automagically generated .myliferc configuration file.\n')
        fout.write('# valid XRES, YRES pairs 640x480, 1024x768\n')
        fout.write('XRES  1024\n')
        fout.write('YRES  768\n')
        fout.write('# valid BLOCK_SIZE values  4, 6, 8, 10, 12, 16, 18, 20 ... 36\n')
        fout.write('# "best values" if XMAX % BLOCKSIZE == 0 and YMAX % BLOCKSIZE == 0.\n')
        fout.write('BLOCK_SIZE  4\n')
        fout.write('# min DELTA_T = 50\n')
        fout.write('DELTA_T 250\n')
        fout.write('#FCOLOR = foreground color R G B, values from 0 - 255\n')
        fout.write('#BCOLOR = background color R G B, values from 0 - 255\n ')
        fout.write('FCOLOR 0   255   0\n')
        fout.write('BCOLOR 0     0   0\n')
        fout.close()         
            
    def printParams(self):
        print self.XRES, self.YRES, self.BLOCK_SIZE, self.DELTA_T, self.FCOLOR, self.BCOLOR
    
    # FIXME -- can't use Optparse here        
    def getOptions(self):
        parser = OptionParser()
        parser.add_option("-f", "--file", dest="filename",
                          help="Filename of start tile", metavar="FILE")
        parser.add_option("-x", type="int", dest="startx", 
                          help="Initial x location of input tile")
        parser.add_option("-y", type="int", dest="starty", 
                          help="Initial y location of input tile")
        parser.add_option("-r", "--random", action="store_true", 
                          dest = "random", default=False,
                          help="Create a random full screen start pattern")
        parser.add_option("-s", "--sstep", action="store_true", 
                          dest = "sstep", default=False,
                          help="Single step mode")
    
        parser.add_option("-R", "--ruleset", type="string", dest="ruleset", 
                          help="Cellular Automation rule set, e.g. B3/S23")
        parser.add_option("-d", "--directory", action = "store_true",
                          dest = "directory", 
                          default = False, help = "List available lifeforms")
    
        self.options, self.args = parser.parse_args()
        #return options, args            
        if self.options.directory:
            printLifeformsDir()
            sys.exit(0)
        
        if self.options.ruleset == None:
            self.ruleset_string = 'B3/S23' # Conway's Life
        else:
            self.ruleset_string = self.options.ruleset
            self.ruleset_string = self.ruleset_string.upper()
            self.ruleset = self.createRuleset(self.ruleset_string)
 
    def createRuleset(self):
        #states = [[0] * 9, [0] * 9]
        temp = self.ruleset_string.split('/')
        b_str = temp[0][1:]
        s_str = temp[1][1:]
    
        for digit in range(len(b_str)):
            self.states[0][int(b_str[digit])] = 1
    
        for digit in range(len(s_str)):
            self.states[1][int(s_str[digit])] = 1
 
    def printLifeformsDir(self):
        print 'Lifeforms available:'
        cmd = 'ls lifeforms/*.* | sed "s/lifeforms\///"'
        os.system(cmd) 
        
    def printRuleset(self):
        print self.ruleset_string
        print self.states
        
    def printDisplay(self):
        if self.display:
            print 'display is True'
        else:
            print 'display is False'
            
    def displayInit(self,display):
        if display: 
            pygame.display.init()
            fullname = os.path.join('data', 'glider32x32.bmp')
            seticon(fullname)
            os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
            self.screen = pygame.display.set_mode((self.XRES, self.YRES))
            pygame.display.set_caption('My So-Called Life')
            pygame.mouse.set_visible(1)
            
            pygame.time.set_timer(USEREVENT, self.DELTA_T) # change state
        
            #Create The Backgound
            self.background = pygame.Surface(self.screen.get_size())
            self.background = self.background.convert()
            self.background.fill(self.BCOLOR)
            
            #Display The Background
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
            
            #Prepare Game Objects
            self.white_block = pygame.Surface((self.BLOCK_SIZE - 2, self.BLOCK_SIZE - 2))
            self.white_block.fill(self.FCOLOR)
             
def main():
    
    
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    testlife = CellularAutomation()
    testlife.printParams()
    testlife.printLifeformsDir()
    testlife.printRuleset()
    testlife.printDisplay()
    
    params = getConfig()
    XRES = params[0]
    YRES = params[1]
    BLOCK_SIZE  = params[2]
    DELTA_T = params[3]
    FCOLOR = params[4]
    BCOLOR = params[5]
    XMAX = XRES / BLOCK_SIZE
    YMAX = YRES / BLOCK_SIZE

    options, args = getOptions() #IGNORE:W0612
    if options.directory:
        printLifeformsDir()
        sys.exit(0)
    
    
    if options.ruleset == None:
        ruleset_string = 'B3/S23' # Conway's Life
    else:
        ruleset_string = options.ruleset
        ruleset_string = ruleset_string.upper()
    ruleset = createRuleset(ruleset_string)

    pygame.display.init()
    fullname = os.path.join('data', 'glider32x32.bmp')
    seticon(fullname)
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    screen = pygame.display.set_mode((XRES, YRES))
    pygame.display.set_caption('My So-Called Life')
    pygame.mouse.set_visible(1)
    
    pygame.time.set_timer(USEREVENT, DELTA_T) # change state

    #Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(BCOLOR)
    
    #Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()
    
    #Prepare Game Objects
    white_block = pygame.Surface((BLOCK_SIZE - 2, BLOCK_SIZE - 2))
    white_block.fill(FCOLOR)

    if options.random or \
    (not options.random and options.filename == None) or \
    options.filename == 'random.lif':
        blocks, ca_matrix = randomStart(XMAX, YMAX, BLOCK_SIZE)
    else:
        try:
            filename = options.filename
            startx = options.startx
            starty = options.starty
            blocks, ca_matrix = loadStart(filename, startx, starty, XMAX, YMAX, BLOCK_SIZE)
            #print 
        except Usage, err:
            print >>sys.stderr, err.msg
            print >>sys.stderr, "for help use --help"
            return 2

    for block in blocks:
        screen.blit(white_block,block)
    pygame.display.flip()    

    print 'Ruleset: ', ruleset_string, rulesetName(ruleset_string)

    generation = 0
    while 1:
        if options.sstep:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.display.quit()
                    return
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    ca_matrix = updateCA_MATRIX(ca_matrix, XMAX, YMAX, ruleset)
                    blocks = updateDisplay(ca_matrix, XMAX, YMAX, BLOCK_SIZE)    
                    screen.blit(background, (0, 0))
                    for block in blocks:
                        screen.blit(white_block,block)
                    pygame.display.flip()
                    generation += 1
                    print 'Generation: ', generation
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.display.quit()
                    return
                elif event.type == KEYDOWN and event.key == K_f:
                    pygame.display.toggle_fullscreen()
                elif event.type == KEYDOWN and event.key == K_d:
                    printLifeformsDir()
                elif event.type == KEYDOWN and event.key == K_s:
                    options.sstep = False
                elif event.type == KEYDOWN and event.key == K_w:
                    # open a file for output
                    try:
                        fullname = os.path.join('lifeforms', 'snapshot.cells')
                        fout = open(fullname, "w")
                    except IOError:
                        print "Error! Cannot open file"
                        print
                        sys.exit(1)
                    
                    # get program version number
                    id_list = __version__.split()
                    version_num = id_list[2]
                    fout.write('! Output from mylife.py version' + \
                    version_num + '\n')
                    fout.write('! XMAX: ' + str(XMAX) + '\n')
                    fout.write('! YMAX: ' + str(YMAX) + '\n')
                    line_list = []
                    for row in range(YMAX):
                        for col in range(XMAX):
                            if ca_matrix[row][col] == 1:
                                line_list.append('0')
                            else:
                                line_list.append('.')
                        line_list.append('\n')
                        line = "".join(line_list)
                        fout.write(line)
                        line_list = []
                            
                    fout.close()
                    print 'Screen written to file "snapshot.cells"'
        else:
            #Handle Input Events
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.display.quit()
                    print generation, 'generations run.'
                    return
                elif event.type == USEREVENT:
                    ca_matrix = updateCA_MATRIX(ca_matrix, XMAX, YMAX, ruleset)
                    blocks = updateDisplay(ca_matrix, XMAX, YMAX, BLOCK_SIZE)    
                    for block in blocks:
                        screen.blit(white_block,block)
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.display.quit()
                    print generation, 'generations run.'
                    return
                elif event.type == KEYDOWN and event.key == K_d:
                    printLifeformsDir()
                elif event.type == KEYDOWN and event.key == K_s:
                    options.sstep = True

            #Draw Everything
            generation += 1
            screen.blit(background, (0, 0))
            for block in blocks:
                screen.blit(white_block,block)
            pygame.display.flip()

if __name__ == '__main__': 
    main()
