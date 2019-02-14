"""
# Description: 
# Autor: 
# Date: 
# todo: 
# notes: 
_____
"""
from scipy import signal
import numpy as np
from numpy import cumprod, array, arange, zeros, floor, lexsort


def up4sample(s, r=0, rk=0, Tend=0, QTk=0):
    """"
    sobremuestreo 4x de la señal

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

