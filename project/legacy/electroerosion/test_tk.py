from tkinter import *
from tkinter import ttk

class MyApp():
    def __init__(self):
        self.root = Tk()

        self.contFrame = LabelFrame(self.root, bg='green', text='Скорость')
        self.contFrame.grid(row=0, column=0, columnspan=2, sticky='nsew')

        self.plotFrame = LabelFrame(self.root, bg='red', text='График и отладка')
        self.plotFrame.grid(row=1, column=0, sticky='nsew')

        self.workFrame = LabelFrame(self.root, bg='blue', text='Позиционирование и эрозия')
        self.workFrame.grid(row=1, column=1, sticky='nsew')

        self.tabControlWork = ttk.Notebook(self.workFrame)
        self.tab1 = ttk.Frame(self.tabControlWork)
        self.tab2 = ttk.Frame(self.tabControlWork)
        self.tabControlWork.add(self.tab1, text='Координаты')
        self.tabControlWork.add(self.tab2, text='Звенья')
        self.tfr = ttk.Frame(self.tab1).grid(column=0, row=0, padx=30, pady=30, sticky='nsew')
        self.tfr = ttk.Frame(self.tab2).grid(column=0, row=0, padx=30, pady=30, sticky='nsew')
        self.tabControlWork.grid(row=0, column=0, sticky='nsew')
        self.tab1.grid_rowconfigure(0, minsize=200, weight=1)
        self.tab2.grid_rowconfigure(0, minsize=200, weight=1)
        self.tab1.grid_columnconfigure(0, minsize=200, weight=1)
        self.tab2.grid_columnconfigure(0, minsize=200, weight=1)

        self.root.grid_rowconfigure(0, minsize=200, weight=1)
        self.root.grid_rowconfigure(1, minsize=200, weight=1)
        self.root.grid_columnconfigure(0, minsize=200, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.root.mainloop()

if __name__ == '__main__':
    app = MyApp()
