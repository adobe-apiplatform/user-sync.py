---
layout: default
lang: de
title: Benötigte Informationen
nav_link: Benötigte Informationen
nav_level: 2
nav_order: 110
parent: success-guide
page_id: before-you-start
---

# Benötigte Informationen

[Zurück zum Inhaltsverzeichnis](index.md) \| [Nächster Abschnitt](layout_orgs.md)

## Einführung in die Benutzersynchronisation

Die Adobe-Benutzersynchronisation ist ein Befehlszeilentool, das Benutzer- und Gruppeninformationen aus dem Unternehmensverzeichnissystem (z. B. einem Active Directory- oder sonstigen LDAP-System) oder aus anderen Quellen in das Adobe-Benutzerverwaltungssystem verschiebt. Der Benutzersynchronisation liegt das Konzept zugrunde, dass das Unternehmensverzeichnissystem die maßgebliche Quelle für Informationen über Benutzer ist. Benutzerinformationen werden von dort in das Adobe-Benutzerverwaltungssystem übertragen. Dieser Vorgang wird durch eine Reihe von Konfigurationsdateien und Befehlszeilenoptionen für die Benutzersynchronisation gesteuert.

Bei jeder Ausführung des Tools wird nach Unterschieden zwischen den Benutzerinformationen in beiden Systemen gesucht und das Adobe-System wird so aktualisiert, dass es dem Unternehmensverzeichnis entspricht.

Mit der Benutzersynchronisation können Sie ein neues Adobe-Konto erstellen, wenn das Verzeichnis einen neuen Benutzer aufweist, die Kontoinformationen aktualisieren, wenn sich bestimmte Felder im Verzeichnis geändert haben, und die Mitgliedschaft in einer Produktkonfiguration oder in einer Benutzergruppe aktualisieren, um die Zuweisung von Lizenzen an Benutzer zu steuern. Sie können auch Adobe-Konten löschen, wenn Benutzer aus dem Unternehmensverzeichnis entfernt werden.

Mit benutzerdefinierten Verzeichnisattributen haben Sie außerdem die Kontrolle über die Werte, die in das Adobe-Konto importiert werden.

Die Synchronisation ist auch ohne Unternehmensverzeichnissystem möglich, es genügt eine einfache CSV-Datei. Diese Lösung eignet sich für kleine Unternehmen und Abteilungen, die über kein zentral verwaltetes Verzeichnissystem verfügen.

Wenn Sie hingegen über ein großes Verzeichnis verfügen, können Sie die Benutzersynchronisation auch über Push-Benachrichtigungen bei Änderungen im Verzeichnissystem veranlassen, statt eine große Anzahl von Benutzerkonten zu vergleichen.

## Terminologie

- Benutzergruppe: eine benannte Gruppe von Benutzern im Adobe-Benutzerverwaltungssystem
- PK: eine Produktkonfiguration. Ein Adobe-Mechanismus, der wie Gruppen funktioniert. Wenn Sie Benutzer einer PK hinzufügen, erhalten diese Zugriff auf ein bestimmtes Adobe-Produkt.
- Verzeichnis: ein allgemeiner Begriff für ein Benutzerverzeichnissystem wie Active Directory (AD), LDAP oder eine CSV-Datei mit Benutzern
- Verzeichnisgruppe: eine benannte Gruppe von Benutzern im Verzeichnis

 

## Mögliche Konfigurationen
Die Benutzersynchronisation ist ein umfassendes Tool, mit dem Sie viele verschiedene Konfigurationen umsetzen und Prozesse abbilden können.

Je nach Unternehmensgröße und erworbenen Adobe-Produkten verfügen Sie in Ihrer Adobe-Umgebung wahrscheinlich über mindestens eine Admin Console und Organisation. Jede Organisation hat einen oder mehrere Administratoren und Sie müssen Administrator sein, um Anmeldeinformationen für den Zugriff auf die Benutzersynchronisation einzurichten.

Jede Adobe-Organisation besteht aus mehreren Benutzern. Jeder Benutzer muss einen dieser drei Typen besitzen:

- Adobe ID: Der Benutzer hat dieses Konto erstellt und ist dessen Eigentümer. Das Konto und der Zugriff darauf werden über das Adobe-System verwaltet. Das Konto kann nicht von einem Administrator gesteuert werden.

- Enterprise ID: Das Unternehmen hat dieses Konto erstellt und ist dessen Eigentümer. Das Konto und der Zugriff darauf werden über das Adobe-System verwaltet. Das Konto kann von einem Administrator gesteuert werden.

- Federated ID: Das Unternehmen hat dieses Konto erstellt und ist dessen Eigentümer. Das Konto wird zum Teil über das Adobe-System verwaltet, der Zugriff (Kennwort und Anmeldename) erfolgt allerdings über das Unternehmen und wird von diesem gesteuert.

Enterprise IDs und Federated IDs müssen sich in einer Domäne befinden, die das Unternehmen beansprucht hat und deren Eigentümer es ist. Die Domäne muss für die Adobe-Organisation mit der Adobe Admin Console eingerichtet werden.

Wenn Sie über mehr als eine Adobe-Organisation verfügen, sollten Sie wissen, welche Domänen und Benutzer welcher Organisation angehören und wie diese Gruppen mit den Konten, die im Verzeichnissystem vorhanden sind, in Zusammenhang stehen. Vielleicht haben Sie eine einfache Konfiguration mit einem einzigen Verzeichnissystem und einer Adobe-Organisation. Wenn von beiden mehrere vorhanden sind, sollten Sie eine Karte anfertigen, die zeigt, welche Systeme Benutzerinformationen an welche Adobe-Organisationen senden. Möglicherweise arbeiten Sie mit mehreren Instanzen der Benutzersynchronisation, von denen jede nur für eine bestimmte Adobe-Organisation verwendet wird.

Mit der Benutzersynchronisation können Sie Benutzer erstellen und aktualisieren sowie Lizenzen verwalten. Für die Lizenzverwaltung ist die Benutzersynchronisation optional. Die entsprechenden Funktionen sind von anderen Funktionen der Benutzersynchronisation unabhängig. Über die Adobe Admin Console oder eine andere Applikation können Sie Lizenzen manuell verwalten.

Zum Löschen von Konten gibt es eine Reihe von Möglichkeiten. Sie können Adobe-Konten, wenn das entsprechende Unternehmenskonto entfernt wird, sofort löschen. Wenn Sie eine andere Vorgehensweise verwenden möchten, können die Adobe-Konten allerdings auch verfügbar bleiben, bis überprüft wird, ob Assets aus diesem Konto abgerufen werden müssen. Die Benutzersynchronisation kann diese und eine Reihe anderer Löschvorgänge ausführen.


## Die Benutzersynchronisation wird auf Ihren Systemen ausgeführt 
Sie benötigen einer Server, auf dem sie gehostet wird. Die Benutzersynchronisation ist eine Python-Open-Source-Applikation. Sie können ein vorkonfiguriertes Python-Paket verwenden oder einen eigenen Build erstellen.

## Voraussetzungen

----------

### Verzeichnissystem
Sie müssen sich mit Ihrem Verzeichnis und dem Zugriff auf das Verzeichnis auskennen.

Sie müssen wissen, welche Benutzer im Verzeichnis auch Adobe-Benutzer sind.

### Prozesse
Sie müssen einen Prozess ausführen können und überwachen lassen.

Sie müssen wissen, wie Produkte in Ihrem Unternehmen verwaltet werden (z. B. wer wie Zugriff erhält).

Sie müssen festlegen, ob Sie ausschließlich Benutzer oder Benutzer und Produktlizenzen verwalten.

Sie müssen entscheiden, wie Konten gelöscht werden sollen, wenn Benutzer aus dem Verzeichnis entfernt werden.

### Adobe-Umgebung
Sie benötigen eingehende Kenntnisse der verwendeten Adobe-Produkte.

Sie müssen wissen, welche Adobe-Organisationen eingerichtet wurden und welche Benutzer zu welchen Organisationen gehören.

Sie benötigen Administratorrechte für den Zugriff auf bestehende Adobe-Organisationen.

[Zurück zum Inhaltsverzeichnis](index.md) \|  [Nächster Abschnitt](layout_orgs.md)
