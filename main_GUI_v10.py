# -*- coding: utf-8 -*-
"""
Created on Tue Feb 04 18:04:57 2020

@author: pc
"""

#pyinstaller --onefile main_GUI_v4.py

# Import: Qt & GUI libraries
from __future__ import with_statement
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal

#from PyQt5 import QtCore, QtGui, QtNetwork

# Import: User Interface Forms: MainWindow & PopUpDialog
# We import the main window designed with Qt Designer;
# the name of the main window in Designer is MainWindow and
# so pyuic4 creates a class called Ui_MainWindow that
# we can now import to have access to the main window object
from GUI.qt_mainwindow import Ui_MainWindow 
from GUI.qt_secondmainwindow import Ui_SecondMainWindow

from ParallelComputing.WorkManager import parallelComputing, plot_ComputingPerformance


#MultiThreading
import multiprocessing
from multiprocessing import freeze_support

#Libraries: Parallel Computing
import concurrent.futures

#Maths Libraries
import numpy as np
#import pandas as pd

#Image Libraries
#import h5py
#import cv2
#from skimage import exposure
#import skimage

#Ploting Libraries
#from matplotlib import pyplot as plt
#import matplotlib.cm as cm
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

#from io import BytesIO
#from PIL import Image

#operative Systems Libraries       
import os
import sys

#Path Handeling
from pathlib import Path
import shutil
#import fnmatch

#Time
import time 

import json 


#Custom:
from IO.Image.ImageReader import read_imageMetada, read_ImageStack
from IO.Image.ImageWriter import save_2Dimage
from DataStructure.MuViSPIM import get_MatrixPaths
from DataStructure.Parser import parse_ScanMetada
from DataStructure.MuViSPIM import get_MatrixLayout
from DataConvertion.StructureConverter import convert_DataStructure
from DataStructure.TeraStitcher import (create_TeraStitcherFolderNames,
                                        create_TeraStitcherFolderStructure, 
                                        get_TeraStitcher_FolderPaths,
                                        get_TeraStitcher_FilePaths,
                                        ) 
from ImageProcessing.ImageMerger import (concatenate_imgScan,
                                         plot_imgConcatenated)

from DataStructure import MuViSPIM
from DataStructure import TeraStitcher
from IO.Files.FileManager import createFolder, removeFolder
from DataConvertion.UnChunkConverter import convert_scanHDF5toUnchunked            
from Plotting.Plotter import save_Figure


my_path = os.path.dirname(sys.argv[0])
graph_dpi = 300


#CAUTION:
# For creating a .exe comment matplotlib
#from matplotlib import pyplot as plt
# import matplotlib.cm as cm
#import matplotlib.patches as patches
import matplotlib
import matplotlib.cm as cm 
matplotlib.use("Qt5Agg")


     
# We now define a class to merge the UI we have designed (with the Qt Designer)
# with the code to develop the application

# Note: setupUi() is a method of Ui_MainWindow, created by pyuic4 at conversion time.
# It is used to create the UI. The parameter is the widget in which the user interface is created.
      
#class Form_MainWindow(QtGui.QMainWindow, Ui_MainWindow):
#    def __init__(self,parent=None):
#        super(Form_MainWindow, self).__init__(parent)
#        self.setupUi(self)
class AnotherWindow(QtWidgets.QMainWindow): 
    def __init__(self): 
        super(AnotherWindow, self).__init__()     
        self.ui = Ui_SecondMainWindow()        
        self.ui.setupUi(self)
        
        #Title
        self.setWindowTitle('Visualize Data') 



class mywindow(QtWidgets.QMainWindow): 
    def __init__(self): 
        super(mywindow, self).__init__()     
        self.ui = Ui_MainWindow()        
        self.ui.setupUi(self)
        
        #Title
        self.setWindowTitle('Data Structure Converter') 
        
        
        self.PopUpWindow = None  # No external window yet.

        #Connection: Paths
        self.ui.pushButton_OpenFile.clicked.connect(self.event_openFile) 
        self.ui.pushButton_selectFolder_toSave.clicked.connect(self.event_selectSavingFolder)
        
        #Connection: Select with the mouse cursos the scan metadata       
        self.ui.lineEdit_File.selectionChanged.connect(self.event_selectionChangedFile)
        self.ui.lineEdit_Folder.selectionChanged.connect(self.event_selectionChangedFolder)
        
        #Connection: Machine Selection
        self.ui.comboBox_Machine.activated.connect(self.event_selectMachine)
        
        #Connection: Settings
        self.ui.pushButton_Save.clicked.connect(self.event_saveUserSettings)
        self.ui.pushButton_SelectSubset.clicked.connect(self.event_saveScanSubset) 
        self.ui.pushButton_check_scan_dxdy.clicked.connect(self.event_check_scan_dxdy) 
        
        #Connection: Actions
        self.ui.pushButton_convert_toPseudoStitched.clicked.connect(self.event_convert_toPseudoStitched)        
        self.ui.pushButton_plot_PseudoStitchedImage.clicked.connect(self.event_plotPseudoStitched)        
        self.ui.pushButton_convert_toUnChunkedHDF5.clicked.connect(self.event_convert_toUnChunked) 
        self.ui.pushButton_convert_toTeraStitcher.clicked.connect(self.event_convert_toTeraStitcher) 
        
        self.ui.pushButton_test.clicked.connect(self.event_test)        


        
        #ComboBox Machine
        self.ui.comboBox_Machine.addItem("MuVi-SPIM")
        self.ui.comboBox_Machine.addItem("LCS-SPIM")
        self.ui.comboBox_Machine.addItem("OPTi-SPIM")
        self.ui.comboBox_Machine.addItem("Custom")
        
         
        #Initialization: ScanMetada
        self.ui.radioButton_Extension.setChecked(True)
        self.ui.lineEdit_scanOverlap.setText(str(15))
        self.ui.lineEdit_cameraPixelSize.setText(str(6.5))
        self.ui.lineEdit_opticalMagnification.setText(str(15))
        self.ui.lineEdit_scan_dx.setText(str(1))
        self.ui.lineEdit_scan_dy.setText(str(1))
        self.set_MachineSettings()
        

        
        
        #Initialization: ComputingSettings
        self.ui.radioButton_Parallel.setChecked(True)
        
        #Enable/Disable
        self.ui.pushButton_plot_PseudoStitchedImage.setEnabled(False)

        
        #Create Results Folder
        rootPath = Path.cwd()
        folderName = "Results"
        pathFolder_Results = Path.joinpath(rootPath, folderName)
        createFolder(str(pathFolder_Results), remove=False)
        
        #GUI Global Variables
        self.pathFile_In  = None          
        self.pathRoot_Out = str(pathFolder_Results)
        self.pathFile_zSlice = None
        self.n = 0
        
        # # Bypass
        # pathFile_In = r'F:\Arias\BrainScans\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1900_13678_4_4x_full\2021-10-22_092839\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
        # pathFile_In  = str(Path(pathFile_In))
        # self.set_pathFile_In(pathFile_In)

        # Check CPU Resources
        try:
            nCPU_Processes = multiprocessing.cpu_count()
            self.ui.label_nProcess_Max.setText(str(nCPU_Processes))
        except:
            print("An exception occurred")
            nCPU_Processes = 1
        
        nProcesses = int(np.ceil(0.4*nCPU_Processes))
        nProcesses = int(4)
        nThreads = int(1)
        self.ui.lineEdit_nProcesses.setText(str(nProcesses))
        self.ui.lineEdit_nThreads.setText(str(nThreads))

       

            
# =============================================================================
# Events Handlers
# =============================================================================

    #Events Handlers           
    def event_openFile(self): 
        print ('')
        print('Openning a file...')
        pathFile_In, selectedFilter = QtWidgets.QFileDialog.getOpenFileName(self, 'Select an Image File')
        pathFile_In  = Path(pathFile_In)
        myFileName   = pathFile_In.name
        myFolderName = pathFile_In.parent.name  
        
        #Display the FolderName and the FileName in the GUI to Parse ScanMetaData
        self.set_FolderAndFileName(str(myFolderName), str(myFileName))
        self.set_pathFile_In(str(pathFile_In))
        

        

    def event_selectSavingFolder(self):
        #Get Current Saving Folder to copy in the new one the settings json file 
        pathRoot_Out = self.get_pathRoot_Out()
        rootPath = Path(pathRoot_Out)
        folderName = "Settings"
        fileName   = "GUI_Settings.json" 
        pathFile   = Path.joinpath(rootPath, folderName, fileName)   
        
        #Load Json
        with open(pathFile, "r") as read_file: 
            data = json.load(read_file)
        
        # Selecting the new Saving Folder
        print()
        print('Selecting a folder to save the convertion...')
        pathRoot_Out = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a Root Directory to save the convertion')
        pathRoot_Out = str(Path(pathRoot_Out))         
        print('pathRoot_Out:', pathRoot_Out)        
        self.set_pathRoot_Out(pathRoot_Out)
        
        #Create the new SavingFolder
        rootPath = Path(pathRoot_Out)
        pathFolder   = Path.joinpath(rootPath, folderName)
        createFolder(str(pathFolder), remove=False)
        pathFile   = Path.joinpath(rootPath, folderName, fileName) 
        
        #Save Json
        with open(pathFile, "w") as write_file: 
             # json.dump(data, write_file)
             json.dump(data, write_file, indent=1, separators=(", ", ": "), sort_keys=False)

    def event_convert_toPseudoStitched(self):
        self.convert_toPseudoStitched()
        
    def event_convert_toUnChunked(self):
        self.convert_toUnChunked()
        
    def event_convert_toTeraStitcher(self):        
        self.convert_toTeraStitcher()        
        
    def event_selectionChangedFolder(self):
        print('')
        print('lineEdit_SelectionChanged-Start--------------')
        if self.ui.lineEdit_Folder.hasSelectedText():
            myRoot = 'Folder'
            self.get_SelectedText(myRoot)                       
        print('lineEdit_SelectionChanged-End------------') 
        

    def event_selectionChangedFile(self):
        print('')
        print('lineEdit_SelectionChanged-Start--------------')
        if self.ui.lineEdit_File.hasSelectedText():
            myRoot = 'File'
            self.get_SelectedText(myRoot)                       
        print('lineEdit_SelectionChanged-End------------' )

    def get_SelectedText(self, myRoot):
        print ('get_SelectedText-Start')
        print (myRoot)
        if myRoot=='File':
            p = self.ui.lineEdit_File        
        if myRoot=='Folder':
            p = self.ui.lineEdit_Folder
        
        if self.ui.radioButton_Extension.isChecked():
            myText = myRoot + '_' + str(p.selectionStart()) + '_'  + p.selectedText() 
            self.ui.label_Extension.setText(myText)

        if self.ui.radioButton_Channel.isChecked():
            myText = myRoot + '_' + str(p.selectionStart()) + '_'  + p.selectedText() 
            self.ui.label_Channel.setText(myText)
            
        if self.ui.radioButton_X.isChecked():
            myText = myRoot + '_' + str(p.selectionStart()) + '_'  + p.selectedText() 
            self.ui.label_X.setText(myText)
            
        if self.ui.radioButton_Y.isChecked():
            myText = myRoot + '_' + str(p.selectionStart()) + '_'  + p.selectedText() 
            self.ui.label_Y.setText(myText)
         
        if self.ui.radioButton_Z.isChecked():
            myText = myRoot + '_' + str(p.selectionStart()) + '_'  + p.selectedText() 
            self.ui.label_Z.setText(myText)           

        print ('get_SelectedText-End')
        
    def event_selectMachine(self):
        print()
        print("Event SelectMachine...")
        self.set_MachineSettings()

    def set_MachineSettings(self):
        print()
        print("Selected Machine is...")
        machine = self.ui.comboBox_Machine.currentText()
        print(machine)

        if machine=="MuVi-SPIM":          
            self.ui.radioButton_ChangeX_to_Y.setChecked(True)
            self.ui.radioButton_ChangeY_to_X.setChecked(True)
            self.ui.radioButton_ChangeZ_to_Z.setChecked(True)
            self.ui.radioButton_depthFormat_Stack.setChecked(True)
            self.ui.radioButton_ScanByRows.setChecked(True)  
            self.ui.checkBox_FlipX.setChecked(False) 
            self.ui.checkBox_FlipY.setChecked(False) 
            self.ui.checkBox_FlipZ.setChecked(False)          
            
            #Enable/Disable
            self.ui.radioButton_Z.setEnabled(False)
            self.ui.checkBox_FlipZ.setEnabled(False)
            
            ending = "File_0_Cam_Left_00000.lux.h5"
            channel = "Folder_16_channel_0"
            scanX = "Folder_9_00" 
            scanY = "Folder_13_00" 
            scanZ = '_'
            xyz_scan = [scanX, scanY, scanZ]
            self.set_ScanMetada(ending, channel, xyz_scan)
            
        elif machine=="LCS-SPIM":
            self.ui.radioButton_ChangeX_to_Y.setChecked(True)
            self.ui.radioButton_ChangeY_to_X.setChecked(True)
            self.ui.radioButton_ChangeZ_to_Z.setChecked(True)
            self.ui.radioButton_depthFormat_Stack.setChecked(True)            
            self.ui.radioButton_ScanByRows.setChecked(True)
            self.ui.checkBox_FlipX.setChecked(False) 
            self.ui.checkBox_FlipY.setChecked(True) 
            self.ui.checkBox_FlipZ.setChecked(False) 
            self.ui.checkBox_FlipZ.setEnabled(False)
            
            #Enable/Disable
            self.ui.radioButton_Z.setEnabled(False)
            self.ui.checkBox_FlipZ.setEnabled(False)
            
            ending = "File_0_Cam_Bottom_00000.lux.h5"
            channel = "Folder_16_channel_0"
            scanX = "Folder_9_00" 
            scanY = "Folder_13_00" 
            scanZ = '_'
            xyz_scan = [scanX, scanY, scanZ]
            self.set_ScanMetada(ending, channel, xyz_scan)

        elif machine=="OPTi-SPIM":
            self.ui.radioButton_ChangeX_to_Y.setChecked(True)
            self.ui.radioButton_ChangeY_to_X.setChecked(True)
            self.ui.radioButton_ChangeZ_to_Z.setChecked(True)
            self.ui.radioButton_depthFormat_Slices.setChecked(True)
            self.ui.radioButton_ScanByRows.setChecked(True)
            self.ui.checkBox_FlipX.setChecked(False) 
            self.ui.checkBox_FlipY.setChecked(False) 
            self.ui.checkBox_FlipZ.setChecked(False) 

            #Enable/Disable
            self.ui.radioButton_Z.setEnabled(True)
            self.ui.checkBox_FlipZ.setEnabled(True)
            
            ending = "pending to implement"
            channel = "pending to implement"
            scanX = "pending to implement" 
            scanY = "pending to implement" 
            scanZ = 'pending to implement'
            xyz_scan = [scanX, scanY, scanZ]
            self.set_ScanMetada(ending, channel, xyz_scan)
            
        elif machine=="Custom":
            self.ui.radioButton_ChangeX_to_X.setChecked(True)
            self.ui.radioButton_ChangeY_to_Y.setChecked(True)
            self.ui.radioButton_ChangeZ_to_Z.setChecked(True)
            self.ui.radioButton_depthFormat_Slices.setChecked(True)
            self.ui.radioButton_ScanByRows.setChecked(True)
            self.ui.checkBox_FlipX.setChecked(False) 
            self.ui.checkBox_FlipY.setChecked(False) 
            self.ui.checkBox_FlipZ.setChecked(False) 
 
            #Enable/Disable
            self.ui.radioButton_Z.setEnabled(True)
            self.ui.checkBox_FlipZ.setEnabled(True)
            
            ending = "select the text ending"
            channel = "select the text channel"
            scanX = "select the text scanX"
            scanY = "select the text scanY" 
            scanZ = "select the text scanZ"
            xyz_scan = [scanX, scanY, scanZ]
            self.set_ScanMetada(ending, channel, xyz_scan)           
        else:
            print()
            print("Selected Machine is unkown")        
        
    
    
    
    def event_saveUserSettings(self): 
        print()
        print ('event_saveUserSettings-Start')
        
        
        # =============================================================================
        #   Path Data
        # =============================================================================
        pathFile_In = str(Path(self.get_pathFile_In() )) 
        
        #???? Bypassing
        # pathFile_In = r"F:\Arias\Brains\SPIM_LCS\LCS_SPIM_Scans\Ref_1800_34583_SPIM_LCS_Line_ACF_Scan\2021-01-25_143342\raw\stack_0-x00-y00_channel_0_obj_bottom\Cam_Bottom_00000.lux.h5"
        # pathFile_In = r"F:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5"
        # pathFile_In = r'F:\Arias\ProcessedBrains\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan_UnChunked\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
        # pathFile_In = r'G:\Musoles_Juanlu\181_APP\Real_18x6x2\2021-02-03_165039\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
        # pathFile_In = r'F:\Arias\ProcessedBrains\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan_UnChunked\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
        # pathFile_In = r'F:\Arias\ProcessedBrains\Ref_181_APP_UnChunked\Real_18x6x2_UnChunked_bk\2021-02-03_165039\raw\stack_0-x00-y00_channel_1_obj_left\Cam_Left_00000.lux.h5'
        # #9,3, chanel_1
        # pathFile_In = r'F:\Arias\BrainScans\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1900_13678_4_4x_full\2021-10-22_092839\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
        # pathFile_In  = str(Path(pathFile_In))
        # self.set_pathFile_In(pathFile_In)
        
        
        
        
        #
        pathRaw_In = str(Path(pathFile_In).parent.parent) 
        pathRoot_Out = self.get_pathRoot_Out() 
        
        #Save Paths
        pathRaw_In = str(Path(pathFile_In).parent.parent)
        pathRoot_In = str(Path(pathFile_In).parent.parent.parent.parent)  

        # =============================================================================
        #   Get GUI Data
        # =============================================================================
        [ending_txt, channel_txt, xyz_scan_txt] = self.get_ScanMetada() 
        xyz_flip = self.get_xyzFlips()

        is_xChange = self.get_xChangeCoords() 
        is_yChange = self.get_yChangeCoords() 
        is_zChange = self.get_zChangeCoords() 
        
        # scanningBy = self.get_ScanbyRowsOrColumns
        # depthFormat = self.get_imageStackorSlices()
        
        #Image Processing
        imgProcessing = str(self.ui.comboBox_16to8bit.currentText())
        
        #Parallel Computing
        isParallel = self.ui.radioButton_Parallel.isChecked()   
        nProcesses  = int(self.ui.lineEdit_nProcesses.text())      
        nThreads    = int(self.ui.lineEdit_nThreads.text())
        
        # =============================================================================
        #   Change the xyz Axis
        # =============================================================================
        xyz_scan_txt = np.asarray(xyz_scan_txt)
        xyz_flip = np.asarray(xyz_flip)  
        
        xyz_order = [np.where(is_xChange)[0][0], np.where(is_yChange)[0][0], np.where(is_zChange)[0][0]]
        
        xyz_scan_txt = xyz_scan_txt[xyz_order]
        xyz_flip = xyz_flip[xyz_order]
        


        # =============================================================================
        #  Curate the GUI Metadata       
        # =============================================================================
        #Parse Data
        dataStructure = {"ending": ending_txt,
                          "channel": channel_txt,
                          "tileX": xyz_scan_txt[0],
                          "tileY": xyz_scan_txt[1],
                          "sliceZ": xyz_scan_txt[2]} 
        parseStructure = parse_ScanMetada(dataStructure)
        ending = parseStructure["parsed_ending"]
        channel = parseStructure["parsed_channel"]
        xyz_index = parseStructure["parsed_coord"]
        # [xyz_index, channel, ending] = parse_ScanMetada(xyz_scan_txt, channel_txt, ending_txt)
        
        #Scan MetaData
        Matrix_Paths = get_MatrixPaths(pathRaw_In, xyz_index, channel, ending, xyz_flip)
        [ny, nx] = Matrix_Paths.shape   
        
        #Image MetaData
        [img_nx, img_ny, img_nz, img_BitDepth, img_Format] = read_imageMetada(pathFile_In)
        nz = img_nz
        
        #Default Subset
        [x0, y0, z0] = [0, 0, 0]
        [dx, dy, dz] = [nx, ny, img_nz]
        xyz_Range = [x0, y0, z0, dx, dy, dz]
        
        #Scan Displacement
        cameraPixelSize = self.get_cameraPixelSize()
        opticalMagnification = self.get_opticalMagnification()
        scanOverlap = self.get_scanOverlap()    
        scan_dx, scan_dy = self.compute_scan_dxdy(cameraPixelSize, opticalMagnification, scanOverlap, img_nx, img_ny)

        # 754.347, 754.347
        scan_dx = self.get_scan_dx()
        scan_dy = self.get_scan_dy()


    
        # =============================================================================
        #         
        # =============================================================================
        # Create a Python Dictionary Object
        myDic = {
                  "pathFile_In":     str(pathFile_In),
                  "pathRaw_In":    str(pathRaw_In),
                  "pathRoot_In":    str(pathRoot_In),
                  "pathRooth_Out":   str(pathRoot_Out),
          
                  "xyz_index": list(xyz_index),
                  "channel": channel,
                  "ending":  ending,               
                  
                  "xyz_flip": [bool(xyz_flip[0]), bool(xyz_flip[1]), bool(xyz_flip[2])],
                  "xyz_Dim": list([nx, ny, nz]),
                  "xyz_Range": list([x0, y0, z0, dx, dy, dz]),
                  
                  "img_Dim": list([img_nx, img_ny, img_nz]),
                  "img_BitDepth": img_BitDepth,
                  "img_Format": img_Format,
                  
                  "cameraPixelSize": cameraPixelSize,
                  "opticalMagnification": opticalMagnification,
                  "scanOverlap": scanOverlap,
                  "scan_dx": scan_dx,
                  "scan_dy": scan_dy,
                  
                  "imgProcessing": imgProcessing,
                  "isParallel": isParallel,
                  "nProcesses": nProcesses,
                  "nThreads": nThreads,
                  }      
        
        #Set Path File to save the json
        rootPath = Path(pathRoot_Out)
        folderName = "Settings"
        fileName   = "GUI_Settings.json" 
        pathFolder = Path.joinpath(rootPath, folderName)
        createFolder(str(pathFolder), remove=False)
        pathFile   = Path.joinpath(rootPath, folderName, fileName)
        
        with open(pathFile, "w") as write_file: 
             # json.dump(myDic, write_file)
             json.dump(myDic, write_file, indent=1, separators=(", ", ": "), sort_keys=False)
    
        # =============================================================================
        #     
        # =============================================================================
        # Set GUI: Matrix Layout                 
        Matrix_LayOut = get_MatrixLayout(nx, ny, x0, y0, dx, dy)
        self.plot_ScanLayout(Matrix_LayOut)
        
        # Set GUI: Scan Subset
        self.set_ScanningLayoutSubset(xyz_Range)
        
        # Set GUI: Image MetadaData
        self.set_ImgMetada(img_nx, img_ny, img_nz, img_BitDepth, img_Format)
        
        # Set z-slice as the mid value
        zSlice = int(0.5*nz)
        self.set_zSlice(zSlice)
    
        # Set data
        self.set_ScanLayoutDimensions(nx, ny)
        self.ui.label_scan_dx.setText('{:0.2f}'.format(scan_dx))
        self.ui.label_scan_dy.setText('{:0.2f}'.format(scan_dy))
        


    def event_saveScanSubset(self):
        print()
        print("Saving desired scanSubset...")
        [nx, ny] = self.get_ScanLayoutDimensions()
        [x0, y0, z0, dx, dy, dz] = self.get_ScanningLayoutSubset() 
        
        Matrix_LayOut = get_MatrixLayout(nx, ny, x0, y0, dx, dy)
        self.plot_ScanLayout(Matrix_LayOut)   
        
        #Set Path File to save the json
        pathRoot_Out = self.get_pathRoot_Out()
        rootPath = Path(pathRoot_Out)
        folderName = "Settings"
        fileName   = "GUI_Settings.json" 
        pathFile   = Path.joinpath(rootPath, folderName, fileName)        
        
        #Load Json
        with open(pathFile, "r") as read_file: 
            data = json.load(read_file)
            
            #Modify Json
            data["xyz_Range"] = list([x0, y0, z0, dx, dy, dz])
            
            #Save Json
            with open(pathFile, "w") as write_file: 
                 # json.dump(data, write_file)
                 json.dump(data, write_file, indent=1, separators=(", ", ": "), sort_keys=False)

    def event_check_scan_dxdy(self):
        #Get Path
        pathFile_In = str(Path(self.get_pathFile_In() )) 
        
        #Image MetaData
        [img_nx, img_ny, img_nz, img_BitDepth, img_Format] = read_imageMetada(pathFile_In)
        nz = img_nz
        
        #Scan Displacement
        cameraPixelSize = self.get_cameraPixelSize()
        opticalMagnification = self.get_opticalMagnification()
        scanOverlap = self.get_scanOverlap()    
        scan_dx, scan_dy = self.compute_scan_dxdy(cameraPixelSize, opticalMagnification, scanOverlap, img_nx, img_ny)
        self.set_scan_dxdy(scan_dx, scan_dy)
        

        
    def plot_ScanLayout(self, M): 
        [ny, nx] = M.shape
#        ax = self.ui.plotWidget.canvas.ax
        fig = self.ui.plotWidget.canvas.fig
        fig.clf()
        ax = fig.subplots(1,1)
        ax.imshow(M, cmap = cm.Greys_r, vmin=0, vmax=2, interpolation='nearest')
        
        #Show the grids at the middle
        ax.set_xticks(np.arange(nx+1) - 0.5, minor='true')
        ax.set_yticks(np.arange(ny+1) - 0.5, minor='true')
        ax.grid(which='minor', color='r', linestyle='-', linewidth=2) 
        # We want to show all ticks...
        ax.set_xticks(np.arange(nx))
        ax.set_yticks(np.arange(ny))
        # ... and label them with the respective list entries
        ax.set_xticklabels(np.arange(nx))
        ax.set_yticklabels(np.arange(ny))
        #
        ax.xaxis.tick_top()
        self.ui.plotWidget.canvas.draw()
        
# =============================================================================
#     GUI internal Variables
# =============================================================================

    def get_pathFile_In(self):
        pathFile_In = self.pathFile_In
        return pathFile_In

    def set_pathFile_In(self, pathFile_In):
        self.pathFile_In = pathFile_In 
        
    def get_pathRoot_Out(self):
        pathRoot_Out = str(Path(self.pathRoot_Out))
        return pathRoot_Out

    def set_pathRoot_Out (self, pathRoot_Out):
        self.pathRoot_Out = pathRoot_Out      
        
# =============================================================================
#   Write/Read Data from the GUI    
# =============================================================================
    def get_ScanMetada(self):
        ending_text   = self.ui.label_Extension.text()
        channel_text  = self.ui.label_Channel.text()         
        scanX_text    = self.ui.label_X.text()
        scanY_text    = self.ui.label_Y.text()
        scanZ_text    = self.ui.label_Z.text()
        xyz_scan_text = [scanX_text, scanY_text, scanZ_text]
        return [ending_text, channel_text, xyz_scan_text]
     
    def set_ScanMetada(self, ending_text, channel_text, xyz_scan_text):
        [scanX_text, scanY_text, scanZ_text] = xyz_scan_text 
        self.ui.label_Extension.setText(str(ending_text))
        self.ui.label_Channel.setText(str(channel_text))
        self.ui.label_X.setText(str(scanX_text))
        self.ui.label_Y.setText(str(scanY_text))
        self.ui.label_Z.setText(str(scanZ_text))    
    
    
    def get_imageStackorSlices(self):
        depthFormat = None
        if  self.ui.radioButton_depthFormat_Slices.isChecked():
            depthFormat = 'ImageSequence'
        elif self.ui.radioButton_depthFormat_Stack.isChecked():
           depthFormat = 'ImageStack'
        return depthFormat
    
    def get_xChangeCoords(self):
        isXtoX = self.ui.radioButton_ChangeX_to_X.isChecked()
        isXtoY = self.ui.radioButton_ChangeX_to_Y.isChecked()
        isXtoZ = self.ui.radioButton_ChangeX_to_Z.isChecked()
        return [isXtoX, isXtoY, isXtoZ]
    
    def get_yChangeCoords(self):
        isYtoX = self.ui.radioButton_ChangeY_to_X.isChecked()
        isYtoY = self.ui.radioButton_ChangeY_to_Y.isChecked()
        isYtoZ = self.ui.radioButton_ChangeY_to_Z.isChecked()
        return [isYtoX, isYtoY, isYtoZ]    
   
    def get_zChangeCoords(self):
        isZtoX = self.ui.radioButton_ChangeZ_to_X.isChecked()
        isZtoY = self.ui.radioButton_ChangeZ_to_Y.isChecked()
        isZtoZ = self.ui.radioButton_ChangeZ_to_Z.isChecked()
        return [isZtoX, isZtoY, isZtoZ]    
    
    def get_xyzFlips(self):
        flipX = self.ui.checkBox_FlipX.isChecked()
        flipY = self.ui.checkBox_FlipY.isChecked()
        flipZ = self.ui.checkBox_FlipZ.isChecked()  
        return [flipX, flipY, flipZ]

    def get_ScanbyRowsOrColumns(self):
        scanningBy = None
        if self.ui.radioButton_ScanByRows.isChecked():
            scanningBy = 'Rows'
        elif self.ui.radioButton_ScanByColumns.isChecked():
            scanningBy = 'Columns'
        return scanningBy

    def get_cameraPixelSize(self):
        cameraPixelSize = float(self.ui.lineEdit_cameraPixelSize.text())
        return cameraPixelSize
    
    def get_opticalMagnification(self):
        opticalMagnification = float(self.ui.lineEdit_opticalMagnification.text())
        return opticalMagnification
    
    def get_scanOverlap(self):
        scanOverlap = float(self.ui.lineEdit_scanOverlap.text())
        return scanOverlap    

    def get_scan_dx(self):
        scan_dx = float(self.ui.lineEdit_scan_dx.text())
        return scan_dx  
    
    def get_scan_dy(self):
        scan_dy = float(self.ui.lineEdit_scan_dy.text())
        return scan_dy        
    
    def compute_scan_dxdy(self, cameraPixelSize, opticalMagnification, scanOverlap, img_nx, img_ny):
        scan_dx = (1-scanOverlap/100)*(cameraPixelSize*img_nx)/opticalMagnification
        scan_dy = (1-scanOverlap/100)*(cameraPixelSize*img_ny)/opticalMagnification
        return scan_dx, scan_dy    
        
    def set_scan_dxdy(self,scan_dx, scan_dy):
        self.ui.lineEdit_scan_dx.setText("{:.2f}".format(scan_dx))
        self.ui.lineEdit_scan_dy.setText("{:.2f}".format(scan_dy))
    
    def get_ScanLayoutDimensions(self):
        nx = int(self.ui.label_layout_nx.text())
        ny = int(self.ui.label_layout_ny.text())
        return nx, ny   
    
    def get_ScanningLayoutSubset(self):
        x0 = int(self.ui.lineEdit_SubSet_x0.text())
        y0 = int(self.ui.lineEdit_SubSet_y0.text())
        z0 = int(self.ui.lineEdit_SubSet_z0.text())
        
        dx = int(self.ui.lineEdit_SubSet_dx.text())
        dy = int(self.ui.lineEdit_SubSet_dy.text())
        dz = int(self.ui.lineEdit_SubSet_dz.text())
        
        return x0, y0, z0, dx, dy, dz 

    def get_ImgMetada(self):
        img_nx = int(self.ui.label_img_nx.text())
        img_ny = int(self.ui.label_img_ny.text())
        img_nz = int(self.ui.label_img_nz.text())
        img_BitDepth = self.ui.label_img_BitDepth.text()
        imgFormat = self.ui.label_imgFormat.text()
        return img_nx, img_ny, img_nz, img_BitDepth, imgFormat

    def get_ScanningBy(self):
        myStr = self.ui.label_ScanByRows.text()    
        return myStr

    def set_zSlice(self, zSlice):
        self.ui.lineEdit_zSlice.setText(str(zSlice)) 
        
    def get_zSlice(self):
        zSlice = int(self.ui.lineEdit_zSlice.text())
        return zSlice
          
    def set_ScanLayoutDimensions(self, nx, ny):
        self.ui.label_layout_nx.setText(str(nx))
        self.ui.label_layout_ny.setText(str(ny))
        
        
    def set_ScanningLayoutSubset(self, xyz_Range):
        [x0, y0, z0, dx, dy, dz] = xyz_Range
        self.ui.lineEdit_SubSet_x0.setText(str(x0))
        self.ui.lineEdit_SubSet_y0.setText(str(y0))
        self.ui.lineEdit_SubSet_z0.setText(str(z0))
        
        self.ui.lineEdit_SubSet_dx.setText(str(dx))
        self.ui.lineEdit_SubSet_dy.setText(str(dy))
        self.ui.lineEdit_SubSet_dz.setText(str(dz))
        
    def set_ScanningBy(self, myStr):
        self.ui.label_ScanByRows.setText(myStr)        
 
    def set_ImgMetada(self ,img_nx, img_ny, img_nz, img_BitDepth, imgFormat):
        self.ui.label_img_nx.setText(str(img_nx))
        self.ui.label_img_ny.setText(str(img_ny))
        self.ui.label_img_nz.setText(str(img_nz))
        self.ui.label_img_BitDepth.setText(str(img_BitDepth))
        self.ui.label_imgFormat.setText(str(imgFormat)) 
            
    def set_FolderAndFileName(self, myFolderName, myFileName):
        self.ui.lineEdit_Folder.setText(str(myFolderName))
        self.ui.lineEdit_File.setText(str(myFileName))
        

# =============================================================================
#   ACTIONS
# =============================================================================
        
    # =============================================================================
    #   1) Read images from SPIM format
    #   2) Image Procesing: 
    #   3) Save images following TeraStitcher Format         
    # =============================================================================  


    def convert_toPseudoStitched(self):
        print()
        print("pushButton_convert_toPseudoStitched...")
        
        #Enable
        self.ui.pushButton_plot_PseudoStitchedImage.setEnabled(False)
        
        #Set Path File to save the json
        pathRoot_Out = self.get_pathRoot_Out()
        rootPath = Path(pathRoot_Out)
        folderName = "Settings"
        fileName   = "GUI_Settings.json" 
        pathFile   = Path.joinpath(rootPath, folderName, fileName)        
        
        #Load Json
        with open(pathFile, "r") as read_file: 
            data = json.load(read_file)
       
        pathRaw_In = str(Path(data["pathRaw_In"])) 
        pathRoot_In = str(Path(data["pathRoot_In"])) 
        [x0, y0, z0, dx, dy, dz]  = data["xyz_Range"] 
        xyz_index = data["xyz_index"] 
        channel = data["channel"] 
        ending = data["ending"] 
        xyz_flip = data["xyz_flip"] 
        
        # pathRoot_Out = data["pathRoot_Out"] 
        
        scan_dx = data["scan_dx"]
        scan_dy = data["scan_dy"]
        
        zSlice = self.get_zSlice()

        isParallel = data["isParallel"]
        imgProcessing = data["imgProcessing"]
        nProcesses = data["nProcesses"]
        nThreads = data["nThreads"]
       
        #Only one slice
        xyz_Range = [x0, y0, zSlice, dx, dy, 1]
        
        #PathFolder zSlices
        pathRoot_Out = self.get_pathRoot_Out()
        pathRoot_Out = str(Path.joinpath(Path(pathRoot_Out), (Path(pathRoot_In).name + '_temp')))
        createFolder(pathRoot_Out, remove=True)        
        
        
        # Step 1: Assign function and args
        fn = self.do_LongTask
        args = [pathRoot_In, pathRaw_In, xyz_Range, xyz_index, channel, ending, xyz_flip, pathRoot_Out, scan_dx, scan_dy, imgProcessing, isParallel, nProcesses, nThreads]
        
        # Step 2: Create a QThread object
        self.thread = QThread()
        
        # Step 3: Create a worker object
        self.worker = Worker(fn, *args)
        
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Step 6: Connect singals 
        # self.worker.progress.connect(self.event_workerPseudoStitched_reaProgress)
        self.worker.results.connect(self.event_workerPseudoStitched_readResults)
        self.worker.finished.connect(self.event_workerPseudoStitched_finished)
        
        # Step 7: Start the thread
        self.thread.start()
        
        #See after processing
        
        
        
    def convert_toTeraStitcher(self):  
        
        #Get Path File to read the Settings json
        pathRoot_Out = self.get_pathRoot_Out()
        rootPath = Path(pathRoot_Out)
        folderName = "Settings"
        fileName   = "GUI_Settings.json" 
        pathFile   = Path.joinpath(rootPath, folderName, fileName)        
        
        #Load Json
        with open(pathFile, "r") as read_file: 
            data = json.load(read_file)
       
        pathRaw_In = str(Path(data["pathRaw_In"])) 
        pathRoot_In = str(Path(data["pathRoot_In"])) 

        xyz_Range  = data["xyz_Range"] 
        xyz_index = data["xyz_index"] 
        channel = data["channel"] 
        ending = data["ending"] 
        xyz_flip = data["xyz_flip"] 
        
        # pathRoot_Out = data["pathRoot_Out"] 
        
        scan_dx = data["scan_dx"]
        scan_dy = data["scan_dy"]
        
        isParallel = data["isParallel"]
        imgProcessing = data["imgProcessing"]
        nProcesses = data["nProcesses"]
        nThreads = data["nThreads"]
           
        
        # Saving Folder: TeraStitcherFormat
        pathRoot_Out = self.get_pathRoot_Out()
        pathRoot_Out = str(Path.joinpath(Path(pathRoot_Out), (Path(pathRoot_In).name + '_TeraStitcher')))
        createFolder(pathRoot_Out, remove=True) 
        
        # Step 1: Assign function and args
        fn = self.do_LongTask
        args = [pathRoot_In, pathRaw_In, xyz_Range, xyz_index, channel, ending, xyz_flip, pathRoot_Out, scan_dx, scan_dy, imgProcessing, isParallel, nProcesses, nThreads]    
        
        # Step 2: Create a QThread object
        self.thread = QThread()
        
        # Step 3: Create a worker object
        self.worker = Worker(fn, *args)
        
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Step 6: Connect singals 
        # self.worker.progress.connect(self.event_workerTeraStitcher_readProgress)
        # self.worker.results.connect(self.event_workerTeraStitcher_readResults)
        self.worker.finished.connect(self.event_workerTeraStitcher_finished)
        
        # Step 7: Start the thread
        self.thread.start()
        
        #See after processing
        
      
    def convert_toUnChunked(self):
        #Get Path File to read the Settings json
        pathRoot_Out = self.get_pathRoot_Out()
        rootPath = Path(pathRoot_Out)
        folderName = "Settings"
        fileName   = "GUI_Settings.json" 
        pathFile   = Path.joinpath(rootPath, folderName, fileName)        
        
        #Load Json
        with open(pathFile, "r") as read_file: 
            data = json.load(read_file)
       
        pathRoot_In = str(Path(data["pathRoot_In"]))
        pathRaw_In = str(Path(data["pathRaw_In"])) 
        
        xyz_Range  = data["xyz_Range"] 
        xyz_index = data["xyz_index"] 
        channel = data["channel"] 
        ending = data["ending"] 
        xyz_flip = data["xyz_flip"] 
        
        # pathRoot_Out = data["pathRoot_Out"] 
        
        # scan_dx = data["scan_dx"]
        # scan_dy = data["scan_dy"]
        
        isParallel = data["isParallel"]
        # imgProcessing = data["imgProcessing"]
        nProcesses = data["nProcesses"]
        nThreads = data["nThreads"]
      
        
        #Setting: Output Paths
        pathRoot_Out = str(Path.joinpath(Path(pathRoot_Out), (Path(pathRoot_In).name + '_UnChunked')))    
        removeFolder(pathRoot_Out)    
        pathRaw_Out = str(Path.joinpath(Path(pathRoot_Out), Path(pathRaw_In).parent.name, Path(pathRaw_In).name))

        
        # Step 1: Assign function and args
        fn = convert_scanHDF5toUnchunked
        isPlot = True
        args = [pathRoot_In, pathRaw_In, pathRoot_Out, pathRaw_Out,
                xyz_Range, xyz_index, channel, ending, xyz_flip,
                isParallel, nProcesses, nThreads, isPlot]    
        
        # Step 2: Create a QThread object
        self.thread = QThread()
        
        # Step 3: Create a worker object
        self.worker = Worker(fn, *args)
        
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Step 6: Connect singals 
        # self.worker.progress.connect(self.event_workerUnChunked_readProgress)
        self.worker.results.connect(self.event_workerUnChunked_readResults)
        self.worker.finished.connect(self.event_workerUnChunked_finished)
        
        # Step 7: Start the thread
        self.thread.start()
        
        #See after processing 
# =============================================================================
#         
# =============================================================================

        
    def event_plotPseudoStitched(self):
        print()
        print("Creating_PopUpWindow...")
        
        #Set Path File to save the json
        pathRoot_Out = self.get_pathRoot_Out()
        rootPath = Path(pathRoot_Out)
        folderName = "Settings"
        fileName   = "GUI_Settings.json" 
        pathFile   = Path.joinpath(rootPath, folderName, fileName)        
        
        #Load Json
        with open(pathFile, "r") as read_file: 
            data = json.load(read_file)
        
        [x0, y0, z0, dx, dy, dz] = data["xyz_Range"]
        [img_nx, img_ny, img_nz] = data["img_Dim"]
        scanOverlap = data["scanOverlap"]
        
        
        #Create: PopUp Window 
        self.show_new_window()

        #Once Created plot something        
        fig = self.PopUpWindow.ui.plotWidgetImg.canvas.fig
        fig.clf()
        axs = fig.subplots(1, 1)   
        
        #Read the Image
        pathFile_zSlice = str(Path(self.pathFile_zSlice))
        print()
        print(pathFile_zSlice)
        [img_zSlice, dt]  = read_ImageStack(pathFile_zSlice)  
        
        
        #Plot the image
        plot_imgConcatenated(axs, img_zSlice, dx, dy, img_nx, img_ny, scanOverlap)         
      
        self.PopUpWindow.ui.plotWidgetImg.canvas.draw()
        fig.tight_layout()        
        
        #Save MatplotImage 
        isMatPlotSaved = False
        if isMatPlotSaved==True:
            pathRoot_Out = Path(pathFile_zSlice)
            pathFolder = pathRoot_Out.parent 
            fileName = 'matPlot_' + ((pathRoot_Out).with_suffix('')).name
            createFolder(str(pathFolder), remove=False)        
            save_Figure(fig, pathFolder, fileName)

   
        print()
        print('Finish')

    def show_new_window(self):
        if self.PopUpWindow is None:
            self.PopUpWindow = AnotherWindow()
        self.PopUpWindow.show()       
# =============================================================================
#         
# =============================================================================

    def event_workerPseudoStitched_readResults(self, pathFile_zSlice):
        print()
        print('event_workerPseudoStitched_readResults....')
        print(pathFile_zSlice)
        pathFile_zSlice = Path(pathFile_zSlice)
        self.pathFile_zSlice = str(pathFile_zSlice)
        
    def event_workerPseudoStitched_finished(self):
        print()
        print('event_workerPseudoStitched_finished....')
        self.ui.pushButton_plot_PseudoStitchedImage.setEnabled(True)

    def event_workerTeraStitcher_readResults(self, res):
        print()
        print('event_workerTeraStitcher_readResults...')
        print(res)
        pass
        
    def event_workerTeraStitcher_finished(self):
        print()
        print('event_workerTeraStitcher_finished...')
        pass
    
    def event_workerUnChunked_readResults(self, res):
        print()
        print('event_workerUnChunked_readResults...')
        print(res)
        pass     
    
    def event_workerUnChunked_finished(self):
        print()
        print('event_workerUnChunked_finished...')
        pass   
           
# =============================================================================
# 
# =============================================================================
    def event_test(self):
        a, b = 1, 2
        args = [a, b]
        fn = self.sum
        # Step 2: Create a QThread object
        self.thread = QThread()
        
        # Step 3: Create a worker object
        self.worker = Worker(fn, *args)
        # self.worker = Worker(RootPath_In, xyz_Range, parse_Data, flipX, flipY, RootPath_Out, scan_dx, scan_dy, z0, imgOperation_16to8bit, isParallel, nProcesses, nThreads)

        
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Step 6: Connect singals    
        self.worker.finished.connect(self.event_Worker_finished)
        # self.worker.progress.connect(self.reportProgress)
        
        # Step 6: Start the thread
        self.thread.start()
        
    def sum(self, a, b):
        c = a + b
        return  c
# =============================================================================
#         
# =============================================================================
        
    def do_LongTask(self, pathRoot_In, pathRaw_In, xyz_Range, xyz_index, channel, ending, xyz_flip, pathRoot_Out, scan_dx, scan_dy, imgProcessing, isParallel, nProcesses, nThreads):
        filePath = None
        [x0, y0, z0, dx, dy, dz] = xyz_Range
    
        #Routine 1: Get Input DataStructure
        [xyMatrix_In, zVector_In] = MuViSPIM.get_DataStructure(pathRaw_In, xyz_Range, xyz_index, channel, ending, xyz_flip)
        
        print('zVector_In', zVector_In)
    
          
        #Routine 2: Get Output DataStructure
        [ny, nx] = xyMatrix_In.shape
        scan_dz = 2
        [xyMatrix_Out, zVector_Out] = TeraStitcher.get_DataStructure(pathRoot_Out, nx, ny, scan_dx, scan_dy, scan_dz, zVector_In)
       
 
        #Routine 3: Convert from Input to Output
        print('')
        print('Convert...') 
        print('Matrix Size:', xyMatrix_In.shape)
        print('Depth:', dz)
        print('isParallel:', isParallel)  
        print('nProcesses:', nProcesses)  
        print('Convertion:', imgProcessing) 
        # try:                     
        dt = convert_DataStructure(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation=imgProcessing, imgOutFormat='tiff3D', isParallel=isParallel, nProcesses=nProcesses, nThreads=nThreads)
        # except Exception as inst:
        #     print(type(inst))    # the exception instance
        #     print(inst.args)     # arguments stored in .args
        #     print(inst)
        print()   
        print('time=', dt)
        rt = dt/(xyMatrix_In.shape[0]*xyMatrix_In.shape[1]*dz)
        print('rate per image:', rt)
        
        # print(zVector_In)
        # print(zVector_Out)
        # print(np.asarray([zVector_Out[0]]))
        # jajaja
        
        if dz==1:    
            #Routine 4: Read TeraStitcher Structure to get FilePaths of images across XY and a single Z 
            print('')
            print ('Read TeraSticher Structure...')
            xyMatrix_FolderNames = get_TeraStitcher_FolderPaths(pathRoot_Out)
            [ny, nx] = xyMatrix_FolderNames.shape
            # zSlice = np.asarray([z0])
            zSlice = np.asarray([zVector_Out[0]])
            xyMatrix_FileNames = get_TeraStitcher_FilePaths(pathRoot_Out, ny, nx , zSlice)
            
            # print(xyMatrix_FileNames)
            
            #Routine 5: Concatenate the Images acrossXY plane        
            print('')
            print ('Read and Concatenate the Tiles...')
            [img_Concatenated, dt] = concatenate_imgScan(xyMatrix_FileNames, isParallel=True)
            print('time=', dt)            
            
            #Routine 6: Save Concatenated Image
            print('')
            print ('Save Concatenated Big Image...')
            pathRoot_Out = Path(pathRoot_Out).parent
            pathRoot_Out = str(Path.joinpath(Path(pathRoot_Out),  (Path(pathRoot_In).name + '_zSlices')))
            createFolder(pathRoot_Out, remove=False)
            
            fileName = ("nx_" + str(nx) + "_ny_" + str(ny) + "_z0_" + str(zSlice[0]) + "_" + imgProcessing)
            [isSaved, filePath, dt] = save_2Dimage(img_Concatenated, rootPath=pathRoot_Out, fileName=fileName, imgFormat='.tif')
            print('time=', dt)
        
        return filePath
 
    



# Step 1: Create a worker class
class Worker(QObject):
    progress = pyqtSignal(int)
    results   = pyqtSignal(object)
    finished = pyqtSignal()
    
    
    # resultsReady = pyqtSignal(np.ndarray, int, int)
    # resultsReady = pyqtSignal()
    # progress = pyqtSignal(int)

    def __init__(self, fn, *args, **kwargs):
        super(QObject, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        
        
    def run(self):
        """Long-running task."""
        print()
        print('----------------------------')
        print('.....Long-Running Task......')
        print('----------------------------')
        
        res = self.fn(*self.args, **self.kwargs)
        self.results.emit(res)
        self.finished.emit()

        #self.resultsReady(img_Concatenated, nx, ny)
        #self.resultsReady.emit()        
        # print()
        # print('----------------------------')
        # print('............End.............')
        # print('----------------------------')
        # self.finished.emit(img_Concatenated, nx, ny)
        
        # self.progress.emit(i + 1)
        # self.finished.emit()





#==============================================================================
#            MAIN
#==============================================================================
if __name__ == '__main__':
    #Prevents issues with pyinstaller
    freeze_support()
    
    # checks if QApplication already exists 
    app = QtWidgets.QApplication.instance() 
    if not app: 
        # create QApplication if it doesnt exist 
         app = QtWidgets.QApplication([])   
    # to cause the QApplication to be deleted later
    app.aboutToQuit.connect(app.deleteLater)    
    
    application = mywindow()     
    application.show()     
    sys.exit(app.exec_())
 
# =============================================================================
# Draft    
# =============================================================================
    # def event_test(self):
    #     a, b = 1, 2
    #     args = [a, b]
    #     fn = self.sum
    #     # Step 2: Create a QThread object
    #     self.thread = QThread()
        
    #     # Step 3: Create a worker object
    #     self.worker = Worker(fn, *args)
    #     # self.worker = Worker(RootPath_In, xyz_Range, parse_Data, flipX, flipY, RootPath_Out, scan_dx, scan_dy, z0, imgOperation_16to8bit, isParallel, nProcesses, nThreads)

        
    #     # Step 4: Move worker to the thread
    #     self.worker.moveToThread(self.thread)
        
    #     # Step 5: Connect signals and slots
    #     self.thread.started.connect(self.worker.run)
    #     self.worker.finished.connect(self.thread.quit)
    #     self.worker.finished.connect(self.worker.deleteLater)
    #     self.thread.finished.connect(self.thread.deleteLater)
        
    #     # Step 6: Connect singals    
    #     self.worker.finished.connect(self.event_Worker_finished)
    #     # self.worker.progress.connect(self.reportProgress)
        
    #     # Step 6: Start the thread
    #     self.thread.start()
        
    # def sum(self, a, b):
    #    c = a + b
    #    return  c

# =============================================================================
# 
# =============================================================================


        # Step 3: Create a worker object        
        # dt = convert_scanHDF5toUnchunked(pathRoot_In, pathRaw_In, pathRoot_Out, pathRaw_Out,
        #                                   xyz_Range, xyz_index, channel, ending, xyz_flip,
        #                                   isParallel, nProcesses, nThreads, isPlot=True) 