# main.py
import tkinter as tk
from DicomFileManager import DicomFileManager

def main():
    root = tk.Tk()
    app = DicomFileManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
