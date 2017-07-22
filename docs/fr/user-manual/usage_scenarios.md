---
layout: default
lang: fr
nav_link: Scénarios d’utilisation
nav_level: 2
nav_order: 50
---

# Scénarios d’utilisation

## Dans cette section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Section précédente](command_parameters.md)  \| [Section suivante](advanced_configuration.md)

---

Il existe plusieurs façons d’intégrer l’outil User Sync dans vos processus d’entreprise, notamment :

* **Mettre à jour les utilisateurs et les appartenances aux groupes.** Synchronisez les utilisateurs et les appartenances aux groupes en ajoutant, en mettant à jour et en retirant des utilisateurs dans le système Adobe de gestion des utilisateurs. Il s’agit du scénario d’utilisation le plus courant.
* **Synchroniser uniquement les informations utilisateur.** Utilisez cette approche si l’accès aux produits doit être géré par l’intermédiaire du portail Admin Console.
* **Filtrer les utilisateurs à synchroniser.** Vous pouvez choisir de limiter la synchronisation aux informations relatives aux utilisateurs de groupes spécifiques, ou aux utilisateurs qui correspondent à un motif donné. Vous pouvez également procéder à la synchronisation par rapport à un fichier CSV plutôt qu’un système d’annuaire.
* **Mettre à jour les utilisateurs et les appartenances aux groupes, mais gérer les retraits séparément.** Synchronisez les utilisateurs et les appartenances aux groupes en ajoutant et en mettant à jour des utilisateurs, mais sans les retirer dans l’appel initial. Dressez à part la liste des utilisateurs à retirer, puis effectuez les retraits dans un appel distinct.

Cette section fournit des instructions détaillées pour chacun de ces scénarios.

## Mettre à jour les utilisateurs et les appartenances aux groupes

Il s’agit du type d’appel le plus courant. User Sync détecte toutes les modifications apportées aux données utilisateur et aux informations sur les appartenances aux groupes du côté de l’entreprise. Il synchronise les systèmes Adobe en ajoutant, en mettant à jour et en retirant des utilisateurs, ainsi que les appartenances aux groupes d’utilisateurs et aux configurations de produits.

Par défaut, seuls les utilisateurs dont le type d’identité est Enterprise ID ou Federated ID sont créés, retirés ou voient leurs appartenances aux groupes gérées par User Sync, car généralement les utilisateurs possédant un Adobe ID ne sont pas gérés dans l’annuaire. Reportez-vous à la [description ci-dessous](advanced_configuration.md#gestion-des-utilisateurs-disposant-dun-adobeid
sous [Configuration avancée](advanced_configuration.md#configuration-avancée) si votre organisation opère de cette façon.

Cet exemple suppose que le fichier de configuration, user-sync-config.yml, contient un mappage entre un groupe d’annuaire et une configuration de produit Adobe nommée **Default Acrobat Pro DC configuration**.

### Commande

Cet appel fournit les paramètres users (utilisateurs) et process-groups (groupes de traitement), et permet le retrait des utilisateurs avec le paramètre `adobe-only-user-action remove`.

```sh
./user-sync –c user-sync-config.yml --users all --process-groups --adobe-only-user-action remove
```

### Données consignées au cours de l’opération

```text
2017-01-20 16:51:02 6840 INFO main - ========== Start Run ==========
2017-01-20 16:51:04 6840 INFO processor - ---------- Start Load from Directory -----------------------
2017-01-20 16:51:04 6840 INFO connector.ldap - Loading users...
2017-01-20 16:51:04 6840 INFO connector.ldap - Total users loaded: 4
2017-01-20 16:51:04 6840 INFO processor - ---------- End Load from Directory (Total time: 0:00:00) ---
2017-01-20 16:51:04 6840 INFO processor - ---------- Start Sync Dashboard ----------------------------
2017-01-20 16:51:05 6840 INFO processor - Adding user with user key: fed_ccewin4@ensemble-systems.com 2017-01-20 16:51:05 6840 INFO dashboard.owning.action - Added action: {"do": \[{"createFederatedID": {"lastname": "004", "country": "CA", "email": "fed_ccewin4@ensemble-systems.com", "firstname": "!Fed_CCE_win", "option": "ignoreIfAlreadyExists"}}, {"add": {"product": \["default acrobat pro dc configuration"\]}}\], "requestID": "action_5", "user": "fed_ccewin4@ensemble-systems.com"}
2017-01-20 16:51:05 6840 INFO processor - Syncing trustee org1... /v2/usermanagement/action/82C654BDB41957F64243BA308@AdobeOrg HTTP/1.1" 200 77
2017-01-20 16:51:07 6840 INFO processor - ---------- End Sync Dashboard (Total time: 0:00:03) --------
2017-01-20 16:51:07 6840 INFO main - ========== End Run (Total time: 0:00:05) ==========
```

### Affichage du résultat

Lorsque la synchronisation réussit, Adobe Admin Console est mis à jour. Une fois que cette commande a été exécutée, vos listes d’utilisateurs et de configurations de produits dans Admin Console indiquent qu’un utilisateur disposant d’un Federated ID a été ajouté à « Default Acrobat Pro DC configuration. ».

![Figure 3: Capture d’écran du portail Admin Console](media/edit-product-config.png)

### Synchroniser uniquement les utilisateurs

Si vous fournissez uniquement le paramètre `users` à la commande, l’action détecte les modifications apportées aux informations utilisateur dans l’annuaire d’entreprise et met à jour les systèmes Adobe en conséquence. Vous pouvez fournir des arguments au paramètre `users` qui déterminent quels utilisateurs examiner côté entreprise.

Cet appel ne recherche pas et ne met pas à jour les modifications apportées aux appartenances aux groupes. Si vous utilisez l’outil de cette façon, vous êtes tenu de contrôler l’accès aux produits Adobe en mettant à jour les appartenances aux groupes d’utilisateurs et aux configurations de produits dans Adobe Admin Console.

Cet appel ignore également les utilisateurs qui figurent dans les systèmes Adobe, mais plus dans l’annuaire, et n’effectue aucune gestion des configurations de produits ou groupes d’utilisateurs.

```sh
./user-sync –c user-sync-config.yml --users all
```

### Filtrer les utilisateurs à synchroniser

Que vous choisissiez ou non de synchroniser les informations sur les appartenances aux groupes, vous pouvez fournir des arguments au paramètre « users » qui filtrent les utilisateurs concernés dans l’annuaire d’entreprise ou qui obtiennent les informations utilisateur à partir d’un fichier CSV au lieu d’utiliser directement l’annuaire d’entreprise LDAP.

### Synchroniser uniquement les utilisateurs faisant partie de groupes spécifiques

Cette action recherche uniquement les changements relatifs aux données des utilisateurs figurant dans les groupes spécifiés. Elle ne s’intéresse à aucun autre utilisateur dans l’annuaire d’entreprise et n’effectue aucune gestion des configurations de produits ou groupes d’utilisateurs.

```sh
./user-sync –c user-sync-config.yml --users groups "group1, group2, group3"
```

### Synchroniser uniquement les utilisateurs faisant partie des groupes mappés

Cette action revient à spécifier `--users groups "..."`, où `...` représente tous les groupes répertoriés dans le mappage des groupes au sein du fichier de configuration.

```sh
./user-sync –c user-sync-config.yml --users mapped
```

### Synchroniser uniquement les utilisateurs correspondants

Cette action recherche uniquement les changements relatifs aux données des utilisateurs dont l’ID correspond à un motif. Le motif est défini à l’aide d’une expression régulière Python. Dans cet exemple, nous mettons également à jour les appartenances aux groupes.

```sh
user-sync --users all --user-filter 'bill@forxampl.com' --process-groups
user-sync --users all --user-filter 'b.*@forxampl.com' --process-groups
```

### Synchroniser à partir d’un fichier

Cette action synchronise les informations utilisateur fournies à partir d’un fichier CSV, au lieu d’examiner l’annuaire d’entreprise. Un exemple de ce type de fichier, users-file.csv, est fourni dans les exemples de fichiers de configuration téléchargeables, dans `examples/csv inputs - user and remove lists/`.

```sh
./user-sync --users file user_list.csv
```

La synchronisation à partir d’un fichier peut être utilisée dans deux contextes. Tout d’abord, les utilisateurs Adobe peuvent être gérés à l’aide d’une feuille de calcul. Celle-ci répertorie les utilisateurs, les groupes dans lesquels ils se trouvent, ainsi que les informations à leur sujet. Ensuite, si l’annuaire d’entreprise peut envoyer des notifications Push en cas de mise à jour, ces notifications peuvent être placées dans un fichier CSV et utilisées pour réaliser les mises à jour de l’outil User Sync. Reportez-vous à la section ci-dessous pour en savoir plus sur ce scénario d’utilisation.

### Mettre à jour les utilisateurs et les appartenances aux groupes, mais gérer les retraits séparément

Si vous n’indiquez pas le paramètre `--adobe-only-user-action`, vous pouvez synchroniser les utilisateurs et les appartenances aux groupes sans retirer aucun utilisateur des systèmes Adobe.

Si vous souhaitez gérer les retraits séparément, vous pouvez indiquer à l’outil de signaler les utilisateurs qui n’existent plus dans l’annuaire de l’entreprise, mais existent toujours dans les systèmes Adobe. Le paramètre `--adobe-only-user-action write-file exiting-users.csv` écrit dans un fichier CSV la liste des utilisateurs qui sont signalés pour retrait.

Pour effectuer les retraits dans un appel distinct, vous pouvez transmettre le fichier généré par le paramètre `--adobe-only-user-action write-file`, ou bien transmettre un fichier CSV d’utilisateurs que vous avez généré d’une autre façon. Un exemple de ce type de fichier, `3 remove-list.csv`, est fourni dans le fichier example-configurations.tar.gz au sein du dossier `csv inputs - user and remove lists`.

#### Ajouter des utilisateurs et générer une liste d’utilisateurs à retirer

Cette action synchronise tous les utilisateurs et génère en parallèle une liste d’utilisateurs qui n’existent plus dans l’annuaire, mais figurent toujours dans les systèmes Adobe.

```sh
./user-sync --users all --adobe-only-user-action write-file users-to-remove.csv
```

#### Retirer des utilisateurs à partir d’une liste distincte

Cette action prend un fichier CSV contenant une liste d’utilisateurs qui ont été signalés pour retrait et retire ces utilisateurs de l’organisation au sein des systèmes Adobe. Le fichier CSV est généralement celui généré par un appel précédent qui a utilisé le paramètre `--adobe-only-user-action write-file`.

Il existe d’autres façons de créer un fichier CSV d’utilisateurs à retirer. Toutefois, si votre liste comprend des utilisateurs qui existent encore dans votre annuaire, ceux-ci seront à nouveau ajoutés aux systèmes Adobe lors de la prochaine action de synchronisation qui ajoute des utilisateurs.

```sh
./user-sync --adobe-only-user-list users-to-remove.csv --adobe-only-user-action remove
```

### Supprimer les utilisateurs qui figurent dans les systèmes Adobe, mais pas dans l’annuaire

Cet appel fournit les paramètres users (utilisateurs) et process-groups (groupes de traitement), et permet la suppression des comptes d’utilisateurs avec le paramètre adobe-only-user-action delete.

```sh
./user-sync --users all --process-groups --adobe-only-user-action delete
```

### Supprimer des utilisateurs à partir d’une liste distincte

De la même façon que l’exemple de retrait d’utilisateurs ci-dessus, celui-ci supprime les utilisateurs qui existent uniquement dans les systèmes Adobe, d’après la liste générée lors d’une précédente exécution de User Sync.

```sh
./user-sync --adobe-only-user-list users-to-delete.csv --adobe-only-user-action delete
```

## Gestion des notifications Push

Si votre système d’annuaire peut générer des notifications de mises à jour, vous pouvez utiliser User Sync pour traiter ces mises à jour de manière incrémentielle. La technique décrite dans cette section peut également servir à traiter les mises à jour immédiates où l’administrateur a modifié un utilisateur ou un groupe d’utilisateurs et souhaite envoyer de suite ces mises à jour (et aucune autre) dans le système Adobe de gestion des utilisateurs. Un script peut être nécessaire pour convertir les informations provenant de la notification Push dans un format CSV lisible par User Sync, ainsi que pour séparer les suppressions des autres mises à jour, qui doivent être gérées séparément dans User Sync.

Créez un fichier, par exemple `updated_users.csv`, avec le format de mise à jour d’utilisateur illustré dans le fichier d’exemple `users-file.csv` au sein du dossier `csv inputs - user and remove lists`. Il s’agit d’un fichier CSV de base constitué de colonnes pour les prénoms, les noms, etc.

    firstname,lastname,email,country,groups,type,username,domain
    John,Smith,jsmith@example.com,US,"AdobeCC-All",enterpriseID
    Jane,Doe,jdoe@example.com,US,"AdobeCC-All",federatedID
 
Ce fichier est ensuite fourni à User Sync :

```sh
./user-sync --users file updated-users.csv --process-groups --update-users --adobe-only-user-action exclude
```

Grâce au paramètre --adobe-only-user-action exclude, User Sync met uniquement à jour les utilisateurs figurant dans le fichier updated-users.csv mis à jour et ignore tous les autres.

Les suppressions sont traitées de la même manière. Créez un fichier `deleted-users.csv` basé sur le format du fichier `remove-list.csv` se trouvant le même dossier d’exemples, puis exécutez User Sync :

```sh
./user-sync --adobe-only-user-list deleted-users.csv --adobe-only-user-action remove
```

Cela permettra de gérer les suppressions sur la base des notifications, et aucune autre action ne sera effectuée. Notez que `remove` peut être remplacé par une des autres actions, en fonction de la façon dont vous souhaitez traiter les utilisateurs supprimés.

## Résumé des actions

À la fin de l’appel, un résumé des actions est consigné dans le journal (si le niveau est INFO ou DEBUG). 
Ce résumé fournit des statistiques recueillies au cours de l’exécution. 
Les statistiques collectées incluent les valeurs suivantes :

- **Total number of Adobe users:** Nombre total d’utilisateurs Adobe dans votre portail Admin Console
- **Number of Adobe users excluded:** Nombre d’utilisateurs Adobe exclus des opérations par les paramètres exclude
- **Total number of directory users:** Nombre total d’utilisateurs lus depuis le fichier LDAP ou CSV
- **Number of directory users selected:** Nombre d’utilisateurs de l’annuaire sélectionnés par le paramètre user-filter
- **Number of Adobe users created:** Nombre d’utilisateurs Adobe créés au cours de cette exécution
- **Number of Adobe users updated:** Nombre d’utilisateurs Adobe mis à jour au cours de cette exécution
- **Number of Adobe users removed:** Nombre d’utilisateurs Adobe retirés de l’organisation dans les systèmes Adobe
- **Number of Adobe users deleted:** Nombre d’utilisateurs Adobe retirés de l’organisation et de comptes d’utilisateurs Enterprise/Federated supprimés des systèmes Adobe
- **Number of Adobe users with updated groups:** Nombre d’utilisateurs Adobe ajoutés à un ou plusieurs groupes d’utilisateurs
- **Number of Adobe users removed from mapped groups:** Nombre d’utilisateurs Adobe retirés d’un ou de plusieurs groupes d’utilisateurs
- **Number of Adobe users with no changes:** Nombre d’utilisateurs Adobe non modifiés au cours de cette exécution

### Exemple de résumé des actions consigné dans le journal
```text
2017-03-22 21:37:44 21787 INFO processor - ------------- Action Summary -------------
2017-03-22 21:37:44 21787 INFO processor -   Total number of Adobe users: 50
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users excluded: 0
2017-03-22 21:37:44 21787 INFO processor -   Total number of directory users: 10
2017-03-22 21:37:44 21787 INFO processor -   Number of directory users selected: 10
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users created: 7
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users updated: 1
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users removed: 1
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users deleted: 0
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users with updated groups: 2
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users removed from mapped groups: 5
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users with no changes: 48
2017-03-22 21:37:44 21787 INFO processor - ------------------------------------------
```

---

[Section précédente](command_parameters.md)  \| [Section suivante](advanced_configuration.md)

