"""
# Description: Algoritms for quality signal descriptors
# Autor: sergio.sanchez@estudiantes.uo.edu.cu
# Date:
# todo: evaluar la validez de los algortimos
# notes:
"""

import numpy as np
from utils import spectral
from scipy import signal


# ---------------------------
class SQI:
    """"

    """
    def __init__(self):

        pass

    def pSQI(self, s, fs):
        """
        the relative power in the QRS complex
        :param s: Senal de entrada
        :type s: float
        """
        ipw1 = spectral.tspect(s, fs, [5, 15])
        ipw2 = spectral.tspect(s, fs, [5, 40])

        rpSQI = ipw1 / ipw2

        return rpSQI

    def basSQI(self, s, fs):
        """"
        the relative power in the baseline
        :type s: float
        :param s: Senal de entrada

        """
        ipw1 = spectral.tspect(s, fs, [0, 1])
        ipw2 = spectral.tspect(s, fs, [0, 40])

        rbasSQI = 1 - ipw1 / ipw2

        return rbasSQI

    def bsSQI(self, s, r, fs):
        """"
        baseline wander check in time domain
        :param s: Senal de entrada
        :type s: float
        """
        n = r.size
        ns = s.size

        w1 = np.intp(np.round(fs * 0.07))
        w2 = np.intp(np.round(fs * 0.08))
        w3 = np.intp(fs)

        ipw1 = np.zeros(n)

        istart = 0

        while r[istart] < w3:
            istart = istart + 1

        istop = n - 1

        while r[istop] + w3 > ns:
            istop = istop - 1

        ri = np.intp(r)

        b = np.array([0.0503])
        a = np.array([1, -0.9497])

        sf = signal.lfilter(b, a, s)

        for i in range(istart, istop):
            sQRS = s[(ri[i] - w1):(ri[i] + w2)]
            sWIN = sf[(ri[i] - w3):(ri[i] + w3)]

            minQRS = np.min(sQRS)
            maxQRS = np.max(sQRS)

            minWIN = np.min(sWIN)
            maxWIN = np.max(sWIN)

            ipw1[i] = (maxQRS - minQRS) / (maxWIN - minWIN)

        rbsSQI = np.mean(ipw1[istart:istop])

        return rbsSQI

    def rsdSQI(self, s, r, fs):
        """"
        :param s: Senal de entrada
        :type s: float
        """
        n = r.size
        ns = s.size

        w1 = np.intp(np.round(fs * 0.07))
        w2 = np.intp(np.round(fs * 0.08))
        w3 = np.intp(np.round(fs * 0.2))

        ipw1 = np.zeros(n)

        istart = 0

        while r[istart] < w3:
            istart = istart + 1

        istop = n - 1

        while r[istop] + w3 > ns:
            istop = istop - 1

        ri = np.intp(r)

        for i in range(istart, istop):
            sQRS = s[(ri[i] - w1):(ri[i] + w2)]
            sWIN = s[(ri[i] - w3):(ri[i] + w3)]

            stdQRS = np.std(sQRS)
            stdWIN = np.std(sWIN)

            ipw1[i] = stdQRS / stdWIN

        rrsdSQI = np.mean(ipw1[istart:istop])

        return rrsdSQI

    def eSQI(self, s, r, fs):
        """"
        the relative energy in the QRS complex
        :param s: Senal de entrada
        :type s: float
        """
        n = r.size
        ns = s.size

        w1 = np.intp(np.round(fs * 0.07))
        w2 = np.intp(np.round(fs * 0.08))
        w3 = np.intp(np.round(fs * 0.2))

        ipw1 = np.zeros(n)
        ipw2 = np.zeros(n)

        istart = 0

        while r[istart] < w3:
            istart = istart + 1

        istop = n - 1

        while r[istop] + w3 > ns:
            istop = istop - 1

        ri = np.intp(r)

        for i in range(istart, istop):
            sQRS = s[(ri[i] - w1):(ri[i] + w2)]
            sWIN = s[(ri[i] - w3):(ri[i] + w3)]

            ipw1[i] = np.dot(sQRS, sQRS)
            ipw2[i] = np.dot(sWIN, sWIN)

        reSQI = np.mean(ipw1[istart:istop] / ipw2[istart:istop])

        return reSQI

    def hfSQI(self, s, r, fs):
        """"
        the relative amplitude of high frequency noise
        :param s: Senal de entrada
        :type s: float
        """
        n = r.size
        ns = s.size

        w1 = np.intp(np.round(fs * 0.07))
        w2 = np.intp(np.round(fs * 0.08))
        w3 = np.intp(np.round(fs * 0.28))
        w4 = np.intp(np.round(fs * 0.05))

        ipw1 = np.zeros(n)

        istart = 0

        while r[istart] < w3:
            istart = istart + 1

        istop = n - 1

        while r[istop] + w3 > ns:
            istop = istop - 1

        ri = np.intp(r)

        b1 = np.array([1, -2, 1])
        b2 = np.array([1, 1, 1, 1, 1, 1])

        a = np.array(1)

        sf1 = signal.lfilter(b1, a, s)
        sf2 = signal.lfilter(b2, a, np.abs(sf1))

        for i in range(istart, istop):
            sQRS = s[(ri[i] - w1):(ri[i] + w2)]
            sWIN = sf2[(ri[i] - w3):(ri[i] - w4)]

            minQRS = np.min(sQRS)
            maxQRS = np.max(sQRS)

            meanWIN = np.mean(sWIN)

            ipw1[i] = (maxQRS - minQRS) / meanWIN

        rhfSQI = np.mean(ipw1[istart:istop])

        return rhfSQI
