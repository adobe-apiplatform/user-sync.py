---
layout: default
lang: de
nav_link: Erweiterte Konfiguration
nav_level: 2
nav_order: 60
---


# Erweiterte Konfiguration

## In diesem Abschnitt
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Voriger Abschnitt](usage_scenarios.md)  \| [Nächster Abschnitt](deployment_best_practices.md)

---

Das Benutzer-Synchronisationstool benötigt zum Synchronisieren von Benutzerdaten in Umgebungen mit komplexeren Datenstrukturen eine erweiterte Konfiguration.

- Wenn Sie Ihre Adobe ID-Benutzer in Tabellen oder im Unternehmensverzeichnis verwalten, können Sie das Tool so konfigurieren, dass es sie nicht ignoriert.
- Wenn Ihr Unternehmen mehrere Adobe-Organisationen umfasst, können Sie das Tool so konfigurieren, dass Benutzer in Ihrer Organisation Gruppen hinzugefügt werden, die in anderen Organisationen definiert sind.
- Wenn zu den Daten Ihres Unternehmens benutzerdefinierte Attribute und Zuordnungen zählen, müssen Sie das Tool so konfigurieren, dass es in der Lage ist, diese Anpassungen zu erkennen.
- Wenn Anmeldungen basierend auf dem Benutzernamen (und nicht auf der E-Mail-Adresse) erfolgen sollen.
- Wenn einige Benutzerkonten außer mit dem Benutzer-Synchronisationstool manuell über die Adobe Admin Console verwaltet werden sollen

## Verwalten von Benutzern mit Adobe IDs

Es gibt eine Konfigurationsoption `exclude_identity_types` (im Abschnitt `adobe_users` der Hauptkonfigurationsdatei), die standardmäßig so festgelegt ist, dass Adobe ID-Benutzer ignoriert werden. Wenn das Benutzer-Synchronisationstool einige Benutzer vom Typ Adobe ID verwalten soll, müssen Sie diese Option in der Konfigurationsdatei deaktivieren, indem Sie den Eintrag `adobeID` unter `exclude_identity_types` entfernen.

Sie möchten wahrscheinlich einen separaten Synchronisationsauftrag speziell für diese Benutzer einrichten, möglicherweise unter Verwendung von CSV-Eingaben anstelle von Eingaben aus dem Unternehmensverzeichnis. Achten Sie in diesem Fall darauf, dass Sie diesen Synchronisationsauftrag so konfigurieren, dass Enterprise ID- und Federated ID-Benutzer ignoriert werden. Andernfalls werden diese mit hoher Wahrscheinlichkeit aus dem Verzeichnis entfernt!

Das Entfernen von Adobe ID-Benutzern über die Benutzersynchronisation hat möglicherweise nicht den gewünschten Effekt:

* Wenn Sie angeben, dass adobeID-Benutzer aus Ihrer Organisation entfernt werden sollen, müssen Sie sie erneut einladen
(und sie wieder akzeptieren), wenn Sie sie später wieder hinzufügen möchten.
* Systemadministratoren verwenden häufig Adobe IDs. Somit können beim Entfernen von Adobe ID-Benutzern versehentlich Systemadministratoren entfernt werden (u. a. auch Sie selbst).

Eine bessere Vorgehensweise beim Verwalten von Adobe ID-Benutzern besteht darin, sie einfach hinzuzufügen und ihre Gruppenmitgliedschaften zu verwalten, sie jedoch nie zu entfernen. Durch Verwalten von Gruppenmitgliedschaften können Sie ihre Berechtigungen entfernen, ohne dass es später einer erneuten Einladung bedarf, wenn Sie sie wieder aktivieren möchten.

Denken Sie daran, dass Adobe ID-Konten den Endbenutzern gehören und daher nicht gelöscht werden können. Wenn Sie eine Aktion „delete“ anwenden, ersetzt das Benutzer-Synchronisationstool die Aktion „delete“ durch eine Aktion „remove“.

Sie können bestimmte Adobe ID-Benutzer auch vor dem Entfernen durch die Benutzersynchronisation schützen, indem Sie die übrigen Konfigurationselemente zum Ausschließen verwenden. Weitere Informationen finden Sie im Abschnitt [Schützen bestimmter Konten vor Löschung durch die Benutzersynchronisation](#schützen-bestimmter-konten-vor-löschung-durch-die-benutzersynchronisation) weiter unten.

## Zugreifen auf Benutzer in anderen Organisationen

Ein großes Unternehmen kann mehrere Adobe-Organisationen umfassen. Das Unternehmen Geometrixx hat beispielsweise mehrere Abteilungen, von denen jede über eine eigene eindeutige Organisations-ID und eine eigene Admin Console verfügt.

Wenn ein Unternehmen Enterprise IDs oder Federated IDs verwendet, muss eine Domäne beansprucht werden. In einem kleineren Unternehmen würde die einzige Organisation die Domäne **geometrixx.com** beanspruchen. Eine Domäne kann jedoch nur von einer einzigen Organisation beansprucht werden. Wenn mehrere Organisationen demselben Unternehmen gehören, sollen u. U. einige davon oder alle Benutzer einschließen, die der Unternehmensdomäne angehören.

In diesem Fall sollte der Systemadministrator diese Domäne zur Identifizierung für jede der Abteilungen beanspruchen. Es ist in der Adobe Admin Console nicht möglich, dass mehrere Abteilungen dieselbe Domäne beanspruchen. Sobald eine Abteilung eine Domäne beansprucht hat, können andere Abteilungen jedoch Zugriff darauf anfordern. Die erste Abteilung, welche die Domäne beansprucht, ist der *Eigentümer* dieser Domäne. Diese Abteilung ist verantwortlich für die Genehmigung von Zugriffsanforderungen durch andere Abteilungen; diese können dann auf Benutzer in der Domäne zugreifen, ohne dass spezielle Konfigurationsanforderungen vorliegen.

Es ist keine spezielle Konfiguration erforderlich, um auf Benutzer in einer Domäne zuzugreifen, auf die Ihnen der Zugriff gewährt wurde. Wenn Sie jedoch Benutzer Benutzergruppen oder Produktkonfigurationen hinzufügen möchten, die in anderen Organisationen definiert sind, müssen Sie das Benutzer-Synchronisationstool für den Zugriff auf die betreffenden Organisationen konfigurieren. Das Tool muss in der Lage sein, die Anmeldeinformationen der Organisation zu finden, welche die Gruppen definiert. Zudem muss es erkennen können, dass die Gruppen einer externen Organisation gehören.


## Zugreifen auf Gruppen in anderen Organisationen

Zum Konfigurieren des Zugriffs auf Gruppen in anderen Organisationen müssen Sie Folgendes ausführen:

- Sie müssen zusätzliche UMAPI-Verbindungskonfigurationsdateien einschließen.
- Sie müssen dem Benutzer-Synchronisationstool mitteilen, wie auf diese Dateien zugegriffen werden soll.
- Sie müssen die Gruppen bestimmen, die in einer anderen Organisation definiert sind.

### 1. Einschließen zusätzlicher Konfigurationsdateien

Für jede zusätzliche Organisation, auf die Sie Zugriff benötigen, müssen Sie eine Konfigurationsdatei hinzufügen, in der die Zugriffsanmeldeinformationen für diese Organisation enthalten sind. Die Datei weist das gleiche Format wie die Datei „connector-umapi.yml“ auf. Auf jede zusätzliche Organisation wird mit einem Kurznamen verwiesen (der von Ihnen festgelegt wird). Sie können der Konfigurationsdatei mit den Anmeldeinformationen für den Zugriff auf die Organisation einen beliebigen Namen zuweisen. 

Angenommen, die zusätzliche Organisation heißt „department 37“. Die Konfigurationsdatei kann wie folgt benannt werden: 

`department37-config.yml`

### 2. Konfigurieren der Benutzersynchronisation für den Zugriff auf die zusätzlichen Dateien


Der Abschnitt `adobe-users` der Hauptkonfigurationsdatei muss Einträge enthalten, die auf diese Dateien verweisen und jeden Eintrag dem Kurznamen der Organisation zuordnen. Beispiel:

```YAML
adobe-users:
  connectors:
    umapi:
      - connector-umapi.yml
      - org1: org1-config.yml
      - org2: org2-config.yml
      - d37: department37-config.yml  # d37 ist der Kurzname für das obige Beispiel
```

Werden nicht qualifizierte Namen verwendet, müssen sich die Konfigurationsdateien im gleichen Ordner wie die Hauptkonfigurationsdatei befinden, in der auf sie verwiesen wird.

Beachten Sie, dass sie wie Ihre eigene Verbindungskonfigurationsdatei vertrauliche Informationen enthalten, die geschützt werden müssen.

### 3. Bestimmen extern definierter Gruppen

Wenn Sie Ihre Gruppenzuordnungen angeben, können Sie eine Unternehmensverzeichnisgruppe einer Adobe-Benutzergruppe oder -Produktkonfiguration zuordnen, die in einer anderen Organisation definiert ist.

Verwenden Sie dazu die Organisations-ID als Präfix für den Gruppennamen. Ordnen Sie sie mit „::“ zu. Beispiel:

```YAML
- directory_group: CCE Trustee Group
  adobe_groups:
    - "org1::Default Adobe Enterprise Support Program configuration"
    - "d37::Special Ops Group"
```

## Benutzerdefinierte Attribute und Zuordnungen

Sie können benutzerdefinierte Zuordnungen von Verzeichnisattributen oder anderen Werten zu den Feldern zum Festlegen und Aktualisieren von Benutzern definieren: Vorname, Nachname, E-Mail-Adresse, Benutzername, Land und Gruppenmitgliedschaft. Normalerweise werden diese Werte mithilfe von Standardattributen im Verzeichnis abgerufen. Sie können festlegen, dass andere Attribute verwendet werden sollen und angeben, wie Feldwerte berechnet werden sollen.

Dazu müssen Sie die Benutzersynchronisation so konfigurieren, dass alle nicht standardmäßigen Zuordnungen zwischen Ihren Benutzerdaten im Unternehmensverzeichnis und Adobe-Benutzerdaten erkannt werden. Beispiele für nicht standardmäßige Zuordnungen:

- Werte für Benutzername, Gruppen, Land oder E-Mail-Adresse, die in einem nicht standardmäßigen Attribut im Verzeichnis enthalten sind oder auf einem solchen basieren.
- Werte für Benutzername, Gruppen, Land oder E-Mail-Adresse, die anhand von Verzeichnisinformationen berechnet werden müssen.
- Zusätzliche Benutzergruppen oder Produkte, die in der Liste für ausgewählte oder alle Benutzer hinzugefügt oder entfernt werden müssen.

In der Konfigurationsdatei müssen alle benutzerdefinierten Attribute angegeben sein, die aus dem Verzeichnis abzurufen sind. Darüber hinaus müssen alle benutzerdefinierten Zuordnungen für diese Attribute sowie jegliche Berechnungen oder Aktionen angegeben sein, die zum Synchronisieren der Werte auszuführen sind. Die benutzerdefinierte Aktion wird mithilfe eines kleinen Python-Codeblocks festgelegt. Beispiele und Standardblöcke werden zur Verfügung gestellt.

Die Konfiguration für benutzerdefinierte Eigenschaften und Zuordnungen muss in einer separaten Konfigurationsdatei enthalten sein. Auf diese Datei wird im Abschnitt `directory_users` der Hauptkonfigurationsdatei verwiesen:

```
directory_users:
  extension: extenstions_config.yml  # Verweis auf die Datei mit Informationen zu benutzerdefinierten Zuordnungen
```

Die Behandlung der benutzerdefinierten Attribute erfolgt für jeden Benutzer; daher werden die Anpassungen im benutzerspezifischen Unterabschnitt des Abschnitts „extensions“ der Hauptkonfigurationsdatei des Benutzer-Synchronisationstools konfiguriert.

```
extensions:
  - context: per_user
    extended_attributes:
      - my-attribute-1
      - my-attribute-2
    extended_adobe_groups:
      - my-adobe-group-1
      - my-adobe-group-2
    after_mapping_hook: |
        pass # Benutzerdefinierten Python-Code hier einfügen
```

### Hinzufügen von benutzerdefinierten Attributen

In der Standardeinstellung erfasst die Benutzersynchronisation diese Standardattribute für jeden Benutzer im Verzeichnissystem des Unternehmens:

* `givenName` – wird für den Vornamen im Profil auf Adobe-Seite verwendet
* `sn` – wird für den Nachnamen im Profil auf Adobe-Seite verwendet
* `c` – wird für das Land auf Adobe-Seite (Ländercode aus zwei Buchstaben) verwendet
* `mail` – wird für die E-Mail-Adresse auf Adobe-Seite verwendet
* `user` – wird für den Benutzernamen auf Adobe-Seite verwendet (nur bei Angabe der Federated ID über den Benutzernamen)

Darüber hinaus erfasst die Benutzersynchronisation alle Attributnamen, die in Filtern in der LDAP-Connector-Konfiguration angegeben sind.

Sie können diesem Satz Attribute hinzufügen, indem Sie diese in einem `extended_attributes`-Schlüssel in der Hauptkonfigurationsdatei angeben, wie oben veranschaulicht. Der Wert des `extended_attributes`-Schlüssels ist eine YAML-Liste von Zeichenfolgen, wobei jede Zeichenfolge den Namen eines zu erfassenden Benutzerattributs angibt. Beispiel:

```YAML
extensions:
  - context: per-user
    extended_attributes:
    - bc
    - subco
```

In diesem Beispiel wird die Benutzersynchronisation angewiesen, die Attribute `bc` und `subco` für jeden geladenen Benutzer zu erfassen.

Wenn eines oder mehrere der angegebenen Attribute in den Verzeichnisinformationen für einen Benutzer fehlt, werden die betreffenden Attribute ignoriert. Bei Codeverweisen auf solche Attribute wird der Python-Wert `None` zurückgegeben; dieses Verhalten ist normal und stellt keinen Fehler dar.

### Hinzufügen von benutzerdefinierten Zuordnungen

Code für benutzerdefinierte Zuordnungen wird mithilfe eines Abschnitts „extensions“ in der Hauptkonfigurationsdatei („user sync“) konfiguriert. In „extensions“ steuert ein benutzerspezifischer Abschnitt benutzerdefinierten Code, der einmal pro Benutzer aufgerufen wird.

Der angegebene Code wird einmal pro Benutzer ausgeführt, nachdem Attribute und Gruppenmitgliedschaften aus dem Verzeichnissystem abgerufen wurden, jedoch bevor Aktionen für Adobe generiert wurden.

```YAML
extensions:
  - context: per-user
    extended_attributes:
      - bc
      - subco
    extended_adobe_groups:
      - Acrobat_Sunday_Special
      - Group for Test 011 TCP
    after_mapping_hook: |
      bc = source_attributes['bc']
      subco = source_attributes['subco']
      if bc is not None:
          target_attributes['country'] = bc[0:2]
          target_groups.add(bc)
      if subco is not None:
          target_groups.add(subco)
      else:
          target_groups.add('Undefined subco')
```

In diesem Beispiel werden die zwei benutzerdefinierten Attribute „bc“ und „subco“ für jeden aus dem Verzeichnis gelesenen Benutzer abgerufen. Der benutzerdefinierte Code verarbeitet die Daten für jeden Benutzer:

- Der Ländercode wird den ersten zwei Zeichen im Attribut „bc“ entnommen.

    Dies veranschaulicht, wie Sie mithilfe von benutzerdefinierten Attributen im Verzeichnis Werte für Standardfelder angeben können, die an Adobe gesendet werden.

- Der Benutzer wird Gruppen hinzugefügt, die aus dem Attribut „subco“ und dem Attribut „bc“ stammen (zusätzlich zu zugeordneten Gruppen aus der Gruppenzuordnung in der Konfigurationsdatei).

    Dies veranschaulicht, wie die Liste der Gruppen oder Produktkonfigurationen angepasst wird, um Benutzer in zusätzlichen Gruppen zu synchronisieren.

Wenn der Hook-Code auf Adobe-Gruppen oder -Produktkonfigurationen verweist, die noch nicht im Abschnitt **groups** der Hauptkonfigurationsdatei aufgeführt werden, werden diese unter **extended_adobe_groups** aufgelistet. Durch diese Liste wird effektiv der Satz der berücksichtigten Adobe-Gruppen erweitert. Weitere Informationen finden Sie unter [Erweiterte Gruppen- und Produktverwaltung](#erweiterte-gruppen--und-produktverwaltung).

### Variablen im Hook-Code

Der Code im `after_mapping_hook` ist vom Rest des Benutzer-Synchronisationstools isoliert, mit Ausnahme der folgenden Variablen.

#### Eingabewerte

Die folgenden Variablen können im benutzerdefinierten Code gelesen werden. Sie dürfen nicht geschrieben werden und Schreibvorgänge für diese Variablen haben keine Auswirkungen; sie sind vorhanden, um die Quellverzeichnisdaten für den Benutzer auszudrücken.

* `source_attributes`: Ein benutzerspezifisches Wörterbuch von Benutzerattributen, die aus dem Verzeichnissystem abgerufen werden. Da es sich um ein Python-Wörterbuch handelt, kann dieser Wert technisch gesehen geändert werden; Änderungen aus benutzerdefiniertem Code haben jedoch keine Auswirkungen.

* `source_groups`: Eine fixierte Gruppe von Verzeichnisgruppen, die für einen bestimmten Benutzer beim Durchlaufen der konfigurierten Verzeichnisgruppen gefunden wurden.

#### Eingabe-/Ausgabewerte

Die folgenden Variablen können vom benutzerdefinierten Code gelesen und geschrieben werden. Mit ihrer Eingabe werden Daten übermittelt, die durch Standardattribut- und Gruppenzuordnungsvorgänge für den aktuellen Benutzer im Verzeichnis festgelegt werden, und sie können so geschrieben werden, dass die für den entsprechenden Adobe-Benutzer durchgeführten Aktionen geändert werden.

* `target_attributes`: Ein Python-Wörterbuch, bei dessen Schlüsseln es sich um die Adobe-seitigen Argumente handelt, die festgelegt werden sollen. Wenn Sie einen Wert in diesem Wörterbuch ändern, wird der Wert geändert, der auf Adobe-Seite geschrieben wird. Da Adobe einen festen Satz von Attributen vordefiniert, hat das Hinzufügen eines Schlüssels zu diesem Wörterbuch keine Auswirkungen. Die Schlüssel in diesem Wörterbuch:
    * `firstName` – für AdobeID ignoriert, an anderer Stelle verwendet
    * `lastName` – für AdobeID ignoriert, an anderer Stelle verwendet
    * `email` – überall verwendet
    * `country` – für AdobeID ignoriert, an anderer Stelle verwendet
    * `username` – für alle ignoriert außer für Federated ID 
      [bei Konfiguration mit benutzernamenbasierter Anmeldung](https://helpx.adobe.com/de/enterprise/help/configure-sso.html)
    * `domain` – für alle ignoriert außer für Federated ID [bei Konfiguration mit benutzernamenbasierter Anmeldung](https://helpx.adobe.com/de/enterprise/help/configure-sso.html)
* `target_groups`: Ein Python-Satz für einzelne Benutzer, mit dem die Benutzergruppen und Produktkonfigurationen auf Adobe-Seite erfasst werden, denen der Benutzer hinzugefügt wird, wenn `process-groups` für die Synchronisation angegeben wird. Bei jedem Wert handelt es sich um einen Satz von Namen. Der Satz wird initialisiert, indem die Gruppenzuordnungen in der Hauptkonfigurationsdatei angewendet werden. Durch Änderungen an diesem Satz (hinzugefügte oder entfernte Elemente) wird der Satz von Gruppen geändert, die auf Adobe-Seite auf den Benutzer angewendet werden.
* `hook_storage`: Ein Python-Wörterbuch für einzelne Benutzer, das beim ersten Übergeben an benutzerdefinierten Code leer ist und über Aufrufe hinweg erhalten bleibt. Mit benutzerdefiniertem Code können alle privaten Daten in diesem Wörterbuch gespeichert werden. Wenn Sie externe Skript-Dateien verwenden, ist dies ein geeigneter Speicherort für die Code-Objekte, die durch Kompilieren dieser Dateien erstellt wurden.
* `logger`: Ein Objekt vom Typ `logging.logger`, dessen Ausgaben in der Konsole und/oder im Dateiprotokoll erfolgen (entsprechend der Protokollierungskonfiguration).

## Erweiterte Gruppen- und Produktverwaltung

Im Abschnitt **group** der Hauptkonfigurationsdatei wird die Zuordnung zwischen Verzeichnisgruppen und Adobe-Benutzergruppen und -Produktkonfigurationen definiert.

- Auf der Seite des Unternehmensverzeichnisses wählt das Benutzer-Synchronisationstool eine Gruppe von Benutzern in Ihrem Unternehmensverzeichnis auf Grundlage der LDAP-Abfrage, des Befehlszeilenparameters `users` und des Benutzerfilters aus und überprüft, ob diese Benutzer in einer der zugeordneten Gruppen aufgeführt sind. Wenn dies der Fall ist, bestimmt das Benutzer-Synchronisationstool anhand der Gruppenzuordnung die Adobe-Gruppen, denen diese Benutzer hinzugefügt werden sollen.
- Auf Adobe-Seite prüft das Benutzer-Synchronisationstool die Mitgliedschaft der zugeordneten Gruppen und Produktkonfigurationen. Wenn ein Benutzer in diesen Gruppen
_nicht_ in der Gruppe von ausgewählten Verzeichnisbenutzern vorhanden ist, entfernt das Benutzer-Synchronisationstool diesen Benutzer aus der Gruppe. Dies ist in der Regel das gewünschte Verhalten. Wenn z. B. ein Benutzer in der Adobe Photoshop-Produktkonfiguration ist und aus dem Unternehmensverzeichnis entfernt wird, erwarten Sie, dass er auch aus der Gruppe entfernt wird, damit ihm keine Lizenz mehr zugewiesen wird.

![Figure 4:Beispiel für Gruppenzuordnung](media/group-mapping.png)

Bei diesem Arbeitsablauf können Schwierigkeiten auftreten, wenn Sie den Synchronisationsvorgang in mehrere Durchläufe aufteilen möchten, um die Anzahl der jeweils abgefragten Verzeichnisbenutzer zu reduzieren. Sie können z. B. einen Durchlauf für Benutzer mit den Anfangsbuchstaben A–M und einen weiteren Durchlauf für Benutzer mit den Anfangsbuchstaben N–Z ausführen. Hierbei muss jeder Durchlauf auf andere Adobe-Benutzergruppen und -Produktkonfigurationen abzielen. Andernfalls würden bei dem Durchlauf für die Buchstaben A–M Benutzer aus zugeordneten Gruppen entfernt werden, die sich in der Gruppe für die Buchstaben N–Z befinden.

Erstellen Sie als Konfiguration für diesen Fall in der Admin Console Benutzergruppen für jede Teilgruppe von Benutzern (z. B. **photoshop_A_M** und
**photoshop_N_Z**)) und fügen Sie die einzelnen Benutzergruppen einzeln den Produktkonfigurationen hinzu (z. B.  **photoshop_config**). In der Konfiguration des Benutzer-Synchronisationstools ordnen Sie dann nur die Benutzergruppen, die nicht die Produktkonfigurationen zu. Jeder Synchronisationsauftrag bezieht sich auf eine Benutzergruppe in der jeweiligen Gruppenzuordnung. Dabei wird die Mitgliedschaft in der Benutzergruppe aktualisiert, wodurch indirekt auch die Mitgliedschaft in der Produktkonfiguration aktualisiert wird.

## Entfernen von Gruppenzuordnungen

Das Entfernen einer zugeordneten Gruppe kann verwirrend sein. Angenommen, die Verzeichnisgruppe `acrobat_users` wird der Adobe-Gruppe `Acrobat` zugeordnet. Sie möchten die Gruppe nicht mehr `Acrobat` zuordnen, daher entfernen Sie den Eintrag. Hierdurch bleiben alle Benutzer in der Gruppe `Acrobat`, weil `Acrobat` keine zugeordnete Gruppe mehr ist und von der Benutzersynchronisation nicht beachtet wird. Dies führt nicht dazu, dass alle Benutzer aus `Acrobat` entfernt werden, wie Sie möglicherweise erwartet haben.

Wenn die Benutzer auch aus der Gruppe `Acrobat` entfernt werden sollen, können Sie sie manuell über die Admin Console entfernen oder Sie belassen (zumindest vorübergehend) den Eintrag in der Gruppenzuordnung in der Konfigurationsdatei, ändern aber die Verzeichnisgruppe in einen Namen, der im Verzeichnis nicht vorhanden ist, z. B. `no_directory_group`. Beim nächsten Ausführen der Synchronisation wird festgestellt, dass die Adobe-Gruppe Benutzer enthält, die nicht in der Verzeichnisgruppe vorhanden sind, und sie werden alle verschoben. Sobald dies geschehen ist, können Sie die gesamte Zuordnung aus der Konfigurationsdatei entfernen.

## Arbeiten mit der benutzernamenbasierten Anmeldung

In der Adobe Admin Console können Sie eine Verbunddomäne konfigurieren, um Anmeldenamen auf Grundlage von E-Mail-Adressen oder die benutzernamenbasierte Anmeldung (d. h. nicht auf Grundlage der E-Mail-Adresse) zu verwenden. Die benutzernamenbasierte Anmeldung kann verwendet werden, wenn davon ausgegangen wird, dass sich die E-Mail-Adressen häufig ändern oder Ihre Organisation die Verwendung von E-Mail-Adressen für die Anmeldung nicht zulässt. Letztendlich hängt es von der allgemeinen Identitätsstrategie eines Unternehmens ab, ob die Anmeldung auf Grundlage von Benutzernamen oder E-Mail-Adressen erfolgt.

Zum Konfigurieren des Benutzer-Synchronisationstools für die Verwendung mit der Anmeldung mit Benutzernamen müssen Sie eine Reihe von zusätzlichen Konfigurationselementen festlegen.

In der Datei `connector-ldap.yml`:

- Legen Sie den Wert von `user_username_format` auf einen Wert wie {attrname} fest, wobei „attrname“ den Namen des Verzeichnisattributs angibt, dessen Wert für den Benutzernamen verwendet wird.
- Legen Sie den Wert von `user_domain_format` auf einen Wert wie {attrname} fest, wenn der Name der Domäne aus dem benannten Verzeichnisattribut stammt, oder auf einen festen Zeichenfolgenwert wie „Beispiel.de“.

Beim Verarbeiten des Verzeichnisses übernimmt das Benutzer-Synchronisationstool den Benutzernamen und die Domänenwerte aus diesen Feldern (oder Werten).

Bei den für diese Konfigurationselemente angegebenen Werten kann es sich um eine Kombination aus Zeichenfolgen und einem oder mehreren Attributnamen in geschweiften Klammern ({}) handeln. Die festen Zeichen werden mit dem Attributwert kombiniert, um daraus die Zeichenfolge zum Verarbeiten des Benutzers zu erstellen.

Bei Domänen, die die benutzernamenbasierte Anmeldung verwenden, sollte das Konfigurationselement `user_username_format` keine E-Mail-Adresse ergeben. Das Zeichen „@“ ist in Benutzernamen für die benutzernamenbasierte Anmeldung nicht zulässig.

Wenn Sie die benutzernamenbasierte Anmeldung verwenden, müssen Sie trotzdem eine eindeutige E-Mail-Adresse für jeden Benutzer angeben. Diese E-Mail-Adresse muss sich in einer Domäne befinden, die die Organisation beansprucht hat und besitzt. Das Benutzer-Synchronisationstool fügt keine Benutzer ohne E-Mail-Adresse zur Adobe-Organisation hinzu.

## Schützen bestimmter Konten vor Löschung durch die Benutzersynchronisation

Wenn Sie Konten über das Benutzer-Synchronisationstool erstellen und entfernen und manuell Konten erstellen möchten, benötigen Sie diese Funktion möglicherweise, damit das Benutzer-Synchronisationstool die manuell erstellten Konten nicht löscht.

Im Abschnitt `adobe_users` der Hauptkonfigurationsdatei können Sie die folgenden Einträge einschließen:

```YAML
adobe_users:
  exclude_adobe_groups: 
      - special_users       # Adobe-Konten in der benannten Gruppe werden durch die Benutzersynchronisation nicht entfernt oder geändert.
  exclude_users:
      - ".*@example.com"    # Benutzer, deren Name dem Muster entspricht, bleiben bei der Benutzersynchronisation erhalten. 
      - another@example.com # Es können mehrere Muster vorhanden sein.
  exclude_identity_types:
      - adobeID             # Hierdurch werden Konten, bei denen es sich um AdobeIds handelt, bei der Benutzersynchronisation nicht entfernt.
      - enterpriseID
      - federatedID         # Sie würden jedoch nicht alle Typen gleichzeitig angeben, da dann sämtliche Benutzer ausgeschlossen würden.  
```

Dies sind optionale Konfigurationselemente. Sie geben einzelne Konten oder Gruppen von Konten an und die angegebenen Konten sind vor dem Löschen durch die Benutzersynchronisation geschützt. Diese Konten können auf Grundlage der Einträge für Gruppenzuordnungen und mit der Befehlszeilenoption `--process-groups` weiterhin in Benutzergruppen oder Produktkonfigurationen hinzugefügt oder entfernt werden. 

Wenn Sie verhindern möchten, dass das Benutzer-Synchronisationstool diese Konten aus Gruppen entfernt, fügen Sie sie nur in Gruppen hinzu, die nicht mit dem Benutzer-Synchronisationstool gesteuert werden, d. h. in Gruppen, die nicht in der Gruppenzuordnung in der Konfigurationsdatei aufgeführt werden.

- `exclude_adobe_groups`: Bei den Werten dieses Konfigurationselements handelt es sich um eine Liste von Zeichenfolgen, die Adobe-Benutzergruppen oder Produktkonfigurationen angeben. Alle Benutzer in diesen Gruppen werden beibehalten und nie als „Nur Adobe“-Benutzer gelöscht.
- `exclude_users`: Bei den Werten dieses Konfigurationselements handelt es sich um eine Liste von Zeichenfolgen, die Muster darstellen, die Adobe-Benutzernamen entsprechen können. Alle übereinstimmenden Benutzer werden beibehalten und nie als „Nur Adobe“-Benutzer gelöscht.
- `exclude_identity_types`: Bei den Werten für dieses Konfigurationselement handelt es sich um eine Liste von Zeichenfolgen, die „adobeID“, „enterpriseID“, und „federatedID“ sein können. Dies führt dazu, dass alle Konten mit den aufgeführten Typen beibehalten und nie als „Nur Adobe“-Benutzer gelöscht werden.


## Arbeiten mit verschachtelten Verzeichnisgruppen in Active Directory

Hinweis: Die ursprünglich in diesem Abschnitt beschriebene Vorgehensweise funktionierte nicht ordnungsgemäß. Das Problem wird in einer späteren Version gelöst.

Wenn Ihre Verzeichnisgruppen verschachtelt strukturiert sind, sodass sich die Benutzer nicht in einer einfachen benannten Verzeichnisgruppe befinden, müssen Sie komplexere LDAP-Abfragen ausführen, um die Benutzer aufzulisten. Die verschachtelte Gruppenstruktur könnte z. B. wie folgt aussehen:


    All_Divisions
		Blue_Division
		       User1@example.com
		       User2@example.com
		Green_Division
		       User3@example.com
		       User4@example.com

Dies wird in einer späteren Version des Benutzer-Synchronisationstools als transparenter Vorgang unterstützt.


---

[Voriger Abschnitt](usage_scenarios.md)  \| [Nächster Abschnitt](deployment_best_practices.md)

