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
# Description: p/q = 4 upsampling utility  
# Authors: 
    - Alexander A. Suarez Leon
    - Sergio D. Sanchez Mercantete <sergio.sanchez@estudiantes.uo.edu.cu>
    - Carolina Varon
    - Rik Willems
    - Sabine Van Huffel
    - Carlos R. Vazquez Seisdedos 
# Date: 2019
# todo:
# notes:
_____
"""
from scipy import signal
import numpy as np
from numpy import cumprod, array, arange, zeros, floor, lexsort


def up4sample(s, r=0, rk=0, Tend=0, QTk=0):
    """"
    4x upsampling

    """
    N = 10
    bta = 5
    pqmax = 4

    fc = 0.125
    L = 2 * N * pqmax + 1

    hp1 = signal.firls(L, [0, 2 * fc, 2 * fc, 1], [1, 1, 0, 0])
    kwin = signal.kaiser(L, bta)

    hp2 = hp1 * kwin
    hp3 = pqmax * hp2 / np.sum(hp2)
    hl = list(hp3)
    hl.insert(0, 0)
    h = np.array(hl)

    delay = int((L-1)/2)

    sout = signal.upfirdn(h, s, pqmax, 1)
    sf = sout[(delay+1):(-delay + 1)].copy()

    rf = pqmax * r
    rkf = pqmax * rk
    Tendf = pqmax * Tend
    QTkf = pqmax * QTk

    return sf, rf, rkf, Tendf, QTkf


