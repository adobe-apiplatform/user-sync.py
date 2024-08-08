---
weight: 140
title: Server-Setup
type: docs
---

# Bestimmen und Einrichten des Servers für die Benutzersynchronisation

Die Benutzersynchronisation kann manuell ausgeführt werden. Die meisten Unternehmen verwenden allerdings Automatisierung, bei der die Benutzersynchronisation mehrmals täglich automatisch ausgeführt wird.

Dafür muss sie auf einem Server installiert und ausgeführt werden, für den folgende Voraussetzungen gelten:

  - Internetverbindung für Zugriff auf Adobe
  - Zugriff auf Verzeichnisdienste wie LDAP und AD
  - Geschützt und sicher (die Administrator-Anmeldeinformationen sind auf dem Server gespeichert oder abrufbar)
  - Unterbrechungsfreie und zuverlässige Verfügbarkeit
  - Funktionen für Backup und Wiederherstellung
  - Möglichkeit zum Senden von E-Mails, damit Berichte der Benutzersynchronisation an Administratoren gesendet werden können

Bestimmen Sie in Zusammenarbeit mit Ihrer IT-Abteilung einen Server, der diese Anforderungen erfüllt, und richten Sie den Zugriff darauf für sich ein.
Die Benutzersynchronisation unterstützt Unix, OS X und Windows.

Beschaffen Sie einen Server, der für die Ausführung der Benutzersynchronisation vorgesehen ist. Sie können die ursprüngliche Einrichtung und Tests mit der Benutzersynchronisation auch auf einem anderen Computer durchführen, z. B. einem Laptop- oder Desktop-Computer, sofern dieser die genannten Kriterien erfüllt.

Erstellen Sie eine Anmeldung auf diesem Computer mit den Berechtigungen, die zum Installieren und Ausführen der Benutzersynchronisation erforderlich sind. In der Regel genügt ein Konto ohne erhöhte Rechte.

