import pyqtgraph as pg
import numpy as np
import PyQt5 as qt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
import sys
from urllib.request import urlopen
import time

import platform
import ctypes
if platform.system()=='Windows' and int(platform.release()) >= 8:  #prevents axis misalignment when going between monitors
  ctypes.windll.shcore.SetProcessDpiAwareness(True) #https://stackoverflow.com/questions/69140610/pyqtgraph-when-show-in-a-different-screen-misalign-axis

class livePlotTemplateGUI(QtWidgets.QMainWindow):
  def __init__(self):
    self.wordList = np.loadtxt('WordList.txt',dtype=str)
    np.random.shuffle(self.wordList);
    self.wordIndex=0

    super().__init__()
    self.setWindowTitle('Freestyle Trainer')
    self.setWindowIcon(QIcon('FreestylePracticeIcon.jpg'))
    self.cw=QtWidgets.QWidget(); self.cw.sizeHint=lambda: QtCore.QSize(600,400)
    self.setCentralWidget(self.cw) #create empty widget and set it as central widget
    self.verticalLayout = QtWidgets.QVBoxLayout(); self.cw.setLayout(self.verticalLayout) #create horizontal layout, and set central widget to use this layout. This will hold everything

    '''Adding label and button and such'''
    self.targetRhymeLabel=QtWidgets.QLabel('TEST'); self.targetRhymeLabel.setStyleSheet(''' font-size: 72px; color:Blue;''')
    self.targetRhymeLabel.setAlignment(QtCore.Qt.AlignCenter)
    self.verticalLayout.addWidget(self.targetRhymeLabel)

    self.horizontalLayout1 = QtWidgets.QHBoxLayout(); self.verticalLayout.addLayout(self.horizontalLayout1)

    self.rhymeSuggestionsLabel1=QtWidgets.QLabel('TEST'); self.rhymeSuggestionsLabel1.setStyleSheet(''' font-size: 24px; color:Gray;''')
    self.rhymeSuggestionsLabel1.setAlignment(QtCore.Qt.AlignCenter)
    self.horizontalLayout1.addWidget(self.rhymeSuggestionsLabel1)
    self.rhymeSuggestionsLabel2=QtWidgets.QLabel('TEST'); self.rhymeSuggestionsLabel2.setStyleSheet(''' font-size: 24px; color:Gray;''')
    self.rhymeSuggestionsLabel2.setAlignment(QtCore.Qt.AlignCenter)
    self.horizontalLayout1.addWidget(self.rhymeSuggestionsLabel2)

    self.horizontalLayout2 = QtWidgets.QHBoxLayout(); self.verticalLayout.addLayout(self.horizontalLayout2)
    self.nextButton = QtWidgets.QPushButton('next'); self.horizontalLayout2.addWidget(self.nextButton) #button to trigger next word
    self.nextButton.clicked.connect(self.updateFunction) #button to toggle to next word

    self.currentlyLive=True
    self.startButton = QtWidgets.QPushButton('stop'); self.horizontalLayout2.addWidget(self.startButton) #button to start and stop live auto refresh
    self.startButton.clicked.connect(self.toggleUpdates)

    self.dt=0; self.interval=5
    self.intervalSpinBox = QtWidgets.QSpinBox(value=self.interval, minimum=1); self.horizontalLayout2.addWidget(self.intervalSpinBox) #spin box to adjust word refresh interval
    self.intervalSpinBox.valueChanged.connect(lambda x: self.setInterval(x))

    self.progressBar=QtWidgets.QProgressBar(); self.verticalLayout.addWidget(self.progressBar) #progress bar to track word refresh interval

    '''creating thread for live-plotting'''
    self.updateFunction()
    self.timer = QtCore.QTimer() #As I understand it, the timer object is basically QT's built-in version of creating a new thread
    self.timer.setInterval(100) #update interval is measured in ms
    self.timer.timeout.connect(self.callUpdater)#updateFunction)
    self.timer.start()

  def callUpdater(self):
    if self.currentlyLive:
      self.dt+=0.1
      if self.dt>self.interval:
        self.updateFunction()
      else: self.progressBar.setValue(int(100*self.dt/self.interval)+1)
    #else: print('sleepy')

  def toggleUpdates(self): #this is what gets called whenever we click the button
    self.currentlyLive=not(self.currentlyLive)
    self.startButton.setText('stop') if self.currentlyLive else self.startButton.setText('start')

  def setInterval(self, x): 
    self.interval=x
    self.progressBar.setValue(min(100,int(100*self.dt/self.interval)+1))

  def updateFunction(self):
    #every update interval, this function is called
    self.wordIndex+=1;
    if self.wordIndex>len(self.wordList):
      np.random.shuffle(self.wordList);
      self.wordIndex=0
    self.targetRhymeLabel.setText(self.wordList[self.wordIndex])
    try: self.generateSuggestions()
    except:
      self.rhymeSuggestionsLabel1.setText('Failed to scrape\nrhymezone :(\nCheck your internet')
      self.rhymeSuggestionsLabel2.setText('Bug Alex if that \ndoesn\'t solve \n the problem.')
    self.dt=0
    self.progressBar.setValue(0)
    #self.time=time.time()

  def generateSuggestions(self):
    word=self.wordList[self.wordIndex]
    url = "https://www.rhymezone.com/r/rhyme.cgi?Word=%s&org1=syl&org2=l&org3=y&typeofrhyme=nry"%word
    page = urlopen(url)
    html = page.read().decode("utf-8")
    startIndex=html.find('API_RESULTS')
    stopIndex=html.find('var CACHED_API_URL')
    goodLine='self.'+html[startIndex:stopIndex]
    exec(goodLine)
    rhymeSuggestionsL=''
    rhymeSuggestionsR=''
    for i in range(1,11):
      nextWord=self.API_RESULTS[i]['word']
      if i%2==0:
        rhymeSuggestionsR+=nextWord+'\n'
      else:
        rhymeSuggestionsL+=nextWord+'\n'
    self.rhymeSuggestionsLabel1.setText(rhymeSuggestionsL)
    self.rhymeSuggestionsLabel2.setText(rhymeSuggestionsR)

if __name__ == '__main__':
  app = QtWidgets.QApplication(sys.argv)
  window = livePlotTemplateGUI()
  window.show()
  sys.exit(app.exec_())