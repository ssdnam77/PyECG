#!
"""
# Description:
# Autor:
# Date:
# todo:
# notes:
_____
"""

import numpy as np
from utils import spectral
from scipy.stats import pearsonr

class QTRR:
    """"
    docs
    """

    def __init__(self):
        pass

    def getQTRRLine(rr, qt, pqt):

        rr_max = np.max(rr)
        rr_min = np.min(rr)

        rr_x = np.arange(rr_min, rr_max, (rr_max - rr_min) / 100)
        # pqt = np.polyfit(rr, qt, 1)
        qt_trend = np.polyval(pqt, rr_x)

        rp = pearsonr(rr, qt)

        return rr_x, qt_trend

    def fitmodelQTRR(rr, qt, model='Linear'):

        if model == "Linear":
            x = rr
            y = qt
            pqt = np.polyfit(x, y, 1)
        elif model == "Hyperbolic":
            x = 1 / rr
            y = qt
            pqt = np.polyfit(x, y, 1)
        elif model == "Parabolic-Log":
            x = np.log(rr)
            y = np.log(qt)
            apqt = np.polyfit(x, y, 1)
            pqt = np.array([apqt[0], np.exp(apqt[1])])
        elif model == "Logarithmic":
            x = np.log(rr)
            y = qt
            pqt = np.polyfit(x, y, 1)
        elif model == "Shifthed logarithmic":
            x = rr
            y = np.exp(qt)
            pqt = np.polyfit(x, y, 1)
        elif model == "Exponential":
            x = np.exp(-rr)
            y = qt
            pqt = np.polyfit(x, y, 1)
        elif model == "Arcus tangent":
            x = np.arctan(rr)
            y = qt
            pqt = np.polyfit(x, y, 1)
        elif model == "Hyperbolic tangent":
            x = np.tanh(rr)
            y = qt
            pqt = np.polyfit(x, y, 1)
        elif model == "Arcus hyperbolic sine":
            x = np.arcsinh(rr)
            y = qt
            pqt = np.polyfit(x, y, 1)
        elif model == "Arcus hyperbolic cosine":
            x = np.arccosh(rr + 1)
            y = qt
            pqt = np.polyfit(x, y, 1)

        rp = pearsonr(x, y)

        return pqt, x, y, rp[0], rp[1]

    def evalmodelQTRR(rr, pqt, model='Linear'):

        rr_max = np.max(rr)
        rr_min = np.min(rr)

        rr_x = np.arange(rr_min, rr_max, (rr_max - rr_min) / 100)

        alpha = pqt[0]
        beta = pqt[1]

        if model == "Linear":
            qt = beta + alpha * rr_x
        elif model == "Hyperbolic":
            qt = beta + alpha / rr_x
        elif model == "Parabolic-Log":
            qt = beta * np.power(rr_x, alpha)
        elif model == "Logarithmic":
            qt = beta + alpha * np.log(rr_x)
        elif model == "Shifthed logarithmic":
            qt = np.log(beta + alpha * rr_x)
        elif model == "Exponential":
            qt = beta + alpha * np.exp(-rr_x)
        elif model == "Arcus tangent":
            qt = beta + alpha * np.arctan(rr_x)
        elif model == "Hyperbolic tangent":
            qt = beta + alpha * np.tanh(rr_x)
        elif model == "Arcus hyperbolic sine":
            qt = beta + alpha * np.arcsinh(rr_x)
        elif model == "Arcus hyperbolic cosine":
            qt = beta + alpha * np.arccosh(rr_x + 1)

        return rr_x, qt

    def correctmodelQTRR(rr, qt, xi, model='Linear'):
        """"
        todo: change the QTc method, add parametric correction option
        enlazar QTc a la ui
        """
        if model == "Linear":
            qtc = qt + xi * (1 - rr)
        elif model == "Hyperbolic":
            qtc = qt + xi * (1 / rr - 1)
        elif model == "Parabolic-Log":
            qtc = qt / np.power(rr, xi)
        elif model == "Logarithmic":
            qtc = qt - xi * np.log(rr)
        elif model == "Shifthed logarithmic":
            qtc = np.log(np.exp(qt) + xi * (1 - rr))
        elif model == "Exponential":
            qtc = qt + xi * (np.exp(-rr) - np.exp(-1))
        elif model == "Arcus tangent":
            qtc = qt + xi * (np.arctan(1) - np.arctan(rr))
        elif model == "Hyperbolic tangent":
            qtc = qt + xi * (np.tanh(1) - np.tanh(rr))
        elif model == "Arcus hyperbolic sine":
            qtc = qt + xi * (np.arcsinh(1) - np.arcsinh(rr))
        elif model == "Arcus hyperbolic cosine":
            qtc = qt + xi * (np.arccosh(2) - np.arccosh(rr + 1))

        return qtc

    def computeXiopt(self, rr, qt, model="Linear"):

        start = -1
        step = 0.1

        neps = 21

        while step >= 1e-4:

            r_xy = np.zeros(neps)

            for i in range(0, neps):
                xi = start + i * step
                qtc = self.correctmodelQTRR(rr, qt, xi, model)
                r_xy[i] = np.abs(pearsonr(rr, qtc))

            idx = np.nanargmin(r_xy)
            rpmin = start + idx * step
            step = step / 10

            start = rpmin - step

        else:
            return rpmin, r_xy[idx]

    def genprofile(lagins, rr, rridx, profile):

        rposins = rr[rridx] - lagins

        if rposins < 0:
            start = 0
        else:
            start = np.sum((rr / 250.0 - lagins) > 0) - 1

        Ni = rridx - start

        j = np.arange(-Ni + 1, 0, 1, dtype=float)

        if profile == "lin":
            wlw = 2 * (j + Ni + 1) / (Ni * (Ni - 1))

        return wlw

    def computeXiopt(self, rr, qt, model="Linear"):
        """

        :type rr: object
        """
        start = -1
        step = 0.1

        neps = 21

        while step >= 1e-4:

            r_xy = np.zeros(neps)

            for i in range(0, neps):
                xi = start + i * step
                qtc = self.correctmodelQTRR(rr, qt, xi, model)
                r_xy[i] = np.abs(pearsonr(rr, qtc))

            idx = np.nanargmin(r_xy)
            rpmin = start + idx * step
            step = step / 10

            start = rpmin - step

        else:
            return rpmin, r_xy[idx]
