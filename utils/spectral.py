# -*- coding: utf-8 -*-
"""
# Description: Tools for spectral processing
# Autor: sergio.sanchez@estudiantes.uo.edu.cu
# Date:
# todo: agregar wavlet y demas helpers
# notes:
______
"""

from scipy.fftpack import next_fast_len, rfft, irfft, fft, ifft
import numpy as np


def tspect(x, fs, wn):
    L = next_fast_len(x.size)

    Y = rfft(x, L)

    wn1 = np.array(2 * wn[0] / fs)
    wn2 = np.array(2 * wn[1] / fs)

    top = np.intp(L / 2)

    P1 = abs(Y / L)
    P2 = P1[0:top].copy()
    P2[1:-2] = 2 * P2[1: -2]

    P3 = P2  # / sum(P2)

    fx = np.linspace(0, np.intp(L / 2), np.intp(L / 2) + 1) / L

    idx1 = (fx >= wn1)
    idx2 = (fx <= wn2)
    idx3 = np.logical_and(idx1, idx2)

    iPw = P3[np.nonzero(idx3)]

    sPw = sum(iPw)

    return sPw
def filtbyfft(x, fs, wn):

    fl = np.max([wn[0], 0])
    fh = np.min([wn[1], fs/2.0])

    oSize = x.size
    N = next_fast_len(oSize)

    y = rfft(x, N)

    lowicut = int(np.round(fl*N/fs)) - 1
    lowmirror = -lowicut + 1#int(N - lowicut + 2)

    highicut = int(np.round(fh*N/fs))
    highmirror = -highicut + 1

    y[np.arange(lowmirror,lowicut)] = 0.0
    y[np.arange(highicut - N, highmirror)] = 0.0

    ixf = irfft(y)
    xf = np.real(ixf)

    return xf[0:oSize]

def main():
    pass


if __name__ == "__main__":
    main()
