#!/bin/env python

import sys
from PyQt5 import uic, QtCore, QtWidgets, Qt
from PyQt5.QtCore import Qt
import os
from datetime import date
import sqlite3

"""
TODOS:
    - [] Alle benötigten Infos werden aus einer SQLite3 DB gelesen oder geschrieben
        - [] In die SQLite3 DB aufzunehmende Werte
            - [] aktueller Tag
            - [] Batteriestatus (geladen / entladen)
            - [] Batterie Kapazität
            - [x] Programm PID
        - [] Alle Texte aufnehmen
        - [] Fenster Hintergrund Fabe
        - [] Button
            - [] Hintergrund Farbe
            - [] Schrift Farbe    

       
"""

class configuration():
    configDB = 'config.db'

    def __init__(self):
        pass

    def createDB(self, db):
        connection = sqlite3.connect(db)

        cursor = connection.cursor()


        sql_command = """
        CREATE TABLE IF NOT EXISTS config ( 
        id INTEGER PRIMARY KEY, 
        section VARCHAR(20), 
        key VARCHAR(30), 
        value CHAR(50));"""

        cursor.execute(sql_command)

        connection.commit()
        connection.close()

        # Set dafault value to table
        self.setConfigData(self.configDB, section='programmInfo', key='programmPID', value='0')
        self.setConfigData(self.configDB, section='lastProgrammRun', key='today', value='getToday')
        self.setConfigData(self.configDB, section='lastProgrammRun', key='batoState', value='entladen')
        self.setConfigData(self.configDB, section='lastProgrammRun', key='batoCapacity', value='0')

    def setConfigData(self, db, section, key, value):
        connection = sqlite3.connect(db)

        cursor = connection.cursor()

        sql_command = """INSERT INTO config (
                            id, 
                            section, 
                            key,
                            value
                        )
                        VALUES (
                            NULL,
                            '""" + section + """',
                            '""" + key + """',
                            '""" + value + """'
                        );
                    """
        cursor.execute(sql_command)
        connection.commit()
        connection.close()

    def setDataUpdateFromTable(self, db, table, section, key, value):
        print("DB: " + db + "\nTable: "+ table + "\nSection: " + section + "\nKey: " + key + "\nValue: " + value)
        connection = sqlite3.connect(db)
        cursor = connection.cursor()

        sql_statment = "UPDATE " + table + " SET value  = '" + value + "' WHERE key = '" + key + "' AND  section = '" + section + "';"
        print("SQL: " + sql_statment)

        cursor.execute(sql_statment)

        connection.commit()
        connection.close()

    def getConfigData(self, db, section, key, value):
        pass

class Batteriestatus(QtWidgets.QDialog, configuration):
    # Variable initialisieren
    #pwd = os.getcwd()

    # Get script dir
    fixed_value = 'test_get_script_path.py'
    this_file = os.path.abspath(__file__)
    pwd = os.path.dirname(this_file)
    #pwd = "/usr/local/bin/Batterieanzeige"
    configDB = pwd + "/config.db"

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

        # Write batterie state to db
        self.getBATOstate()

        # SQLite 3 DB für die Configuration erstellen
        if not os.path.exists(self.configDB):
            configuration.createDB(self, self.configDB)

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

        # Programm PID in die Config Datei schreiben
        configuration.setDataUpdateFromTable(self, db=self.configDB, table="config", section='programmInfo', key='programmPID', value=str(os.getpid()))

    def getBATOstate(self):
        fobj = open(self.fileBATOstate, 'r')
        for line in fobj:
            BATOstate = line.rstrip()
        fobj.close()

        # Set bato state to db
        configuration.setDataUpdateFromTable(self, db=self.configDB, table="config", section='lastProgrammRun', key='batoState', value=str(BATOstate))

    def getBATOcapacity(self):
        # Variable initialisieren
        #fileBATOcapacity = "/sys/class/power_supply/BAT0/capacity"

        # Read Batterie charge
        fobj = open(self.fileBATOcapacity, 'r')
        for line in fobj:
            setBATOcapacityInGui = line.rstrip()
        fobj.close()

        configuration.setDataUpdateFromTable(self, db=self.configDB, table="config", section='lastProgrammRun', key='batoCapacity', value=str(setBATOcapacityInGui))

        return setBATOcapacityInGui

    # Es wird geprüft, wann das Skript das letztes mal gestartet wurde.
    def checkLastScriptRun(self):
        lastProgrammRun = {}
        getBATOcapacity = self.getBATOcapacity()
        getLastBATOcapacityToRunScript = self.pwd + "/lastBATOcapacity"
        getToday = date.today()

        lastProgrammRun.update({'time' : str(getToday)})
        configuration.setDataUpdateFromTable(self, db=self.configDB, table="config", section='lastProgrammRun', key='today', value=str(getToday))

        if os.path.isfile(getLastBATOcapacityToRunScript):
            #print('Exist\n' + getLastBATOcapacityToRunScript)
            #lastBATOcapacity = "lastBATOcapacity"
            statusFile = open(getLastBATOcapacityToRunScript, "r+")
            getLastBATOcapacityFile = statusFile.read().split(',')
            getLastBATOcapacity = getLastBATOcapacityFile[0]

            lastProgrammRun.update({'batterieentladung' : getLastBATOcapacity})
            #print(getLastBATOcapacity + "\n" + self.getBATOcapacity())
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
        # Set Programm PID value to 0
        print(self.configDB)
        self.setDataUpdateFromTable(db=self.configDB, table="config", section='programmInfo', key='programmPID', value='0')
        # Exit App with button "buttonExit"
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = Batteriestatus()
    dialog.show()

    #print("Count: " + dialog.getCount)

    sys.exit(app.exec_())
