---
weight: 180
title: Test d’exécution
type: docs
---

# Réalisation d’un test d’exécution pour vérifier la configuration

Pour appeler l’outil User Sync :

Fenêtres:      **python user-sync.pex ….**

Unix, OS X :     **./user-sync ….**


Essayez :

	./user-sync –v            Afficher la version
	./user-sync –h            Aide sur les arguments de ligne de commande

Essayez les deux commandes ci-dessus et vérifiez qu’elles fonctionnent. (Sous Windows, la commande diffère légèrement.)

![img](/user-sync.py/images/test_run_screen.png)

Ensuite, essayez une synchronisation limitée à un seul utilisateur et exécutée en mode test. Vous devez connaître le nom de certains utilisateurs figurant dans votre annuaire. Par exemple, pour l’utilisateur bart@example.com, essayez :

	./user-sync -t --users all --user-filter bart@example.com --adobe-only-user-action exclude

	./user-sync -t --users all --user-filter bart@example.com --process-groups --adobe-only-user-action exclude

La première commande ci-dessus synchronise uniquement l’utilisateur en question (en raison du filtre d’utilisateur), ce qui devrait entraîner une tentative de création de l’utilisateur. En raison de l’exécution en mode test (-t), User Sync tente uniquement de créer l’utilisateur, sans le créer réellement. L’option `--adobe-only-user-action exclude` empêche de mettre à jour les comptes utilisateurs qui existent déjà dans l’organisation Adobe.

La deuxième commande ci-dessus (avec l’option --process-groups) tente de créer l’utilisateur et de l’ajouter aux groupes qui sont mappés à partir de leurs groupes d’annuaire. Là encore, il s’agit du mode test donc aucune action n’est effectivement réalisée. S’il existe déjà des utilisateurs et que les groupes contiennent déjà des utilisateurs, User Sync peut tenter de les retirer. Si tel est le cas, ignorez le prochain test. En outre, si vous n’utilisez pas de groupes d’annuaire pour gérer l’accès aux produits, ignorez les tests contenant l’argument --process-groups.

Ensuite, essayez une synchronisation limitée à un seul utilisateur sans le mode test. Cela devrait réellement entraîner la création de l’utilisateur et son ajout à des groupes (s’ils sont mappés). 

	./user-sync --users all --user-filter bart@example.com --process-groups --adobe-only-user-action exclude

	./user-sync --users all --user-filter bart@example.com --process-groups --adobe-only-user-action exclude

Ensuite, vérifiez dans Adobe Admin Console si l’utilisateur apparaît et si les appartenances aux groupes ont été ajoutées.

Puis exécutez à nouveau la même commande. Normalement, User Sync ne tente pas de recréer l’utilisateur et de l’ajouter à nouveau aux groupes. Il doit détecter que l’utilisateur existe déjà et qu’il est membre du groupe d’utilisateurs ou de la configuration de produit, et donc ne rien faire.

Si tout fonctionne comme prévu, vous êtes prêt à effectuer une exécution complète (sans filtre d’utilisateur). Si votre annuaire ne comporte pas un très grand nombre d’utilisateurs, vous pouvez effectuer un test maintenant. Si vous avez plusieurs centaines d’utilisateurs, la synchronisation peut prendre un certain temps. Soyez donc prêt à laisser la commande s’exécuter pendant plusieurs heures. Prenez également connaissance des sections suivantes avant d’exécuter l’outil, dans le cas où il existe d’autres options de ligne de commande susceptibles de vous intéresser.
