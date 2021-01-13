import tkinter as tk
import tkinter.messagebox as tkm
import os
import creatures
import engine
from neat.NEAT import path

creatureFiles = [f for f in os.listdir(path) if not os.path.isfile(os.path.join(path, f))]
windowSize = (300, 300)


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

def startCallback(root : tk.Tk, name : str, top : int, showGUI : bool):
    root.destroy()
    e = engine.Engine(name, top, showGUI)
    e.learn_loop()


## INIT WINDOW FUNCTIONS ##

def selectInit(root : tk.Tk, name : str):
    root = tk.Tk()
    root.title(name)
    root.geometry("%dx%d+%d+%d" % (windowSize[0], windowSize[1], (root.winfo_screenwidth() - windowSize[0]) / 2, (root.winfo_screenheight() - windowSize[1]) / 2))
    saveFiles = [f for f in os.listdir(path + name) if
        os.path.isfile(os.path.join(path + name, f)) and
        f.endswith(".neat") and f[0:-5].isdigit()]
    saveFiles = sorted(saveFiles, key = lambda x : int(x[0:-5]))
    top = 0 if saveFiles == [] else saveFiles[-1][0:-5]
    highGen = tk.Label(root, text="Highest generation completed: " + str(top))
    showGUIVar = tk.BooleanVar()
    showGUI = tk.Checkbutton(root, text="Show GUI", variable=showGUIVar)
    start = tk.Button(root, text="Start learning", command = lambda : startCallback(root, name, top, showGUIVar.get()))

    highGen.pack()
    showGUI.pack()
    start.pack()

    tk.mainloop()


def createInit(root):
    root = tk.Tk()
    root.title("New Creature")
    root.geometry("%dx%d+%d+%d" % (windowSize[0], windowSize[1], (root.winfo_screenwidth() - windowSize[0]) / 2, (root.winfo_screenheight() - windowSize[1]) / 2))
    nameLabel = tk.Label(root, text="Creature name")
    name = tk.Entry(root)
    create = tk.Button(root, text="Add Creature", command = lambda : addCreatureCallback(root, name.get()))

    nameLabel.pack()
    name.pack()
    create.pack()
    tk.mainloop()


def init():
    global creatureFiles
    windowSize = (300, 300)
    creatureFiles = [f for f in os.listdir(path) if not os.path.isfile(os.path.join(path, f))]
    root = tk.Tk()
    root.title("Select Creature")
    root.geometry("%dx%d+%d+%d" % (windowSize[0], windowSize[1], (root.winfo_screenwidth() - windowSize[0]) / 2, (root.winfo_screenheight() - windowSize[1]) / 2))
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