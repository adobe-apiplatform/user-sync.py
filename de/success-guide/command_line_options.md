---
layout: default
lang: de
nav_link: Befehlszeile
nav_level: 2
nav_order: 310
parent: success-guide
page_id: command-line-options
---

# Befehlszeilenoptionen

[Voriger Abschnitt](monitoring.md) \| [Zurück zum Inhaltsverzeichnis](index.md) \|  [Nächster Abschnitt](scheduling.md)

Über die Befehlszeile der Benutzersynchronisation werden die zu verarbeitenden Benutzer ausgewählt. Dort können Sie auch festlegen, ob Sie die Mitgliedschaft in einer Benutzergruppe oder der Produktkonfiguration verwalten möchten und wie bei einer Kontolöschung verfahren werden soll, sowie einige andere Optionen angeben.

## Benutzer


| Befehlszeilen-option „users“  | Verwendung           |
| ------------- |:-------------| 
|   `--users all` |    Alle Benutzer im Verzeichnis werden eingeschlossen. |
|   `--users group "g1,g2,g3"`  |    Die benannten Verzeichnisgruppen werden als Auswahl der Benutzer herangezogen. <br>Die Liste umfasst Benutzer, die Mitglied in einer dieser Gruppen sind. |
|   `--users mapped`  |    Dieser Befehl entspricht `--users group g1,g2,g3,...`, wobei `g1,g2,g3,...` alle Verzeichnisgruppen in der Gruppenzuordnung der Konfigurationsdatei sind.|
|   `--users file f`  |    Die Benutzermenge wird aus der Datei „f“ ausgelesen. Das LDAP-Verzeichnis wird in diesem Fall nicht verwendet. |
|   `--user-filter pattern`    |  Der Befehl kann mit den Optionen oben kombiniert werden, um die Benutzerauswahl zu filtern und einzuschränken. <br>„pattern“ ist eine Zeichenfolge im Python-Format für reguläre Ausdrücke. <br>Der Benutzername muss dem Muster entsprechen, um einbezogen zu werden. <br>Das richtige Muster zu finden, kann eine Herausforderung sein. Unten finden Sie Beispiele dazu. Weitere Informationen erhalten Sie in der [Python-Dokumentation](https://docs.python.org/2/library/re.html). |


Wenn Sie alle im Verzeichnis aufgelisteten Benutzer mit Adobe synchronisieren möchten, verwenden Sie die Option `--users all`. Wenn die Synchronisation nur einige Benutzer betreffen soll, können Sie die Auswahl eingrenzen, indem Sie die LDAP-Abfrage in der Konfigurationsdatei „connector-ldap.yml“ ändern (und die Option `--users all` verwenden). Sie können die Benutzerauswahl auch über die Gruppenmitgliedschaft (mit „--users group“) beschränken. Bei beiden Befehlen können Sie mit der Option `--user-filter pattern` die Auswahl der zu synchronisierenden Benutzer weiter eingrenzen.

Wenn Sie kein Verzeichnissystem verwenden, können Sie die Benutzer mit dem Befehl `--users file f` aus einer CSV-Datei auslesen. Welches Format Sie dazu verwenden, sehen Sie in der Beispieldatei mit Benutzern („csv inputs - user and remove lists/users-file.csv“). Die in CSV-Dateien aufgeführten Gruppen stellen die Namen dar, aus den Sie wählen können. Die Zuordnung zu Adobe-Benutzergruppen oder Produktkonfigurationen entspricht der Zuordnung zu Verzeichnisgruppen.

## Gruppen

Wenn Sie keine Produktlizenzen mit der Benutzersynchronisation verwalten, müssen Sie die Gruppenzuordnung in der Konfigurationsdatei nicht angeben und keine Befehlszeilenparameter für die Gruppenverarbeitung hinzufügen.

Wenn Sie mit der Benutzersynchronisation Lizenzen verwalten, fügen Sie in der Befehlszeile die Option `--process-groups` hinzu.


## Kontolöschung


Welche Aktion ausgeführt werden soll, wenn ein Adobe-Konto, aber kein entsprechendes Verzeichniskonto gefunden wird (ein „Nur Adobe“-Benutzer), kann mit verschiedenen Befehlszeilenoptionen gesteuert werden.
Nur solche Benutzer, die bei der Verzeichnisabfrage und -filterung zurückgegeben werden, gelten als im Unternehmensverzeichnis vorhanden. Die möglichen Vorgehensweisen reichen vom völligen Ignorieren bis zur vollständigen Löschung.



| Befehlszeilen-option       ...........| Verwendung           |
| ------------- |:-------------| 
|   `--adobe-only-user-action exclude`                        |  Bei Konten, die nur in Adobe vorhanden sind und denen kein Verzeichniskonto entspricht, wird keine Aktion ausgeführt. Adobe-Gruppenmitgliedschaften werden auch dann nicht aktualisiert, wenn die Option `--process-groups` angegeben ist. |
|   `--adobe-only-user-action preserve`                        |  Konten, die nur in Adobe vorhanden sind und denen kein Verzeichniskonto entspricht, werden nicht entfernt und nicht gelöscht. Adobe-Gruppenmitgliedschaften werden aktualisiert, wenn die Option `--process-groups` angegeben wird. |
|   `--adobe-only-user-action remove-adobe-groups` |    Das Adobe-Konto bleibt bestehen, aber Lizenzen und <br>Gruppenmitgliedschaften werden entfernt. |
|   `--adobe-only-user-action remove`  |    Das Adobe-Konto bleibt bestehen, aber Lizenzen und Gruppenmitgliedschaften werden entfernt und das Konto wird in der Adobe Admin Console nicht mehr angezeigt.   |
|   `--adobe-only-user-action delete`  |    Das Adobe-Konto wird gelöscht und aus den <br>Adobe-Produktkonfigurationen und Benutzergruppen entfernt. Der gesamte Speicherplatz wird freigegeben und die Einstellungen werden gelöscht. |
|   `--adobe-only-user-action write-file f.csv`    |  Keine das Konto betreffenden Aktionen werden ausgeführt. Der Benutzername wird zur späteren Verwendung in eine Datei geschrieben. |




## Weitere Optionen

`--test-mode`: führt dazu, dass die Benutzersynchronisation alle Verarbeitungsschritte ausführt, einschließlich der Abfrage des Verzeichnisses und des Aufrufs der Adobe User Management APIs, die für die Verarbeitung der Anforderung erforderlich sind. Es wird jedoch keine tatsächliche Aktion ausgeführt. Es werden keine Benutzer erstellt, gelöscht und geändert.

`--update-user-info`: führt dazu, dass die Benutzersynchronisation nach Änderungen des Vornamens, Nachnamens oder der E-Mail-Adresse von Benutzern sucht und die Adobe-Informationen aktualisiert, wenn sie nicht den Verzeichnisinformationen entsprechen. Wenn Sie diese Option angeben, kann sich die Verarbeitungszeit erhöhen.


## Beispiele

Einige Beispiele:

`user-sync --users all --process-groups --adobe-only-user-action remove`

- Alle Benutzer werden entsprechend den Konfigurationseinstellungen verarbeitet, die Adobe-Gruppenmitgliedschaft wird aktualisiert und Adobe-Benutzer, die sich nicht im Verzeichnis befinden, werden auf Adobe-Seite entfernt (alle zugewiesenen Lizenzen werden freigegeben). Das Adobe-Konto wird nicht gelöscht, sodass es später wieder hinzugefügt werden kann und die gespeicherten Assets abgerufen werden können.
    
`user-sync --users file users-file.csv --process-groups --adobe-only-user-action remove`

- Die Datei „users-file.csv“ (die Master-Benutzerliste) wird ausgelesen. Es wird nicht versucht, eine Verbindung mit einem Verzeichnisdienst wie AD und LDAP herzustellen. Die Adobe-Gruppenmitgliedschaft wird entsprechend den Informationen in der Datei aktualisiert. Adobe-Konten, die in der Datei nicht aufgelistet sind, werden ggf. entfernt (siehe oben).

## Befehlszeile definieren

Sie können mit einigen Testläufen beginnen, ohne Optionen zum Löschen anzugeben.

&#9744; Stellen Sie die gewünschten Befehlszeilenoptionen für die Benutzersynchronisation zusammen.


[Voriger Abschnitt](monitoring.md) \| [Zurück zum Inhaltsverzeichnis](index.md) \|  [Nächster Abschnitt](scheduling.md)
