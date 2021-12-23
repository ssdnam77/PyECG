#!

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
# Description: Qon detection algorithms
# Authors: 
    - Alexander A. Suarez Leon
    - Sergio D. Sanchez Mercantete
    - Carolina Varon
    - Rik Willems
    - Sabine Van Huffel
    - Carlos R. Vazquez Seisdedos 
# Date: 2020
# todo:
# notes:
_____
"""

import numpy as np

F_CONST1 = 10.0/1000
F_CONST2 = 50.0/1000
F_CONST3 = 30.0/1000

class Qwd:
    """"
    Class for detecting the Qon 
    """

    def __init__(self, tag=0):
        self.tag = tag


    def initq(self, s, r, ridx, fs=250):
        """        
	Detects of Qon for a single heartbeat
	s: signal
	r: R-peak index positions
	ridx : heartbeat index
	fs: sampling frequency
        """
        fac1 = np.intp(np.round(F_CONST1 * fs))
        fac2 = np.intp(np.round(F_CONST2 * fs))

        v = s[(r[ridx] - fac1 - fac2):(r[ridx] - fac1)]
        sof = np.argmin(v)
        qm = r[ridx] - fac1 - fac2 + sof

        xmax = qm
        ymax = s[xmax]

        fac3 = np.intp(np.round(F_CONST3 * fs))

        xref = xmax - fac3
        yref = s[xref]

        areavalues = np.zeros(fac3)

        for xi in range(xref, xmax):
            yi = s[xi]
            areavalues[xi - xref] = 0.5 * ((xmax - xi) * (yref - yi) - (xref - xi) * (ymax - yi))

        xon = np.argmin(areavalues)
        qon = xref + xon

        return qon

    def globalinitq(self, s, r, fs=250):
        """"
        Detects of Qon for a set of heartbeats
	s: signal
	r: R-peak index positions
	fs: sampling frequency
        """
        fac1 = np.intp(np.round(F_CONST1 * fs))
        fac2 = np.intp(np.round(F_CONST2 * fs))

        rs = r.size

        qm = np.zeros(rs, dtype=np.intp)

        for i in range(0, rs):
            v = s[(r[i] - fac1 - fac2):(r[i] - fac1)]
            if v.any():
                sof = np.argmin(v)
                qm[i] = r[i] - fac1 - fac2 + sof

        m = qm.size

        xmax = qm.copy()
        ymax = s[np.intp(xmax)].copy()

        fac3 = np.intp(np.round(F_CONST3 * fs))

        xref = xmax - fac3
        yref = s[np.intp(xref)].copy()

        qon = np.zeros(m)

        for i in range(0, m):

            areavalues = np.zeros(fac3)

            for xi in range(xref[i], xmax[i]):
                yi = s[xi]
                areavalues[xi - xref[i]] = 0.5 * ((xmax[i] - xi) * (yref[i] - yi) - (xref[i] - xi) * (ymax[i] - yi))

            xon = np.argmin(areavalues)
            qon[i] = xref[i] + xon

        return np.intp(qon)
