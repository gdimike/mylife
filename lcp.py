#!/usr/bin/python
"""
lcp.py

Life control panel
GUI program to control mylife.py, my take on Conway's Game of Life.
Just run the program and push the buttons.

See http://en.wikipedia.org/wiki/Conway%27s_Game_of_Life for more
information about Conway's Life.

Michael Goldberg Thu Jul 23 18:00:29 CDT 2009
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

__author__= "Mike Goldberg"
__date__ = "Thu Jul 23 18:00:29 CDT 2009"
__version__ = "$Id: lcp.py,v 1.17 2009/08/13 01:30:49 mikey Exp mikey $"


import os
from Tkinter import * #IGNORE:W0614
import tkFileDialog
#import tkMessageBox

class LifeControl:
    def __init__(self, master):
        self.stepval = IntVar()
        self.rules = IntVar()
        self.ruleset = StringVar()
        self.rulesets = ["B3/S23 Conway's Life", "B36/S23 Highlife", "B3678/S34678 Day & Night", \
        "B3/S012345678 Life Without Death", "B1357/S1357 Replicator", \
        "B1/S1 Gnarl", "B2/S Seeds", "B3/S12345 Maze", "B234/S Serviettes", "B345/S5 Long Life"] 

        self.rulesetdict = {}
        for i in range(len(self.rulesets)):
            temp = self.rulesets[i].split()
            self.rulesetdict[str(i)] = temp[0]


        self.ruleset.set('B3/S23')

        menubar = Menu(root)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=1)
        filemenu.add_command(label="Load", command=self.choose_file)
        filemenu.add_command(label="Run", command=self.runLife)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        configmenu = Menu(menubar, tearoff=0)
        configmenu.add_command(label="Config", command=self.runEditor)
        configmenu.add_command(label="Rulesets", command=self.setRuleset)
        menubar.add_cascade(label="Config", menu=configmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.showAbout)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        root.config(menu=menubar, relief='flat')

        self.frame1 = Frame(master, bd=4, relief='sunken')
        self.frame1.pack()

        self.label2 = Label(self.frame1, text="Start pattern",\
        bd=5, fg='black', relief='flat')
        self.label2.grid(row=0, column=0, sticky='e')

        self.lifeform = StringVar()
        self.lifeform.set('random')
        self.label3 = Label(self.frame1, textvariable=self.lifeform, \
        bg='black', fg='green', bd=5, relief='ridge', padx=3, font='courier')
        self.label3.grid(row=0, column=1, sticky='w')

        self.label4 = Label(self.frame1, text="    Ruleset ",\
        bd=5, fg='black', relief='flat')
        self.label4.grid(row=1,column=0, sticky='e')

        self.label5 = Label(self.frame1, textvariable=self.ruleset, \
        bg='black', fg='green', bd=5, relief='ridge', padx=3,font='courier')
        self.label5.grid(row=1, column=1,sticky='w')


        self.label6 = Label(self.frame1, text='Ruleset:')
        self.label6.grid(row=2, column=0)

        self.r3 = Radiobutton(self.frame1, \
        text="B3/S23 Conway's life",width=20,\
        variable=self.rules, value=0) 
        self.r3.grid(row=3, column=0, sticky='e')
         
        self.r4 = Radiobutton(self.frame1, \
        text="Input ruleset:           ",width=20,\
        variable=self.rules, value=1) 
        self.r4.grid(row=4, column=0, sticky='e')

        self.r3.select()

        self.entry1 = Entry(self.frame1)
        self.entry1.grid(row=5, column=0)

        self.btn5 = Button(self.frame1, text="Set rules", width=10,
        command=self.retrieveRuleset, bd=3, pady=3)
        self.btn5.grid(row=6, column=0)


        self.label7 = Label(self.frame1, text='Run mode:')
        self.label7.grid(row=2, column=1)


        self.r1 = Radiobutton(self.frame1, text='Single step',width=11,\
        variable=self.stepval, value=1) 
        self.r1.grid(row=3, column=1, sticky='w')
        self.r2 = Radiobutton(self.frame1, text='Continuous',width=11,\
        variable=self.stepval, value=0) 
        self.r2.grid(row=4, column=1, sticky='w')
        self.r2.select()

    def retrieveRuleset(self):
        if self.rules.get() == 1:
            temp_ruleset = self.entry1.get()
            self.ruleset.set(temp_ruleset.upper())
        else:
            self.ruleset.set('B3/S23')

    def runEditor(self):
        cmd = 'gedit .myliferc &' 
        os.system(cmd)

    def choose_file(self):
        file = tkFileDialog.askopenfile(parent=root,
        initialdir="./lifeforms", mode='rb',title='Choose file to load')
        temp = file.name
        temp1 = temp.split('/')
        filename = temp1[-1]
        self.lifeform.set(filename) #IGNORE:W0622

    def process(self):
        self.runLife(self.lifeform)
        #pass

    def runLife(self):
        if self.lifeform.get() == 'random':
            if self.stepval.get() == 1:
                cmd = 'python ./mylife.py -s -r -R '+\
                self.ruleset.get() + '&'
            else:
                cmd = 'python ./mylife.py -r -R' + self.ruleset.get() + '&'
        else:
            if self.stepval.get() == 1:
                cmd = 'python ./mylife.py -s -f ' + \
                self.lifeform.get() + \
                ' -R ' + self.ruleset.get() + ' &'
            else:
                cmd = 'python ./mylife.py -f ' + \
                self.lifeform.get() + \
                ' -R ' + self.ruleset.get() + ' &'
        os.system(cmd)

    def showAbout(self):
        ver_info = __version__.split()
        pgm = ver_info[1][:-2]
        
        # popup code
        about = Tk()
        ##  make a  window that is not re-sizable & disable the maximize button
        about.resizable(width=FALSE, height=FALSE)
        # changing the default icon in a Tkinter window
        about.wm_iconbitmap("@./data/glider.xbm")
        # give the window a title
        about.title("About") 
        
        aframe = Frame(about)
        aframe.pack()

        infotext = pgm + '\n' + \
        'Version ' + ver_info[2] + '\n' \
        'GUI program to launch mylife.py.\n' + \
        "myife.py is yet another Conway's Game of Life program.\n\n" + \
        'lcp.py Copyright (C) 2009 Michael Lee Goldberg\n'

        info = Label(aframe, text=infotext, justify=CENTER)
        info.pack()

        gnutext = "This program is free software: you can redistribute it and/or modify\n" + \
        "it under the terms of the GNU General Public License as published by\n" + \
        "the Free Software Foundation, either version 3 of the License, or\n" + \
        "(at your option) any later version.\n\n" + \
        "This program is distributed in the hope that it will be useful,\n" + \
        "but WITHOUT ANY WARRANTY; without even the implied warranty of\n" + \
        "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n" + \
        "GNU General Public License for more details.\n\n" + \
        "You should have received a copy of the GNU General Public License\n" + \
        "along with this program.  If not, see <http://www.gnu.org/licenses/>.\n"
        
        gpl = Label(aframe, text=gnutext, anchor=W, justify=LEFT)
        gpl.pack()

        ok = Button(aframe, text='OK', width=6, command=about.destroy, bd=3, pady=3)  
        ok.pack()

    def setRuleset(self):
        # popup code
        rsets = Tk()
        ##  make a  window that is not resizable & disable the maximize button
        rsets.resizable(width=FALSE, height=FALSE)
        rsets.geometry('320x240+5+150')
        # changing the default icon in a Tkinter window
        rsets.wm_iconbitmap("@./data/glider.xbm")
        # give the window a title
        rsets.title("Interesting Rulesets") 

        self.listbox = Listbox(rsets)
        self.listbox.pack(fill='both', expand=1)

        for rule in self.rulesets:
            self.listbox.insert(END, rule)

        select = Button(rsets, text='Select', command=self.setRule, width=8, bd=3, pady=3)  
        select.pack()

        select = Button(rsets, text='Close', command=rsets.destroy, width=8, bd=3, pady=3)  
        select.pack()

    def setRule(self):
        temp_sel = self.listbox.curselection()
        if temp_sel == ():
            self.ruleset.set(self.rulesetdict['0'])
        else:
            sel = temp_sel[0]
            self.ruleset.set(self.rulesetdict[sel])
        
def handler():
    root.quit()

root = Tk()
root.geometry('320x200+5+430')
##  make a  window that is not re-sizable & disable the maximize button
#root.resizable(width=FALSE, height=FALSE)

# changing the default icon in a Tkinter window
root.wm_iconbitmap("@./data/glider.xbm")
#root.wm_iconbitmap("@/usr/include/X11/bitmaps/escherknot")

# give the window a title
root.title("Mylife.py Start Program")

# keep a window always on top
root.wm_attributes('-topmost', 1)

root.protocol("WM_DELETE_WINDOW", handler)
# or toplevel.protocol(...

app = LifeControl(root)
root.mainloop()

