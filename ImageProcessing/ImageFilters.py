# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 18:55:26 2021

@author: aarias
"""
import numpy as np

def get_DoG(s, rS=1.1, rV=1.0, a=1.0):
    
    #Get Dimensions
    dim = len(s)

    
    #1D-DoG
    if dim==1:
        #Unpaking the Parameters
        rx = s[0]
        
        #Variable Change: control the Spatial Scale of the DoG with r_cross
        sx = np.sqrt(rx**2*((rS**2 - 1)/(rS**2))*(1.0/(a*np.log(rS/rV))))
        s = [sx]
        
        #Discretization
        smax =np.max(s)
        Tr = int(np.ceil(3.0*smax*rS))
        n = 1 + 2*Tr
        r = np.linspace(-Tr, +Tr, n)
        xx = r
    
        #Difference of a Gaussian (DoG)
        Gc = rS*np.exp(-(xx**2)/(a*sx**2))
        Gs = rV*np.exp(-(xx**2)/(a*sx**2*rS**2))
        
        #Normalization
        A = (a*np.pi*sx**2*rS**2)**(1.0/2.0)
        B = ((1.0/rV)*(1.0/rS**2))**(1.0/(rS**2 - 1)) - rV*((1.0/rV)*(1.0/rS**2))**(rS**2/(rS**2 - 1))
        K_norm = 1.0/(A*B)
        DoG = K_norm*(Gc-Gs)
 
    #2D-DoG
    elif dim==2:
        #Unpaking the Parameters
        rx, ry = s
        
        #Variable Change: control the Spatial Scale of the DoG with r_cross
        sx = np.sqrt(rx**2*((rS**2 - 1)/(rS**2))*(1.0/(a*np.log(rS**2/rV))))
        sy = np.sqrt(ry**2*((rS**2 - 1)/(rS**2))*(1.0/(a*np.log(rS**2/rV))))
        s = [sx, sy]
        
        #Discretization
        smax =np.max(s)
        Tr = int(np.ceil(3.0*smax*rS))
        n = 1 + 2*Tr
        r = np.linspace(-Tr, +Tr, n)
        [xx, yy] = np.meshgrid(r, r) 
    
        #Difference of a Gaussian (DoG)
        Gc = rS**2*np.exp(-( (xx**2)/(a*sx**2)       + (yy**2)/(a*sy**2) ) )
        Gs = rV*np.exp(-( (xx**2)/(a*sx**2*rS**2) + (yy**2)/(a*sy**2*rS**2) ) )
        
        #Normalization
        A = ((a*np.pi*sx**2*rS**2)**(1.0/2.0)) * ((a*np.pi*sy**2*rS**2)**(1.0/2.0))
        B = ((1.0/rV)*(1.0/rS**2))**(1.0/(rS**2 - 1)) - rV*((1.0/rV)*(1.0/rS**2))**(rS**2/(rS**2 - 1))
        K_norm = 1.0/(A*B)
        print()
        DoG = K_norm*(Gc-Gs)
        
    #3D-DoG
    elif dim==3:
        #Unpaking the Parameters
        rx, ry, rz = s
        
        #Variable Change: control the Spatial Scale of the DoG with r_cross
        sx = np.sqrt(rx**2*((rS**2 - 1)/(rS**2))*(1.0/(a*np.log(rS**3/rV))))
        sy = np.sqrt(ry**2*((rS**2 - 1)/(rS**2))*(1.0/(a*np.log(rS**3/rV))))
        sz = np.sqrt(rz**2*((rS**2 - 1)/(rS**2))*(1.0/(a*np.log(rS**3/rV))))
        s = [sx, sy, sz]
        
        #Discretization
        smax =np.max(s)
        Tr = int(np.ceil(3.0*smax*rS))
        n = 1 + 2*Tr
        r = np.linspace(-Tr, +Tr, n)
        [xx, yy, zz] = np.meshgrid(r, r, r) 
    
        #Difference of a Gaussian (DoG)
        Gc = rS**3*np.exp(-( (xx**2)/(a*sx**2) + (yy**2)/(a*sy**2) + (zz**2)/(a*sz**2)) )
        Gs = rV*np.exp(-( (xx**2)/(a*sx**2*rS**2) + (yy**2)/(a*sy**2*rS**2) + (zz**2)/(a*sz**2*rS**2) ) )
        
        #Normalization
        A = ((a*np.pi*sx**2*rS**2)**(1.0/2.0)) * ((a*np.pi*sy**2*rS**2)**(1.0/2.0)) * ((a*np.pi*sz**2*rS**2)**(1.0/2.0))
        B = ((1.0/rV)*(1.0/rS**2))**(1.0/(rS**2 - 1)) - rV*((1.0/rV)*(1.0/rS**2))**(rS**2/(rS**2 - 1))
        K_norm = 1.0/(A*B)
        DoG = K_norm*(Gc-Gs)
        
    return DoG
if __name__ == '__main__':
    
    s = [34, 34]
    DoG_2D = get_DoG(s, rS=1.1, rV=1.0, a=1.0)
    DoG_2D.shape
