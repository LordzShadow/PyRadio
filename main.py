import vlc
import sys
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2. QtGui import QColor
from PySide2.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QListWidget


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.streams = {}

        with open("radios.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                nline = line.strip().split(":", 1)
                self.streams[nline[0]] = nline[1]
            print(self.streams)

        self.radio = vlc.MediaPlayer("http://retro.babahhcdn.com/RETRO")
        self.playing = False

        self.pal = QtGui.QPalette(self.palette())
        self.pal.setColor(self.pal.Background, QColor(10,10,10,255))
        self.setPalette(self.pal)
        self.pal.setColor(self.pal.Text, QColor(255, 255, 255, 255))
        self.playing_label = QLabel("Stopped")
        self.label = QLabel("Radios:")
        self.playing_label.setPalette(self.pal)
        self.label.setPalette(self.pal)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.playing_label.setAlignment(QtCore.Qt.AlignCenter)
        self.pal.setColor(self.pal.Button, QColor(30, 30, 30, 255))
        self.btn = QPushButton("Play/Stop")
        self.btn.setPalette(self.pal)
        self.btn.clicked.connect(self.control)
        self.list = QListWidget()
        self.pal.setColor(self.pal.Base, QColor(20, 20, 20, 255))
        self.list.setPalette(self.pal)
        self.pal.setColor(self.pal.Text, QColor(255, 255, 255, 255))
        self.list.setPalette(self.pal)

        for n in self.streams:
            self.list.addItem(n)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.playing_label)
        self.layout.addWidget(self.btn)

        self.setLayout(self.layout)

    def control(self):

        if self.playing:
            self.radio.stop()
            self.playing_label.setText("Stopped")
            self.playing = False
        else:
            self.play()

    def play(self):
        current = self.list.currentItem().text()
        for i in self.streams:
            if current == i:
                current = self.streams[i]
                break
        self.radio = vlc.MediaPlayer(current)
        self.radio.play()
        self.playing_label.setText("Playing")
        self.playing = True


if __name__ == "__main__":

    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(600, 400)
    widget.show()

    sys.exit(app.exec_())
