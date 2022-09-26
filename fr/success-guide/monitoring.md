---
layout: default
lang: fr
nav_link: Contrôle
nav_level: 2
nav_order: 300
parent: success-guide
page_id: monitoring
---

# Surveillance du processus User Sync

[Section précédente](test_run.md) \| [Revenir au sommaire](index.md) \| [Section suivante](command_line_options.md)

Si vous utilisez User Sync en continu, vous devez désigner une personne capable de surveiller et gérer le processus de l’outil. Vous pouvez également mettre en place un mécanisme de suivi automatisé pour voir plus facilement ce qui se passe et déterminer si des erreurs ont lieu.

Il existe plusieurs approches possibles pour la surveillance :

- Inspecter les fichiers journaux suite à l’exécution de l’outil User Sync
- Envoyer par e-mail le résumé du journal de la dernière exécution aux administrateurs, qui vérifient qu’il n’y a pas eu d’erreurs (ou contrôlent l’absence de livraison)
- Associer les fichiers journaux à un système de surveillance et configurer des notifications en cas d’erreur

Pour cette étape, vous devez désigner une personne chargée du fonctionnement de l’outil User Sync et déterminer la manière dont la surveillance sera mise en place.

&#9744; Identifiez la personne ou l’équipe responsable de la surveillance et assurez-vous qu’elle connaît le fonctionnement et le rôle de User Sync.

&#9744; Si vous disposez d’un système d’analyse de journaux et d’alerte, faites en sorte que le journal de l’outil User Sync soit envoyé à ce système et configurez des alertes si des erreurs ou des messages critiques apparaissent dans le journal. Vous pouvez également définir des alertes en présence de messages d’avertissement.

[Section précédente](test_run.md) \| [Revenir au sommaire](index.md) \| [Section suivante](command_line_options.md)
