# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 14:35:50 2020

@author: aarias
"""

#Libraries: Maths 
import numpy as np

#Libraries: Parallel Computing
import concurrent.futures

#Libraries: Iterator Algebra
import itertools

#Libraries: Operative Systems        
import os

#Libraries: Path Handeling
from glob import glob
from pathlib import Path

#Libraries: Time
import time 

from tqdm import tqdm


#Libraries: Custom 
from IO.Image.read import read_SlicefromStack
from IO.Image.write import save_2Dimage
from ImageProcessing.ImageConverter import process_Image


# =============================================================================
# 
# =============================================================================
def convert_DataStructure(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation, isParallel=False, cpu_nProcesses=1, cpu_nThreads=1):
#def convert_DataStructure(imgStackIn_MatrixPath, z, scan_dx, scan_dy, imgOut_RootFolder, isParallel=False):
    t0 = time.time()
     
    if not isParallel:
        t0 = time.time()
        run_SequentialComputing(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation) 
        
    else:
        t0 = time.time()
        run_ParallelComputing(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation, cpu_nProcesses, cpu_nThreads)
        
    dt = time.time() - t0  
    return dt
        
def run_SequentialComputing(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation):    
    xyVector_In = xyMatrix_In.flatten()  
    xyVector_Out = xyMatrix_Out.flatten()
    
    n_stacks = xyVector_In.shape[0]
    nz = zVector_In.shape[0] 
    
    for i in tqdm(range(n_stacks)):
        #Get the file Path to read an Image Stack (a stack is a tile in the scanning layout conducted by the SPIM machine)
        imgStackIn_FilePath = xyVector_In[i]
        
        #Get the folder Path to save an Image Series  
        imgSeriesOut_FolderPath = xyVector_Out[i] 
        
        #Get all the file Paths to save an Image Series 
#        imgOut_FilePaths = create_TeraStitcherImageSeiresNames(imgSeriesOut_FolderPath, z)
        
        for k in range(nz):   
            #1) Read the k-th slide (i.e. a single image) from the stack 
            #2) Process the image (e.g. convert from 16bit to 8 bit)
            #3) Save the image in a new format (e.g. from .h5 to .tif)
            z_In  = zVector_In[k]
            z_Out = zVector_Out[k]            
            do_Task(imgStackIn_FilePath, z_In, imgSeriesOut_FolderPath, z_Out, imgOperation)       


def run_ParallelComputing(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation, cpu_nProcesses=1, cpu_nThreads=1):
    xyVector_In = xyMatrix_In.flatten()  
    xyVector_Out = xyMatrix_Out.flatten()    
    n_stacks = xyVector_In.shape[0]  
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_nProcesses) as executor:
    # with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_nProcesses) as executor:
        # executor.map(process_Tile,
        #               xyVector_In,  itertools.repeat(zVector_In, n_stacks),
        #               xyVector_Out, itertools.repeat(zVector_Out, n_stacks), 
        #               itertools.repeat(imgOperation, n_stacks),
        #               itertools.repeat(cpu_nThreads, n_stacks)
        #               ) 
        list(tqdm(executor.map(process_Tile,
                      xyVector_In,  itertools.repeat(zVector_In, n_stacks),
                      xyVector_Out, itertools.repeat(zVector_Out, n_stacks), 
                      itertools.repeat(imgOperation, n_stacks),
                      itertools.repeat(cpu_nThreads, n_stacks)
                      ), 
                  total=n_stacks))
        
def process_Tile(imgStack_In, zVector_In, imgStack_Out, zVector_Out, imgOperation, cpu_nThreads=1):     
    
    n_slides = zVector_In.shape[0]
    #Process each image slice in the Stack in a dedicated Thread
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(do_Task,                     
                     itertools.repeat(imgStack_In, n_slides),
                     zVector_In,
                     itertools.repeat(imgStack_Out, n_slides),
                     zVector_Out,
                     itertools.repeat(imgOperation, n_slides)
                     )


def do_Task(imgStackIn_FilePath, z_In, imgSeriesOut_FolderPath, z_Out, imgOperation, verbose=True):
    # print()
    # print('do_Task...')

    #Read Image Stack: H5 format 
    # print()
    # print('read_SlicefromStack')
    [img, dt_read] = read_SlicefromStack(imgStackIn_FilePath, z_In)
    
    #Process Image Stack:
    # print()
    # print('process_Image')
    [img, dt_process] = process_Image(img, imgOperation)

    
    #Save Image
    # print()
    # print('save_2Dimage')
    [isSaved, filePath, dt_write] = save_2Dimage(img, rootPath=imgSeriesOut_FolderPath, fileName=z_Out, imgFormat='.tif')

    #Total Time
    dt_total = dt_read + dt_process + dt_write
    
    if verbose==True:
        print()
        # print('do_Task...')
        # print('dt_read:', dt_read)
        # print('dt_process:', dt_process)
        # print('dt_write:', dt_write)
        print('dt_total:', dt_total)
        




# =============================================================================
#         
# =============================================================================



if __name__ == '__main__':
    #ByPassing
    FilePath_In =  "K:\\AriasDB\\Brains\\MuViSPIM\\17635\\0_raw\\2020-02-05_172847\\stack_0-x00-y00_channel_0\\Cam_Left_00000.h5"
    RootPath_Out =  "K:\\AriasDB\\Brains\\MuViSPIM\\17635\\" + 'testingGUI'
    

    parse_ending = "File_0_Cam_Left_00000.h5"
    parse_channel = "Folder_16_channel_0"
    parse_scanY = "Folder_9_00" 
    parse_scanX =  "Folder_13_00" 
    parse_scanZ = '_'
    

    from DataStructure.Parser import parse_String
    [myRoot, scanX, x_index] = parse_String(parse_scanX)
    [myRoot, scanY, y_index] = parse_String(parse_scanY)
    [myRoot, channel, index] = parse_String(parse_channel)
    [myRoot, ending, index] = parse_String(parse_ending)
    
    scan_dx, scan_dy = 754.347, 754.347
    
# =============================================================================
#     Data Structure: Input
# =============================================================================
    #Computing: Matrix In
    from DataStructure.MuViSPIM import get_MatrixPaths       

    p = Path(FilePath_In)
    RootPath_In = p.parent.parent 
    xyMatrix_In = get_MatrixPaths(RootPath_In, x_index, y_index, channel, ending)
    
    #Get the selected SubLayout
    [x0, y0, z0, dx, dy, dz] = [3, 0, 950, 2, 3, 1] 
    xyMatrix_In = xyMatrix_In[y0:y0+dy, x0:x0+dx]
    z1 = z0 + dz 
    zVector_In = np.arange(z0, z1)
    [ny, nx] = xyMatrix_In.shape    
            
# =============================================================================
#   Data Structure: Output  
# =============================================================================
    #Computing: Matrix Out
    
    
    from DataStructure.TeraStitcher import (create_TeraStitcherFolderNames,
                                            create_TeraStitcherFolderStructure)
    
    
    RootPath_Out = Path(RootPath_Out) #str(p.absolute())
    xStr, yStr = create_TeraStitcherFolderNames(nx, ny, scan_dx, scan_dy)
    xyMatrix_Out = create_TeraStitcherFolderStructure(RootPath_Out, xStr, yStr)
    zVector_Out = ['{0:06d}'.format(i) for i in zVector_In]
# =============================================================================
#     
# =============================================================================
    print (xyMatrix_In.shape)   
    print (xyMatrix_Out.shape)  
    
# =============================================================================
#    Data Structure Convertion: Input to Output  
# =============================================================================
#    isParallel = False
#    dt = convert_DataStructure(xyMatrix_In, zVector_In,
#                               xyMatrix_Out, zVector_Out,
#                               isParallel=isParallel)
    isParallel = True
    dt = convert_DataStructure(xyMatrix_In, zVector_In,
                               xyMatrix_Out, zVector_Out,
                               isParallel=isParallel)
    
# =============================================================================
#    #Routine
# =============================================================================
    
#    xyVector_In = xyMatrix_In.flatten()  
#    xyVector_Out = xyMatrix_Out.flatten()
#    
#    n_stacks = xyVector_In.shape[0]
#    nz = zVector_In.shape[0] 
#    
#    for i in range (n_stacks):
#        #Get the file Path to read an Image Stack (a stack is a tile in the scanning layout conducted by the SPIM machine)
#        imgStackIn_FilePath = xyVector_In[i]
#        
#        #Get the folder Path to save an Image Series  
#        imgSeriesOut_FolderPath = xyVector_Out[i] 
# 
#        for k in range(nz):   
#            #1) Read the k-th slide (i.e. a single image) from the stack 
#            #2) Process the image (e.g. convert from 16bit to 8 bit)
#            #3) Save the image in a new format (e.g. from .h5 to .tif)
#            z_In  = zVector_In[k]
#            z_Out = zVector_Out[k]  
#            
#            print('')
#            print (imgStackIn_FilePath)
#            print (z_In)
#            print('')
#            print (imgSeriesOut_FolderPath)
#            print (z_Out)
#            
#            #Read Image Stack: H5 format 
#            img = read_SlicefromStack(imgStackIn_FilePath, z_In)
#            
#            #Process Image Stack:
#            img = process_Image(img)
#        
#            #Save Image  
#            p = Path(imgSeriesOut_FolderPath)
#            imgOut_FilePath = p / z_Out
#            
#            jajja
#            img_Format = '.tif'
#            img_FilePath = str(imgOut_FilePath.absolute()) + img_Format 
#            print('hola')
#            print (img_FilePath)
#            cv2.imwrite(img_FilePath, img)

    
    
#            imgOut_FilePath.joinpath(imgOut_FilePath, img_Format )
    
    