---
layout: default
lang: fr
nav_link: Avant de commencer
nav_level: 2
nav_order: 110
---

# Ce que vous devez savoir avant de commencer

[Revenir au sommaire](index.md) \| [Section suivante](layout_orgs.md)

## Présentation de l’outil User Sync

User Sync est un outil de ligne de commande qui transfère les informations relatives aux utilisateurs et aux groupes du système d’annuaire de votre entreprise (tel qu’Active Directory ou autre système LDAP) ou d’autres sources vers le système Adobe de gestion des utilisateurs. User Sync repose sur la notion que le système d’annuaire d’entreprise est la source d’informations de référence sur les utilisateurs, et les données utilisateur qu’il contient sont transmises au système Adobe de gestion des utilisateurs sous le contrôle d’un ensemble de fichiers de configuration User Sync et d’options de ligne de commande.

Chaque fois que vous exécutez l’outil, il recherche les différences entre les données utilisateur dans les deux systèmes, puis met à jour le système Adobe afin qu’il corresponde à votre annuaire d’entreprise.

User Sync permet de créer des comptes Adobe lorsque de nouveaux utilisateurs apparaissent dans l’annuaire, de mettre à jour les informations de compte lorsque certains champs de l’annuaire changent, ainsi que de mettre à jour les appartenances aux groupes d’utilisateurs et aux configurations de produits afin de contrôler l’attribution des licences aux utilisateurs. Vous pouvez également gérer la suppression des comptes Adobe lorsque l’utilisateur est retiré de l’annuaire d’entreprise.

D’autres fonctionnalités permettent d’utiliser des attributs d’annuaire personnalisés afin de contrôler les valeurs transmises au compte Adobe.

Outre la synchronisation avec les systèmes d’annuaire d’entreprise, il est possible de synchroniser les données à partir d’un simple fichier CSV. Cela peut être utile pour les petites organisations ou les petits services qui n’utilisent pas de système d’annuaire centralisé.

Enfin, pour les annuaires volumineux, il est possible de piloter User Sync via des notifications Push signalant les modifications apportées dans le système d’annuaire, plutôt que de comparer un grand nombre de comptes d’utilisateurs.

## Terminologie

- Groupe d’utilisateurs : groupe nommé d’utilisateurs dans le système Adobe de gestion des utilisateurs.
- CP : configuration de produit. Procédé de groupe Adobe selon lequel, lorsque des utilisateurs sont ajoutés à une configuration de produit, ils obtiennent l’accès à un produit Adobe spécifique.
- Annuaire : terme général correspondant à un système d’annuaire d’utilisateurs, tel qu’Active Directory (AD), LDAP ou un fichier CSV répertoriant les utilisateurs.
- Groupe d’annuaire : groupe nommé d’utilisateurs dans l’annuaire.

 

## Portée des configurations
User Sync est un outil très général qui peut prendre en charge une grande variété de configurations et de besoins de traitement.

En fonction de la taille de votre organisation et des produits Adobe que vous avez achetés, vous aurez probablement une ou plusieurs consoles d’administration et organisations au sein de votre environnement Adobe. Chaque organisation possède un ou plusieurs administrateurs, et vous devez être l’un d’eux pour pouvoir définir les informations d’accès associées à User Sync.

Chaque organisation Adobe possède un ensemble d’utilisateurs. Les utilisateurs peuvent être de l’un des trois types suivants :

- Adobe ID : compte créé et détenu par l’utilisateur. Le compte et l’accès à celui-ci sont gérés à l’aide des fonctions d’Adobe. Un administrateur ne peut pas contrôler le compte.

- Enterprise ID : compte créé et détenu par l’entreprise. Le compte et l’accès à celui-ci sont gérés à l’aide des fonctions d’Adobe. Un administrateur peut contrôler le compte.

- Federated ID : compte créé et détenu par l’entreprise. Le compte est partiellement géré à l’aide des fonctions d’Adobe, mais les paramètres d’accès (mot de passe et identifiant) sont contrôlés et gérés par l’entreprise.

Les Enterprise ID et Federated ID doivent être dans un domaine déposé et détenu par l’entreprise, et configuré dans l’organisation Adobe à l’aide du portail Adobe Admin Console.

Si vous avez plusieurs organisations Adobe, vous devrez connaître les domaines et les utilisateurs compris dans chaque organisation, et savoir de quelle manière ces groupes correspondent aux comptes définis par votre système d’annuaire. Vous pouvez tout à fait disposer d’une configuration simple avec un seul système d’annuaire et une seule organisation Adobe. Si vous avez plusieurs annuaires ou organisations, il vous faudra établir les correspondances entre les systèmes et les organisations Adobe auxquelles ils envoient les informations utilisateur. Vous aurez peut-être besoin de plusieurs instances de l’outil User Sync, chacune ciblant une organisation Adobe différente.

User Sync peut gérer la création et la mise à jour des utilisateurs, de même que les licences. L’utilisation de User Sync pour la gestion des licences est facultative et ne dépend pas des autres fonctions de l’outil. Les licences peuvent être gérées manuellement depuis le portail Adobe Admin Console ou une autre application.

Il existe diverses options pour gérer la suppression des comptes. Il est possible que vous souhaitiez supprimer immédiatement les comptes Adobe lorsque le compte d’entreprise correspondant est retiré, ou que vous ayez mis en place un autre processus visant à conserver le compte Adobe jusqu’à ce qu’une personne vérifie s’il y a des actifs à récupérer dans ce compte. User Sync peut traiter toute une gamme de processus de suppression, y compris ceux-ci.


## User Sync s’exécute sur vos systèmes. 
Vous aurez besoin d’un serveur pour l’héberger. User Sync est une application Python open source. Vous pouvez utiliser un package Python prédéfini ou le générer vous-même à partir de la source.

## Ce qu’il vous faut savoir et faire

----------

### Système d’annuaire
Vous devez comprendre votre annuaire et savoir comment y accéder.

Parmi les utilisateurs figurant dans l’annuaire, vous devez savoir lesquels doivent être des utilisateurs Adobe.

### Questions de processus
Vous devez établir un processus continu et dédier une personne à sa surveillance.

Vous devez comprendre comment les produits doivent être gérés (qui y a accès et comment, par exemple) dans votre entreprise.

Vous devez décider si vous souhaitez gérer seulement les utilisateurs, ou les utilisateurs et les licences de produits.

Vous devez décider comment vous souhaitez gérer les suppressions de comptes lorsque des utilisateurs sont retirés de l’annuaire.

### Environnement Adobe
Vous devez bien connaître les produits Adobe que vous détenez.

Vous devez savoir quelles sont les organisations Adobe mises en place et quels utilisateurs en font partie.

Vous avez besoin d’un accès d’administrateur à votre ou vos organisations Adobe.

[Revenir au sommaire](index.md) \|  [Section suivante](layout_orgs.md)
