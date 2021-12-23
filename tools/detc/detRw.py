# -*- coding: utf-8 -*-

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
# Description: R-peak detection algorithms
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
import scipy.linalg as linalg

class Rwd:
    """"
    docs here
    """

    def __init__(self, tag=0):
        self.tag = tag

    def rpeak(self, s0, fs):
        """"
        detection of ECG R-peaks by parabolic fitting
        Autor: Qinghua Zhang
        :param s0: signal vector
        :type s0: ndarray
        :param fs: sampling frequency
        :type fs: int
        :return ridx: index of R peaks
        :type ridx: list
        :return s: signal without baseline wander
        """
        s = spectral.filtbyfft(s0 - np.mean(s0), fs, [0.5, fs])
        N = s.size

        # Frequence ratio w.r.t. 250hz.

        fratio = fs / 250

        hwin = int(np.ceil(5 * fratio))  # half window width for parabolic fitting
        rweights = np.arange(1, 0, (-1 / hwin), float)  # parabolic fitting weights in half window
        fweights = np.arange((1 / hwin), 1 + (1 / hwin), (1 / hwin), float)
        dsw = np.sqrt(np.hstack([fweights, 1, rweights]))  # square root of double side weights

        ps2 = np.zeros(N)
        ps0 = np.zeros(N)

        xw = np.vstack((-1 * (np.arange(-hwin, hwin + 1, 1, float)) ** 2, np.ones(2 * hwin + 1)))
        xw = np.vstack((dsw, dsw)) * xw

        invxw = np.dot(linalg.inv(np.dot(xw, xw.transpose())), xw)

        for k in range(hwin, N - hwin - 1):
            yw = s[range((k - hwin), (k + hwin + 1))]
            yw1 = np.outer(dsw, yw)

            th = np.dot(invxw, yw1)

            ps2[k] = th[0, 0]
            ps0[k] = th[1, 0]

        pth = ps2 * ps0

        PTc = np.zeros(N)
        kpt = 0

        pth0 = pth.copy()

        srtlen = int(np.min([10000 * fratio, pth.size]))
        sortedpth = np.sort(pth[np.arange(0, srtlen)])

        seuil = sortedpth[int(np.round(srtlen * 0.975))]

        pth[pth < seuil] = 0.0

        cnth = int(np.round(0.36 * fs))
        debut = 0
        # fin = 0

        for k in range(cnth, (N - cnth)):

            if pth[k] != 0 and np.logical_not(np.any(pth[(k - cnth):(k - 1)])):
                debut = k

            if pth[k] != 0 and np.logical_not(np.any(pth[(k + 1):(k + cnth)])):
                fin = k

                if fin > debut:
                    ind = np.argmax(pth[debut:fin])
                else:
                    ind = pth[debut]

                ind = ind + debut - 1
                PTc[kpt] = ind
                kpt = kpt + 1

        picind = np.array(PTc[0:kpt])

        srtlen1 = int(np.min([10000 * fratio, kpt]))
        dpic = np.diff(picind[0:srtlen1])
        sorteddpic = np.sort(dpic)
        thirdidx = int(np.ceil(srtlen1 / 3))
        typicnum = np.median(sorteddpic[0:thirdidx])

        # Treat possible beginning peaks

        beginexind = []
        self.BeginPeakRecovery(picind[0], pth0, typicnum, seuil, beginexind)

        if len(beginexind) > 0:
            beginexind2 = np.array(beginexind)
            if beginexind2.size > 1:
                picind2 = np.hstack([np.sort(beginexind2), picind])
            else:
                picind2 = np.hstack([beginexind2, picind])
        else:
            picind2 = picind.copy()

        # These 3 lines have to be redone since now picind may have been changed.

        dpic2 = np.diff(picind2[0:srtlen1])
        sorteddpic2 = np.sort(dpic2)
        typicnum2 = np.median(sorteddpic2[0:thirdidx])

        tmp = dpic2 > (1.5 * typicnum2)
        cond = np.any(tmp)

        if cond:
            idxfind = np.intp(np.linspace(0, tmp.size - 1, tmp.size))
            indmiss = idxfind[tmp]
            misscase = indmiss.size
            extraind = []

            for km in range(0, misscase):
                self.PeakRecovery(picind2[indmiss[km]], picind2[indmiss[km] + 1], pth0, typicnum2, extraind)

            vecextraind = np.array(extraind, dtype=np.intp)
            keptind = pth0[vecextraind] > (0.3 * seuil)
            picind3 = np.sort(np.hstack([picind2, vecextraind[keptind]]))

            ridx = np.intp(picind3) - hwin
            return ridx, s

        ridx = np.intp(picind2) - hwin
        return ridx, s

    def BeginPeakRecovery(self, ind1, pth0, typicnum, seuil, mylist):

        if ind1 > (typicnum * 0.7):
            ind2 = int(np.ceil(ind1 - typicnum * 0.3))
            maxv = np.max(pth0[0:ind2])
            maxi = np.argmax(pth0[0:ind2])

            if maxv > (seuil * 0.6):
                mylist.append(maxi)
                self.BeginPeakRecovery(maxi, pth0, typicnum, seuil, mylist)

    def PeakRecovery(self, ind1, ind2, pth, typicnum, exind):
        """"

        """
        hnum = np.intp(np.ceil(0.5 * typicnum))

        lo = np.intp(ind1 + hnum)
        hi = np.intp(ind2 - hnum)

        maxind = np.argmax(pth[lo:hi])
        maxindglobal = maxind + ind1 + hnum - 1

        if (maxindglobal - ind1) > (typicnum * 1.5):
            self.PeakRecovery(ind1, maxindglobal, pth, typicnum, exind)
            exind.append(maxindglobal)

        if (ind2 - maxindglobal) > typicnum * 1.5:
            exind.append(maxindglobal)
            self.PeakRecovery(maxindglobal, ind2, pth, typicnum, exind)

    def detqrs(self, y, fs, fac=1.5):
        """"

        """

        yf = y
        yfd = np.diff(yf)

        nterm = np.max(np.abs(yfd))

        yfds = np.round(yfd * fac / nterm)
        yfdds = np.diff(yfds)

        k = np.nonzero(yfdds)[0]
        l = len(k)
        r = []

        for i in range(0, (l - 1)):
            if (k[i + 1] - k[i]) > round(0.1 * fs):
                r.append(k[i])

        N_lat = len(r)

        ra = np.array(r)
        rb = ra.copy()

        d = round(0.1 * fs)

        for i in range(1, N_lat - 1):
            a = y[(ra[i] - d):(ra[i] + d)]
            idx = np.argmax(np.diff(a))
            rb[i] = rb[i] + idx - d

        rc = np.unique(rb)

        rr = np.diff(rc)
        q = np.min(rr)
        s = np.argmin(rr)

        lr = list(rc)

        thr = np.mean(rr) - 2 * np.std(rr)

        if q < thr:
            lr.remove(lr[s])

        rd = np.array(lr)

        rdl = rd.size
        wns = np.intp(0.05 * fs)

        for i in range(1, rdl):
            wdw = y[(rd[i] - wns):(rd[i] + wns)]

            if wdw.shape[0] > 0:
                pp = np.argmax(wdw)
                rd[i] = rd[i] + pp - wns
            else:
                continue

        re = np.unique(rd)

        return re, yf

    def getIdx(self, aList, aValue):
        """
        
        :param aValue: 
        :type aValue: 
        :return: 
        """
        Line = aList > aValue
        idx = np.argmax(Line)
        pidx = idx - 1

        return pidx, idx

    def detectRealIdx(self, aList, aValue):
        """"
        Hallar valor del QRS en una lista
        ej: si devuelve true, false, 0 el valor se encuentra en el principio
        si devuelve false, true, 0 está en el final
        si devuelve false, false, i (i) es la pocision donde encontro el valor en la lista
        """
        l = len(aList)
        end = l - 1

        if aValue >= aList[-1]:

            return False, True, end

        elif aValue <= aList[0]:

            return True, False, 0

        else:

            ind1, ind2 = self.getIdx(aList, aValue)

            d1 = aValue - aList[ind1]
            d2 = aList[ind2] - aValue

            if d1 < d2:
                return ind1 == 0, False, ind1
            else:
                return False, ind2 == end, ind2
