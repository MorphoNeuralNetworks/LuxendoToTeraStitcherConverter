# -*- coding: utf-8 -*-
"""
Created on Fri May 22 18:43:54 2020

@author: pc
"""
import os
import time
import stat
 
import shutil
from pathlib import Path

# def createFolder(path, remove=True):
#     #If the Path already exist remove all the content
#     #If the Path not exist create Folder  
# #    path  = Path(path)
#     print(path)
#     if os.path.exists(path) & remove==True: 
#         print('Remove Folder Content...')
#         # shutil.rmtree(path)
#         rmtree(path)
# #        time.sleep(5.0)
        
#     #This dealy is required to avoid the following Error
#     #PermissionError: [WinError 5] Access is denied
#     #It seems that the OS requires time to finish the above operation
# #    time.sleep(0.000000001)
#     time.sleep(0.00001)
    
#     if not os.path.exists(path):
#         print('Create Folder...')
#         os.makedirs(path)

def createFolder(pathFolder, remove=True, verbose=False):
    if verbose:
        print()
        print('Creating a Folder...')
    
    pathFolder = Path(pathFolder)
    if verbose:
        print('pathFolder: \n', pathFolder)

    if (pathFolder.exists()==True):
        if verbose:
            print("The Folder is already there")
        if (remove==True):
            if verbose:
                print("Deleting recursively the old Folder...")
            shutil.rmtree(str(pathFolder))
            
            if verbose:
                print('Creating anew the Folder...')
            pathFolder.mkdir(parents=True, exist_ok=False)
        else:
            if verbose:
                print("Keeping the content of Folder")
            pass
           
    else:
        pathFolder.mkdir(parents=True, exist_ok=False)


def removeFolder(pathFolder):
    print()
    print('Removing a Folder...')
    
    pathFolder = Path(pathFolder)
    if (pathFolder.exists()==True):
        print("The Folder is already there")
        print("Deleting recursively the old Folder...")
        shutil.rmtree(str(pathFolder)) 
    else:
        print("The Folder does not exist")
        

    # # Create Folder 
    # try:
    #     print()
    #     print('Creating Folder...')
    #     pathFolder.mkdir(parents=True, exist_ok=False)
    # except FileExistsError:
    #     print("Folder is already there")
    # else:
    #     print("Folder was successfully created")

#Custumize Shutil.rmtree
# def rmtree(top):
#     for root, dirs, files in os.walk(top, topdown=False):
#         for name in files:
#             filename = os.path.join(root, name)
#             os.chmod(filename, stat.S_IWUSR)
#             os.remove(filename)
#         for name in dirs:
#             os.rmdir(os.path.join(root, name))
#     os.rmdir(top) 
    
    
if __name__== '__main__':
    pass

    # rootPath = Path.cwd()
    # folderName = "Settings"
    # fileName   = "GUI_Settings.json"    
    # pathFolder = Path.joinpath(rootPath, folderName)
    # print()
    # print(str(pathFolder))
    # createFolder(str(pathFolder), remove=False)
    # Path('asd')
    # Path(None)
    # is



















