import tkinter as tk
from tkinter import messagebox
import os

def run_register():
    os.system("python register_student.py")

def run_dataset():
    os.system("python dataset_creator.py")

def run_train():
    os.system("python train_model.py")

def run_recognize():
    os.system("python recognize.py")

def run_dashboard():
    os.system("python dashboard.py")

# Main window
root = tk.Tk()
root.title("Smart Attendance System")
root.geometry("400x400")

# Title
title = tk.Label(root, text="Smart Attendance System",
                 font=("Arial", 16, "bold"))
title.pack(pady=20)

# Buttons
btn1 = tk.Button(root, text="Register Student", width=25, command=run_register)
btn1.pack(pady=5)

btn2 = tk.Button(root, text="Create Dataset", width=25, command=run_dataset)
btn2.pack(pady=5)

btn3 = tk.Button(root, text="Train Model", width=25, command=run_train)
btn3.pack(pady=5)

btn4 = tk.Button(root, text="Start Attendance", width=25, command=run_recognize)
btn4.pack(pady=5)

btn5 = tk.Button(root, text="View Dashboard", width=25, command=run_dashboard)
btn5.pack(pady=5)

btn_exit = tk.Button(root, text="Exit", width=25, command=root.quit)
btn_exit.pack(pady=20)

root.mainloop()