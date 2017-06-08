---
layout: default
lang: de
nav_link: Adobe.io-Integration
nav_level: 2
nav_order: 150
---

# Einrichten einer Adobe.io-Integration

[Voriger Abschnitt](decide_deletion_policy.md) \| [Zurück zum Inhaltsverzeichnis](index.md) \| [Nächster Abschnitt](identify_server.md)

Adobe hat ein sicheres Protokoll für die Integration von Applikationen mit Adobe-APIs entwickelt. Zu diesen Applikationen zählt auch das Benutzer-Synchronisationstool.

Die Schritte zur Einrichtung sind dokumentiert. Die vollständigen Informationen zum Einrichtungsvorgang für die Integration und zu den Anforderungen an Zertifikate finden Sie [hier](https://www.adobe.io/apis/cloudplatform/console/authentication.html).

– Sie müssen ein digitales Zertifikat erstellen oder erwerben, mit dem die Erstaufrufe der API signiert werden.
  - Das Zertifikat wird nicht für SSL oder sonstige Zwecke verwendet, sodass Vertrauensketten und Browser-Probleme keine Rolle spielen.
  - Sie können das Zertifikat mithilfe kostenloser Tools selbst erstellen oder käuflich erwerben (bzw. von der IT-Abteilung erhalten).
  - Sie benötigen eine Zertifikatsdatei mit dem öffentlichen Schlüssel und eine Datei mit dem privaten Schlüssel.
  - Sie sollten die Datei mit dem privaten Schlüssel wie ein Root-Kennwort schützen.
– Nach der Einrichtung werden alle benötigten Werte in der Adobe.io-Konsole angezeigt. Kopieren Sie diese in die Konfigurationsdatei für das Benutzer-Synchronisationstool.
– Außerdem müssen Sie die Datei mit dem privaten Schlüssel zur Konfiguration des Benutzer-Synchronisationstools hinzufügen.

&#9744; Besorgen oder erstellen Sie ein Zertifikat für digitale Signaturen. Siehe [Anleitung zum Erstellen von Zertifikaten](https://www.adobe.io/apis/cloudplatform/console/authentication/createcert.html).

&#9744; Verwenden Sie die [Adobe I/O-Konsole](https://console.adobe.io), um für jede Organisation, auf die Sie zugreifen möchten (in der Regel eine), den Benutzerverwaltungsdienst einer neuen oder bestehenden adobe.io-Integration hinzuzufügen. 

&#9744; Beachten Sie die Parameter für Ihre Integration (siehe bearbeitetes Beispiel unten). Diese werden in einem späteren Schritt verwendet.


![img](images/setup_adobe_io_data.png)


[Voriger Abschnitt](decide_deletion_policy.md) \| [Zurück zum Inhaltsverzeichnis](index.md) \| [Nächster Abschnitt](identify_server.md)
