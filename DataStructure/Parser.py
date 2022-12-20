# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 21:34:43 2020

@author: aarias
"""
import numpy as np

# def parse_ScanMetada(xyz_scan_txt, channel_txt, ending_txt):
def parse_ScanMetada(dataStructure):
    
    #Unpack Dictionary
    ending_txt = dataStructure["ending"]
    channel_txt = dataStructure["channel"]
    tileX_txt = dataStructure["tileX"]
    tileY_txt = dataStructure["tileY"]
    sliceZ_txt = dataStructure["sliceZ"]
    
    #Parse DataStructure
    [myRoot, tileX, x_index] = parse_String(tileX_txt)
    [myRoot, tileY, y_index] = parse_String(tileY_txt)
    [myRoot, sliceZ, z_index] = parse_String(sliceZ_txt)
    [myRoot, channel, index] = parse_String(channel_txt)
    [myRoot, ending, index]  = parse_String(ending_txt)     
    xyz_index = np.array([x_index, y_index, z_index], dtype=object)
    
    # print()
    # print('x_index', x_index)
    # print('y_index', y_index)
    # print('z_index', z_index)
    # print('xyz_index', xyz_index)
    # jajaja
    
    #Pack Dictionary
    parsedStructure = {"parsed_ending": ending,
                      "parsed_channel": channel,
                      "parsed_coord": xyz_index,
                      }
    
    return parsedStructure
    # return  [xyz_index, channel, ending]

def parse_String(myStr):
    myStr  = myStr.split('_', 2)    
    myRoot = myStr[0]
    data = None
    index = None
    if len(myStr)==3:
        data  = myStr[2] 
        index = [int(myStr[1]), (int(myStr[1]) + len(data))]
    return [myRoot, data, index]

        
if __name__ == '__main__':
     ending = "File_0_Cam_Left_00000.h5"
     channel = "Folder_16_channel_0"
     scanX = "Folder_9_12" 
     scanY = "Folder_13_00" 
     scanZ = '_'
     # scanZ = None
# =============================================================================
#      
# =============================================================================
     
     print (parse_String(scanX))
     [myRoot, data, index] = parse_String(scanX)
     myName = 'stack_0-x12-y00_channel_0'
     print(myName[index[0]:index[1]])
     
     
     a ='dfgdfgd'.split('_', 2)
     b = 'Folder_13_00'.split('_', 2)
     c = "File_0_Cam_Left_00000.h5".split('_', 2)
     print (parse_String(scanZ))
      
     
##     myName[x_index[0]:x_index[-1]]
#     v = list(np.arange(4))
#     myName[1:2]
     
