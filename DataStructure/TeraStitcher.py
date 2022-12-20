# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 20:57:45 2020

@author: aarias
"""
import numpy as np



#Path Handeling
import os
from pathlib import Path

def create_TeraStitcherFolderNames(nx, ny, scan_dx, scan_dy):
    
    #Get Scanning Rows
    y = np.arange(ny)
    y = np.round(10*scan_dy*y)
    y = y.astype(int)
    yStr = [('{0:06d}'.format(i))  for i in y]
    yStr = np.asarray(yStr)
    
    #Get Scanning Columns
    x = np.arange(nx)
    x = np.round(10*scan_dx*x)
    x = x.astype(int)
    xStr = [('{0:06d}'.format(i))  for i in x]
    xStr = np.asarray(xStr)
    
    return xStr, yStr

def create_TeraStitcherImageSeiresNames(imgSeriesOut_FolderPath, z):
    imgOut_FileNames = ['{0:06d}'.format(i) for i in z] 
    imgOut_FilePaths = [os.path.join(imgSeriesOut_FolderPath, i) for i in imgOut_FileNames]
    return imgOut_FilePaths


def create_TeraStitcherFolderStructure(imgOut_RootFolder, xStr, yStr):        
    
#    str(p.absolute())
    nx = xStr.shape[0]
    ny = yStr.shape[0]
    
    #Create TeraStitcher: Root Level (L0)     
    L0 = os.path.join(imgOut_RootFolder)  
    if not os.path.exists(L0):
        os.makedirs(L0) 
    
    #Create TeraStitcher: Two Hierarchical Levels 
    imgSeriesOut_FolderPaths = []
    for i in range(0, ny):
        #Create TeraStitcher Folder: First Level (L1)       
        L1 = os.path.join(L0, yStr[i])  
        if not os.path.exists(L1):
            os.makedirs(L1)
            
        for j in range(0, nx):            
            #Create TeraStitcher Folder: Second Level (L2) 
            L2 = os.path.join(L1, yStr[i] + '_' + xStr[j])  
            if not os.path.exists(L2):
                os.makedirs(L2)                 
            imgSeriesOut_FolderPaths.append(L2)
    imgSeriesOut_FolderPaths = np.asarray(imgSeriesOut_FolderPaths)
    M = imgSeriesOut_FolderPaths.reshape((ny,nx))
    return M


# =============================================================================
# 
# =============================================================================
def get_TeraStitcher_FolderPaths(RootFolder):
    
    # Get Paths
    img_TilePaths = sorted(list(Path(RootFolder).glob('*/*/**/')))

    v_x_str = []
    v_y_str = []
    for path in img_TilePaths:
        p = Path(path) 
        y_str, x_str = p.name.split('_')
        v_x_str.append(x_str)
        v_y_str.append(y_str)        

    #Convert from str to int32        
    v_x = np.asarray(v_x_str, dtype=np.int)
    v_y = np.asarray(v_y_str, dtype=np.int)
        
    #Get Unique
    v_x = np.unique(v_x)
    v_y = np.unique(v_y)
   
    #3) Output: Get dimensions
    nx = v_x.shape[0]   #Columns
    ny = v_y.shape[0]   #Rows
    img_TilePaths = np.asarray(img_TilePaths)
    M_FolderPaths = img_TilePaths.reshape((ny,nx))
    
    return M_FolderPaths

def get_TeraStitcher_FilePaths(RootFolder, ny, nx, z): 

    # img_FileName = '{0:06d}'.format(z[0]) + '.tif'   
    # img_FileName = str(z[0]) + '.tif'
    # img_FileName = '*.tif'
    
    img_FilePaths = sorted(list(Path(RootFolder).glob('**/*.tif*')))

    img_FilePaths = np.asarray(img_FilePaths)
    M_FilePaths = img_FilePaths.reshape((ny,nx))
    
    return M_FilePaths

def get_DataStructure(RootPath_Out, nx, ny, scan_dx, scan_dy, scan_dz, zVector_In, zUnits='slices'):
        #1) Computing: MatrixLayout
        xStr, yStr = create_TeraStitcherFolderNames(nx, ny, scan_dx, scan_dy)
        xyMatrix_Out = create_TeraStitcherFolderStructure(RootPath_Out, xStr, yStr)
        
        if zUnits=='thenths_microns':
            scan_dz = 10*scan_dz # ??? tenths of microns (this might not be required)
        elif zUnits=='slices':
            scan_dz =  1 # slices units
        else:
            print('')
            print('Folder:DataStructue')
            print('Module:TeraStitcher')
            print('Function: get_DataStructure()')
            print('WARNING: not supported zUnits string')
        zVector_Out = scan_dz*zVector_In
        
        #2) Computing: VectorSlices
        zVector_Out = ['{0:06d}'.format(i) for i in zVector_Out]
        return [xyMatrix_Out, zVector_Out]

        # #2) Computing: VectorSlices
        # zVector_Out = ['{0:06d}'.format(i) for i in zVector_In]
        # return [xyMatrix_Out, zVector_Out] 
# =============================================================================
# 
# =============================================================================

if __name__ == '__main__':
    pass


# =============================================================================
# 
# =============================================================================
