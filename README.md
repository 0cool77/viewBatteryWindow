Dieses Skript Erstellt ein Fenster das den aktuellen Batterie Stand anzeigt.

Voraussetzungen:
- Linux als Betriebssytem
- Python 3
- PyQt5

Programmaufruf per Crontab
*/5  *  *  *  * DISPLAY=:0 /usr/bin/python /pfad/zum/skript/mainWindow.py 30

Beschreibung:
Über diesen User Crontab Eintrag, wird das Skript alle 5 Minuten auf dem ersten Display gestartet.
Mit dem mitgegebenen Parameter, wird festgelegt zu wieviel Prozent der Akku höchstens noch geladen
sein darf, damit das Skript weiter ausgeführt wird.

Die folgenden Bedingungen müssen gegeben sein, damit das Skript nicht vorzeitig beendet und sich 
das Fenster nicht öffnet.

1. Der Akku wird nicht aufgeladen
2. Es muss als Parameter der Akku Ladestand als Zahl mitgegeben werden
3. Das Skript darf nicht schon gestartet sein
4. Das Skript darf nicht schon gestartet sein
5. Das Skript darf nicht schon gestartet sein

Als Datenquelle wird eine sqlite3 Datenbank verwendet.

