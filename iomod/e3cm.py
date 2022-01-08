# -*- coding: utf-8 -*-
#
import numpy as np
import sys
import io
import os
import struct
import zipfile
import logging
import pathlib

logger = logging.getLogger("e3c_logger")


class E3cc:
    """"
    para abrir archivos e3c
    """
    def __init__(self):
        self.reade3c()
        self.e3cfilesize()
        # self.ensure_dir()
        self.reade3cecg()
        self._unzipfiles()

    def _unzipfiles(self, fpath, wdir):
        logger.debug('descomprimido')
        # logger.debug(type(wdir))
        try:
            zip_ref = zipfile.ZipFile(fpath, 'r')
            zip_ref.extractall(wdir)
            zip_ref.close()
            logger.info(fpath)

        except zipfile.BadZipFile:
            logger.error('este archivo esta corrupto')
            pass

    def reade3cecg(self, file, channels, fs, time_start=0, time_len=50):
        """"This function read the ECG data from the current.ECG record
            Parameters:
                File: ECG record file
                Channels: Channels on record
                fs: Sampling frequency (250 Hz)
                timeStart: Time (in seconds)
                timeLen: Window length (in seconds)
        """""
        # todo: file name in path is not a pathlike object
        offset = 2 * channels * time_start * fs
        fid = open(file, "rb")  # Read only file. Open in binary mode for portability
        fid.seek(0, 2)
        a_size = fid.tell() / 2
        samples = a_size / 2
        if time_len != -1:
            a_size = channels * fs * time_len
        fid.seek(offset, 0)
        mystruct = fid.read(a_size * 2)
        Q = struct.unpack('<' + str(a_size) + 'h', mystruct)
        fid.close()
        del mystruct
        ecg = np.array(Q)
        del Q
        m_c = ecg.reshape(channels, int(a_size / channels), order='F').copy()
        del ecg
        return samples, 2.65e-3*m_c

    def e3cfilesize(self, file):
        """""
         This function gets the ECG data from record
         Parameters:
          file: ECG record file
          Channels: Channels on record
          fs: Sampling frequency (250 Hz)
          timeStart: Time (in seconds)
          timeLen: Window length (in seconds)
        """""
        fid = open(file, "rb")  # Read only file. Open in binary mode for portability
        fid.seek(0, 2)
        a_size = fid.tell() / 2
        fid.close()
        samples = a_size / 2
        fs = 250
        ns = samples / fs
        nm = ns / 60
        nh = ns / 3600
        nh1 = nh
        nm1 = (ns - nh1 * 3600) / 60
        ns1 = (ns - nh1 * 3600 - nm1 * 60)
        timeval = [nh1, nm1, ns1]
        return samples, timeval

    def reade3c(self, filename, arch, time_start=0, time_len=5):
        """"
        funcion para leer el archivo qrs del excorde
        formato de los archivos inicio(4by), fin(4by), patron(4by), picoR(4by), RRanterior(4by),
        RRpromedio(4bay), Clasficacion(2by)
        FID es dado por la funcion fopen, num_m es el numero de muestras a leer
        devuelve RRanterior, picoR
        """""
        if arch == 'Windows':
            workdirpath = pathlib.PureWindowsPath(pathlib.Path.home().joinpath('AppData/Local/PyECG/temp'))
            wokrdir = pathlib.Path(workdirpath)
            try:
                # se crea el directorio de trabajo si no existe
                wokrdir.mkdir(parents=True)
                # logger.debug("directorio /temp creado")
                pass
            except FileExistsError:
                logger.debug("directorio ya existe")
                pass
            except Exception:
                logger.debug('Opps!!')
                pass
            self._unzipfiles(self, fpath=filename, wdir=workdirpath)
            file1 = workdirpath.joinpath('current.QRS')
            file2 = workdirpath.joinpath('current.ECG')
        elif arch == 'Linux':
            workdirpath = pathlib.PurePosixPath(pathlib.Path.home().joinpath('var/temp/PyECG/temp'))
            workdir = pathlib.Path(workdirpath)
            try:
                workdir.mkdir(parents=True)
                logger.debug("directorio creado")
            except FileExistsError:
                logger.debug("el directorio ya existe")
                pass
            self._unzipfiles(fpath=filename, wdir=workdirpath)
            file1 = workdirpath.joinpath('current.QRS')
            file2 = workdirpath.joinpath('current.ECG')
        else:
            logger.error("error desconocido")
            pass
        Header = {'Channels': 2, 'Fs': 250}
        fs = 250  # Sample Freq.
        bpm = 2  # Number of bytes per ECG sample
        channel_count = 2
        fid = open(file1, "rb")  # read only
        offset = 0
        fid.seek(offset, 2)  # pongo el puntero en el primer elemento
        file1_sz = fid.tell()
        beat_cnt = int(file1_sz / 25)
        fid.seek(offset, 0)
        chunk_sz = 600
        count = chunk_sz * 7
        chk_string = '<'
        chk_string = chk_string + '6IB' * chunk_sz
        num_it = int(beat_cnt / chunk_sz)
        last_it = beat_cnt - chunk_sz * num_it
        qrson = []
        qrsend = []
        pattern = []
        rpeak = []
        rrprev = []
        rrmean = []
        bclass = []
        mystruct = fid.read(file1_sz)
        fid.close()
        offset = 0
        step = struct.calcsize(chk_string)
        for i in range(0, num_it):
            y = struct.unpack_from(chk_string, mystruct, offset)
            offset = offset + step
            qrson.extend(np.array(y[0:count:7]))
            qrsend.extend(np.array(y[1:count:7]))
            pattern.extend(np.array(y[2:count:7]))
            rpeak.extend(np.array(y[3:count:7]))
            rrprev.extend(np.array(y[4:count:7]))
            rrmean.extend(np.array(y[5:count:7]))
            bclass.extend(np.array(y[6:count:7]))
        if last_it > 0:
            l_string = '<'
            l_string = l_string + '6IB' * last_it
            countl = last_it * 7
            y = struct.unpack_from(l_string, mystruct, offset)
            qrson.extend(np.array(y[0:countl:7]))
            qrsend.extend(np.array(y[1:countl:7]))
            pattern.extend(np.array(y[2:countl:7]))
            rpeak.extend(np.array(y[3:countl:7]))
            rrprev.extend(np.array(y[4:countl:7]))
            rrmean.extend(np.array(y[5:countl:7]))
            bclass.extend(np.array(y[6:countl:7]))

        Header['File Name'] = filename
        qrson1 = np.unique(np.array(qrson))
        qrsend1 = np.unique(np.array(qrsend))
        pattern1 = np.unique(np.array(pattern))
        rpeak1 = np.unique(np.array(rpeak))
        rrprev1 = np.array(rrprev)
        rrmean1 = np.array(rrmean)
        bclass1 = np.array(bclass)
        samples, Data = self.reade3cecg(self, file2, channel_count, fs, time_start, time_len)
        ns = samples / fs
        nm = int(ns / 60)
        nh = int(ns / 3600)
        nh1 = nh
        nm1 = int((ns - nh * 3600) / 60)
        ns1 = (ns - nh1 * 3600 - nm1 * 60)
        Header['Hours'] = nh1
        # Header['TotalTimeH'] = nh
        Header['Minutes'] = nm1
        #Header['TotalTimeM'] = nm
        Header['Seconds'] = int(ns1)
        #Header['TotalTimeS'] = ns
        Header['Samples'] = int(samples)
        Header['AnnData'] = {'QRSon':qrson1, 'QRSend': qrsend1, 'Pattern': pattern1, 'Rp':rpeak1, 'RRp': rrprev1,
                             'RRm': rrmean1, 'Class': bclass1}
        Header['Start'] = time_start
        Header['Length'] = time_len
        return Header, Data

def main():
    """"
    test read
    """
    import platform
    direc = r'C:\Users\DNA\DataRaw\7.e3c'
    tempdir = r'C:\Users\DNA\AppData\Local\PyECG\aka'
    sd = pathlib.Path(direc)
    df = pathlib.Path(tempdir)
    m3 = E3cc()
    # m3._unzipfiles(sd,df)
    archname = platform.system()
    m3.reade3c(filename=direc, arch=archname, time_len=500)
    pass


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    main()
