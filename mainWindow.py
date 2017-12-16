#!/bin/env python

import sys
from PyQt5 import uic, QtCore, QtWidgets, Qt
from PyQt5.QtCore import Qt
import os
from datetime import date
import configparser

"""
TODOS:
    - [i] Alle benötigten Infos aus einer INI Datei lesen / schreiben
        - [] In die INI Datei aufzunehmende Werte
            - [x] Batteriestatus (geladen / entladen)
            - [x] Batterieladung
        - [] Alle Texte aufnehmen
        - [] Fenster Hintergrund Fabe
        - [] Button
            - [] Hintergrund Farbe
            - [] Schrift Farbe    

       
"""

class configuration():
    config = configparser.ConfigParser()

    def __init__(self):
        pass

    def setConfigData(self, section, key, data):
        #type(self).config['lastProgrammRun'] = {'day':getDay,
        #                                        'time':'19:00',
        #                                        'count':1,
        #                                        'batteiestate':'entladen',
        #                                        'batterieladung':'Prozent'}

        type(self).config["'" + section + "'"] = {"'" + key + "'":"'" + data + "'",
                                      'text2':''}

        with open('config', 'w') as configfile:
            type(self).config.write(configfile)

    def getConfigData(self):
        type(self).config.read('config')
        type(self).getDay = type(self).config.get('lastProgrammRun', 'day')
        type(self).getTime =  type(self).config.get('lastProgrammRun', 'time')
        type(self).getCount =  type(self).config.get('lastProgrammRun', 'count')
        type(self).getText1 = type(self).config.get('texte', 'text1')

        print(type(self).getDay)

class Batteriestatus(QtWidgets.QDialog, configuration):
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

    fileBATOcapacity = "/sys/class/power_supply/BAT0/capacity"
    fileBATOstate = "/sys/class/power_supply/BAT0/status"

    if len(tmpBildschirmAufloesung) > 2:
        getBildschimAufloesung = tmpBildschirmAufloesung[len(tmpBildschirmAufloesung) -1]
    else:
        getBildschimAufloesung = tmpBildschirmAufloesung[0]


    def __init__(self, parent=None):
        configuration.__init__(self)
        configuration.getConfigData(self)

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
        self.statusAusgabe.setText("<font color='white'>Die Batterie hat noch " + str(self.getBATOcapacity()) + "% Ladung</font>")

        # Set window background color
        self.setAutoFillBackground(True)
        getColorPalette = self.palette()
        getColorPalette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(getColorPalette)

        # Set button "buttonExit" Color
        self.buttonExit.setStyleSheet("background-color: black; color: white")

    def getBATOstate(self):
        fobj = open(self.fileBATOstate, 'r')
        for line in fobj:
            BATOstate = line.rstrip()
        fobj.close()

    def getBATOcapacity(self):
        # Variable initialisieren
        #fileBATOcapacity = "/sys/class/power_supply/BAT0/capacity"

        # Read Batterie charge
        fobj = open(self.fileBATOcapacity, 'r')
        for line in fobj:
            setBATOcapacityInGui = line.rstrip()
        fobj.close()

        return setBATOcapacityInGui

    # Es wird geprüft, wann das Skript das letztes mal gestartet wurde.
    def checkLastScriptRun(self):
        getBATOcapacity = self.getBATOcapacity()
        getLastBATOcapacityToRunScript = self.pwd + "/lastBATOcapacity"
        getToday = date.today()

        configuration.setConfigData(self, section="lastprogrammRun", key="time", data="2017-11-20")

        if os.path.isfile(getLastBATOcapacityToRunScript):
            #print('Exist\n' + getLastBATOcapacityToRunScript)
            #lastBATOcapacity = "lastBATOcapacity"
            statusFile = open(getLastBATOcapacityToRunScript, "r+")
            getLastBATOcapacityFile = statusFile.read().split(',')
            getLastBATOcapacity = getLastBATOcapacityFile[0]
            print(getLastBATOcapacity + "\n" + self.getBATOcapacity())
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

    print("Count: " + dialog.getCount)

    sys.exit(app.exec_())
