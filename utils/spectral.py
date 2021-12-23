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
# Description: Tools for spectral processing
# Author: sergio.sanchez@estudiantes.uo.edu.cu
# Date: 2019
# todo: add wavelet signal processing
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

def getspectrum(sig, fs, RealFFT=True):

    L = next_fast_len(sig.size)

    if RealFFT:
        s_fft = rfft(sig, L)

        P2 = np.abs(s_fft / L)

        P1 = P2[0:int(L / 2)]
        P1[1: -2] = 2 * P1[1: -2]

        f = fs / L * np.arange(0, L / 2, 1)

        return f, P1

    else:

        s_fft = fft(sig, L)

        P2 = np.abs(s_fft / L)

        P1 = P2[0:int(L / 2)]
        P1[1: -2] = 2 * P1[1: -2]

        f = fs/L * np.arange(0, L/2, 1)

        return f, P1

def main():
    pass


if __name__ == "__main__":
    main()
