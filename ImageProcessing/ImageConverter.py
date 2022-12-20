# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 14:47:33 2020

@author: aarias
"""

import numpy as np
#Libraries: Time
import time 
import sys
import os

# import cv2
from skimage.exposure import equalize_adapthist
from skimage import img_as_uint

from ImageProcessing.ImageFilters import get_DoG
from scipy import signal

#Libraries: Ploting 
from matplotlib import pyplot as plt
import matplotlib.cm as cm

# import skimage
# print(skimage.__version__) #'0.16.2'



def process_Image(img, imgOperation='None'):    
    t0 = time.time()
    if imgOperation=='None':
        pass
    elif imgOperation=='img16to8_Linear':
        img = img16to8_Linear(img)
    elif imgOperation=='img16to8_Linear_Crop5to12':
        img = img16to8_Linear_Crop5to12(img)
    elif imgOperation=='img16to8_Linear_CropMinMax':
        img = img16to8_Linear_CropMinMax(img)
    elif imgOperation=='img16to8_HistEq':
        img = img16to8_HistEq(img)
    elif imgOperation=='img16to8_CLAHE':
        img = img16to8_CLAHE(img, clip_limit=0.01, nbins=2**8) #clip_limit=0.01 (default)
    elif imgOperation=='wait_1sec':
        time.sleep(1)
    else:
        print()
        print('process_Image: Operation is unknown')
        print("imgOperation: ", imgOperation)
        
    dt = time.time() - t0
    return [img, dt]


def img16to8_Linear(img):
    img = LinearConvert_16bitTo8bit(img, x_min=0, x_max=2**16-1)
    return img

def img16to8_Linear_Crop5to12(img):
    img = LinearConvert_16bitTo8bit(img, x_min=2**5-1, x_max=2**12-1)
    return img

def img16to8_Linear_CropMinMax(img):
    img = LinearConvert_16bitTo8bit(img, x_min=img.min(), x_max=img.max())
    return img

def img16to8_HistEq(img):
    InBitDepth = 16
    OutBitDepth = 8                
    hist,bins = np.histogram(img.flatten(),2**InBitDepth,[0,2**InBitDepth]) 
    cdf = hist.cumsum()  
    cdf_m = np.ma.masked_equal(cdf,0)
    cdf_m = (cdf_m - cdf_m.min())*(2**OutBitDepth-1)/(cdf_m.max()-cdf_m.min())
    cdf2 = np.ma.filled(cdf_m,0)
    img = cdf2[img]
    img = np.uint8(np.round(img)) 
    return img

#CLAHE: Contrast Limited Adaptive Histogram Equalization
def img16to8_CLAHE(img, clip_limit=0.01, nbins=2**8):

    
    if (len(img.shape)==2):
        img = equalize_adapthist(img, clip_limit=clip_limit, nbins=nbins) 

    elif (len(img.shape)==3):
        imgAux = np.zeros(img.shape)
        for k in range(0, img.shape[0]):
            imgAux[k,:,:] = equalize_adapthist(img[k,:,:], clip_limit=clip_limit, nbins=nbins)   
        img = imgAux
    else:
        print()
        print('img16to8_CLAHE: Unkown image dimension')
          
    #Convetion: float to unint 16bit
    img = img_as_uint(img) 
    
    #Convertion: 16bit to 8bit
    img = img16to8_Linear(img)
    return img

def LinearConvert_16bitTo8bit(x, x_min=0, x_max=2**16 - 1):     
    #Substract Background
    # x = x - x.mean()
    #x = x - x.min()
    # x = (x - 150)
    # s = [30, 30]
    # F_DoG_2D = get_DoG(s, rS=1.1, rV=1.0, a=1.0)
    # x = signal.convolve(x, F_DoG_2D, "same")
    
    #Masking Saturation 
    x[x<x_min] = x_min
    x[x>x_max] = x_max
    

    x_min = float(x_min)
    x_max = float(x_max)
    
    y_min = 0.0
    y_max = float(2**8 - 1)
    
    y = (x - x_min)*((y_max - y_min)/(x_max - x_min)) + y_min
    y = np.uint8(np.round(y))
    return y 

#def img16to8_Linear(img):
#time= 0.5670566558837891
    
#def img16to8_Linear_Crop5to12(img):
#time= 0.5220522880554199 

#def img16to8_Linear_CropMinMax(img):
#time= 0.5740571022033691

#def img16to8_HistEq(img):   
#time= 0.7000701427459717
    
#def CLAHE(img, clip_limit=0.01, nbins=2**8):
#time= 1.9421942234039307         
if __name__ == '__main__':

    from pathlib import Path
    from IO.Image.ImageReader import read_ImageStack, read_SlicefromStack
    
    from matplotlib import pyplot as plt
    import matplotlib.cm as cm  
# =============================================================================
# 
# =============================================================================
    pathFile_In = r"F:\Arias\Brains\SPIM_MuVi\SPIM_MuVi_Scans\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan\2020-12-14_201244\raw\stack_0-x07-y03_channel_0_obj_left\Cam_Left_00000.lux.h5"
    # pathFile_In = r'C:\Users\aarias\MySpyderProjects\p1_11_DataStructureConverter\Results\Ref_1800_34583_SPIM_MuVi_Line_ACF_Scan_UnChunked_TeraStitcher\000000\000000_000000\019500_019500.tif'
    pathFile_In  = str(Path(pathFile_In))
    
    # Path(pathFile_In).suffix
    
    # [imgStack, dt] = read_ImageStack(pathFile_In)
    [imgStack, dt] = read_ImageStack(pathFile_In, zRange=[0,10])
    print()
    print(imgStack.shape)
    imgStack = imgStack[0:2,:,:]
    # imgStack = imgStack[0:1,:,:]
    # imgStack = imgStack[0,:,:]
    print(imgStack.shape)
    
    [img, dt] = process_Image(imgStack, imgOperation='img16to8_CLAHE')
    print(img.shape)

    # img[0,:,:] = equalize_adapthist(img[0,:,:]) 
    # plt.imshow(imgStack,  cm.Greys_r, interpolation='nearest') 
    # plt.show()
    
    # plt.imshow(img,  cm.Greys_r, interpolation='nearest') 
    # plt.show()

    # plt.imshow(img[1,:,:],  cm.Greys_r, interpolation='nearest') 
    # plt.show()
    
    # plt.imshow(img[0,:,:],  cm.Greys_r, interpolation='nearest') 
    # plt.show()
    
    # [img, dt] = process_Image(imgStack, imgOperation='img16to8_Linear_Crop5to12')
    # [img, dt] = process_Image(imgStack, imgOperation='img16to8_HistEq')
# =============================================================================
# 
# =============================================================================

    # from skimage import exposure, util
    
    
    # Prepare data and apply histogram equalization
    
    # from skimage.data import cells3d
    
    # im_orig = util.img_as_float(cells3d()[:, 1, :, :])  # grab just the nuclei
    # im_orig = 0.1*np.ones([256, 256, 256])
    
    # # Reorder axis order from (z, y, x) to (x, y, z)
    # im_orig = im_orig.transpose()
    
    # # Rescale image data to range [0, 1]
    # im_orig = np.clip(im_orig,
    #                   np.percentile(im_orig, 5),
    #                   np.percentile(im_orig, 95))
    # im_orig = (im_orig - im_orig.min()) / (1 + im_orig.max() - im_orig.min())
    
    # # Degrade image by applying exponential intensity decay along x
    # sigmoid = np.exp(-3 * np.linspace(0, 1, im_orig.shape[0]))
    # im_degraded = (im_orig.T * sigmoid).T
    
    # Set parameters for AHE
    # Determine kernel sizes in each dim relative to image shape
    # kernel_size = (im_orig.shape[0] // 5,
    #                im_orig.shape[1] // 5,
    #                im_orig.shape[2] // 5)
    # kernel_size = np.array(kernel_size)
    # clip_limit = 0.9
    # exposure.equalize_adapthist(im_orig, kernel_size=kernel_size, clip_limit=clip_limit)
    # exposure.equalize_adapthist(im_orig)
    
    # # Perform histogram equalization
    # im_orig_he, im_degraded_he = \
    #     [exposure.equalize_hist(im)
    #      for im in [im_orig, im_degraded]]
    
    # im_orig_ahe, im_degraded_ahe = \
    #     [exposure.equalize_adapthist(im,
    #                                  kernel_size=kernel_size,
    #                                  clip_limit=clip_limit)
    #      for im in [im_orig, im_degraded]]


# Define functions to help plot the data




# =============================================================================
# 
# =============================================================================
# # Perform histogram equalization
#     im_orig_he, im_degraded_he = [exposure.equalize_hist(im)
#      for im in [im_orig, im_degraded]]

#     im_orig_ahe, im_degraded_ahe =
#     [exposure.equalize_adapthist(im, kernel_size=kernel_size, clip_limit=clip_limit) for im in [im_orig, im_degraded]]


# =============================================================================
#    Path 
# =============================================================================
    
    # LocalRootFolder = Path(os.path.dirname(sys.argv[0]))
    # LocalRootFolder = str(LocalRootFolder.parent)
    # myPath = os.path.join(LocalRootFolder,  'Temp_Tests', 'test_h5_tiff0000.tif')
    # myPath = os.path.join(LocalRootFolder,  'Temp_Tests', 'test_h5_tiff0717.tif')
        
 
# =============================================================================
#     In
# =============================================================================
    # imgIn = cv2.imread(myPath, -1)
    # print('')
    # print('BitDepth=', type(imgIn[0,0])) 
    # print('min=', imgIn.min(), ', max=', imgIn.max())
# =============================================================================
#     Out
# =============================================================================
    # t0 = time.time()
    # imgOut = process_Image(imgIn, imgOperation='img16to8_Linear_CropMinMax')
    # dt = time.time() - t0 
    
     
    # print('')
    # print('time=', dt)
    # print('')
    # print('BitDepth=', type(imgOut[0,0])) 
    # print('min=', imgOut.min(), ', max=', imgOut.max())
    # jajja
# =============================================================================
#    Ref: 16to8bit linear
    
# =============================================================================
#    imgRef = img16to8_Linear(imgIn)
#    imgRef = img16to8_Linear_Crop5to12(imgIn)
#    imgRef = img16to8_Linear_CropMinMax(imgIn)
#    imgRef = img16to8_HistEq(imgIn)
#    imgRef = img16to8_CLAHE(imgIn, clip_limit=0.01, nbins=2**8)
    # imgRef = process_Image(imgIn, imgOperation='img16to8_CLAHE')
    
# =============================================================================
#     
# =============================================================================
    # [ny, nx] = 1,2
    # fig, axs = plt.subplots(ny,nx)
    # myFigScale = 0.40
    # fig.set_size_inches(nx*myFigScale*10.5, ny*myFigScale*10.5, forward=True)
    # axs[0].imshow(imgRef, cmap= cm.Greys_r, vmin=0, vmax=255) 
    # axs[1].imshow(imgOut, cmap= cm.Greys_r, vmin=0, vmax=255)
    # plt.show()


# =============================================================================
# 
# =============================================================================
    # [ny, nx] = imgRef.shape
    # [y0, x0] = int(ny/2), int(ny/2)
    # [dx, dy] = 100, 100
    
    # imgOutCrop = imgOut[y0-dy:y0+dy, x0-dx:x0+dx]
    # imgRefCrop = imgRef[y0-dy:y0+dy, x0-dx:x0+dx]
# =============================================================================
#     
# =============================================================================
    # [ny, nx] = 1,2
    # fig, axs = plt.subplots(ny,nx)
    # myFigScale = 0.40
    # fig.set_size_inches(nx*myFigScale*10.5, ny*myFigScale*10.5, forward=True)
    # axs[0].imshow(imgRefCrop, cmap= cm.Greys_r, vmin=0, vmax=255) 
    # axs[1].imshow(imgOutCrop, cmap= cm.Greys_r, vmin=0, vmax=255)
    # plt.show()








##    image, kernel_size=None, clip_limit=0.01, 
#    img = equalize_adapthist(imgIn, clip_limit=0.01)    
#    imga = equalize_adapthist(imgIn, clip_limit=0.01, nbins=2**8) 
#    print (imga[imga==imga[0,0]].shape)
#    imgb = equalize_adapthist(imgIn, clip_limit=0.01, nbins=2**16)
#    print (imgb[imgb==imgb[0,0]].shape)
#    img = img_as_uint(img)  
#    img = img16to8_Linear(img)
    
#    a = np.asarray([0,10,20,30,40])
#    b = np.asarray([0, 1, 2, 3, 4])
#    a[b]
              

# =============================================================================
#     
# =============================================================================
#                #Conversion
#                #Op0:
#                if conversion_16to8bit=="16to8bit_Linear_0bit_16bit":                 
#                    img = LinearConvert_16bitTo8bit(img, x_min=0, x_max=2**16-1)
#                
#                #Op1:
#                if conversion_16to8bit=="16to8bit_LinearCrop_5bit_12bit":  
#                    img = LinearConvert_16bitTo8bit(img, x_min=2**5-1, x_max=2**12-1)
#                
#                #Op2:
#                if conversion_16to8bit=="16to8bit_LinearCrop_Min_Max": 
#                    img = LinearConvert_16bitTo8bit(img, x_min=img.min(), x_max=img.max())
#                
#                #Op3
#                if conversion_16to8bit=="16to8bit_HistEq": 
#                    InBitDepth = 16
#                    OutBitDepth = 8                
#                    hist,bins = np.histogram(img.flatten(),2**InBitDepth,[0,2**InBitDepth]) 
#                    cdf = hist.cumsum()                 
#                    cdf_m = np.ma.masked_equal(cdf,0)
#                    cdf_m = (cdf_m - cdf_m.min())*(2**OutBitDepth-1)/(cdf_m.max()-cdf_m.min())
#                    cdf2 = np.ma.filled(cdf_m,0)
#                    img = cdf2[img]
#                    img = np.uint8(np.round(img))
##       
#                #Op4
#                if conversion_16to8bit=="16to8bit_HistEq_Local": 
#                    img = exposure.equalize_adapthist(img, clip_limit=0.01)    
#                    img = skimage.img_as_uint(img)  
#                    img = LinearConvert_16bitTo8bit(img, x_min=0, x_max=2**16-1)    
#def convert_img16to8(img):         
##    global img16to8bit_Type 
##    time.sleep(1) 
##    img = img16to8_Linear(img)
##    img = img16to8_Linear_Crop5to12(img)
##    img = img16to8_Linear_CropMinMax(img)
##    img = img16to8_HistEq(img)
##    img = CLAHE(img, clip_limit=0.01, nbins=2**8)
#    return img
#None
#img16to8_Linear
#img16to8_Linear_Crop5to12
#img16to8_Linear_CropMinMax
#img16to8_HistEq
#img16to8_CLAHE
#wait_1sec    