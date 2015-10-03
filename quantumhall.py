#!/usr/bin/env python
import sys
import numpy as np
import pyqtgraph as pg
import visa
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import random
import pyqtgraph.exporters

class AppForm(QMainWindow):
    
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.createMain()
        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle("Quantum Hall Experiment") 

    def createMain(self):        
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
        self.p1.setRange(xRange=[0, 10], yRange=[0, 100])
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
        number = self.edit1.text()
        try:
            self.driveCurrent = float(number)
            # QMessageBox.about(self, 'Success','Drive Current set successfuly.')
        except Exception:
            QMessageBox.about(self, 'Error','Input can only be a number')
            pass
    
    def saveCSV(self):
        name = QFileDialog.getSaveFileName(self, "Save File")
        exporter = pg.exporters.CSVExporter(self.p1.plotItem)
        exporter.export(name)
        self.start.setEnabled(True)
        self.stop.setEnabled(True)
        self.button.setEnabled(True)
        self.edit1.setEnabled(True)
    
    def getInsts(self):
        rm = visa.ResourceManager()
        instruments = rm.list_resources()
        self.voltmeter1 = rm.open_resource(instruments[2])
        self.voltmeter2 = rm.open_resource(instruments[3])
        # self.voltmeter1.values_format.container = np.array
        # self.voltmeter2.values_format.container = np.array
        return self.voltmeter1, self.voltmeter2
    
    def getValuesX(self):
        x = self.voltmeter1.query_ascii_values('MEAS:CURR?')
        x = x[0]
        x = x * 0.1149 
        return x
    
    def getValuesY(self):
        y = self.voltmeter2.query_ascii_values('CURV?')
        y = y[0]
        y = y / self.driveCurrent
        return abs(y)
    
    def closeApp(self):
        choice = QtGui.QMessageBox.question(self, 'Exit', 'Quit?',\
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            sys.exit()
        else:
            pass
    
    def dataSim(self):
        x = random.uniform(1, 9)
        y = random.uniform(1, 100)
        return x, y
    
    def instValidator(self):
        try:
            self.getInsts()
            self.startGraphing()
        except Exception:
            QMessageBox.about(self, 'Error','Something went wrong when trying to \
                communicate with the instruments. \n\nMake sure they are turned on.')
            pass

    def startGraphing(self):
        self.data3 = np.empty(100)
        self.data4 = np.empty(100)
        self.ptr3 = 0

        def update():
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
        self.timer.start(70)

    def stopGraphing(self):
        choice = QMessageBox.question(self, 'End', 'Stop?',\
            QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
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

