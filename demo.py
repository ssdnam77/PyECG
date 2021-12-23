#!/usr/bin/env python
# -*- coding: utf-8 -*-

#The MIT License (MIT)
#
#Copyright (c) 2020 Universidad de Oriente & KU Leuven
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""
# Description: Simple demo application
# Authors: 
    - Alexander A. Suarez Leon
    - Sergio D. Sanchez Mercantete
    - Carolina Varon
    - Rik Willems
    - Sabine Van Huffel
    - Carlos R. Vazquez Seisdedos 
# Date: 2020
# todo:
# notes: This script ca be tested using Anaconda, a list with all 
         dependencies is available in requirements.txt.
_____
"""


import numpy as np
import matplotlib.pyplot as plt

import tools.detc.detQw as qon
import tools.detc.detRw as rp
import tools.detc.detTf as toff
from tools.filterc.filtertools import FilterTools
import tools.QTRR as qtrr

from scipy.io.matlab import loadmat
#import scipy.signal as signal
 

if __name__ == '__main__':

    mat = loadmat('testqtrr10.mat')
    
    s = mat['ecg']
    
    s1 = s[0, :]
        
    fs = 250
    
    FilterPack = FilterTools()
    
    # Nonlinear lowpass median filtering 
    s2 = FilterPack.medianfilter(s1, fs)
    
    # FIR Bandpass filtering 
    s2, b = FilterPack.filterfir(s2, fs, 0.5, 40)
    
    
    # Create an R-peak detection object
    RpDet   = rp.Rwd()
    
    # Create a Qon detection object
    QonDet  = qon.Qwd()
    
    # Create a Toff detection object
    ToffDet = toff.Twd()
    
        
    [ridx, sf] = RpDet.detqrs(s2, fs)
    
    qonidx = QonDet.globalinitq(s2, ridx)
    
    toffidx = ToffDet.globalzhangTend(s2, ridx)
    
    # Next figure shows the results of the detection for all points (Qon, R, Toff)
    # Please note that there are heartbeats where the detection will fail due to 
    # noise and/or baseline drift
    
    top = s2.size / fs
    t = np.linspace(0, top, s2.size, endpoint=False)
    
    plt.figure()
    
    plt.plot(t, s2, 'k')
    plt.plot(t[ridx], s2[ridx], 'ro')
    plt.plot(t[qonidx], s2[qonidx], 'g^')
    plt.plot(t[toffidx], s2[toffidx], 'b+')
    
    plt.show()
    
    
    

    
    

