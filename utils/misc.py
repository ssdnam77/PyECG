import numpy as np

def getIdx(aList, aValue):

    Line = aList > aValue
    idx = np.argmax(Line)
    pidx = idx -1

    return pidx, idx


def detectRealIdx(aList, aValue):

    l = len(aList)
    end = l - 1

    if aValue >= aList[-1]:

        return False, True, end

    elif aValue <= aList[0]:

        return True, False, 0

    else:

        ind1, ind2 = getIdx(aList, aValue)

        d1 = aValue - aList[ind1]
        d2 = aList[ind2] - aValue

        if d1 < d2:
            return ind1 == 0, False, ind1
        else:
            return False, ind2 == end, ind2