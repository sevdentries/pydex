import os 
import sys
import atexit
import shutil
import platform
import webbrowser 
import warnings
import stat
import getpass
import time
from urllib.request import urlopen
from tkinter import *
from tkinter import ttk
import tkinter as tk
projectlink = "https://github.com/sevdentries/pydex"
system = platform.system()
reader = "" #A global tracker to store the current directory being read.
toggle = 1 #A simple toggle flag for showing/hiding the option panel.
filecompile = "" 
compsel = () #A global tracker to store the current selected file index under filelist. This differs from optsel which locally tracks indexes under optionlist.
dirlist = []
filelistflag = 0 #A flag which is raised when a person decides to open options for the entire directory instead of a specific file
clipstore = "" #A storage variable for the user's previous clipboard store, used for cut/copy/paste.
entryflag = 0
user = getpass.getuser()

def optionshow(event): #command for showing the optionlist. the other two functions below are also self explanatory.
    global toggle
    toggle = 1
    optionlist.grid()

def optiontoggle(event): #togglescript to show/hide the option panel.
    global toggle
    if toggle == 1:
        optionlist.grid_remove()
        toggle = 0
    elif toggle == 0:
        optionlist.grid()
        toggle = 1

def optionhide(event): #command for hiding the optionlist.
    global toggle
    optionlist.grid_remove()
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

def procrename(): #renaming files, wow
    global filecompile,dirlist,compsel
    print(dirlist) #dirlist is a list containing the current contents of the directory being read.
    dstcompile = reader+renameentry.get() #assemble the target path of the new file based on the user's entry in renameentry
    compsel = filelist.curselection() #also get the index of the file selected for the next line
    filename = (filelist.get(compsel[0])) #retrieve the filename by fetching the index compsel in filelist. returns the original filename.
    fileprefix = "."+(filename.split("."))[-1] 
    #above, 
    #separate the text and find the file's extension by splitting the name into a list by "." and retrieving the last entry on the list.
    print(fileprefix) #program uses this as reference for the next couple lines.
    if "." in renameentry.get(): #if the user has specified the extension, leave it be and let shutil.move change the extension.
        print("Prefix detected!")
    else: #if the user just enters a name with no extension, add back the file's original extension and update the final path to dstcompile.
        dstcompile = reader + renameentry.get() + fileprefix
        print("Reconstructed prefixes with prefix: "+fileprefix)

    if renameentry.get() == "": #error handling to check if user input is empty
        print("Error: No name entered!")
    elif dstcompile == filecompile or renameentry.get() in dirlist: #check for a matching file with the same name in the directory
        print("Error: File match found, cannot rename in same directory!")
    else:
        print(filecompile, dstcompile)
        try: #error handling try statement
            shutil.move(str(filecompile), str(dstcompile)) 
#shutil.move is versatile because if you change the filename in destination with the same path it will essentially just rename the file.
            print(filecompile+", moving to "+ renameentry.get())
        except PermissionError: #straight forward
            print("Error: Permission denied. Maybe try running pydex with sudo/administration permissions for this.")
        
    renamewindow.withdraw() #close the window.
    
    read(reader) #and make sure to refresh!

def optionselect(event): 
    #listboxes in tkinter have to programmatically make entries for lists. so for something like a list of options with changing
    #options based on the user's selection, there has to be a script that logically decides what entries to add to the optionlist
    #based on what the user has selected; that is what optionselect does.
    #there are two main choices: user selects options for a specific file, or user selects options for the directory being displayed.

    global filecompile, filelistflag, compsel #need some globals first
    compsel = filelist.curselection() #this alone can decide the choice because if the user hasn't selected anything
    #and called the optionselect() function, an empty tuple is returned.
    try:
        selectopt = compsel[0] #jank logic but the choice is here where if the tuple is empty it will raise exception IndexError.
        print(selectopt)
        selectopt = (filelist.get(compsel[0])) #gets the name of the file chosen, zero indexed
        print(str(selectopt)+" selected!")
        filecompile = reader+selectopt #filecompile is not used in this function, but it is helpful to update it for other functions.
        filelistflag = 0 #tell actionselect() whether the user selected a file or the whole directory.
        optionlist.delete(0,END) #clear the optionlist and then insert the options below, each entry at the end of the last.
        optionlist.insert(END, "Open")
        optionlist.insert(END, "Cut")
        optionlist.insert(END, "Copy")
        optionlist.insert(END, "Move to...")
        optionlist.insert(END, "Copy to...")
        optionlist.insert(END, "Rename")
        optionlist.insert(END, "Delete")
    except IndexError: #if compsel[0] fails, the user hasnt selected any file and we know to display options for the whole directory instead.
        print("Global option selected!")
        filelistflag = 1 #tell actionselect as well.
        optionlist.delete(0,END) #same as above, delete everything and add entries, one after another.
        optionlist.insert(END,"Make directory...")
        optionlist.insert(END, "Paste")
    optionshow(event) #and show the optionlist.

        

#ROOT BELOW
#These elements are the definitions of the elements. optionlist starts with defaults for sizing.
root = Tk() #this is the main window. the parent of all the elements.
root.geometry("600x400+100+100") #set the main window's default size.
root.minsize(600,400)  #set the main window's minimum size.

style = ttk.Style(root) #bind variable style to root's style.
style.theme_use('clam') #set root's theme as clam. this creates an off-white look that I liked.
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=1)
root.rowconfigure(6, weight=1)
root.rowconfigure(7, weight=1)
root.rowconfigure(8, weight=1)
root.rowconfigure(9, weight=1)
root.rowconfigure(10, weight=1)
root.rowconfigure(11, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=1)
root.columnconfigure(4, weight=1)
root.columnconfigure(5, weight=1)
root.columnconfigure(6, weight=1)
root.columnconfigure(7, weight=1)
root.columnconfigure(8, weight=1)
root.columnconfigure(9, weight=1)
root.grid_propagate(FALSE)


reader = "" #reader is here and not at the top because this was the first prototype's code, if it ain't broke don't fix it lol
root.title("pyDex") #set the title
pathvalue = ttk.Entry(root) #create an entry object. from here on out all objects have root as the parent of the object.
pathvalue.insert(0, "Enter a filepath...") #set the default text for entry.
trigger1 = ttk.Button(root, text="Go", command=lambda:read(pathvalue.get())) #a button which when triggered reads the entry above.
filebar = ttk.Scrollbar(root)
filepathlabel = ttk.Label(root, text="",wraplength=200)
backbtn = ttk.Button(root, text="<--", command=lambda:back(reader)) 
#lambdas are used to signify a delay in python's function calling, specifically the called function bound to this button.
#long story short when python sees a function with parentheses it will run it regardless of whether the user has clicked the button or not.
filelist = Listbox(root, yscrollcommand=filebar.set,exportselection=False) #the filelist. it displays files.
filelist.bind("<Double-Button-1>",doubleselect) #bind double left mouse clicking to doubleselect.
#these functions dont need parentheses because they use globals and the only parameter that tkinter passes is what triggered the function.
#notice how all functions bound to objects using .bind methods have an unused "event" parameter defined in the function.
filelist.bind("<Button-3>",optionselect) 
filelist.bind("<Double-Button-1>",doubleselect)
filelist.bind("<Button-3>",optionselect)
filelist.bind("<Button-1>",optionhide)

#default entries and definitions for the optionlist.
optionlist = Listbox(root)
optionlist.insert(END, "Open")
optionlist.insert(END, "Cut")
optionlist.insert(END, "Copy")
optionlist.insert(END, "Move to...")
optionlist.insert(END, "Copy to...")
optionlist.insert(END, "Rename")
optionlist.insert(END, "Delete")
optionlist.bind('<Double-Button-1>', actionselect)

#below are all the input windows for options, defined in tkinter as Toplevels. Objects in the toplevel are parented to the toplevel
#and not the root. All of them use similar commands above to define parameters and once created, immediately withdraws the window 
#by default.

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


#FUNCTIONS BELOW
def exitcatcher(): #A KILL CATCH DESIGNED TO CLOSE ALL WORKING THREADS BEFORE EXITING
    print("goodbye world...")
#there's a story behind this, originally I thought it was a good idea to index the ENTIRE computer, so i was intending to use this to
#close a subprocess which would index the entire computer in the background. This was removed because there is LITERALLY NO REASON
#to index everything all at once. What was left was this, which I thought was a good feature to leave behind because it shows up
#whenever I closed it and was funny. long story short i am not removing it lol.

#below is all the important, foundational functions of this script, which includes underlying functions such as read, back, and search.

def back(event): #goes back up the filetree by stepping back to the roots of the directory it is in.
    global reader, toggle
    optionlist.grid_remove() #hide the optionlist if it was open.
    toggle = 0 #tell other functions that optionlist is hidden.
    print(reader)
    if system == "Linux": #linux and windows have different roots, the former starting at / and latter starting at c:/ or C:/.
        if reader == "/": #there is no directory above / for linux.
            print("You are already at the first directory!")
        else: #we are not at the highest directory? ok!
            compile = reader[:reader.rindex("/")] #slice the end of the path, all the way to the last occurence of /.
            compile = compile[:(compile.rindex("/"))+1] #also get rid of the /.
            read(compile) #and finally show it to the user
    elif system == "Windows": #self explanatory.
        if reader == "C:/" or reader == "c:/": #self explanatory and same as previous if statement.
            print("You are already at the first directory!")
        else:
            compile = reader[:reader.rindex("/")] #windows and linux are great because they use the same filesystem.
            compile = compile[:(compile.rindex("/"))+1] #idk about mac because i was never rich enough to afford a mac lol.
            read(compile) #same thing.

def search(path, starget): #an internal function which uses os.walk to search a path for a target and return true if found.
    searchlist = [] #a general compile list for files walked, however initially separated from directories because they need prefixes added.
    sdirlist = [] #the compile list for directories. see the line above.
    for(roots,dirs,files) in os.walk(path, topdown=True): 
        #the important part of this program, walks a path from the top-down and returns a triple tuple containing lists of the names mentioned
        #above.
        searchlist = files
        for dir in dirs: #need another for loop to add a slash to the end of every directory, then storing them in sdirlist.
            sdirlist.append(dir+"/") #yeah.
        dirs[:] = [] #os.walk is recursive and will walk EVERY directory in your path. Stop it from doing that by emptying the "dir" list from the triple tuple.
    searchlist = sdirlist + searchlist #and finally combine all the files and directories together.
    if starget in searchlist: #check if the target is in the list.
        return True #YES!
    else:
        return False #NO!

def read(target): #THE FOUNDATIONAL FUNCTION! reads a target path using os.walk and displays it in a neat little sorted list.
    global reader, dirlist, toggle #I AM THE GLOBALS!!!!
    optionlist.grid_remove() #oh yeah close the optionlist if its open
    toggle = 0 #and tell others
    dirlist = [] #keep a list of what you have walked, like a list version of the entries to filelist (listbox).
    for(roots,dirs,files) in os.walk(target, topdown=True): #i love this function
        reader = roots #now you know what reader is from, first object in os.walk's triple tuple is a string containing the target's root path.
        print(target)
        dirhandler = [] #the list used to append all directories with a slash at the end, otherwise, we have no way of telling whether it is a directory or not.
        for dir in dirs: #the for loop that appends all dirs.
            dirhandler.append(dir+"/")
        dirhandler.sort() #sort the dirs alphabetically,
        files.sort() #sort the files alphabetically,
        sort = dirhandler+files #AND MERGE THEM!!!
        if [""] in sort: #error handling... zzz...
            print("Nothing found in directory \""+ roots + "\"!")
        listhandler = sort
        dirlist = sort
        qcounter = 0 #a counter for the files that i was intending to use later but forgot about. ill be honest lol
        filelist.delete(0,END) #delete everything in filelist before adding entries.
        for dirfiles in listhandler: #and add all the entries using a for loop.
                filelist.insert(END, dirfiles)
                qcounter += 1
        dirs[:] = [] #really important for stopping the neverending train which is os.walk haha
    try: #display the root path.
        filepathlabel.config(text="Current path: "+roots)
        
    except:
        print("Nothing scanned")
    pathvalue.delete(0,END)
    pathvalue.insert(0,roots)

def winadmin(): #function which checks if the user is an admin in windows. Linux has no way to check for elevation because it has to be manually elevated.
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        return False

atexit.register(exitcatcher) #tell python to run this function exitcatcher at exit.

#PACKS
renamewindow.protocol('WM_DELETE_WINDOW', renamewindow.withdraw)
mkdirwindow.protocol("WM_DELETE_WINDOW", mkdirwindow.withdraw)
deletewindow.protocol("WM_DELETE_WINDOW", deletewindow.withdraw)
copytowindow.protocol("WM_DELETE_WINDOW", copytowindow.withdraw)
movewindow.protocol("WM_DELETE_WINDOW", movewindow.withdraw)


#logos below
logolink = "https://raw.githubusercontent.com/sevdentries/pydex/refs/heads/main/%5BpyDex%5D.png"
try:
    with urlopen(logolink) as image:
        imgdata = image.read()
except Exception as lerror:
    print("Fetch logo failed: "+lerror)
img = PhotoImage(data=imgdata)
smallerimg = img.subsample(4,4)
logolabel = Label(root, image=smallerimg)
logolabel.bind("<Button-1>",lambda event:webbrowser.open(projectlink))

shortlogo = "https://raw.githubusercontent.com/sevdentries/pydex/refs/heads/main/%5BpD%5D.png"
try:
    with urlopen(logolink) as icimg:
        iconimg = icimg.read()
except Exception as ierror:
    print("Fetch logo failed: "+ierror)
iconlogo = PhotoImage(data=iconimg)
root.iconphoto(True, iconlogo)

#adding time, date, and greeting

def dateupdate():
    gtime = time.strftime("%H:%M:%S\n%b %d, %Y",time.localtime())
    glabeltime.config(text=gtime)
    root.after(1000, dateupdate)

gwindow = Frame(root)
usergreet = Label(gwindow,text="/welcome, "+user+"/", font=("Helvetica", 14, "bold", "italic"))
gtime = time.strftime("%H:%M:%S\n%b %d, %Y",time.localtime())
glabeltime = Label(gwindow,text=gtime, font=("Helvetica", 12, "bold"))
usergreet.pack()
glabeltime.pack()
gwindow.grid(row=1,column=0, sticky="nsew", rowspan=1,columnspan=2)
dateupdate()

#grid adjustments

filebar.grid(row=1, column=9, sticky="nsew", padx=0, pady=5)
filelist.grid(row=1, column=2, sticky="nsew", padx=5, pady=5,rowspan=10,columnspan=9)
pathvalue.grid(row=0,column=3, sticky="nsew", padx=5, pady=5, columnspan=6,rowspan=1)
trigger1.grid(row=0,column=9, sticky="nsew", padx=5, pady=5,rowspan=1,columnspan=1)
backbtn.grid(row=0,column=2, sticky="nsew", padx=5, pady=5,rowspan=1,columnspan=1)
logolabel.grid(row=0,column=0,sticky="nsew",padx=5,pady=5, rowspan=1,columnspan=2)
optionlist.grid(row=2,column=0,sticky="nsew", padx=5, pady=5,rowspan=7,columnspan=2)
optionlist.grid_remove()



#filepathlabel.pack(side=TOP)

#CONFIGS

filebar.config(command=filelist.yview)

def requestadminwin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1) #no this is not a virus this just reruns the code with admin privleges
    sys.exit(0)

def requestadminIDEWIN():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    root.title("pyDexIDE")
    root.state("iconic")
    introwindow.withdraw()

introwindow = Toplevel(root)
def introwindowclose(): #extra code that needs to be run when the user acknowledges the introwindow.
    introwindow.withdraw()
    introwindow.grab_release()
    def delay4linux():
        root.deiconify()
        root.lift()
        root.focus_set()
        if system == "Linux":
            root.focus_force()
            root.attributes("-topmost", True)
            root.attributes("-topmost", False)
    root.after(500,delay4linux)
    

introwindow.title("pyDex: Admin")
introwindow.geometry("500x200+100+100")
introlabel = ttk.Label(introwindow, text="Welcome to pydex! In some cases while interacting with pydex you may run into permission errors when using sensitive system functions. 95% of pydex can run regardless, and pydex will warn you if this happens.", wraplength=485, justify=CENTER)
introlabel2 = ttk.Label(introwindow, text="If you are running this script in an IDE and would like admin permissions, please select \"IDE Mode\" and disregard permission errors.\n\nWould you like to rerun this script with admin?", wraplength=490,justify=CENTER)
introlabel2alt = ttk.Label(introwindow, text="Since you are on Linux, please rerun the code with sudo permissions if you would like to resolve this.",wraplength=490, justify=CENTER)
introyesbutton = ttk.Button(introwindow, text="Yes", command=requestadminwin)
intronobutton = ttk.Button(introwindow, text="No", command=introwindowclose)
introidebutton = ttk.Button(introwindow, text="IDE Mode", command=requestadminIDEWIN)
introokbutton = ttk.Button(introwindow, text="I understand", command=introwindowclose)
introwindow.protocol("WM_DELETE_WINDOW", introwindowclose)
introwindow.resizable(False,False)
if system == "Windows":
    introwindow.columnconfigure(0,weight=1)
    introwindow.columnconfigure(1,weight=1)
    introwindow.columnconfigure(2,weight=1)
else:
    introwindow.columnconfigure(0,weight=1)
   
introwindow.rowconfigure(0, weight=1)
introwindow.rowconfigure(1,weight=1)
introwindow.rowconfigure(2,weight=1)

bypass = False

print("Welcome to pydex!")
if system == "Windows":
    import ctypes
    if not winadmin() and bypass == False:
        introwindow.deiconify()
        introlabel.grid(row=0,column=0,sticky="nsew", padx=5, pady=5, columnspan=3)
        introlabel2.grid(row=1,column=0,sticky="nsew", padx=5, pady=5, columnspan=3)
        introyesbutton.grid(row=2,column=0,sticky="nsew", padx=5, pady=5)
        intronobutton.grid(row=2,column=1,sticky="nsew", padx=5, pady=5)
        introidebutton.grid(row=2,column=2,sticky="nsew", padx=5, pady=5)
        introwindow.focus_force()
        introwindow.grab_set()
        root.state("iconic")
    else:
        introwindow.withdraw()
        print("Admin on!")
    read("C:/")
elif system == "Linux":
    if os.geteuid() == 0 or bypass == True:
        print("Admin on!")
        introwindow.withdraw()
    else:
        introwindow.deiconify()
        introlabel.grid(row=0,column=0,sticky="nsew", padx=5, pady=5)
        introlabel2alt.grid(row=1,column=0,sticky="nsew", padx=5, pady=5)
        introokbutton.grid(row=2,column=0,sticky="nsew", padx=5, pady=5)
        introwindow.focus_force()
        introwindow.grab_set()
        root.withdraw()
    read("/")
else:
    m = input("This project was designed for Windows and Linux support, sorry! Press enter to exit.")
    sys.exit(0)

root.mainloop()