---
layout: default
lang: fr
nav_link: Configuration de User Sync
nav_level: 2
nav_order: 30
---

# Configuration de l’outil User Sync

## Dans cette section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Section précédente](setup_and_installation.md)  \| [Section suivante](command_parameters.md)

---

Le fonctionnement de l’outil User Sync est contrôlé par un ensemble de fichiers de configuration portant les noms ci-dessous et situés (par défaut) dans le même dossier que l’exécutable de ligne de commande.

| Fichier de configuration | Utilisation |
|:------|:---------|
| user-sync-config.yml | Obligatoire. Contient les options de configuration qui définissent le mappage des groupes d’annuaire aux configurations de produits et aux groupes d’utilisateurs Adobe, et qui contrôlent le comportement de mise à jour. Contient également des références aux autres fichiers de configuration.|
| connector&#x2011;umapi.yml&nbsp;&nbsp; | Obligatoire. Contient des identifiants de connexion et des informations d’accès pour appeler l’API Adobe User Management. |
| connector-ldap.yml | Obligatoire. Contient des identifiants de connexion et des informations d’accès pour accéder à l’annuaire d’entreprise. |
{: .bordertablestyle }

Si vous devez configurer l’accès aux groupes Adobe dans d’autres organisations qui vous y ont habilité, vous pouvez inclure des fichiers de configuration supplémentaires. Pour en savoir plus, reportez-vous à la section [Instructions de configuration avancée](advanced_configuration.md#instructions-de-configuration-avancée) ci-dessous.

## Paramétrage des fichiers de configuration

Des exemples des trois fichiers requis sont fournis dans le dossier `config files - basic`, au niveau de l’artefact de version `example-configurations.tar.gz` :

```text
1 user-sync-config.yml
2 connector-umapi.yml
3 connector-ldap.yml
```

Pour créer votre propre configuration, copiez les fichiers d’exemple dans votre dossier racine User Sync et renommez-les (de manière à supprimer le nombre initial). Utilisez un éditeur de texte brut afin de personnaliser les fichiers de configuration ainsi copiés en fonction de votre environnement et de votre modèle d’utilisation. Les exemples contiennent des commentaires indiquant tous les éléments de configuration possibles. Vous pouvez annuler la mise en commentaire des éléments que vous devez utiliser.

Les fichiers de configuration sont au [format YAML](http://yaml.org/spec/) et utilisent le suffixe `yml`. Lorsque vous modifiez du code YAML, n’oubliez pas certaines règles importantes :

- Les sections et la hiérarchie du fichier sont basées sur la mise en retrait. Vous devez utiliser des ESPACES pour la mise en retrait. N’utilisez pas de caractères TAB.
- Le tiret (-) est utilisé pour former une liste de valeurs. Par exemple, le code suivant définit une liste nommée « adobe\_groups » contenant deux éléments.

```YAML
adobe_groups:
  - Photoshop Users
  - Lightroom Users
```

Notez que cela peut prêter à confusion si la liste ne comprend qu’un seul élément. Par exemple :

```YAML
adobe_groups:
  - Photoshop Users
```

## Création et sécurisation des fichiers de configuration de connexion

Les deux fichiers de configuration de connexion stockent les identifiants de connexion qui donnent à User Sync accès au portail Adobe Admin Console ainsi qu’à votre annuaire d’entreprise LDAP. Afin d’isoler les informations sensibles nécessaires pour se connecter aux deux systèmes, tous les identifiants sont regroupés dans ces deux fichiers. **N’oubliez pas de les sécuriser correctement**, comme expliqué à la section [Recommandations de sécurité](deployment_best_practices.md#recommandations-de-sécurité) de ce document.

User Sync prend en charge trois techniques pour sécuriser les identifiants de connexion.


1. Les identifiants de connexion peuvent être placés directement dans les fichiers connector-umapi.yml et connector-ldap.yml, ainsi que dans les fichiers protégés par le contrôle d’accès du système d’exploitation.

2. Les identifiants de connexion peuvent être placés dans le référentiel sécurisé correspondant du système d’exploitation et référencés à partir des deux fichiers de configuration.

3. Les deux fichiers peuvent être intégralement stockés en toute sécurité ou chiffrés, et un programme qui renvoie leur contenu est référencé à partir du fichier de configuration principal.


Les exemples de fichiers de configuration comportent des entrées illustrant chacune de ces techniques. Vous ne devez conserver qu’un seul ensemble d’éléments de configuration et mettre en commentaire ou retirer les autres.

### Configuration de la connexion au portail Adobe Admin Console (UMAPI)

Une fois que vous avez obtenu les droits d’accès et mis en place une intégration User Management sur le [portail de développement](https://www.adobe.io/console/) d’Adobe O/I, prenez note des éléments de configuration suivants que vous avez créés ou qui ont été attribués à votre organisation :

- ID d’organisation
- Clé d’API
- Secret client
- ID de compte technique
- Certificat privé

Ouvrez votre copie du fichier connector-umapi.yml dans un éditeur de texte brut et saisissez ces valeurs dans la section « enterprise » :

```YAML
enterprise:
  org_id : indiquez ici l’ID d’organisation
  api_key : indiquez ici la clé d’API
  client_secret : indiquez ici le secret client
  tech_acct : indiquez ici l’ID de compte technique
  priv_key_path : indiquez ici le chemin d’accès au certificat privé
```

**Remarque :** Veillez à placer le fichier de clé privée à l’emplacement spécifié dans `priv_key_path`, et à ce qu’il soit lisible uniquement par le compte d’utilisateur qui exécute l’outil.

User Sync version 2.1 ou ultérieure propose une alternative au stockage de la clé privée dans un fichier distinct. Vous pouvez en effet placer la clé privée directement dans le fichier de configuration. Plutôt que d’utiliser la clé `priv_key_path`, utilisez `priv_key_data` comme suit :

	  priv_key_data: |
	    -----BEGIN RSA PRIVATE KEY-----
	    MIIJKAIBAAKCAge85H76SDKJ8273HHSDKnnfhd88837aWwE2O2LGGz7jLyZWSscH
	    ...
	    Fz2i8y6qhmfhj48dhf84hf3fnGrFP2mX2Bil48BoIVc9tXlXFPstJe1bz8xpo=
	    -----END RSA PRIVATE KEY-----

Dans User Sync version 2.2 ou ultérieure, des paramètres supplémentaires permettent de contrôler le délai d’attente de connexion et de nouvelle tentative. Ceux-ci ne devraient jamais être utilisés, sauf dans le cas d’une situation inhabituelle où vous pouvez les définir dans la section `server` :

  server:
    timeout: 120
    retries: 3

`timeout` définit le temps d’attente maximum, en secondes, pour qu’un appel soit terminé.
`retries` définit le nombre de tentatives d’une opération si elle échoue en raison d’un problème non spécifique tel que l’expiration d’un délai d’attente ou une erreur du serveur.

### Configuration de la connexion à votre annuaire d’entreprise

Ouvrez votre copie du fichier connector-ldap.yml dans un éditeur de texte brut et définissez ces valeurs pour permettre l’accès à votre système d’annuaire d’entreprise :

```
username: indiquez-le-nom-d-utilisateur-ici
password: indiquez-le-mot-de-passe-ici
host: FQDN.de.l’hôte
base_dn: base_dn.de.l’annuaire
```

Voir la section [Recommandations de sécurité](deployment_best_practices.md#recommandations-de-sécurité) pour plus de détails sur la façon de stocker le mot de passe avec plus de sécurité dans User Sync version 2.1 ou ultérieure.

## Options de configuration

Le fichier de configuration principal, user-sync-config.yml, est divisé en plusieurs sections principales : **adobe_users**,  **directory_users**,
**limits** et  **logging**.

- La section **adobe_users** indique comment l’outil User Sync se connecte à Adobe Admin Console par le biais de l’API User Management. Elle doit pointer vers le fichier de configuration sécurisé distinct qui stocke les identifiants d’accès. Cela est défini dans le champ umapi du champ connectors.
    - La section adobe_users peut également contenir les sections exclude_identity_types, exclude_adobe_groups et exclude_users qui limitent la portée des utilisateurs affectés par User Sync. Pour plus de détails, reportez-vous à la section [Protection de comptes spécifiques contre la suppression par User Sync](advanced_configuration.md#protection-de-comptes-spécifiques-contre-la-suppression-par-user-sync).
- La sous-section **directory_users** contient elle-même deux sous-sections, connectors et groups :
    - La sous-section **connectors** pointe vers le fichier de configuration sécurisé distinct qui stocke les identifiants d’accès à votre annuaire d’entreprise.
    - La section **groups** définit le mappage entre vos groupes d’annuaire et les configurations de produits et groupes d’utilisateurs Adobe.
    - **directory_users** peut également contenir des clés qui définissent le type d’identité et le code de pays par défaut. Reportez-vous aux exemples de fichiers de configuration pour plus de détails.
- La section **limits** définit la valeur `max_adobe_only_users` qui empêche User Sync de mettre à jour ou de supprimer les comptes d’utilisateurs Adobe si un nombre de comptes supérieur à la valeur spécifiée apparaît dans l’organisation Adobe, mais pas dans l’annuaire. Cette limite empêche le retrait d’un grand nombre de comptes en cas de problème de configuration ou d’autres erreurs. Cet élément est obligatoire.
- La section **logging** spécifie le chemin d’accès à la piste d’audit et contrôle la quantité d’informations écrites dans le journal.

### Configuration des fichiers de connexion

Le fichier de configuration principal de User Sync comporte uniquement les noms des fichiers de configuration de connexion qui contiennent les identifiants de connexion. Les informations sensibles sont ainsi isolées, ce qui permet de sécuriser les fichiers et de limiter l’accès à ceux-ci.

Fournissez des pointeurs vers les fichiers de configuration de connexion dans les
sections **adobe_users** et  **directory_users** :

```
adobe_users:
  connectors:
    umapi: connector-umapi.yml

directory_users:
  connectors:
    ldap: connector-ldap.yml
```

### Configuration d’un mappage de groupe

Pour synchroniser les groupes d’utilisateurs et les droits d’accès, vous devez d’abord créer les configurations de produits et les groupes d’utilisateurs dans Adobe Admin Console, ainsi que les groupes correspondants dans votre annuaire d’entreprise, comme expliqué ci-dessus à la section [Configuration de la synchronisation d’accès aux produits](setup_and_installation.md#configuration-de-la-synchronisation-d’accès-aux-produits).

**REMARQUE :** Tous les groupes doivent exister et porter les mêmes noms des deux côtés. User Sync ne crée aucun groupe d’un côté ni de l’autre. S’il ne trouve pas un groupe nommé, il consigne une erreur.

La section **groups** sous  **directory_users** doit avoir une entrée pour chaque groupe d’annuaire d’entreprise qui représente l’accès à un ou plusieurs produits Adobe. Pour chaque entrée de groupe, répertoriez les configurations de produits auxquelles les utilisateurs de ce groupe sont autorisés à accéder. Par exemple :

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

Les groupes de l’annuaire peuvent être mappés à des *configurations de produits* ou des *groupes d’utilisateurs*. Une entrée `adobe_groups` peut désigner l’un ou l’autre des deux types de groupes.

Par exemple :

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - Default Acrobat Pro DC configuration
  - directory_group: Acrobat_Accounting
    adobe_groups:
      - Accounting_Department
```

### Configuration de limites

Les comptes d’utilisateurs sont retirés du système Adobe lorsque les utilisateurs correspondants ne figurent pas dans l’annuaire et que l’outil est appelé avec l’une des options suivantes :

- `--adobe-only-user-action delete`
- `--adobe-only-user-action remove`
- `--adobe-only-user-action remove-adobe-groups`

Si votre organisation possède un grand nombre d’utilisateurs dans l’annuaire d’entreprise, mais que le nombre d’utilisateurs lus durant une synchronisation est subitement très faible, cela peut indiquer une erreur ou une configuration incorrecte. La valeur de `max_adobe_only_users` est un seuil qui indique à User Sync de suspendre la suppression et la mise à jour des comptes Adobe existants, et de signaler une erreur si les utilisateurs dans l’annuaire d’entreprise (tel que filtré par les paramètres de requête) sont moins nombreux que dans le portail Adobe Admin Console (et que la différence dépasse la valeur de seuil).

Augmentez cette valeur si vous pensez que le nombre d’utilisateurs peut baisser en deçà de la valeur actuelle.

Par exemple :

```YAML
limits:
  max_adobe_only_users: 200
```

Cette configuration indique à User Sync de vérifier si plus de 200 comptes d’utilisateurs présents dans les systèmes Adobe ne se trouvent pas dans l’annuaire d’entreprise (tel que filtré). Le cas échéant, aucun compte Adobe n’est mis à jour et un message d’erreur est consigné.

###  Configuration de la consignation

Les entrées de journal sont écrites dans la console à partir de laquelle l’outil a été appelé, et éventuellement dans un fichier journal. Une nouvelle entrée est écrite dans le journal, avec la date et l’heure, chaque fois que User Sync s’exécute.

La section **logging** permet d’activer et de désactiver la consignation dans un fichier et contrôle la quantité d’informations écrites dans le journal et la console.

```YAML
logging:
  log_to_file: True | False
  file_log_directory: "path to log folder"
  file_log_level: debug | info | warning | error | critical
  console_log_level: debug | info | warning | error | critical
```

La valeur log_to_file active ou désactive la consignation dans un fichier. Les messages de journal sont toujours écrits dans la console, quel que soit le paramètre log_to_file.

Lorsque la consignation dans un fichier est activée, la valeur de file_log_directory est requise. Cette valeur spécifie le dossier dans lequel les entrées de journal doivent être écrites.

- Indiquez un chemin d’accès absolu ou un chemin relatif au dossier contenant ce fichier de configuration.
- Assurez-vous que le fichier et le dossier disposent des autorisations de lecture/d’écriture appropriées.

Les valeurs log_level déterminent la quantité d’informations écrites dans le fichier journal ou la console.

- Le niveau le plus bas, debug, écrit le plus d’informations, tandis que le plus élevé, critical, en écrit le moins.
- Vous pouvez définir différentes valeurs log_level pour le fichier et la console.

Les entrées de journal contenant WARNING, ERROR ou CRITICAL comportent une description qui accompagne le statut. Par exemple :

> `2017-01-19 12:54:04 7516 WARNING
console.trustee.org1.action - Error requestID: action_5 code: `"error.user.not_found" message: "No valid users were found in the request"`

Dans cet exemple, un avertissement a été consigné lors de l’exécution le 19/01/2017 à 12:54:04. Une action a provoqué une erreur avec le code « error.user.not_found ». La description associée à ce code d’erreur est incluse.

Vous pouvez utiliser la valeur requestID pour rechercher la demande exacte associée à une erreur signalée. Dans l’exemple, la recherche de « action_5 » renvoie les détails suivants :

> `2017-01-19 12:54:04 7516 INFO console.trustee.org1.action -
Added action: {"do":
\[{"add": {"product": \["default adobe enterprise support program configuration"\]}}\],
"requestID": "action_5", "user": "cceuser2@ensemble.ca"}`

Cela vous donne plus d’informations sur l’action qui a engendré le message d’avertissement. Dans ce cas, User Sync a tenté d’ajouter « default adobe enterprise support program configuration » (configuration de programme Adobe de support aux entreprises par défaut) à l’utilisateur « cceuser2@ensemble.ca ». L’action d’ajout a échoué car l’outil n’a pas trouvé l’utilisateur.

## Exemples de configurations

Ces exemples présentent la structure des fichiers de configuration et illustrent des valeurs de configuration possibles.

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
  # Cette section décrit l’emplacement des serveurs utilisés pour la gestion des utilisateurs Adobe. Valeur par défaut :
  # host: usermanagement.adobe.io
  # endpoint: /v2/usermanagement
  # ims_host: ims-na1.adobelogin.com
  # ims_endpoint_jwt: /ims/exchange/jwt

enterprise:
  org_id : indiquez ici l’ID d’organisation
  api_key : indiquez ici la clé d’API
  client_secret : indiquez ici le secret client
  tech_acct : indiquez ici l’ID de compte technique
  priv_key_path : indiquez ici le chemin d’accès à la clé privée
  # priv_key_data : indiquez ici les données de la clé # Il s’agit d’une alternative à priv_key_path
```

## Test de votre configuration

Utilisez ces scénarios de test pour vous assurer que votre configuration fonctionne correctement et que les configurations de produits sont correctement mappées à vos groupes sécurisés de l’annuaire d’entreprise. Exécutez l’outil en mode test pour commencer (en indiquant le paramètre -t), afin de voir le résultat avant de l’exécuter pour du bon.

Les exemples suivants utilisent `--users all` pour sélectionner des utilisateurs, mais vous pouvez souhaiter utiliser `--users mapped` pour sélectionner uniquement des utilisateurs dans des groupes d’annuaires répertoriés dans votre fichier de configuration, ou `--users file f.csv` pour sélectionner un plus petit ensemble d’utilisateurs de test répertoriés dans un fichier.

###  Création d’utilisateurs


1. Créez un ou plusieurs utilisateurs test dans l’annuaire d’entreprise.


2. Ajoutez les utilisateurs à un ou plusieurs groupes de l’annuaire/de sécurité configurés.


3. Exécutez User Sync en mode test. (`./user-sync -t --users all --process-groups --adobe-only-user-action exclude`)


3. Exécutez User Sync sans le mode test. (`./user-sync --users all --process-groups --adobe-only-user-action exclude`)


4. Vérifiez que les utilisateurs test ont été créés dans Adobe Admin Console.

### Mise à jour d’utilisateurs


1. Modifiez l’appartenance d’un ou de plusieurs utilisateurs test aux groupes de l’annuaire.


1. Exécutez User Sync. (`./user-sync --users all --process-groups --adobe-only-user-action exclude`)


2. Vérifiez que les utilisateurs test dans Adobe Admin Console ont été mis à jour et qu’ils indiquent la nouvelle appartenance à la configuration de produit.

###  Désactivation d’utilisateurs


1. Retirez ou désactivez un ou plusieurs utilisateurs test existants dans votre annuaire d’entreprise.


2. Exécutez User Sync. (`./user-sync --users all --process-groups --adobe-only-user-action remove-adobe-groups`) Vous souhaiterez peut-être exécuter cette commande en mode test (-t) d’abord.


3. Vérifiez que les utilisateurs ont été retirés des configurations de produits définies dans Adobe Admin Console.


4. Exécutez User Sync pour retirer les utilisateurs (`./user-sync -t --users all --process-groups --adobe-only-user-action delete`), puis exécutez-le à nouveau sans le paramètre -t. Attention : Vérifiez que seuls les utilisateurs souhaités ont été retirés lors de l’exécution avec le paramètre -t. La nouvelle exécution (sans le paramètre -t) aura pour effet de supprimer définitivement les utilisateurs concernés.


5. Vérifiez que les comptes d’utilisateurs sont retirés du portail Adobe Admin Console.

---

[Section précédente](setup_and_installation.md)  \| [Section suivante](command_parameters.md)
