"""
# Description: 
# Autor: 
# Date: 
# todo: 
# notes: 
_____
"""

import numpy as np
from sktensor import dtensor,cp

class tensor:
    """"
    Tools for build
    """

    def buildtensor(self, s, r, st_int=50, end_int=80):

        slen = st_int + end_int + 1

        n = s.shape[1]
        end = n - 1
        tsize = r.shape[0]

        start = 0

        if r[0] - st_int < 0:
            start = 1
            tsize = tsize - 1

        if r[-1] + end_int > end:
            tsize = tsize - 1

        T = np.zeros((2, slen, tsize))

        k = 0
        for i in range(start, tsize):
            mtx = s[:, r[i] - st_int: r[i] + end_int + 1]
            sigmtx = (mtx - np.mean(mtx)) / np.std(mtx)
            T[:, :, k] = sigmtx
            k = k + 1

        T3d = dtensor(T)

        return T, T3d

    def tensor_class(self, s, r):

        st_int = 80
        end_int = 50

        T, T3d = self.buildtensor(s, r, st_int, end_int)

        P, fit, itr, _ = cp.als(T3d, 1)

        scores = np.array(P.U[2][:]).flatten()

        md = np.median(scores)
        sd = np.std(scores)

        var = 100 * sd / md

        if var > 10.0:
            thrd1 = md + sd
            thrd2 = md - sd
        else:
            thrd1 = 1.1 * md
            thrd2 = 0.9 * md

        t1 = (scores > thrd1)
        t2 = (scores < thrd2)

        t3 = np.logical_or(t1, t2)
        # t4 = np.array(t3, dtype=int)

        # print('Hello!!')

        return t3, T

    def tensor_class2(self, s, r):

        st_int = 80
        end_int = 50

        T, T3d = self.buildtensor(s, r, st_int, end_int)

        P, fit, itr, _ = cp.als(T3d, 1)

        scores = np.array(P.U[2][:]).flatten()

        md = np.median(scores)
        sd = np.std(scores)

        var = 100 * sd / md

        if var > 10.0:
            thrd1 = md + sd
            thrd2 = md - sd
        else:
            thrd1 = 1.1 * md
            thrd2 = 0.90 * md

        t1 = (scores > thrd1)
        t2 = (scores < thrd2)

        t3 = np.logical_or(t1, t2)
        # t4 = np.array(t3, dtype=int)

        # print('Hello!!')

        return t3, T
