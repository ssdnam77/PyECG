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
import scipy.interpolate as intrp

class BQTVI:
    """"
    Implementation of Berger index (QTVI)
    """
    def __init__(self):
        pass

    def BergerQTVI(self, s, r, rk, Tend, QTk, start, fs=250, rr_lin=None, qt_lin=None):
        """"

        :param s: signal input
        :type s: int
        :param r:
        """
        rr = np.diff(r) / 1000
        rrt = np.cumsum(rr)

        if rr_lin is None:
            """" 
            
            """
            n = rr.size

            QT = np.zeros(n)

            es = Tend - rk - 50

            for i in range(1, n):
                opt_alpha = self.optimalpha(s, r[i], rk, es)
                QT[i] = QTk * opt_alpha

            # Spline interpolation RR 4 Hz

            tck1 = intrp.splrep(rrt, rr, s=0)
            txnew1 = np.linspace(0, rrt[-1], rrt[-1] * 4, endpoint=False)
            rr_int = intrp.splev(txnew1, tck1, der=0)

            # RR linear trend removing

            pr = np.polyfit(txnew1, rr_int, 1)
            trend_rr = np.polyval(pr, txnew1)

            rr_lin = rr_int - trend_rr

            QT = QT / 1000

            # Spline interpolation QT 4 Hz

            tck2 = intrp.splrep(rrt[:-1], QT[1:], s=0)
            txnew2 = np.linspace(0, rrt[-1], rrt[-1] * 4, endpoint=False )
            qt_int = intrp.splev(txnew2, tck2, der=0)

            # QT linear trend removing

            pqt = np.polyfit(txnew2, qt_int, 1)
            trend_qt = np.polyval(pqt, txnew2)

            qt_lin = qt_int - trend_qt

        end = start + 256000

        mystart = np.sum(rrt < (start / 1000))
        myend = np.sum(rrt < (end / 1000))

        varQT = np.var(qt_lin[mystart:myend])
        mnsQT = np.mean(qt_lin[mystart:myend])

        varRR = np.var(rr_lin[mystart:myend])
        mnsRR = np.mean(rr_lin[mystart:myend])

        k1 = varQT / varRR

        k2 = (mnsRR / mnsQT) ** 2

        logQTVI = np.log10(k1*k2)

        return logQTVI, rr_lin, qt_lin

    def optimalpha(self, s, r2, r1, es):

        a_step = 0.01
        sstart = 0.9

        neps = 21

        while a_step >= 1e-4:

            eps_vals = np.zeros(neps)

            for i in range(0, neps):
                alpha = sstart + i * a_step
                eps_vals[i] = self.e_cost(s, r2, r1, es, alpha)

            idx = np.argmin(eps_vals)

            alpha = sstart + idx * a_step

            sstart = sstart + (idx - 1) * a_step

            a_step = a_step / 10
        else:
            return alpha

    def e_cost(self, s, r2, r1, es, alpha) -> float:

        be_idx = r1 + 50
        en_idx = r1 + 50 + es

        s_view = s[(r2 + 50):(r2 + 200 + es)].copy()
        idx = np.intp(np.arange(0, es) * alpha)

        subval = s[be_idx:en_idx] - s_view[idx]

        eps_val = np.dot(subval, subval)

        return eps_val


