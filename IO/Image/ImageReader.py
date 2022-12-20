# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 14:44:28 2020

@author: aarias
"""



#Libraries: Image Processing 
import h5py
import tifffile
# import cv2
import time
from pathlib import Path
# =============================================================================
# 
# =============================================================================

#Read: the complete h5 stack (3D)
def read_ImageStack(pathFile, zRange=None):
    t0 = time.time()
    imgFormat = Path(pathFile).suffix
    
    if imgFormat=='.h5':
        #Read Image Stack: H5 format 
        with h5py.File(pathFile, 'r') as f:
            myKeys = list(f.keys())
            imgStack= f[myKeys[0]] 
            if zRange==None:
                print('eeee')
                imgStack = imgStack[:,:,:]
                # imgStack = imgStack[18,:,:]
                # imgStack = np.memmap(pathFile, dtype=np.uint16, mode='r+', shape=(36, 2048, 2048))
                # imgStack = np.memmap(pathFile, dtype=np.uint16, mode='r+', shape=(2048, 36, 2048))
                # imgStack = np.memmap(pathFile, dtype=np.uint16, mode='r+', shape=(2048, 2048, 36))
                 
                # imgStack = np.array(imgStack[:,:,:])
            else:
                if (len(list(zRange)))==1:            
                    imgStack = imgStack[zRange, :, :]
                elif (len(list(zRange)))==2:            
                    imgStack = imgStack[zRange[0]:zRange[1] + 1, :, :]
                else:
                    print()
                    print('read_ImageStack: wrong zRange')
    elif (imgFormat=='.tif') or (imgFormat=='.tiff'): 
        if zRange==None:
            # imgStack = tifffile.imread(pathFile)
            imgStack = tifffile.memmap(pathFile)
        else:
            if (len(list(zRange)))>1:  
                # imgStack = tifffile.imread(pathFile, key=range(zRange[0], zRange[1] + 1))
                imgStack = tifffile.memmap(pathFile, key=range(zRange[0], zRange[1] + 1))
                
        
    else:
        print()
        print('read_ImageStack: Image Format Unkown')
        
    dt = time.time() - t0
    return [imgStack, dt] 
    
#Generalize to read_Stack
def read_SlicefromStack(pathFile, z, verbose=False):
    with h5py.File(pathFile, 'r') as f:
        t0 = time.time()
        myKeys = list(f.keys())
        data = f[myKeys[0]] 
        imgSlice = data[z,:,:]
        dt = time.time() - t0
        
        if verbose==True:
            print()
            print('Data')
            print(data)
            print(type(data))
            print('BitDepth:', data.dtype)
            print('Chunks:', data.chunks)
            print('MaxShape:', data.maxshape)
            print('Compression:', data.compression)
            print('Compression Opts:', data.compression_opts) 
            print(list(data.attrs))        
            print(list(data.attrs['element_size_um']))
            print('dt:', time.time() - t0)
        
    return imgSlice, dt
    # return data, dt

# def read_SlicefromStack2(pathFile, z):

#     # Open the HDF5 file
#     file = h5py.File(pathFile, "r")

#     image = np.array(file["/image"]).astype("uint8")
#     label = int(np.array(file["/meta"]).astype("uint8"))
#     file.close()

#     return image, label

# def read_image(path):
#     img = cv2.imread(path, -1)
#     return img 

def read_imageMetada(pathFile):
    pathFile = str(Path(pathFile))
    # if pathFile
    img_Format = pathFile.split('.')[-1]
    img_nx, img_ny, img_nz, img_BitDepth = None, None, None, None
    #Parse Image Format
    if img_Format=="h5":
        with h5py.File(pathFile, 'r') as read_file:
            myKeys = list(read_file.keys())
            imgStack= read_file[myKeys[0]] 
            img_nz, img_ny, img_nx = imgStack.shape
            img_BitDepth = str(type(imgStack[0,0,0]))
    else:
        pass      
        
    return [img_nx, img_ny, img_nz, img_BitDepth, img_Format]     

# =============================================================================
# 
# =============================================================================
if __name__ == '__main__':    
    #Ploting Library
    from matplotlib import pyplot as plt
    import matplotlib.cm as cm    
    import time
    from pathlib import Path
    from ImageProcessing.ImageConverter import process_Image
    import os
    import numpy as np
    import sys
    
    # z0 = np.random.randint(0, high=1700, size=1, dtype=int)[0]
    # print(z0)
# =============================================================================
# 
# =============================================================================
    pathFile_In = r'F:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x02-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
    # pathFile_In = r'C:\Users\aarias\MySpyderProjects\p1_11_DataStructureConverter\Results\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan_UnChunked_TeraStitcher\000000\000000_000000\000000_000380.tif'
    pathFile_In = r'C:\Users\aarias\MySpyderProjects\p1_11_DataStructureConverter\Results\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan_UnChunked_zSlices\nx_19_ny_21_z0_019500_img16to8_Linear_CropMinMax.tif'
    
    
    #Before Chunked
    pathFile_In = r'F:\Arias\BrainScans\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1800_17635_SPIM_MuVi_Line_ACF_Scan_Partial\Ref_1800_17635_raw\2020-02-05_172847\stack_0-x00-y00_channel_0\Cam_Left_00000.h5'
    
    #After Chunked
    # pathFile_In = r'F:\Arias\BrainScans\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan\Ref_1800_34583_Raw\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'

    pathFile_In = r'G:\Ref_722\Ref_722_scan\2021-04-15_161946\raw\stack_1-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
    
    pathFile_In = r'G:\Ref_1800_14500_SPIM_MuVi_Line_QK_Scan\Ref_1800_14500_Raw\2021-05-21_111307\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5' 

    pathFile = r'Ref_2100_39765_SPIM_MuVi_15x_Line_AJO_TS_M_Test\2022-01-28_152503\raw\stack_1-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'


    # Default: pathFileIn
    rootPath = Path.cwd().parent.parent
    folderName = "example"
    subfolderName = "data"
    pathFile = r'Ref_2100_39765_SPIM_MuVi_15x_Line_AJO_TS_M_Test\2022-01-28_152503\raw\stack_1-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
    pathFile = r'Ref_2100_39765_SPIM_MuVi_15x_Line_AJO_TS_M_Test\2022-01-28_152503\raw\stack_1-x12-y12_channel_0_obj_left\Cam_Left_00000.lux.h5'

    pathFile_In = Path.joinpath(rootPath, folderName, subfolderName, pathFile)  
    
    # pathFile_In = r'C:\Users\aarias\MySpyderProjects\p1_15_DataStructureConverter\example\results\TeraStitcherFormat\01_Structure\000000\000000_000000\000018_000018.tif'
# =============================================================================
#     
# =============================================================================
    
    pathFile_In  = str(Path(pathFile_In))
    
    [imgStack, dt] = read_ImageStack(pathFile_In)
    imgStack = imgStack[18, :, :]
    print()
    print('dt', dt)
    print('shape:', imgStack.shape)
    print('type :', type(imgStack))
    print('type item:', type(imgStack[0,0]))
    plt.imshow(imgStack,  cm.Greys_r, interpolation='nearest') 
    plt.show()
    # print(imgStack)
    
    
    # imgSlice, dt = read_SlicefromStack(pathFile=pathFile_In, z=0, verbose=True)
    # [imgStack, dt] = read_ImageStack(pathFile_In, zRange=[0,2])
    # [imgStack, dt] = read_ImageStack(pathFile_In)
    # imgStack = read_image(pathFile_In)
    # [img_nx, img_ny, img_nz, img_BitDepth, img_Format] = read_imageMetada(pathFile_In)



    
    # imgStack = tifffile.imread(pathFile_In, key=[0, 2, 1])
    # print()
    # print(imgStack.shape)  
    # Path(pathFile_In).suffix
    
    # [imgStack, dt] = read_ImageStack(pathFile_In)
    # print()
    # print('dt', dt)
    # print('shape:', imgStack.shape)
    
    # pathFile_In = r'C:\\Users\\aarias\\MySpyderProjects\\p1_15_DataStructureConverter\\example\\results\\TeraStitcherFormat\\01_Structure\\000000\\000000_000000\\000018_000018.tif'
    # [imgStack, dt] = read_ImageStack(pathFile_In)
    # print()
    # print('dt', dt)
    # print('shape:', imgStack.shape)
    
    # pathFile_In =  r'F:\Arias\BrainTempProcessing\Ref_1900_13678_15x_full\Ref_1900_13678_Raw_TeraStitcher\000000\000000_000000\000000_076000.tif'
    # [imgStack, dt] = read_ImageStack(pathFile_In)
    # print()
    # print('dt', dt)
    # print('shape:', imgStack.shape)
    
    
    
# =============================================================================
# 
# =============================================================================
    # InFilePath = r'F:\Arias\ProcessedBrains\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan_UnChunked_bk\2020-12-14_201244\raw\stack_0-x02-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
    # InFilePath = r'F:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x02-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'

    # #Reading Time: Slice
    # imgSlice, dt = read_SlicefromStack(InFilePath, z0, verbose=True)
    # print()
    # print(InFilePath)
    # print('dt=', dt)
    
    #Result:
        #Chunked:   1.55
        #Unchunked: 0.05
        #ratio:     31 faster
    
    # #Reading Time: Stack
    # imgStack, dt = read_ImageStack(InFilePath)
    # print()
    # print(InFilePath)
    # print('dt=', dt)
    
    #Result:
        #Chunked:   52
        #Unchunked: 34
        #ratio:     1.5 faster
        
    # from streamlit import caching
    # caching.clear_cache()
    # del imgSlice
    # sys._clear_type_cache()    
    # sys.getallocatedblocks()
    
    
# =============================================================================
#     MetaData
# =============================================================================
    # pathFile_In = r"F:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5"
    # pathFile_In  = str(Path(pathFile_In))
    # [img_nx, img_ny, img_nz, img_BitDepth, img_Format] = read_imageMetada(pathFile_In)
    
# =============================================================================
#     
# =============================================================================

    # InFilePath =  r"C:\Users\aarias\MyPipeLine\Cam_Left_00000.h5"
    # InFilePath =  r"C:\Users\aarias\MyPipeLine\Cam_Left_00000.lux.h5" 
    
    # InFilePath =  r"C:\Users\aarias\MyPipeLine\file_unchunked.h5"
    # InFilePath =  r"C:\Users\aarias\MyPipeLine\file_chunked.h5"
    # InFilePath =  r"C:\Users\aarias\MyPipeLine\file_chunked_2048.h5"
    # InFilePath =  r"C:\Users\aarias\MyPipeLine\file_AutoChunked.h5"
    
    # OutFilePath =  r"C:\Users\aarias\MyPipeLine\file_unchunked.h5"
    # OutFilePath =  r"C:\Users\aarias\MyPipeLine\file_chunked.h5"
    # OutFilePath =  r"C:\Users\aarias\MyPipeLine\file_AutoChunked.h5"
    # OutFilePath =  r"C:\Users\aarias\MyPipeLine\file_chunked_2048.h5"

# =============================================================================
# 
# =============================================================================
    
    # # Open the HDF5 file
    # t0 = time.time()
    # file = h5py.File(InFilePath, "r")
    # myKeys = list(file.keys())
    # print(myKeys)

    # image = file[myKeys[0]]
    # data = np.asarray(image[z0,:,:])
    # # data = np.asarray(image[0:64,0:64,0:64])
    # # data = np.asarray(image)
    
    
    # print()
    # print('Image')
    # print(image)
    # print(type(image))
    # print('BitDepth:', image.dtype)
    # print('Chunks:', image.chunks)
    # print('MaxShape:', image.maxshape)
    # print('Compression:', image.compression)
    # print('Compression Opts:', image.compression_opts) 
    
    
    # print()
    # print('MetaData')
    # metadata = file[myKeys[1]]
    # print(metadata)
    # print(type(metadata))
    # print(metadata.maxshape)
    

    
    # # Write data to HDF5
    # with h5py.File(OutFilePath, "w") as data_file:
    #     # data_file.create_dataset("data", data=data)
    #     # data_file.create_dataset("data", data=data, chunks=(64, 64, 64))
    #     # data_file.create_dataset("data", data=data, chunks=True)
    #     data_file.create_dataset("data", data=data, chunks=(1, 2048, 2048))
    
    
    # # data.shape
    # print(file.__bool__() )
    # file.close()
    # print(file.__bool__() ) 
    # dt1 = time.time() - t0
    # print(dt1)
    
    # label.astype
    # image = np.array(file[myKeys[0]]).astype("uint16")
    #     data_file.create_dataset("data", data=data, maxshape=(1901, 2048, 2048)) 

# =============================================================================
#     
# =============================================================================
    # t0 = time.time()
    # img = read_SlicefromStack(InFilePath, z)
    # # img = read_ImageStack(InFilePath)
    # dt1 = time.time() - t0
    # print(dt1)
    
# =============================================================================
#     
# =============================================================================
    # #My Book Duo: Whole
    # InFilePath =  r"G:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Brain_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5"
    # InFilePath = str(Path(InFilePath))
    # parse_ending = "File_0_Cam_Left_00000.lux.h5"

    # #Lacie: Partial
    # InFilePath =  r"F:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1800_17635_SPIM_MuVi_Line_ACF_Scan_Partial\0_raw\2020-02-05_172847\stack_0-x00-y01_channel_0\Cam_Left_00000.h5"
    # InFilePath = str(Path(InFilePath))
    # parse_ending = "File_0_Cam_Left_00000.h5"
# =============================================================================
#     
# =============================================================================
    # #MyBooKDuo: Whole Brain (Chunked)
    # InFilePath =  r"G:\Arias\Brains\ReadSpeedTest\Brain_0000_0000_SPIM\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5"
    # InFilePath = str(Path(InFilePath))
    
    # #MyBooKDuo: Whole Brain (UnChunked)
    # InFilePath =  r"G:\Arias\Brains\ReadSpeedTest\Brain_0000_0000_SPIM_Unchunked\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5"
    # InFilePath = str(Path(InFilePath))
    
    # #Lacie: Whole Brain (Chunked)
    # InFilePath =  r"F:\Arias\Brains\ReadSpeedTest\Brain_0000_0000_SPIM\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5"
    # InFilePath = str(Path(InFilePath))
    
    # #Lacie: Whole Brain (UnChunked)
    # InFilePath =  r'F:\Arias\Brains\ReadSpeedTest\Brain_0000_0000_SPIM_Unchunked\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
    # InFilePath = str(Path(InFilePath))
    
    # #SDD: Whole Brain (Chunked)
    # InFilePath =  r'C:\Users\aarias\MyPipeLine\ReadSpeedTest\Brain_0000_0000_SPIM\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
    # InFilePath = str(Path(InFilePath))
   
    # #SDD: Whole Brain (Unchunked)
    # InFilePath =  r'C:\Users\aarias\MyPipeLine\ReadSpeedTest\Brain_0000_0000_SPIM_Unchunked\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
    # InFilePath = str(Path(InFilePath))

    # #SDD: test
    # InFilePath =    r'C:\Users\aarias\MyPipeLine\TestConvertUnChunked\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan_UnChunked\2020-12-14_201244\raw\stack_0-x01-y03_channel_0_obj_left\Cam_Left_00000.lux.h5'  
    # InFilePath = str(Path(InFilePath))

# =============================================================================
# 
# =============================================================================
    # InFilePath = r'F:\Arias\ProcessedBrains\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan_UnChunked_bk\2020-12-14_201244\raw\stack_0-x02-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
    # InFilePath = r'F:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x02-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'

    # #Reading Time: Slice
    # imgSlice, dt = read_SlicefromStack(InFilePath, z0, verbose=True)
    # print()
    # print(InFilePath)
    # print('dt=', dt)

    
    # #Reading Time: Stack
    # imgStack, dt = read_ImageStack(InFilePath)
    # print()
    # print(InFilePath)
    # print('dt=', dt)
    
        
    # from streamlit import caching
    # caching.clear_cache()
    # del imgSlice
    # sys._clear_type_cache()    
    # sys.getallocatedblocks()

# =============================================================================
#     Summary
# =============================================================================
    #Chunked Vs UnChunked
    #HDD (LaCie ): 2.2951/0.0079=290.51
    #HDD (MyBook): 
    #SSD (PC    ): 0.1234/0.0069= 17.88
    
# =============================================================================
# 
# =============================================================================

    
    # imgSlice, dt = read_SlicefromStack(InFilePath, z0)
    # # img = read_ImageStack(InFilePath)
    # print()
    # print(InFilePath)
    # print('dt=', dt)
    
    # t0 = time.time()
    # img = process_Image(img, 'None')
    # dt2 = time.time() - t0
    # print(dt2)
    
    # rootPath =  r"C:\Users\aarias\MyPipeLine"
    # rootPath = str(Path(rootPath))
    # fileName = 'test'
    # isSaved, dt3 = save_2Dimage(img, rootPath, fileName, img_Format='.tif')
    # print(dt3, isSaved)
    
    # dt = dt1 + dt2 + dt3
    # print(dt)
    
    
    

# =============================================================================
#     
# =============================================================================
    # InFilePath =  r"G:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Brain_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5"
    # InFilePath = str(Path(InFilePath))
    # print()
    # print(InFilePath)

    # t0 = time.time()
    # img = read_SlicefromStack(InFilePath, z)
    # dt1 = time.time() - t0
    # print(dt1)
    
    # t0 = time.time()
    # img = process_Image(img, 'None')
    # dt2 = time.time() - t0
    # print(dt2)
    
    # rootPath =  r"C:\Users\aarias\MyPipeLine"
    # rootPath = str(Path(rootPath))
    # fileName = 'test'
    # isSaved, dt3 = save_2Dimage(img, rootPath, fileName, img_Format='.tif')
    # print(dt3, isSaved)
    
    # dt = dt1 + dt2 + dt3
    # print(dt)
    
    
# =============================================================================
# 
# =============================================================================


    # for z in range(0,5):
    #     InFilePath =  r"G:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Brain_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5"
    #     InFilePath = str(Path(InFilePath))
    #     print()
    #     print(InFilePath)
    
    #     t0 = time.time()
    #     img = read_SlicefromStack(InFilePath, z)
    #     dt = time.time() - t0
    #     print(dt)
    
    # vz = [0, 300, 1800]
    # for z in vz:
    #     InFilePath =  r"G:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Brain_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5"
    #     InFilePath = str(Path(InFilePath))
    #     print()
    #     print(InFilePath)
    
    #     t0 = time.time()
    #     img = read_SlicefromStack(InFilePath, z)
    #     dt = time.time() - t0
    #     print(dt)
# =============================================================================
# 
# =============================================================================
    # plt.imshow(img,  cm.Greys_r, interpolation='nearest') 
    # plt.show()



