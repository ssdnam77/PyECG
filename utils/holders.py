import pathlib
from io import *
from scipy.io.matlab import savemat
from json import JSONEncoder

class OptionsHolder:

    def __init__(self, viewSpectrum=False, viewInfoPanel=False):

        self.data = {'Header': {}, 'Signal': [], 'Time': [], 'RR': {}, 'QT': {}, 'QTemplate': {}, 'QTTflag': False}
        self.Lead = 'A'
        self.Outliers = {'Lead A': [], 'Lead B': []}
        self.Classes = []

        self.viewSpectrum = viewSpectrum
        self.viewInfoPanel = viewInfoPanel
        self.SelFilter = 0
        self.SelRDet = 0
        self.IHB = 0
        self.LeadCode = 0
        self.__isProcessing = False
        self.__lastEvent = None
        self.__Filtered = False

    def setProcessing(self, proc=False):

        self.__isProcessing = proc

    def getProcessing(self):

        return self.__isProcessing

    def setHeader(self, aheader):

        self.data['Header'] = aheader

    def getHeader(self):

        return self.data['Header']

    def setSignal(self, asignal):

        self.data['Signal'] = asignal

    def getSignal(self):

        return self.data['Signal']

    def setTime(self, atime):

        self.data['Time'] = atime

    def getTime(self):

        return self.data['Time']

    def setViewInfoPanel(self, viewInfoPanel = False):

        self.viewInfoPanel = viewInfoPanel

    def getViewInfoPanell(self):

        return self.viewInfoPanel

    def setViewSpectrum(self, viewSpectrum = False):

        self.viewSpectrum = viewSpectrum

    def getViewSpectrum(self):

        return self.viewSpectrum

    def setLastEvent(self, ev):

        self.__lastEvent = ev

    def getLastEvent(self):

        return self.__lastEvent

    def setRR(self, ev):

        self.data['RR'] = ev

    def getRR(self):

        return self.data['RR']

    def setFiltered(self, filt=False):

        self.__Filtered = filt

    def getFiltered(self):

        return self.__Filtered

    def setQT(self, ev):

        self.data['QT'] = ev

    def getQT(self):

        return self.data['QT']

    def setOutLier(self, lead, olist):

        self.Outliers[lead] = olist

    def getOutLiers(self):

        return self.Outliers

    def setClasses(self, classes):

        self.Classes = classes

    def getClasses(self):

        return self.Classes

    def setA(self):

        self.Lead = 'A'

    def setB(self):

        self.Lead = 'B'

    def getLead(self):

        return self.Lead

    def getQTTemplate(self):

        return self.data['QTemplate']

    def getQTTflag(self):

        return self.data['QTTflag']

    def setQTTemplate(self, qttemp):

        self.data['QTemplate'] = qttemp
        self.data['QTTflag'] = True

    def getFilter(self):

        return self.SelFilter

    def setFilter(self, fval):

        self.SelFilter = fval % 2

    def getRDet(self):

        return self.SelRDet

    def setRDet(self, redet):

        self.SelRDet = redet % 2

    def getLeadCode(self):

        return self.LeadCode

    def setLeadCode(self, lc):

        self.LeadCode = lc % 3

    def saveToFile(self, filename):
        """

        :param filename: Name of the file
        :return:
        :todo include JSON support
        """

        header = self.data['Header']
        Signal = self.data['Signal']
        time = self.data['Time']
        rr = self.data['RR']
        qt = self.data['QT']
        qtt = self.data['QTemplate']
        qtf = self.data['QTTflag']

        struct = {'Header': header, 'Signal': Signal, 'Time': time, 'RR': rr, 'QT': qt, 'QTemplate': qtt, 'QTTflag': qtf}

        #path = pathlib.PurePath(filename)
        savemat(filename, struct)


        # if path.suffix == '.mat':
        #     savemat(filename, struct)
        # else:
        #     encoder = JSONEncoder()
        #     json_string = encoder.encode(signal)
        #     fid = open(filename, mode="w")
        #     fid.write(json_string)
        #     fid.close()

class CursorInfo:

    def __init__(self, enCross, lastPoint):

        self.enCross = enCross
        self.lastPoint = lastPoint
        self.currentLead = 'A'


    def setCross(self, adata):

        self.enCross = adata


    def getCross(self):

        return self.enCross


    def setPoint(self, adata):

        self.lastPoint = adata


    def getPoint(self):

        return self.lastPoint

    def setCurrentLead(self, lead):

        self.currentLead = lead

    def getCurrentLead(self):

        return self.currentLead