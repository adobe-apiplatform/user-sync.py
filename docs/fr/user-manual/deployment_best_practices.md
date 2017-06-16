---
layout: default
lang: fr
nav_link: Bonnes pratiques de déploiement
nav_level: 2
nav_order: 70
---


# Bonnes pratiques de déploiement

## Dans cette section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Section précédente](advanced_configuration.md)

---

User Sync est conçu pour fonctionner avec peu d’interaction humaine (voire aucune), lorsqu’il est configuré correctement. Vous pouvez utiliser un planificateur dans votre environnement pour exécuter l’outil à la fréquence qui vous convient.

- Les premières exécutions de l’outil User Sync peuvent prendre du temps, en fonction du nombre d’utilisateurs devant être ajoutés au portail Adobe Admin Console. Nous vous recommandons d’effectuer ces exécutions initiales manuellement, avant de configurer l’outil pour une exécution en tant que tâche planifiée, afin d’éviter d’avoir plusieurs instances actives en même temps.
- Les exécutions suivantes sont généralement plus rapides, car elles doivent uniquement mettre à jour les données utilisateur si nécessaire. La fréquence à laquelle vous choisissez d’exécuter User Sync dépend de la fréquence à laquelle votre annuaire d’entreprise change, et de la rapidité avec laquelle vous souhaitez que les changements soient répercutés dans les systèmes Adobe.
- Il est déconseillé d’exécuter User Sync plus que toutes les 2 heures.

## Recommandations de sécurité

Compte tenu du caractère des données figurant dans les fichiers journaux et de configuration, il convient de dédier un serveur à cette tâche et de le verrouiller selon les bonnes pratiques du secteur. Il est recommandé qu’un serveur qui se trouve derrière le pare-feu de l’entreprise soit provisionné pour cette application. Seuls les utilisateurs avec privilèges doivent être en mesure de se connecter à cet ordinateur. Un compte de service système aux privilèges limités doit être spécifiquement créé pour exécuter l’application et écrire les fichiers journaux sur le système.

L’application effectue des requêtes GET et POST de l’API User Management auprès d’un point de terminaison HTTPS. Elle construit des données JSON pour représenter les modifications qui doivent être écrites sur le portail Admin Console et associe les données dans le corps d’une requête POST envoyée à l’API User Management.

Pour protéger la disponibilité des systèmes d’identité des utilisateurs Adobe, l’API User Management impose des limites sur l’accès des clients aux données. Ces limites concernent le nombre d’appels qu’un client peut faire dans un intervalle de temps. Des limites globales s’appliquent également à l’accès par tous les clients au cours d’une période donnée. User Sync implémente une logique de type « back off and retry » (reculer et réessayer) pour empêcher le script de recontacter l’API User Management chaque fois que la limite est atteinte. Il est normal de voir dans la console des messages qui indiquent que le script est en pause pendant quelques instants avant de tenter une nouvelle exécution.

À compter de la version 2.1 de User Sync, deux techniques supplémentaires sont disponibles pour protéger les identifiants de connexion. La première utilise le référentiel d’identifiants de connexion pour stocker les valeurs correspondantes individuelles. La deuxième utilise un mécanisme que vous devez fournir pour stocker l’intégralité du fichier de configuration pour umapi et/ou ldap, qui inclut tous les identifiants de connexion requis. Ces méthodes sont décrites dans les deux sections suivantes.

### Stockage des identifiants de connexion dans l’espace de stockage du système d’exploitation

Pour configurer User Sync afin qu’il obtienne les identifiants de connexion à partir du référentiel correspondant du système d’exploitation Keyring Python, définissez les fichiers connector-umapi.yml et connector-ldap.yml comme suit :

connector-umapi.yml

	server:
	
	enterprise:
	  org_id: your org id
	  secure_api_key_key: umapi_api_key
	  secure_client_secret_key: umapi_client_secret
	  tech_acct: your tech account@techacct.adobe.com
	  secure_priv_key_data_key: umapi_private_key_data

Notez le remplacement de `api_key`, `client_secret` et `priv_key_path` par `secure_api_key_key`, `secure_client_secret_key` et `secure_priv_key_data_key`, respectivement. Ces nouvelles valeurs de configuration donnent les noms des clés à rechercher dans le service keychain utilisateur (ou le service équivalent sur d’autres plates-formes) pour récupérer les valeurs des identifiants de connexion. Dans cet exemple, les noms des clés des identifiants de connexion sont `umapi_api_key`, `umapi_client_secret` et `umapi_private_key_data`.

Le contenu du fichier de clé privée est utilisé en tant que valeur de `umapi_private_key_data` dans le référentiel d’identifiants de connexion.

Les valeurs des identifiants de connexion seront recherchées à partir des noms de clés spécifiés, et l’utilisateur correspond à la valeur org_id.


connector-ldap.yml

	username : votre nom d’utilisateur de compte ldap
	secure_password_key: ldap_password 
	host : ldap://nom du serveur ldap
	base_dn : DC=nom de domaine,DC=com

Le mot de passe d’accès à LDAP sera examiné en utilisant le nom de clé spécifié
(`ldap_password` dans cet exemple), et l’utilisateur correspond à la valeur de configuration de nom d’utilisateur spécifiée.

Les identifiants de connexion sont stockés dans le référentiel sécurisé sous-jacent du système d’exploitation. Le système de stockage spécifique dépend du système d’exploitation.

| OS | Référentiel d’identifiants de connexion |
|------------|--------------|
|Windows | Service d’archivage sécurisé des identifiants de connexion Windows |
| Mac OS X | Keychain |
| Linux | Service Secret Freedesktop ou KWallet |
{: .bordertablestyle }

Sous Linux, l’application de stockage sécurisé est installée et configurée par le fournisseur du système d’exploitation.

Les identifiants de connexion sont ajoutés à l’espace de stockage sécurisé du système d’exploitation, et reçoivent le nom d’utilisateur et l’ID que vous utiliserez pour spécifier les identifiants de connexion. Dans le cas des identifiants de connexion Umapi, le nom d’utilisateur est l’ID de l’organisation. Dans le cas des identifiants de connexion LDAP, le nom d’utilisateur est le nom d’utilisateur LDAP. Vous pouvez choisir l’identificateur que vous souhaitez pour les identifiants de connexion ; ils doivent correspondre aux données du référentiel d’identifiants de connexion ainsi qu’au nom utilisé dans le fichier de configuration. Vous trouverez des suggestions de valeurs pour les noms de clés dans les exemples ci-dessus.


### Stockage des fichiers d’identifiants de connexion dans des systèmes de gestion externes

Comme alternative au stockage des identifiants de connexion dans le référentiel local, il est possible d’intégrer User Sync à un autre système ou mécanisme de chiffrement. Pour prendre en charge de telles intégrations, il est possible de stocker l’ensemble des fichiers de configuration pour umapi et ldap à l’extérieur dans un autre système ou format.

Pour cela, il convient d’indiquer dans le fichier de configuration principal de User Sync une commande à exécuter, dont la sortie est utilisée comme les contenus du fichier de configuration umapi ou ldap. Vous devez fournir la commande qui récupère les informations de configuration et les transmet à la sortie standard au format YAML, avec un contenu correspondant au fichier de configuration.

Pour ce faire, utilisez les éléments suivants dans le fichier de configuration principal.


user-sync-config.yml (représentation partielle du fichier)

	adobe_users:
	   connectors:
	      # umapi: connector-umapi.yml   # Au lieu de cette référence au fichier, utilisez :
	      umapi: $(read_umapi_config_from_s3)
	
	directory_users:
	   connectors:
	      # ldap: connector-ldap.yml # Au lieu de cette référence au fichier, utilisez :
	      ldap: $(read_ldap_config_from_server)
 
Le format général des références aux commandes externes est

	$(command args)

Dans les exemples ci-dessus, nous supposons qu’il existe des commandes portant le nom `read_umapi_config_from_s3` et `read_ldap_config_from_server` que vous avez fournies.

Une interface de commande est lancée par User Sync qui exécute la commande. La sortie standard de la commande est capturée, et cette sortie est utilisée en tant que fichier de configuration umapi ou ldap.

La commande est exécutée avec l’annuaire de travail comme annuaire contenant le fichier de configuration.

Si la commande se termine anormalement, User Sync s’arrête avec une erreur.

La commande peut faire référence à un programme nouveau ou existant, ou à un script.

Remarque : Si vous utilisez cette technique pour le fichier connector-umapi.yml, vous devrez incorporer les données de clés privées dans connector-umapi-yml directement à l’aide de la clé priv_key_data et de la valeur de clé privée. Si vous utilisez priv_key_path et le nom du fichier contenant la clé privée, vous devrez également stocker la clé privée dans un endroit sécurisé et disposer d’une commande qui la récupère dans la référence au fichier.

## Exemples de tâches planifiées

Vous pouvez utiliser un planificateur fourni par votre système d’exploitation de façon à exécuter périodiquement User Sync, en fonction des exigences de votre entreprise. Ces exemples montrent comment configurer les planificateurs Unix et Windows.

Vous pouvez configurer un fichier de commandes qui exécute User Sync avec des paramètres spécifiques, puis extrait un résumé de journal et l’envoie par e-mail aux personnes chargées de suivre le processus de synchronisation. Ces exemples fonctionnent de manière optimale avec le niveau de journalisation log_level de la console défini sur INFO.

```YAML
logging:
  console_log_level: info
```

### Exécution avec analyse du journal sous Windows

L’exemple suivant montre la configuration d’un fichier de commandes `run_sync.bat` sous Windows.

```sh
python C:\\...\\user-sync.pex --users file users-file.csv --process-groups | findstr /I "WARNING ERROR CRITICAL ---- ==== Number" > temp.file.txt
rem email the contents of temp.file.txt to the user sync administration
sendmail -s “Adobe User Sync Report for today” UserSyncAdmins@example.com < temp.file.txt
```

*REMARQUE* : Bien que nous utilisions `sendmail` dans cet exemple, il n’existe aucun outil de ligne de commande standard pour l’envoi d’e-mail sous Windows. Plusieurs sont disponibles dans le commerce.

### Exécution avec analyse du journal sur les plates-formes Unix

L’exemple suivant montre la configuration d’un fichier shell `run_sync.sh` sous Linux ou MAC OS X :

```sh
user-sync --users file users-file.csv --process-groups | grep "CRITICAL\|WARNING\|ERROR\|=====\|-----\|number of\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” UserSyncAdmins@example.com
```

### Planification d’une tâche User Sync

#### Cron

Cette entrée du crontab Unix exécute l’outil User Sync tous les jours à 4 h du matin :

```text
0 4 * * * /path/to/run_sync.sh
```

Cron peut également être configuré pour envoyer les résultats par e-mail à un utilisateur précis ou à une liste de diffusion. Pour plus de détails, consultez la documentation de votre système relative à cron.

#### Planificateur de tâches Windows

Cette commande utilise le planificateur de tâches Windows pour exécuter l’outil User Sync tous les jours à 16 h :

```text
schtasks /create /tn "Adobe User Sync" /tr C:\path\to\run_sync.bat /sc DAILY /st 16:00
```

Pour en savoir plus, consultez la documentation du planificateur de tâches Windows (`help schtasks`).

Il existe également une interface graphique pour gérer les tâches planifiées Windows. Vous trouverez le planificateur de tâches dans le panneau de configuration d’administration Windows.

---

[Section précédente](advanced_configuration.md)
