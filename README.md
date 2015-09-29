# Quantum Hall Effect Software (Columbia University)

A relatively simple piece of software used to record live data for
the Quantum Hall Effect experiment in the Physics department. 

It makes heavy use of PyQt4 and pyqtgraph for fast live plotting. It also 
relies on PyVISA to supply the backend used to query the machines for data.

The user inputs an estimated drive current and then clicks the start
button to begin collecting data. The stop button is only pressed at 
the end of the experiment, where the user will be locked out of pressing
any buttons except the save button. 

The software, assuming the dependencies listed in the requirements file are 
met, will run on Linux, Windows, and OSX.