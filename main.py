import tkinter as tk
import tkinter.messagebox as tkm
import os
import creatures
import engine
from engine import path

creatureFiles = [f for f in os.listdir(path) if not os.path.isfile(os.path.join(path, f))]

## CALLBACK FUNCTIONS ##

def selectCallback(root : tk.Tk, listbox : tk.Listbox):
    if listbox.curselection != ():
        name = creatureFiles[listbox.curselection()[0]]
        root.destroy()
        selectInit(root, name)

def createCallback(root : tk.Tk):
    root.destroy()
    createInit(root)

def addCreatureCallback(root : tk.Tk, name : str):
    if (name in creatures.creatures):
        try:
            os.mkdir(path + name)
        except OSError:
            tkm.showinfo("Error", "Invalid input somehow")
    else:
        tkm.showinfo("Error", "Creature model does not exist")
    root.destroy()
    init()

def startCallback(name : str, top : int):
    engine.startNEAT(name, top, True)


## INIT WINDOW FUNCTIONS ##

def selectInit(root : tk.Tk, name : str):
    root = tk.Tk()
    root.title(name)
    saveFiles = [f for f in os.listdir(path + name) if
        os.path.isfile(os.path.join(path + name, f)) and
        f.endswith(".neat") and f[0:-5].isdigit()]
    saveFiles = sorted(saveFiles, key = lambda x : x[0:-5])
    top = 0 if saveFiles == [] else saveFiles[-1][0:-5]
    highGen = tk.Label(root, text="Highest generation completed: " + str(top))
    start = tk.Button(root, text="Start learning", command = lambda : startCallback(name, top))

    highGen.pack()
    start.pack()

    tk.mainloop()

def createInit(root):
    root = tk.Tk()
    root.title("New Creature")
    nameLabel = tk.Label(root, text="Creature name")
    name = tk.Entry(root)
    create = tk.Button(root, text="Add Creature", command = lambda : addCreatureCallback(root, name.get()))

    nameLabel.pack()
    name.pack()
    create.pack()
    tk.mainloop()

def init():
    global creatureFiles
    creatureFiles = [f for f in os.listdir(path) if not os.path.isfile(os.path.join(path, f))]
    root = tk.Tk()
    root.title("Select Creature")
    listbox = tk.Listbox(root, selectmode=tk.SINGLE)
    for i in range(len(creatureFiles)):
        listbox.insert(i, creatureFiles[i])
    new = tk.Button(root, text="New Creature", command = lambda : createCallback(root))
    ok = tk.Button(root, text="Okay", command = lambda : selectCallback(root, listbox))

    listbox.pack(side = tk.TOP)
    new.pack(side = tk.LEFT)
    ok.pack(side = tk.RIGHT)
    tk.mainloop()


if __name__ == "__main__":
    init()