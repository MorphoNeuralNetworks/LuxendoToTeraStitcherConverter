# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 01:12:23 2020

@author: aarias
"""
import numpy as np

import concurrent.futures
from tqdm import tqdm

import matplotlib
# matplotlib.use("Qt5Agg")
from matplotlib import pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')

# from IO.Files.FileWriter import save_Figure
# from IO.Files.FileManager import createFolder

import time
#==============================================================================
# Repeats
#==============================================================================
#        myArgs = [imgPaths, itertools.repeat([x0, x1, y0, y1], len(imgPaths))]
#        myArgs = [imgPaths, [[x0, x1, y0, y1] for i in range(len(imgPaths))]]
#==============================================================================
# 
#==============================================================================
def multithreading(func, args, workers):
    t0 = time.time()
    args = args.copy()
    nTasks = len(args[0])
    args.append([t0 for i in range(nTasks)])
    print (args)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # res = executor.map(func, *args)
        res = list(tqdm(executor.map(func, *args),total=nTasks))
    return list(res)


def multiprocessing(func, args, workers):
    t0 = time.time()
    args = args.copy()
    nTasks = len(args[0])
    args.append([t0 for i in range(nTasks)])
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        # res = executor.map(func, *args)
        res = list(tqdm(executor.map(func, *args),total=workers))
    return list(res)

#==============================================================================
# 
#==============================================================================
def parallelComputing(func, args, nProcesses=1, nThreads=1):
    # print('')
    # print('Launch Main Parallel')   
    t0 = time.time()
    args = args.copy()
    nTasks = len(args[0])
    args.append([t0 for i in range(nTasks)])
    
    m = []
    for i in args:
        m.append(np.array_split(i, nProcesses))
    args = list(zip(*m))
  
    func = [func for i in range(len(args))]
    nThreads = [nThreads for i in range(len(args))]
    
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=nProcesses) as executor:
    # with concurrent.futures.ThreadPoolExecutor(max_workers=nProcesses) as executor:        
        # res = executor.map(run_threads, func, args, nThreads) 
        res = list(tqdm(executor.map(run_threads, func, args, nThreads), total=nProcesses))
    return list(res)   
 

def run_threads(func, args, workers):
    # print('')
    # print('From Process Launch Threads: Start')
   
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        res = executor.map(func, *args) 
    return list(res)    
   
    
# =============================================================================
# 
# =============================================================================
def plot_ComputingPerformance(df, computation_labels=None, sortedBy='taskID', skipStart=True):
    
    # =============================================================================
    #   Select Plot Settings
    # =============================================================================
    
    #Selecting the ColorMap of the Operations Lables (ColorMaps Options: 'RdYlGn', 'hsv', 'Pastel1','Paired')
    category_names = np.unique(df['compID'])
    n_catergories = category_names.shape[0] 
    category_colors = plt.get_cmap('Paired')(np.linspace(0, 1, n_catergories))
    
    #if not given... Selecting the Operation Tags
    if (computation_labels==None) or (len(list(computation_labels))!=n_catergories):
        computation_labels = list(category_names)
    
    #Selecting sortedBy Options; "taskID" or "workerID" or "unknown"
    nTasks = np.unique(df['taskID']).shape[0]
    if (sortedBy=='taskID') or (sortedBy==None):
        print()
        print('plot_ComputingPerformance: sortedBy taskID')        
    elif (sortedBy=='workerID'): 
        print()
        print('plot_ComputingPerformance: sortedBy workerID')
        a = df['threadID']
        _, ix = np.unique(a, return_index=True)
        threadsID = a[np.sort(ix)]
      
        nWorkers = threadsID.shape[0]
        nTasks = nWorkers
        # Overwrite the taskIDs with the workerIDs
        for i in range(0, nWorkers):        
            maskBool = df['threadID']==threadsID.iloc[i]
            df['taskID'].loc[maskBool] = i + 1 
    else:
        print()
        print('plot_ComputingPerformance: sortedBy unknown')
          
    #Selecting the minimum "comnputing time" to be plotted in the bars as a string
    maskBool = df['width']>0    
    # dt_min = df['width'][maskBool].min()
    dt_min = df['width'][maskBool].mean()
      
    #Selecting the Figure Dimensions
    start = df['start'].min()
    stop = df['stop'].max()
    width = stop - start
    inches_per_second = 0.28
    inches_per_second = 0.5*(1/dt_min)    
    # fig, ax = plt.subplots(figsize=((width)*inches_per_second, nTasks*1)) 
    
    fig = Figure(figsize=((width)*inches_per_second, nTasks*1))
    ax = fig.add_subplot(111)
    # fig = self.ui.plotWidget.canvas.fig
    # fig.clf()
    # ax = fig.subplots(1,1)
    # =============================================================================
    #   Start Ploting the "Computing Performance" Graph     
    # =============================================================================    
    
    #Ploting Loop: each loop plots the bars of each operation
    for i, (colname, color) in enumerate(zip(computation_labels, category_colors)):
        #Plot the "Horizontal Bars" that represents the time that takes each operation
        dfSub = df[(df['compID']==category_names[i])]
        ycenters = np.asarray(dfSub['taskID'])
        starts = dfSub['start'] 
        widths = dfSub['width']   
        ax.barh(ycenters, widths, left=starts, height=0.5, align="center", label=str(colname), color=color, alpha= 0.75)

        #Plot the "texts" that represents the time that takes each operation
        xcenters = starts + widths / 2
        text_color = 'k'
        for j, (x, c) in enumerate(zip(xcenters, widths)):
            if c>=dt_min:
                myText = '{:0.3f}'.format(c)
                ax.text(x, ycenters[j], myText, ha='center', va='center',color=text_color)
        
    #Plot the "processID and threadID" above the horizontal bars
    for task in range(1, nTasks+1):           
        dfsub = df[(df['taskID']==task)]        
        process_ID = dfsub['processID'].iloc[0]
        thread_ID = dfsub['threadID'].iloc[0]
        myText = 'p_Id:' + '{:0.0f}'.format(process_ID) + ', t_Id:' + '{:0.0f}'.format(thread_ID)       
        x_left = dfsub['start'].min()
        ax.text(x_left, task + 0.30, myText, ha='left', va='bottom',color=text_color)
    
    #Plot the "Total Time" Horizontal Bar
    ycenter = 0.0
    colname = 'Total'    
    ax.barh(ycenter, width, left=start, height=0.5, align="center", label=colname, color='0.25', alpha=0.5)
    
    #Plot the "Total Time" text
    xcenter = start + width / 2
    myText = '{:0.3f}'.format(width) 
    ax.text(xcenter, ycenter, myText, ha='center', va='center',color=text_color)

    # =============================================================================
    #    Select Plot Lables 
    # =============================================================================
    
    #Legend Settings     
    ax.legend(loc='upper left',
              fontsize='small',
              bbox_to_anchor=(1.05, 1, 1., 0.),
              borderaxespad=0,              
              mode=None) #mode=None ,'expand'   
              
    #Axis Settings:    
    ax.set_yticks(np.arange(0, nTasks + 1)) 
    if skipStart==False:
        ax.set_xlim(0, ax.axes.get_xlim()[1])
    else:
        ax.set_xlim(start, ax.axes.get_xlim()[1])
        print()
        print('start', start)
    ax.set_ylim(-0.5, nTasks + 1) 
    ax.set_ylim(-0.5, nTasks + 1)   
    
    #Axis Labels:
    ax.set_ylabel(str(sortedBy)) 
    ax.set_xlabel('Time [seconds]')   
         
    return fig, ax


#==============================================================================
# Debugging Stuff
#==============================================================================
def mySum(a,b,t0):    
    start = time.time() - t0
    time.sleep(1.0)
    c = a + b
    stop = time.time() - t0
    return c, start, stop


def mySum5(a,b,t0): 
    print(a)
    print(b)
    print(t0)
    
    M1 = [[1, 2],[3,4]]
    M2 = [[1,2,3], [4,5,6],[7,8,9]]
    M = [M1, M2]
    
    return M
        
def mySum6(t0, *args):
    print (args)
    a, b, T0 = args
    M1 = [[1, 2],[3,4]]
    M2 = [[1,2,3], [4,5,6],[7,8,9]]
    M = [M1, M2]
    return M 
#==============================================================================
#     deprecated outdated obsolete
#==============================================================================
# def plot_TaskRunTimes(ax, start, stop, bar_color, label=None):       
#     widths   = stop - start
#     xcenters = start + widths/2.0  
#     ycenters = np.arange(1, len(start)+1)
#     ax.barh(ycenters, widths, left=start, color=bar_color, align='center', alpha=0.5, label=label)
#     for xcenter, ycenter, width in zip(xcenters, ycenters, widths):
#         ax.text(xcenter, ycenter, '{:0.2f}'.format(width), ha='center', va='center', color='k')
  
#     return stop[-1]-start[0]

if __name__== '__main__':
    # from matplotlib import pyplot as plt
    import itertools


    a = [1,2,3]
    b = [1,2]    
    args = [a,b]

    func = mySum
    a = list(itertools.chain.from_iterable(itertools.repeat(a, 2)))
    b = list(itertools.repeat(b, 3))
    args = [a,b]
      
    a = np.ones(10)
    b = 2*np.ones(10)
    args = [a,b]
    # n_Tasks = len(args[0])

    print()
    print(args)
    
    
    
    
    res0 = parallelComputing(func, args, nProcesses=2, nThreads=1)
    res = list(filter(None, res0))
    M = np.concatenate(res, axis=0)
    print(M)
    
    # res0 = filter(None, res0)  
    # M =  np.array(res0, dtype=object)    
    # M = np.concatenate(M, axis=0)
    # print(M)
#==============================================================================
# Debuguin
#==============================================================================
#    res = parallelComputing(mySum, args, nProcesses=4, nThreads=1)
#    res0 = parallelComputing(mySum5, args, nProcesses=2, nThreads=2)
#    res0 = parallelComputing(mySum, args, nProcesses=2, nThreads=2)
    # res0 = parallelComputing(mySum5, args, nProcesses=2, nThreads=1)
#    res0 = parallelComputing(mySum6, args, nProcesses=1, nThreads=1)
    # print()    
    # print(args)

    # res = multithreading(mySum5, args, workers=2)
    # print()
    # print(args)
    
    # res = multiprocessing(mySum5, args, workers=2)
    
#    print('')
#    print res0
    
    
    # res0 = filter(None, res0)  
    # M =  np.array(res0, dtype=object)    
    # M = np.concatenate(M, axis=0)
    
    # M1, M2 = M[:,0], M[:,1]
    
    # n1 = M1.shape[0]
    # M1 = np.concatenate(M1, axis=0)
    # M1 = M1.reshape(n1,-1)
    
    # n2 = M2.shape[0]
    # M2 = np.concatenate(M2, axis=0)
    
#    print('')
#    print res0
#    
#    print('')
#    print M1
#    print('')
#    print M1.shape
#    
#    print('')
#    print M2
#    print('')
#    print M2.shape
    
       
        