import vlc
import sys
import os
import webbrowser
from pynput import keyboard
from PySide2 import QtWidgets, QtGui
from PySide2.QtGui import QColor
from PySide2.QtCore import *
from PySide2.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QListWidget, QHBoxLayout, QSystemTrayIcon, QSlider

streamfile = "radios.txt"


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.streams = {}
        scriptdir = os.path.dirname(os.path.realpath(__file__))
        icon = (scriptdir + os.path.sep + "icon/pyradio.ico")
        self.setWindowIcon(QtGui.QIcon(icon))

        # Tray
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QtGui.QIcon(icon))
        self.tray.activated.connect(self.call)

        self.icon = QtGui.QIcon()
        self.icon.addFile(icon)
        self.setWindowIcon(self.icon)

        #traysignal = "activated(QSystemTrayIcon::ActivationReason)"
        #QObject.connect(self.tray, SIGNAL(traysignal), self.call)

        # tray menu
        self.trayIconMenu = QtWidgets.QMenu()
        self.quitAction = QtWidgets.QAction("&Quit", triggered=QtWidgets.QApplication.instance().quit)
        self.trayIconMenu.addAction(self.quitAction)
        self.tray.setContextMenu(self.trayIconMenu)

        # Media player
        self.radio = vlc.MediaPlayer()
        self.playing = False

        self.pal = QtGui.QPalette(self.palette())

        self.pal.setColor(self.pal.Background, QColor(15, 15, 15, 255))
        self.setPalette(self.pal)

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
        self.slider.setValue(self.getVolume())
        self.slider.valueChanged.connect(self.changeVolume)

        self.pal.setColor(self.pal.Button, QColor(30, 30, 30, 255))
        self.btn.setPalette(self.pal)
        self.edit.setPalette(self.pal)
        self.refresh.setPalette(self.pal)

        self.pal.setColor(self.pal.Base, QColor(20, 20, 20, 255))
        self.list.setPalette(self.pal)

        self.pal.setColor(self.pal.Text, QColor(255, 255, 255, 255))
        self.list.setPalette(self.pal)
        self.playing_label.setPalette(self.pal)
        self.label.setPalette(self.pal)

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

    def changeVolume(self):
        self.radio.audio_set_volume(self.slider.value())
        with open("data", "w") as file:
            file.write(str(self.slider.value()))

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
            print(self.current)

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
        print(self.radio.audio_get_volume())
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

        self.streams = {}

        with open(streamfile, "r") as file:
            lines = file.readlines()
            for line in lines:
                nline = line.strip().split(":", 1)
                self.streams[nline[0]] = nline[1].split("#")[0]

        self.list.clear()

        for n in self.streams:
            self.list.addItem(n)

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
    widget.resize(600, 400)
    widget.show()
    widget.setWindowTitle("PyRadio")

    sys.exit(app.exec_())


