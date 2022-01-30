import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from .string import Format


class Qt(QtCore.Qt):
    QObject = QtCore.QObject
    QEvent = QtCore.QEvent
    QCoreApplication = QtCore.QCoreApplication


class QPixmap(QtGui.QPixmap):
    pass


class Window(QtWidgets.QMainWindow):
    def __init__(self, geometry=(160, 160), title="Main Window", parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setFixedSize(*geometry)
        self.setWindowTitle(title)

    def get_entry(self, default_text="", geometry=(10, 10, 45, 45)):
        widget = QtWidgets.QPlainTextEdit(parent=self)
        widget.insertPlainText(default_text)
        widget.setGeometry(*geometry)
        return widget

    def get_push_button(self, text="Button", geometry=(10, 10, 75, 25), icon=QtGui.QIcon(), command=lambda: None):
        widget = QtWidgets.QPushButton(parent=self, text=text, icon=icon)
        widget.setGeometry(*geometry)
        widget.clicked.connect(command)
        return widget

    def get_label(self, text="", geometry=(10, 10, 100, 25)):
        widget = QtWidgets.QLabel(parent=self, text=text)
        widget.setGeometry(*geometry)
        return widget

    def __call__(self):
        self.show()


class QtApplication(QtWidgets.QApplication):
    def __init__(self, argv=None, on_exit_event=lambda: None):
        if argv is None:
            argv = sys.argv
        super().__init__(argv)
        self.aboutToQuit.connect(on_exit_event)

    def __call__(self):
        self.exec()


class VariablesArray:
    def __init__(self):
        self.__container = {}
        self.key = None

    def add(self, element):
        if self.key is None:
            self.key = element
        else:
            self.__container[self.key] = element
            self.key = None

    def get_container(self):
        return self.__container


class Skin:
    def __init__(self, file):
        self.__file = file
        self.__name = file.split("\\")[-1][:-4]

    def get_file(self):
        return self.__file

    def get_name(self):
        return self.__name


class SkinManager:
    def __init__(self):
        self.skins = []
        self.__origin = None
        self.__main_color = {}
        self.__main_color_replace = {}
        self.get_current()

    def add(self, skin: Skin):
        if type(skin) == Skin:
            self.skins.append(skin)
        else:
            raise TypeError

    def delete(self, name):
        for index, skin in enumerate(self.skins):
            if skin.get_name() == name:
                self.skins.pop(index)
                return skin.get_file()

    def get(self, arg, by_name=True):
        for skin in self.skins:
            if skin.get_name() == arg and by_name:
                return skin.get_file()
            elif skin.get_file() == arg and not by_name:
                return skin.get_name()

    def get_current(self, ROOT):
        try:
            skin = open(f"{ROOT}\\skins\\__current__.hst")
            skin = skin.read()
            try:
                skin, variables = skin.split("--variables--")
                self.__origin = skin
            except ValueError:
                return skin
            container = VariablesArray()
            for var in variables.split("\n"):
                for element in var.split(" = "):
                    if not len(element):
                        pass
                    else:
                        container.add(element)
            for key, value in container.get_container().items():
                if key == "@main_color":
                    defined_main_color = Format.remove_spaces(Format.remove_brackets(value)).split(",")
                    if defined_main_color[0] == "rgb":
                        if len(self.__main_color_replace):
                            if self.__main_color_replace["type"] == defined_main_color[0]:
                                variables = variables.replace(f"@main_color = ({self.__main_color['type']},\
                                {self.__main_color['r']}, {self.__main_color['g']}, {self.__main_color['b']})",
                                                              f"@main_color = ({self.__main_color_replace['type']},\
                                                               {self.__main_color_replace['r']},\
                                                               {self.__main_color_replace['g']},\
                                                               {self.__main_color_replace['b']})")
                                self.__main_color = self.__main_color_replace
                        else:
                            self.__main_color["type"] = "rgb"
                            self.__main_color["r"] = defined_main_color[1]
                            self.__main_color["g"] = defined_main_color[2]
                            self.__main_color["b"] = defined_main_color[3]
                        skin = skin.replace(key, f"{self.__main_color['type']}({self.__main_color['r']},\
                        {self.__main_color['g']}, {self.__main_color['b']})")

                elif key.endswith("_main_color"):
                    defined_second_color = Format.remove_spaces(Format.remove_brackets(value)).split(",")
                    if defined_second_color[0] == "RGBdiff":
                        defined_second_color[1] = int(defined_second_color[1]) + int(self.__main_color['r'])
                        defined_second_color[2] = int(defined_second_color[2]) + int(self.__main_color['g'])
                        defined_second_color[3] = int(defined_second_color[3]) + int(self.__main_color['b'])
                        for count, color_range in enumerate(defined_second_color):
                            try:
                                defined_second_color[count] = Format.keep_range(defined_second_color[count],
                                                                                   (0, 255))
                            except TypeError:
                                pass
                        defined_second_color = Format.elements_to_datatype(defined_second_color, str)
                        skin = skin.replace(key, f"rgb({defined_second_color[1]}, {defined_second_color[2]},\
                         {defined_second_color[3]})")
                    elif defined_second_color[0] == "RGBAdiff":
                        defined_second_color[1] = int(defined_second_color[1]) + int(self.__main_color['r'])
                        defined_second_color[2] = int(defined_second_color[2]) + int(self.__main_color['g'])
                        defined_second_color[3] = int(defined_second_color[3]) + int(self.__main_color['b'])
                        for count, color_range in enumerate(defined_second_color):
                            try:
                                defined_second_color[count] = Format.keep_range(defined_second_color[count],
                                                                                   (0, 255))
                            except TypeError:
                                pass
                        defined_second_color = Format.elements_to_datatype(defined_second_color, str)
                        skin = skin.replace(key, f"rgba({defined_second_color[1]}, {defined_second_color[2]},\
                        {defined_second_color[3]}, {defined_second_color[4]})")

                for_write = open(f"{ROOT}\\skins\\__current__.hst", "w")
                for_write.write(f"{self.__origin}--variables--{variables}")
                skin = skin.replace(key, value)
        except FileNotFoundError:
            skin = open(f"{ROOT}\\skins\\__current__.hst", "w")
            skin.write("*{}")
            skin = "*{}"
        return skin

    def get_main_color_type(self):
        return self.__main_color["type"]

    def get_main_color_replace_type(self):
        return self.__main_color_replace["type"]

    def set_main_color_replace(self, new_color: {}):
        self.__main_color_replace = new_color