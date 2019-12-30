#!/bin/env python

import sys
from PyQt5 import uic, QtCore, QtWidgets, Qt
from PyQt5.QtCore import Qt
import os
from datetime import date
import sqlite3
import subprocess


class configuration():
    def __init__(self):
        pass

    def createDB(self, db):

        #print("###########################################")
        #print("")
        #print("DB wird erstellt")

        connection = sqlite3.connect(db)

        cursor = connection.cursor()

        sql_command = """
        CREATE TABLE IF NOT EXISTS config ( 
        id INTEGER PRIMARY KEY, 
        section VARCHAR(20), 
        key VARCHAR(30), 
        value CHAR(50),
        count INTEGER(2));"""

        cursor.execute(sql_command)

        connection.commit()
        connection.close()

        #print("DB wird befüllt")

        # Set dafault value to table
        self.setConfigData(db, section='programmInfo', key='programmPID', value='0')
        self.setConfigData(db, section='lastProgrammRun', key='today', value='getToday')
        self.setConfigData(db, section='lastProgrammRun', key='batoState', value='entladen')
        self.setConfigData(db, section='lastProgrammRun', key='batoCapacity', value='0')
        self.setConfigData(db, section='programmInfo', key='count', value='0')

        #print("")
        #print("###########################################")

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
        #print("DB: " + db + "\nTable: " + table + "\nSection: " + section + "\nKey: " + key + "\nValue: " + value)
        connection = sqlite3.connect(db)
        cursor = connection.cursor()

        sql_statement = "UPDATE " + table + " SET value  = '" + value + "' WHERE key = '" + key + \
                       "' AND  section = '" + section + "';"
        #print("SQL: " + sql_statement)

        cursor.execute(sql_statement)

        connection.commit()
        connection.close()

    def getDataFromTable(self, db, table, section, key):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()

        cursor.execute("select * from " + table + " where section = '" + section + "' and key = '" + key + "';")
        result = cursor.fetchall()

        connection.close()
        return result


class Batteriestatus(QtWidgets.QDialog, configuration):
    """
        Für die Batterieabfrage das Tool ACPI verwenden
        - acpi -i liefert alle Infos die benötigt werden
            - acpi -i | head -n1 -> Letzte Zeile lesen
            - acpi -i | tail -1 -> Erste Zeile lesen
    """

    # Variable initialisieren

    # Get script dir
    fixed_value = 'test_get_script_path.py'
    this_file = os.path.abspath(__file__)
    pwd = os.path.dirname(this_file)
    configDB = pwd + "/config.db"
    pathToPowerSupply = "/sys/class/power_supply" 
    folderBatNumber1 = "/BAT0"
    folderBatNumber2 = "/BAT1"
    folderBatNumber3 = "/BAT2"
    fileBATcapacity = "/capacity"
    fileBATstatus = "/status"
    msgFileNotFound = "File not found"

    tmpBildschirmAufloesung = subprocess.getoutput(
        "/usr/bin/xrandr | grep -v disconnected | grep -A 1 connected | grep -v connected | awk '{print $1}'",).split()
    # print(tmpBildschirmAufloesung1)
   
    if os.path.exists ( pathToPowerSupply + folderBatNumber1 ):
        fileBATOcapacity = pathToPowerSupply + folderBatNumber1 + fileBATcapacity
        fileBATOstate = pathToPowerSupply + folderBatNumber1 + fileBATstatus
    elif os.path.exists ( pathToPowerSupply + folderBatNumber2 ):
        fileBATOcapacity = pathToPowerSupply + folderBatNumber2 + fileBATcapacity
        fileBATOstate = pathToPowerSupply + folderBatNumber2 + fileBATstatus
    elif os.path.exists ( pathToPowerSupply + folderBatNumber3 ):
        fileBATOcapacity = pathToPowerSupply + folderBatNumber3 + fileBATcapacity
        fileBATOstate = pathToPowerSupply + folderBatNumber3 + fileBATstatus
    else:
        fileBATcapacity = msgFileNotFound 
        fileBATstatus = msgFileNotFound

    # fileBATOcapacity = "/sys/class/power_supply/BAT0/capacity"
    # fileBATOstate = "/sys/class/power_supply/BAT0/status"

    if len(tmpBildschirmAufloesung) > 2:
        getBildschimAufloesung = tmpBildschirmAufloesung[len(tmpBildschirmAufloesung) - 1]
    else:
        getBildschimAufloesung = tmpBildschirmAufloesung[0]

    def __init__(self, parent=None):
        configuration.__init__(self)

        # print(" ############# SQLite 3 DB für die Configuration erstellen ##################")
        if not os.path.exists(self.configDB):
            configuration.createDB(self, self.configDB)
        
        if self.fileBATstatus == self.msgFileNotFound: 
            print ("Der Batterie Status konnte nicht abgefragt werden.\nDas Skript wird beendet.")
            sys.exit()

        # Write batterie state to db
        self.setBATOstate()

        if self.fileBATOcapacity == self.msgFileNotFound:
            print ("Der Ladestand konnte nicht abgefragt werden.\nDas Skript wird beendet.")
            sys.exit()


        # Write BATO capacity to db
        self.setBATOcapcity()

        # Check Skrip Abhängigkeiten
        self.checkScriptRun()

        self.checkLastScriptRun()
        super().__init__(parent)
        self.ui = uic.loadUi(self.pwd + "/main.ui", self)
        
        # Create Slot
        self.ui.buttonExit.clicked.connect(self.pushExit)

        # Set Desktop Resolution
        getDesktopResolution = self.getBildschimAufloesung.split('x')
        getDesktopResolutionWidth = getDesktopResolution[0]

        # Fenster Breite auf die gesamte Bildschirmbreite erweitern
        self.setFixedWidth(int(getDesktopResolutionWidth))

        # Set title to hint (verstecken)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)

        # Get BATO capcity form db
        self.BATOcapacity = configuration.getDataFromTable(self, self.configDB, table='config',
                                                           section='lastProgrammRun', key='batoCapacity')

        # Set label Text "statusAusgabe"
        self.statusAusgabe.setText(
            "<font color='white'>Die Batterie hat noch " + str(self.BATOcapacity[0][3]) + "% Ladung</font>")

        # Set window background color
        self.setAutoFillBackground(True)
        getColorPalette = self.palette()
        getColorPalette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(getColorPalette)

        # Set button "buttonExit" Color
        self.buttonExit.setStyleSheet("background-color: black; color: white")

    def checkScriptRun(self):
        BATOstate =  self.getDataFromTable(db=self.configDB, table='config', section='lastProgrammRun',
                                           key='batoState')
        BATOcapacity = self.getDataFromTable(db=self.configDB, table='config', section='lastProgrammRun',
                                             key='batoCapacity')
        fileName = __file__.split('/')
        fileName = fileName[len(fileName)-1]

        if not str(BATOstate[0][3]) == "Discharging":
            print("Skript wird beendet.\nKeine Batterie Entladung")
            sys.exit()

         # Prüfen ob ein Argument mitgegeben wurde das den Batterie Stand angibt der maximal sein darf,
         # damit das Skript startet
        if len(sys.argv) != 2:
            print("example: \n\t" + sys.argv[0] + " Prozentzahl")
            sys.exit()

        try:
            if int(sys.argv[1]) <= int(BATOcapacity[0][3]):
                print("Batterie zu viel geladen: " + str(BATOcapacity[0][3]))
                sys.exit()
        except ValueError:
            print("Bitte geben Sie ein Zahl ein!")
            sys.exit()

        # PID aus DB auslesen
        ScriptPIDinDB = self.getDataFromTable(db=self.configDB, table='config', section='programmInfo',
                                              key='programmPID')

        # Mehrfache Skript Ausführung verhindern
        if len(subprocess.getoutput("ps -fC 'python " + fileName  + "' | grep '" + fileName + "'").split()) > 18:
            print(len(subprocess.getoutput("ps -fC 'python " + fileName  + "'").split()))
            sys.exit()

        if len(subprocess.getoutput("ps -fC 'python3 " + fileName  + "' | grep '" + fileName  + "'").split()) > 18:
            print(len(subprocess.getoutput("ps -fC 'python3 " + fileName + "' | grep '" + fileName  + "'").split()))
            sys.exit()

        # prüfen ob die PID in der DB 0 ist
        if str(ScriptPIDinDB[0][3]) == '0':
            # Programm PID in die Config DB schreiben
            configuration.setDataUpdateFromTable(self, db=self.configDB, table="config", section='programmInfo',
                                                 key='programmPID', value=str(os.getpid()))

        # Prüfen ob die PID in der DB gleich der PID des Programmes ist
        if str(ScriptPIDinDB[0][3]) != str(os.getpid()):
            # Programm PID in die Config DB schreiben
            configuration.setDataUpdateFromTable(self, db=self.configDB, table="config", section='programmInfo',
                                                 key='programmPID', value=str(os.getpid()))

    def setBATOstate(self):
        fobj = open(self.fileBATOstate, 'r')
        for line in fobj:
            # Set bato state to db
            configuration.setDataUpdateFromTable(self, db=self.configDB, table="config", section='lastProgrammRun',
                                                 key='batoState', value=str(line.rstrip()))
        fobj.close()

    def setBATOcapcity(self):
        # Read Batterie charge
        fobj = open(self.fileBATOcapacity, 'r')
        for line in fobj:
            setBATOcapacityInDB = line.rstrip()
        fobj.close()

        configuration.setDataUpdateFromTable(self, db=self.configDB, table="config", section='lastProgrammRun',
                                             key='batoCapacity', value=str(setBATOcapacityInDB))

    # Es wird geprüft, wann das Skript das letztes mal gestartet wurde.
    def checkLastScriptRun(self):
        getToday = date.today()

        configuration.setDataUpdateFromTable(self, db=self.configDB, table="config", section='lastProgrammRun',
                                             key='today', value=str(getToday))

    def pushExit(self):
        # Set Programm PID value to 0
        self.setDataUpdateFromTable(db=self.configDB, table="config", section='programmInfo', key='programmPID',
                                    value='0')
        # Exit App with button "buttonExit"
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = Batteriestatus()
    dialog.show()

    sys.exit(app.exec_())
