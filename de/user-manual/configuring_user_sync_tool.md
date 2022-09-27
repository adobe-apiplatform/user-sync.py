---
layout: default
lang: de
title: Konfigurieren der Benutzersynchronisation
nav_link: Konfigurieren der Benutzersynchronisation
nav_level: 2
nav_order: 30
parent: user-manual
page_id: configuration
---

# Konfigurieren des Benutzer-Synchronisationstools

## In diesem Abschnitt
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Voriger Abschnitt](setup_and_installation.md)  \| [Nächster Abschnitt](command_parameters.md)

---

Die Ausführung des Benutzer-Synchronisationstools wird durch eine Reihe von Konfigurationsdateien mit diesen Dateinamen gesteuert, die sich (in der Standardeinstellung) im gleichen Ordner wie die ausführbare Befehlszeilendatei befindet.

| Konfigurationsdatei | Zweck |
|:------|:---------|
| user-sync-config.yml | Erforderlich. Enthält Konfigurationsoptionen, welche die Zuordnung von Verzeichnisgruppen zu Konfigurationen und Benutzergruppen von Adobe-Produkten definieren und das Updateverhalten steuern. Zudem sind Verweise auf die anderen Konfigurationsdateien enthalten.|
| connector&#x2011;umapi.yml&nbsp;&nbsp; | Erforderlich. Enthält Anmeldeinformationen und Zugriffsinformationen für den Zugriff auf die Adobe User Management API. |
| connector-ldap.yml | Erforderlich. Enthält Anmeldeinformationen und Zugriffsinformationen für den Zugriff auf das Unternehmensverzeichnis. |
{: .bordertablestyle }

Wenn Sie den Zugriff auf Adobe-Gruppen in anderen Organisationen einrichten müssen, die Ihnen Zugriff gewährt haben, können Sie weitere Konfigurationsdateien einschließen. Weitere Informationen finden Sie weiter unten in den [Anweisungen für die erweiterte Konfiguration](advanced_configuration.md#zugreifen-auf-gruppen-in-anderen-organisationen).

## Einrichten der Konfigurationsdateien

Beispiele für die drei erforderlichen Dateien finden Sie im Ordner `config files - basic` im Versionsartefakt `example-configurations.tar.gz`:

```text
1 user-sync-config.yml
2 connector-umapi.yml
3 connector-ldap.yml
```

Um eine eigene Konfiguration zu erstellen, kopieren Sie die Beispieldateien in den Stammordner des Benutzer-Synchronisationstools und benennen Sie sie um (Entfernen der vorangestellten Zahl). Passen Sie die kopierten Konfigurationsdateien in einem Nur-Text-Editor für Ihre Umgebung und Ihr Verwendungsmodell an. Die Beispiele enthalten Kommentare, in denen alle möglichen Konfigurationselemente angegeben werden. Sie können bei Elementen, die Sie verwenden möchten, die Kommentarzeichen entfernen.

Konfigurationsdateien liegen im [YAML-Format](http://yaml.org/spec/) vor und weisen das `yml`-Suffix auf. Beim Bearbeiten von YAML sind einige wichtige Regeln zu beachten:

- Die Abschnitte und die Hierarchie in der Datei beruhen auf Einrückungen. Sie müssen Einrückungen mit LEERZEICHEN vornehmen. Verwenden Sie keine Tabulatorzeichen.
- Mit Bindestrichen (-) wird eine Liste von Werten gebildet. Im Folgenden finden Sie ein Beispiel für die Definition der Liste „adobe\_groups“ mit zwei Elementen.

```YAML
adobe_groups:
  - Photoshop Users
  - Lightroom Users
```

Beachten Sie, dass dies verwirrend aussehen kann, wenn die Liste nur ein Element enthält. Beispiel:

```YAML
adobe_groups:
  - Photoshop Users
```

## Erstellen und Sichern von Verbindungskonfigurationsdateien

In den beiden Verbindungskonfigurationsdateien werden die Anmeldeinformationen gespeichert, mit denen das Benutzer-Synchronisationstool auf die Adobe Admin Console und das LDAP-Verzeichnis Ihres Unternehmens zugreift. Zum Isolieren der vertraulichen Informationen, die zum Verbinden der beiden Systeme erforderlich sind, sind alle tatsächlichen Details zu Anmeldeinformationen ausschließlich auf diese zwei Dateien beschränkt. **Sichern Sie sie ordnungsgemäß** entsprechend der Beschreibung im Abschnitt [Sicherheitsempfehlungen](deployment_best_practices.md#sicherheitsempfehlungen) in diesem Dokument.

Es gibt drei Verfahren zum Sichern von Anmeldeinformationen, die vom Benutzer-Synchronisationstool unterstützt werden.


1. Anmeldeinformationen können direkt in den Dateien „connector-umapi.yml“ und „connector-ldap.yml“ gespeichert werden und die Dateien werden über die Zugriffskontrolle des Betriebssystems geschützt.

2. Sie können Anmeldeinformationen im sicheren Speicher für Anmeldeinformationen des Betriebssystems platzieren und Sie verweisen aus den beiden Konfigurationsdateien darauf.

3. Die beiden Dateien können in ihrer Gesamtheit sicher gespeichert oder verschlüsselt werden und aus der Hauptkonfigurationsdatei wird auf ein Programm verwiesen, das ihren Inhalt zurückgibt.


Die Beispielkonfigurationsdateien enthalten Einträge, die jedes dieser Verfahren veranschaulichen. Sie behalten lediglich einen Satz von Konfigurationselementen und entfernen bzw. kommentieren die übrigen aus.

### Konfigurieren der Verbindung mit der Adobe Admin Console (UMAPI)

Wenn Sie Zugriff erhalten haben und eine Integration mit der Benutzerverwaltung im Adobe I/O-[Entwicklerportal](https://www.adobe.io/console/) einrichten, notieren Sie sich die Konfigurationselemente, die Sie erstellt haben oder die Ihrer Organisation zugewiesen wurden:

- Organisations-ID
- API-Schlüssel
- Geheimer Clientschlüssel
- ID des technischen Kontos
- Privates Zertifikat

Öffnen Sie Ihre Kopie der Datei „connector-umapi.yml“ in einem Nur-Text-Editor und geben Sie im Abschnitt „enterprise“ die folgenden Werte ein:

```YAML
enterprise:
  org_id: "Organisations-ID hier einfügen"
  api_key: "API-Schlüssel hier einfügen"
  client_secret: "Geheimen Clientschlüssel hier einfügen"
  tech_acct: "ID des technischen Kontos hier einfügen"
  priv_key_path: "Pfad zum privaten Zertifikat hier einfügen"
```

**Hinweis:** Die Datei mit dem privaten Schlüssel muss an dem in `priv_key_path` angegebenen Speicherort abgelegt sein und sie darf nur für das Benutzerkonto lesbar sein, unter dem das Tool ausgeführt wird.

In Version 2.1 oder höher des Benutzer-Synchronisationstools besteht die Möglichkeit, den privaten Schlüssel alternativ in einer separaten Datei zu speichern. Sie können den privaten Schlüssel auch direkt in der Konfigurationsdatei platzieren. Verwenden Sie nicht den Schlüssel `priv_key_path`, sondern `priv_key_data` wie folgt:

	  priv_key_data: |
	    -----BEGIN RSA PRIVATE KEY-----
	    MIIJKAIBAAKCAge85H76SDKJ8273HHSDKnnfhd88837aWwE2O2LGGz7jLyZWSscH
	    ...
	    Fz2i8y6qhmfhj48dhf84hf3fnGrFP2mX2Bil48BoIVc9tXlXFPstJe1bz8xpo=
	    -----END RSA PRIVATE KEY-----

Version 2.2 des Benutzer-Synchronisationstools verfügt auch über einige zusätzliche Parameter zur Steuerung von Verbindungstimeouts und Wiederholungen. Eigentlich sollte man diese niemals brauchen, aber in außergewöhnlichen Situation können Sie sie im Abschnitt `server` festlegen.

  server:
    timeout: 120
    retries: 3

`timeout` bestimmt die maximale Wartezeit in Sekunden, bis ein Aufruf abgeschlossen ist.
`retries` legt fest, wie oft ein Vorgang wiederholt wird, wenn er aus unspezifischen Gründen wie Serverfehler oder Timeout nicht erfolgreich war.

### Konfigurieren der Verbindung mit Ihrem Unternehmensverzeichnis

Öffnen Sie Ihre Kopie der Datei „connector-ldap.yml“ in einem Nur-Text-Editor und legen Sie diese Werte fest, um den Zugriff auf Ihr Unternehmensverzeichnissystem zu aktivieren:

```
username: "Benutzernamen-hier-einfügen"
password: "Kennwort-hier-einfügen"
host: "FQDN.des.Hosts"
base_dn: "Basis-DN.des.Verzeichnisses"
```

Wie Sie ab Version 2.1 des Benutzer-Synchronisationstools das Kennwort sicherer speichern, erfahren Sie unter [Hinweise zur Sicherheit](deployment_best_practices.md#sicherheitsempfehlungen).

## Konfigurationsoptionen

Die Hauptkonfigurationsdatei „user-sync-config.yml“ ist in verschiedene Hauptabschnitte unterteilt: **adobe_users**,  **directory_users**,
**limits** und  **logging**.

- Im Abschnitt **adobe_users** wird festgelegt, wie das Benutzer-Synchronisationstool über die User Management API eine Verbindung mit der Adobe Admin Console herstellt. Es muss auf die separate, sichere Konfigurationsdatei verweisen, in der die Anmeldeinformationen für den Zugriff gespeichert sind. Dies wird im Feld „umapi“ des Felds „connectors“ festgelegt.
    - Der Abschnitt „adobe_users“ kann zudem „exclude_identity_types“, „exclude_adobe_groups“ und „exclude_users“ enthalten, die den Bereich der Benutzer beschränken, welche von der Benutzersynchronisation betroffen sind. Dies wird ausführlicher im Abschnitt [Schützen bestimmter Konten vor Löschung durch die Benutzersynchronisation](advanced_configuration.md#schützen-bestimmter-konten-vor-löschung-durch-die-benutzersynchronisation) weiter unten beschrieben.
- Der Unterabschnitt **directory_users** enthält die zwei Unterabschnitte „connectors“ und „groups“:
    - Der Unterabschnitt **connectors** verweist auf die separate, sichere Konfigurationsdatei, in der die Anmeldeinformationen für den Zugriff für Ihr Unternehmensverzeichnis gespeichert sind.
    - Im Abschnitt **groups** wird die Zuordnung zwischen Ihren Verzeichnisgruppen und Konfigurationen und Benutzergruppen für Adobe-Produkte definiert.
    - **directory_users** kann auch Schlüssel enthalten, die den Standard-Ländercode und -Identitätstyp festlegen. Weitere Einzelheiten können Sie den Beispielkonfigurationsdateien entnehmen.
- Im Abschnitt **limits** wird der Wert von `max_adobe_only_users` festgelegt, der verhindert, dass das Benutzer-Synchronisationstool Adobe-Benutzerkonten aktualisiert oder löscht, wenn mehr Konten als die angegebene Anzahl von Konten vorhanden sind, die zwar in der Adobe-Organisation, jedoch nicht im Verzeichnis aufgeführt werden. Diese Einschränkung verhindert, dass bei einer falschen Konfiguration oder anderen auftretenden Fehlern eine große Anzahl von Konten entfernt wird. Dieses Element ist obligatorisch.
- Der Abschnitt **logging** gibt einen Prüfprotokollpfad an und steuert, wie viele Informationen in das Protokoll geschrieben werden.

### Konfigurieren von Verbindungsdateien

Die wichtigste Konfigurationsdatei des Benutzer-Synchronisationstools enthält lediglich die Namen der Verbindungskonfigurationsdateien mit den Verbindungsanmeldeinformationen. Dadurch werden die vertraulichen Informationen isoliert, sodass Sie die Dateien sichern und den Zugriff auf die Dateien beschränken können.

Geben Sie Verweise auf die Verbindungskonfigurationsdateien in den
Abschnitten **adobe_users** und  **directory_users** an:

```
adobe_users:
  connectors:
    umapi: connector-umapi.yml

directory_users:
  connectors:
    ldap: connector-ldap.yml
```

### Konfigurieren der Gruppenzuordnung

Bevor Sie Benutzergruppen und Berechtigungen synchronisieren können, müssen Sie Benutzergruppen und Produktkonfigurationen in der Adobe Admin Console sowie entsprechende Gruppen in Ihrem Unternehmensverzeichnis erstellen. Siehe dazu die Beschreibung weiter oben unter [Einrichten der Synchronisation für den Produktzugriff](setup_and_installation.md#einrichten-der-synchronisation-für-den-produktzugriff).

**HINWEIS:** Alle Gruppen müssen vorhanden sein und auf beiden Seiten die angegebenen Namen aufweisen. Das Benutzer-Synchronisationstool erstellt auf keiner Seite Gruppen; wenn eine benannte Gruppe nicht gefunden wird, protokolliert das Benutzer-Synchronisationstool einen Fehler.

Der Abschnitt **groups** unter  **directory_users** muss einen Eintrag für jede Unternehmensverzeichnisgruppe enthalten, der den Zugriff auf ein oder mehrere Adobe-Produkte darstellt. Für jeden Gruppeneintrag sind die Produktkonfigurationen aufzulisten, für welche Benutzern in der betreffenden Gruppe der Zugriff gewährt wird. Beispiel:

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - "Default Acrobat Pro DC configuration"
  - directory_group: Photoshop
    adobe_groups:
      - "Default Photoshop CC - 100 GB configuration"
      - "Default All Apps plan - 100 GB configuration"
```

Verzeichnisgruppen können entweder *Produktkonfigurationen* oder *Benutzergruppen* zugeordnet werden. Ein `adobe_groups`-Eintrag kann eine beliebige Art von Gruppe benennen.

Beispiel:

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - Default Acrobat Pro DC configuration
  - directory_group: Acrobat_Accounting
    adobe_groups:
      - Accounting_Department
```

### Konfigurieren von Einschränkungen

Benutzerkonten werden aus dem Adobe-System entfernt, wenn entsprechende Benutzer im Verzeichnis nicht vorhanden sind und das Tool mit einer dieser Optionen aufgerufen wird:

- `--adobe-only-user-action delete`
- `--adobe-only-user-action remove`
- `--adobe-only-user-action remove-adobe-groups`

Wenn Ihre Organisation im Unternehmensverzeichnis über eine große Anzahl von Benutzern verfügt und die Anzahl der während eines Synchronisationsvorgangs gelesenen Benutzer plötzlich klein ist, kann dies auf eine falsche Konfiguration oder einen aufgetretenen Fehler hinweisen. Der Wert von `max_adobe_only_users` ist ein Schwellenwert, der bewirkt, dass das Benutzer-Synchronisationstool die Löschung und Aktualisierung vorhandener Adobe-Konten aussetzt und einen Fehler meldet, wenn im Unternehmensverzeichnis sehr viel weniger Benutzer (gemäß Filtervorgang mit Abfrageparametern) als in der Adobe Admin Console vorhanden sind.

Vergrößern Sie diesen Wert, wenn Sie erwarten, dass die Anzahl der Benutzer um mehr als den aktuellen Wert sinkt.

Beispiel:

```YAML
limits:
  max_adobe_only_users: 200
```

Eine solche Konfiguration bewirkt, dass das Benutzer-Konfigurationstool prüft, ob mehr als 200 in Adobe vorhandene Benutzerkonten im Unternehmensverzeichnis (gemäß Filtervorgang) nicht gefunden werden können; wenn dies der Fall ist, werden keine vorhandenen Adobe-Konten aktualisiert und eine Fehlermeldung wird protokolliert.

###  Konfigurieren der Protokollierung

Protokolleinträge werden in die Konsole geschrieben, von der aus das Tool gestartet wurde, sowie optional in eine Protokolldatei. Bei jeder Ausführung der Benutzersynchronisation wird ein neuer Eintrag mit einem Datums-/Zeitstempel in das Protokoll geschrieben.

Im Abschnitt **logging** können Sie die Protokollierung in einer Datei aktivieren und deaktivieren; zudem können Sie dort die Ausführlichkeit der Informationen steuern, die in das Protokoll und die Konsolenausgabe geschrieben werden.

```YAML
logging:
  log_to_file: True | False
  file_log_directory: "path to log folder"
  file_log_level: debug | info | warning | error | critical
  console_log_level: debug | info | warning | error | critical
```

Mit dem Wert für „log_to_file“ wird die Protokollierung in einer Datei aktiviert bzw. deaktiviert. Protokollmeldungen werden unabhängig von der Einstellung für „log_to_file“ immer in die Konsole geschrieben.

Wenn die Protokollierung in einer Datei aktiviert ist, ist der Wert von „file_log_directory“ erforderlich. Damit wird der Ordner angegeben, in den die Protokolleinträge geschrieben werden sollen.

- Geben Sie einen absoluten Pfad oder einen relativen Pfad zum Ordner mit dieser Konfigurationsdatei an.
- Stellen Sie sicher, dass für die Datei und den Ordner die entsprechenden Lese-/Schreibberechtigungen festgelegt sind.

Mit Werten für die Protokollebene wird festgelegt, mit welcher Ausführlichkeit Informationen in die Protokolldatei oder die Konsole geschrieben werden.

- Bei der untersten Ebene („debug“) werden die meisten Informationen und bei der obersten Ebene („critical“) die wenigsten Informationen aufgezeichnet.
- Sie können für die Datei und für die Konsole unterschiedliche Werte für die Protokollierungsebene festlegen.

Protokolleinträge, die die Begriffe WARNING, ERROR oder CRITICAL (WARNUNG, FEHLER oder KRITISCH) enthalten, weisen neben dem Status eine Beschreibung auf. Beispiel:

> `2017-01-19 12:54:04 7516 WARNING
console.trustee.org1.action - Error requestID: action_5 code: `"error.user.not_found" message: "No valid users were found in the request"`

In diesem Beispiel wurde während der Ausführung eine Warnung am 19.01.2017 um 12:54:04 Uhr protokolliert. Eine Aktion verursachte einen Fehler mit dem Code „error.user.not_found“. Die zum Fehlercode gehörende Beschreibung ist ebenfalls angegeben.

Sie können mithilfe des requestID-Werts nach der genauen Anforderung suchen, die den gemeldeten Fehler verursacht hat. Wenn Sie beispielsweise nach „action_5“ suchen, werden die folgenden Details zurückgegeben:

> `2017-01-19 12:54:04 7516 INFO console.trustee.org1.action -
Added action: {"do":
\[{"add": {"product": \["default adobe enterprise support program configuration"\]}}\],
"requestID": "action_5", "user": "cceuser2@ensemble.ca"}`

Damit verfügen Sie über weitere Informationen zu der Aktion, welche die Warnmeldung ausgelöst hat. In diesem Fall hat das Benutzer-Synchronisationstool versucht, dem Benutzer „cceuser2@ensemble.ca“ die „default adobe enterprise support program configuration“ hinzuzufügen. Die Hinzufügeaktion ist fehlgeschlagen, weil der Benutzer nicht gefunden wurde.

## Beispielkonfigurationen

In diesen Beispielen werden die Konfigurationsdateistrukturen gezeigt und mögliche Konfigurationswerte veranschaulicht.

### user-sync-config.yml

```YAML
adobe_users:
  connectors:
    umapi: connector-umapi.yml
  exclude_identity_types:
    - adobeID

directory_users:
  user_identity_type: federatedID
  default_country_code: US
  connectors:
    ldap: connector-ldap.yml
  groups:
    - directory_group: Acrobat
      adobe_groups:
        - Default Acrobat Pro DC configuration
    - directory_group: Photoshop
      adobe_groups:
        - "Default Photoshop CC - 100 GB configuration"
        - "Default All Apps plan - 100 GB configuration"
        - "Default Adobe Document Cloud for enterprise configuration"
        - "Default Adobe Enterprise Support Program configuration"

limits:
  max_adobe_only_users: 200

logging:
  log_to_file: True
  file_log_directory: userSyncLog
  file_log_level: debug
  console_log_level: debug
```

### connector-ldap.yml

```YAML
username: "LDAP_username"
password: "LDAP_password"
host: "ldap://LDAP_ host"
base_dn: "base_DN"

group_filter_format: "(&(objectClass=posixGroup)(cn={group}))"
all_users_filter: "(&(objectClass=person)(objectClass=top))"
```

### connector-umapi.yml

```YAML
server:
  # In diesem Abschnitt werden die Standorte der Server beschrieben, die für die Verwaltung von Adobe-Benutzern verwendet werden. Standardwerte:
  # host: usermanagement.adobe.io
  # endpoint: /v2/usermanagement
  # ims_host: ims-na1.adobelogin.com
  # ims_endpoint_jwt: /ims/exchange/jwt

enterprise:
  org_id: "Unternehmens-ID hier einfügen"
  api_key: "API-Schlüssel hier einfügen"
  client_secret: "Geheimen Clientschlüssel hier einfügen"
  tech_acct: "ID des technischen Kontos hier einfügen"
  priv_key_path: "Pfad zum privaten Schlüssel hier einfügen"
  # priv_key_data: "tatsächliche Schlüsseldaten hier einfügen" # Dies ist eine Alternative zu priv_key_path
```

## Testen Ihrer Konfiguration

Stellen Sie mithilfe von Testfällen sicher, dass Ihre Konfiguration ordnungsgemäß funktioniert und dass die Produktkonfigurationen den Sicherheitsgruppen in Ihrem Unternehmensverzeichnis korrekt zugeordnet sind. Führen Sie das Tool zunächst im Testmodus aus (geben Sie dazu den -t-Parameter an), sodass Sie das Ergebnis überprüfen können, bevor Sie die Live-Ausführung starten.

Die folgenden Beispiele verwenden `--users all`, um Benutzer auszuwählen, aber mithilfe von `--users mapped` können Sie nur Benutzer auswählen, die in Verzeichnisgruppen in Ihrer Konfigurationsdatei aufgeführt sind und mithilfe von `--users file f.csv` können Sie eine kleinere Gruppe von Testbenutzern auswählen, die in einer Datei aufgeführt sind.

###  Erstellen von Benutzern


1. Erstellen Sie einen oder mehrere Testbenutzer im Unternehmensverzeichnis.


2. Fügen Sie Benutzer einem oder mehreren konfigurierten Verzeichnissen/Sicherheitsgruppen hinzu.


3. Führen Sie die Benutzersynchronisation im Testmodus aus. (`./user-sync -t --users all --process-groups --adobe-only-user-action exclude`)


3. Führen Sie die Benutzersynchronisation nicht im Testmodus aus. (`./user-sync --users all --process-groups --adobe-only-user-action exclude`)


4. Vergewissern Sie sich, dass Testbenutzer in der Adobe Admin Console erstellt wurden.

### Aktualisieren von Benutzern


1. Ändern Sie die Gruppenmitgliedschaft eines oder mehrerer Testbenutzer im Verzeichnis.


1. Führen Sie das Benutzer-Synchronisationstool aus. (`./user-sync --users all --process-groups --adobe-only-user-action exclude`)


2. Vergewissern Sie sich, dass Testbenutzer in der Adobe Admin Console aktualisiert wurden, sodass die Produktkonfiguration-Mitgliedschaft widergespiegelt wird.

###  Deaktivieren von Benutzern


1. Entfernen oder deaktivieren Sie einen oder mehrere vorhandene Testbenutzer in Ihrem Unternehmensverzeichnis.


2. Führen Sie das Benutzer-Synchronisationstool aus. (`./user-sync --users all --process-groups --adobe-only-user-action remove-adobe-groups`) Oft empfiehlt es sich, das Tool erst im Testmodus („-t“) auszuführen.


3. Vergewissern Sie sich, dass Benutzer aus konfigurierten Produktkonfigurationen in der Adobe Admin Console entfernt wurden.


4. Führen Sie die Benutzersynchronisation aus, um die Benutzer zu entfernen (`./user-sync -t --users all --process-groups --adobe-only-user-action delete`). Führen Sie das Tool anschließend ohne den -t-Parameter aus. Vorsicht: Vergewissern Sie sich, dass bei der Ausführung mit -t nur der gewünschte Benutzer entfernt wurde. Bei dieser Ausführung (ohne -t) werden Benutzer tatsächlich gelöscht.


5. Vergewissern Sie sich, dass die Benutzerkonten aus der Adobe Admin Console entfernt wurden.

---

[Voriger Abschnitt](setup_and_installation.md)  \| [Nächster Abschnitt](command_parameters.md)
