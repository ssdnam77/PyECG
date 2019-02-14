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

class Qwd:
    """"
    Deteccion de inicio de onda Q

    """

    def initq(s, r, ridx, fs=250):
        """"
        detectar inicio de onda Q (en ventana)
        """
        fac1 = np.intp(np.round(10 * fs / 1000))
        fac2 = np.intp(np.round(50 * fs / 1000))

        v = s[(r[ridx] - fac1 - fac2):(r[ridx] - fac1)]
        sof = np.argmin(v)
        qm = r[ridx] - fac1 - fac2 + sof

        xmax = qm
        ymax = s[xmax]

        fac3 = np.intp(np.round(30 * fs / 1000))

        xref = xmax - fac3
        yref = s[xref]

        areavalues = np.zeros(fac3)

        for xi in range(xref, xmax):
            yi = s[xi]
            areavalues[xi - xref] = 0.5 * ((xmax - xi) * (yref - yi) - (xref - xi) * (ymax - yi))

        xon = np.argmin(areavalues)
        qon = xref + xon

        return qon

    def globalinitq(s, r, fs=250):
        """"
        detectar inicio de onda Q para un conjunto de latidos
        """
        fac1 = np.intp(np.round(10 * fs / 1000))
        fac2 = np.intp(np.round(50 * fs / 1000))

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

        fac3 = np.intp(np.round(30 * fs / 1000))

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
