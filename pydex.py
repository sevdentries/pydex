import os 
import sys
import atexit
import shutil
import webbrowser
import platform
import time
from tkinter import *
from tkinter import ttk
import getpass
reader = ""
toggle = 1
filecompile = ""

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
    print("test")
    global reader
    compsel = filelist.curselection()
    try:
        select = compsel[0]
    except IndexError:
        print("No file selected!")
    select = (filelist.get(compsel[0]))
    if select.endswith("/"):
        read(reader+select)
        print("hi")

def actionselect(event):
    compsel = optionlist.curselection()
    if compsel[0] == 0:
        print("Open selected!")
        procopen()
    elif compsel[0] == 1:
        print("Cut selected!")
    elif compsel[0] == 2:
        print("Copy selected!")
    elif compsel[0] == 3:
        print("Move to... selected!")
    elif compsel[0] == 4:
        print("Copy to... selected!")
    elif compsel[0] == 5:
        print("Rename selected!")
        renamewindow.deiconify()
        renamelabel.pack()
        renameentry.pack()  
        renamebutton.pack() 

    elif compsel[0] == 6:
        print("Move to trash selected!")
    elif compsel[0] == 7:    
        print("Delete selected!")

def procopen():
    webbrowser.open(filecompile)

def procrename():
    global filecompile
    print(filelist.curselection())
    if renameentry.get() == "":
        print("No name entered!")
        renamewindow.withdraw()
        return
    else:
        dstcompile = reader+renameentry.get()
        print(filecompile, dstcompile)
        shutil.move(str(filecompile), str(dstcompile))
    fileinquestion = filecompile
    renamewindow.withdraw()
    print(fileinquestion+", moving to "+ renameentry.get())
    read(reader)

def optionselect(event):
    global filecompile
    compsel = filelist.curselection()
    try:
        selectopt = compsel[0]
        selectopt = (filelist.get(compsel[0]))
        print(str(selectopt)+" option selected!")
        filecompile = reader+selectopt
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
renamewindow = Toplevel(root)
renamewindow.title("Rename file")
renamewindow.geometry("300x100")
renamewindow.withdraw()
renamelabel = ttk.Label(renamewindow, text="Rename file to:")
renameentry = ttk.Entry(renamewindow)
renamebutton = ttk.Button(renamewindow, text="Rename", command=procrename)
#TKINTER ELEMENT PROCESSES
optionlist.bind('<Double-Button-1>', actionselect)
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
system = platform.system()
if system == "Windows":
    trashpath = "C:/$Recycle.Bin/"
    try:
        read(trashpath)
    except:
        print("ERROR: No trash directory found!!! DO NOT DELETE ANYTHING!!!")
    read("C:/")
elif system == "Linux":
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