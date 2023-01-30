import pickle
import time
from threading import Thread
from tkinter import messagebox


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Folder(metaclass=Singleton):
    pass

    def __init__(self):
        try:
            f = open("./repertoire.txt", "rb")
            self.repertoire = pickle.load(f)
            f.close()

            def confirm():
                time.sleep(2)
                messagebox.showinfo("Confirmation",
                                    "Profile chrome chargé")

            thread1 = Thread(target=confirm)
            thread1.start()
        except Exception as e:
            print(e)
            self.repertoire = ""

            def aide():
                time.sleep(10)
                messagebox.showinfo("Capsule d´aide",
                                    "1) Entrez ´chrome://version/´ dans votre navigateur\n 2) Recuperez le chemin de ´C:/Users/user/AppData/Local/Google/Chrome/User Data´ \n3) Fermez le navigateur tout de suite apres")

            thread1 = Thread(target=aide)
            thread1.start()

        self.currentUrl = ""
        self.currentPage = 0
        self.total = 0
        self.total_recupere = 0

    # getter method
    def get_repertoire(self):
        return self.repertoire

    # setter method
    def set_repertoire(self, rep):
        self.repertoire = rep

    def get_total(self):
        return self.total

    # setter method
    def set_total(self, rep):
        self.total = rep

    def get_total_recup(self):
        return self.total_recupere

    # setter method
    def set_total_recup(self, rep):
        self.total_recupere = rep

    # getter method
    def get_currentUrl(self):
        return self.currentUrl

    # setter method
    def set_currentUrl(self, rep):
        self.currentUrl = rep

    # getter method
    def get_currentPage(self):
        return (self.currentPage)

    # setter method
    def set_currentPage(self, rep):
        self.currentPage = rep

    def erease(self):
        self.currentUrl = ""
        self.currentPage = 0
        self.total = 0
