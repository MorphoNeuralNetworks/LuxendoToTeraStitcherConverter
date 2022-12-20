# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 11:59:41 2021

@author: aarias
"""




from pathlib import Path

def save_Figure(fig, folderPath, fileName, verbose=False):
    #Saving the Matplotlib Figure
    graph_dpi = 150
    fileExtension = '.png'
    filePath = Path.joinpath(folderPath, fileName + fileExtension)
    
    if verbose:
        print()
        print('Saving Plot...')
        print(filePath)
    try:
        fig.savefig(filePath, dpi=graph_dpi, bbox_inches='tight')
    except:
        print()
        print("save_Figure: An exception occurred")
        