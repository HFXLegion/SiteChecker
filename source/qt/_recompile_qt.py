import os

if __name__ == "__main__":
    os.system("main_window_to_py.bat")
    os.system("resources_to_py.bat")

    with open("main_window.py", "r") as resources:
        resources = resources.read()
    os.remove("main_window.py")
    with open("main_window.py", "w") as res:
        res.write(resources.replace("import resources_rc", "import qt.resources_rc"))