import os
import shutil
import re
import subprocess
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def show_error_dialog(error_message):
    root.withdraw()
    messagebox.showerror("Whoopsy", error_message)
    root.quit()


def moveItems(source, destination):
    for item in os.listdir(source):
        source_file_path = os.path.join(
            source, item)
        destination_file_path = os.path.join(
            destination, item)
        if os.path.isdir(destination_file_path) and len(os.listdir(destination_file_path)) == 0:
            os.rmdir(destination_file_path)
            shutil.move(source_file_path, os.path.dirname(
                destination_file_path))
        else:
            shutil.move(source_file_path, destination_file_path)


def parseVersion(version_string):
    return tuple(map(int, re.findall(r"\d+", version_string)))


def openDirectory(file_path, argument=None, supressplugs=False):
    try:
        if ((os.path.exists(qsys_user_assets_dir_bypassed) and
            not len(os.listdir(qsys_user_assets_dir_bypassed)) == 0) or
            (os.path.exists(qsys_user_plugins_dir_bypassed) and
                not len(os.listdir(qsys_user_plugins_dir_bypassed)) == 0)):
            raise ValueError(
                "-bypassed Folders already exist with contents.  Terminating to avoid overwriting")
        if supressplugs:
            moveItems(qsys_user_assets_dir, qsys_user_assets_dir_bypassed)
            moveItems(qsys_user_plugins_dir, qsys_user_plugins_dir_bypassed)
        if os.path.exists(file_path):
            if argument:
                subprocess.Popen([file_path, argument])
            else:
                os.startfile(file_path)
        else:
            tk.messagebox.showerror("Error", f"File not found: {file_path}")
        root.quit()
    except ValueError as e:
        show_error_dialog(str(e))


def findDesignerExe(program_files_dir, folder_name):
    designer_executables = []
    target_dir = os.path.join(program_files_dir, folder_name)
    if os.path.exists(target_dir):
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path) and "Designer" in item:
                executable_path = os.path.join(item_path, "Q-Sys Designer.exe")
                if os.path.exists(executable_path):
                    designer_executables.append(executable_path)
    return designer_executables


def getVersionFromFile(file_path):
    try:
        with open(file_path, "rb") as file:
            content = file.read()
            version_match = re.search(rb"Version=(\d+(\.\d+)*)", content)
            if version_match:
                return version_match.group(1).decode("utf-8")
    except Exception as e:
        print(f"Error reading file: {e}")
    return ""


# Main


program_files_dir = os.environ.get("PROGRAMFILES", " ")
program_files_x86_dir = os.environ.get("PROGRAMFILES(x86)", " ")
qsys_user_assets_dir = os.path.join(
    os.environ["USERPROFILE"], "Documents", "QSC", "Q-Sys Designer", "Assets")
qsys_user_plugins_dir = os.path.join(
    os.environ["USERPROFILE"], "Documents", "QSC", "Q-Sys Designer", "Plugins")
qsys_user_assets_dir_bypassed = os.path.join(
    os.path.dirname(qsys_user_assets_dir), "Assets-bypassed")
qsys_user_plugins_dir_bypassed = os.path.join(
    os.path.dirname(qsys_user_plugins_dir), "Plugins-bypassed")


'''
Before doing anything, if bypassed folders exist with contents, check if 
original folders are empty because QSD was last launched w/o plugins. If
they are, move plugins back to original place from bypassed folders.  If 
there is are plugins in both places, something is wrong and an error is thrown.
'''

try:
    if os.path.exists(qsys_user_plugins_dir_bypassed):
        if not len(os.listdir(qsys_user_plugins_dir_bypassed)) == 0:
            if len(os.listdir(qsys_user_plugins_dir)) == 0:
                moveItems(qsys_user_plugins_dir_bypassed,
                          qsys_user_plugins_dir)
            else:
                raise ValueError(
                    "There are files/folders in both Plugins and Plugins-bypassed, this shouldn't happen.")
    if os.path.exists(qsys_user_assets_dir_bypassed):
        if not len(os.listdir(qsys_user_assets_dir_bypassed)) == 0:
            if len(os.listdir(qsys_user_assets_dir)) == 0 or len(os.listdir(os.path.join(qsys_user_assets_dir, "qsc-managed-plugins"))) == 0:
                moveItems(qsys_user_assets_dir_bypassed, qsys_user_assets_dir)
            else:
                raise ValueError(
                    "There are files/folders (except for an empty qsc-managed-plugins folder) in both Assets and Assets-bypassed, this shouldn't happen.")
except ValueError as e:
    show_error_dialog(str(e))


if len(sys.argv) > 1:
    file_path = ' '.join(sys.argv[1:])
    version_number = getVersionFromFile(file_path)
else:
    version_number = ""
    file_path = None


designer_executables = []
if program_files_dir:
    designer_executables.extend(findDesignerExe(program_files_dir, "QSC"))
if program_files_x86_dir:
    designer_executables.extend(findDesignerExe(
        program_files_x86_dir, "QSC Audio"))

designer_executables.sort(key=lambda x: parseVersion(
    re.search(r"\d+\.\d+", os.path.basename(os.path.dirname(x))).group()))

root = tk.Tk()
root.title("Q-SYS Launcher")
root.minsize(300, 100)
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
elif __file__:
    application_path = os.path.dirname(__file__)
iconFile = 'Icon.ico'
# root.iconbitmap(default=os.path.join(application_path, iconFile))

if version_number:
    version_label = ttk.Label(
        root, text=f"Version from file: {version_number}", font=("Arial", 14))
    version_label.pack(padx=10, pady=3)

max_button_width = max([len(os.path.basename(os.path.dirname(exe_path)))
                       for exe_path in designer_executables], default=0)

for index, exe_path in enumerate(designer_executables):
    dir_name = os.path.basename(os.path.dirname(exe_path))
    button = tk.Button(root, text=dir_name, width=max_button_width,
                       command=lambda path=exe_path: openDirectory(path, file_path))
    plugin_launch_suppress_button = tk.Button(
        root, text="Launch w/o Plugins", command=lambda path=exe_path: openDirectory(path, file_path, True))
    button.grid(row=index, column=0, padx=20, pady=3)
    plugin_launch_suppress_button.grid(row=index, column=1, padx=5, pady=3)


root.mainloop()
