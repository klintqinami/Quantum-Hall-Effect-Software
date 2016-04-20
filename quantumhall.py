#!/usr/bin/env python
import sys
import numpy as np
import pyqtgraph as pg
import visa
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pyqtgraph.exporters


class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.createMain()
        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle("Quantum Hall Experiment")

    def createMain(self):
        '''Create the main application window. Should display an input 
        bar and 4 push buttons. An empy graph should also appear.'''
        page = QWidget()
        self.save = QPushButton("Save CSVs", self)
        self.save.clicked.connect(self.saveCSV)
        self.save.resize(self.save.minimumSizeHint())
        self.button = QPushButton('Enter Drive Current', page)
        self.button.resize(self.button.minimumSizeHint())
        self.edit1 = QLineEdit()
        self.edit1.setMaxLength(8)
        self.start = QPushButton("Start", self)
        self.start.clicked.connect(self.instValidator)
        self.start.resize(self.start.minimumSizeHint())
        self.stop = QPushButton("Stop", self)
        self.stop.clicked.connect(self.stopGraphing)
        vbox1 = QGridLayout()
        vbox1.addWidget(self.edit1)
        vbox1.addWidget(self.button)
        vbox1.addWidget(self.save)
        vbox1.addWidget(self.start)
        vbox1.addWidget(self.stop)
        page.setLayout(vbox1)
        self.setCentralWidget(page)
        self.p1 = pg.PlotWidget()
        self.p1.setTitle("Resistance vs B-Field")
        self.p1.setLabel('left', 'Resistance', units='ohms')
        self.p1.setLabel('bottom', 'B-Field', units='tesla')
        vbox1.addWidget(self.p1)
        self.button.clicked.connect(self.inputValidator)
        pg.setConfigOptions(antialias=True)
        self.curve = self.p1.plot(pen='r')
        self.p1.setDownsampling(mode='peak')
        self.p1.setClipToView(True)
        self.p1.enableAutoRange(x=True)
        self.p1.enableAutoRange(y=True)
        self.driveCurrent = 1.0

    def inputValidator(self):
        '''Validates that the drive current is an actual number'''
        number = self.edit1.text()
        try:
            self.driveCurrent = float(number)
            message = "Drive Current set to " + str(number)
            QMessageBox.about(self, 'Success', message)
        except Exception:
            QMessageBox.about(self, 'Error', 'Input can only be a number')
            pass

    def saveCSV(self):
        '''Saves data in CSV format and enables buttons'''
        name = QFileDialog.getSaveFileName(self, "Save File")
        exporter = pg.exporters.CSVExporter(self.p1.plotItem)
        exporter.export(name)
        self.start.setEnabled(True)
        self.stop.setEnabled(True)
        self.button.setEnabled(True)
        self.edit1.setEnabled(True)

    def getInsts(self):
        '''Gets instruments using resource manager. It assumes that the
        instruments are the 3rd and 4th instruments when resource manager
        is called. If software is used on a different computer, the calls to 
        instruments[2] and instruments[3] must be changed accordingly. 
        Instruments[2] tries to connect to the device measuring current.
        Instrument[3] tries to connect to the device measuring voltage.
        Sample GPIB instrument name: GPIB::2::INSTR'''
        rm = visa.ResourceManager('@py')
        instruments = rm.list_resources()
        self.voltmeter1 = rm.open_resource(instruments[2])
        self.voltmeter2 = rm.open_resource(instruments[3])
        # self.voltmeter1.values_format.container = np.array
        # self.voltmeter2.values_format.container = np.array
        return self.voltmeter1, self.voltmeter2

    def getValuesX(self):
        '''Measures current and multiplies by the manufacturer specified
        conversion, currently set to 0.1149'''
        x = self.voltmeter1.query_ascii_values('MEAS:CURR?')
        x = x[0] * 0.1149
        return x

    def getValuesY(self):
        '''Measures voltage and divides by user input for drive current'''
        y = self.voltmeter2.query_ascii_values('CURV?')
        y = y[0] / self.driveCurrent
        return abs(y)

    def closeApp(self):
        '''Exits application. Has not been integrated into application.'''
        choice = QtGui.QMessageBox.question(
           self, 'Exit', 'Quit?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def dataSim(self):
        '''Used to simulate data during testing of software.'''
        x = random.uniform(1, 9)
        y = random.uniform(1, 100)
        return x, y

    def instValidator(self):
        '''Tries to start graphing using instruments. Throws an exception and
        gives user a warning if machines are unresponsive.'''
        try:
            self.getInsts()
            self.startGraphing()
        except Exception:
            QMessageBox.about(self, 'Error', 
                'Instruments are either off or unresponsive. \
                 \n\nTurn on instruments. \
                 \n\nIf error persists, check GPIB ports.')
            pass

    def startGraphing(self):
        self.data3 = np.empty(100)
        self.data4 = np.empty(100)
        self.ptr3 = 0

        def update():
            '''Updates graph and maintains left-to-right live plotting'''
            self.data3[self.ptr3] = self.getValuesX()
            self.data4[self.ptr3] = self.getValuesY()
            self.ptr3 += 1
            if self.ptr3 >= self.data3.shape[0]:
                tmp = self.data3
                tms = self.data4
                self.data3 = np.empty(self.data3.shape[0] * 2)
                self.data3[:tmp.shape[0]] = tmp
                self.data4 = np.empty(self.data4.shape[0] * 2)
                self.data4[:tms.shape[0]] = tms
            # curve3.setData(data3[:self.ptr3])
            # curve3.setPos(-self.ptr3, 0)
            self.curve.setData(self.data3[:self.ptr3], self.data4[:self.ptr3])
        self.update = update
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(70) # argument controls speed of plotting

    def stopGraphing(self):
        '''Stops collecting data and locks user out of all buttons except
        the save button. Buttons are reenabled once user saves data run.'''
        choice = QMessageBox.question(self, 'End', 'Stop?',
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.timer = pg.QtCore.QTimer()
            self.timer.stop()
            self.start.setEnabled(False)
            self.stop.setEnabled(False)
            self.button.setEnabled(False)
            self.edit1.setEnabled(False)
        else:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()
