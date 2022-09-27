---
layout: default
lang: fr
title: Ligne de commande
nav_link: Ligne de commande
nav_level: 2
nav_order: 310
parent: success-guide
page_id: command-line-options
---

# Choix des options de ligne de commande finales

[Section précédente](monitoring.md) \| [Revenir au sommaire](index.md) \|  [Section suivante](scheduling.md)

La ligne de commande de l’outil User Sync sélectionne l’ensemble des utilisateurs à traiter, spécifie comment les appartenances aux groupes d’utilisateurs et aux configurations de produits doivent être gérées, indique la façon dont la suppression des comptes doit être traitée, ainsi que quelques options supplémentaires.

## Utilisateurs


| Option de ligne de commande Utilisateurs  | Contexte           |
| ------------- |:-------------| 
|   `--users all` |    Tous les utilisateurs qui figurent dans l’annuaire sont inclus. |
|   `--users group "g1,g2,g3"`  |    Les groupes d’annuaire nommés forment la sélection d’utilisateurs. <br>Les utilisateurs qui font partie de l’un des groupes sont inclus. |
|   `--users mapped`  |    Revient à spécifier `--users group g1,g2,g3,...`, où `g1,g2,g3,...` représente tous les groupes d’annuaire spécifiés dans le mappage des groupes au sein du fichier de configuration.|
|   `--users file f`  |    Le fichier f est lu pour former la sélection d’utilisateurs. L’annuaire LDAP n’est pas utilisé dans ce cas. |
|   `--user-filter pattern`    |  Peut être combiné avec les options ci-dessus pour filtrer davantage et réduire la sélection d’utilisateurs. <br>« pattern » est une chaîne au format d’expression régulière Python. <br>Le nom d’utilisateur doit correspondre au motif afin d’être inclus. <br>L’écriture des motifs est un art en soi. Reportez-vous aux exemples ci-dessous ou à la documentation Python [ici](https://docs.python.org/2/library/re.html). |


Si tous les utilisateurs qui figurent dans l’annuaire doivent être synchronisés avec Adobe, utilisez `--users all`. Si vous souhaitez seulement synchroniser certains utilisateurs, vous pouvez limiter l’ensemble en modifiant la requête LDAP dans le fichier de configuration connector-ldap.yml (et utiliser `--users all`). Vous pouvez également limiter les utilisateurs à ceux appartenant à des groupes spécifiques (à l’aide de --users group). Vous pouvez combiner l’un ou l’autre avec un motif `--user-filter pattern` de façon à limiter la sélection d’utilisateurs à synchroniser.

Si vous n’utilisez pas de système d’annuaire, vous pouvez utiliser `--users file f` pour sélectionner les utilisateurs à partir d’un fichier CSV. Reportez-vous à l’exemple de fichier d’utilisateurs (csv inputs - user and remove lists/users-file.csv) pour observer le format. Vous pouvez choisir les noms des groupes figurant dans les fichiers CSV. Ils sont mappés aux groupes d’utilisateurs et aux configurations de produits Adobe de la même manière que les groupes d’annuaire.

## Groupes

Si vous ne gérez pas les licences de produits avec User Sync, vous n’avez pas besoin de spécifier le mappage de groupes dans le fichier de configuration ni d’ajouter de paramètres de ligne de commande pour le traitement groupé.

Si vous gérez les licences avec User Sync, incluez l’option `--process-groups` sur la ligne de commande.


## Suppression de compte


Il existe plusieurs options de ligne de commande qui permettent de spécifier la mesure à prendre lorsque le système détecte un compte Adobe sans compte correspondant dans l’annuaire (il s’agit d’un utilisateur « Adobe uniquement »).
Notez que seuls les utilisateurs renvoyés par le filtre et la requête d’annuaire sont considérés comme « existants » dans l’annuaire d’entreprise. Ces options vont d’ignorer à supprimer complètement, avec plusieurs options entre les deux.



| Option de ligne de commande       ...........| Contexte           |
| ------------- |:-------------| 
|   `--adobe-only-user-action exclude`                        |  Aucune action à effectuer sur les comptes qui se trouvent uniquement dans les systèmes Adobe et ne correspondent à aucun compte dans l’annuaire. Les appartenances aux groupes Adobe ne sont pas mises à jour, même si `--process-groups` est présent. |
|   `--adobe-only-user-action preserve`                        |  Pas de retrait ou de suppression des comptes qui se trouvent uniquement dans les systèmes Adobe et ne correspondent à aucun compte dans l’annuaire. Les appartenances aux groupes Adobe sont mises à jour si `--process-groups` est présent. |
|   `--adobe-only-user-action remove-adobe-groups` |    Les comptes Adobe sont conservés, mais les licences <br>et les appartenances aux groupes sont retirées. |
|   `--adobe-only-user-action remove`  |    Les comptes Adobe sont conservés, mais les licences, les appartenances aux groupes et l’entrée dans Adobe Admin Console sont retirées.   |
|   `--adobe-only-user-action delete`  |    Compte Adobe à supprimer : retiré des configurations de produits<br>et des groupes d’utilisateurs Adobe ; le compte est effacé et tout le stockage et les paramètres sont remis à disposition. |
|   `--adobe-only-user-action write-file f.csv`    |  Aucune action à effectuer sur ce compte. Nom d’utilisateur écrit dans le fichier pour action ultérieure. |




## Autres options

`--test-mode` : indique à User Sync d’exécuter le traitement, y compris l’interrogation de l’annuaire et l’appel de l’API Adobe User Management pour traiter la demande, mais sans effectuer d’action. Aucun utilisateur n’est créé, supprimé ou modifié.

`--update-user-info` : indique à User Sync de vérifier si les prénoms, noms et adresses e-mail des utilisateurs ont changé et de mettre à jour les informations des systèmes Adobe si elles ne correspondent pas à celles de l’annuaire. La spécification de cette option peut augmenter le temps d’exécution.


## Exemples

Quelques exemples :

`user-sync --users all --process-groups --adobe-only-user-action remove`

- Traiter tous les utilisateurs en fonction des paramètres de configuration, mettre à jour les appartenances aux groupes Adobe et, si des utilisateurs Adobe ne figurent pas dans l’annuaire, les retirer des systèmes Adobe pour libérer les éventuelles licences attribuées. Le compte Adobe n’est pas supprimé afin qu’il soit possible de l’ajouter à nouveau ou de récupérer les actifs stockés.
    
`user-sync --users file users-file.csv --process-groups --adobe-only-user-action remove`

- Le fichier « users-file.csv » est lu en tant que liste d’utilisateurs principale. Aucune tentative de communication avec un service d’annuaire tel qu’AD ou LDAP n’est effectuée dans ce cas. Les appartenances aux groupes Adobe sont mises à jour d’après les informations figurant dans le fichier, et tous les comptes Adobe qui n’apparaissent pas dans le fichier sont retirés (voir la définition du retrait plus haut).

## Définition de votre ligne de commande

Vous préférerez peut-être réaliser les premières exécutions sans option de suppression.

&#9744;Mettez en place les options de ligne de commande dont vous avez besoin pour exécuter User Sync.


[Section précédente](monitoring.md) \| [Revenir au sommaire](index.md) \|  [Section suivante](scheduling.md)
