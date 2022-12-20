# -*- coding: utf-8 -*-
"""
Created on Fri May 22 18:43:54 2020

@author: pc
"""
import os
# import sys

# import pandas as pd
# import numpy as np


def save_CSV(df, folderPath, fileName):
    
    #Create Folder
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)  
    
    #Saving the Table
    fileExtension = '.csv'
    filePath = os.path.join(folderPath, fileName + fileExtension)  
    df.to_csv(filePath, sep=',', encoding='utf-8', index=True)  #sep=,
    
if __name__== '__main__':
    pass




















