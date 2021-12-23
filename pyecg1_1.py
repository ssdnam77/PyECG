#!

#The MIT License (MIT)
#
#Copyright (c) 2020 Universidad de Oriente & KU Leuven
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""
# Description: Berger's QTVI analysis
# Authors:
    - Alexander A. Suarez Leon
    - Sergio D. Sanchez Mercantete
    - Carolina Varon
    - Rik Willems
    - Sabine Van Huffel
    - Carlos R. Vazquez Seisdedos
# Date: 2020
# todo:
# notes:
_____
"""

# OS and platform imports
import pathlib
import logging
import platform

# Science package
from scipy.io.matlab import loadmat

# Qt imports
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenuBar, QMenu, QAction

# pyqtgraph
import pyqtgraph as pg
from pyqtgraph.dockarea import *
from pyqtgraph import DataTreeWidget
from pyqtgraph.Qt import QtGui, QtCore

# PyECG imports
from iomod.e3cm import E3cc
from tools.QTVI import BQTVI
from tools.QTRR import BQTRR
from tools.SQI import SQIObject
from tools.detc.detRw import Rwd
from tools.detc.detQw import Qwd
from tools.detc.detTf import Twd
from tools.filterc.filtertools import FilterTools

from utils.helpm import up4sample
from utils.misc import detectRealIdx
from utils.spectral import getspectrum
from utils.holders import OptionsHolder, CursorInfo

# dialogs
from selform import Ui_IntervalDialog
from optionsdialog import Ui_OptionsDialog
from svmHolder import *

logger = logging.getLogger()

# Define some functions

def ClickedLabel(ev):

    cInfo.setPoint(QtGui.QCursor.pos())
    dHolder.setLastEvent(ev.opts['name'])
    cmClassTMenu.popup(QtGui.QCursor.pos())


def computeQTVI():

    qtvicalc = BQTVI(0)

    tmp = dHolder.getQTTemplate()
    s = dHolder.getSignal()
    header = dHolder.getHeader()

    if dHolder.getLead() == 'A':
        s2 = s[0]
        r2 = s[2]
    else:
        s2 = s[1]
        r2 = s[3]

    ridx = tmp['Ridx']
    t2 = tmp['Toff']
    q2 = tmp['Qon']

    d6 = area.docks['QTVI Analysis']
    gb = d6.widgets[2]

    samp0 = gb.findChild(QtWidgets.QLineEdit, name="Sample0")
    lqtvi = gb.findChild(QtWidgets.QLabel, name="QTVIl")

    overlap = gb.findChild(QtWidgets.QSpinBox, name="spbOverlap")
    overValue = overlap.value()

    fs = header['Fs']

    if overValue < 0:

        if fs == 250:
            start = int(samp0.text()) * 4
            sf, rf, rkf, Tendf, QTkf = up4sample(s2, r2, r2[ridx], t2, t2-q2)
        else:
            start = int(samp0.text())
            sf = s2
            rf = r2
            rkf = r2[ridx]
            Tendf = t2
            QTkf = t2 - q2

        qtvival, _, _, _ = qtvicalc.BergerQTVI(sf, rf, rkf, Tendf, QTkf, start)

        lqtvi.setText(str.format("QTVI: {:.2f}", qtvival))

    else:

        if fs == 250:
            start = int(samp0.text()) * 4
            sf, rf, rkf, Tendf, QTkf = up4sample(s2, r2, r2[ridx], t2, t2-q2)
            fp = 4*fs
        else:
            start = int(samp0.text())
            sf = s2
            rf = r2
            rkf = r2[ridx]
            Tendf = t2
            QTkf = t2 - q2
            fp = fs

        T = sf.size
        I = start
        O = (1 - overValue/100)
        W = 256 * fp
        D = O * W
        N = np.fix((T - I)/D)

        n = int(N)

        qtvis = np.zeros(n)

        QT = None

        for i in range(0, n):
            qtvis[i], QT, _, _ = qtvicalc.BergerQTVI(sf, rf, rkf, Tendf, QTkf, I, fs, QT)
            I = I + D

        lqtvi.setText(str.format("QTVI: {:.2f}", qtvis[0]))

        drrqt = Dock("Multiple QTVI", size=(200, 600), closable=True)
        area.addDock(drrqt, 'left')

        # p2 = pg.PlotWidget()
        # p2.plot(rr_lin, pen='y', name="RR")
        # p2.showGrid(x=True, y=True)
        # p2.plotItem.setMenuEnabled(False)
        # p2.setWindowTitle("RR series")
        # p3 = pg.PlotWidget()
        # p3.plot(qt_lin, pen='r', name="QT")
        # p3.showGrid(x=True, y=True)
        # p3.plotItem.setMenuEnabled(False)
        # p3.setWindowTitle("QT series")
        p4 = pg.PlotWidget()
        p4.plot(qtvis, pen='r', name="QTVI")
        p4.showGrid(x=True, y=True)
        p4.plotItem.setMenuEnabled(False)
        p4.setWindowTitle("QTVI values")
        p4.plot(qtvis, pen=None, symbolBrush='r', symbolPen='w')
        # drrqt.addWidget(p2, row=0, col=0)
        # drrqt.addWidget(p3, row=1, col=0)
        drrqt.addWidget(p4, row=0, col=0)


def another(p):

    txt = p.data()
    txtnum = float(txt)

    wdw_st = txtnum - 2.5
    wdw_ed = txtnum + 2.5

    d3 = area.docks['Lead B']
    p3 = d3.widgets[0]
    p31 = d3.widgets[1]

    lr3 = p3.plotItem.items[1]

    lr3.setRegion([wdw_st, wdw_ed])


def another0(p):

    print("Hola")

    txt = p.data()
    txtnum = float(txt)

    wdw_st = txtnum - 2.5
    wdw_ed = txtnum + 2.5

    d2 = area.docks['Lead A']
    p3 = d2.widgets[0]
    p31 = d2.widgets[1]

    lr3 = p3.plotItem.items[1]

    lr3.setRegion([wdw_st, wdw_ed])

def doQTAprocess(p):

    qtrrcalc = BQTRR(0)
    QTInfo = dHolder.getQT()
    header = dHolder.getHeader()
    fs = header['Fs']

    tend = QTInfo['Toff']
    qon = QTInfo['Qon']
    r1 = QTInfo['Rp']


    if tend[-1] < r1[-1]:
        qend = qon.shape[0] -2
    else:
        qend = qon.shape[0] -1

    rr = np.diff(r1)

    st_q = 0

    while qon[st_q] < r1[0]:
        st_q = st_q + 1

    newtend = np.array(tend[st_q:-1])
    newqon = np.array(qon[st_q:qend])

    qt = (newtend - newqon) / fs

    dock = area.docks['QT Analysis']
    gbx = dock.widgets[2]

    cbprofile = gbx.findChild(QtWidgets.QComboBox, "cbp")
    elag = gbx.findChild(QtWidgets.QLineEdit, "lelag")

    prf = cbprofile.currentIndex()

    dlag = float(elag.text())

    if prf == 0:
        newrr = np.array(rr[(st_q - 1):-1], dtype=float) / fs
        anewrr = newrr.copy()
    elif prf == 1:
        r2 = np.array(r1, dtype=float) / fs
        newrr = qtrrcalc.compnewrr(dlag, r2)
        anewrr = np.array(newrr[(st_q - 1):-1])
    else:
        r2 = np.array(r1, dtype=float) / fs
        newrr = qtrrcalc.compnewrr(fs, r2, "exp")
        anewrr = np.array(newrr[(st_q - 1):-1])

    QTc = np.array(qt[anewrr > 0], dtype=float)
    RRi = np.array(anewrr[anewrr > 0], dtype=float)


    Methods = ["Linear", "Hyperbolic", "Parabolic-Log", "Logarithmic", "Shifthed logarithmic", "Exponential",
               "Arcus tangent", "Hyperbolic tangent", "Arcus hyperbolic sine", "Arcus hyperbolic cosine"]

    pear_rp = np.zeros(10)
    j = 0

    for me in Methods:
        pqt, x, y, rp, pval = qtrrcalc.fitmodelQTRR(RRi, QTc, me)
        pear_rp[j] = rp
        j = j + 1

    idx = np.intp(np.nanargmax(pear_rp))

    pqt, x, y, rp, pval = qtrrcalc.fitmodelQTRR(RRi, QTc, Methods[idx])

    p3 = pg.PlotWidget(name="QTRR")
    p3.plot(RRi, QTc, pen=None, symbol='t', symbolPen=None, symbolSize=10, symbolBrush=(100, 100, 255, 50))

    rr_x, qt_y = qtrrcalc.evalmodelQTRR(newrr, pqt, Methods[idx])

    p3.plot(rr_x, qt_y, pen=(200, 200, 200), name="RBL2")

    p3.setLabel('left', "QT", units='s')
    p3.setLabel('bottom', "RR", units='s')

    frame = QtWidgets.QFrame()

    gridlayout = QtWidgets.QGridLayout()

    frame.setLayout(gridlayout)

    gridlayout.addWidget(p3, 0, 0, 1, -1, Qt.Alignment(132))

    lmodel = QtWidgets.QLabel(text="<b>Models:<\b>")
    ltext = QtWidgets.QLabel(text="<b>Parameters:<\b>")
    ltalphaval = QtWidgets.QLabel(text=str.format("Alpha: {:.2f}", pqt[0]))
    ltalphaval.setObjectName("ltalphaval")
    ltbetaval = QtWidgets.QLabel(text=str.format("Beta: {:.2f}", pqt[1]))
    ltbetaval.setObjectName("ltbetaval")
    ltrval = QtWidgets.QLabel(text=str.format("Pearson CC (r): {:.2f}", rp))
    ltrval.setObjectName("ltrval")

    cb = QtWidgets.QComboBox()
    cb.setObjectName("cbmodel")

    cb.addItems(["Linear", "Hyperbolic", "Parabolic-Log", "Logarithmic", "Shifthed logarithmic", "Exponential",
                 "Arcus tangent", "Hyperbolic tangent", "Arcus hyperbolic sine", "Arcus hyperbolic cosine"])

    gridlayout.addWidget(lmodel, 1, 0)
    gridlayout.addWidget(ltext, 1, 1)
    gridlayout.addWidget(cb, 2, 0)
    gridlayout.addWidget(ltalphaval, 2, 1)
    gridlayout.addWidget(ltbetaval, 3, 1)
    gridlayout.addWidget(ltrval, 4, 1)

    cb.setCurrentIndex(idx)
    cb.currentIndexChanged.connect(cbmodelChange)

    d = area.docks['QT Analysis']
    d.addWidget(frame, row=1, col=1, colspan=2)

    infoqt = {'Rp': r1, 'Qon': qon, 'Toff': tend, 'RR': RRi, 'QT': QTc}
    dHolder.setQT(infoqt)


def cbmodelChange(p):

    qtrrcalc = BQTRR(0)

    d = area.docks['QT Analysis']

    fr = d.widgets[3]

    cbmodel = fr.findChild(QtWidgets.QComboBox, name="cbmodel")

    ltalphaval = fr.findChild(QtWidgets.QLabel, name="ltalphaval")
    ltbetaval = fr.findChild(QtWidgets.QLabel, name="ltbetaval")
    ltrval = fr.findChild(QtWidgets.QLabel, name="ltrval")

    p3 = fr.findChild(pg.PlotWidget)

    p3.removeItem(p3.plotItem.items[-1])

    model = cbmodel.currentText()

    QTInfo = dHolder.getQT()

    rr = QTInfo['RR']
    qt = QTInfo['QT']

    pqt, x, y, rp, pval = qtrrcalc.fitmodelQTRR(rr, qt, model)

    ltalphaval.setText(str.format("Alpha: {:.4f}", pqt[0]))
    ltbetaval.setText(str.format("Beta: {:.4f}", pqt[1]))
    ltrval.setText(str.format("Pearson CC (r): {:.2f}", rp))

    rr_x, qt_y = qtrrcalc.evalmodelQTRR(rr, pqt, model)

    p3.plot(rr_x, qt_y, pen=(200, 200, 200), name="RBL2")


def LeadASelectedQTVI():

    print("Lead A was selected")

    dHolder.setA()

    s = dHolder.getSignal()

    t = dHolder.getTime()

    y1 = s[0]
    r1 = s[2]

    d6 = Dock("QTVI Analysis", size=(1000, 600))
    area.addDock(d6, 'top')

    p2 = pg.PlotWidget()
    p2.plot(t, y1, pen=(0, 0, 255), name="RBL1")
    p2.showGrid(x=True, y=True)
    p2.plotItem.setMenuEnabled(False)

    # Draw the whole data block

    lr2 = pg.LinearRegionItem(values=[0, 1])
    lr2.setZValue(-10)
    p2.addItem(lr2)

    p2.plot(t[r1], y1[r1], pen=None, symbolBrush=(0, 0, 255), symbolPen='w', name="RBL3")

    p21 = pg.PlotWidget()
    p21.plot(t, y1, pen=(0, 0, 255), name="RBL2")
    p21.showGrid(x=True, y=True)
    p21.plotItem.setMenuEnabled(False)

    gb = QtWidgets.QGroupBox("Options panel")

    ly = QtWidgets.QGridLayout()

    qlR = QtWidgets.QLabel("R: ")
    qlR.setFixedWidth(30)
    qlcdR = QtWidgets.QLabel()
    qlcdR.setObjectName("lcdR")
    qlcdR.setFixedWidth(50)

    ly.addWidget(qlR, 1, 0)
    ly.addWidget(qlcdR, 1, 1)

    qlQon = QtWidgets.QLabel("Q-on: ")
    qlQon.setFixedWidth(30)
    qlcdQon = QtWidgets.QLabel()
    qlcdQon.setObjectName("lcdQ")
    qlcdQon.setFixedWidth(50)

    ly.addWidget(qlQon, 0, 0)
    ly.addWidget(qlcdQon, 0, 1)

    qlToff = QtWidgets.QLabel("T-off: ")
    qlToff.setFixedWidth(30)
    qlcdToff = QtWidgets.QLabel()
    qlcdToff.setObjectName("lcdT")
    qlcdToff.setFixedWidth(50)

    ly.addWidget(qlToff, 0, 2)
    ly.addWidget(qlcdToff, 0, 3)

    qlQT = QtWidgets.QLabel("QT: ")
    qlQT.setFixedWidth(30)
    qlcdQT = QtWidgets.QLabel()
    qlcdQT.setObjectName("lcdQT")
    qlcdQT.setFixedWidth(50)

    ly.addWidget(qlQT, 1, 2)
    ly.addWidget(qlcdQT, 1, 3)

    ltsSample0 = QtWidgets.QLabel("Start sample: ")
    ltsSample0.setFixedWidth(100)
    tesetSample0 = QtWidgets.QLineEdit("0")
    tesetSample0.setAlignment(Qt.Alignment(130))

    tesetSample0.setFixedWidth(80)
    tesetSample0.setObjectName("Sample0")

    ly.addWidget(ltsSample0, 0, 4)
    ly.addWidget(tesetSample0, 0, 5)

    ltsSample = QtWidgets.QLabel("Set start sample: ")
    ltsSample.setFixedWidth(100)
    pbsetSample = QtWidgets.QPushButton("...")
    pbsetSample.setFixedWidth(50)

    ly.addWidget(ltsSample, 1, 4)
    ly.addWidget(pbsetSample, 1, 5)

    ltsOverl = QtWidgets.QLabel("Set overlap: ")
    ltsOverl.setFixedWidth(100)
    spOverl = QtWidgets.QSpinBox()
    spOverl.setMinimum(-1)
    spOverl.setMaximum(99)
    spOverl.setValue(-1)
    spOverl.setFixedWidth(70)
    spOverl.setObjectName("spbOverlap")

    ly.addWidget(ltsOverl, 0, 6)
    ly.addWidget(spOverl, 0, 7)

    pbQTVI = QtWidgets.QPushButton("QTVI")
    pbQTVI.clicked.connect(computeQTVI)
    pbQTVI.setObjectName("QTVIbtn")

    lQTVI = QtWidgets.QLabel("")
    lQTVI.setObjectName("QTVIl")

    ly.addWidget(lQTVI, 1, 6)
    ly.addWidget(pbQTVI, 1, 7)

    gb.setLayout(ly)

    d6.addWidget(p2, row=0, col=0)
    d6.addWidget(p21, row=1, col=0)
    d6.addWidget(gb, row=2, col=0)

    lr2.sigRegionChanged.connect(updateplot3)
    p21.sigXRangeChanged.connect(updateregion3)

    p21hdl1 = p21.plot(t[r1], y1[r1], pen=None, symbolBrush=(0, 0, 255), symbolPen='w', name="RBL3")
    p21hdl1.sigClicked.connect(ClickedQTVI)


def LeadBSelectedQTVI():

    dHolder.setB()

    s = dHolder.getSignal()

    t = dHolder.getTime()

    y1 = s[1]
    r1 = s[3]

    d6 = Dock("QTVI Analysis", size=(1000, 600))
    area.addDock(d6, 'top')

    p2 = pg.PlotWidget()
    p2.plot(t, y1, pen=(0, 0, 255), name="RBL1")
    p2.showGrid(x=True, y=True)
    p2.plotItem.setMenuEnabled(False)

    # Draw the whole data block

    lr2 = pg.LinearRegionItem(values=[0, 1])
    lr2.setZValue(-10)
    p2.addItem(lr2)

    p2.plot(t[r1], y1[r1], pen=None, symbolBrush=(0, 0, 255), symbolPen='w', name="RBL3")

    p21 = pg.PlotWidget()
    p21.plot(t, y1, pen=(0, 0, 255), name="RBL2")
    p21.showGrid(x=True, y=True)
    p21.plotItem.setMenuEnabled(False)

    gb = QtWidgets.QGroupBox("Options panel")

    ly = QtWidgets.QGridLayout()

    qlR = QtWidgets.QLabel("R: ")
    qlR.setFixedWidth(30)
    qlcdR = QtWidgets.QLabel()
    qlcdR.setObjectName("lcdR")
    qlcdR.setFixedWidth(50)

    ly.addWidget(qlR, 1, 0)
    ly.addWidget(qlcdR, 1, 1)

    qlQon = QtWidgets.QLabel("Q-on: ")
    qlQon.setFixedWidth(30)
    qlcdQon = QtWidgets.QLabel()
    qlcdQon.setObjectName("lcdQ")
    qlcdQon.setFixedWidth(50)

    ly.addWidget(qlQon, 0, 0)
    ly.addWidget(qlcdQon, 0, 1)

    qlToff = QtWidgets.QLabel("T-off: ")
    qlToff.setFixedWidth(30)
    qlcdToff = QtWidgets.QLabel()
    qlcdToff.setObjectName("lcdT")
    qlcdToff.setFixedWidth(50)

    ly.addWidget(qlToff, 0, 2)
    ly.addWidget(qlcdToff, 0, 3)

    qlQT = QtWidgets.QLabel("QT: ")
    qlQT.setFixedWidth(30)
    qlcdQT = QtWidgets.QLabel()
    qlcdQT.setObjectName("lcdQT")
    qlcdQT.setFixedWidth(50)

    ly.addWidget(qlQT, 1, 2)
    ly.addWidget(qlcdQT, 1, 3)

    ltsSample0 = QtWidgets.QLabel("Start sample: ")
    ltsSample0.setFixedWidth(100)
    tesetSample0 = QtWidgets.QLineEdit("0")
    tesetSample0.setAlignment(Qt.Alignment(130))

    tesetSample0.setFixedWidth(80)
    tesetSample0.setObjectName("Sample0")

    ly.addWidget(ltsSample0, 0, 4)
    ly.addWidget(tesetSample0, 0, 5)

    ltsSample = QtWidgets.QLabel("Set start sample: ")
    ltsSample.setFixedWidth(100)
    pbsetSample = QtWidgets.QPushButton("...")
    pbsetSample.setFixedWidth(50)

    ly.addWidget(ltsSample, 1, 4)
    ly.addWidget(pbsetSample, 1, 5)

    ltsOverl = QtWidgets.QLabel("Set overlap: ")
    ltsOverl.setFixedWidth(100)
    spOverl = QtWidgets.QSpinBox()
    spOverl.setMinimum(-1)
    spOverl.setMaximum(99)
    spOverl.setValue(-1)
    spOverl.setFixedWidth(70)
    spOverl.setObjectName("spbOverlap")

    ly.addWidget(ltsOverl, 0, 6)
    ly.addWidget(spOverl, 0, 7)

    pbQTVI = QtWidgets.QPushButton("QTVI")
    pbQTVI.clicked.connect(computeQTVI)
    pbQTVI.setObjectName("QTVIbtn")

    lQTVI = QtWidgets.QLabel("")
    lQTVI.setObjectName("QTVIl")

    ly.addWidget(lQTVI, 1, 6)
    ly.addWidget(pbQTVI, 1, 7)

    gb.setLayout(ly)

    d6.addWidget(p2, row=0, col=0)
    d6.addWidget(p21, row=1, col=0)
    d6.addWidget(gb, row=2, col=0)

    lr2.sigRegionChanged.connect(updateplot3)
    p21.sigXRangeChanged.connect(updateregion3)

    p21hdl1 = p21.plot(t[r1], y1[r1], pen=None, symbolBrush=(0, 0, 255), symbolPen='w', name="RBL3")
    p21hdl1.sigClicked.connect(ClickedQTVI)


def doQTAnalysisLeadA():

    qw = Qwd(0)
    tw = Twd(0)

    s = dHolder.getSignal()
    head = dHolder.getHeader()
    fs = head['Fs']

    t = dHolder.getTime()

    y1 = s[0]
    r1 = s[2]

    d6 = Dock("QT Analysis", size=(1000, 600))
    area.addDock(d6, 'top')

    p2 = pg.PlotWidget()
    p2.plot(t, y1, pen=(200, 200, 200), name="RBL1")
    p2.showGrid(x=True, y=True)
    p2.plotItem.setMenuEnabled(False)

    # Draw the whole data block

    lr2 = pg.LinearRegionItem(values=[0, 1])
    lr2.setZValue(-10)
    p2.addItem(lr2)

    p2.plot(t[r1], y1[r1], pen=None, symbolBrush=(255, 255, 255), symbolPen='w', name="RBL3")

    p21 = pg.PlotWidget()
    p21.plot(t, y1, pen=(200, 200, 200), name="RBL2")
    p21.showGrid(x=True, y=True)
    p21.plotItem.setMenuEnabled(False)

    tend = tw.globalzhangTend(y1, r1, fs=fs)
    qon  = qw.globalinitq(y1, r1, fs=fs)

    plotR = p21.plot(t[r1], y1[r1], pen=None, symbolBrush=(255, 255, 255), symbolPen='w', name="WR1")
    plotT = p21.plot(t[tend], y1[tend], pen=None, symbolBrush=(0, 0, 255), symbolPen='b', name="BT1")
    plotQ = p21.plot(t[qon], y1[qon], pen=None, symbolBrush=(0, 255, 0), symbolPen='g', name="GQ1")

    plotR.sigClicked.connect(Clicked)
    plotT.sigClicked.connect(Clicked)
    plotQ.sigClicked.connect(Clicked)

    agb = QtWidgets.QGroupBox("Control panel/Analysis parameters")
    agbl = QtWidgets.QGridLayout()
    agb.setLayout(agbl)

    lblpro = QtWidgets.QLabel("RRi profile")
    lblpro.setFixedHeight(20)
    lblpro.setFixedWidth(100)

    cbprofile = QtWidgets.QComboBox()

    cbprofile.addItems(["QT-RR", "QT-RRi-LW",  "QT-RRi-EW"])
    cbprofile.setCurrentIndex(0)
    cbprofile.setObjectName("cbp")

    agbl.addWidget(lblpro)
    agbl.addWidget(cbprofile, 1, 0, Qt.Alignment(132))

    lbltlag = QtWidgets.QLabel("Time Lag (s):")
    lbltlag.setFixedHeight(20)
    lbltlag.setFixedWidth(100)

    letlag = QtWidgets.QLineEdit("0")
    letlag.setFixedHeight(20)
    letlag.setFixedWidth(100)
    letlag.setObjectName("lelag")

    agbl.addWidget(lbltlag, 0, 2, Qt.Alignment(132))
    agbl.addWidget(letlag, 1, 2, Qt.Alignment(132))

    pbCalc = QtWidgets.QPushButton("QT/RR Analysis")

    pbCalc.setFixedWidth(100)
    pbCalc.setFixedHeight(25)

    pbCalc.clicked.connect(doQTAprocess)

    agbl.addWidget(pbCalc, 1, 3, Qt.Alignment(132))

    d6.addWidget(p2, row=0, col=0)
    d6.addWidget(p21, row=1, col=0)
    d6.addWidget(agb, row=2,  col=0)
    #
    lr2.sigRegionChanged.connect(updateplot4)
    p21.sigXRangeChanged.connect(updateregion4)

    infoqt = {'Rp': r1, 'Qon': qon, 'Toff': tend}
    dHolder.setQT(infoqt)


def doQTAnalysisLeadB():

    print("doQTAnalysis")

    qw = Qwd(0)
    tw = Twd(0)

    s = dHolder.getSignal()
    head = dHolder.getHeader()
    fs = head['Fs']

    t = dHolder.getTime()

    y1 = s[1]
    r1 = s[3]

    d6 = Dock("QT Analysis", size=(1000, 600))
    area.addDock(d6, 'top')

    p2 = pg.PlotWidget()
    p2.plot(t, y1, pen=(200, 200, 200), name="RBL1")
    p2.showGrid(x=True, y=True)
    p2.plotItem.setMenuEnabled(False)

    # Draw the whole data block

    lr2 = pg.LinearRegionItem(values=[0, 1])
    lr2.setZValue(-10)
    p2.addItem(lr2)

    p2.plot(t[r1], y1[r1], pen=None, symbolBrush=(255, 255, 255), symbolPen='w', name="RBL3")

    p21 = pg.PlotWidget()
    p21.plot(t, y1, pen=(200, 200, 200), name="RBL2")
    p21.showGrid(x=True, y=True)
    p21.plotItem.setMenuEnabled(False)

    tend = tw.globalzhangTend(y1, r1, fs=fs)
    qon  = qw.globalinitq(y1, r1, fs=fs)

    p21.plot(t[r1], y1[r1], pen=None, symbolBrush=(255, 255, 255), symbolPen='w', name="WR2")
    p21.plot(t[tend], y1[tend], pen=None, symbolBrush=(0, 0, 255), symbolPen='b', name="BT2")
    p21.plot(t[qon], y1[qon], pen=None, symbolBrush=(0, 255, 0), symbolPen='g', name="GQ2")

    agb = QtWidgets.QGroupBox("Control panel/Analysis parameters")
    agbl = QtWidgets.QGridLayout()
    agb.setLayout(agbl)

    lblpro = QtWidgets.QLabel("RRi profile")
    lblpro.setFixedHeight(20)
    lblpro.setFixedWidth(100)

    cbprofile = QtWidgets.QComboBox()

    cbprofile.addItems(["QT-RR", "QT-RRi-LW",  "QT-RRi-EW"])
    cbprofile.setCurrentIndex(0)
    cbprofile.setObjectName("cbp")

    agbl.addWidget(lblpro)
    agbl.addWidget(cbprofile, 1, 0, Qt.Alignment(132))

    lbltlag = QtWidgets.QLabel("Time Lag (s):")
    lbltlag.setFixedHeight(20)
    lbltlag.setFixedWidth(100)

    letlag = QtWidgets.QLineEdit("0")
    letlag.setFixedHeight(20)
    letlag.setFixedWidth(100)
    letlag.setObjectName("lelag")

    agbl.addWidget(lbltlag, 0, 2, Qt.Alignment(132))
    agbl.addWidget(letlag, 1, 2, Qt.Alignment(132))

    pbCalc = QtWidgets.QPushButton("QT/RR Analysis")

    pbCalc.setFixedWidth(100)
    pbCalc.setFixedHeight(25)

    pbCalc.clicked.connect(doQTAprocess)

    agbl.addWidget(pbCalc, 1, 3, Qt.Alignment(132))

    d6.addWidget(p2, row=0, col=0)
    d6.addWidget(p21, row=1, col=0)
    d6.addWidget(agb, row=2,  col=0)
    #
    lr2.sigRegionChanged.connect(updateplot4)
    p21.sigXRangeChanged.connect(updateregion4)

    infoqt = {'Rp': r1, 'Qon': qon, 'Toff': tend}
    dHolder.setQT(infoqt)


def openfile():
    """"
           load recording
    """
    logger.debug("Cargando archivo")
    # pasar tipo de archivo para decidir como se abrirá
    # check que el archivo exista
    filname, fltyp = QtGui.QFileDialog.getOpenFileName(caption='Importar registro', directory='/home',
                                                 filter='Excorder3C files(*.e3c);;DICOM files'
                                                        '(*.dcm);;OpenXDF files(*.xdf);;ISHNE files(*.ecg);;MATLAB files(*.mat)')
    # logger.debug(type(flname))
    if filname:
        flname = pathlib.PurePath(filname)
        logger.debug(type(flname))
        archname = platform.system()
        # import traceback
        try:
            # pasar path y tipo de archivo al control esperar estructura de datos (señal, canales, fs, size, date and time,
            # sex, resolucion ...)
            path = pathlib.PurePath(flname)
            if path.suffix == '.e3c':
                "E3C reg"

                idqd = QtWidgets.QDialog()
                ui = Ui_IntervalDialog()
                ui.setupUi(idqd)
                result = idqd.exec_()

                if result:
                    h_start = ui.spbh_start.value()
                    m_start = ui.spbm_start.value()
                    s_start = ui.spbs_start.value()

                    h_stop = ui.spbh_stop.value()
                    m_stop = ui.spbm_stop.value()
                    s_stop = ui.spbs_stop.value()

                    start_p = h_start * 3600 + m_start * 60 + s_start
                    stop_p = h_stop * 3600 + m_stop * 60 + s_stop

                    if stop_p < start_p:
                        long = stop_p
                    else:
                        long = stop_p - start_p

                    abs_start = start_p
                    abs_long = long

                    arch = platform.system()
                    e3cins = E3cc()

                    header, ecg = e3cins.reade3c(path, arch, abs_start, abs_long)

                    time_len = ecg.shape[1]
                    time_len = float(time_len) / 250.0

                    step = 1 / 250.0
                    fin = time_len

                    t = np.arange(0, fin, step)

                    y1 = ecg[0][:]
                    y2 = ecg[1][:]

                    return 1, (header, t, y1, y2)

                else:
                    return 0, 0

            elif path.suffix == '.dcm':
                "DICOM std"
                #header
                pass
            elif path.suffix == '.ecg':
                "ISHNE std"

                pass
            elif path.suffix == '.xdf':
                "OpenXDF"
                pass
            elif path.suffix == '.mat':

                mat = loadmat(filname)

                ecg = mat['ecg']
                fs = float(mat['fs'][0])

                time_len = ecg.shape[1]
                samples = time_len
                fin = float(time_len) / fs

                t = np.linspace(0, fin, num=time_len, endpoint=False)

                y1 = ecg[0][:]
                y2 = ecg[1][:]

                header = {'Channels': 2, 'Fs': fs}

                ns = samples / fs
                nm = int(ns / 60)
                nh = int(ns / 3600)

                nh1 = nh
                nm1 = int((ns - nh * 3600) / 60)
                ns1 = (ns - nh1 * 3600 - nm1 * 60)

                header['Hours'] = nh1

                header['Minutes'] = nm1

                header['Seconds'] = int(ns1)

                header['Samples'] = int(samples)

                header['AnnData'] = {}

                header['Start'] = 0

                header['Length'] = time_len

                header['FileName'] = filname

                return 1, (header, t, y1, y2)

            # filedrv.openreg(filname, regtyp=fltyp)
            # breakpoint()
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

    return 0, 0

def Clicked(ev):

    dHolder.setLastEvent(ev.opts['name'])

    if cInfo.getCross():
        cInfo.setCross(False)
    else:
        cInfo.setPoint(QtGui.QCursor.pos())
        cmToolMenu.popup(QtGui.QCursor.pos())


def ClickedQTVI(ev):

    cInfo.setPoint(QtGui.QCursor.pos())
    cmQTVIMenu.popup(QtGui.QCursor.pos())


def setProcActions(enval = False):

    save.setEnabled(enval)
    viewspa.setEnabled(enval)
    viewpaa.setEnabled(enval)
#    detectihba.setEnabled(enval)
#    loadlia.setEnabled(enval)
    detecta.setEnabled(enval)
    loadva.setEnabled(enval)

def buildSpectrumDock(y1, y2, fs, nonew = True):

    if dHolder.getProcessing():

        if nonew:

            d4 = area.docks['Spectrum']
            d4.widgets.clear()
        else:

            d4 = Dock("Spectrum", size=(200, 600), closable=True)
            d4.sigClosed.connect(closeSpectrumDock)
            area.addDock(d4, 'right')

        p4 = pg.PlotWidget(title="Power spectrum Lead A")
        fx, px = getspectrum(y1, fs, False)
        p4.plot(fx, px, pen=(255, 255, 255), name="Power spectrum")
        p4.showGrid(x=True, y=True)

        p5 = pg.PlotWidget(title="Power spectrum Lead B")
        fx, px = getspectrum(y2, fs, False)
        p5.plot(fx, px, pen=(255, 255, 255), name="Power spectrum")
        p5.showGrid(x=True, y=True)

        d4.addWidget(p4, row=0, col=0)
        d4.addWidget(p5, row=1, col=0)

        dHolder.setViewSpectrum(True)

def closeSpectrumDock(obj):

    dHolder.setViewSpectrum(False)

def closeInfoDock(obj):

    dHolder.setViewInfoPanel(False)

def buildInfoDock(nonew = True):

    if dHolder.getProcessing():

        if nonew:

            d1 = area.docks['Info panel']
            d1.widgets.clear()
        else:

            d1 = Dock("Info panel", size=(200, 600), closable=True)
            d1.sigClosed.connect(closeInfoDock)
            area.addDock(d1, 'right')

        dtw = DataTreeWidget()
        dtw.setData(dHolder.getRR(), True)
        dtw.setColumnCount(3)
        dtw.setHeaderLabels(['Name', 'Type', 'Value'])
        d1.addWidget(dtw, row=0, col=0)

        dHolder.setViewInfoPanel(True)

# Menu handlers

def procTriggerFile(q):

    if q.text() == 'Open':

        result, mydata = openfile()

        if result == 1:

            header = mydata[0]

            t = mydata[1]

            y1 = mydata[2]
            y2 = mydata[3]

            if dHolder.getViewInfoPanell():

                d1 = Dock("Data", size=(200, 600), closable=True)
                area.addDock(d1, 'left')
                dtw = DataTreeWidget()

                #dtw.setData(header, True)

                dtw.setColumnCount(3)
                dtw.setHeaderLabels(['Name', 'Type', 'Value'])
                d1.addWidget(dtw, row=0, col=0)

            d2 = Dock("Lead A", size=(1000, 600))
            d3 = Dock("Lead B", size=(1000, 600))

            area.addDock(d2, 'right')  ## place d2 at right edge of dock area
            area.addDock(d3, 'bottom', d2)  ## place d3 at right edge of dock area

            p2 = pg.PlotWidget()
            p2hdl1 = p2.plot(t, y1, pen='y', name="RB1")
            p2.showGrid(x=True, y=True)
            p2.plotItem.setMenuEnabled(False)

            # Draw the whole data block

            lr2 = pg.LinearRegionItem([0, 5])
            lr2.setZValue(-10)
            p2.addItem(lr2)

            p21 = pg.PlotWidget()
            p21hdl1 = p21.plot(t, y1, pen='y', name="RB2")
            p21.showGrid(x=True, y=True)
            p21.plotItem.setMenuEnabled(False)

            lr2.sigRegionChanged.connect(updateplot1)
            p21.sigXRangeChanged.connect(updateregion1)

            p3 = pg.PlotWidget()
            p3hdl1 = p3.plot(t, y2, pen='m', name="GB1")
            p3.showGrid(x=True, y=True)
            p3.plotItem.setMenuEnabled(False)

            lr3 = pg.LinearRegionItem([0, 5])
            lr3.setZValue(-10)
            p3.addItem(lr3)

            p31 = pg.PlotWidget()
            p31hdl1 = p31.plot(t, y2, pen='m', name="GB2")
            p31.showGrid(x=True, y=True)
            p31.plotItem.setMenuEnabled(False)

            lr3.sigRegionChanged.connect(updateplot2)
            p31.sigXRangeChanged.connect(updateregion2)

            d2.addWidget(p2, row=0, col=0)
            d2.addWidget(p21, row=1, col=0)
            d3.addWidget(p3, row=0, col=0)
            d3.addWidget(p31, row=1, col=0)

            updateplot1()
            updateplot2()

            dHolder.setHeader(header)
            dHolder.setTime(t)
            dHolder.setSignal([y1, y2])
            dHolder.setProcessing(True)
            setProcActions(dHolder.getProcessing())

            if dHolder.getViewSpectrum():
               buildSpectrumDock(y1, y2, header['Fs'])

    elif q.text() == 'Save':

        filname, fltyp = QtGui.QFileDialog.getSaveFileName(caption='Guardar resultados', directory='/home',
                                                           filter='MATLAB files(*.mat);; JSON files(*.json)')
        if filname:
            dHolder.saveToFile(filname)

    elif q.text() == 'Options':

        idqd = QtWidgets.QDialog()
        ui = Ui_OptionsDialog()
        ui.setupUi(idqd)
        result = idqd.exec_()

        if result:
            dHolder.setFilter(ui.cbfilter.currentIndex())
            dHolder.setRDet(ui.cbrdet.currentIndex())
            dHolder.setLeadCode(ui.rbleada.isChecked() + ui.rbleadb.isChecked() * 2)

    else:

        quit(0)

def procTriggerEdit(q):

    ft = FilterTools(0)
    rd = Rwd(0)
    sq = SQIObject(0)

    if q.text() == 'Detect R':

        header = dHolder.getHeader()
        t = dHolder.getTime()

        s = dHolder.getSignal()

        y1 = s[0]
        y2 = s[1]

        fs = header['Fs']

        if dHolder.getFiltered():

            y1f = ft.notchfilter(y1, fs, 60.0, 6.0)
            y2f = ft.notchfilter(y2, fs, 60.0, 6.0)

            y1f2 = ft.medianfilter(y1f, fs)
            y2f2 = ft.medianfilter(y2f, fs)

            if dHolder.getFilter() == 0:

                y1f3 = ft.filterbut4(y1f2, fs, 0.05, 50.0)
                y2f3 = ft.filterbut4(y2f2, fs, 0.05, 50.0)

            else:

                y1f3 = ft.filterfir(y1f2, fs, 0.05, 50.0)
                y2f3 = ft.filterfir(y2f2, fs, 0.05, 50.0)

            dHolder.setFiltered(True)

        else:

            y1f3 = y1
            y2f3 = y2

        if dHolder.SelRDet == 0:
            r1, y1f4 = rd.detqrs(y1f3, fs)
            r2, y2f4 = rd.detqrs(y2f3, fs)
        else:
            r1, y1f4 = rd.rpeak(y1f3, fs)
            r2, y2f4 = rd.rpeak(y2f3, fs)

        # Update plots

        d2 = area.docks['Lead A']

        p2 = d2.widgets[0]
        p21 = d2.widgets[1]

        lr2 = p2.plotItem.items[1]

        p2.plotItem.clear()

        p2.plot(t, y1f4, pen='y', name="RB1")
        p2.addItem(lr2)

        p2.plot(t[r1], y1f4[r1], pen=None, symbolBrush='y', symbolPen='w', name="RB3")

        p21.plotItem.clear()

        p21.plot(t, y1f4, pen='y', name="RB2")

        p21hdl1 = p21.plot(t[r1], y1f4[r1], pen=None, symbolBrush='y', symbolPen='w', name="RB4")
        p21hdl1.sigClicked.connect(Clicked)
        #p21hdl1.sigPointsClicked.connect(ClickedPoints)

        lr2.sigRegionChanged.connect(updateplot1)
        p21.sigXRangeChanged.connect(updateregion1)

        d3 = area.docks['Lead B']

        p3 = d3.widgets[0]
        p31 = d3.widgets[1]

        lr3 = p3.plotItem.items[1]

        p3.plotItem.clear()

        p3.plot(t, y2f4, pen='m', name="GB1")
        p3.addItem(lr3)

        p3.plot(t[r2], y2f4[r2], pen=None, symbolBrush='m', symbolPen='w', name="GB3")

        p31.plotItem.clear()
        p31.plot(t, y2f4, pen='m', name="GB2")

        p31hdl1 = p31.plot(t[r2], y2f4[r2], pen=None, symbolBrush='m', symbolPen='w', name="GB4")
        p31hdl1.sigClicked.connect(Clicked)
        #p31hdl1.sigPointsClicked.connect(ClickedPoints)

        lr3.sigRegionChanged.connect(updateplot2)
        p31.sigXRangeChanged.connect(updateregion2)

        if dHolder.getViewSpectrum():
            buildSpectrumDock(y1f4, y2f4, fs)

        cnt, des = sq.doSQA(y1f4, y2f4, r1, r2, fs)
        cnt = cnt + des

        dHolder.setSignal([y1f4, y2f4, r1, r2, cnt])

        qtaa.setEnabled(True)
        qtvia.setEnabled(True)
        dHolder.setFiltered(True)

        d0 = np.diff(r1)
        md0 = np.median(d0)
        sd0 = np.std(d0)

        c = np.fix(0.5 * md0 / sd0)
        thrd01 = np.sum(d0 < (md0 - c*sd0))
        thrd02 = np.sum(d0 > (md0 + c*sd0))

        if thrd01 + thrd02 > 0:

            d011 = np.argsort(d0)

            if thrd01 > 0:
                d012 = d011[0:thrd01]
                wd0 = 0.5 * (r1[d012] + r1[d012+1])
            else:
                wd0 = np.array([])

            if thrd02 > 0:
                d013 = d011[-thrd02:]
                md2 = 0.5 * (r1[d013] + r1[d013])
            else:
                md2 = np.array([])

            QLead1 = {'MinValues': wd0, 'MaxValues': md2}

            dHolder.setOutLier('Lead A', QLead1)

            rowval = 0

            if np.any(wd0):
                qf01 = QtWidgets.QFrame()
                qf01lm = QtWidgets.QGridLayout()

                qf01.setLayout(qf01lm)

                ql01 = QtWidgets.QListWidget()
                ql01.setFixedWidth(100)
                ql01.setFixedHeight(50)

                wdl0 = wd0.size

                for i in range(wdl0):
                    ql01.addItem(str.format("{:.2f}", wd0[i] / 250))

                lbl01 = QtWidgets.QLabel("Wrong Peaks")
                lbl01.setFixedHeight(20)
                lbl01.setFixedWidth(100)

                qf01lm.addWidget(lbl01)
                qf01lm.addWidget(ql01, 1, 0, Qt.Alignment(36))

                ql01.clicked.connect(another0)
                d2.addWidget(qf01, row=rowval, col=1)
                rowval = rowval + 1

            if np.any(md2):
                qf02 = QtWidgets.QFrame()
                qf02lm = QtWidgets.QGridLayout()

                qf02.setLayout(qf02lm)

                ql02 = QtWidgets.QListWidget()
                ql02.setFixedWidth(100)
                ql02.setFixedHeight(50)

                mdl0 = md0.size

                for i in range(mdl0):
                    ql02.addItem(str.format("{:.2f}", md2[i] / 250))

                lbl02 = QtWidgets.QLabel("Missing Peaks")
                lbl02.setFixedHeight(20)
                lbl02.setFixedWidth(100)

                qf02lm.addWidget(lbl02)
                qf02lm.addWidget(ql02, 1, 0, Qt.Alignment(36))

                ql02.clicked.connect(another0)
                d2.addWidget(qf02, row=rowval, col=1)

        d1 = np.diff(r2)
        md1 = np.median(d1)
        sd1 = np.std(d1)

        c = np.fix(0.5 * md1 / sd1)
        thrd1 = np.sum(d1 < (md1 - c*sd1))
        thrd2 = np.sum(d1 > (md1 + c*sd1))

        if thrd1+thrd2 > 0:

            d11 = np.argsort(d1)

            if thrd1 > 0:
                d12 = d11[0:thrd1]
                wd = 0.5 *(r2[d12] + r2[d12 + 1])
            else:
                wd = np.array([])

            if thrd2 > 0:
                d13 = d11[-thrd2:]
                md = 0.5 *(r2[d13] + r2[d13 + 1])
            else:
                md = np.array([])


            QLead2 = {'MinValues': wd, 'MaxValues': md}

            dHolder.setOutLier('Lead B', QLead2)

            rowval = 0

            if np.any(wd):
                qf1 = QtWidgets.QFrame()
                qf1lm = QtWidgets.QGridLayout()

                qf1.setLayout(qf1lm)

                ql1 = QtWidgets.QListWidget()
                ql1.setFixedWidth(100)
                ql1.setFixedHeight(50)

                wdl = wd.size

                for i in range(wdl):
                    ql1.addItem(str.format("{:.2f}", wd[i] / 250))

                lbl1 = QtWidgets.QLabel("Wrong Peaks:")
                lbl1.setFixedHeight(20)
                lbl1.setFixedWidth(100)

                qf1lm.addWidget(lbl1)
                qf1lm.addWidget(ql1, 1, 0, Qt.Alignment(36))

                ql1.clicked.connect(another)
                d3.addWidget(qf1, row=rowval, col=1)
                rowval = rowval + 1


            if np.any(md):
                qf2 = QtWidgets.QFrame()
                qf2lm = QtWidgets.QGridLayout()

                qf2.setLayout(qf2lm)

                ql2 = QtWidgets.QListWidget()
                ql2.setFixedWidth(100)
                ql2.setFixedHeight(50)

                mdl = md.size

                for i in range(mdl):
                    ql2.addItem(str.format("{:.2f}", md[i] / 250))

                lbl2 = QtWidgets.QLabel("Missing Peaks:")
                lbl2.setFixedHeight(20)
                lbl2.setFixedWidth(100)

                qf2lm.addWidget(lbl2)
                qf2lm.addWidget(ql2, 1, 0, Qt.Alignment(36))

                ql2.clicked.connect(another)
                d3.addWidget(qf2, row=rowval, col=1)

    elif q.text() == 'Load QRS data from file':

        header = dHolder.getHeader()

        fname = header['FileName']

        path = pathlib.PurePath(fname)

        if path.suffix == '.e3c':


            t = dHolder.getTime()

            s = dHolder.getSignal()

            y1 = s[0]
            y2 = s[1]

            if not dHolder.getFiltered():

                y1f = ft.notchfilter(y1, header['Fs'], 60.0, 3.0)
                y2f = ft.notchfilter(y2, header['Fs'], 60.0, 3.0)

                y1f2 = ft.medianfilter(y1f, header['Fs'])
                y2f2 = ft.medianfilter(y2f, header['Fs'])

                y1f3 = ft.filterbut4(y1f2, header['Fs'], 0.5, 40.0)
                y2f3 = ft.filterbut4(y2f2, header['Fs'], 0.5, 40.0)

            else:

                y1f3 = y1
                y2f3 = y2

            # Update plots

            d2 = area.docks['Lead A']

            p2 = d2.widgets[0]
            p21 = d2.widgets[1]

            lr2 = p2.plotItem.items[1]

            p2.plotItem.clear()

            fs = header['Fs']

            rstart = header['Start'] * fs
            rfinal = rstart + header['Length'] * fs

            rtx = header['AnnData']

            rtpos = np.array(np.unique(rtx['Rp']))

            ridx1 = np.intp(rtpos) > rstart
            ridx2 = np.intp(rtpos) <= rfinal
            ridx = np.logical_and(ridx1, ridx2)

            rpos1 = rtpos[ridx].copy()

            rpos = rpos1 - rstart

            p2.plot(t, y1, pen='y', name="RB1")
            p2.addItem(lr2)
            p2.plot(t[rpos], y1f3[rpos], pen=None, symbolBrush='y', symbolPen='w', name="RB3")

            p21.plotItem.clear()

            p21.plot(t, y1f3, pen='y', name="RB2")

            p21hdl1 = p21.plot(t[rpos], y1f3[rpos], pen=None, symbolBrush='y', symbolPen='w', name="RB4")
            p21hdl1.sigClicked.connect(Clicked)
            #p21hdl1.sigPointsClicked.connect(ClickedPoints)

            lr2.sigRegionChanged.connect(updateplot1)
            p21.sigXRangeChanged.connect(updateregion1)

            d3 = area.docks['Lead B']

            p3 = d3.widgets[0]
            p31 = d3.widgets[1]

            lr3 = p3.plotItem.items[1]

            p3.plotItem.clear()

            p3.plot(t, y2, pen='m', name="GB1")
            p3.addItem(lr3)

            p3.plot(t[rpos], y2f3[rpos], pen=None, symbolBrush='m', symbolPen='w', name="GB3")

            p31.plotItem.clear()
            p31.plot(t, y2f3, pen='m', name="GB2")

            p31hdl1 = p31.plot(t[rpos], y2f3[rpos], pen=None, symbolBrush='m', symbolPen='w', name="GB4")
            p31hdl1.sigClicked.connect(Clicked)
            #p31hdl1.sigPointsClicked.connect(ClickedPoints)

            lr3.sigRegionChanged.connect(updateplot2)
            p31.sigXRangeChanged.connect(updateregion2)

            if dHolder.getViewSpectrum():
                buildSpectrumDock(y1f3, y2f3, header['Fs'])

            cnt, des = sq.doSQA(y1f3, y2f3, rpos, rpos, fs)
            cnt = cnt + des

            dHolder.setSignal([y1f3, y2f3, rpos, rpos, cnt])

            qtaa.setEnabled(True)
            qtvia.setEnabled(True)
            dHolder.setFiltered(True)


    elif q.text() == "QTVI":

        data = dHolder.getSignal()
        cnt = data[4]

        if cnt >= 0:
            strLead = "<b>Lead A</b>."
        else:
            strLead = "<b>Lead B</b>."

        acnt = np.abs(cnt)

        if acnt == 0:
            strAdj = "<b>suggests</b> "
        elif acnt == 2:
            strAdj = "<b>slightly recommends</b> "
        elif acnt == 4:
            strAdj = "<b>recommends</b> "
        else:
            strAdj = "<b>strongly recommends</b> "

        FullText = "<h4>Tutorial for computing QTVI </h4> <ol>(1) First, please check that all R peaks have been correctly detected. " \
                   "If it is necessary correct all missed peaks. Then, select the lead you would like to use. Software " + \
                   strAdj + "using " + strLead + "\n\n</ol> <ol>(2) Then, select a heartbeat as template and manually identify the Q-on and T-off points." \
                   "\n\n</ol><ol>(3) Please, select a start sample for the 256 s window. If QTVI profile is needed, please specify also the overlapping factor</ol>"

        d5 = Dock("QTVI Tutorial", size=(200, 600), closable=True)
        area.addDock(d5, 'right')

        text1 = QtWidgets.QTextEdit()
        text1.setHtml(FullText)
        d5.addWidget(text1, row=0, col=0, colspan=2)

        pb1 = QtWidgets.QPushButton("Lead A")
        pb2 = QtWidgets.QPushButton("Lead B")

        pb1.clicked.connect(LeadASelectedQTVI)
        pb2.clicked.connect(LeadBSelectedQTVI)

        d5.addWidget(pb1, row=1, col=0)
        d5.addWidget(pb2, row=1, col=1)

    elif q.text() == "QT Analysis":

        data = dHolder.getSignal()
        cnt = data[4]

        if cnt >= 0:
            strLead = "<b>Lead A</b>."
        else:
            strLead = "<b>Lead B</b>."

        acnt = np.abs(cnt)

        if acnt == 0:
            strAdj = "<b>suggests</b> "
        elif acnt == 2:
            strAdj = "<b>slightly recommends</b> "
        elif acnt == 4:
            strAdj = "<b>recommends</b> "
        else:
            strAdj = "<b>strongly recommends</b> "

        FullText = "<h4>Tutorial for performing QT Analysis </h4> <ol>(1) First, please check that all R peaks have been correctly detected. " \
                   "If it is necessary correct all missed peaks. Then, select the lead you would like to use. Software " + \
                   strAdj + "using " + strLead + "\n\n</ol> <ol>(2) Then, check and manually correct Qon and Toff points" \
                                                 "\n\n</ol><ol>(3) Please, select a profile and a time lag value for QT/RR adaptation. </ol>"

        d5 = Dock("QT Adaptation Tutorial", size=(200, 600), closable=True)
        area.addDock(d5, 'right')

        text1 = QtWidgets.QTextEdit()
        text1.setHtml(FullText)
        d5.addWidget(text1, row=0, col=0, colspan=2)

        pb1 = QtWidgets.QPushButton("Lead A")
        pb2 = QtWidgets.QPushButton("Lead B")

        pb1.clicked.connect(doQTAnalysisLeadA)
        pb2.clicked.connect(doQTAnalysisLeadB)

        d5.addWidget(pb1, row=1, col=0)
        d5.addWidget(pb2, row=1, col=1)

    elif q.text() == "Detect irregular heartbeats":

        LeadCode = 0

        data = dHolder.getSignal()

        cnt = data[4]

        if cnt < 0:
            r = data[3]
        else:
            r = data[2]

        if LeadCode == 1:
            s = np.vstack((data[0], np.abs(data[0])))
        elif LeadCode == 2:
            s = np.vstack((np.abs(data[1]), data[1]))
        else:
            s = np.vstack((data[0], data[1]))

        classes1, T = tensor_class(s, r)
        classes2, _ = tensor_class2(s, r)

        classes = np.logical_or(classes1, classes2)

        header = dHolder.getHeader()
        t = dHolder.getTime()

        y1 = data[0]
        y2 = data[1]

        fs = header['Fs']

        # Update plots

        d2 = area.docks['Lead A']

        p2 = d2.widgets[0]
        p21 = d2.widgets[1]

        lr2 = p2.plotItem.items[1]

        p2.plotItem.clear()

        p2.plot(t, y1, pen='y', name="RB1")
        p2.addItem(lr2)

        idxsel = np.logical_not(classes)

        rreg = r[idxsel]
        ireg = r[classes]

        p2.plot(t[rreg], y1[rreg], pen=None, symbolBrush=(0, 255, 0), symbolPen='g', symbol='o', name="RB3")
        p2.plot(t[ireg], y1[ireg], pen=None, symbolBrush=(255, 0, 0), symbolPen='r', symbol='o', name="RB3")

        p21.plotItem.clear()

        p21.plot(t, y1, pen='y', name="RB2")

        p21hdl1 = p21.plot(t[rreg], y1[rreg], pen=None, symbolBrush=(0, 255, 0), symbolSize=14, symbol='o', symbolPen='g', name="RB4")
        p21hdl2 = p21.plot(t[ireg], y1[ireg], pen=None, symbolBrush=(255, 0, 0), symbolSize=14, symbol='o', symbolPen='r', name="RB4")
        p21hdl1.sigClicked.connect(ClickedLabel)
        p21hdl2.sigClicked.connect(ClickedLabel)
        # # p21hdl1.sigPointsClicked.connect(ClickedPoints)
        #
        lr2.sigRegionChanged.connect(updateplot1)
        p21.sigXRangeChanged.connect(updateregion1)
        #
        d3 = area.docks['Lead B']

        p3 = d3.widgets[0]
        p31 = d3.widgets[1]

        lr3 = p3.plotItem.items[1]

        p3.plotItem.clear()

        p3.plot(t, y2, pen='m', name="GB1")
        p3.addItem(lr3)

        p3.plot(t[rreg], y2[rreg], pen=None, symbolBrush=(0, 255, 0), symbol='o', symbolPen='g', name="GB3")
        p3.plot(t[ireg], y2[ireg], pen=None, symbolBrush=(255, 0, 0), symbol='o',  symbolPen='r', name="GB3")

        p31.plotItem.clear()
        p31.plot(t, y2, pen='m', name="GB2")
        #
        p31hdl1 = p31.plot(t[rreg], y2[rreg], pen=None, symbolBrush=(0, 255, 0), symbolSize=14, symbol='o', symbolPen='g', name="GB4")
        p31hdl2 = p31.plot(t[ireg], y2[ireg], pen=None, symbolBrush=(255, 0, 0), symbolSize=14, symbol='o', symbolPen='r', name="GB4")

        p31hdl1.sigClicked.connect(ClickedLabel)
        p31hdl2.sigClicked.connect(ClickedLabel)

        dHolder.setClasses(classes)
        # p31hdl1.sigClicked.connect(Clicked)
        # # p31hdl1.sigPointsClicked.connect(ClickedPoints)
        #
        # lr3.sigRegionChanged.connect(updateplot2)
        # p31.sigXRangeChanged.connect(updateregion2)
        #
        # if dHolder.getViewSpectrum():
        #     buildSpectrumDock(y1f4, y2f4, header['Fs'])
        #
        # cnt = 0

        # print('Hello')

        # from scipy.io.matlab import savemat
        #
        # savemat('physio.mat', {'y2': y2})
        if cnt < 0:
            print('\nLead B\n')
        else:
            print('\nLead A\n')

        # print('Detected Rs: ')
        # print(r.size)
        # print('\nDetected normals: ')
        # print(np.sum(idxsel))
        # print('\nDetected abnormals: ')
        # print(np.sum(classes))

    elif q.text() == "Load label information from file":

        header = dHolder.getHeader()
        t = dHolder.getTime()

        fs = header['Fs']

        data = dHolder.getSignal()

        y1 = data[0]
        y2 = data[1]

        rstart = header['Start'] * fs
        rfinal = rstart + header['Length'] * fs

        rtx = header['AnnData']
        rtpos = np.array(np.unique(rtx['Rp']))

        ridx1 = np.intp(rtpos) > rstart
        ridx2 = np.intp(rtpos) <= rfinal
        ridx = np.logical_and(ridx1, ridx2)

        rpos1 = rtpos[ridx].copy()

        rpos = rpos1 - rstart

        r = rpos

        allclass = np.array(rtx['Class'])

        classes = allclass[ridx].copy()
        classes = (classes > 0)

        # Update plots

        d2 = area.docks['Lead A']

        p2 = d2.widgets[0]
        p21 = d2.widgets[1]

        lr2 = p2.plotItem.items[1]

        p2.plotItem.clear()

        p2.plot(t, y1, pen='y', name="RB1")
        p2.addItem(lr2)

        idxsel = np.logical_not(classes)

        rreg = r[idxsel]
        ireg = r[classes]

        p2.plot(t[rreg], y1[rreg], pen=None, symbolBrush=(0, 255, 0), symbolPen='g', symbol='o', name="RB3")
        p2.plot(t[ireg], y1[ireg], pen=None, symbolBrush=(255, 0, 0), symbolPen='r', symbol='o', name="RB3")

        p21.plotItem.clear()

        p21.plot(t, y1, pen='y', name="RB2")

        p21hdl1 = p21.plot(t[rreg], y1[rreg], pen=None, symbolBrush=(0, 255, 0), symbolSize=14, symbol='o',
                           symbolPen='g', name="RB4")
        p21hdl2 = p21.plot(t[ireg], y1[ireg], pen=None, symbolBrush=(255, 0, 0), symbolSize=14, symbol='o',
                           symbolPen='r', name="RB4")
        p21hdl1.sigClicked.connect(ClickedLabel)
        p21hdl2.sigClicked.connect(ClickedLabel)
        # # p21hdl1.sigPointsClicked.connect(ClickedPoints)
        #
        lr2.sigRegionChanged.connect(updateplot1)
        p21.sigXRangeChanged.connect(updateregion1)
        #
        d3 = area.docks['Lead B']

        p3 = d3.widgets[0]
        p31 = d3.widgets[1]

        lr3 = p3.plotItem.items[1]

        p3.plotItem.clear()

        p3.plot(t, y2, pen='m', name="GB1")
        p3.addItem(lr3)

        p3.plot(t[rreg], y2[rreg], pen=None, symbolBrush=(0, 255, 0), symbol='o', symbolPen='g', name="GB3")
        p3.plot(t[ireg], y2[ireg], pen=None, symbolBrush=(255, 0, 0), symbol='o', symbolPen='r', name="GB3")

        p31.plotItem.clear()
        p31.plot(t, y2, pen='m', name="GB2")
        #
        p31hdl1 = p31.plot(t[rreg], y2[rreg], pen=None, symbolBrush=(0, 255, 0), symbolSize=14, symbol='o',
                           symbolPen='g', name="GB4")
        p31hdl2 = p31.plot(t[ireg], y2[ireg], pen=None, symbolBrush=(255, 0, 0), symbolSize=14, symbol='o',
                           symbolPen='r', name="GB4")

        p31hdl1.sigClicked.connect(ClickedLabel)
        p31hdl2.sigClicked.connect(ClickedLabel)

        dHolder.setClasses(classes)
        # p31hdl1.sigClicked.connect(Clicked)
        # # p31hdl1.sigPointsClicked.connect(ClickedPoints)
        #
        # lr3.sigRegionChanged.connect(updateplot2)
        # p31.sigXRangeChanged.connect(updateregion2)
        #
        # if dHolder.getViewSpectrum():
        #     buildSpectrumDock(y1f4, y2f4, header['Fs'])
        #
        # cnt = 0

        #print('Hello')

        # from scipy.io.matlab import savemat
        #
        # savemat('physio.mat', {'y2': y2})
        # print('\nBoth leads B\n')
        #
        # print('Detected Rs: ')
        # print(r.size)
        # print('\nDetected normals: ')
        # print(np.sum(idxsel))
        # print('\nDetected abnormals: ')
        # print(np.sum(classes))

def procTriggerView(q):

    if q.text() == 'View spectrum':

        if not(dHolder.getViewSpectrum()):

            header = dHolder.getHeader()
            s = dHolder.getSignal()

            y1 = s[0]
            y2 = s[1]

            buildSpectrumDock(y1, y2, header['Fs'], False)

    elif q.text() == 'View parameters':

        if not (dHolder.getViewInfoPanell()):
            buildInfoDock(False)
        else:
            buildInfoDock(True)

def procTriggerTool(q):

    s = dHolder.getSignal()

    t = dHolder.getTime()

    y11 = s[0]
    y21 = s[1]
    r11 = s[2]
    r21 = s[3]
    cnt = s[4]

    fs = dHolder.getHeader()['Fs']

    a = dHolder.getLastEvent()

    GCorrect = False

    if a[0:2] == "WR" or a[0:2] == "BT" or a[0:2] == "GQ":
        d2 = area.docks['QT Analysis']

        if a[-1] == '1':
            y1 = s[0]
            futureLabels = ['WR1', 'GQ1', 'BT1']
        else:
            y1 = s[1]
            futureLabels = ['WR2', 'GQ2', 'BT2']

        QTdata = dHolder.getQT()

        tr = QTdata['Rp']
        tq = QTdata['Qon']
        tt = QTdata['Toff']

        if a[0] == 'W':

            r1 = QTdata['Rp']

        elif a[0] == 'B':

            r1 = QTdata['Toff']

        else:

            r1 = QTdata['Qon']

        GCorrect = True
    else:

        if dHolder.getLastEvent() == "RB4":
            d2 = area.docks['Lead A']
            futureLabels = ["RB3", "RB4"]
            color = 'y'
            y1 = s[0]
            r1 = s[2]
        else:
            d2 = area.docks['Lead B']
            futureLabels = ["GB3", "GB4"]
            color = 'm'
            y1 = s[1]
            r1 = s[3]

    if q.text() == "Adjust point":

        p2 = d2.widgets[0]
        p21 = d2.widgets[1]

        vb = p21.getViewBox()
        ipoint = cInfo.getPoint() - win.pos()
        point = vb.mapSceneToView(ipoint)

        idx = int(point.x() * fs)

        isFirst, isLast, ind = detectRealIdx(r1, idx)

        rl = list(r1)
        rl.remove(rl[ind])
        rm = np.array(np.intp(rl))

        if not GCorrect:

            p21hdl1 = p21.plotItem.items[1]

            p21hdl1.sigClicked.disconnect(Clicked)

            p2.removeItem(p2.plotItem.items[-1])
            p21.removeItem(p21.plotItem.items[-1])

            p2.plot(t[rm], y1[rm], pen=None, symbolBrush=color, symbolPen='w', name=futureLabels[0])
            p21.plot(t[rm], y1[rm], pen=None, symbolBrush=color, symbolPen='w', name=futureLabels[1])

        else:

            for u in range(3):
                tmphdl1 = p21.plotItem.items[-1]
                p21.removeItem(tmphdl1)

            if a[0] == 'W':
                p21.plot(t[rm], y1[rm], pen=None, symbolBrush='w', symbolPen='w', name=futureLabels[0])
                p21.plot(t[tq], y1[tq], pen=None, symbolBrush='g', symbolPen='g', name=futureLabels[1])
                p21.plot(t[tt], y1[tt], pen=None, symbolBrush='b', symbolPen='b', name=futureLabels[2])
            elif a[0] == 'G':
                p21.plot(t[tr], y1[tr], pen=None, symbolBrush='w', symbolPen='w', name=futureLabels[0])
                p21.plot(t[rm], y1[rm], pen=None, symbolBrush='g', symbolPen='g', name=futureLabels[1])
                p21.plot(t[tt], y1[tt], pen=None, symbolBrush='b', symbolPen='b', name=futureLabels[2])
            else:
                p21.plot(t[tr], y1[tr], pen=None, symbolBrush='w', symbolPen='w', name=futureLabels[0])
                p21.plot(t[tq], y1[tq], pen=None, symbolBrush='g', symbolPen='g', name=futureLabels[1])
                p21.plot(t[rm], y1[rm], pen=None, symbolBrush='b', symbolPen='b', name=futureLabels[2])

            #p21.plot(t[rm], y1[rm], pen=None, symbolBrush=color, symbolPen=color, name="WR2")
            #p21.plot(t[tend], y1[tend], pen=None, symbolBrush=(0, 0, 255), symbolPen='b', name="BT2")
            #p21.plot(t[qon], y1[qon], pen=None, symbolBrush=(0, 255, 0), symbolPen='g', name="GQ2")

        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)

        p21.addItem(vLine, ignoreBounds=True)
        p21.addItem(hLine, ignoreBounds=True)

        proxy1 = pg.SignalProxy(p21.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved1)
        proxy2 = pg.SignalProxy(p21.scene().sigMouseClicked, delay=0.5, rateLimit=1, slot=mouseClicked1)

        app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

        cInfo.setCross(True)

        while cInfo.getCross():
            app.processEvents()

        app.restoreOverrideCursor()

        proxy1.disconnect()
        proxy2.disconnect()

        mypoint = cInfo.getPoint()

        idx2 = int(mypoint.x() * fs)

        rl.insert(0, idx2)

        rm1 = np.array(np.intp(rl))
        rm2 = np.sort(rm1)

        if not GCorrect:

            p2.plotItem.removeItem(p2.plotItem.items[-1])

            p21.plotItem.removeItem(p21.plotItem.items[-1])
            p21.plotItem.removeItem(p21.plotItem.items[-1])
            p21.plotItem.removeItem(p21.plotItem.items[-1])

            p2.plot(t[rm2], y1[rm2], pen=None, symbolBrush=color, symbolPen='w', name=futureLabels[0])
            p21hdl1 = p21.plot(t[rm2], y1[rm2], pen=None, symbolBrush=color, symbolPen='w', name=futureLabels[1])

            p21hdl1.sigClicked.connect(Clicked)
            #p21hdl1.sigPointsClicked.connect(ClickedPoints)

            if dHolder.getLastEvent() == "RB4":
                dHolder.setSignal([y11, y21, rm2, r21, cnt])
            else:
                dHolder.setSignal([y11, y21, r11, rm2, cnt])
        else:

            for u in range(5):
                tmphdl1 = p21.plotItem.items[-1]
                p21.removeItem(tmphdl1)

            if a[0] == 'W':
                plotR = p21.plot(t[rm2], y1[rm2], pen=None, symbolBrush='w', symbolPen='w', name=futureLabels[0])
                plotQ = p21.plot(t[tq], y1[tq], pen=None, symbolBrush='g', symbolPen='g', name=futureLabels[1])
                plotT = p21.plot(t[tt], y1[tt], pen=None, symbolBrush='b', symbolPen='b', name=futureLabels[2])
                infoqt = {'Rp': rm2, 'Qon': tq, 'Toff': tt}
            elif a[0] == 'G':
                plotR = p21.plot(t[tr], y1[tr], pen=None, symbolBrush='w', symbolPen='w', name=futureLabels[0])
                plotQ = p21.plot(t[rm2], y1[rm2], pen=None, symbolBrush='g', symbolPen='g', name=futureLabels[1])
                plotT = p21.plot(t[tt], y1[tt], pen=None, symbolBrush='b', symbolPen='b', name=futureLabels[2])
                infoqt = {'Rp': tr, 'Qon': rm2, 'Toff': tt}
            else:
                plotR = p21.plot(t[tr], y1[tr], pen=None, symbolBrush='w', symbolPen='w', name=futureLabels[0])
                plotQ = p21.plot(t[tq], y1[tq], pen=None, symbolBrush='g', symbolPen='g', name=futureLabels[1])
                plotT = p21.plot(t[rm2], y1[rm2], pen=None, symbolBrush='b', symbolPen='b', name=futureLabels[2])
                infoqt = {'Rp': tr, 'Qon': tq, 'Toff': rm2}

            dHolder.setQT(infoqt)

            plotR.sigClicked.connect(Clicked)
            plotT.sigClicked.connect(Clicked)
            plotQ.sigClicked.connect(Clicked)

    elif q.text() == "Remove point":

        p2 = d2.widgets[0]
        p21 = d2.widgets[1]

        vb = p21.getViewBox()
        ipoint = cInfo.getPoint() - win.pos()
        #opoint = win.pos()
        point = vb.mapSceneToView(ipoint)

        idx = int(point.x() * fs)

        isFirst, isLast, ind = detectRealIdx(r1, idx)

        rl = list(r1)
        rl.remove(rl[ind])
        rm = np.array(np.intp(rl))

        p21hdl1 = p21.plotItem.items[1]

        p21hdl1.sigClicked.disconnect(Clicked)
        #p21hdl1.sigPointsClicked.disconnect(ClickedPoints)

        p2.removeItem(p2.plotItem.items[-1])
        p21.removeItem(p21.plotItem.items[-1])

        p2.plot(t[rm], y1[rm], pen=None, symbolBrush=color, symbolPen='w', name=futureLabels[0])
        p21hdl1 = p21.plot(t[rm], y1[rm], pen=None, symbolBrush=color, symbolPen='w', name=futureLabels[1])

        p21hdl1.sigClicked.connect(Clicked)
        #p21hdl1.sigPointsClicked.connect(ClickedPoints)

        if dHolder.getLastEvent() == "RB4":
            dHolder.setSignal([y11, y21, rm, r21, cnt])
        else:
            dHolder.setSignal([y11, y21, r11, rm, cnt])

    elif q.text() == "Add point":

        p2 = d2.widgets[0]
        p21 = d2.widgets[1]

        vb = p21.getViewBox()
        ipoint = cInfo.getPoint() - win.pos()
        point = vb.mapSceneToView(ipoint)

        idx = int(point.x() * fs)

        isFirst, isLast, ind = detectRealIdx(r1, idx)

        if isFirst:
            newR = np.intp(r1[0] / 2)
        else:
            newR = np.intp((r1[ind - 1] + r1[ind])/2)

        rl = list(r1)
        rl.insert(ind, newR)
        rm = np.array(np.intp(rl))

        p21hdl1 = p21.plotItem.items[1]

        p21hdl1.sigClicked.disconnect(Clicked)
        #p21hdl1.sigPointsClicked.disconnect(ClickedPoints)

        p2.removeItem(p2.plotItem.items[-1])
        p21.removeItem(p21.plotItem.items[-1])

        p2.plot(t[rm], y1[rm], pen=None, symbolBrush=color, symbolPen='w', name=futureLabels[0])
        p21hdl1 = p21.plot(t[rm], y1[rm], pen=None, symbolBrush=color, symbolPen='w', name=futureLabels[1])

        p21hdl1.sigClicked.connect(Clicked)
        #p21hdl1.sigPointsClicked.connect(ClickedPoints)

        if dHolder.getLastEvent() == "RB4":
            dHolder.setSignal([y11, y21, rm, r21, cnt])
        else:
            dHolder.setSignal([y11, y21, r11, rm, cnt])

    if dHolder.getViewInfoPanell():
        buildInfoDock(True)

def procTriggerQTVI(q):

    s = dHolder.getSignal()

    t = dHolder.getTime()

    if dHolder.getLead() == 'A':
        y21 = s[0]
        r21 = s[2]
    else:
        y21 = s[1]
        r21 = s[3]

    fs = dHolder.getHeader()['Fs']

    dock = area.docks['QTVI Analysis']

    if q.text() == "Set this beat as template":

        # store and draw the beat
        tw = Twd(0)
        qw = Qwd(0)

        p21 = dock.widgets[1]

        if dHolder.getQTTflag():

            p21.removeItem(p21.plotItem.items[-1])
            p21.removeItem(p21.plotItem.items[-1])
            p21.removeItem(p21.plotItem.items[-1])

        vb = p21.getViewBox()
        ipoint = cInfo.getPoint() - win.pos()
        point = vb.mapSceneToView(ipoint)

        idx = int(point.x() * fs)

        isFirst, isLast, ind = detectRealIdx(r21, idx)

        k = int(fs / 250.0)

        ind_start = np.max([np.intp(0.5 * (r21[ind] + r21[ind - 1])), r21[ind] - 110 * k])
        ind_final = np.min([np.intp(0.55 * (r21[ind] + r21[ind + 1])), r21[ind] + 110 * k])

        p21.plot(t[ind_start:ind_final], y21[ind_start:ind_final], pen=pg.mkPen('y', width=3, style=QtCore.Qt.DashLine))

        rp = r21
        rp_idx = ind

        r = rp[rp_idx]
        rx = r / fs

        tend = tw.zhangTend(y21, rp, rp_idx, fs=fs)

        p21 = dock.widgets[1]

        tendx = tend / fs
        tendy = y21[tend]

        vLineTend = pg.InfiniteLine(angle=90, pos=(tendx, tendy), movable=True, label='T-off')
        vLineTend.sigPositionChanged.connect(posChanged)

        p21.addItem(vLineTend)

        qon = qw.initq(y21, rp, rp_idx, fs=fs)

        qonx = qon / fs
        qony = y21[qon]

        vLineQon = pg.InfiniteLine(angle=90, pos=(qonx, qony), movable=True, label='Q-on')

        vLineQon.sigPositionChanged.connect(posChanged)

        p21.addItem(vLineQon)

        gb = dock.widgets[2]

        lcdR = gb.findChild(QtWidgets.QLabel, "lcdR")
        lcdQ = gb.findChild(QtWidgets.QLabel, "lcdQ")
        lcdT = gb.findChild(QtWidgets.QLabel, "lcdT")
        lcdQT = gb.findChild(QtWidgets.QLabel, "lcdQT")

        qt = tendx - qonx

        lcdR.setText(rx.__str__())
        lcdQ.setText(qonx.__str__())
        lcdT.setText(tendx.__str__())
        lcdQT.setText(qt.__str__())

        Template = {"Start": ind_start, "End": ind_final, "Rpos": r, "Ridx": ind, "Qon": qon, "Toff": tend}
        dHolder.setQTTemplate(Template)

def procTriggerTC(q):

    print('Hello!!')

    if q.text() == "Toggle class":

        cl = np.array(dHolder.getClasses())
        sig = dHolder.getSignal()
        lead = dHolder.getLead()

        head = dHolder.getHeader()
        fs = head['Fs']

        thedraw = dHolder.getLastEvent()

        if lead == 'A':
            r = sig[2]
        else:
            r = sig[3]

        if thedraw[0] == 'R':
            d = area.docks['Lead A']
        else:
            d = area.docks['Lead B']

        p = d.widgets[1]

        vb = p.getViewBox()

        mypoint = vb.mapSceneToView(cInfo.getPoint() - win.pos())

        idx = int(mypoint.x() * fs)

        isFirst, isLast, ind = detectRealIdx(r, idx)

        if cl[ind] == False:
            cl[ind] = True
        else:
            cl[ind] = False


# Supervised classifier code

def procTriggerTrain(q):

    if q.text() == 'Toggle class':
        print('Toggling classs')
    elif q.text() == 'Current beat':
        print('Adding this heartbeat to the training set')
    else:
        print('Adding several heartbeats to the training set')


# Events handling

def posChanged(par):

    d6 = area.docks["QTVI Analysis"]
    gb = d6.widgets[2]

    head = dHolder.getHeader()
    fs = head['Fs']

    apos = par.pos()
    aux_1 = np.intp(np.round(apos.x() * fs))

    lcdQ = gb.findChild(QtWidgets.QLabel, "lcdQ")
    lcdT = gb.findChild(QtWidgets.QLabel, "lcdT")
    lcdQT = gb.findChild(QtWidgets.QLabel, "lcdQT")

    tmp = dHolder.getQTTemplate()

    if par.label.format == "Q-on":
        tmp["Qon"] = aux_1
    else:
        tmp["Toff"] = aux_1

    tendx = tmp["Toff"] / fs
    qonx = tmp["Qon"] / fs

    qt = (tendx - qonx)

    lcdQ.setText(qonx.__str__())
    lcdT.setText(tendx.__str__())
    lcdQT.setText(qt.__str__())

def mouseClicked1(evt):

    if evt[0]._double:
        a = dHolder.getLastEvent()

        if a == "RB4":
            d2 = area.docks['Lead A']
        elif a == "GB4" :
            d2 = area.docks['Lead B']
        else:
            d2 = area.docks['QT Analysis']

        p21 = d2.widgets[1]

        vb = p21.getViewBox()
        cInfo.setCross(False)
        cInfo.setPoint(vb.mapSceneToView(evt[0]._scenePos))

def mouseMoved1(evt):

    flg = 0

    pos = evt[0]

    s = dHolder.getSignal()
    fs = dHolder.getHeader()['Fs']

    if dHolder.getLastEvent() == "RB4":
        d2 = area.docks['Lead A']
        y = s[0]
    elif dHolder.getLastEvent() == "GB4":
        d2 = area.docks['Lead B']
        y = s[1]
    else:
        d2 = area.docks['QT Analysis']
        a = dHolder.getLastEvent()

        if a[-1] == '1':
            y = s[0]
        else:
            y = s[1]

        flg = 1


    p21 = d2.widgets[1]

    vb = p21.getViewBox()

    if flg == 0:
        vLine = p21.plotItem.items[2]
        hLine = p21.plotItem.items[3]
    else:
        vLine = p21.plotItem.items[4]
        hLine = p21.plotItem.items[5]

    rect = p21.sceneBoundingRect()

    if rect.contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        idx = int(fs * mousePoint.x())
        vLine.setPos(mousePoint.x())
        hLine.setPos(y[idx])


# Graphics updating

def updateplot1():

    d2 = area.docks['Lead A']

    p2 = d2.widgets[0]
    p21 = d2.widgets[1]

    lr2 = p2.plotItem.items[1]

    p21.setXRange(*lr2.getRegion(), padding=0)

def updateregion1():

    d2 = area.docks['Lead A']

    p2 = d2.widgets[0]
    p21 = d2.widgets[1]

    lr2 = p2.plotItem.items[1]

    lr2.setRegion(p21.getViewBox().viewRange()[0])

def updateplot2():

    d3 = area.docks['Lead B']

    p3 = d3.widgets[0]
    p31 = d3.widgets[1]

    lr3 = p3.plotItem.items[1]

    p31.setXRange(*lr3.getRegion(), padding=0)

def updateregion2():

    d3 = area.docks['Lead B']

    p3 = d3.widgets[0]
    p31 = d3.widgets[1]

    lr3 = p3.plotItem.items[1]

    lr3.setRegion(p31.getViewBox().viewRange()[0])

def updateplot3():

    d3 = area.docks['QTVI Analysis']

    p3 = d3.widgets[0]
    p31 = d3.widgets[1]

    lr3 = p3.plotItem.items[1]

    p31.setXRange(*lr3.getRegion(), padding=0)

def updateregion3():

    d3 = area.docks['QTVI Analysis']

    p3 = d3.widgets[0]
    p31 = d3.widgets[1]

    lr3 = p3.plotItem.items[1]

    lr3.setRegion(p31.getViewBox().viewRange()[0])

def updateplot4():

    d3 = area.docks['QT Analysis']

    p3 = d3.widgets[0]
    p31 = d3.widgets[1]

    lr3 = p3.plotItem.items[1]

    p31.setXRange(*lr3.getRegion(), padding=0)

def updateregion4():

    d3 = area.docks['QT Analysis']

    p3 = d3.widgets[0]
    p31 = d3.widgets[1]

    lr3 = p3.plotItem.items[1]

    lr3.setRegion(p31.getViewBox().viewRange()[0])


# Main Window construction

app = QtGui.QApplication([])
win = QtGui.QMainWindow()
win.setWindowTitle('PyECG: A tool for QT interval analysis')

# Main Menu construction

Menu = QMenuBar()

MenuFile = Menu.addMenu("File")
MenuEdit = Menu.addMenu("Analysis")
MenuView = Menu.addMenu("View")

opena = QAction("Open", win)
opena.setShortcut("Ctrl+O")
openi = QtGui.QIcon("open.png")
opena.setIcon(openi)

save = QAction("Save", win)
save.setShortcut("Ctrl+S")
savei = QtGui.QIcon("save.png")
save.setIcon(savei)

opta = QAction("Options", win)
opta.setShortcut("Ctrl+Alt+O")
optii = QtGui.QIcon("opt.png")
opta.setIcon(optii)

exita = QAction("Exit", win)
exita.setShortcut("Ctrl+Alt+X")
exiti = QtGui.QIcon("exit.png")
exita.setIcon(exiti)

detecta = QAction("Detect R", win)
detecta.setShortcut("Ctrl+R")
detecti = QtGui.QIcon("qrs2.png")
detecta.setIcon(detecti)

loadva = QAction("Load QRS data from file", win)
loadva.setShortcut("Ctrl+L")
loadvi = QtGui.QIcon("qrs5.png")
loadva.setIcon(loadvi)

# detectihba = QAction("Detect irregular heartbeats", win)
# detectihba.setShortcut("Ctrl+K")
# detectii = QtGui.QIcon("ectopic.png")
# detectihba.setIcon(detectii)
#
# loadlia = QAction("Load label information from file", win)
# loadlia.setShortcut("Ctrl+N")
# loadlii = QtGui.QIcon("lectopic.png")
# loadlia.setIcon(loadlii)

qtvia = QAction("QTVI", win)
qtvia.setShortcut("Ctrl+I")
qtvii = QtGui.QIcon("qtvi.png")
qtvia.setIcon(qtvii)

qtaa = QAction("QT Analysis", win)
qtaa.setShortcut("Ctrl+Q")
qtai = QtGui.QIcon("qtrr.png")
qtaa.setIcon(qtai)

MenuFile.addAction(opena)
MenuFile.addAction(save)
MenuFile.addSeparator()
MenuFile.addAction(opta)
MenuFile.addSeparator()
MenuFile.addAction(exita)

MenuEdit.addAction(detecta)
MenuEdit.addAction(loadva)
MenuEdit.addSeparator()
# MenuEdit.addAction(detectihba)
# MenuEdit.addAction(loadlia)
# MenuEdit.addSeparator()
MenuEdit.addAction(qtvia)
MenuEdit.addAction(qtaa)
MenuEdit.addSeparator()

viewspa = QAction("View spectrum", win)
viewi = QtGui.QIcon("spectrum3.png")
viewspa.setIcon(viewi)

MenuView.addAction(viewspa)

viewpaa = QAction("View parameters", win)
 #MenuView.addAction(viewpaa)

MenuFile.triggered[QAction].connect(procTriggerFile)
MenuEdit.triggered[QAction].connect(procTriggerEdit)
MenuView.triggered[QAction].connect(procTriggerView)

ContextMenu = QMenu()

cmToolMenu = ContextMenu.addMenu("Tools")

adjusta = QAction("Adjust point", win)
remova = QAction("Remove point", win)
adda = QAction("Add point", win)

cmToolMenu.addAction(adjusta)
cmToolMenu.addAction(remova)
cmToolMenu.addAction(adda)

cmToolMenu.triggered[QAction].connect(procTriggerTool)

QTVIMenu = QMenu()

cmQTVIMenu = QTVIMenu.addMenu("QTVI Tools")

setthisa = QAction("Set this beat as template", win)
# sugpointsa = QAction("Suggest points", win)
# sugpointsa.setEnabled(False)

cmQTVIMenu.addAction(setthisa)
# cmQTVIMenu.addAction(sugpointsa)

cmQTVIMenu.triggered[QAction].connect(procTriggerQTVI)

# Context menu Classes

ClassesMenu = QMenu()
TrainMenu = QMenu()

cmClassTMenu = ClassesMenu.addMenu("Classes")
cmTrainMenu = TrainMenu.addMenu("To training set")

togglea = QAction("Toggle class", win)
train1 = QAction("Current beat", win)
train2 = QAction("Current window", win)
info = QAction("Current beat info", win)

cmTrainMenu.addAction(train1)
cmTrainMenu.addAction(train2)
cmTrainMenu.addAction(info)

#cmTrainMenu.triggered[QAction].connect(procTriggerTrain)
#cmClassTMenu.triggered[QAction].connect(procTriggerTrain)

cmClassTMenu.addAction(togglea)

cmClassTMenu.triggered[QAction].connect(procTriggerTC)
cmClassTMenu.addMenu(cmTrainMenu)
cmClassTMenu.addAction(info)

win.setMenuBar(Menu)

tb = QtWidgets.QToolBar()

tb.addAction(opena)
tb.addAction(save)
tb.addAction(opta)
tb.addAction(exita)
tb.addSeparator()
tb.addAction(detecta)
tb.addAction(loadva)
tb.addSeparator()
# tb.addAction(detectihba)
# tb.addAction(loadlia)
# tb.addSeparator()
tb.addAction(qtvia)
tb.addAction(qtaa)
tb.addSeparator()
tb.addAction(viewspa)

tb.setToolButtonStyle(Qt.ToolButtonStyle(0))

win.addToolBar(tb)

# Docking system

area = DockArea()

win.setCentralWidget(area)
win.resize(1000, 600)
win.show()


# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Data structure handler

dHolder = OptionsHolder()
setProcActions(dHolder.getProcessing())
qtaa.setEnabled(False)
qtvia.setEnabled(False)

cInfo = CursorInfo(False, QtCore.QPointF())


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
