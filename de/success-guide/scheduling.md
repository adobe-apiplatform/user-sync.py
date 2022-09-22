---
layout: default
lang: de
nav_link: Zeitplan
nav_level: 2
nav_order: 320
---

# Einrichten eines Zeitplans für die Benutzersynchronisation


[Voriger Abschnitt](command_line_options.md) \| [Nächster Abschnitt](index.md) 

## Einrichten der Ausführung nach einem Zeitplan unter Windows

Erstellen Sie zunächst eine Stapeldatei, in der das Benutzer-Synchronisationstool aufgerufen wird und die Ausgabe übergeben wird, um relevante Protokolleinträge für eine Zusammenfassung auszulesen. Erstellen Sie dazu die Datei „run_sync.bat“ mit folgendem Inhalt:

	cd user-sync-directory
	python user-sync.pex --users file example.users-file.csv --process-groups | findstr /I "==== ----- WARNING ERROR CRITICAL Number" > temp.file.txt
	rem email the contents of temp.file.txt to the user sync administration
	your-mail-tool –send file temp.file.txt


Unter Windows gibt es kein Standard-Befehlszeilentool für E-Mails, es sind aber verschiedene Lösungen erhältlich.
Sie müssen die Ihrer Umgebung entsprechenden Befehlszeilenoptionen angeben.

In diesem Code wird die Aufgabenplanung von Windows verwendet, um das Benutzer-Synchronisationstool täglich um 16:00 Uhr auszuführen:

	C:\> schtasks /create /tn "Adobe User Sync" /tr pfad_zur_bat-datei/run_sync.bat /sc DAILY /st 16:00

Einzelheiten können Sie der Dokumentation zur Windows-Aufgabenplanung (help schtasks) entnehmen.

Beachten Sie, dass Befehle, die von der Befehlszeile problemlos ausgeführt werden können, beim Einrichten von geplanten Aufgaben oft nicht mehr funktionieren, weil sich das aktuelle Verzeichnis oder die Benutzer-ID unterscheidet. Wenn Sie die geplante Aufgabe zum ersten Mal ausführen, sollten Sie einen der Testmodusbefehle ausführen (wie im Abschnitt „Ausführen eines Testlaufs“ beschrieben).


## Einrichten der Ausführung nach einem Zeitplan auf Unix-Systemen

Erstellen Sie zunächst ein Shell-Skript, in dem das Benutzer-Synchronisationstool aufgerufen wird und die Ausgabe übergeben wird, um relevante Protokolleinträge für eine Zusammenfassung auszulesen. Erstellen Sie dazu die Datei „run_sync.sh“ mit folgendem Inhalt:

	cd user-sync-directory
	./user-sync --users file example.users-file.csv --process-groups |  grep "CRITICAL\\|WARNING\\|ERROR\\|=====\\|-----\\|number of\\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” 
    Your_admin_mailing_list@example.com


Sie müssen Ihre eigenen Befehlszeilenoptionen für das Benutzer-Synchronisationstool und die E-Mail-Adresse angeben, an die der Bericht gesendet werden soll.

Durch diesen Eintrag in der Unix-Crontab wird das Benutzer-Synchronisationstool täglich um 04:00 Uhr ausgeführt: 

	0 4 * * *  pfad_zum_Sync_shell_befehl/run_sync.sh 

Cron kann auch so eingerichtet werden, dass Ergebnisse per E-Mail an einen bestimmten Benutzer oder Verteiler versendet werden. Weitere Einzelheiten können Sie der Cron-Dokumentation für Ihr Unix-System entnehmen.

Beachten Sie, dass Befehle, die von der Befehlszeile problemlos ausgeführt werden können, beim Einrichten von geplanten Aufgaben oft nicht mehr funktionieren, weil sich das aktuelle Verzeichnis oder die Benutzer-ID unterscheidet. Wenn Sie die geplante Aufgabe zum ersten Mal ausführen, sollten Sie einen der Testmodusbefehle ausführen (wie im Abschnitt „Ausführen eines Testlaufs“ beschrieben).


[Voriger Abschnitt](command_line_options.md) \| [Nächster Abschnitt](index.md) 

