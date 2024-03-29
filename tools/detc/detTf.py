#!

#The MIT License (MIT)
#
#Copyright (c) 2016 MIT Laboratory for Computational Physiology
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
# Description: Toff detection methods 
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
from utils import spectral

class Twd:
    """"

    """

    def __init__(self,tag=0):
        self.tag = tag

    def zhangTend(self, s, rp, rp_idx, fs=250, win=32):
        """"
        encuentra final de onda T para un solo latido ( en ventana)
        """

        fratio = fs / 250

        swin = np.intp(win * fratio)

        N = s.size

        ptwin = np.intp(np.ceil(4 * fratio))

        ald = 0.15
        bld = 37 * fratio
        alu = 0.7
        blu = -9 * fratio
        ard = 0.0
        brd = 70 * fratio
        aru = 0.20
        bru = 101 * fratio

        kR = rp[rp_idx]
        knR = rp_idx

        if (kR == rp[-1]):
            RRk = 200 * fratio
        else:
            RRk = rp[knR + 1] - kR

        if RRk < 220 * fratio:
            minRtoT = np.intp(np.floor(ald * RRk + bld))
            maxRtoT = np.intp(np.ceil(alu * RRk + blu))
        else:
            minRtoT = np.intp(np.floor(ard * RRk + brd))
            maxRtoT = np.intp(np.ceil(aru * RRk + bru))

        leftbound = kR + minRtoT
        rightbound = kR + maxRtoT

        rightbound = np.intp(np.min([rightbound, N - ptwin]))
        leftbound = np.intp(np.min([leftbound, rightbound]))

        if kR != rp[-1] and rightbound > rp[knR + 1]:
            rightbound = np.intp(rp[knR + 1])

        areavalue = np.zeros(rightbound - leftbound)

        for kT in range(leftbound, rightbound):

            cutlevel = np.sum(s[(kT - ptwin):(kT + ptwin)]) / (ptwin * 2 + 1)
            r = kT - swin + 1

            if r < 0:
                r = 0

            corsig = s[r:kT] - cutlevel
            areavalue[kT - leftbound] = np.sum(corsig)

        Tval = areavalue.copy()

        maxind = np.argmax(Tval)

        Tend = maxind + leftbound - 1

        return Tend

    def globalzhangTend(self, s0, rp, fs=250, win=32, mthd='p', thrld=6):
        """"
        Encuentra los finales de onda T en un conjunto de latidos
        """
        fratio = fs / 250

        swin = np.intp(win * fratio)

        s = spectral.filtbyfft((s0 - np.mean(s0)), 250, [0.05, 250])

        N = s.size

        ptwin = np.intp(np.ceil(4 * fratio))

        nT = rp.size

        if rp[-1] + 200 > N:
            nT = nT - 1

        areavalue = np.zeros(N)
        Tends = np.zeros(nT)

        ald = 0.15
        bld = 37 * fratio
        alu = 0.7
        blu = -9 * fratio
        ard = 0.0
        brd = 70 * fratio
        aru = 0.20
        bru = 101 * fratio

        for knR in range(0, nT):

            kR = rp[knR]

            if (knR == (nT - 1)):
                RRk = 200 * fratio
            else:
                RRk = rp[knR + 1] - kR

            if RRk < 220 * fratio:
                minRtoT = np.intp(np.floor(ald * RRk + bld))
                maxRtoT = np.intp(np.ceil(alu * RRk + blu))
            else:
                minRtoT = np.intp(np.floor(ard * RRk + brd))
                maxRtoT = np.intp(np.ceil(aru * RRk + bru))

            leftbound1 = kR + minRtoT
            rightbound1 = kR + maxRtoT

            rightbound2 = np.intp(np.min([rightbound1, N - ptwin]))
            leftbound = np.intp(np.min([leftbound1, rightbound2]))

            if (knR < (nT - 1)) and rightbound2 > rp[knR + 1]:
                rightbound2 = np.intp(rp[knR + 1])

            for kT in range(leftbound, rightbound2):

                cutlevel = np.sum(s[(kT - ptwin):(kT + ptwin + 1)]) / (ptwin * 2 + 1)
                r = kT - swin + 1

                if r < 0:
                    r = 0

                corsig = s[r:kT] - cutlevel
                areavalue[kT] = np.sum(corsig)

            Tval = areavalue[leftbound:rightbound2].copy()

            if Tval.size > 0:

                dum = np.max(Tval)
                maxind = np.argmax(Tval)
                duminv = np.max(-Tval)
                maxindinv = np.argmax(-Tval)

                if mthd == 'n':
                    fmaxind = maxindinv
                else:
                    if maxind < maxindinv:
                        leftind = maxind
                        rightind = maxindinv
                        leftdum = dum
                        rightdum = duminv
                    else:
                        leftind = maxindinv
                        rightind = maxind
                        leftdum = duminv
                        rightdum = dum

                    if leftdum > thrld * rightdum:
                        fmaxind = leftind
                    else:
                        fmaxind = rightind

                Tends[knR] = fmaxind + leftbound

        return np.intp(Tends)
