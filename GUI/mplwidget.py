from PyQt5 import QtWidgets

import matplotlib
matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

#from matplotlib import pyplot as plt

# Ensure using PyQt5 backend
#matplotlib.use('QT5Agg')

# Matplotlib canvas class to create figure
class MplCanvas(FigureCanvas):
    def __init__(self):
        
        self.fig = Figure()        
#        self.ax = self.fig.add_subplot(111) 
        
#        self.axs = self.fig.subplots(nx, ny) 
        
#        self.fig, self.axs = plt.subplots(2, 2)
        FigureCanvas.__init__(self,self.fig)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
#        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        #FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        FigureCanvas.updateGeometry(self)
#        self.toolbar = NavigationToolbar(self, self.fig)
        
#        self.fig, self.axs = plt.subplots(2, 2)
#        FigureCanvas.__init__(self,self.fig)
#        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
#        FigureCanvas.updateGeometry(self)

        
        
# Matplotlib widget
class mplwidget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        
        self.canvas = MplCanvas()
        self.toolbar = NavigationToolbar(self.canvas, self)
#        self.vbl = QtWidgets.QVBoxLayout()  
        self.vbl = QtWidgets.QGridLayout()  
        self.vbl.addWidget(self.canvas)
        self.vbl.addWidget(self.toolbar)
        self.setLayout(self.vbl)    




# import matplotlib # Make sure that we are using QT5 matplotlib.use('Qt5Agg')
# import matplotlib.pyplot as plt
# from PyQt5 import QtWidgets
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
 
# class ScrollableWindow(QtWidgets.QMainWindow):
#     def __init__(self, fig):
#         self.qapp = QtWidgets.QApplication([])
#         QtWidgets.QMainWindow.__init__(self)
#         self.widget = QtWidgets.QWidget()
#         self.setCentralWidget(self.widget)
#         self.widget.setLayout(QtWidgets.QVBoxLayout())
#         self.widget.layout().setContentsMargins(0,0,0,0)
#         self.widget.layout().setSpacing(0)
#         self.fig = fig
#         self.canvas = FigureCanvas(self.fig)
#         self.canvas.draw()
#         self.scroll = QtWidgets.QScrollArea(self.widget)
#         self.scroll.setWidget(self.canvas) 
#         self.nav = NavigationToolbar(self.canvas, self.widget) 
#         self.widget.layout().addWidget(self.nav) 
#         self.widget.layout().addWidget(self.scroll) 
#         self.show() exit(self.qapp.exec_()) # create a figure and some subplots
#         fig, axes = plt.subplots(ncols=4, nrows=5, figsize=(16,16))
#         for ax in axes.flatten(): ax.plot([2,3,5,1]) # pass the figure to the custom window
#         a = ScrollableWindow(fig) 


# =============================================================================
# PYQT5 Example
# =============================================================================
## Imports
#from PyQt5 import QtWidgets
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
#import matplotlib
#
## Ensure using PyQt5 backend
#matplotlib.use('QT5Agg')
#
## Matplotlib canvas class to create figure
#class MplCanvas(Canvas):
#    def __init__(self):
#        self.fig = Figure()
#        self.ax = self.fig.add_subplot(111)
#        Canvas.__init__(self, self.fig)
#        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
#        Canvas.updateGeometry(self)
#
## Matplotlib widget
#class MplWidget(QtWidgets.QWidget):
#    def __init__(self, parent=None):
#        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
#        self.canvas = MplCanvas()                  # Create canvas object
#        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
#        self.vbl.addWidget(self.canvas)
#        self.setLayout(self.vbl)

# =============================================================================
# PYQT4 Example
# =============================================================================

#from PyQt4 import QtGui
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
###from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
##from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
#from matplotlib.figure import Figure
#
#
#
#
##This is the class that represents the Matplotlib Figure for the Qt backend
#class MplCanvas(FigureCanvas):
#    def __init__(self):
#        
#        self.fig = Figure()        
#        self.ax = self.fig.add_subplot(111)        
#        FigureCanvas.__init__(self,self.fig)
##        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
#        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
#        #FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
#        FigureCanvas.updateGeometry(self)
#        
#        
#        #self.toolbar = NavigationToolbar(self, self.fig)
#
#
##class MplWidget(QtGui.QWidget):
#class MplWidget(QtGui.QWidget):
#    def __init__(self, parent = None):
#        QtGui.QWidget.__init__(self, parent)
#        
#        self.canvas = MplCanvas()
##        self.toolbar = NavigationToolbar(self.canvas, self)
##        self.vbl = QtGui.QVBoxLayout()  
#        self.vbl = QtGui.QGridLayout()  
#        self.vbl.addWidget(self.canvas)
##        self.vbl.addWidget(self.toolbar)
#        self.setLayout(self.vbl)
#        
    
