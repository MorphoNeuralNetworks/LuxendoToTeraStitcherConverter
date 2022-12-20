# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 20:59:22 2020

@author: aarias
"""
import numpy as np

#Path Handeling
from pathlib import Path
import fnmatch


import os
#from Parser import parse_String

from DataStructure.Parser import parse_String

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

#Particular Case MuViSPIM
def get_MatrixPaths(RootPath, xyz_index, channel, ending, xyz_flip):
    # Get Paths
    imgStack_FolderPaths = sorted(list(Path(RootPath).glob('*/')))
    [x_index, y_index, z_index] = xyz_index
    [flipX, flipY, flipZ] = xyz_flip

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
    if flipX==True:       
        M = np.flip(M,axis=1)
    if flipY==True:       
        M = np.flip(M,axis=0) 
        
    # print()
    # print('Matrix of Paths...')
    # print('Size')
    # print(nx, ny)
    # print('Length')
    # print(v_name.shape[0])
    # print('Flips')
    # print(flipX,flipY)
    # print()
    # print(M)
    # jajjaa
    
    return M

def get_MatrixLayout(nx, ny, x0, y0, dx, dy):
     M = np.ones((ny,nx)) 
     for i in range(y0, y0 + dy):
         for j in range(x0, x0 + dx):
             M[i,j] = 2
     return M
 
 
        #Routine 1: Get Input DataStructure
def get_DataStructure(RootPath_In, xyz_Range, xyz_index, channel, ending, xyz_flip):
    # print()
    # print("get_DataStructure")
    [x0, y0, z0, dx, dy, dz] = xyz_Range    
    
    #1) Computing: MatrixLayout   
    xyMatrix_In = get_MatrixPaths(RootPath_In, xyz_index, channel, ending, xyz_flip)
    
    #2) Computing: SubMatrix (ROI: Region of Interest)
    xyMatrix_In = xyMatrix_In[y0:y0+dy, x0:x0+dx]
    # print()
    # print("xyMatrix_In: \n", xyMatrix_In)
    
    
    #3) Computing: VectorSlices
    zVector_In = np.arange(z0, z0 + dz)
    
    return [xyMatrix_In, zVector_In]
        
if __name__ == '__main__':
    #ByPassing
    # FilePath =  "K:\\AriasDB\\Brains\\MuViSPIM\\17635\\0_raw\\2020-02-05_172847\\stack_0-x00-y00_channel_0\\Cam_Left_00000.h5"
    # RootPath =  "K:\\AriasDB\\Brains\\MuViSPIM\\17635\\0_raw\\2020-02-05_172847"

    # parse_ending = "File_0_Cam_Left_00000.h5"
    # parse_channel = "Folder_16_channel_0"
    # parse_scanY = "Folder_9_00" 
    # parse_scanX =  "Folder_13_00" 
    # parse_scanZ = '_'
    
# =============================================================================
#     
# =============================================================================
    FilePath =  "G:\\Arias\\Brains\\SPIM_LCS\\SPIM_LCS_Scans\\Brain_1800_34583_SPIM_LCS_Line_ACF_Scan\\2021-01-25_143342\\raw\\stack_0-x00-y00_channel_0_obj_bottom\\Cam_Bottom_00000.lux.h5"
    parse_ending = "File_0_Cam_Bottom_00000.lux.h5"
      
    FilePath =  "G:\\Arias\\Brains\\SPIM_MuVi\\SPIM_MuVi_Scans\\Brain_1800_34583_SPIM_MuVi_Line_ACF_Scan\\2020-12-14_201244\\raw\\stack_0-x00-y00_channel_0_obj_left\\Cam_Left_00000.lux.h5"
    parse_ending = "File_0_Cam_Left_00000.lux.h5"
     
    # self.InFilePath =  "F:\\4197 th\\stack_0-x00-y00_channel_0\\Cam_Left_00000.h5"
    # parse_ending = "File_0_Cam_Left_00000.h5"
     
    parse_channel = "Folder_16_channel_0"
    parse_scanX = "Folder_9_00" 
    parse_scanY =  "Folder_13_00" 
    parse_scanZ = ''
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
    p = Path(FilePath)
    RootPath = p.parent.parent
#    print(RootPath)
#    RootPath = (p.parent.parent.as_posix()  / '\\*\\'  ) 
         
    M = get_MatrixPaths(RootPath, x_index, y_index, channel, ending)
    
    print(M.shape)
 

# =============================================================================
#   Path: Unix and Windows OS Compatibility
# =============================================================================
  
