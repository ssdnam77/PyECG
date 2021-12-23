# -*- coding: utf-8 -*-
"""

Berger R.D, Akselrod S, Gordon D and Cohen R. J. An Efficient Algorithm for 
Spectral Analysis of Heart Rate Variability. IEEE Transactions on Biomedical 
Engineering, 33(9), 1986.

"""

import numpy as np 


def resample_berger(rr, fs = 4):    
    
    n = rr.__len__()
    
    totalT = int(np.ceil(rr[-1] * fs) + 1)
    
    rt = np.linspace(0, totalT, totalT, endpoint=False) / fs
    
    rrv = np.zeros(totalT)
    
    x = int(0)
    
    for i in range (1, totalT - 1):
        top  = rt[i + 1]
        bot  = rt[i - 1]
        
        wsiz = 2/fs
        
        if rr[x] < top:
            x = x + 1
        
        if x == n:
            break
        
        if rr[x - 1] <= bot:
            rrv[i] = wsiz / (rr[x] - rr[x - 1])
        else:
            rrv[i] = (rr[x -  1] - bot)/(rr[x - 1] - rr[x - 2]) + \
                     (top - rr[x - 1])/(rr[x] - rr[x - 1]) 
    
    return rt, rrv
        
    
