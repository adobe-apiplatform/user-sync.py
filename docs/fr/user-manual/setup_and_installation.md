---
layout: default
lang: fr
nav_link: Installation et configuration
nav_level: 2
nav_order: 20
---

# Installation et configuration

## Dans cette section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Section précédente](index.md)  \| [Section suivante](configuring_user_sync_tool.md)

---

Pour utiliser User Sync, votre entreprise doit avoir défini des configurations de produits dans Adobe Admin Console. Pour savoir comment procéder, reportez-vous à la page d’aide [Configuration des services](https://helpx.adobe.com/fr/enterprise/help/configure-services.html#configure_services_for_group).

## Configuration d’une intégration de l’API User Management dans Adobe I/O

L’outil User Sync est un client de l’API User Management. Avant d’installer l’outil, vous devez l’enregistrer en tant que client de l’API en ajoutant une *intégration* dans le [portail de développement](https://www.adobe.io/console/) d’Adobe I/O. Vous devrez ajouter une intégration de clé d’entreprise afin d’obtenir les identifiants de connexion dont l’outil a besoin pour accéder au système Adobe de gestion des utilisateurs.

Les étapes de création d’une intégration sont décrites en détail dans la section [Setting up Access](https://www.adobe.io/apis/cloudplatform/usermanagement/docs/setup.html) (Configuration des accès) du site web relatif à l’API User Management d’Adobe I/O. Le processus requiert la création d’un certificat spécifique à l’intégration, qui peut être autosigné. À la fin du processus, les éléments suivants vous seront attribués : **API key** (clé d’API),  **Technical account ID** (ID de compte technique),  **Organization ID** (ID d’organisation) et  **client secret** (secret client). L’outil se servira de ces éléments, ainsi que de vos informations de certificat, pour communiquer en toute sécurité avec Admin Console. Lorsque vous installez User Sync, vous devez fournir ces valeurs de configuration pour que l’outil puisse accéder au référentiel d’informations utilisateur de votre organisation dans Adobe.

## Configuration de la synchronisation d’accès aux produits

Si vous avez l’intention d’utiliser User Sync pour mettre à jour les droits d’accès des utilisateurs aux produits Adobe, vous devez créer des groupes dans votre propre annuaire d’entreprise qui correspondent aux groupes d’utilisateurs et aux configurations de produits que vous avez définis dans [Adobe Admin Console](https://www.adobe.io/console/). L’appartenance à une configuration de produit donne accès à un ensemble particulier de produits Adobe. Vous pouvez accorder ou révoquer des droits d’accès à des utilisateurs ou à des groupes d’utilisateurs définis en les ajoutant ou en les retirant d’une configuration de produit.

User Sync peut accorder l’accès aux produits en ajoutant des utilisateurs aux groupes d’utilisateurs et aux configurations de produits en fonction de leurs appartenances dans l’annuaire d’entreprise. Il faut pour cela que les noms des groupes soient correctement mappés et que vous exécutiez l’outil avec l’option de traitement des appartenances aux groupes.

Si vous souhaitez utiliser l’outil de cette façon, vous devez mapper les groupes de votre annuaire d’entreprise aux groupes Adobe correspondants dans le fichier de configuration principal. Pour cela, vous devez vous assurer que les groupes existent des deux côtés, et que vous connaissez les noms correspondants exacts.

### Vérification de vos produits et de vos configurations de produits

Avant de commencer à configurer User Sync, vous devez savoir quels produits Adobe votre entreprise utilise, et quelles configurations de produits et quels groupes d’utilisateurs sont définis dans le système Adobe de gestion des utilisateurs. Pour en savoir plus, consultez la page d’aide [Configuration des services d’entreprise](https://helpx.adobe.com/fr/enterprise/help/configure-services.html#configure_services_for_group).

Si vous n’avez pas encore de configurations de produits, vous pouvez utiliser Admin Console pour les créer. Vous devez disposer de quelques configurations de produits, et les groupes correspondants doivent figurer dans l’annuaire d’entreprise, pour pouvoir configurer User Sync de manière à mettre à jour les informations sur les droits de vos utilisateurs.

Les noms des configurations de produits identifient généralement les types d’accès aux produits dont les utilisateurs auront besoin, tels que l’accès complet ou à un produit individuel. Pour vérifier les noms exacts, accédez à la section Produits dans [Adobe Admin Console](https://www.adobe.io/console/) afin de voir les produits activés pour votre entreprise. Pour voir le détail des configurations de produits qui ont été définies pour un produit, cliquez sur celui-ci.

### Création de groupes correspondants dans votre annuaire d’entreprise

Une fois que vous avez défini les configurations de produits et les groupes d’utilisateurs dans Adobe Admin Console, vous devez créer et nommer des groupes correspondants dans votre propre annuaire d’entreprise. Par exemple, un groupe de l’annuaire correspondant à la configuration de produit « Toutes les applications » pourrait s’appeler « toutes_les_applications ».

Prenez note des noms que vous donnez à ces groupes et identifiez les groupes Adobe auxquels ils correspondent. Vous allez utiliser ces informations pour configurer un mappage dans le fichier de configuration principal de User Sync. Reportez-vous aux instructions détaillées dans la section [Configuration d’un mappage de groupe](configuring_user_sync_tool.md#configuration-d-un-mappage-de-groupe) ci-dessous.

Dans le champ de description de la configuration de produit ou du groupe d’utilisateurs, il est recommandé de noter que le groupe est géré par User Sync et qu’il ne doit pas être modifié dans Admin Console.

![Figure 2: Présentation du mappage de groupe](media/group-mapping.png)

## Installation de l’outil User Sync

### Configuration requise

L’outil User Sync est mis en œuvre à l’aide de Python et nécessite la version 2.7.9 ou ultérieure. Pour chaque environnement dans lequel vous avez l’intention d’installer, de configurer et d’exécuter le script, vous devez veiller à ce que Python ait été installé sur le système d’exploitation avant de passer à l’étape suivante. Pour plus d’informations, consultez le [site web de Python](https://www.python.org/).

L’outil repose sur un package LDAP Python, `pyldap`, lui-même basé sur la bibliothèque du client OpenLDAP. Windows Server, Apple OS X et de nombreuses versions de Linux possèdent un client OpenLDAP prêt à l’emploi. Toutefois, certains systèmes d’exploitation UNIX, tels qu’OpenBSD et FreeBSD, ne l’incluent pas dans leur installation de base.

Vérifiez votre environnement pour vous assurer qu’un client OpenLDAP est installé avant d’exécuter le script. Si ce n’est pas le cas, vous devez y remédier avant d’installer User Sync.

### Installation

L’outil User Sync est disponible à partir du [référentiel User Sync sur GitHub](https://github.com/adobe-apiplatform/user-sync.py). Pour installer l’outil :


1. Créez un dossier sur votre serveur, dans lequel vous installerez User Sync et placerez les fichiers de configuration.


1. Cliquez sur le lien **Releases** pour localiser la dernière version, qui contient les notes de mise à jour, la présente documentation, des exemples de fichiers de configuration ainsi que toutes les versions générées (de même que les archives sources).


2. Sélectionnez et téléchargez le package compressé correspondant à votre plate-forme (fichier `.tar.gz`). Des versions pour Windows, OS X et Ubuntu sont disponibles. (Si vous compilez à partir de la source, vous pouvez télécharger le package de code source correspondant à la version ou utiliser la source la plus récente au niveau de la branche principale.)


3. Recherchez le fichier exécutable Python (`user-sync` ou `user-sync.pex` pour Windows) et placez-le dans votre dossier User Sync.


4. Téléchargez l’archive `example-configurations.tar.gz` d’exemples de fichiers de configuration. L’archive contient le dossier « config files – basic ». Les trois premiers fichiers de ce dossier sont nécessaires. Les autres fichiers du package sont facultatifs et/ou des versions secondaires destinées à des fins spécifiques. Vous pouvez les copier dans votre dossier racine, puis les renommer et les modifier afin d’établir vos propres fichiers de configuration. (Voir la section suivante, [Configuration de l’outil User Sync](configuring_user_sync_tool./md#configuration-de-l-outil-user-sync).)


5. **Sous Windows uniquement :**

    Avant d’exécuter le fichier exécutable user-sync.pex sous Windows, vous devrez peut-être contourner un problème d’exécution de Python rencontré uniquement sous Windows :

    Le système d’exploitation Windows limite la longueur du chemin d’accès au fichier à 260 caractères. Lors de l’exécution d’un fichier PEX Python, il crée un emplacement temporaire pour extraire le contenu du package. Si le chemin d’accès à cet emplacement dépasse 260 caractères, le script ne s’exécute pas correctement.

    Par défaut, le cache temporaire est placé dans votre dossier Utilisateur, ce qui peut entraîner un dépassement de la limite. Pour contourner ce problème, créez une variable d’environnement sous Windows appelée PEX\_ROOT, et définissez son chemin d’accès sur C:\\user-sync\\.pex. Le système d’exploitation utilise cette variable pour l’emplacement du cache, ce qui évite que le chemin d’accès ne dépasse la limite de 260 caractères.


6. Pour exécuter l’outil User Sync, double-cliquez sur le fichier exécutable Python, `user-sync` (ou exécutez `python user-sync.pex` sous Windows).

### Remarques de sécurité

User Sync accédant à des informations sensibles aussi bien du côté de l’entreprise que d’Adobe, son utilisation nécessite un certain nombre de fichiers qui contiennent des informations sensibles. Vous devez vous assurer que ces fichiers sont protégés contre tout accès non autorisé.

La version 2.1 ou ultérieure de User Sync vous permet de stocker les identifiants de connexion dans le référentiel sécurisé du système d’exploitation, plutôt que de les stocker dans des fichiers qu’il vous faut sécuriser, ou de stocker les fichiers de configuration umapi et ldap avec la sécurité que vous pouvez définir. Reportez-vous à la section [Recommandations de sécurité](deployment_best_practices.md#recommandations-de-sécurité) pour plus de détails.

#### Fichiers de configuration

Les fichiers de configuration doivent inclure des informations sensibles, telles que votre clé de l’API Adobe User Management, le chemin d’accès à votre clé privée de certificat et les identifiants de connexion de votre annuaire d’entreprise (le cas échéant). Vous devez prendre les mesures nécessaires pour protéger tous les fichiers de configuration et vous assurer que seuls les utilisateurs autorisés sont en mesure d’y accéder. En particulier : n’autorisez pas l’accès en lecture à tout fichier contenant des informations sensibles, excepté à partir du compte d’utilisateur qui exécute le processus de synchronisation.

Si vous choisissez d’utiliser le système d’exploitation pour stocker les identifiants de connexion, vous créez toujours les mêmes fichiers de configuration. Toutefois, ceux-ci ne stockent plus les identifiants de connexion eux-mêmes, mais les ID de clés qui servent à rechercher ces identifiants. Pour en savoir plus, consultez la section [Recommandations de sécurité](deployment_best_practices.md#recommandations-de-sécurité).

Si vous laissez User Sync accéder à votre annuaire d’entreprise, il doit être configuré pour lire à partir du serveur d’annuaire à l’aide d’un compte de service. Ce compte requiert seulement un accès en lecture, et il est recommandé qu’il ne bénéficie PAS d’un accès en écriture (de sorte que toute divulgation non autorisée des identifiants ne permette pas l’accès en écriture).

#### Fichiers de certificats

Les fichiers qui contiennent les clés publiques et privées, en particulier les clés privées, contiennent des informations sensibles. Vous devez garder chaque clé privée en sécurité. Elle ne peut pas être récupérée, ni remplacée. Si vous la perdez ou si elle est compromise, vous devez supprimer le certificat correspondant de votre compte. Si nécessaire, vous devez créer et charger un nouveau certificat. Vous devez protéger ces fichiers au moins avec le même niveau de protection que pour un nom de compte et un mot de passe. Les bonnes pratiques consistent à stocker les fichiers de clés dans un système de gestion des identifiants ou à utiliser la protection du système de fichiers, de sorte que seuls les utilisateurs autorisés puissent y avoir accès.

#### Fichiers journaux

La journalisation est activée par défaut et transmet à la console toutes les transactions de l’API User Management. Vous pouvez également configurer l’outil pour écrire dans un fichier journal. Les fichiers créés lors de l’exécution sont datés et écrits sur le système de fichiers, au sein d’un dossier indiqué dans le fichier de configuration.

L’API User Management traite l’adresse électronique d’un utilisateur comme un identificateur unique. Chaque action, ainsi que l’adresse électronique associée à l’utilisateur, est écrite dans le journal. Si vous choisissez de consigner les données dans des fichiers, ces derniers contiennent ces informations.

User Sync ne fournit aucune fonction de contrôle ou de gestion concernant la conservation des journaux. Il commence chaque jour un nouveau fichier. Si vous choisissez de consigner les données dans des fichiers, prenez les précautions nécessaires pour gérer la durée de vie de ces fichiers et l’accès à ceux-ci.

Si la stratégie de sécurité de votre entreprise n’autorise pas la conservation sur disque de données personnelles, configurez l’outil pour désactiver la consignation sur fichier. L’outil continue de transmettre les transactions consignées à la console, où les données sont stockées temporairement dans la mémoire lors de l’exécution.

## Assistance pour l’outil User Sync

Les clients Adobe Enterprise peuvent utiliser leurs canaux d’assistance habituels concernant User Sync.

Dans la mesure où il s’agit d’un projet open source, vous pouvez également ouvrir un ticket dans GitHub. Pour faciliter le processus de débogage, précisez votre plate-forme, indiquez les options de ligne de commande concernées et incluez tous les fichiers journaux générés lors de l’exécution de l’application dans votre demande d’assistance (à condition qu’ils ne contiennent aucune information sensible).


---

[Section précédente](index.md)  \| [Section suivante](configuring_user_sync_tool.md)
