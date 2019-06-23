import vlc
import sys
import os
import webbrowser
from PySide2 import QtWidgets, QtGui
from PySide2.QtGui import QColor
from PySide2.QtCore import *
from PySide2.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QListWidget, QHBoxLayout, QSystemTrayIcon

streamfile = "radios.txt"


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.streams = {}


        scriptDir = os.path.dirname(os.path.realpath(__file__))
        icon = (scriptDir + os.path.sep + "icon/pyradio.ico")
        self.setWindowIcon(QtGui.QIcon(icon))
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QtGui.QIcon(icon))

        traySignal = "activated(QSystemTrayIcon::ActivationReason)"
        QObject.connect(self.tray, SIGNAL(traySignal), self.call)

        self.radio = vlc.MediaPlayer("http://retro.babahhcdn.com/RETRO")
        self.playing = False

        self.pal = QtGui.QPalette(self.palette())
        self.pal.setColor(self.pal.Background, QColor(15, 15, 15, 255))
        self.setPalette(self.pal)
        self.pal.setColor(self.pal.Foreground, QColor(255, 255, 255, 255))
        self.playing_label = QLabel("Stopped")
        self.label = QLabel("Radios:")
        self.playing_label.setPalette(self.pal)
        self.label.setPalette(self.pal)
        self.label.setAlignment(Qt.AlignCenter)
        self.playing_label.setAlignment(Qt.AlignCenter)
        self.pal.setColor(self.pal.Button, QColor(30, 30, 30, 255))
        self.btn = QPushButton("Play/Stop")
        self.btn.setPalette(self.pal)
        self.btn.clicked.connect(self.control)
        self.list = QListWidget()
        self.pal.setColor(self.pal.Base, QColor(20, 20, 20, 255))
        self.list.setPalette(self.pal)
        self.pal.setColor(self.pal.Text, QColor(255, 255, 255, 255))
        self.list.setPalette(self.pal)
        self.pal.setColor(self.pal.Button, QColor(30, 30, 30, 255))
        self.edit = QPushButton("Edit Radios")
        self.edit.setPalette(self.pal)
        self.edit.clicked.connect(self.openfile)
        self.refresh = QPushButton("Refresh")
        self.refresh.clicked.connect(self.refreshstreams)
        self.refresh.setPalette(self.pal)

        self.refreshstreams()

        self.current = ""
        self.buttons = QHBoxLayout()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.playing_label)
        self.buttons.addWidget(self.btn)
        self.buttons.addWidget(self.edit)
        self.buttons.addWidget(self.refresh)

        self.layout.addLayout(self.buttons)
        self.setLayout(self.layout)

    def control(self):

        if self.playing and self.current == self.streams[self.list.currentItem().text()]:
            self.radio.stop()
            self.playing_label.setText("Stopped")
            self.playing = False
        else:
            self.radio.stop()
            self.play()
            print(self.current)

    def play(self):
        self.current = self.list.currentItem().text()
        for i in self.streams:
            if self.current == i:
                self.current = self.streams[i]
                break
        self.radio = vlc.MediaPlayer(self.current)
        self.radio.play()
        self.playing_label.setText("Playing")
        self.playing = True

    def openfile(self):
        webbrowser.open(streamfile)

    def refreshstreams(self):

        self.streams = {}

        with open(streamfile, "r") as file:
            lines = file.readlines()
            for line in lines:
                nline = line.strip().split(":", 1)
                self.streams[nline[0]] = nline[1]

        self.list.clear()

        for n in self.streams:
            self.list.addItem(n)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() and Qt.WindowMinimized:
                if QSystemTrayIcon.isSystemTrayAvailable():
                    self.tray.show()
                    self.hide()

    def call(self):
        self.show()
        self.tray.hide()


if __name__ == "__main__":

    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(600, 400)
    widget.show()
    widget.setWindowTitle("PyRadio")

    sys.exit(app.exec_())
