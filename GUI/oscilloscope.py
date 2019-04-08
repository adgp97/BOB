#!python 3.x
#################################################
## Author       : Jose Moran
## Github       : jose0796
## email        : jmoran071996@gmail.com
## file         : oscilloscope.py 
## Description  : Implementation of a Graphical 
## User Interface for serial communication and 
## plotting of data received from MC9S08QE128 
## microprocessor.  
#################################################


import sys 
from com import *
import numpy as np
import math
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation



def showScale(scl):
    
    """ Calculates scaling to show on screen
        :returns:
            A float identifying Y-axis scale 
    """

    if scl == 0:
        return 0.3 
    elif scl == 1:
        return 1.0
    elif scl == 2:
        return 3.0


def scaleYAxis(scl): 
    
    """ Calculates Y-axis scaling factor for internal data correction
        :returns:
            A float, Y-axis scaling correction for data
    """

    if scl== 0:
        return 1
    elif scl == 1:
        return 1/3
    elif scl == 2:
        return 1/9


def scaleTimeAxis(time=0):
    
    """ Calculates time axis scaling factor 
        :returns:
            A float, X-axis (time) number of data points
    """
    return 2000//(10**(time))


def timeScaleFactor(time=0):
    
    """ Calculate X-axis (time) per division
        :returns:
            A float indicating time axis scale
    """

    return 10**(-time)


def showDivScales(self,ch1: str,ch2: str, ch3: str, ch4: str, xpos, timeScale ) -> None:
    """ Shows V/div for every channel accordingly
    """
    self.axes.text(xpos,1.80,"channel 1: %.1f V/div" % ch1,color='r')
    self.axes.text(xpos,1.50,"channel 2: %.1f V/div" % ch2,color='r')
    self.axes.text(xpos,1.15,"channel 3: %.1f V/div" % ch3, color='r')
    self.axes.text(xpos,0.8,"channel 4: %.1f V/div" % ch4, color='r')
    self.axes.text(xpos,0.45,"time scale: %.1f s/div" % timeScale, color='r')

class MplCanvas(FigureCanvas):
    """ Matplotlib Canvas object for creating plotting window

    """

    def __init__(self, parent=None, width=1, height=1, dpi=100):

        #Plot config
        self.fig = plt.figure()  
        FigureCanvas.__init__(self, self.fig)
        self.axes = self.fig.add_subplot(111)
        #hide x's and y's labels 
        self.axes.set_yticklabels([])
        self.axes.set_xticklabels([])

        #Grid configuration
        
        self.axes.grid(b=True,which='major',color='k',linestyle='-')
        self.axes.minorticks_on()
        self.axes.grid(b=True,which='minor',linestyle='--')
        
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(parent) #really important to do this for the gui to show image
        self.canvas.move(60,80) 

        #these are empty arrays for channel data 
        self.channelA1 = []
        self.channelA2 = []
        self.channelD1 = []
        self.channelD2 = []

        
        self.timescale = np.linspace(start=0,stop=1,num=2000,endpoint=True)
        
        self.xticks = np.linspace(0,1,10) #these both are based on project requirements
        self.yticks = np.linspace(0,3,10)
        self.axes.xaxis.set_ticks(self.xticks) 
        self.axes.yaxis.set_ticks(self.yticks)

        #open serial port for serial communication with DEM0QE
        self.dataSerial = openPort(listPorts(sys.platform))

        
    
    def plot(self,enabledChannels,ch1=0, ch2=0, ch3=0, ch4=0,time=0):
        
        """ Closure function for _plot to be call with parameters
            
            :returns:
                A function _plot which calls update_figure.

        """
        def _plot():
            self.update_figure(enabledChannels,ch1,ch2,ch3,ch4,time)
        return _plot

    def update_figure(self,enableCh=[False for i in range(4)],ch1=0, ch2=0, ch3=0, ch4=0, time=0):
        
        self.axes.clear()
        data = [] #empty array to receive data from DEM0QE
        
        
        if len(self.channelA1) != len(self.timescale): #fill channels with data if completely empty
            while len(self.channelA1) != len(self.timescale):
                
                data = receiveData(self.dataSerial) #receive data from DEM0QE

                """ 
                    Convert data from binary to proper voltage value and scale 
                    to adjust view scale in gui. Then, append to both of analog channels.
                    For digital channels just receive and append, 1-> 3V and 0 -> 0V. 

                """
                self.channelA1.append(scaleYAxis(ch1)*convertAnalog(data[0]))
                self.channelA2.append(scaleYAxis(ch2)*convertAnalog(data[1]))
                self.channelD1.append(scaleYAxis(ch3)*convertDigital(data[2]))
                self.channelD2.append(scaleYAxis(ch4)*convertDigital(data[3]))
        else: 
        
            """
                If array already full then refresh partly in order to  
                enhance rendering performance and not get too stuck on
                data reception 
            """
            i = 0
            while i < 300:
                
                data = receiveData(self.dataSerial)
                
                #pop data from first element in order to add new ones
                self.channelA1.pop(0)
                self.channelA2.pop(0)
                self.channelD1.pop(0)
                self.channelD2.pop(0)
                self.channelA1.append(scaleYAxis(ch1)*convertAnalog(data[0]))
                self.channelA2.append(scaleYAxis(ch2)*convertAnalog(data[1]))
                self.channelD1.append(scaleYAxis(ch3)*convertDigital(data[2]))
                self.channelD2.append(scaleYAxis(ch4)*convertDigital(data[3]))
                i = i + 1

        
        ts = scaleTimeAxis(time)
        
        xlim = [timeScaleFactor(time)*i for i in [0.0, 1.0]] #set new x limit in case of new time scale 
        self.xticks = np.linspace(0,xlim[1],10) #new xticks for new time scale
        
        # All False case
        if enableCh == [False, False, False, False]:
            pass
        # All True case
        elif enableCh == [True, True, True, True]:
            self.axes.plot(self.timescale[0:ts],self.channelA1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelA2[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD2[0:ts], color='k')
        # one False case scenerios
        elif enableCh == [True, True, True, False]:
            self.axes.plot(self.timescale[0:ts],self.channelA1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelA2[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD1[0:ts], color='k')
        elif enableCh == [True, True, False, True]:
            self.axes.plot(self.timescale[0:ts],self.channelA1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelA2[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD2[0:ts], color='k')
        elif enableCh == [True, False, True, True]: 
            self.axes.plot(self.timescale[0:ts],self.channelA1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD2[0:ts], color='k')
        elif enableCh == [False, True, True, True]:
            self.axes.plot(self.timescale[0:ts], self.channelA2[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD2[0:ts], color='k')
        #######################################################################################
        # Falses' cases 
        elif enableCh == [True, True, False, False]:
            self.axes.plot(self.timescale[0:ts],self.channelA1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts],self.channelA2[0:ts], color='k')
        elif enableCh == [True, False, False, True]:
            self.axes.plot(self.timescale[0:ts],self.channelA1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD2[0:ts], color='k')
        elif enableCh == [False, False, True, True]:
            self.axes.plot(self.timescale[0:ts], self.channelD1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD2[0:ts], color='k')
        ########################################################################################
        ## Falses' pairs separated cases
        elif enableCh == [True, False, True, False]:
            self.axes.plot(self.timescale[0:ts],self.channelA1[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD1[0:ts], color='k')
        elif enableCh == [False, True, False, True]:
            self.axes.plot(self.timescale[0:ts], self.channelA2[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD2[0:ts], color='k')
        elif enableCh == [False, True, True, False]:
            self.axes.plot(self.timescale[0:ts], self.channelA2[0:ts], color='k')
            self.axes.plot(self.timescale[0:ts], self.channelD1[0:ts], color='k')
        ########################################################################################
        # Falses' triples cases 
        elif enableCh == [False, False, False, True]: 
            self.axes.plot(self.timescale[0:ts],self.channelD2[0:ts], color='k')
        elif enableCh == [True, False, False, False]:
            self.axes.plot(self.timescale[0:ts],self.channelA1[0:ts], color='k')
        ########################################################################################
        # Remaining cases 
        # one True cases 
        elif enableCh == [False, False, False, True]:
            self.axes.plot(self.timescale[0:ts],self.channelD2[0:ts], color='k')
        elif enableCh == [False, False, True, False]:
            self.axes.plot(self.timescale[0:ts],self.channelD1[0:ts], color='k')
        elif enableCh == [False, True, False, False]:
            self.axes.plot(self.timescale[0:ts],self.channelA2[0:ts], color='k')
        elif enableCh == [True, False, False, False]:
            self.axes.plot(self.timescale[0:ts],self.channelA1[0:ts], color='k')
        else:
            pass
        ########################################################################################
        
        
        showDivScales(self,showScale(ch1),showScale(ch2), showScale(ch3), showScale(ch4), 0.68*xlim[1], timeScaleFactor(time))
        
        self.axes.xaxis.set_ticks(self.xticks)
        self.axes.yaxis.set_ticks(self.yticks)
        self.axes.set_xlim(xlim)
        self.axes.set_ylim([0.0, 3.0])
        #hide ticks labels 
        self.axes.set_xticklabels([])
        self.axes.set_yticklabels([])
        
        self.axes.grid(b=True,which='major',color='k',linestyle='-')
        self.axes.minorticks_on()
        self.axes.grid(b=True,which='minor',linestyle='--')
        
        self.canvas.draw() #draw

class textBox(QMainWindow):

    def __init__(self,mainWindow):
        super(textBox,self).__init__()
        self.main = mainWindow
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.title = 'Save Plot'
        self.left = 500
        self.top = 500
        self.width = 250
        self.height = 150
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)  
        
        # Create label
        self.text = QLabel("Enter file name: ", self)
        self.text.move(20,20)
    
        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 50)
        self.textbox.resize(200,20)
 
        # Create a button in the window
        self.button = QPushButton('Save', self)
        self.button.move(85,90)
        self.button.resize(80,30)
        self.button.clicked.connect(self.saveFile)
 
    
        self.show()
    
    def saveFile(self):
        self.main.canvas.fig.savefig(self.textbox.text() + '.png')
        self.close()
    

class Window(QMainWindow): 
    def __init__(self):
        super().__init__()

        #Status bar 
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.file_menu.addAction('&Save As', self.fileSave,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.menuBar().addMenu(self.file_menu)
        #Help option
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        #create canvas object 
        self.canvas = MplCanvas(self)

        #timer configuration for refreshing graph
        self.timer = None


        self.enabledChannels = [False for i in range(4)]

        #window config
        self.title = "Demoqe Project"
        self.top = 100
        self.left = 100
        self.width = 1000 
        self.height = 600 
        
        #push button config 
        button = QPushButton("Start", self) 
        button.move(790,350)
        button.clicked.connect(self.__plot(0))

        #push button config 
        button = QPushButton("Stop", self) 
        button.move(790,400)
        button.clicked.connect(self.stop)


        self.setWindowIcon(QtGui.QIcon("icon.png"))
        
        #slider for analog channel 1
        self.text = QLabel("Channel 1", self)
        self.text.move(800,75)

        self.channelA1 = QSlider(Qt.Horizontal, self)
        self.channelA1.setGeometry(750,100,170,20)
        self.channelA1.setMinimum(0)
        self.channelA1.setMaximum(2)
        self.channelA1.setTickPosition(QSlider.TicksAbove)
        self.channelA1.setTickInterval(1)
        self.channelA1.valueChanged.connect(self.sliderChangedValue)

        self.chA1checkBox = QCheckBox("",self)
        self.chA1checkBox.stateChanged.connect(self.enableChannel(self.chA1checkBox,0))
        self.chA1checkBox.move(950,92)
        self.chA1checkBox.resize(40,40) 

        #slider for analog channel 2
        self.text = QLabel("Channel 2", self)
        self.text.move(800,125)

        self.channelA2 = QSlider(Qt.Horizontal, self)
        self.channelA2.setGeometry(750,150,170,20)
        self.channelA2.setMinimum(0)
        self.channelA2.setMaximum(2)
        self.channelA2.setTickPosition(QSlider.TicksAbove)
        self.channelA2.setTickInterval(1)
        self.channelA2.valueChanged.connect(self.sliderChangedValue)

        self.chA2checkBox = QCheckBox("",self)
        self.chA2checkBox.stateChanged.connect(self.enableChannel(self.chA2checkBox,1))
        self.chA2checkBox.move(950,142)
        self.chA2checkBox.resize(40,40) 

        #slider for digital channel 1  
        self.text = QLabel("Channel 3", self)
        self.text.move(800,175)

        self.channelD1 = QSlider(Qt.Horizontal, self)
        self.channelD1.setGeometry(750,200,170,20)
        self.channelD1.setMinimum(0)
        self.channelD1.setMaximum(2)
        self.channelD1.setTickPosition(QSlider.TicksAbove)
        self.channelD1.setTickInterval(1)
        self.channelD1.valueChanged.connect(self.sliderChangedValue)

        self.chD1checkBox = QCheckBox("",self)
        self.chD1checkBox.stateChanged.connect(self.enableChannel(self.chD1checkBox,2))
        self.chD1checkBox.move(950,192)
        self.chD1checkBox.resize(40,40) 

        #slider digital channel 2 
        self.text = QLabel("Channel 4", self)
        self.text.move(800,225)

        self.channelD2 = QSlider(Qt.Horizontal, self)
        self.channelD2.setGeometry(750,250,170,20)
        self.channelD2.setMinimum(0)
        self.channelD2.setMaximum(2)
        self.channelD2.setTickPosition(QSlider.TicksAbove)
        self.channelD2.setTickInterval(1)
        self.channelD2.valueChanged.connect(self.sliderChangedValue)

        self.chD2checkBox = QCheckBox("",self)
        self.chD2checkBox.stateChanged.connect(self.enableChannel(self.chD2checkBox,3))
        self.chD2checkBox.move(950,242)
        self.chD2checkBox.resize(40,40) 

        #time per division slider 
        self.text = QLabel("Time Division", self)
        self.text.move(800,275)

        self.time = QSlider(Qt.Horizontal, self)
        self.time.setGeometry(750,300,170,20)
        self.time.setMinimum(0)
        self.time.setMaximum(2)
        self.time.setTickPosition(QSlider.TicksAbove)
        self.time.setTickInterval(1)
        self.time.valueChanged.connect(self.sliderChangedValue)

        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.title) #show windows title
        self.setGeometry(self.top, self.left, self.width, self.height) #set window geometry
        self.show() #show all above

    def fileQuit(self): 
        self.close() #exit application
    
    def fileSave(self):
        self.newTb = textBox(self)
        self.newTb.show()
        
    def sliderChangedValue(self):
        channelA1 = self.channelA1.value()
        channelA2 = self.channelA2.value()
        channelD1 = self.channelD1.value()
        channelD2 = self.channelD2.value()
        time      = self.time.value()
        self.plot(self.enabledChannels,channelA1,channelA2,channelD1,channelD2,time) 

    def enableChannel(self,channelObj,channel):
        
        """ Closure function for __enableChannel

            :returns:
                calls __enableChannel which calls plot with given parameters
        """

        def __enableChannel():
            channelA1 = self.channelA1.value()
            channelA2 = self.channelA2.value()
            channelD1 = self.channelD1.value()
            channelD2 = self.channelD2.value()
            time      = self.time.value()
            self.enabledChannels[channel] = channelObj.isChecked()       
            self.plot(self.enabledChannels, channelA1, channelA2, channelD1, channelD2)
        
        return __enableChannel
        
    
    

    def __plot(self,option=1):
        
        """ Closure function for ___plot
            :returns:
                A function, __plot which calls plot
        """

        def ___plot():
            if option == 0:
                channelA1 = self.channelA1.value()
                channelA2 = self.channelA2.value()
                channelD1 = self.channelD1.value()
                channelD2 = self.channelD2.value()
                time      = self.time.value()
                self.plot(self.enabledChannels,channelA1,channelA2,channelD1,channelD2,time)

        return ___plot


    def plot(self,enabledChannels=[False for i in range(4)], chA1=0, chA2=0, chD1=0, chD2=0, time=0):
        
        """ 
            Sets timer and calls canvas plot internal function

        """
        
        if self.timer: #if timer is running stop and restart a new one
            self.timer.stop()
            self.timer.deleteLater()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.canvas.plot(enabledChannels, chA1,chA2,chD1,chD2,time))
        self.timer.start(2.5) 
        
        """
            As 60Hz, indicates a 1/60 s or 16.6ms refreshing time. 
            As we are partly refresshing the graph. Only 15% 
            we shall refresh every 2.5ms 

        """

    def stop(self):
        self.timer.stop() #kill timer
        

        


    
#Run GUI 

App = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(App.exec())
