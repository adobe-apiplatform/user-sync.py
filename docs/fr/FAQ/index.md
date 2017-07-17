---
layout: page
title: FAQ sur l’outil User Sync
advertise: FAQ
lang: fr
nav_link: FAQ
nav_level: 1
nav_order: 500
---
### Table des matières
{:."no_toc"}

* TOC Placeholder
{:toc}


### À quoi sert User Sync ?

Il s’agit d’un outil qui permet aux entreprises clientes de créer/gérer les utilisateurs Adobe et leurs droits d’accès Active Directory (ou d’autres services d’annuaire OpenLDAP testés). Cet outil est destiné aux administrateurs d’identités (administrateurs système/d’annuaire d’entreprise) qui seront chargés de l’installer et de le configurer. Cet outil open source est personnalisable, de sorte que les clients peuvent demander à un développeur de le modifier selon leurs propres besoins. 

### En quoi User Sync est-il important ?

Étant indépendant du cloud (CC, EC, DC), l’outil User Sync agit comme un catalyseur pour inciter davantage d’utilisateurs à opter pour un déploiement avec licences nominatives et tirer pleinement parti des fonctionnalités des produits et services au sein du portail Admin Console.
 
### Comment cela fonctionne-t-il ?

Lorsque User Sync s’exécute, il récupère une liste d’utilisateurs à partir de l’annuaire Active Directory (ou autre source de données) de l’entreprise et la compare avec la liste présente dans Admin Console. Il appelle alors l’API Adobe User Management pour qu’Admin Console se synchronise avec l’annuaire de l’entreprise. Le flux de changement est entièrement à sens unique, les modifications apportées dans Admin Console n’étant pas répercutées dans l’annuaire.

L’outil permet à l’administrateur système de mapper les groupes d’utilisateurs figurant dans l’annuaire du client avec la configuration de produit et les groupes d’utilisateurs définis dans Admin Console.

Pour configurer User Sync, l’entreprise doit créer un ensemble d’identifiants comme elle le ferait pour utiliser l’API User Management.
 
### Comment l’obtenir ?

User Sync est un outil open source, distribué sous licence MIT et maintenu par Adobe. Il est disponible [ici](https://github.com/adobe-apiplatform/user-sync.py/releases/latest).


### La synchronisation des utilisateurs s’effectue-t-elle à la fois pour les serveurs Azure Active Directory et les serveurs sur site ?

La synchronisation des utilisateurs prend en charge les serveurs AD (Active Directory) hébergés sur Azure ou locaux, ainsi que tout autre serveur LDAP. Elle peut également être pilotée à partir d’un fichier local.

### Active Directory est-il traité comme un serveur LDAP ?

Oui, l’accès à Active Directory s’effectue via le protocole LDAP v3, entièrement pris en charge par Active Directory.

### L’outil User Sync place-t-il automatiquement tous mes groupes d’utilisateurs LDAP/AD dans Adobe Admin Console ?

Non, dans le cas où les groupes du côté de l’entreprise correspondent aux configurations d’accès aux produits souhaités, le fichier de configuration de User Sync peut être paramétré de manière à mapper les utilisateurs aux configurations de produits (CP) ou aux groupes d’utilisateurs dans les systèmes Adobe en fonction de leurs appartenances de groupe du côté de l’entreprise. Les groupes d’utilisateurs et les configurations de produits doivent être définis manuellement dans Adobe Admin Console.

 
### L’outil User Sync peut-il être utilisé pour gérer les appartenances liées aux groupes d’utilisateurs ou uniquement aux configurations de produits ?

Dans User Sync, vous pouvez faire appel à des groupes d’utilisateurs ou des configurations de produits pour procéder au mappage à partir des groupes d’annuaire, de façon à ce que des utilisateurs puissent être ajoutés aux groupes d’utilisateurs ou aux CP, ou bien en être supprimés. Toutefois, vous ne pouvez pas créer de groupes d’utilisateurs ou de configurations de produits, cette opération devant être réalisée dans Admin Console.

### Dans les exemples du manuel d’utilisation, je vois que chaque groupe de l’annuaire est mappé à un seul groupe Adobe. Est-il possible de mapper un groupe Active Directory à plusieurs configurations de produits ?

La plupart des exemples montrent un seul groupe d’utilisateurs ou une seule configuration de produit Adobe, mais le mappage peut se faire vers plusieurs éléments. Il vous suffit de dresser la liste de tous les groupes d’utilisateurs ou de toutes les configurations de produits, un par ligne, avec un trait d’union (« - ») initial (et la mise en retrait appropriée) devant chaque entrée pour respecter le format de liste YML.

### La limitation du serveur UMAPI peut-elle interférer avec le fonctionnement de l’outil User Sync ?

Non, User Sync gère la limitation et les nouvelles tentatives, de sorte que la limitation peut ralentir le processus global de synchronisation mais pas l’empêcher totalement et que User Sync peut mener à bien toutes les opérations.

Les systèmes Adobe se protègent des surcharges en surveillant le volume des demandes entrantes. Lorsque le volume commence à dépasser les limites, les demandes renvoient un en-tête « retry-after » indiquant le moment où la capacité sera à nouveau disponible. User Sync respecte ces en-têtes et attend le temps indiqué avant d’effectuer une nouvelle tentative. Vous trouverez plus d’informations, y compris des exemples de code, dans la [documentation de l’API User Management](https://www.adobe.io/apis/cloudplatform/usermanagement/docs/gettingstarted.html).
 
## Existe-t-il une liste locale des utilisateurs créés/mis à jour (du côté de User Sync) afin de réduire les appels au serveur Adobe ?

Lors de son exécution, l’outil User Sync interroge toujours les systèmes Adobe de gestion des utilisateurs pour obtenir des informations actualisées, à l’exception de ce qui suit. Il existe une option disponible dans User Sync version 2.2 ou ultérieure pour empêcher cette requête et l’envoi de mises à jour à Adobe sans tenir compte de l’état actuel des utilisateurs dans le système de gestion des utilisateurs d’Adobe. Si vous pouvez déterminer quels utilisateurs ont changé dans l’annuaire local et êtes certain que les autres utilisateurs n’ont pas été modifiés du côté Adobe, cette approche peut raccourcir le temps d’exécution (et l’utilisation du réseau) de vos travaux de synchronisation.
 
### L’outil User Sync est-il limité aux Federated ID ou est-il possible de créer n’importe quel type d’ID ?

User Sync prend en charge tous les types d’ID (Adobe ID, Enterprise ID et Federated ID).

### Une organisation Adobe peut avoir accès à des profils d’utilisateurs à partir de domaines détenus par d’autres organisations. User Sync est-il capable de gérer ce cas de figure ?

Oui, User Sync peut à la fois interroger et gérer les appartenances aux groupes d’utilisateurs et les droits d’accès aux produits dans les domaines que vous possédez ou auxquels vous avez accès. Toutefois, comme avec Admin Console, l’outil User Sync peut uniquement être utilisé pour créer et mettre à jour des comptes d’utilisateurs dans des domaines que vous possédez, et non des domaines détenus par d’autres organisations. Les utilisateurs de ces domaines peuvent obtenir l’accès aux produits, mais ils ne peuvent être ni modifiés, ni supprimés.

### Y a-t-il une fonction de mise à jour, ou simplement d’ajout/de retrait d’utilisateurs (Federated ID uniquement) ?

Pour tous les types d’ID (Adobe, Enterprise et Federated), User Sync prend en charge la mise à jour des appartenances aux groupes sous le contrôle de l’option --process-groups pour les Enterprise ID et Federated ID. User Sync prend en charge la mise à jour des champs de prénom, de nom et d’adresse e-mail sous le contrôle de l’option --update-user-inf. Lorsque la mise à jour du pays sera disponible dans Admin Console, elle le sera également via l’API User Management (UMAPI). En ce qui concerne les Federated ID dont le « paramètre d’identifiant utilisateur » correspond au « nom d’utilisateur », User Sync prend en charge la mise à jour du nom d’utilisateur, ainsi que des autres champs.

### L’outil User Sync est-il dédié à un système d’exploitation donné ?

User Sync est un projet Python open source que les utilisateurs peuvent développer pour le système d’exploitation de leur choix. Nous proposons des versions pour Windows, OS X, Ubuntu et CentOS 7.

### L’outil a-t-il été testé sur Python 3.5 ?

User Sync a été exécuté avec succès sur Python 3.x, mais la plupart de nos exécutions et de nos tests ont été réalisés sur Python 2.7. Il est donc possible que vous rencontriez des problèmes, et nous fournissons uniquement des versions sur Python 2.7. N’hésitez pas à signaler tout problème (et à fournir des correctifs) sur le site open source https://github.com/adobe-apiplatform/user-sync.py.

### En cas de modification de l’API (ajout d’un nouveau champ lors de la création d’utilisateurs, par exemple), comment la mise à jour est-elle appliquée à l’outil User Sync ?

User Sync est un projet open source. Les utilisateurs peuvent télécharger et générer les sources les plus récentes comme bon leur semble. Adobe publiera régulièrement de nouvelles versions. Les utilisateurs peuvent en être informés par notifications git. Lors de l’adoption d’une nouvelle version, seul le fichier PEX doit être mis à jour par l’utilisateur. En cas de modification de la configuration ou de la ligne de commande pour prendre en charge de nouvelles fonctionnalités, il est possible que les fichiers associés soient mis à jour pour pouvoir en tirer parti.

Notez également que User Sync est créé par-dessus umapi-client, qui est le seul module disposant d’une connaissance directe de l’API. Lorsque l’API change, umapi-client est toujours mis à jour pour la prendre en charge. Si les modifications de l’API prévoient des fonctionnalités supplémentaires liées à l’outil User Sync, alors celui-ci peut être mis à jour afin de proposer ces fonctionnalités.

### User Sync requiert-il une sorte de liste blanche avec les règles du pare-feu de l’ordinateur sur lequel il s’exécute ?

En règle générale, non. L’outil User Sync est uniquement un client réseau et il n’accepte pas les connexions entrantes. Les règles de pare-feu de l’ordinateur local pour les connexions entrantes ne sont donc pas pertinentes.

Toutefois, en tant que client réseau, User Sync requiert un accès sortant SSL (port 443) à travers les pare-feu réseau du client pour atteindre les serveurs Adobe. Les réseaux du client doivent également permettre à User Sync, s’il est configuré de cette façon, d’atteindre le serveur LDAP/AD du client, sur le port spécifié dans la configuration de User Sync (port 389 par défaut).

### User Sync fait-il partie de l’offre Adobe destinée aux clients EVIP ?
 
Oui, tous les clients Enterprise ont accès à l’API User Management et à l’outil User Sync, quel que soit leur programme d’achat (E-VIP, ETLA ou Enterprise Agreement).
 
### User Sync est-il adapté aux langues autres que l’anglais (prend-il au moins en charge la saisie de caractères codés sur deux octets) ?
 
Les versions antérieures de l’outil User Sync étaient erratiques dans leur prise en charge des données de caractères internationaux, même si elles fonctionnaient de manière assez fiable avec des sources de données codées par utf8. Depuis la version 2.2, User Sync est entièrement compatible avec Unicode et peut accepter des fichiers de configuration et des sources de données de tableur ou d’annuaire qui utilisent n’importe quel codage de caractères (avec, par défaut, une attente du codage utf8).
