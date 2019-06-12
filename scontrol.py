""""
Control the app

"""

import sys
import platform
import pathlib
import os
import datetime
import logging
import multiprocessing
import hashlib
from PyQt5.QtWidgets import QAction, qApp, QMessageBox
from iomod import ishnef
from iomod import dicomf
from iomod import wfdbf
from iomod import xdf
from iomod import hl7m
from iomod import e3cm

logger = logging.getLogger()


class Optcontrol:
    """" maneja las configuraciones"""
    pass


class Maincontrol:
    """" maneja la interfaz grafica"""

    def __init__(self):
        pass

    pass


class Filecontrol:
    """"" maneja los modulos de entrada/salida"""

    def __init__(self):

        pass

    def openreg(self, filecnm, regtyp=None):
        """"
        :param path
        :type path: object
        abrir el archivo segun su tipo
        formatos soportados:
        dicom
        ishne
        physionet
        xdf
        scp-ecg
        """
        path = pathlib.PurePath(filecnm)
        if path.suffix == '.e3c':
            "E3C reg"
            e3cins = e3cm.E3cc
            arch = platform.system()
            header, datarg = e3cins.reade3c(path, arch, 2444)
            pass
        elif path.suffix == '.dcm':
            "DICOM std"
            header
            pass
        elif path.suffix == '.ecg':
            "ISHNE std"

            pass
        elif path.suffix == '.xdf':
            "OpenXDF"
            pass
        pass


class Dbcontrol:
    """"" maneja la(s) base de dato(s)"""

    def new_db(self):
        # todo: recivir path y crea una nueva
        # initializer.remake()
        pass

    def opendb(self):
        # todo: recivir path y instancia la DB

        pass
