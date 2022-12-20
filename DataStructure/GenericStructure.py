# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 20:59:22 2020

@author: aarias
"""
import numpy as np

#Path Handeling
from glob import glob
from pathlib import Path
import fnmatch


import os

from DataStructure.parser import parse_String

#Improvements:
#   1) Image: imgSequence or imgStacks
#   2) Layout Information: File or Folder
#   3) Filter: 
#        3.1)Channel Information: File or Folder
#        3.2)File Ending: only on Folder case
#   4) 
#Note: An image stack is a series of 2D image
#Functions:
#   1) get_ScanningLayoutFromFolders
#   2) get_ScanningLayoutFromFiles

def get_MatrixPaths(RootPath, x_index, y_index, channel, ending):
    imgStack_FolderPaths = glob(RootPath + '\\*\\')  

    v_name = []    
    v_x_str = []
    v_y_str = []
    for path in imgStack_FolderPaths:
        #Parsing Channel
        p = Path(path) 
        if fnmatch.fnmatch(p.name, ('*' + channel + '*')):
            
            myName = p.name
            x = myName[x_index[0]:x_index[-1]]
            y = myName[y_index[0]:y_index[-1]]

            myAux = os.path.join(str(p.absolute()),  ending)
            v_name.append(myAux)
            v_x_str.append(x)
            v_y_str.append(y)
    
    #Convert from str to int32        
    v_x = np.asarray(v_x_str, dtype=np.int)
    v_y = np.asarray(v_y_str, dtype=np.int)
        
    #Get Unique
    v_x = np.unique(v_x)
    v_y = np.unique(v_y)
   
    #Get dimensions
    nx = v_x.shape[0]   #Columns
    ny = v_y.shape[0]   #Rows
    
    #Store
    v_name = np.asanyarray(v_name)
    M = v_name.reshape((ny, nx))
    return M


if __name__ == '__main__':
    #ByPassing
    FilePath =  "K:\\AriasDB\\Brains\\MuViSPIM\\17635\\0_raw\\2020-02-05_172847\\stack_0-x00-y00_channel_0\\Cam_Left_00000.h5"
    RootPath =  "K:\\AriasDB\\Brains\\MuViSPIM\\17635\\0_raw\\2020-02-05_172847"

    parse_ending = "File_0_Cam_Left_00000.h5"
    parse_channel = "Folder_16_channel_0"
    parse_scanY = "Folder_9_00" 
    parse_scanX =  "Folder_13_00" 
    parse_scanZ = '_'
# =============================================================================
#      
# =============================================================================
    [myRoot, scanX, x_index] = parse_String(parse_scanX)
    [myRoot, scanY, y_index] = parse_String(parse_scanY)
    [myRoot, channel, index] = parse_String(parse_channel)
    [myRoot, ending, index] = parse_String(parse_ending)
# =============================================================================
#     
# =============================================================================
    M = get_MatrixPaths(RootPath, x_index, y_index, channel, ending)
    
# =============================================================================
#     
# =============================================================================
    
    