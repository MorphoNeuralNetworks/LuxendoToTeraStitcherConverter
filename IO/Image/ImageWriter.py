# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 14:45:03 2020

@author: aarias
"""

#Libraries: Image Processing 
# import cv2
import os
import time
from pathlib import Path 
import tifffile

def save_image(img, rootPath, fileName, imgFormat='.tif', mode=None):
    # print()
    # print("Saving Image...")
    t0 = time.time()
    
    # if mode=='xyz':
    #     img = img[1,2,0]

    filePath = str(Path.joinpath(Path(rootPath), fileName + imgFormat))    
    # isSaved = tifffile.imsave(filePath, img) #Faster , photometric='minisblack'
    # isSaved = tifffile.imwrite(filePath, img)
    isSaved = tifffile.imwrite(filePath,
                               img,
                               bigtiff=True,
                               photometric='minisblack',
                               # metadata={'axes': 'XYZ'}
                               )
    
    
    dt = time.time() - t0 
    return isSaved, filePath, dt

def save_2Dimage(img2D, rootPath, fileName, imgFormat='.tif'):
    # print()
    # print("Saving Image...")
    t0 = time.time()

    filePath = str(Path.joinpath(Path(rootPath), fileName + imgFormat))    
    # isSaved = cv2.imwrite(filePath, img2D)    #Slower (LZW Compression)
    isSaved = tifffile.imsave(filePath, img2D) #Faster
    
    dt = time.time() - t0 
    return isSaved, filePath, dt


def save_3Dimage(img3D, rootPath, fileName, imgFormat='.tif'):
    # print()
    # print("Saving Image...")
    t0 = time.time()

    filePath = str(Path.joinpath(Path(rootPath), fileName + imgFormat))    
    isSaved = tifffile.imsave(filePath, img3D) #Faster
    
    dt = time.time() - t0 
    return isSaved, filePath, dt

    
if __name__ == '__main__':
    from IO.Image.ImageReader import read_ImageStack, read_SlicefromStack, read_image
    from matplotlib import pyplot as plt
    import matplotlib.cm as cm
    
    pathFile_In = r'F:\Arias\ProcessedBrains\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan_UnChunked\2020-12-14_201244\raw\stack_0-x00-y00_channel_0_obj_left\Cam_Left_00000.lux.h5'
    pathFile_In = r'F:\Arias\ProcessedBrains\Real_18x6x2_UnChunked_bk\2021-02-03_165039\raw\stack_0-x00-y04_channel_1_obj_left\Cam_Left_00000.lux.h5'
    pathFile_In  = str(Path(pathFile_In))    
    z_In = 300

# =============================================================================
# 
# =============================================================================
    #Read
    # [imgStack, dt_read] = read_ImageStack(pathFile_In, z_range=None)
    [imgStack, dt_read] = read_ImageStack(pathFile_In, zRange=[3])
    nz = imgStack.shape[0]
    print()
    print('read :', dt_read)
    print('ratio:', dt_read/nz)
    
    #Write
    localPath = Path.cwd().parent.parent
    #Save SSD
    rootPath = Path.joinpath(localPath, 'Results') 
    #Save HDD
    rootPath = str(Path(r'F:\Arias\ProcessedBrains'))
    fileName = 'Test_tiff_img'
    [isSaved, filePath, dt_write] = save_3Dimage(imgStack, rootPath, fileName)
    print()
    # print(isSaved)
    # print(filePath)
    print('write:', dt_write)
    print('ratio:', dt_write/nz)
    

    #OP1: nz=1936
    # read : 34.5926570892334
    # ratio: 0.017868108000637085
    
    # write: 44.546151876449585
    # ratio: 0.02300937596924049
   
    #OP2: nz=1
    # read : 0.1687638759613037
    # ratio: 0.1687638759613037

    # write: 2.6946098804473877
    # ratio: 2.6946098804473877
# =============================================================================
#     
# =============================================================================
    # #Read
    # [img, dt_read] = read_SlicefromStack(pathFile_In, z_In)
    
    # #Write
    # localPath = Path.cwd().parent.parent
    # rootPath = Path.joinpath(localPath, 'Results')  
    # # rootPath = str(Path(r'F:\Arias\ProcessedBrains'))
    # fileName = 'Test_tiff_img'
    # [isSaved, filePath, dt] = save_2Dimage(img, rootPath, fileName)
    # print(isSaved)
    # print(filePath)
    # print(dt)
    
    # #Read to check how was saved
    # imgSaved = read_image(filePath)
    
    # fig, axs = plt.subplots(1,1)
    # axs.imshow(imgSaved, cmap=cm.Greys_r,  interpolation='nearest')
# =============================================================================
#     
# =============================================================================


    

    

# =============================================================================
# Draft
# =============================================================================

# def save_HDF5(img):    
    # # Write data to HDF5
    # with h5py.File(OutFilePath, "w") as data_file:
    #     # data_file.create_dataset("data", data=data)
    #     # data_file.create_dataset("data", data=data, chunks=(64, 64, 64))
    #     # data_file.create_dataset("data", data=data, chunks=True)
    #     data_file.create_dataset("data", data=data, chunks=(1, 2048, 2048))
    
# def save_Image(img, img_FilePath, img_Format='.tif'):
#     img_FilePath = str(img_FilePath.absolute()) + img_Format 
#     #img_FilePath = img_FilePath + img_Format 
#     print()
#     print("Saving Image...")
#     print("path to save:")
#     print(img_FilePath)
#     a = cv2.imwrite(img_FilePath, img)
#     return a  