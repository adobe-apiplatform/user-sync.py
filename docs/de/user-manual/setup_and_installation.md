---
layout: default
lang: de
nav_link: Setup und Installation
nav_level: 2
nav_order: 20
---

# Setup und Installation

## In diesem Abschnitt
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Voriger Abschnitt](index.md)  \| [Nächster Abschnitt](configuring_user_sync_tool.md)

---

Damit Sie das Benutzer-Synchronisationstool verwenden können, müssen in Ihrem Unternehmen Produktkonfigurationen in der Adobe Admin Console eingerichtet sein. Weitere Informationen hierzu finden Sie auf der [Hilfeseite zum Konfigurieren von Diensten](https://helpx.adobe.com/de/enterprise/help/configure-services.html#configure_services_for_group).

## Einrichten einer User Management API-Integration in Adobe I/O

Das Benutzer-Synchronisationstool ist ein Client der User Management API. Bevor Sie das Tool installieren, müssen Sie es als Client der API registrieren, indem Sie eine *Integration* im Adobe I/O-[Entwicklerportal](https://www.adobe.io/console/) hinzufügen. Sie müssen eine Unternehmensschlüssel-Integration hinzufügen, um die für den Zugriff auf das Adobe-Benutzerverwaltungssystem benötigten Anmeldeinformationen abzurufen.

Die zum Erstellen einer Integration erforderlichen Schritte werden ausführlich im Abschnitt [Übersicht über die Adobe I/O-Authentifizierung](https://www.adobe.io/apis/cloudplatform/console/authentication/gettingstarted.html) erläutert. Suchen Sie nach den Abschnitten zur Authentifizierung von Service-Konten. Hierfür müssen Sie ein integrationsspezifisches Zertifikat erstellen, das selbstsigniert sein kann. Wenn der Vorgang abgeschlossen ist, werden Ihnen ein **API Key**, eine  **Technical Account ID**, eine  **Organization ID** und ein  **Client Secret** zugewiesen, die das Tool verwendet. Außerdem erhalten Sie Zertifikatinformationen, um sicher mit der Admin Console kommunizieren zu können. Wenn Sie das Benutzer-Synchronisationstool installieren, müssen Sie diese Informationen als Konfigurationswerte angeben, die das Tool zum Zugriff auf die in Adobe gespeicherten Benutzerinformationen Ihrer Organisation benötigt.

Weitere Informationen finden Sie in der UMAPI-Dokumentation [hier](https://adobe-apiplatform.github.io/umapi-documentation) oder [hier ](https://www.adobe.io/apis/cloudplatform/usermanagement/docs/gettingstarted.html).

## Einrichten der Synchronisation für den Produktzugriff

Wenn Sie das Benutzer-Synchronisationstool zum Aktualisieren des Benutzerzugriffs auf Adobe-Produkte verwenden möchten, müssen Sie Gruppen in Ihrem Unternehmensverzeichnis erstellen, die den in der [Adobe I/O Console](https://www.adobe.io/console/) konfigurierten Benutzergruppen und Produktkonfigurationen entsprechen. Die Mitgliedschaft in einer Produktkonfiguration ermöglicht den Zugriff auf eine bestimmte Gruppe von Adobe-Produkten. Sie können den Zugriff für Benutzer oder definierte Benutzergruppen gewähren oder widerrufen, indem Sie sie in einer Produktkonfiguration hinzufügen bzw. entfernen.

Das Benutzer-Synchronisationstool kann Benutzern den Produktzugriff erlauben, indem Benutzer auf Grundlage ihrer Mitgliedschaften im Unternehmensverzeichnis zu Gruppen und Produktkonfigurationen hinzugefügt werden. Hierfür müssen die Gruppennamen korrekt zugewiesen werden und das Tool muss mit der Option zum Verarbeiten von Gruppenmitgliedschaften ausgeführt werden.

Wenn Sie das Tool auf diese Weise verwenden möchten, müssen Sie die Gruppen im Unternehmensverzeichnis den entsprechenden Adobe-Gruppen in der Hauptkonfigurationsdatei zuordnen. Hierfür müssen Sie sicherstellen, dass die Gruppen auf beiden Seiten vorhanden sind und dass Sie deren genaue Namen kennen.

### Überprüfen der Produkte und Produktkonfigurationen

Bevor Sie mit der Konfiguration des Benutzer-Synchronisationstools beginnen, müssen Sie wissen, welche Adobe-Produkte in Ihrem Unternehmen verwendet werden und welche Produktkonfigurationen und Benutzergruppen im Adobe-Benutzerverwaltungssystem definiert wurden. Weitere Informationen hierzu finden Sie auf der [Hilfeseite zum Konfigurieren von Unternehmensdiensten](https://helpx.adobe.com/de/enterprise/help/configure-services.html#configure_services_for_group).

Wenn noch keine Produktkonfigurationen vorhanden sind, können Sie sie in der Console erstellen. Sie benötigen Produktkonfigurationen mit entsprechenden Gruppen im Unternehmensverzeichnis, um das Benutzer-Synchronisationstool zum Aktualisieren der Informationen für Benutzerberechtigungen zu konfigurieren.

Die Namen der Produktkonfigurationen geben normalerweise den Typ des Produktzugriffs an, den die Benutzer benötigen, z. B. Vollzugriff oder Zugriff auf ein Einzelprodukt. Die genauen Namen können Sie ermitteln, indem Sie im Abschnitt „Produkte“ in der [Adobe Admin Console](https://www.adobe.io/console/) die für Ihr Unternehmen aktivierten Produkte aufrufen. Klicken Sie auf ein Produkt, um die Details der für dieses Produkt definierten Produktkonfigurationen anzuzeigen.

### Erstellen von zugehörigen Gruppen im Unternehmensverzeichnis

Wenn Sie Benutzergruppen und Produktkonfigurationen in der Adobe Admin Console definiert haben, müssen Sie entsprechende Gruppen in Ihrem Unternehmensverzeichnis erstellen und benennen. Für eine Verzeichnisgruppe für die Produktkonfiguration „Alle Applikationen“ können Sie z. B. den Namen „alle_apps“ verwenden.

Notieren Sie die Namen, die Sie für die Gruppen festlegen, sowie die Adobe-Gruppen, denen sie entsprechen. Mit diesen Informationen richten Sie eine Zuordnung in der Hauptkonfigurationsdatei für das Benutzer-Synchronisationstool ein. Weitere Informationen finden Sie weiter unten im Abschnitt [Konfigurieren der Gruppenzuordnung](configuring_user_sync_tool.md#konfigurieren-der-gruppenzuordnung).

Als Best Practice sollten Sie im Beschreibungsfeld der Produktkonfiguration oder Benutzergruppe darauf hinweisen, dass die Gruppe vom Benutzer-Synchronisationstool verwaltet wird und in der Admin Console nicht bearbeitet werden sollte.

![Figure 2: Übersicht zum Zuordnen von Gruppen](media/group-mapping.png)

## Installieren des Benutzer-Synchronisationstools

### Systemanforderungen

Das Benutzer-Synchronisationstool ist in Python implementiert, wobei Python-Version 2.7.9 oder höher erforderlich ist. Für jede Umgebung, in der Sie das Skript installieren, konfigurieren und ausführen möchten, müssen Sie sicherstellen, dass Python im Betriebssystem installiert wurde, bevor Sie mit dem nächsten Schritt fortfahren. Weitere Informationen finden Sie auf der [Python-Website](https://www.python.org/).

Das Tool wird mit dem Python-LDAP-Paket `pyldap` erstellt, das wiederum auf der OpenLDAP-Clientbibliothek basiert. Unter Windows Server, Apple OS X und vielen Varianten von Linux ist bereits ein OpenLDAP-Client installiert. Bei einigen UNIX-Betriebssystemen wie OpenBSD und FreeBSD ist dieser jedoch nicht in der Basisinstallation enthalten.

Vergewissern Sie sich, dass in Ihrer Umgebung ein OpenLDAP-Client installiert ist, bevor Sie das Skript ausführen. Wenn kein solcher Client vorhanden ist, müssen Sie ihn vor der Installation des Benutzer-Synchronisationstools installieren.

### Installation

Sie können das Benutzer-Synchronisationstool im [User Sync-Repository auf GitHub](https://github.com/adobe-apiplatform/user-sync.py) herunterladen. So installieren Sie das Tool:


1. Erstellen Sie einen Ordner auf Ihrem Server, in dem das Benutzer-Synchronisationstool installiert wird und in dem die Konfigurationsdateien gespeichert werden.


1. Klicken Sie auf den Link **Releases**, um das aktuelle Release zu suchen. Dieses umfasst Versionshinweise, Beispielkonfigurationsdateien und alle Build-Versionen (sowie Quellarchive).


2. Wählen Sie das komprimierte Paket für Ihre Plattform aus und laden Sie es herunter (Datei mit der Erweiterung `.tar.gz`). Es sind Builds für Windows, OS X, Centos und Ubuntu verfügbar. (Wenn Sie selbst einen Build aus dem Quellcode erstellen möchten, können Sie das Quellcodepaket für den Release herunterladen oder die aktuelle Quelle in der Master-Verzweigung verwenden.) In späteren Versionen des Benutzer-Synchronisationstools sind möglicherweise auch Python 3-Builds verfügbar.


3. Suchen Sie die ausführbare Python-Datei (`user-sync` oder `user-sync.pex` für Windows) und speichern Sie sie in Ihrem Ordner für das Benutzer-Synchronisationstool.


4. Laden Sie das Archiv `example-configurations.tar.gz` mit Beispielkonfigurationsdateien herunter. Im Archiv befindet sich ein Ordner für „config files – basic“. Die ersten 3 Dateien in diesem Ordner werden benötigt. Die anderen Dateien im Paket sind optional und/oder Alternativversionen für bestimmte Zwecke. Sie können diese Dateien in Ihren Stammordner kopieren und dann umbenennen und bearbeiten, um so eigene Konfigurationsdateien zu erstellen. (Weitere Informationen finden Sie im folgenden Abschnitt [Konfigurieren des Benutzer-Synchronisationstools](configuring_user_sync_tool.md#konfigurieren-des-benutzer-synchronisationstools).)


5. **Nur Windows:**

    Bevor Sie die ausführbare Datei „user-sync.pex“ unter Windows ausführen, müssen Sie möglicherweise ein Problem umgehen, das nur beim Ausführen von Python unter Windows auftritt:

    Das Windows-Betriebssystem erzwingt eine Längenbeschränkung für Dateipfade von 260 Zeichen. Beim Ausführen einer Python-PEX-Datei wird ein temporärer Speicherort zum Extrahieren des Paketinhalts erstellt. Wenn der Pfad zu diesem Speicherort länger als 260 Zeichen ist, wird das Skript nicht richtig ausgeführt.

    Standardmäßig befindet sich der temporäre Cache in Ihrem Basisordner, wodurch die Dateipfade die Längenbeschränkung überschreiten können. Erstellen Sie zum Umgehen dieses Problems unter Windows die Umgebungsvariable PEX\_ROOT und legen Sie den Pfad auf „C:\\pex“ fest. Das Betriebssystem verwendet diese Variable für den Cache-Speicherort, wodurch der Pfad die Längenbeschränkung von 260 Zeichen nicht überschreitet.


6. Führen Sie zum Ausführen des Benutzer-Synchronisationstools die ausführbare Python-Datei `user-sync` aus (oder führen Sie unter Windows `python user-sync.pex` aus).

### Hinweise zur Sicherheit

Da das Benutzer-Synchronisationstool sowohl im Unternehmen als auch bei Adobe auf vertrauliche Informationen zugreift, werden für die Verwendung eine Reihe von Dateien mit vertraulichen Daten benötigt. Achten Sie daher besonders darauf, diese Dateien vor nicht autorisiertem Zugriff zu schützen.

Ab Release 2.1 des Benutzer-Synchronisationstools können Sie Anmeldeinformationen im sicheren Anmeldeinformationsspeicher des Betriebssystems speichern, anstatt sie in Dateien zu speichern und diese Dateien dann zu sichern, oder umapi- und ldap-Konfigurationsdateien sicher mit einem von Ihnen definierten Verfahren speichern. Im Abschnitt [Sicherheitsempfehlungen](deployment_best_practices.md#sicherheitsempfehlungen) finden Sie weitere Informationen.

#### Konfigurationsdateien

Konfigurationsdateien müssen vertrauliche Informationen enthalten, z. B. Ihren Adobe User Management API-Schlüssel, den Pfad zum privaten Zertifikatschlüssel und die Anmeldeinformationen für Ihr Unternehmensverzeichnis (sofern vorhanden). Sie müssen die erforderlichen Schritte ausführen, um alle Konfigurationsdateien zu schützen und sicherzustellen, dass nur autorisierte Benutzer darauf zugreifen können. Das heißt: Gewähren Sie keinen Lesezugriff auf Dateien mit vertraulichen Informationen. Die einzige Ausnahme ist das Benutzerkonto, über das der Synchronisationsprozess ausgeführt wird.

Wenn Sie die Anmeldeinformationen im Betriebssystem speichern, erstellen Sie die gleichen Konfigurationsdateien, speichern aber nicht die tatsächlichen Anmeldeinformationen, sondern Schlüssel-IDs, mit denen die Anmeldeinformationen abgerufen werden. Im Abschnitt [Sicherheitsempfehlungen](deployment_best_practices.md#sicherheitsempfehlungen) finden Sie weitere Informationen.

Wenn das Benutzer-Synchronisationstool auf das Unternehmensverzeichnis zugreift, muss es zum Lesen auf dem Verzeichnisserver mit einem Dienstkonto konfiguriert werden. Dieses Dienstkonto benötigt nur Lesezugriff und es wird empfohlen, dass es KEINEN Schreibzugriff erhält (damit ein Benutzer, der unautorisiert Zugang zu den Anmeldeinformationen erhält, keinen Schreibzugriff hat).

#### Zertifikatsdateien

Die Dateien, die den öffentlichen und den privaten Schlüssel enthalten, jedoch insbesondere den privaten Schlüssel, der vertrauliche Informationen enthält. Sie müssen den privaten Schlüssel sicher verwahren. Er kann weder wiederhergestellt noch ersetzt werden. Wenn Sie den Schlüssel verlieren oder er beschädigt wird, müssen Sie das entsprechende Zertifikat aus Ihrem Konto löschen. Gegebenenfalls müssen Sie ein neues Zertifikat erstellen und hochladen. Sie müssen diese Dateien mindestens ebenso sicher wie Kontonamen und Kennwörter schützen. Es wird empfohlen, die private Schlüsseldatei in einem Verwaltungssystem für Anmeldeinformationen zu speichern, im sicheren Speicher des Betriebssystems oder Dateisystemschutz anzuwenden, sodass nur befugte Benutzer darauf zugreifen können.

#### Protokolldateien

Die Protokollierung ist standardmäßig aktiviert und alle Transaktionen für die User Management API werden an der Konsole ausgegeben. Sie können das Tool auch so konfigurieren, dass in eine Protokolldatei geschrieben wird. Die während der Ausführung erstellten Dateien erhalten einen Datumsstempel und werden im Dateisystem in einen Ordner geschrieben, der in der Konfigurationsdatei angegeben ist.

Die User Management API behandelt die E-Mail-Adresse eines Benutzers als eindeutige Kennung. Jede Aktion wird zusammen mit der dem Benutzer zugeordneten E-Mail-Adresse in das Protokoll geschrieben. Wenn Sie angeben, dass Daten in Dateien protokolliert werden sollen, enthalten die betreffenden Dateien diese Informationen.

Das Benutzer-Synchronisationstool bietet keine Steuerung und Verwaltung der Protokollaufbewahrung. Jeden Tag wird eine neue Protokolldatei begonnen. Wenn Sie angeben, dass Daten in Dateien protokolliert werden sollen, ergreifen Sie die nötigen Vorsichtmaßnahmen, um die Lebensdauer der Dateien und den Zugriff auf diese Dateien zu verwalten.

Wenn die Sicherheitsrichtlinie Ihres Unternehmens die Beibehaltung personenbezogener Daten auf der Festplatte nicht gestattet, konfigurieren Sie das Tool so, dass die Datenprotokollierung in Dateien deaktiviert ist. Das Tool gibt die Protokolltransaktionen weiterhin an der Konsole aus, wo die Daten während der Ausführung vorübergehend im Arbeitsspeicher gespeichert werden.

## Unterstützung für das Benutzer-Synchronisationstool

Adobe Enterprise-Kunden können über ihre normalen Supportkanäle Unterstützung für das Benutzer-Synchronisationstool erhalten.

Da es sich hierbei um ein Open-Source-Projekt handelt, können Sie Ihr Problem auch in GitHub vorbringen. Um den Debuggingprozess zu erleichtern, geben Sie in der Supportanfrage Ihre Plattform, die Befehlszeilenoptionen sowie alle Protokolldateien an, die während der Applikationsausführung generiert werden (sofern darin keine vertraulichen Informationen enthalten sind).


---

[Voriger Abschnitt](index.md)  \| [Nächster Abschnitt](configuring_user_sync_tool.md)
