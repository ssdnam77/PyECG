""""

"""

import logging
from utils.metadt import Meta
from ishneholterlib import Holter

logger = logging.getLogger("ishne_logger")


class Ishne(Meta):
    def __init__(self, name=None, last_name=None):
        self.header['name'] = name
        self.header['last_name'] = last_name
        # self.header['age'] =
        pass

    # def header(self):
    #     pass

    def read_ishne(self, filename):
        ecgreg = Holter(filename)
        ecgreg.load_data()
        return ecgreg


def main():
    test = ish.read_ishne(r'B:\60.ecg')
    test.load_data()
    ld1 = test.lead[0]
    ld2 = test.lead[1]



if __name__ == '__main__':
    ish = Ishne()
    main()
