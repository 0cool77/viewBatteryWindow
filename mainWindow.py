#!/bin/env python

import sys
from PyQt5 import uic, QtCore, QtWidgets, Qt
from PyQt5.QtCore import Qt
import os
from datetime import date

"""
TODOS:
    - Alle benötigten Infos aus einer INI Datei lesen / schreiben
"""

class Batteriestatus(QtWidgets.QDialog):
    # Variable initialisieren
    #pwd = os.getcwd()

    # Get script dir
    fixed_value = 'test_get_script_path.py'
    this_file = os.path.abspath(__file__)
    pwd = os.path.dirname(this_file)
    #pwd = "/usr/local/bin/Batterieanzeige"


    tmpBildschirmAufloesung = os.popen("/usr/bin/xrandr | grep -v disconnected | grep -A 1 connected | grep -v connected | awk '{print $1}'").readlines()
    #print(len(tmpBildschirmAufloesung))
    #print(tmpBildschirmAufloesung)

    dateiBatterieStatus = "/sys/class/power_supply/BAT0/capacity"


    if len(tmpBildschirmAufloesung) > 2:
        getBildschimAufloesung = tmpBildschirmAufloesung[len(tmpBildschirmAufloesung) -1]
    else:
        getBildschimAufloesung = tmpBildschirmAufloesung[0]


    def __init__(self, parent=None):
        self.checkLastScriptRun()
        super().__init__(parent)
        self.ui = uic.loadUi(self.pwd + "/main.ui", self)
        #self.ui = uic.loadUi(self.this_file_path + "/main.ui", self)

        # Create Slot
        self.ui.buttonExit.clicked.connect(self.pushExit)

        # Set Desktop Resolution
        getDesktopResolution = self.getBildschimAufloesung.split('x')
        getDesktopResolutionWidth = getDesktopResolution[0]
        getDesktopResolutionHeight = getDesktopResolution[1]

        # Set window position on top
        #print(int(getDesktopResolutionHeight) / 2)

        # Fenster Breite auf die gesamte Bildschirmbreite erweitern
        self.setFixedWidth(int(getDesktopResolutionWidth))

        # Set title to hint (verstecken)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)

        # Set label Text "statusAusgabe"
        self.statusAusgabe.setText("<font color='white'>Die Batterie hat noch " + str(self.getBatterieStatus()) + "% Ladung</font>")

        # Set window background color
        self.setAutoFillBackground(True)
        getColorPalette = self.palette()
        getColorPalette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(getColorPalette)

        # Set button "buttonExit" Color
        self.buttonExit.setStyleSheet("background-color: black; color: white")


    def getBatterieStatus(self):
        # Variable initialisieren
        #dateiBatterieStatus = "/sys/class/power_supply/BAT0/capacity"

        # Read Batterie charge
        fobj = open(self.dateiBatterieStatus, 'r')
        for line in fobj:
            setBatterieStatusInGui = line.rstrip()
        fobj.close()

        return setBatterieStatusInGui

    # Es wird geprüft, wann das Skript das letztes mal gestartet wurde.
    def checkLastScriptRun(self):
        getBATOcapacity = self.getBatterieStatus()
        getLastBATOcapacityToRunScript = self.pwd + "/lastBATOcapacity"
        getToday = date.today()

        if os.path.isfile(getLastBATOcapacityToRunScript):
            #print('Exist\n' + getLastBATOcapacityToRunScript)
            #lastBATOcapacity = "lastBATOcapacity"
            statusFile = open(getLastBATOcapacityToRunScript, "r+")
            getLastBATOcapacityFile = statusFile.read().split(',')
            getLastBATOcapacity = getLastBATOcapacityFile[0]
            print(getLastBATOcapacity + "\n" + self.getBatterieStatus())
            if (int(getLastBATOcapacity)) == int(getBATOcapacity):
                print('gleich')
                sys.exit(app.exec_())
            else:
                print('ungleich')

            statusFile.close()
        else:
            print("Error")
            statusFile = open(getLastBATOcapacityToRunScript, "w")
            statusFile.write(getBATOcapacity + "," + str(getToday).replace('-', ''))
            statusFile.close()


    def getScriptDir():
        fixed_value = 'test_get_script_path.py'
        this_file = os.path.abspath(__file__)
        this_file_path = os.path.dirname(this_file)
        working_directory = os.getcwd()
        print(('Fester Wert: %s\nScriptpfad: %s\nScripterzeichnis: %s\nCWD: %s')
              % (fixed_value,this_file,this_file_path,working_directory))

    def pushExit(self):
        # Exit App with button "buttonExit"
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = Batteriestatus()
    dialog.show()
    sys.exit(app.exec_())
