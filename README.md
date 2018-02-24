<h2>viewBatteryWindow</h2>

<h3>Voraussetzungen:</h3>
<ul>
	<li>Linux als Betriebssytem</li>
	<li>Python 3</li>
	<li>PyQt5</li>
</ul>
<h3>Skript Beschreibung</h3>
Dieses Skript öffnet ein Fenster das den aktuellen Batterie Stand anzeigt.<br />
Als Datenquelle wird eine sqlite3 Datenbank verwendet, die beim ersten Start des Skriptes im Arbeitsverzeichniss
erstellt wird.<br />
<h3>Programaufruf per Crontab:</h3>
*/5  *  *  *  * DISPLAY=:0 /usr/bin/python /pfad/zum/skript/mainWindow.py 30<br />
<h3>Beschreibung:</h3>
Über diesen User Crontab Eintrag, wird das Skript alle 5 Minuten auf dem Display :0 gestartet.
Mit dem mitgegebenen Parameter, wird festgelegt zu wieviel Prozent der Akku höchstens noch geladen
sein darf, damit das Skript weiter ausgeführt wird.
<h3>Laufzeit Voraussetzungen</h3>
<ul>
	<ol>Der Akku wird nicht aufgeladen</ol>
	<ol>Es muss als Parameter der Akku Ladestand als Zahl mitgegeben werden</ol>
	<ol>Das Skript darf nicht schon gestartet sein</ol>
</ul>
<h3>Skript über ein Crontab starten</h3>
<ul> 
    <ol>Shell öffnen</ol>
    <ol>Den Befehl "crontab -e" eingeben</ol>
    <ol>Crontab eintragen<br />*/5  *  *  *  * DISPLAY=:0 /usr/bin/python /pfad/zum/skript/mainWindow.py 30</ol>
    <ol>Crontab speichern</ol>
</ul>

<h3>Author</h3>
Thorsten Zelt
