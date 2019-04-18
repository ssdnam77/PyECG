""""

"""

import pathlib
import datetime
import logging
from ishneholterlib import Holter

logger = logging.getLogger("ishne_logger")


class Ishne:
    def __init__(self):

        pass

    def read_ishne(self, filename):
        ecgreg = Holter(filename)
        ecgreg.load_data()




def main():
    test = Holter('60.ecg')
    head = test.load_data()

    return test.lead(0)


if __name__ == '__main__':

    h = main()
    print(h)

