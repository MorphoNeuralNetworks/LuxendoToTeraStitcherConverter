# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 14:56:22 2020

@author: aarias
"""

#Libraries: Maths 
import numpy as np

#Libraries: Time
import time 

#Libraries: Parallel Computing
import concurrent.futures

#Libraries: Iterator Algebra
import itertools

#Libraries: Ploting
import matplotlib.cm as cm
# Ensure using PyQt5 backend
#matplotlib.use('QT5Agg')

#Libraries: Custom
from IO.Image.ImageReader import read_ImageStack

def concatenate_imgScan(M_FilePaths, isParallel=False):

    if not isParallel:
        img, dt = concatenate_imgScan_Sequential(M_FilePaths)
    else:
        img, dt = concatenate_imgScan_Parallel(M_FilePaths)
    
    return img, dt 

def concatenate_imgScan_Sequential(M_FilePaths):
    t0 = time.time()    
    ny, nx = M_FilePaths.shape
    imgRows = np.zeros(ny, dtype=object) 
    imgRow = np.zeros(nx, dtype=object) 
    for i in range(ny):
        for j in range(nx):
            # imgRow[j] = read_image(M_FilePaths[i, j]) 
            imgRow[j] = read_ImageStack(M_FilePaths[i, j]) 
        imgRows[i] = np.concatenate(imgRow, axis=1)    
        
    img = np.concatenate(imgRows, axis=0) 
    dt = time.time() - t0 
    return img, dt     
    
def concatenate_imgScan_Parallel(M_FilePaths):         
    t0 = time.time()
    ny, nx = M_FilePaths.shape
    # print()
    # print('ny, nx', ny, nx)
    v_FilePaths = M_FilePaths.flatten()
    imgRowPaths = chunks(v_FilePaths, nx)     
    with concurrent.futures.ThreadPoolExecutor() as executor:
        p = executor.map(merge_YacrossX,
                         imgRowPaths,
                         itertools.repeat(nx, ny),
                         ) 
        imgRows = np.zeros(ny, dtype=object)
        k = 0
        for imgRow in p:            
            imgRows[k] = imgRow
            k = k + 1
        # img = np.concatenate(imgRows, axis=0) 
        img = np.concatenate(imgRows, axis=1) 
    dt = time.time() - t0   
    return img, dt 

def chunks(lst, n):   
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def merge_YacrossX(imgRowPath, nx):
    imgRow = np.zeros(nx, dtype=object)
    # print()
    # print("imgRowPath", imgRowPath)
    for j in  range(nx):
        # imgRow[j] = read_image(imgRowPath[j]) 
        [imgRow[j], dt]  = read_ImageStack(imgRowPath[j]) 
        # print(imgRow[j].shape)

    # print('before:', imgRow.shape)
    # imgRowMerged = np.concatenate(imgRow, axis=1)
    imgRowMerged = np.concatenate(imgRow, axis=2)
    # print('after:', imgRow.shape)
    return imgRowMerged

# =============================================================================
# 
# =============================================================================
    # rows = np.zeros(2, dtype=object)  
    # a = np.ones([1,2, 2])
    # b = np.zeros([1,2, 2])
    # rows[0] = np.ones([1, 2, 2])
    # rows[1] = np.zeros([1,2, 2])
    # r0 = np.concatenate(rows, axis=0)
    # r1 = np.concatenate(rows, axis=1)
    # r2 = np.concatenate(rows, axis=2)
    # print()
    # print(r0)
    # print(r0.shape)
    # print()
    # print(r1)
    # print(r1.shape)
    # print()
    # print(r2)
    # print(r2.shape)
  
    
# =============================================================================
# 
# =============================================================================

def plot_imgConcatenated(ax, img, nx_Tiles, ny_Tiles, img_nx, img_ny, overlap):
    overlap = overlap/100.0
#    ax.imshow(img, cmap= cm.Greys_r) 
    print('img.shape', img.shape)
    img = np.squeeze(img)
    print('img.shape', img.shape)
    if type(img[0,0])==np.uint8:
        print ('uint8')
        ax.imshow(img, cmap= cm.Greys_r, vmin=0, vmax=2**8-1) 
    if type(img[0,0])==np.uint16:
        print ('uint16')
        ax.imshow(img, cmap= cm.Greys_r, vmin=0, vmax=2**16-1) 
    
    vx = np.arange(0, nx_Tiles*img_nx, img_nx)
    vx0 = np.arange(overlap*img_nx, nx_Tiles*img_nx, img_nx)
    vx1 = np.arange((1-overlap)*img_nx, nx_Tiles*img_nx, img_nx)
    
    vy = np.arange(0, ny_Tiles*img_ny, img_ny)
    vy0 = np.arange(overlap*img_nx, ny_Tiles*img_ny, img_ny)
    vy1 = np.arange((1-overlap)*img_nx, ny_Tiles*img_ny, img_ny)
    for i in range(0,ny_Tiles):
        ax.hlines(y=vy[i],  xmin=0, xmax=nx_Tiles*img_nx, linestyle = '-', linewidth=2, color='g')
        ax.hlines(y=vy0[i], xmin=0, xmax=nx_Tiles*img_nx, linestyle = ':', linewidth=2, color='r', alpha=0.4)
        ax.hlines(y=vy1[i], xmin=0, xmax=nx_Tiles*img_nx, linestyle = ':', linewidth=2, color='r', alpha=0.4)
    for j in range(0,nx_Tiles):
        ax.vlines(x=vx[j],  ymin=0, ymax=ny_Tiles*img_ny, linestyle = '-', linewidth=2, color='g')
        ax.vlines(x=vx0[j], ymin=0, ymax=ny_Tiles*img_ny, linestyle = ':', linewidth=2, color='r', alpha=0.4)
        ax.vlines(x=vx1[j], ymin=0, ymax=ny_Tiles*img_ny, linestyle = ':', linewidth=2, color='r', alpha=0.4)
    
    ax.set_xlim([0, nx_Tiles*img_nx])
    ax.set_ylim([ny_Tiles*img_ny, 0])
    
    
if __name__ == '__main__':
    pass






