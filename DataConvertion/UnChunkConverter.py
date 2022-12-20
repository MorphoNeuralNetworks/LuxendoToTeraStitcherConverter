# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 21:34:15 2020

@author: aarias
"""


from pathlib import Path
import os
# import sys
import shutil
import numpy as np
# import concurrent.futures
from tqdm import tqdm


from DataStructure.Parser import parse_String
from DataStructure import MuViSPIM
# from DataStructure import TeraStitcher
# from DataConvertion.StructureConverter import convert_DataStructure

from IO.Files.FileManager import createFolder


from matplotlib import pyplot as plt
import matplotlib.cm as cm

# from ImageProcessing.ImageMerger import (concatenate_imgScan)
# from IO.Image.write import save_2Dimage

from shutil import copytree, ignore_patterns
import h5py
import time   
import threading
import pandas as pd
import sys

from  ParallelComputing.WorkManager import parallelComputing, plot_ComputingPerformance
import itertools


from Plotting.Plotter import save_Figure
from IO.Files.FileWriter import save_CSV     



# =============================================================================
#   Main Function
# =============================================================================
def convert_scanHDF5toUnchunked(pathRoot_In, pathRaw_In, pathRoot_Out, pathRaw_Out, xyz_Range, xyz_index, channel, ending, xyz_flip, isParallel=False, nProcesses=1, nThreads=1, isPlot=False):
    print('')
    print('convert_scanHDF5toUnchunked...')
    
    
    t0 = time.time()
    
      
    #Step 1: Get Input Folders (All)
    xyMatrix_In_All = MuViSPIM.get_MatrixPaths(pathRaw_In, xyz_index, channel, ending, xyz_flip)
    
    #Step 2: Get Input DataStructure (Subset)
    [xyMatrix_In, zVector_In] = MuViSPIM.get_DataStructure(pathRaw_In, xyz_Range, xyz_index, channel, ending, xyz_flip)
    
    #Step 3: Get the Input  
    vectorPath_In_All  = xyMatrix_In_All.flatten()
    vectorPath_In  = xyMatrix_In.flatten()
    vectorPath_In_Ignore = np.setxor1d(vectorPath_In_All, vectorPath_In)
    vectorFolder_In_Ignore = get_folderName(vectorPath_In_Ignore)
 
    #Copy all the Folders but ignore:
    #   a) HDF5 files
    #   b) Tiles (when converting a subset of tiles, ignore the ones that are not included in the subset)
    ingnore_Files_HDF5 ='*.h5'
    ingnore_Files_HDF5 = ending    
    
    if channel=='channel_0':
        ingnore_channel = '*channel_1*'
    elif channel=='channel_1':
        ingnore_channel = '*channel_0*'
    else:
        print()
        print('convert_scanHDF5toUnchunked: unkown channel to ignore')
        
    copytree(pathRoot_In, pathRoot_Out, ignore=ignore_patterns(ingnore_Files_HDF5, ingnore_channel, *vectorFolder_In_Ignore))     
    
    
    
    # print(pathRoot_In)
    # print(pathRaw_In)
    # print(pathRoot_Out)
    # print(pathRaw_Out)    
    # jajaja
    
    #Runn Routine
    if not isParallel:
        t0 = time.time()
        run_SequentialComputing(vectorPath_In, pathRaw_Out)         
    else:
        t0 = time.time()
        run_ParallelComputing(vectorPath_In, pathRaw_Out, nProcesses, nThreads, isPlot)
        
    dt = time.time() - t0  
    return dt

# =============================================================================
#   Sequential Computing
# ============================================================================= 

def run_SequentialComputing(vectorPath_In, pathRoot_Out):
    nPaths = vectorPath_In.shape[0]
    for i in tqdm(range(0, nPaths)):
        [dt1, dt2] = convert_fileHDF5toUnchunked(vectorPath_In[i], pathRoot_Out)
    
    
# =============================================================================
#   Parallel Computing
# =============================================================================

def run_ParallelComputing(vectorPath_In, pathRoot_Out, nProcesses=1, nThreads=1, isSaveTable=True, isSavePlot=True, sortedBy='workerID'):     
    nPaths = vectorPath_In.shape[0] 
    taskID = np.arange(1, nPaths + 1)
    # t0 = time.time()
    func = convert_fileHDF5toUnchunked    
    args = [vectorPath_In, 
            list(itertools.repeat(str(pathRoot_Out), nPaths)),
            taskID,
            # list(itertools.repeat(t0, nPaths))
            ] 
    
    # Start Parallel Computing  
    res = parallelComputing(func, args, nProcesses, nThreads)
    
    
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

    #Saving Paths
    pathRoot_Out = Path(pathRoot_Out)
    pathFolder = Path.joinpath(pathRoot_Out.parent.parent.parent, pathRoot_Out.parent.parent.name + '_Performance')        
    createFolder(str(pathFolder), remove=False)   
    
    #Saving FileName
    fileName = ('2_convert_toUnchunked' +
                '_time_per_task_' + '{:0.3f}'.format(time_per_task) + 
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
        computation_labels = [ '1_Read', '2_Write']
        fig, ax = plot_ComputingPerformance(df_Times, computation_labels, sortedBy)    
        
        #Figure Labels
        figure_title = (
                        'nWorkers=' + str(nProcesses*nThreads) +
                        ', nProcesses='+ str(nProcesses) +
                        ', nThreads='+ str(nThreads) +
                        ', time_per_task=' + '{:0.3f}'.format(time_per_task)
                        )
        ax.set_title(figure_title, fontsize=12)    
        
        #Save Figure
        save_Figure(fig, pathFolder, fileName)
        
        #Close Figures
        # plt.clf()
        # plt.close(fig)
        plt.close('all')



                               
def convert_fileHDF5toUnchunked(FilePath_In, pathRoot_Out, taskID=1, t0=0):  
    # Cast
    FilePath_In = Path(FilePath_In)
    pathRoot_Out = Path(pathRoot_Out)
    
    #Taking Process and Threads ID
    process_ID = os.getpid()
    thread_ID = threading.current_thread().ident
    compID_Read  = 1
    compID_Write = 2
    
    # Get: the Output Tile File and Folder
    FilePath_Out = Path.joinpath(pathRoot_Out, FilePath_In.parent.name, FilePath_In.name)    
    
    # Read: h5 file
    start_Read = time.time() - t0
    with h5py.File(FilePath_In, 'r') as f:
        
        file_keys = list(f.keys())
        
        #Data
        data_key = file_keys[0] 
        data = f[data_key]
        imgStack = data[:,:,:]
        # imgStack =  np.array(data) #this operation takes longer
        
        #Metada
        metadata_key = file_keys[1] 
        metadata = f[metadata_key]
        
        stop_Read = time.time() - t0
        dt_read = stop_Read - start_Read
        print() 
        print('Reading chunked h5...')
        print('File Path In:', FilePath_In)
        print('dt_read=', dt_read)      
                   
        # Write: h5 file (without chunks)
        start_Write = time.time() - t0
        with h5py.File(FilePath_Out, "w") as data_file:            
            
            #Data
            data_file.create_dataset(data_key, data=imgStack)
            data_file[data_key].attrs.update(data.attrs)
            
            #MetaData
            data_file.create_dataset(metadata_key, data=metadata)
            data_file[metadata_key].attrs.update(data.attrs)
            
            stop_Write = time.time() - t0
            dt_write = stop_Write - start_Write
            print()
            print('Writing unchunked h5...')
            print('File Path Out:', FilePath_Out)
            print ('dt_write=', dt_write)
    
    op1 = [taskID, compID_Read,  process_ID, thread_ID, start_Read,  stop_Read]  
    op2 = [taskID, compID_Write, process_ID, thread_ID, start_Write, stop_Write] 
     
    return [op1, op2] 

    
# =============================================================================
#   Additional Function   
# =============================================================================
def get_folderName(pathFiles):
    folderNames = []
    for pathFile in pathFiles: 
        pathFile = Path(pathFile)
        folderName = pathFile.parent.name
        folderNames.append(folderName)
    return folderNames

# =============================================================================
#   Main
# =============================================================================
if __name__ == '__main__':

 
    # =============================================================================
    #     Input Path
    # =============================================================================
    
    # Set Input Path
    FilePath_In = r'C:\Users\aarias\MyPipeLine\TestConvertUnChunked\Brain_0000_0000_SPIM\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
    FilePath_In = r'F:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
  
    
    # =============================================================================
    #     Output Path
    # =============================================================================
    
    # Set Output Path
    RootPath_Out =r'C:\Users\aarias\MyPipeLine\TestConvertUnChunked'    

    # =============================================================================
    #     Simulating the GUI Data introduced by the User
    # =============================================================================
    
    #GUI features
    parse_ending = "File_0_Cam_Left_00000.lux.h5"         
    parse_channel = "Folder_16_channel_0"
    parse_scanX = "Folder_9_00" 
    parse_scanY =  "Folder_13_00" 
    parse_scanY = "Folder_9_00" 
    parse_scanX =  "Folder_13_00" 
    parse_scanZ = ''
    flipX = False
    flipY = False
    flipZ = False    
    xyz_flip = [flipX, flipY, flipZ]
    
    #Parsing
    [myRoot, scanX, x_index] = parse_String(parse_scanX)
    [myRoot, scanY, y_index] = parse_String(parse_scanY)
    [myRoot, scanY, z_index] = parse_String(parse_scanZ)
    [myRoot, channel, index] = parse_String(parse_channel)
    [myRoot, ending, index] = parse_String(parse_ending) 
    xyz_index = [x_index, y_index, z_index]
    
    #Subset
    x0=0
    y0=0
    z0=0
    z0 = np.random.randint(0, high=1700, size=1, dtype=int)[0]
    z0=0
    dx=2
    dy=1
    dz=1
    xyz_Range = [x0, y0, z0, dx, dy, dz]


    # =============================================================================
    #   Setting the Paths
    # =============================================================================
    
    #Setting: Input Paths
    FilePath_In = Path(FilePath_In)    
    pathRoot_In = FilePath_In.parent.parent.parent.parent     
    pathRaw_In = FilePath_In.parent.parent  

    #Setting: Output Paths
    pathRoot_Out = str(Path.joinpath(Path(RootPath_Out), (pathRoot_In.name + '_UnChunked')))    
    if  os.path.exists(pathRoot_Out): 
        shutil.rmtree(pathRoot_Out)     
    pathRaw_Out = str(Path.joinpath(Path(pathRoot_Out), pathRaw_In.parent.name, pathRaw_In.name))
    
    
    
    #Settings
    isParallel = True
    nProcesses = 2
    nThreads = 1    
    isPlot = True
    
    
    jjajaja
    # =============================================================================
    #     
    # =============================================================================

    dt = convert_scanHDF5toUnchunked(pathRoot_In, pathRaw_In, pathRoot_Out, pathRaw_Out,
                                     xyz_Range, xyz_index, channel, ending, xyz_flip,
                                     isParallel, nProcesses, nThreads, isPlot)
 


   
# =============================================================================
#     
# =============================================================================
    #Read:  12.45
    #Write: 16.67
    #Total: 29.12 sec -> 400 tiles -> 3.2h

# =============================================================================
# 
# =============================================================================
    # if isPlot==True:
            
    #     # =============================================================================
    #     #   Unpacking
    #     # =============================================================================
    #     res = list(filter(None, res))
    #     M = np.concatenate(res, axis=0)
    #     M = np.concatenate(M, axis=0)  
    #     df_Times = pd.DataFrame(M, columns=['taskID', 'compID', 'processID', 'threadID', 'start', 'stop'])
    #     df_Times['width'] = df_Times['stop'] - df_Times['start']
        
    
    #     # =============================================================================
    #     #   Plotting
    #     # =============================================================================
    #     computation_labels = [ '1_Read', '2_Write']  
        
    #     # localPath = Path(os.path.dirname(sys.argv[0]))
    #     # localPath = localPath.parent
    #     # rootName = 'Results'        
    #     # pathFolder = Path.joinpath(localPath, rootName, 'Performance_CPU_IO')
    #     pathRoot_Out = Path(pathRoot_Out)
    #     pathFolder = Path.joinpath(pathRoot_Out.parent.parent.parent, pathRoot_Out.parent.parent.name +' _Performance')        
    #     createFolder(str(pathFolder), remove=False)   
        
    #     #Compute: the time per task
    #     nTasks = np.unique(df_Times['taskID']).shape[0]
    #     dt_total = (df_Times['stop'].max() - df_Times['start'].min())
    #     time_per_task = dt_total/nTasks
        
    #     #Figure    
    #     fig, ax  = plot_ComputingPerformance(df_Times, computation_labels)    
        
    #     #Figure Labels
    #     figure_title = (
    #                     'nWorkers=' + str(nProcesses*nThreads) +
    #                     ', nProcesses='+ str(nProcesses) +
    #                     ', nThreads='+ str(nThreads) +
    #                     ', time_per_task=' + '{:0.2f}'.format(time_per_task)
    #                     )
    #     ax.set_title(figure_title, fontsize=12)  
    #     ax.set_ylabel('Task') 
    #     ax.set_xlabel('Time [seconds]')   
    #     plt.show()
        
    #     #Save Figure
    #     fileName = ('1_unchunk_HDF5' +
    #                 '_time_per_task_' + '{:0.2f}'.format(time_per_task) + 
    #                 '_nW_' + str(nProcesses*nThreads) + 
    #                 '_nP_' + str(nProcesses) +
    #                 '_nT_' + str(nThreads) )
    #     save_Figure(fig, pathFolder, fileName)

