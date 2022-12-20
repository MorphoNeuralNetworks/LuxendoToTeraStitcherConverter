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
from IO.Image.ImageReader import read_ImageStack
from IO.Image.ImageWriter import save_image, save_2Dimage
from ImageProcessing.ImageConverter import process_Image
from ParallelComputing.WorkManager import parallelComputing, plot_ComputingPerformance


import threading
import pandas as pd
# from matplotlib import pyplot as plt

from Plotting.Plotter import save_Figure
from IO.Files.FileManager import createFolder
from IO.Files.FileWriter import save_CSV     

from matplotlib import pyplot as plt



# list(itertools.product(np.asarray([1,2]), repeat=2))
# list(itertools.combinations_with_replacement(np.asarray([1,2, 3]), r=2))


# =============================================================================
# 
# =============================================================================
def convert_DataStructure(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation, imgOutFormat='tiff3D', isParallel=True, nProcesses=1, nThreads=1):
#def convert_DataStructure(imgStackIn_MatrixPath, z, scan_dx, scan_dy, imgOut_RootFolder, isParallel=False):
    t0 = time.time()
     
    if not isParallel:
        t0 = time.time()
        run_SequentialComputing(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation) 
        
    else:
        t0 = time.time()
        run_ParallelComputing(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation, imgOutFormat=imgOutFormat, nProcesses=nProcesses, nThreads=nThreads)
        
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



def run_ParallelComputing(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation, imgOutFormat='tiff3D' , nProcesses=1, nThreads=1, isSaveTable=True, isSavePlot=True, sortedBy='workerID'):     
    # t0 = time.time()

    # Set the arguments
    xyVector_In = xyMatrix_In.flatten()  
    xyVector_Out = xyMatrix_Out.flatten() 
    
    n_Tiles = xyVector_In.shape[0]
    n_Slices = zVector_In.shape[0]    

    

    if (imgOutFormat=='tiff2D'):
        # Set the Function
        func = do_Task 
    
        nTasks = n_Tiles*n_Slices
        taskID = np.arange(1, nTasks + 1)
    
        xyVector_In = list(np.asarray(list(zip(*list(itertools.repeat(xyVector_In, n_Slices))))).flatten())
        zVector_In  = list(np.asarray(list(itertools.repeat(zVector_In, n_Tiles))).flatten())    
        xyVector_Out = list(np.asarray(list(zip(*list(itertools.repeat(xyVector_Out, n_Slices))))).flatten())
        zVector_Out  = list(np.asarray(list(itertools.repeat(zVector_Out, n_Tiles))).flatten())    
        imgOperation = list(itertools.repeat(imgOperation, nTasks))    
    elif (imgOutFormat=='tiff3D'):
        # Set the Function
        func = do_Task 
        
        nTasks = n_Tiles
        taskID = np.arange(1, nTasks + 1) 
        
        zVector_In   = list(itertools.repeat(zVector_In,  n_Tiles))    
        zVector_Out  = list(itertools.repeat(zVector_Out, n_Tiles))   
        imgOperation = list(itertools.repeat(imgOperation, nTasks))  
    else:
        print()
        print('Invalid OutPut Image Format')
      
    # print()
    # print(xyVector_In)
    # print(zVector_In)
    # print(xyVector_Out)
    # print(zVector_Out)
    # print(imgOperation)

    
    args = [xyVector_In, zVector_In,
            xyVector_Out, zVector_Out,
            imgOperation,
            taskID
            ] 
    
    # Start Parallel Computing
    res = parallelComputing(func, args, nProcesses, nThreads)
    
    # print()
    # print('Long Computation finished...')
    # print('Storing performance data of the Long Computation...')
    
    #Unpack: Parallel Computing Results
    res = list(filter(None, res))
    M = np.concatenate(res, axis=0)
    M = np.concatenate(M, axis=0)  
    df_Times = pd.DataFrame(M, columns=['taskID', 'compID', 'processID', 'threadID', 'start', 'stop'])
    df_Times['width'] = df_Times['stop'] - df_Times['start']
       
    #Compute: the time per task
    nTasks = np.unique(df_Times['taskID']).shape[0]
    dt_total = (df_Times['stop'].max() - df_Times['start'].min())
    time_per_task = dt_total/nTasks
    time_per_image = dt_total/(n_Tiles*n_Slices)

    #Saving Paths
    pathRoot_Out = Path(xyVector_Out[0])
    pathFolder = Path.joinpath(pathRoot_Out.parent.parent.parent, '03_Performance') 
    createFolder(str(pathFolder), remove=False)   
    
    #Saving FileName
    fileName = ('2_convert_toTeraStitcher' +
                '_time_per_image_' + '{:0.3f}'.format(time_per_image) + 
                '_nW_' + str(nProcesses*nThreads) + 
                '_nP_' + str(nProcesses) +
                '_nT_' + str(nThreads) +
                '_nTasks_' + str(nTasks))        
    
    #Saving: Table (.csv format)
    if isSaveTable==True:        
        save_CSV(df_Times, pathFolder, fileName)
    
    #Saving: Plot (.png format)
    if isSavePlot==True:           

        #Ploting: Parallel Computing Graph 
        computation_labels = [ '1_Read', '2_Process', '3_Write']
        fig, ax = plot_ComputingPerformance(df_Times, computation_labels, sortedBy)    
        
        #Figure Labels
        figure_title = (
                        'nWorkers=' + str(nProcesses*nThreads) +
                        ', nProcesses='+ str(nProcesses) +
                        ', nThreads='+ str(nThreads) +
                        ', time_per_task=' + '{:0.3f}'.format(time_per_task) +
                        ', time_per_image=' + '{:0.3f}'.format(time_per_image)
                        )
        ax.set_title(figure_title, fontsize=12)    
        
        #Save Figure
        save_Figure(fig, pathFolder, fileName)
        
        #Close Figures
        plt.close('all')



def do_Task(imgStackIn_FilePath, z_In, imgSeriesOut_FolderPath, z_Out, imgOperation, taskID=1, t0=0):
    # print()
    # print('do_Task...')
    

    #Read Image Stack: H5 format 
    # print()
    # print('read_SlicefromStack')
    start_Read = time.time() - t0
    [img, dt_read] = read_ImageStack(imgStackIn_FilePath, zRange=[z_In[0], z_In[-1]])
    stop_Read = time.time() - t0
    # print(img.shape)
    
    #Process Image Stack:
    # print()
    # print('process_Image')
    start_Process= time.time() - t0
    [img, dt_process] = process_Image(img, imgOperation)
    stop_Process= time.time() - t0
    dt_process = stop_Process - start_Process
    # print(img.shape)

    #Save Image
    # print()
    # print('save_2Dimage')
    start_Write= time.time() - t0
    z_Out = z_Out[0] + '_' + z_Out[-1]
    [isSaved, filePath, dt_write] = save_image(img, rootPath=imgSeriesOut_FolderPath, fileName=z_Out, imgFormat='.tif')
    stop_Write= time.time() - t0
    # print(img.shape)

    #Total Time
    dt_total = dt_read + dt_process + dt_write
    
    #Taking Process and Threads ID
    process_ID = os.getpid()
    thread_ID = threading.current_thread().ident
    [compID_Read, compID_Process, compID_Write] = [1, 2, 3]
    
    op1 = [taskID, compID_Read,  process_ID, thread_ID, start_Read,  stop_Read]  
    op2 = [taskID, compID_Process, process_ID, thread_ID, start_Process, stop_Process] 
    op3 = [taskID, compID_Write, process_ID, thread_ID, start_Write, stop_Write] 
    
    verbose=False
    if verbose==True:        
        print()
        # print(imgStackIn_FilePath, z_In)
        # print('do_Task...')
        # print('dt_read:', dt_read)
        # print('dt_process:', dt_process)
        # print('dt_write:', dt_write)
        print('dt_total:', dt_total)
        
    return [op1, op2, op3]

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
    
# =============================================================================
#   Draft  
# =============================================================================
    # l = [1,2,3]
    # b = list(itertools.repeat(l, 3))
    
    # np.asarray(list(zip(*list(itertools.repeat(l, 3))))).flatten()
    
    # list(itertools.chain.from_iterable(zip(*b)))
    # list(itertools.chain.from_iterable(zip(*(itertools.repeat(l, 3)) )))

    
    # c = list(itertools.chain(*[ 2*x for x in a] ))
    
    
    # =============================================================================
# 
# =============================================================================
# def run_ParallelComputing(xyMatrix_In, zVector_In, xyMatrix_Out, zVector_Out, imgOperation, nProcesses=1, nThreads=1):
#     xyVector_In = xyMatrix_In.flatten()  
#     xyVector_Out = xyMatrix_Out.flatten()    
#     n_stacks = xyVector_In.shape[0]  
#     with concurrent.futures.ProcessPoolExecutor(max_workers=nProcesses) as executor:
#     # with concurrent.futures.ThreadPoolExecutor(max_workers=nProcesses) as executor:
#         # executor.map(process_Tile,
#         #               xyVector_In,  itertools.repeat(zVector_In, n_stacks),
#         #               xyVector_Out, itertools.repeat(zVector_Out, n_stacks), 
#         #               itertools.repeat(imgOperation, n_stacks),
#         #               itertools.repeat(nThreads, n_stacks)
#         #               ) 
#         list(tqdm(executor.map(process_Tile,
#                       xyVector_In,  itertools.repeat(zVector_In, n_stacks),
#                       xyVector_Out, itertools.repeat(zVector_Out, n_stacks), 
#                       itertools.repeat(imgOperation, n_stacks),
#                       itertools.repeat(nThreads, n_stacks)
#                       ), 
#                   total=n_stacks))
        
# def process_Tile(imgStack_In, zVector_In, imgStack_Out, zVector_Out, imgOperation, nThreads=1):     
    
#     n_slides = zVector_In.shape[0]
#     #Process each image slice in the Stack in a dedicated Thread
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         executor.map(do_Task,                     
#                      itertools.repeat(imgStack_In, n_slides),
#                      zVector_In,
#                      itertools.repeat(imgStack_Out, n_slides),
#                      zVector_Out,
#                      itertools.repeat(imgOperation, n_slides)
#                      )

# =============================================================================
# 
# =============================================================================

    # nz = img.shape[0]
    # for k in range(0, nz):
    #     [img[k,:,:], dt_process] = process_Image(img[k,:,:], imgOperation)