---
layout: default
lang: fr
title: Planification
nav_link: Planification
nav_level: 2
nav_order: 320
parent: success-guide
page_id: scheduling
---

# Configuration de l’exécution planifiée en continu de l’outil User Sync


[Section précédente](command_line_options.md) \| [Revenir au sommaire](index.md) 

## Configuration d’une exécution planifiée sous Windows

Tout d’abord, créez un fichier de commandes avec l’appel de user-sync transmis pour effectuer une analyse de façon à extraire les entrées de journal appropriées pour un résumé. Pour ce faire, créez le fichier run_sync.bat comme dans l’exemple ci-dessous :

	cd user-sync-directory
	python user-sync.pex --users file example.users-file.csv --process-groups | findstr /I "==== ----- WARNING ERROR CRITICAL Number" > temp.file.txt
	rem email the contents of temp.file.txt to the user sync administration
	your-mail-tool –send file temp.file.txt


Il n’existe aucun outil de ligne de commande standard pour envoyer des e-mails dans Windows, mais plusieurs outils sont disponibles dans le commerce.
Vous devez y ajouter vos options de ligne de commande spécifiques.

Ce code utilise le planificateur de tâches Windows pour exécuter l’outil User Sync tous les jours à 16 h :

	C:\> schtasks /create /tn "Adobe User Sync" /tr chemin_d’accès_au_fichier_bat/run_sync.bat /sc DAILY /st 16:00

Pour en savoir plus, consultez la documentation du planificateur de tâches Windows (help schtasks).

Notez que lors de la configuration de tâches planifiées, il arrive souvent que les commandes exécutées à partir de la ligne de commande ne fonctionnent pas dans la tâche planifiée, car le répertoire ou l’identifiant utilisateur actif est différent. Il est conseillé d’exécuter l’une des commandes de mode test (décrites dans la section « Réalisation d’un test d’exécution pour vérifier la configuration ») la première fois que vous tentez d’exécuter la tâche planifiée.


## Configuration d’une exécution planifiée sur les systèmes Unix

Tout d’abord, créez un script shell avec l’appel de user-sync transmis à une analyse de façon à extraire les entrées de journal appropriées pour un résumé. Pour ce faire, créez le fichier run_sync.sh comme dans l’exemple ci-dessous :

	cd user-sync-directory
	./user-sync --users file example.users-file.csv --process-groups |  grep "CRITICAL\\|WARNING\\|ERROR\\|=====\\|-----\\|number of\\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” 
    Your_admin_mailing_list@example.com


Vous devez ajouter vos options de ligne de commande spécifiques pour l’outil User Sync et l’adresse e-mail à laquelle le rapport doit être envoyé.

Cette entrée du crontab Unix exécute l’outil User Sync tous les jours à 4 h du matin : 

	0 4 * * *  chemin_d’accès_à_la_commande_shell_Sync/run_sync.sh 

Cron peut également être configuré pour envoyer les résultats par e-mail à un utilisateur précis ou à une liste de diffusion. Pour plus de détails, consultez la documentation de votre système Unix relative à cron.

Notez que lors de la configuration de tâches planifiées, il arrive souvent que les commandes exécutées à partir de la ligne de commande ne fonctionnent pas dans la tâche planifiée, car le répertoire ou l’identifiant utilisateur actif est différent. Il est conseillé d’exécuter l’une des commandes de mode test (décrites dans la section « Réalisation d’un test d’exécution pour vérifier la configuration ») la première fois que vous tentez d’exécuter la tâche planifiée.


[Section précédente](command_line_options.md) \| [Revenir au sommaire](index.md) 

