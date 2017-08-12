---
layout: default
lang: de
nav_link: Best Practices für die Bereitstellung
nav_level: 2
nav_order: 70
---


# Best Practices für die Bereitstellung

## In diesem Abschnitt
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Voriger Abschnitt](advanced_configuration.md)

---

Das Benutzer-Synchronisationstool ist so konzipiert, dass es mit geringer oder ohne Benutzerinteraktion ausgeführt werden kann, sobald es ordnungsgemäß konfiguriert wurde. Sie können das Tool mit einem Planer in Ihrer Umgebung mit der gewünschten Häufigkeit ausführen.

- Die ersten Male kann die Ausführung des Benutzer-Synchronisationstools einige Zeit in Anspruch nehmen, abhängig davon, wie viele Benutzer in der Adobe Admin Console hinzugefügt werden müssen. Sie sollten das Tool die ersten Male manuell ausführen, bevor Sie die Ausführung als geplante Aufgabe einrichten, damit nicht mehrere Instanzen ausgeführt werden.
- Danach geht das Ausführen in der Regel schneller, da die Benutzerdaten nur bei Bedarf aktualisiert werden müssen. Die Häufigkeit, mit der Sie die Benutzersynchronisation ausführen möchten, ist davon abhängig, wie häufig Änderungen in Ihrem Unternehmensverzeichnis auftreten und wie schnell diese Änderungen auf Adobe-Seite übernommen werden sollen.
- Es wird nicht empfohlen, die Benutzersynchronisation häufiger als alle zwei Stunden auszuführen.

## Sicherheitsempfehlungen

Angesichts der Art der Daten in den Konfigurations- und Protokolldateien sollte ein Server für diese Aufgabe vorgesehen und entsprechend branchenspezifischen Best Practices gesichert werden. Es wird empfohlen, dass ein Server hinter der Unternehmensfirewall für diese Applikation bereitgestellt wird. Nur Benutzer mit entsprechenden Berechtigungen sollten in der Lage sein, eine Verbindung mit diesem Computer herzustellen. Sie sollten ein Systemdienstkonto mit eingeschränkten Berechtigungen erstellen, das speziell zum Ausführen der Applikation und Schreiben der Protokolldateien im System vorgesehen ist.

Die Applikation sendet GET- und POST-Anforderungen von der User Management API an einen HTTPS-Endpunkt. Dabei werden JSON-Daten zum Darstellen der Änderungen erstellt, die in die Admin Console geschrieben werden müssen, und die Daten werden im Textkörper einer POST-Anforderung an die User Management API angefügt.

Um die Verfügbarkeit der Back-End-Benutzeridentitätssysteme von Adobe zu schützen, legt die User Management API Einschränkungen für den Clientzugriff auf die Daten fest. Es gelten Grenzwerte für die Anzahl der Aufrufe, die ein einzelner Client innerhalb eines bestimmten Zeitintervalls senden kann, und es gelten globale Grenzwerte für den Zugriff aller Clients innerhalb des angegebenen Zeitraums. Das Benutzer-Synchronisationstool implementiert Logik für Back-off und Wiederholung, damit das Skript nicht kontinuierlich die User Management API aufruft, wenn die Grenzwerte erreicht wurden. Es ist normal, dass Meldungen in der Konsole anzeigt werden, dass das Skript für eine kurze Zeit unterbrochen wird, bevor die Ausführung wiederholt wird.

Bei Version 2.1 des Benutzer-Synchronisationstools sind zwei zusätzliche Verfahren zum Schutz von Anmeldeinformationen verfügbar. Beim ersten Verfahren wird der Anmeldeinformationsspeicher des Betriebssystems verwendet, um die Konfigurationswerte für die Anmeldeinformationen zu speichern. Beim zweiten Verfahren wird mit einem Mechanismus, den Sie bereitstellen müssen, die gesamte Konfigurationsdatei, die alle erforderlichen Anmeldeinformationen enthält, für umapi und/oder ldap sicher gespeichert. Diese Verfahren werden in den nächsten beiden Abschnitten beschrieben.

### Speichern von Anmeldeinformationen im Speicher auf Betriebssystemebene

Um das Benutzer-Synchronisationstool so einzurichten, dass Anmeldeinformationen aus dem Python-Keyring-Anmeldeinformationsspeicher des Betriebssystems abgerufen werden, legen Sie die Dateien „connector-umapi.yml“ und „connector-ldap.yml“ wie folgt fest:

connector-umapi.yml

	server:
	
	enterprise:
	  org_id: your org id
	  secure_api_key_key: umapi_api_key
	  secure_client_secret_key: umapi_client_secret
	  tech_acct: your tech account@techacct.adobe.com
	  secure_priv_key_data_key: umapi_private_key_data

Beachten Sie die Änderung von `api_key`, `client_secret` und `priv_key_path` in `secure_api_key_key`, `secure_client_secret_key` bzw. `secure_priv_key_data_key`. Diese alternativen Konfigurationswerte geben die Schlüsselnamen an, nach denen in der Schlüsselkette (oder dem entsprechenden Dienst auf anderen Plattformen) gesucht werden soll, um die tatsächlichen Werte der Anmeldeinformationen abzurufen. In diesem Beispiel sind die Schlüsselnamen der Anmeldeinformationen `umapi_api_key`, `umapi_client_secret` und `umapi_private_key_data`.

Der Inhalt der privaten Schlüsseldatei wird im Anmeldeinformationsspeicher als Wert von `umapi_private_key_data` verwendet. Dies ist nicht auf Windows, sondern nur auf anderen Plattformen möglich. Unten sehen Sie, wie Sie auf Windows die Datei mit dem privaten Schlüssel sichern.

Die Anmeldeinformationen werden mit „org_id“ als Wert für den Benutzernamen und den Schlüsselnamen in der Konfigurationsdatei als Schlüsselnamen im sicheren Speicher nachgeschlagen.

Ab Version 2.1.1 des Benutzer-Synchronisationstools gibt es eine kleine Variante zu diesem Ansatz: dabei wird die private Schlüsseldatei mit RSA verschlüsselt, dem Standardverschlüsselungsverfahren für private Schlüssel (wird auch als PKCS#8-Format bezeichnet). Dieser Ansatz muss auf Windows verwendet werden, da der sichere Speicher von Windows keine Zeichenfolgen speichern kann, die länger als 512 Bytes sind, wodurch die Verwendung mit privaten Schlüsseln verhindert wird. Wenn Sie möchten, können Sie diesen Ansatz auch auf den anderen Plattformen verwenden.

Um den privaten Schlüssel in einem verschlüsselten Format zu speichern, gehen Sie folgendermaßen vor: Erstellen Sie zunächst eine verschlüsselte Version der privaten Schlüsseldatei. Wählen Sie eine Passphrase aus und verschlüsseln Sie die private Schlüsseldatei:

    openssl pkcs8 -in private.key -topk8 -v2 des3 -out private-encrypted.key

Auf Windows müssen Sie von Cygwin oder einem anderen Anbieter aus „openssl“ ausführen, denn in der Standard-Windows-Distribution ist es nicht enthalten.

Verwenden Sie als Nächstes die folgenden Konfigurationselemente in „connector-umapi.yml“. Durch die letzten beiden Elemente unten wird die Verschlüsselungs-Passphrase von dem sicheren Speicher mit den Anmeldeinformationen bezogen und auf die verschlüsselte Datei mit dem privaten Schlüssel verwiesen, nämlich:

	server:
	
	enterprise:
	  org_id: your org id
	  secure_api_key_key: umapi_api_key
	  secure_client_secret_key: umapi_client_secret
	  tech_acct: your tech account@techacct.adobe.com
	  secure_priv_key_pass_key: umapi_private_key_passphrase
	  priv_key_path: private-encrypted.key

Schließlich fügen Sie die Passphrase als Eintrag in den sicheren Speicher ein, mit dem Benutzernamen oder URL als Unternehmens-ID, dem Schlüsselnamen als `umapi_private_key_passphrase`, die dem Eintrag für `secure_priv_key_pass_key` in der Konfigurationsdatei entspricht, und dem Wert als Passphrase. (Sie können den verschlüsselten privaten Schlüssel auch innerhalb einfügen, indem Sie die Daten in der Datei connector-umapi.yml unter dem Schlüssel `priv_key_data` anstelle von `priv_key_path` platzieren.)

Hier endet die Beschreibung für die Variante, bei der die private RSA-Verschlüsselung verwendet wird.

connector-ldap.yml

	username: "Ihr LDAP-Konto-Benutzername"
	secure_password_key: ldap_password 
	host: "ldap://LDAP-Servername"
	base_dn: "DC=Domänenname,DC=com"

Das LDAP-Zugriffskennwort wird anhand des angegebenen Schlüsselnamens gesucht
(`ldap_password` in diesem Beispiel), wobei der Benutzername der angegebene Benutzername-Konfigurationswert ist.

Anmeldeinformationen werden im sicheren Speicher des zugrunde liegenden Betriebssystems gespeichert. Das konkrete Speichersystem hängt vom Betriebssystem ab.

| OS | Anmeldeinformationsspeicher |
|------------|--------------|
| Windows | Windows-Tresor für Anmeldeinformationen |
| Mac OS X | Schlüsselbund |
| Linux | Freedesktop Secret Service oder KWallet |
{: .bordertablestyle }

Unter Linux wird die Applikation für sicheren Speicher vom Betriebssystemanbieter installiert und konfiguriert.

Die Anmeldeinformationen werden dem sicheren Speicher des Betriebssystems hinzugefügt und ihnen werden der Benutzername und die Anmeldeinformations-ID zugewiesen, mit denen Sie die Anmeldeinformationen angeben. Bei UMAPI-Anmeldeinformationen entspricht der Benutzername der Organisations-ID. Für das LDAP-Kennwort entspricht der Benutzername dem LDAP-Benutzernamen. Sie können für die jeweiligen Anmeldeinformationen eine beliebige ID auswählen. Die Angabe im Anmeldeinformationsspeicher und der in der Konfigurationsdatei verwendete Name müssen übereinstimmen. Vorgeschlagene Werte für die Schlüsselnamen können Sie den obigen Beispielen entnehmen.


### Speichern von Anmeldeinformationsdateien in externen Verwaltungssystemen

Als Alternative zum Speichern von Anmeldeinformationen im lokalen Anmeldeinformationsspeicher kann das Benutzer-Synchronisationstool mit einem anderen System oder Verschlüsselungsmechanismus integriert werden. Zur Unterstützung solcher Integrationen ist es möglich, die gesamten Konfigurationsdateien für UMAPI und LDAP extern in anderen Systemen oder Formaten zu speichern.

Dazu wird in der Hauptkonfigurationsdatei des Benutzer-Synchronisationstools ein auszuführender Befehl angegeben, dessen Ausgabe als Inhalt der UMAPI- oder LDAP-Konfigurationsdatei verwendet wird. Sie müssen den Befehl angeben, der die Konfigurationsinformationen abruft und im YAML-Format an die Standardausgabe sendet; diese entsprechen dem Inhalt der Konfigurationsdatei.

Richten Sie dies anhand der folgenden Elemente in der Hauptkonfigurationsdatei ein.


user-sync-config.yml (Abbildung zeigt nur einen Teil der Datei)

	adobe_users:
	   connectors:
	      # umapi: connector-umapi.yml   # Verwenden Sie anstelle dieses Dateiverweises Folgendes:
	      umapi: $(read_umapi_config_from_s3)
	
	directory_users:
	   connectors:
	      # ldap: connector-ldap.yml # Verwenden Sie anstelle dieses Dateiverweises Folgendes:
	      ldap: $(read_ldap_config_from_server)
 
Das allgemeine Format für Verweise auf externe Befehle lautet wie folgt:

	$(command args)

In den obigen Beispielen wird angenommen, dass Sie einen Befehl mit dem Namen `read_umapi_config_from_s3` und `read_ldap_config_from_server` angegeben haben.

Das Benutzer-Synchronisationstool startet eine Eingabeaufforderung, an der der Befehl ausgeführt wird. Die Standardausgabe des Befehls wird erfasst und diese Ausgabe wird als UMAPI- bzw. LDAP-Konfigurationsdatei verwendet.

Der Befehl wird mit einem Arbeitsverzeichnis ausgeführt, welches dem Verzeichnis mit der Konfigurationsdatei entspricht.

Wird der Befehl nicht ordnungsgemäß beendet, wird die Benutzersynchronisation mit einer Fehlermeldung abgebrochen.

Der Befehl kann auf ein neues oder vorhandenes Programm oder Skript verweisen.

Hinweis: Wenn Sie dieses Verfahren für die Datei „connector-umapi.yml“ verwenden, empfiehlt es sich, die Daten zum privaten Schlüssel in „connector-umapi-yml“ mit dem Schlüssel „priv_key_data“ und dem Wert für den privaten Schlüssel direkt einzubetten. Wenn Sie den „priv_key_path“ und den Namen der Datei mit dem privaten Schlüssel verwenden, müssen Sie außerdem den privaten Schlüssel an einem sicheren Speicherort speichern und einen Befehl zum Abrufen im Dateiverweis angeben.

## Beispiele für geplante Vorgänge

Sie können mithilfe eines Planers in Ihrem Betriebssystem festlegen, dass das Benutzer-Synchronisationstool in regelmäßigen Abständen je nach den Anforderungen im Unternehmen ausgeführt wird. In diesen Beispielen wird veranschaulicht, wie Sie die Planer von Unix und Windows konfigurieren können.

Es empfiehlt sich, eine Befehlsdatei einzurichten, die das Benutzer-Synchronisationstool mit bestimmten Parametern ausführt und anschließend eine Protokollübersicht extrahiert, die an die Verantwortlichen für die Überwachung des Synchronisationsprozesses versendet wird. Diese Beispiele funktionieren am besten, wenn die Protokollebene der Konsole auf INFO festgelegt ist.

```YAML
logging:
  console_log_level: info
```

### Ausführen mit Protokollanalyse unter Windows

Im folgenden Beispiel wird das Einrichten einer Batchdatei `run_sync.bat` unter Windows veranschaulicht.

```sh
python C:\\...\\user-sync.pex --users file users-file.csv --process-groups | findstr /I "WARNING ERROR CRITICAL ---- ==== Number" > temp.file.txt
rem email the contents of temp.file.txt to the user sync administration
sendmail -s “Adobe User Sync Report for today” UserSyncAdmins@example.com < temp.file.txt
```

*HINWEIS*: In diesem Beispiel wird zwar die Verwendung von `sendmail` dargestellt, es gibt jedoch kein standardmäßiges E-Mail-Befehlszeilentool unter Windows. Es sind verschiedene Tools erhältlich.

### Ausführen mit Protokollanalyse auf Unix-Plattformen

Im folgenden Beispiel wird das Einrichten der Eingabeaufforderungsdatei `run_sync.sh` unter Linux oder Mac OS X veranschaulicht:

```sh
user-sync --users file users-file.csv --process-groups | grep "CRITICAL\|WARNING\|ERROR\|=====\|-----\|number of\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” UserSyncAdmins@example.com
```

### Planen eines Benutzer-Synchronisationsvorgangs

#### Cron

Durch diesen Eintrag in der Unix-Crontab wird das Benutzer-Synchronisationstool täglich um 04:00 Uhr ausgeführt:

```text
0 4 * * * /path/to/run_sync.sh
```

Cron kann auch so eingerichtet werden, dass Ergebnisse per E-Mail an einen bestimmten Benutzer oder Verteiler versendet werden. Weitere Einzelheiten können Sie der Cron-Dokumentation für Ihr System entnehmen.

#### Windows-Aufgabenplanung

Dieser Befehl nutzt die Aufgabenplanung von Windows, um das Benutzer-Synchronisationstool täglich um 16:00 Uhr auszuführen:

```text
schtasks /create /tn "Adobe User Sync" /tr C:\path\to\run_sync.bat /sc DAILY /st 16:00
```

Einzelheiten können Sie der Dokumentation zur Windows-Aufgabenplanung (`help schtasks`) entnehmen.

Geplante Tasks können unter Windows auch über eine Benutzeroberfläche verwaltet werden. Sie können die Aufgabenplanung in der Systemsteuerung von Windows aufrufen.

---

[Voriger Abschnitt](advanced_configuration.md)
