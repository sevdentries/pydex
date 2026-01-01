import os 
import sys
import atexit
import shutil
import subprocess
import platform
import time 
import webbrowser 
from tkinter import *
from tkinter import ttk
import tkinter as tk
import getpass 
reader = "" #A global tracker to store the current directory being read.
toggle = 1 #A simple toggle flag for showing/hiding the option panel.
filecompile = "" 
compsel = () #A global tracker to store the current selected file index under filelist. This differs from optsel which locally tracks indexes under optionlist.
dirlist = []
filelistflag = 0 #A flag which is raised when a person decides to open options for the entire directory instead of a specific file

def optionshow(event): #command for showing the optionlist.
    global toggle
    toggle = 1
    optionlist.pack()

def optiontoggle(event): #togglescript to show/hide the option panel.
    global toggle
    if toggle == 1:
        optionlist.pack_forget()
        toggle = 0
    elif toggle == 0:
        optionlist.pack()
        toggle = 1

def optionhide(event): #command for hiding the optionlist.
    global toggle
    optionlist.pack_forget()
    toggle = 0
    filelist.selection_clear(0,tk.END)

def doubleselect(event): #redirects double click events to open files or read directories
    print("doubleselect")
    global reader
    compsel = filelist.curselection()
    try:
        select = compsel[0]
        select = (filelist.get(compsel[0]))
    except IndexError:
        print("No file selected!")

    if select.endswith("/"):
        read(reader+select)
    else:
        procopen(reader+select)
        

def actionselect(event): #a redirector of actions selected by users to functions
    optsel = optionlist.curselection()
    print(compsel)
    try:
        select2 = (filelist.get(compsel[0]))
    except IndexError:
        select2 = ""
    if filelistflag == 0:
        if optsel[0] == 0:
            print("Open selected!")
            print(reader)
            print(select2)
            procopen(reader+select2)
        elif optsel[0] == 1:
            print("Cut selected!")
        elif optsel[0] == 2:
            print("Copy selected!")
            proccopy()
        elif optsel[0] == 3:
            print("Move to... selected!")
            movewindow.deiconify()
            movebutton.pack()
            moveentry.pack()
            movelabel.pack()
        elif optsel[0] == 4:
            print("Copy to... selected!")
        elif optsel[0] == 5:
            print("Rename selected!")
            renamewindow.deiconify() 
            renamelabel.pack()
            renameentry.pack()  
            renamebutton.pack() 
        elif optsel[0] == 6:
            print("Move to trash selected!")
        elif optsel[0] == 7:    
            print("Delete selected!")
    elif filelistflag == 1:
        if optsel[0] == 0:
            print("mkdir selected!")
            mkdirwindow.deiconify()
            mkdirbutton.pack()
            mkdirentry.pack()
            mkdirlabel.pack()
        elif optsel[0] == 1:
            print("Paste selected!")
    print("reader: "+reader)

def proccopy():
    fullpath = filecompile+"[-/pydex/-]"
    root.clipboard_clear()
    root.clipboard_append(fullpath)
    print("copied: "+fullpath)
    root.update()

def procpaste():
    pasteread = root.clipboard_get()
    if pasteread.endswith("[-/pydex/-]"):
        pasteread = pasteread.replace("[-/pydex/-]","")
        ################################################################continue here, use shutil copytree and copy to copy the directory/file gnight
    else:
        print("No pastefiles/directories found!")

def procmove():
    movecompile = filecompile
    endcompile = moveentry.get()
    filename = filelist.get(compsel[0])
    endpath = str(moveentry.get()+filename)
    if endcompile == "":
        print("Error: No path entered!")
        movewindow.withdraw()
    elif not endcompile.endswith("/"):
        print("Error: Format incorrect! Please make sure to add a backslash at the end of your path!")
        movewindow.withdraw()
    elif os.path.exists(endcompile):
        try:
            if not search(endcompile,filename):
                shutil.move(str(movecompile), endpath)
                print(movecompile+", moving to "+ endpath)
                read(endcompile)
                movewindow.withdraw()
            else:
                print("Error: Cannot move to directory with same file/file name!")
                movewindow.withdraw()
        except PermissionError:
            print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.")
            movewindow.withdraw()
    else:
        print("Error: Path entered doesn't exist!")
        movewindow.withdraw()

def procmkdir(path):
    mkdcompile = path+mkdirentry.get()
    if mkdirentry.get() == "":
        print("No name entered!")
    else:
        try:
            os.mkdir(mkdcompile)
            read(mkdcompile)
        except FileExistsError:
            print("Error: Directory with the same name already exists!")
        except PermissionError:
            print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.")
    mkdirwindow.withdraw()
    

def procopen(selected):
    print("procopen")
    if selected.endswith("/") == False:
        if system == "Linux":
            #linux is pretty complicated because using the internal handler xdg-open requires "container rights"
            #so I found a workaround where webbrowser actually handles all the internal handlers (haha see what i did there)
            posixfile = "file://"+selected
            print(posixfile)
            webbrowser.open(posixfile)
        elif system == "Windows":
            #windows doesn't care about containers it just throws the link at someone else lol
            os.startfile(selected)
    elif selected.endswith("/") == True:
        read(selected)

def procrename():
    global filecompile,dirlist
    print(dirlist)
    dstcompile = reader+renameentry.get()
    print(filelist.curselection())
    if renameentry.get() == "":
        print("Error: No name entered!")
    elif dstcompile == filecompile or renameentry.get() in dirlist:
        print("Error: File match found, cannot rename in same directory!")
        pass
    else:
        print(filecompile, dstcompile)
        try:
            shutil.move(str(filecompile), str(dstcompile))
            print(filecompile+", moving to "+ renameentry.get())
        except PermissionError:
            print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.")
        
    renamewindow.withdraw()
    
    read(reader)

def optionselect(event):
    global filecompile, filelistflag, compsel
    compsel = filelist.curselection()
    try:
        selectopt = compsel[0]
        print(selectopt)
        selectopt = (filelist.get(compsel[0])) #gets the name of the item chosen, zero indexed
        print(str(selectopt)+" selected!")
        filecompile = reader+selectopt
        filelistflag = 0
        optionlist.delete(0,END)
        optionlist.insert(END, "Open")
        optionlist.insert(END, "Cut")
        optionlist.insert(END, "Copy")
        optionlist.insert(END, "Move to...")
        optionlist.insert(END, "Copy to...")
        optionlist.insert(END, "Rename")
        optionlist.insert(END, "Move to trash")
        optionlist.insert(END, "Delete")
    except IndexError:
        print("Global option selected!")
        filelistflag = 1
        optionlist.delete(0,END)
        optionlist.insert(END,"Make directory...")
    optionshow(event)



#ROOT BELOW

root = Tk()
root.geometry("600x400")
style = ttk.Style(root)
style.theme_use('clam')
reader = ""
root.title("PyDex")
pathvalue = ttk.Entry(root)
test = ttk.Label(root, text="This is a test of the directory scanning system.")
trigger1 = ttk.Button(root, text="scan directory", command=lambda:read(pathvalue.get()))
kill = ttk.Button(root, text="Exit program",command=root.destroy)
filebar = ttk.Scrollbar(root)
filepathlabel = ttk.Label(root, text="")
backbtn = ttk.Button(root, text="Back", command=lambda:back(reader)) #lambdas are used to signify a delay in python's function calling, specifically the called function bound to this button.
filelist = Listbox(root, yscrollcommand=filebar.set, width=50, height=10)
filelist.bind("<Double-Button-1>",doubleselect)
filelist.bind("<Button-3>",optionselect)


optionlist = Listbox(root)
optionlist.insert(END, "Open")
optionlist.insert(END, "Cut")
optionlist.insert(END, "Copy")
optionlist.insert(END, "Move to...")
optionlist.insert(END, "Copy to...")
optionlist.insert(END, "Rename")
optionlist.insert(END, "Move to trash")
optionlist.insert(END, "Delete")


renamewindow = Toplevel(root)
renamewindow.title("Rename file")
renamewindow.geometry("300x100")
renamelabel = ttk.Label(renamewindow, text="Rename file to:")
renameentry = ttk.Entry(renamewindow)
renamebutton = ttk.Button(renamewindow, text="Rename", command=procrename)
renamewindow.withdraw()

mkdirwindow = Toplevel(root)
mkdirwindow.title("Make directory")
mkdirwindow.geometry("300x100")
mkdirlabel = ttk.Label(mkdirwindow, text="Enter the name of the new directory:")
mkdirentry = ttk.Entry(mkdirwindow)
mkdirbutton = ttk.Button(mkdirwindow, text="Create", command=lambda:procmkdir(reader))
mkdirwindow.withdraw()

movewindow = Toplevel(root)
movewindow.title("Move to")
movewindow.geometry("300x100")
movelabel = ttk.Label(movewindow, text="Enter the path to the directory:")
moveentry = ttk.Entry(movewindow)
movebutton = ttk.Button(movewindow, text="Move", command=procmove)
movewindow.withdraw()

#TKINTER ELEMENT PROCESSES
optionlist.bind('<Double-Button-1>', actionselect)
filelist.bind("<Double-Button-1>",doubleselect)
filelist.bind("<Button-3>",optionselect)
filelist.bind("<Button-1>",optionhide)

#FUNCTIONS BELOW
def exitcatcher(): #A KILL CATCH DESIGNED TO CLOSE ALL WORKING THREADS BEFORE EXITING
    print("goodbye world...")


def back(target):
    global reader, toggle
    optionlist.pack_forget()
    toggle = 0
    print(reader)
    if system == "Linux":
        if reader == "/":
            print("You are already at the first directory!")
        else:
            compile = reader[:reader.rindex("/")]
            compile = compile[:(compile.rindex("/"))+1]
            read(compile)
    elif system == "Windows":
        if reader == "C:/":
            print("You are already at the first directory!")
        else:
            compile = reader[:reader.rindex("/")]
            compile = compile[:(compile.rindex("/"))+1]
            read(compile)

def search(path, starget):
    searchlist = []
    sdirlist = []
    for(roots,dirs,files) in os.walk(path, topdown=True):
        searchlist = files
        for dir in dirs:
            sdirlist.append(dir+"/")
        dirs[:] = []
    searchlist = sdirlist + searchlist
    if starget in searchlist:
        return True
    else:
        return False

def read(target):
    global reader, dirlist, toggle
    optionlist.pack_forget()
    toggle = 0
    dirlist = []
    for(roots,dirs,files) in os.walk(target, topdown=True):
        #exec(roots=dirs+files)
        reader = roots
        variable = {}
        print(target)
        dirhandler = []
        for dir in dirs:
            dirhandler.append(dir+"/")
            dirlist.append(dir+"/")
        sort = dirhandler+files
        sort.sort()
        if [""] in sort:
            print("Nothing found in directory \""+ roots + "\"!")
        variable[roots]= sort
        listhandler = sort
        dirlist += sort
        #print(dirlist)
        #print(variable[roots])
        qcounter = 0
        filelist.delete(0,END)
        for dirfiles in listhandler:
            if qcounter != 0:
                filelist.insert(END, dirfiles)
                qcounter += 1
            else:
                filelist.delete(0,END)
                filelist.insert(END, dirfiles)
                qcounter += 1

        dirs[:] = [] #really important for stopping the neverending train which is os.walk haha
    try:
        filepathlabel.config(text="Current path: "+roots)
    except:
        print("Nothing scanned")

atexit.register(exitcatcher)


#this entire chunk below is the inital commands run at start, which checks the system platform, 
#and starts the user at the highest branch of their respective OS.
print(os.name, platform.system())
system = platform.system()
if system == "Windows":
    read("C:/")
elif system == "Linux":
    read("/")
else:
    m = input("This project was designed for Windows and Linux support, sorry! Press enter to exit.")
    sys.exit(0)

#TKINTER ELEMENTS/DEFINITIONS



#PACKS
renamewindow.protocol('WM_DELETE_WINDOW', renamewindow.withdraw)
mkdirwindow.protocol("WM_DELETE_WINDOW", mkdirwindow.withdraw)
filebar.pack(side = RIGHT, fill=Y)
filelist.pack(side = RIGHT, fill = BOTH)
pathvalue.pack()
trigger1.pack()
backbtn.pack()
kill.pack()
test.pack()
filepathlabel.pack()
#CONFIGS
filebar.config(command=filelist.yview)

root.mainloop()