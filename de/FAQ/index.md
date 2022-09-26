---
layout: page
title: Häufige Fragen zur Benutzersynchronisation
advertise: Häufige Fragen
lang: de
nav_link: Häufige Fragen
nav_level: 1
nav_order: 500
parent: root
page_id: faq
---
### Inhaltsverzeichnis
{:."no_toc"}

* TOC Placeholder
{:toc}


### Was ist die Benutzersynchronisation?

Hierbei handelt es sich um ein Tool, mit dem Kunden Zuweisungen von Adobe-Benutzern und Berechtigungen unter Verwendung von Active Directory (oder anderen geprüften OpenLDAP-Verzeichnisdiensten) erstellen können. Die Adressaten sind Administratoren von IT-Identitäten (Unternehmensverzeichnis-/Systemadministratoren), die das Tool installieren und konfigurieren können. Das Open-Source-Tool ist anpassbar, sodass es von Entwicklern des Kunden auf die jeweiligen Anforderungen zugeschnitten werden kann. 

### Weshalb ist die Benutzersynchronisation wichtig?

Das mit beliebigen Clouds (CC, EC, DC) einsetzbare Benutzer-Synchronisationstool soll die Einführung einer noch größeren Anzahl von Benutzern in eine personengebundene Bereitstellung fördern und es ermöglichen, die Vorteile der Funktionen von Produkten und Diensten in der Admin Console umfassend zu nutzen.
 
### Wie funktioniert das?

Bei Ausführung des Benutzer-Synchronisationstools wird eine Liste der Benutzer aus dem Active Directory (oder einer anderen Datenquelle) der Organisation abgerufen und mit der Liste der Benutzer in der Admin Console verglichen. Anschließend wird die Adobe User Management API aufgerufen, sodass die Admin Console mit dem Verzeichnis der Organisation synchronisiert wird. Der Änderungsfluss ist komplett unilateral; in der Admin Console vorgenommene Änderungen werden nicht per Push an das Verzeichnis der Organisation übertragen.

Mithilfe des Tools kann der Systemadministrator Benutzergruppen im Verzeichnis des Kunden Produktkonfigurationen und Benutzergruppen in der Admin Console zuordnen.

Zum Einrichten des Benutzer-Synchronisationstools muss die Organisation eine Reihe von Anmeldeinformationen auf die gleiche Weise wie für die Verwendung der User Management API erstellen.
 
### Wo finde ich das Tool?

Das Benutzer-Synchronisationstool ist ein Open-Source-Werkzeug, das unter der MIT-Lizenz vertrieben und von Adobe gepflegt wird. Es ist [hier](https://github.com/adobe-apiplatform/user-sync.py/releases/latest) verfügbar.


### Kann die Benutzersynchronisation sowohl für lokale Server als auch für Azure Active Directory-Server ausgeführt werden?

Die Benutzersynchronisation unterstützt lokale Server und von Azure gehostete AD (Active Directory)-Server sowie alle sonstigen LDAP-Server. Die Ausführung aus einer lokalen Datei ist ebenfalls möglich.

### Wird AD als LDAP-Server behandelt?

Ja, der Zugriff auf AD erfolgt über das LDAP v3-Protokoll, das von AD uneingeschränkt unterstützt wird.

### Platziert die Benutzersynchronisation automatisch alle meine LDAP/AD-Benutzergruppen in der Adobe Admin Console?

Nein. In Fällen, in denen die Gruppen auf Unternehmensseite den gewünschten Produktzugriffskonfigurationen entsprechen, kann die Konfigurationsdatei des Benutzer-Synchronisationstools so eingerichtet werden, dass Benutzer Produktkonfigurationen oder Benutzergruppen gemäß ihrer Gruppenmitgliedschaft auf der Unternehmensseite zugeordnet werden. Benutzergruppen und Produktkonfigurationen müssen in der Adobe Admin Console manuell eingerichtet werden.

 
### Kann mithilfe der Benutzersynchronisation die Mitgliedschaft in Benutzergruppen verwaltet werden oder ist lediglich die Verwaltung von Produktkonfigurationen möglich?

Bei der Benutzersynchronisation können Sie Benutzergruppen oder Produktkonfigurationen in der Zuordnung aus Verzeichnisgruppen verwenden. Somit können Benutzer Benutzergruppen hinzugefügt bzw. aus Benutzergruppen entfernt werden und dasselbe gilt auch für Produktkonfigurationen. Sie können jedoch keine neuen Benutzergruppen oder Produktkonfigurationen erstellen; dies muss in der Admin Console erfolgen.

### Aus den Beispielen im Benutzerhandbuch wird ersichtlich, dass jede Verzeichnisgruppe genau einer Adobe-Gruppe zugeordnet wird; ist es möglich, eine AD-Gruppe mehreren Produktkonfigurationen zuzuordnen?

In den meisten Beispielen wird lediglich eine einzige Adobe-Benutzergruppe oder -Produktkonfiguration veranschaulicht, es ist jedoch eine 1:n-Zuordnung möglich. Listen Sie dazu einfach alle Benutzergruppen oder Produktkonfigurationen auf, jeweils eine pro Zeile und gemäß dem YML-Listenformat jeweils mit einem vorangestellten „-“ (und eingerückt auf die entsprechende Ebene).

### Kann die Drosselung des UMAPI-Servers die Ausführung der Benutzersynchronisation beeinträchtigen?

Nein, die Benutzersynchronisation behandelt Drosselung und Wiederholungsversuche. So kann die Drosselung möglicherweise den Benutzer-Synchronisations-Gesamtprozess verlangsamen. Es wird jedoch kein Problem durch die Drosselung verursacht und die Benutzersynchronisation schließt alle Vorgänge ordnungsgemäß ab.

Adobe-Systeme schützen sich selbst vor Überlastung, indem das Aufkommen eingehender Anforderungen verfolgt wird. Sollte dieses die Grenzwerte überschreiten, geben Anforderungen einen Header vom Typ „retry-after“ zurück, der angibt, wann die entsprechende Kapazität wieder verfügbar sein wird. Die Benutzersynchronisation berücksichtigt diese Header und wartet den angegebenen Zeitraum, bevor ein Neuversuch unternommen wird. Weitere Informationen, einschließlich von Codebeispielen, finden Sie in der [User Management API-Dokumentation](https://www.adobe.io/apis/cloudplatform/usermanagement/docs/gettingstarted.html).
 
## Besteht eine lokale Liste der erstellten/aktualisierten Benutzer (auf Benutzer-Synchronisations-Seite), um die Aufrufe von Adobe-Servern zu reduzieren?

Mit Ausnahme des folgenden Falls, fragt die Benutzersynchronisation stets die Adobe-Benutzerverwaltungssysteme ab, um bei Ausführung aktuelle Informationen abzurufen. Im Benutzer-Synchronisationstool ab der Version 2.2, gibt es eine Option, mit der – unabhängig vom aktuellen Benutzerstatus im Adobe-Benutzerverwaltungssystem – diese Abfrage verhindert werden kann und Updates per Push zu Adobe übertragen werden können. Wenn Sie feststellen können, welche Benutzer im lokalen Verzeichnis geändert wurden und sicher sind, dass auf Adobe-Seite keine anderen Benutzer geändert wurden, kann diese Vorgehensweise die Laufzeit (und somit Netzwerknutzung) Ihrer Synchronisationsprozesse verkürzen.
 
### Ist das Benutzer-Synchronisationstool auf Federated IDs beschränkt oder können beliebige Typen von IDs erstellt werden?

Die Benutzersynchronisation unterstützt alle ID-Typen (Adobe IDs, Federated IDs und Enterprise IDs).

### Einer Adobe-Organisation kann Zugriff auf Benutzer aus Domänen im Besitz anderer Organisationen gewährt werden. Kann die Benutzersynchronisation derartige Fälle verarbeiten?

Ja. Die Benutzersynchronisation kann die Benutzergruppenmitgliedschaft und den Produktzugriff für Benutzer sowohl in eigenen als auch in aufgerufenen Domänen abfragen und verwalten. Wie bei der Admin Console können jedoch von der Benutzersynchronisation Benutzerkonten ausschließlich in eigenen Domänen erstellt und aktualisiert werden, nicht jedoch in Domänen im Besitz anderer Organisationen. Benutzern aus solchen Domänen kann der Produktzugriff gewährt werden, sie können jedoch nicht bearbeitet oder gelöscht werden.

### Gibt es eine Aktualisierungsfunktion oder können Benutzer lediglich hinzugefügt/entfernt werden (nur für Federated IDs)?

Für alle Typen von IDs (Adobe, Enterprise und Federated) unterstützt das Benutzer-Synchronisationstool das Aktualisieren von Gruppenmitgliedschaften unter Kontrolle der Option --process-groups. Für Enterprise IDs und Federated IDs unterstützt das Benutzer-Synchronisationstool die Aktualisierung der Felder für Vorname, Nachname und E-Mail-Adresse unter Kontrolle der Option --update-user-inf. Wenn Aktualisierungen für das Länder-Feld in der Admin Console verfügbar werden, werden diese über die UMAPI und für Federated IDs verfügbar, deren „Einstellung für die Benutzeranmeldung“ gleich „Benutzername“ ist, und das Benutzer-Synchronisationstool unterstützt Aktualisierungen des Benutzernamens ebenso wie Aktualisierungen der anderen Felder.

### Ist das Benutzer-Synchronisationstool auf ein bestimmtes Betriebssystem ausgelegt?

Das Benutzer-Synchronisationstool ist ein Open-Source-Python-Projekt, das Benutzer für das gewünschte Betriebssystem erstellen können. Wir stellen Builds für die Plattformen Windows, OS X, Ubuntu und CentOS 7 bereit.

### Wurde dies unter Python 3.5 getestet?

Die Benutzersynchronisation wurde erfolgreich unter Python 3.x ausgeführt. Der Großteil unserer Verwendung und der Tests erfolgte jedoch für Python 2.7. Daher stellen Sie möglicherweise Probleme fest und wir stellen nur Builds für Python 2.7 bereit. Probleme (und mögliche Behebungen) können Sie jederzeit auf der Open-Source-Website unter https://github.com/adobe-apiplatform/user-sync.py melden.

### Wenn Änderungen in der API auftreten (z. B. ein neues Feld beim Erstellen von Benutzern), wie werden die Aktualisierungen auf das Benutzer-Synchronisationstool angewendet?

Das Benutzer-Synchronisationstool ist ein Open Source-Projekt. Benutzer können die neuesten Quellen nach Wahl herunterladen und erstellen. Adobe veröffentlicht regelmäßig neue Versionen mit Builds. Benutzer können über Git-Benachrichtigungen über diese auf dem Laufenden bleiben. Bei Einführung einer neuen Version muss vom Benutzer nur die einzelne PEX-Datei aktualisiert werden. Wenn Konfigurationsänderungen oder Änderungen an der Befehlszeile vorgenommen werden müssen, damit neue Funktionen unterstützt werden, gibt es Aktualisierungen in diesen Dateien, sodass ihre Vorteile genutzt werden können.

Beachten Sie zudem, dass das Benutzer-Synchronisationstool auf umapi-client aufbaut, dem einzigen Modul, das die API direkt erkennt. Bei Änderungen der API wird umapi-client stets aktualisiert, damit diese unterstützt werden. Sollten Änderungen der API eine Ausweitung der Funktionen des Benutzer-Synchronisationstools bewirken, kann die Benutzersynchronisation aktualisiert werden, um diese bereitzustellen.

### Muss für die Benutzersynchronisation in Bezug auf die Firewall des Computers, auf dem das Tool ausgeführt wird, ein Eintrag in die Positivliste eingefügt werden?

Im Allgemeinen ist dies nicht der Fall. Die Benutzersynchronisation stellt lediglich einen Netzwerkclient dar und akzeptiert keine eingehenden Verbindungen, daher sind die lokalen Firewallregeln des Computers für eingehende Verbindungen irrelevant.

Als Netzwerkclient erfordert die Benutzersynchronisation jedoch ausgehenden SSL-Zugriff (Port 443) über Firewalls des Kundennetzwerks, damit Verbindungen mit den Adobe-Servern hergestellt werden können. Zudem müssen Kundennetzwerke der Benutzersynchronisation (sofern derart konfiguriert) das Herstellen von Verbindungen mit dem LDAP/AD-Server des Kunden an dem Port erlauben, der in der Konfiguration des Benutzer-Synchronisationstools angegeben ist (in der Standardeinstellung Port 389).

### Stellt das Benutzer-Synchronisationstool einen Teil des Adobe-Angebots für E-VIP-Kunden dar?
 
Ja, alle Unternehmenskunden haben Zugriff auf die UMAPI und die Benutzersynchronisation, ungeachtet ihres Kaufprogramms (E-VIP, ETLA oder Enterprise Agreement).
 
### Wie steht es mit der Internationalisierung des Benutzer-Synchronisationstools? Ist es für die internationale Verwendung geeignet (d. h. wird zumindest die Eingabe von Doppelbyte-Zeichen unterstützt)?
 
Bei früheren Versionen des Benutzer-Synchronisationstools war die Unterstützung internationaler Zeichen fehlerhaft, wenngleich die Verarbeitung UTF-8-kodierter Datenquellen recht zuverlässig war. Seit Version 2.2 unterstützt das Benutzer-Synchronisationstool alle Unicode-Zeichensätze und kann Konfigurationsdateien und Ordner sowie Datenquellen aus Tabellenkalkulationsprogrammen mit beliebiger Zeichenkodierung verarbeiten (wobei als Standard von UTF-8 ausgegangen wird).

