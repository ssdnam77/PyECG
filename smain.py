#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# Description:
# Autor:
# Date:
# todo:
# notes:
______
"""


import sys
import platform
import pathlib
import os
import datetime
import logging
import multiprocessing

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog, QAction, qApp
from gui.windp import Ui_MainWindow
from gui.setwin import Ui_Dialog
from resources import resc
import pyqtgraph as pg

import scontrol

# ----------------------------------------------------------------------------------------------------------------------
logger = logging.getLogger()
dbdrv = scontrol.Dbcontrol()
confdrv = scontrol.Optcontrol()
filedrv = scontrol.Filecontrol()
guidrv = scontrol.Maincontrol()


class MainWindow(QMainWindow, Ui_MainWindow):
    """"
    configurar ventana
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        qApp.installEventFilter(self)
        # here is where the issue is occurs
        # self.show()
        self.setupUi(self)
        self.showMaximized()  # maximizing windows
        self.setWindowTitle("PyECG")  # windows title
        self.action_general_config.triggered.connect(self.config_windw)  # connect configuration options
        self.confbtn.clicked.connect(self.config_windw)  # same of above
        self.action_Exit.triggered.connect(self.close)  # in exit dialog
        self.importbtn.clicked.connect(self.openreg)  # import reg
        self.cmbox_comments.currentIndexChanged.connect(self.stack_widg_comment.setCurrentIndex)  # comment index
        self.cmbox_hrv1.currentIndexChanged.connect(self.stack_hrv.setCurrentIndex)  # hrv view index
        self.lost_bt.clicked.connect(self.ls_beat)  # something
        self.gBox_lost_beat.setHidden(True)  #

        # self.tunebtn.clicked.connect()

    def config_windw(self):  # control
        """"
        ventana de configuracion
        """
        logger.debug("Ventana de configuracion")
        # instanciar ventana de configuracion
        self.conf = OptDialog(parent=MainWindow)
        #
        self.conf.sett_db__new_button.clicked.connect(dbdrv.new_db)
        self.conf.sett_db__open_button.clicked.connect(dbdrv.open_db())

        # instanciar la ventana de config
        self.conf.show()

    def openreg(self):  # control
        """"
        cargar registro
        """
        logger.debug("Cargando archivo")
        # pasar tipo de archivo para decidir como se abrirá
        # check que el archivo exista
        filname, fltyp = QFileDialog.getOpenFileName(caption='Importar registro', directory='/home',
                                                     filter='Excorder3C files(*.e3c);;DICOM files'
                                                            '(*.dcm);;OpenXDF files(*.xdf);;ISHNE files(*.ecg)')
        # logger.debug(type(flname))
        if filname:
            flname = pathlib.PurePath(filname)
            logger.debug(type(flname))
            archname = platform.system()
            # import traceback
            try:
                # pasar path y tipo de archivo al control esperar estructura de datos (señal, canales, fs, size, date and time,
                # sex, resolucion ...)
                filedrv.openreg(filname, regtyp=fltyp)
                breakpoint()
                pass
            except Exception as ex:
                # todo: cual es la expt
                # traceback.format_exc()
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                logger.debug(message)
                logger.error('Opps!')
                pass
        else:
            logger.debug("Operation: 'Import' cancelled by user: file opening")
            pass
        # recibe estructura de datos y plotea canales

    def ls_beat(self):
        if self.lost_bt.isChecked:
            self.groupBox_lostbt.hide()
        else:
            self.groupBox_lostbt.show()

    # def closeEvent(self, event): # ui
    #     """"
    #     preguntar antes de salir
    #     """
    #     logger.debug("Cerrando app")
    #     choice = QtGui.QMessageBox.question(self, 'Salir',
    #                                         "Está cerrando la aplicación?, confirme",
    #                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    #     if choice == QtGui.QMessageBox.Yes:
    #         event.accept()
    #         logger.debug("app terminada")
    #     else:
    #         event.ignore()


class OptDialog(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(OptDialog, self).__init__(parent)
        self.setupUi(self)
        # aqui comienza la accion
        # self.sett_db__open_button.clicked.connect(self.open_db())
        self.sett_db__open_button.clicked.connect(lambda: self.open_db())
        self.sett_db__new_button.clicked.connect(lambda: self.new_db())
        # self.show()

    def open_db(self):
        # todo: how avoid open file dialog from crash when is aborted
        dbname = QFileDialog.getOpenFileName(caption='Abrir Registro', directory='/home',
                                             filter='Sqlite file:(*db)(*sqlite)(*db3)(*sqlite3)')
        if dbname:
            # dbname = pathlib.Path(dbname)
            # pasar el path al control de la DB
            pass
        else:
            logger.debug("db opening canceled by user")
            pass

    def new_db(self):
        # pasar el path al creador de DB y luego al control
        dbname = QFileDialog.getSaveFileName(caption='Crear Base de datos', directory='AppData/Local/PyECG/DB',
                                             filter='dbfile(*.db)')
        pass


# ----------------------------------------------------------------------------------------------------------------------


def main():
    """"
    Main Windows setup
    setup logger
    getting plataform
    """
    logging.basicConfig(level=logging.DEBUG)
    # archname = platform.system()
    # logger.debug(archname)
    app = QApplication(sys.argv)
    # app.setStyle("clearlooks")
    win = MainWindow()
    # control
    win.show()
    # terminacion
    sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
