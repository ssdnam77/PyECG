""""

"""

import logging
import sys
import platform
import pathlib
import hl7

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class Isnhe:
    """"
    clase para manejar archivos ishne (*.ecg) estandar
    """
