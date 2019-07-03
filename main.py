import vlc
import sys
import os
import webbrowser
from pynput import keyboard
from PySide2 import QtWidgets, QtGui
from PySide2.QtGui import QColor
from PySide2.QtCore import *
from PySide2.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QListWidget, QHBoxLayout, QSystemTrayIcon

streamfile = "radios.txt"

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.streams = {}
        scriptdir = os.path.dirname(os.path.realpath(__file__))
        icon = (scriptdir + os.path.sep + "icon/pyradio.ico")
        self.setWindowIcon(QtGui.QIcon(icon))
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QtGui.QIcon(icon))

        traysignal = "activated(QSystemTrayIcon::ActivationReason)"
        QObject.connect(self.tray, SIGNAL(traysignal), self.call)

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
        self.playing_label.setText("Playing")
        self.playing = True

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
            if self.windowState() == Qt.WindowMinimized:
                if QSystemTrayIcon.isSystemTrayAvailable():
                    self.tray.show()
                    self.hide()
                    event.ignore()
                    self.listener = keyboard.Listener(on_release=self.on_release)
                    self.listener.start()

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == Qt.Key_MediaPlay or key == Qt.Key_MediaTogglePlayPause or \
                key == Qt.Key_MediaPause:
            if self.playing:
                self.stop()
            elif not self.playing:
                self.play()
        elif key == Qt.Key_MediaNext:
            self.next()
        elif key == Qt.Key_MediaPrevious:
            self.previous()
    def call(self):
        self.show()
        self.setFocus()
        self.listener.stop()
        del self.listener
        self.tray.hide()


    def on_release(self, key):
        try:
            if key.vk == 269025044:
                if self.playing:
                    self.stop()
                elif not self.playing:
                    self.play()
            elif key.vk == 269025047:
                self.next()
            elif key.vk == 269025046:
                self.previous()
        except:
            pass
if __name__ == "__main__":

    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(600, 400)
    widget.show()
    widget.setWindowTitle("PyRadio")

    sys.exit(app.exec_())


