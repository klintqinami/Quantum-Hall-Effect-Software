# Quantum Hall Effect Software (Columbia University)

A relatively simple piece of software used to record live data for
the Quantum Hall Effect experiment in the Physics department. 

It makes heavy use of PyQt4 and pyqtgraph for fast live plotting. It also 
relies on PyVISA to supply the backend used to query the machines for data.
PyVISA currently requires that National Instruments Visa is installed and
configured, though hopefully open-source projects will replace this in the
near future.

The user inputs an estimated drive current and then clicks the start
button to begin collecting data. After clicking the stop button, the user
must save the data before being allowed to click start again. This is
to avoid unfortunate mouse slips.

The software, assuming the dependencies listed in the requirements file are 
met, will run on Linux, Windows, and OSX.
