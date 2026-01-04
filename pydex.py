import os 
import sys
import atexit
import shutil
import platform
import webbrowser 
import warnings
import stat
from tkinter import *
from tkinter import ttk
import tkinter as tk
reader = "" #A global tracker to store the current directory being read.
toggle = 1 #A simple toggle flag for showing/hiding the option panel.
filecompile = "" 
compsel = () #A global tracker to store the current selected file index under filelist. This differs from optsel which locally tracks indexes under optionlist.
dirlist = []
filelistflag = 0 #A flag which is raised when a person decides to open options for the entire directory instead of a specific file
clipstore = "" #A storage variable for the user's previous clipboard store, used for cut/copy/paste.
entryflag = 0

def optionshow(event): #command for showing the optionlist. the other two functions below are also self explanatory.
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

def doubleselect(event): #redirects double click events to open files or read directories
    print("doubleselect")
    global reader
    compsel = filelist.curselection()
    try:
        select = compsel[0] #tkinter provides the user's selection as an index of the file in the list.
        select = (filelist.get(compsel[0])) #this uses the index and calls tkinter for the filename with the selected index compsel[0].
    except IndexError:
        warnings.warn("No file selected!") #filelist.curselection returns a list from tkinter with what the user has selected in the filelist, if the list is empty the user didn't select anything

    if not reader.endswith("/"): #directories are still read if they are missing the / at the end but it breaks my code so ill add it jic
        reader += "/"

    if select.endswith("/"): #is the file doubleclicked a file or a directory? 
        read(reader+select) #if its a directory read what is inside and show it to the user
    else:
        procopen(reader+select) #its a file, open it
        

def actionselect(event): #a redirector of actions selected by users to functions
    optsel = optionlist.curselection() #optsel is different from compsel and is used to find the optionlist's index.
    try:
        select2 = (filelist.get(compsel[0])) #procopen requires the filename selected as an arguement so we need to fetch it first
    except IndexError:
        select2 = ""
    if filelistflag == 0: #the next big elif statement just calls different features based on the order of the options in optionlist, by index.
        if optsel[0] == 0:
            print("Open selected!")
            print(reader)
            print(select2)
            procopen(reader+select2) #rootpath+filename = full path!
        elif optsel[0] == 1:
            print("Cut selected!")
            proccut() #the better functions use globals and were programmed without arguments in mind but the older ones still work so im not complaining
        elif optsel[0] == 2:
            print("Copy selected!")
            proccopy() 
        elif optsel[0] == 3:
            print("Move to... selected!")
            movewindow.deiconify() #weird function essentially just shows the window
            movebutton.pack() #also show all of the stuff inside the window, same goes for all the other packs here
            moveentry.pack()
            movelabel.pack()
        elif optsel[0] == 4:
            print("Copy to... selected!")
            copytowindow.deiconify()
            copytobutton.pack()
            copytolabel.pack()
            copytoentry.pack()
        elif optsel[0] == 5:
            print("Rename selected!")
            renamewindow.deiconify() 
            renamelabel.pack()
            renameentry.pack()  
            renamebutton.pack() 
        elif optsel[0] == 6:    
            print("Delete selected!")
            deletewindow.deiconify()
            deletelabel.pack()
            deletebuttonyes.pack()
            deletebuttonno.pack()
    elif filelistflag == 1: #A different selection of options are given if the user does not select a file, essentially options for the directory the user is in.
        if optsel[0] == 0: #See function optionselect() for how this works.
            print("mkdir selected!")
            mkdirwindow.deiconify()
            mkdirbutton.pack()
            mkdirentry.pack()
            mkdirlabel.pack()
        elif optsel[0] == 1:
            print("Paste selected!")
            procpaste()
    print("reader: "+reader) #finish the redirect script with a final debug of the rootpath.

def proccut(): #cut a selected file/directory
    global clipstore
    fullpath = filecompile+"[-/cutpydex/-]" #precompile the user's selected path and add a special set of characters for the program to detect
    if (root.clipboard_get()).endswith("[-/cutpydex/-]") or (root.clipboard_get()).endswith("[-/pydex/-]"):
        print("Warning: Double exception triggered, ignoring clipstore!") #see if the user has already cut or copy and has not pasted yet
        root.clipboard_clear()
        root.clipboard_append(clipstore) #if the user has not pasted, its an exception so maintain what was stored for the user
        root.update()
    clipstore = root.clipboard_get() #store the user's original clipboard before overwriting it
    root.clipboard_clear() #now clear it
    root.clipboard_append(fullpath) #copy the precompiled string with the special characters for pasting
    print("stored: "+clipstore)
    print("copied: "+fullpath)
    root.update() #make sure tkinter actually copies the stuff


def proccopy(): #copy a selected file/directory
    global clipstore
    fullpath = filecompile+"[-/pydex/-]" #precompile the user's selected path and add a special set of characters for the program to detect
    if (root.clipboard_get()).endswith("[-/cutpydex/-]") or (root.clipboard_get()).endswith("[-/pydex/-]"):
        print("Warning: Double exception triggered, ignoring clipstore!") #see if the user has already cut or copy and has not pasted yet
        root.clipboard_clear()
        root.clipboard_append(clipstore) #if the user has not pasted, its an exception so maintain what was stored for the user
        root.update()
    clipstore = root.clipboard_get()
    root.clipboard_clear()
    root.clipboard_append(fullpath)
    print("stored: "+clipstore)
    print("copied: "+fullpath)
    root.update() #this function fundamentally is the same as cut except gives a different set of special chars to separate the two functions

def procdelete(): #delete a file or directory

    if not os.path.isdir(filecompile):

        try: #lots of error handling cases from here on out cuz deleting stuff usually needs permission
            #WINDOWS YOU ARE STUPID
            os.remove(filecompile)
            print("File at "+filecompile+" has been deleted!")
            read(reader) #of course need to reread the filelist if we remove a file in it
            deletewindow.withdraw() #and close the confirmation window.
        except PermissionError:
            print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.") #self explanatory.
            deletewindow.withdraw()
    #os.remove does not work for directories, need a recursive delete function instead.
    else:
        try:
            shutil.rmtree(filecompile) #shutil.rmtree does that :))
            print("Directory at "+filecompile+" has been deleted!")
            read(reader) #reread the list
            deletewindow.withdraw() #delete the window
        except PermissionError: #and error handling...
            print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.")
            deletewindow.withdraw()

def procpaste(): #when the user wants to paste from the proccopy/proccut function
    global clipstore #getting old clipboard to return it after this program
    pasteread = root.clipboard_get() #get the characters in the clipboard
    if pasteread.endswith("[-/pydex/-]"): #check for the special characters from copy
        pasteread = pasteread.replace("[-/pydex/-]","") #strip the characters if it exists
        if pasteread.endswith("/"): #check if the copy is a directory
            endpath = reader+(pasteread.split("/"))[-2] + "/" #get ONLY the name of the directory by splitting at every slash and getting the second last object.
            try: #btw endpath is a precompile of the "destination" of where the user wants to paste it along with the directory name.
                shutil.copytree(pasteread,endpath) #copy the entire directory recursively to endpath.
                print("Pasting: "+pasteread+" to "+reader+"!")
                read(reader) #and refresh the filelist to see the new directory.
            except FileExistsError:
                print("ErrorD: Cannot paste to a directory with the same file!") #D just means directory, did this for debugging
            except PermissionError:
                print("ErrorD: Permission denied. Maybe try running pydex with sudo/administration permissions for this.") #yeah self explanatory
            except FileNotFoundError:
                print("Error: Source file was not found!") #so what if the user did something to the source file at the start?
        elif pasteread == "":
            print("Error: Paste is NULL! Ignoring...") #If paste prefix was found but no path was found.
        else: #okay so what if the source being pasted was a file and not a directory?
            try:
                endpath = reader+(pasteread.split("/"))[-1] #we can get the last object this time because there is no slash that splits the end into two.
                if search(reader, (pasteread.split("/"))[-1]):
                    raise FileExistsError
                else:
                    shutil.copy2(pasteread, endpath) #copy2 is a special copy that tries to also copy any special arguments in the source file.
                    print("Pasting: "+pasteread+" to "+reader+"!")
                read(reader) #refresh!
            except FileExistsError:
                print("ErrorF: Cannot paste to a directory with the same file!") #same error handling as directory
            #except PermissionError:
                #print("ErrorC2: Permission denied. Maybe try running pydex with sudo/administration permissions for this.") #yeah the same
            except FileNotFoundError:
                print("Error: Source file was not found!") #yeah pretty much the same error handling
            #except:
                #print("Error: Source file matches destination!") #got this special one becauses directory shutil.copytree thinks this case is a FileExistsError.

        root.clipboard_clear()
        root.clipboard_append(clipstore) #returns the stored clipboard to the user and the operation is finished.
        print("recopied: "+clipstore)
        root.update() #make sure tkinter actually does the clipboard stuff

    elif pasteread.endswith("[-/cutpydex/-]"): #okay so all the stuff above was just for copy, cut is mostly the same except we delete the source directory/file
        pasteread = pasteread.replace("[-/cutpydex/-]","") #also strip the special characters...
        if pasteread.endswith("/"): #my fingers hurt writing these comments, check if its directory
            endpath = reader+(pasteread.split("/"))[-2] + "/" #assemble destination filepath with same method as copy
            try:
                shutil.copytree(pasteread,endpath) #yeah its the same 
                print("Pasting: "+pasteread+" to "+reader+"!")
                shutil.rmtree(pasteread) #but we remove the source directory at the end!
                print("Deleted cut directory at: "+pasteread+"!")
                read(reader) #refresh!
            except FileExistsError: #SAME ERROR HANDLING FINGERS HURT
                print("ErrorD: Cannot paste to a directory with the same file!")
            except PermissionError:
                print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.")
            except FileNotFoundError:
                print("Error: Source file was not found!")

        elif pasteread == "":
            print("Error: Paste is NULL! Ignoring...") #also check if special characters was found but no path was found for the source
        else: #same thing as before except for file and not directory. explanations of the code are in the copy side.
            try:
                if search(reader, (pasteread.split("/"))[-1]):
                    raise FileExistsError
                else:
                    shutil.copy2(pasteread, endpath) #copy2 is a special copy that tries to also copy any special arguments in the source file.
                    print("Pasting: "+pasteread+" to "+reader+"!")
                    os.remove(pasteread) #not a directory so use file-specific remove.
                    print("Deleted cut file at: "+pasteread+"!")
                read(reader)
            except FileExistsError: #error handling, fingers hurt
                print("ErrorF: Cannot paste to a directory with the same file!")
            except PermissionError:
                print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.")
            except FileNotFoundError:
                print("Error: Source file was not found!")
            except:
                print("Error: Source file matches destination!")

        root.clipboard_clear()
        root.clipboard_append(clipstore) #and finally return the user's clipboard.
        print("recopied: "+clipstore)
        root.update() #update tkinter.
    else: #if none of the special characters was found, do nothing
        print("No pastefiles/directories found!")

def proccopyto(): #path specific copypaste function with a window.
    copyingfile = filecompile
    endcompile = copytoentry.get()
    filename = filelist.get(compsel[0]) #get the filename.
    endpath = str(copytoentry.get()+filename) #precompile the destination of the copy
    if endcompile == "": #error handling if the user enters nothing
        print("Error: No path entered!")
    elif not endcompile.endswith("/"): #my string slicing relies on the assumption that there are slashes at the end so check for it first.
        print("Error: Format incorrect! Please make sure to add a backslash at the end of your path!")
    elif os.path.exists(endcompile): #check if the path the user enters exists and is accessible by pydex.
        try:
            if not search(endcompile, filename): #call the search function to check if the file already exists in the end path
                if filename.endswith("/"): #like before copying directories and files use different functions.
                    shutil.copytree(copyingfile,endpath)
                    print("Copying Directory: "+copyingfile+" to "+endcompile+"!")
                    read(endcompile)#refresh.
                else:
                    shutil.copy2(copyingfile,endpath) #yeah.
                    print("Copying File: "+filename+" to "+endcompile+"!")
                    read(endcompile)#refresh
            else: #if the file already exists do nothing.
                print("Error: Copy source already exists at destination!")
        except PermissionError: #permission error handling.
            print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.")
    else: #error handling logic if the path doesn't exist or was not found.
        print("Error: Path entered doesn't exist!")
        
    copytowindow.withdraw() #close the window after everything is done.


def procmove(): #same thing as copy to, makes the user enter a path for the program to move.
    movecompile = filecompile #get full path of the source
    endcompile = moveentry.get() #get the user's path
    filename = filelist.get(compsel[0]) #and get only the filename to add to the destination path.
    endpath = str(moveentry.get()+filename) #user input path + filename = precompiled endpath for functions to use!
    if endcompile == "": #same error handling check if user entered nothing
        print("Error: No path entered!")
        movewindow.withdraw() #close the window after making error statement
    elif not endcompile.endswith("/"): #I NEED THE SLASH!!!! RAHHH!!!!
        print("Error: Format incorrect! Please make sure to add a backslash at the end of your path!")
        movewindow.withdraw() #also close the window.
    elif os.path.exists(endcompile): #now check if the user's entered path exists.
        try: #error handling try except statement
            if not search(endcompile,filename): #if the file/directory doesn't already exist at the user's path, time to move it.
                shutil.move(str(movecompile), endpath) #shutil.move is recursive so both file and directory work for this function.
                print(movecompile+", moving to "+ endpath)
                read(endcompile) #oh yeah this time we display the destination path so the user knows that its there now
                movewindow.withdraw() #close the input window
            else: #more errorrrrr hannnddlllinnnggg......
                print("Error: Cannot move to directory with same file/file name!")
                movewindow.withdraw()
        except PermissionError: #and self explanatory.
            print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.")
            movewindow.withdraw()
    else:
        print("Error: Path entered doesn't exist!")
        movewindow.withdraw() #i just noticed that I could have just used one withdraw statement at the end, bruh...

def procmkdir(path): #make a directory
    global reader
    mkdcompile = path+mkdirentry.get() #only need a precompile of the destination path now.
    if mkdirentry.get() == "": #error handling.
        print("No name entered!")
    else:
        try: #also error handling. zzz...
            os.mkdir(mkdcompile) #make the directory
            if system == "Windows":
                os.chmod(mkdcompile, stat.S_IREAD | stat.S_IWRITE)
            read(mkdcompile) #and open the new directory.
        except FileExistsError: #both these except statements are pretty self explanatory...
            print("Error: Directory with the same name already exists!")
        except PermissionError:
            print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.")
    mkdirwindow.withdraw() #close the input window.
    

def procopen(selected): #open (by open i mean run) things
    print("procopen") #pydex was at a standstill because of the linux side of this being stupid, see inline comments below
    if selected.endswith("/") == False: #check for 
        if system == "Linux":
            #linux is pretty complicated because using the internal handler xdg-open requires "container rights"
            #so I found a workaround where webbrowser actually "handles" all the internal handlers (haha see what i did there)
            posixfile = "file://"+selected #webbrowsers use a different prefix to indicate that the file is not a website but a local path on the computer
            print(posixfile)
            webbrowser.open(posixfile) #this method technically also works for windows but windows has better handlers sooo...
        elif system == "Windows":
            #windows doesn't care about containers it just throws the link at someone else lol
            os.startfile(selected) #windows is easier for this and just has this handler built in.
    elif selected.endswith("/") == True:
        read(selected) #just in case somehow this function gets called for a directory (don't worry doubleselect should catch this)

def procrename():
    global filecompile,dirlist,compsel
    print(dirlist)
    dstcompile = reader+renameentry.get()
    compsel = filelist.curselection()
    filename = (filelist.get(compsel[0]))
    fileprefix = "."+(filename.split("."))[-1]
    print(fileprefix)
    
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
        optionlist.insert(END, "Delete")
    except IndexError:
        print("Global option selected!")
        filelistflag = 1
        optionlist.delete(0,END)
        optionlist.insert(END,"Make directory...")
        optionlist.insert(END, "Paste")
    optionshow(event)

def entrysoftflag(event):
    global entryflag
    if entryflag == 0:
        pathvalue.delete(0,tk.END)
        entryflag = 1
        

#ROOT BELOW

root = Tk()
root.geometry("600x400")
style = ttk.Style(root)
style.theme_use('clam')
reader = ""
root.title("PyDex")
pathvalue = ttk.Entry(root)
pathvalue.insert(0, "Enter a filepath...")
#test = ttk.Label(root, text="This is a test of the directory scanning system.")
trigger1 = ttk.Button(root, text="scan directory", command=lambda:read(pathvalue.get()))
kill = ttk.Button(root, text="Exit program",command=root.destroy)
filebar = ttk.Scrollbar(root)
filepathlabel = ttk.Label(root, text="",wraplength=200)
backbtn = ttk.Button(root, text="Back", command=lambda:back(reader)) #lambdas are used to signify a delay in python's function calling, specifically the called function bound to this button.
filelist = Listbox(root, yscrollcommand=filebar.set, width=50, height=1,exportselection=False)
filelist.bind("<Double-Button-1>",doubleselect)
filelist.bind("<Button-3>",optionselect)
pathvalue.bind("<Button-1>",entrysoftflag)


optionlist = Listbox(root)
optionlist.insert(END, "Open")
optionlist.insert(END, "Cut")
optionlist.insert(END, "Copy")
optionlist.insert(END, "Move to...")
optionlist.insert(END, "Copy to...")
optionlist.insert(END, "Rename")
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

copytowindow = Toplevel(root)
copytowindow.title("Copy To")
copytowindow.geometry("300x100")
copytolabel = ttk.Label(copytowindow, text="Enter the path to the directory:")
copytoentry = ttk.Entry(copytowindow)
copytobutton = ttk.Button(copytowindow, text="Copy", command=proccopyto)
copytowindow.withdraw()

deletewindow = Toplevel(root)
deletewindow.title("Delete")
deletewindow.geometry("300x100")
deletelabel = ttk.Label(deletewindow, text="Are you sure you want to delete?")
deletebuttonyes = ttk.Button(deletewindow, text="Yes", command=procdelete)
deletebuttonno = ttk.Button(deletewindow, text="No", command=deletewindow.withdraw)
deletewindow.withdraw()

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
        if reader == "C:/" or reader == "c:/":
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

def winadmin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        return False

atexit.register(exitcatcher)


#this entire chunk below is the inital commands run at start, which checks the system platform, 
#and starts the user at the highest branch of their respective OS.
print(os.name, platform.system())
system = platform.system()
if system == "Windows":
    read("C:/")
    import ctypes
    import psutil
    #if not winadmin():
        #ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1) #no this is not a virus this just reruns the code with admin privleges
        #sys.exit(0)
    #else:
        #print("Admin on!")

elif system == "Linux":
    read("/")
else:
    m = input("This project was designed for Windows and Linux support, sorry! Press enter to exit.")
    sys.exit(0)

#PACKS
renamewindow.protocol('WM_DELETE_WINDOW', renamewindow.withdraw)
mkdirwindow.protocol("WM_DELETE_WINDOW", mkdirwindow.withdraw)
deletewindow.protocol("WM_DELETE_WINDOW", deletewindow.withdraw)
copytowindow.protocol("WM_DELETE_WINDOW", copytowindow.withdraw)
movewindow.protocol("WM_DELETE_WINDOW", movewindow.withdraw)
filebar.pack(side = RIGHT, fill=Y)
filelist.pack(side = RIGHT, fill = BOTH)
pathvalue.pack()
trigger1.pack()
backbtn.pack()
kill.pack()
#test.pack()
filepathlabel.pack(side=TOP)
#CONFIGS
filebar.config(command=filelist.yview)
root.mainloop()