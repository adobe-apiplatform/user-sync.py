---
layout: default
lang: fr
title: Configuration du serveur
nav_link: Configuration du serveur
nav_level: 2
nav_order: 160
parent: success-guide
page_id: identify-server
---

# Identification et configuration du serveur sur lequel doit s’exécuter User Sync

[Section précédente](setup_adobeio.md) \| [Revenir au sommaire](index.md) \|  [Section suivante](install_sync.md)


User Sync peut être exécuté manuellement, mais la plupart des entreprises préféreront l’automatiser afin qu’il s’exécute automatiquement une ou plusieurs fois par jour.

Il doit être installé et exécuté sur un serveur qui :

  - Peut accéder à Adobe par le biais d’Internet
  - Peut accéder à votre service d’annuaire tel que LDAP ou AD
  - Est protégé et sécurisé (vos identifiants d’administrateur y seront stockés ou lus)
  - Est fiable et fonctionne en continu
  - A certaines fonctions de sauvegarde et de restauration
  - Peut idéalement envoyer des e-mails afin que les rapports puissent être envoyés par User Sync aux administrateurs

Il vous faudra voir avec votre service informatique pour identifier un serveur de ce type et obtenir les droits d’accès associés.
Les plates-formes Unix, OS X et Windows sont toutes prises en charge par User Sync.

&#9744; Allouez un serveur à l’exécution de l’outil User Sync. Notez que vous pouvez réaliser la configuration initiale et tester User Sync sur une autre machine, telle qu’un ordinateur portable ou de bureau, tant que celle-ci répond aux critères ci-dessus.

&#9744; Obtenez un identifiant pour cet ordinateur qui possède des droits suffisants pour installer et exécuter User Sync. Un compte sans privilèges peut généralement suffire.




[Section précédente](setup_adobeio.md) \| [Revenir au sommaire](index.md) \|  [Section suivante](install_sync.md)

