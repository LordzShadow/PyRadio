import vlc
import sys
import os
import webbrowser
from pynput import keyboard
from PySide2 import QtWidgets, QtGui
from PySide2.QtGui import QColor
from PySide2.QtCore import *
from PySide2.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QListWidget, QHBoxLayout, QSystemTrayIcon, \
    QSlider

streamfile = "radios.txt"


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.streams = {}
        scriptdir = os.path.dirname(os.path.realpath(__file__))
        icon = (scriptdir + os.path.sep + "icon/pyradio.ico")
        self.setWindowIcon(QtGui.QIcon(icon))
        self.setStuff()
        # Tray
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QtGui.QIcon(icon))
        self.tray.activated.connect(self.call)

        self.icon = QtGui.QIcon()
        self.icon.addFile(icon)
        self.setWindowIcon(self.icon)

        # tray menu
        self.trayIconMenu = QtWidgets.QMenu()
        self.quitAction = QtWidgets.QAction("&Quit", triggered=self.close)
        self.trayIconMenu.addAction(self.quitAction)
        self.tray.setContextMenu(self.trayIconMenu)
        self.trayIconMenu.setStyleSheet(open("css/main.css", "r").read())

        # Media player
        self.radio = vlc.MediaPlayer()
        self.playing = False

        self.pal = QtGui.QPalette(self.palette())

        self.playing_label = QLabel("Stopped")
        self.label = QLabel("Radios:")

        self.label.setAlignment(Qt.AlignCenter)
        self.playing_label.setAlignment(Qt.AlignCenter)
        self.btn = QPushButton("Play/Stop")
        self.btn.clicked.connect(self.control)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.control)

        self.edit = QPushButton("Edit Radios")
        self.edit.clicked.connect(self.openfile)
        self.refresh = QPushButton("Refresh")
        self.refresh.clicked.connect(self.refreshstreams)

        self.slider = QSlider(QtGui.Qt.Horizontal)
        self.slider.setMaximum(100)
        self.slider.setValue(self.volume)
        self.slider.valueChanged.connect(self.changeVolume)

        self.setStyleSheet(open("css/main.css", "r").read())

        self.refreshstreams()

        self.current = ""
        self.buttons = QHBoxLayout()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.playing_label)
        self.layout.addWidget(self.slider)
        self.buttons.addWidget(self.btn)
        self.buttons.addWidget(self.edit)
        self.buttons.addWidget(self.refresh)

        self.layout.addLayout(self.buttons)
        self.setLayout(self.layout)

    def setStuff(self):
        info = self.readInfo()
        print(info)
        if len(info) == 0:
            info = ["", "", "", ""]
        if (info[0] == ""):
            self.volume = 80
        else:
            self.volume = int(info[0])
        if info[3].strip() == "false" or info[3] == "":
            if info[1] == "":
                self.resize(800, 600)
            else:
                w, h = info[1].split(" ")
                self.resize(int(w), int(h))
            if info[2] != "":
                x, y = info[2].split(" ")
                self.move(int(x), int(y))
        else:
            self.showMaximized()

    def changeVolume(self):
        self.volume = self.slider.value()
        self.radio.audio_set_volume(self.volume)

    def getVolume(self):
        try:
            with open("data", "r") as file:
                return int(file.readline())
        except:
            with open("data", "w") as file:
                file.write(str(80))
                return 80

    def control(self):
        if self.playing and self.current == self.streams[self.list.currentItem().text()]:
            self.stop()
        else:
            self.radio.stop()
            self.play()

    def stop(self):
        self.radio.stop()
        self.playing_label.setText("Stopped")
        self.playing = False

    def play(self):
        self.current = self.list.currentItem().text()
        for i in self.streams:
            if self.current == i:
                self.current = self.streams[i]
                break
        self.radio = vlc.MediaPlayer(self.current)
        self.radio.play()
        self.radio.audio_set_volume(self.slider.value())
        self.playing_label.setText("Playing")
        self.playing = True
        self.tray.showMessage(self.list.currentItem().text(), "", self.tray.icon(), 1000)

    def next(self):
        isthis = False
        self.current = self.list.currentItem().text()
        for n, i in enumerate(self.streams):
            if isthis:
                self.list.setCurrentRow(n)
                break
            else:
                if self.current == i:
                    isthis = True
                    if n+1 >= len(self.streams):
                        self.list.setCurrentRow(0)
        self.stop()
        self.play()

    def previous(self):
        isthis = False
        self.current = self.list.currentItem().text()
        for n, i in enumerate(self.streams):
            if isthis:
                self.list.setCurrentRow(n-2)
                break
            else:
                if self.current == i:
                    isthis = True
                    if n-1 < 0:
                        self.list.setCurrentRow(len(self.streams) - 1)
                        break
                    elif n == len(self.streams)-1:
                        self.list.setCurrentRow(n-1)


        self.stop()
        self.play()

    def openfile(self):
        # Opens radios.txt
        webbrowser.open(streamfile)

    def refreshstreams(self):

        # Refreshes the stream list when button pressed
        if self.list.currentItem():
            current = self.list.currentItem().text()
        else:
            current = None
        self.streams = {}

        with open(streamfile, "r") as file:
            lines = file.readlines()
            for line in lines:
                nline = line.strip().split(":", 1)
                self.streams[nline[0]] = nline[1].split("#")[0]

        self.list.clear()

        for i,n in enumerate(self.streams):
            self.list.addItem(n)
            if n == current:
                self.list.setCurrentRow(i)
        if not self.list.currentItem():
            self.list.setCurrentRow(0)
    def changeEvent(self, event):

        # This minimizes the program to tray when Minimize button pressed

        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                print(QSystemTrayIcon.isSystemTrayAvailable())
                if QSystemTrayIcon.isSystemTrayAvailable() and self.isActiveWindow():
                    event.ignore()
                    self.tray.show()
                    self.hide()
                    self.listener = keyboard.Listener(on_release=self.on_release)
                    self.listener.start()

    def closeEvent(self, event):
        file = open("data", "w+")
        info = str(self.volume) + "\n" + str(self.size().width()) + " " + str(self.size().height()) + "\n" +\
               str(self.pos().x()) + " " + str(self.pos().y()) + "\n"
        if (self.isMaximized()):
            info += "true"
        else:
            info += "false"
        info += "\n"
        file.write(info)
        file.close()

    def readInfo(self):
        try:
            with open("data", "r", encoding="utf-8") as file:
                info = file.readlines()
                return info
        except:
            with open("data", "w", encoding="utf-8") as file:
                file.write("")
                return ""

    def keyReleaseEvent(self, event):

        # This is for media controls when radio is opened

        key = event.key()
        if key == Qt.Key_MediaPlay or key == Qt.Key_MediaTogglePlayPause or \
                key == Qt.Key_MediaPause:
            self.control()
        elif key == Qt.Key_MediaNext:
            self.next()
        elif key == Qt.Key_MediaPrevious:
            self.previous()

    def call(self, reason):
        # This is caled when tray icon is pressed
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()
            self.setFocus()
            self.listener.stop()
            del self.listener
            self.tray.hide()
            self.setWindowState(Qt.WindowActive)
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            self.tray.contextMenu().show()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            print("Middle click on tray icon")
        else:
            print("Unknown reason")

    def on_release(self, key):
        # This is for media controls when program in tray.
        try:
            if key == keyboard.Key.media_play_pause:  # might need a different key
                self.control()
            elif keyboard.Key.media_next == key:  # might need a different key
                self.next()
            elif keyboard.Key.media_previous == key:  # might need a different key
                self.previous()
        except AttributeError as e:
            print(e)


if __name__ == "__main__":

    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.show()
    widget.setWindowTitle("PyRadio")

    sys.exit(app.exec_())


