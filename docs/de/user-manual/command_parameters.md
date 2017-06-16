---
layout: default
lang: de
nav_link: Befehlsparameter
nav_level: 2
nav_order: 40
---


# Befehlsparameter

---

[Voriger Abschnitt](configuring_user_sync_tool.md)  \| [Nächster Abschnitt](usage_scenarios.md)

---
Sobald die Konfigurationsdateien eingerichtet wurden, können Sie das Benutzer-Synchronisationstool an der Befehlszeile oder in einem Skript ausführen. Führen Sie zum Ausführen des Tools den folgenden Befehl in einer Befehlszeile oder aus einem Skript aus:

`user-sync` \[ _Optionale Parameter_ \]

Das Tool akzeptiert optionale Parameter, die sein spezifisches Verhalten in diversen Situationen bestimmen.


| Parameter&nbsp;und&nbsp;Angaben&nbsp;zu&nbsp;Argumenten | Beschreibung |
|------------------------------|------------------|
| `-h`<br />`--help` | Diese Hilfemeldung wird angezeigt und der Vorgang beendet. |
| `-v`<br />`--version` | Die Versionsnummer des Programms wird angezeigt und der Vorgang beendet. |
| `-t`<br />`--test-mode` | API-Aktionsaufrufe werden im Testmodus ausgeführt (Änderungen werden nicht ausgeführt). Es werden die Aktionen protokolliert, die ausgeführt werden würden. |
| `-c` _dateiname_<br />`--config-filename` _dateiname_ | Der komplette Pfad zur Hauptkonfigurationsdatei; ein absoluter Pfad oder ein Pfad relativ zum Arbeitsordner. Der Standarddateiname lautet „user-sync-config.yml“ |
| `--users` `all`<br />`--users` `file` _eingabepfad_<br />`--users` `group` _grp1,grp2_<br />`--users` `mapped` | Hiermit werden die für die Synchronisation ausgewählten Benutzer angegeben. Der Standardwert ist `all`, d. h. alle Benutzer im Verzeichnis. Wenn `file` angegeben wird, werden Benutzerspezifikationen aus der vom Argument benannten CSV-Datei als Eingabe angenommen. Bei Angabe von `group` wird das Argument als durch Kommas getrennte Liste von Gruppen im Unternehmensverzeichnis interpretiert und es werden nur Benutzer in diesen Gruppen ausgewählt. Die Angabe von `mapped` entspricht der Angabe von `group`, wobei alle Gruppen in der Gruppenzuordnung der Konfigurationsdatei aufgelistet sind. Dies ist häufig der Fall, wenn lediglich die Benutzer in zugeordneten Gruppen synchronisiert werden sollen.|
| `--user-filter` _regex-muster_ | Beschränken Sie hiermit die Gruppe von Benutzern, die für die Synchronisation überprüft werden, auf diejenigen, die einem Muster entsprechen, welches in einem regulären Ausdruck angegeben wird. Informationen zum Erstellen regulärer Ausdrücke in Python finden Sie in der [Dokumentation zu regulären Ausdrücken in Python](https://docs.python.org/2/library/re.html). Der Benutzername muss vollständig dem regulären Ausdruck entsprechen.|
| `--update-user-info` | Bei dieser Angabe werden Benutzerinformationen synchronisiert. Wenn sich die Informationen auf der Unternehmensverzeichnisseite und der Adobe-Seite unterscheiden, wird die Adobe-Seite aktualisiert, sodass Übereinstimmung hergestellt wird. Hierzu zählen die Felder „firstname“ und „lastname“. |
| `--process-groups` | Bei dieser Angabe werden Informationen zur Gruppenmitgliedschaft synchronisiert. Wenn sich die Mitgliedschaft in zugeordneten Gruppen auf Unternehmensverzeichnisseite und Adobe-Seite unterscheiden, wird die Gruppenmitgliedschaft auf Adobe-Seite aktualisiert, sodass Übereinstimmung hergestellt wird. Dabei werden u. a. Gruppenmitgliedschaften für Adobe-Benutzer entfernt, die nicht auf der Verzeichnisseite aufgelistet sind (es sei denn, die Option `--adobe-only-user-action exclude` ist ebenfalls ausgewählt) |
| `--adobe-only-user-action preserve`<br />`--adobe-only-user-action remove-adobe-groups`<br />`--adobe-only-user-action  remove`<br />`--adobe-only-user-action delete`<br /><br/>`--adobe-only-user-action  write-file`&nbsp;dateiname<br/><br/>`--adobe-only-user-action  exclude` | Bei dieser Angabe gilt Folgendes: Wenn Benutzerkonten auf Adobe-Seite gefunden werden, die im Verzeichnis nicht vorhanden sind, ist die angegebene Aktion auszuführen. <br/><br/>`preserve`: Es wird keine Aktion in Bezug auf die Löschung von Konten ausgeführt. Dies ist die Standardeinstellung. Möglicherweise treten dennoch Änderungen der Gruppenmitgliedschaft auf, wenn die Option `--process-groups` angegeben wurde.<br/><br/>`remove-adobe-groups`: Das Konto wird aus Benutzergruppen und Produktkonfigurationen entfernt, alle belegten Lizenzen werden freigegeben; es wird jedoch als aktives Konto in der Organisation beibehalten.<br><br/>`remove`: Zusätzlich zu „remove-adobe-groups“ wird das Konto auch aus der Organisation entfernt, das Benutzerkonto verbleibt jedoch mit seinen zugeordneten Elementen in der Domäne und kann der Organisation ggf. wieder hinzugefügt werden.<br/><br/>`delete`: Neben der Aktion zum Entfernen wird das Konto entfernt, wenn seine Domäne im Besitz der Organisation ist.<br/><br/>`write-file`: Es wird keine Aktion in Bezug auf die Löschung von Konten ausgeführt. Die Liste der Benutzerkonten, die auf Adobe-Seite, jedoch nicht im Verzeichnis vorhanden sind, wird in die angegebene Datei geschrieben. Sie können diese Datei in einer späteren Ausführung an das Argument `--adobe-only-user-list` übergeben. Möglicherweise treten dennoch Änderungen der Gruppenmitgliedschaft auf, wenn die Option `--process-groups` angegeben wurde.<br/><br/>`exclude`: Es wird keine Aktualisierung, gleich welcher Art, auf die Benutzer angewendet, die lediglich auf Adobe-Seite vorhanden sind. Dies wird verwendet, wenn Aktualisierungen bestimmter Benutzer über eine Datei (--users file f) vorgenommen werden, wobei in der Datei nur Benutzer aufgelistet sind, für die ausdrücklich eine Aktualisierung benötigt wird, und alle übrigen Benutzer werden ignoriert.<br/><br>Es werden nur zulässige Aktionen ausgeführt. Konten vom Typ adobeID sind im Besitz des Benutzers, sodass die Löschaktion die gleiche Wirkung wie das Entfernen hat. Dies gilt auch für Adobe-Konten, die im Besitz anderer Organisationen sind. |
| `adobe-only-user-list` _dateiname_ | Hiermit wird eine Datei angegeben, aus der eine Liste von Benutzern gelesen wird. Diese Liste wird als definitive Liste der „Nur Adobe“-Benutzerkonten verwendet, für die Aktionen auszuführen sind. Eine der Anweisungen für `--adobe-only-user-action` muss ebenfalls angegeben werden und die zugehörige Aktion wird auf die Benutzerkonten in der Liste angewendet. Die Option `--users` ist nicht zulässig, wenn diese Option vorhanden ist: Es können nur Entfernungsaktionen verarbeitet werden. |
{: .bordertablestyle }

---

[Voriger Abschnitt](configuring_user_sync_tool.md)  \| [Nächster Abschnitt](usage_scenarios.md)
