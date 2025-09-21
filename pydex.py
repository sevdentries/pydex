import os 
import sys
import atexit
import shutil
import time
from tkinter import *
from tkinter import ttk
import getpass
reader = ""
toggle = 1

def optionshow(event):
    global toggle
    toggle = 1
    optionlist.pack()

def optiontoggle(event):
    global toggle
    if toggle == 1:
        optionlist.pack_forget()
        toggle = 0
    elif toggle == 0:
        optionlist.pack()
        toggle = 1

def optionhide(event):
    global toggle
    optionlist.pack_forget()
    toggle = 0

def doubleselect(event):
    global reader
    compsel = filelist.curselection()
    select = compsel[0]
    select = (filelist.get(compsel[0]))
    if select.endswith("/"):
        read(reader+select)
        print("hi")

def optionselect(event):
    compsel = filelist.curselection()
    try:
        selectopt = compsel[0]
        selectopt = (filelist.get(compsel[0]))
        print(str(selectopt)+" option selected!")
    except IndexError:
        print("Global option selected!")
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
backbtn = ttk.Button(root, text="Back", command=lambda:back(reader))
filelist = Listbox(root, yscrollcommand=filebar.set)
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
#TKINTER ELEMENT PROCESSES
filelist.bind("<Double-Button-1>",doubleselect)
filelist.bind("<Button-3>",optionselect)
filelist.bind("<Button-1>",optionhide)

#FUNCTIONS BELOW
def exitcatcher(): #A KILL CATCH DESIGNED TO CLOSE ALL WORKING THREADS BEFORE EXITING
    print("killcatch triggered!")
    time.sleep(3)

def back(target):
    global reader
    print(reader)
    if reader == "/":
        print("You are already at the first directory!")
    else:
        compile = reader[:reader.rindex("/")]
        compile = compile[:(compile.rindex("/"))+1]
        read(compile)

def read(target):
    global reader
    for(roots,dirs,files) in os.walk(target, topdown=True):
        #exec(roots=dirs+files)
        reader = roots
        variable = {}
        print(target)
        dirhandler = []
        for dir in dirs:
            dirhandler.append(dir+"/")
        sort = dirhandler+files
        sort.sort()
        if [""] in sort:
            print("Nothing found in directory \""+ roots + "\"!")
        variable[roots]= sort
        listhandler = sort
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

        dirs[:] = []
    try:
        filepathlabel.config(text="Current path: "+roots)
    except:
        print("Nothing scanned, did you click Scan Directory with nothing in the textbox?")

atexit.register(exitcatcher)

print(os.name)
if os.name == "nt":
    system = "win"
    trashpath = "C:/$Recycle.Bin/"
    try:
        read(trashpath)
    except:
        print("ERROR: No trash directory found!!! DO NOT DELETE ANYTHING!!!")
    read("C:/")
elif os.name == "posix":
    system = "linux"
    try:
        trashpath = "/home/"+getpass.getuser()+"/.local/share/Trash"
        read(trashpath)
    except:
        print("No trash path found! Creating...")
        trashpath = "/home/"+getpass.getuser()+"/.local/share/Trash"
        #os.mkdir(trashpath)
    read("/")
else:
    m = input("This project was designed for Windows and Linux support, sorry! Press enter to exit.")
    sys.exit(0)

#TKINTER ELEMENTS/DEFINITIONS



#PACKS
filebar.pack(side = RIGHT, fill=Y)
filelist.pack(side = RIGHT, fill = BOTH)
optionlist.pack()
pathvalue.pack()
trigger1.pack()
backbtn.pack()
kill.pack()
test.pack()
filepathlabel.pack()
#CONFIGS
filebar.config(command=filelist.yview)



root.mainloop()