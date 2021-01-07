import tkinter as tk
import os

path = "./neat/data/"
creatures = os.listdir(path)

def okCallback(root : tk.Tk, listbox : tk.Listbox):
    if listbox.curselection != ():
        name = creatures[listbox.curselection()[0]]
        print(listbox.curselection()[0])
        root.destroy()
        initSelected(root, name)


def initSelected(root : tk.Tk, name : str):
    root = tk.Tk()
    root.title(name)
    saveFiles = [f for f in os.listdir(path + name) if
        os.path.isfile(os.path.join(path + name, f)) and
        f.endswith(".neat") and f[0:-5].isdigit()]
    saveFiles = sorted(saveFiles, key = lambda x : x[0:-5])
    top = saveFiles[-1]
    highGen = tk.Label(root, text="Highest generation: " + top)

    highGen.pack()

    tk.mainloop()

def newCallback():
    pass


def init():
    root = tk.Tk()
    root.title("Select Creature")
    listbox = tk.Listbox(root, selectmode=tk.SINGLE)
    print(creatures)
    for i in range(len(creatures)):
        if not os.path.isfile(os.path.join(path, creatures[i])):
            listbox.insert(i, creatures[i])
            print(i)
    new = tk.Button(root, text="New Creature", command = newCallback)
    ok = tk.Button(root, text="Okay", command = lambda : okCallback(root, listbox))

    listbox.pack(side = tk.TOP)
    new.pack(side = tk.LEFT)
    ok.pack(side = tk.RIGHT)
    tk.mainloop()


if __name__ == "__main__":
    init()