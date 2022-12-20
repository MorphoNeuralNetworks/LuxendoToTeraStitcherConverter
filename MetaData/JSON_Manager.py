# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 17:23:03 2021

@author: aarias
"""


import json
from  pathlib import Path
from IO.Files.FileManager import createFolder
import numpy as np

# =============================================================================
# 
# =============================================================================
def save_JSON(pathFile, data):    
    pathFile = str(Path(pathFile))
    #Save Json
    with open(pathFile, "w") as write_file: 
         # json.dump(data, write_file)
         json.dump(data, write_file, indent=1, separators=(", ", ": "), sort_keys=False)
         
def read_JSON(pathFile): 
    pathFile = str(Path(pathFile))
    # Load Json
    with open(pathFile, "r") as read_file: 
        data = json.load(read_file)
    return data

# =============================================================================
#     
# =============================================================================

def read_Config(pathFile, verbose=False): 
    if verbose:
        print()
        print('START: readJSON_Config()...')
    
    # Load Json
    data = read_JSON(pathFile)
    if verbose:
        print()
        print('data: \n:', data)

    # DataStructure
    parse_ending = str(Path(data["DataStructure"]["ending"])) 
    parse_channel = str(Path(data["DataStructure"]["channel"]))     
    parse_tileX = str(data["DataStructure"]["tileX"])
    parse_tileY = str(data["DataStructure"]["tileY"])
    parse_sliceZ = str(data["DataStructure"]["sliceZ"])
    dataStructure = {"ending": parse_ending,
                     "channel": parse_channel,
                     "tileX": parse_tileX,
                     "tileY": parse_tileY,
                     "sliceZ": parse_sliceZ}
    
    # Scan
    scan_Overlap = float(data["Scan"]["overlap"])
    
    scan_DeltaX = float(data["Scan"]["delta"]["x"])
    scan_DeltaY = float(data["Scan"]["delta"]["y"])
    scan_DeltaZ = float(data["Scan"]["delta"]["z"])
    scan_Delta = np.array([scan_DeltaX, scan_DeltaY, scan_DeltaZ])
    
    scan_FlipX = bool(data["Scan"]["imageFlip"]["x"]) 
    scan_FlipY = bool(data["Scan"]["imageFlip"]["y"]) 
    scan_FlipZ = bool(data["Scan"]["imageFlip"]["z"]) 
    scan_Flip = np.array([scan_FlipX, scan_FlipY, scan_FlipZ])
    
    scan_AxisX = int(data["Scan"]["imageAxes"]["x"]) 
    scan_AxisY = int(data["Scan"]["imageAxes"]["y"]) 
    scan_AxisZ = int(data["Scan"]["imageAxes"]["z"]) 
    scan_Axes = np.array([scan_AxisX, scan_AxisY, scan_AxisZ])
    
        
    # Camera
    cameraPixelSize = float(data["Camera"]["pixelSize"])
    
    # Optics
    opticsMagnification = float(data["Optics"]["magnification"]) 
    

    # Pack Parameters in a Dictionary
    config = {"dataStructure": dataStructure,
            "scan_Overlap": scan_Overlap, 
            "scan_Delta": scan_Delta,
            "scan_Flip": scan_Flip,
            "scan_Axes": scan_Axes,
            "cameraPixelSize": cameraPixelSize,
            "opticsMagnification": opticsMagnification          
            }
    
    if verbose:
        print()
        print('STOP: readJSON_Config()...')
    return config



# =============================================================================
#      
# =============================================================================
if __name__== '__main__':
    # 2) Parameter: pathFile_Config
      
    rootPath = (Path.cwd()).parent
    folderName = "example"
    subfolderName = "config"
    fileName = "config.json"
    pathFile_Config = Path.joinpath(rootPath, folderName, subfolderName, fileName)    
    
    config = readJSON_Config(pathFile_Config)
    
    print()
    print('config: \n:', config)
    


# =============================================================================
# 
# =============================================================================
    # parse = np.array([parse_ending,
    #                   parse_channel,
    #                   parse_scanX, parse_scanY, parse_scanZ])

