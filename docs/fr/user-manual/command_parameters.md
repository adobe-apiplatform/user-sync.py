---
layout: default
lang: fr
nav_link: Paramètres de commande
nav_level: 2
nav_order: 40
---


# Paramètres de commande

---

[Section précédente](configuring_user_sync_tool.md)  \| [Section suivante](usage_scenarios.md)

---
Une fois les fichiers de configuration définis, vous pouvez exécuter User Sync sur la ligne de commande ou dans un script. Pour lancer l’outil, exécutez la commande suivante dans un shell de commande ou à partir d’un script :

`user-sync` \[ _optional parameters_ \]

L’outil accepte des paramètres facultatifs qui déterminent son comportement spécifique dans différentes situations.


| Paramètres&nbsp;et&nbsp;définition&nbsp;des arguments | Description |
|------------------------------|------------------|
| `-h`<br />`--help` | Afficher ce message d’aide et quitter. |
| `-v`<br />`--version` | Afficher le numéro de version du programme et quitter. |
| `-t`<br />`--test-mode` | Exécuter les appels d’action d’API en mode test (sans procéder à de réelles modifications). Consigne dans le journal ce qui aurait été exécuté. |
| `-c` _filename_<br />`--config-filename` _filename_ | Chemin d’accès complet au fichier de configuration principal, absolu ou relatif par rapport au dossier de travail. Le nom de fichier par défaut est « user-sync-config.yml ». |
| `--users` `all`<br />`--users` `file` _input_path_<br />`--users` `group` _grp1,grp2_<br />`--users` `mapped` | Spécifier les utilisateurs à sélectionner pour la synchronisation. La valeur par défaut est `all` et signifie tous les utilisateurs figurant dans l’annuaire. La valeur `file` indique de prendre les spécifications d’utilisateurs en entrée dans le fichier CSV désigné par l’argument. La valeur `group` interprète l’argument comme une liste de groupes de l’annuaire d’entreprise délimités par des virgules. Seuls les utilisateurs figurant dans ces groupes sont sélectionnés. Spécifier `mapped` revient à spécifier `group` avec tous les groupes répertoriés dans le mappage des groupes au sein du fichier de configuration. Il arrive très souvent que seuls les utilisateurs figurant dans des groupes mappés doivent être synchronisés.|
| `--user-filter` _regex\_pattern_ | Limiter l’ensemble d’utilisateurs examinés pour la synchronisation à ceux correspondant à un motif spécifié par une expression régulière. Reportez-vous à la [documentation de Python sur les expressions régulières](https://docs.python.org/2/library/re.html) pour en savoir plus sur la construction d’expressions régulières en Python. Le nom d’utilisateur doit entièrement correspondre à l’expression régulière.|
| `--update-user-info` | Lorsqu’il est indiqué, ce paramètre synchronise les informations utilisateur. Si les informations diffèrent entre l’annuaire d’entreprise et les systèmes Adobe, ceux-ci sont mis à jour pour correspondre à l’annuaire. Cela inclut les champs firstname (prénom) et lastname (nom). |
| `--process-groups` | Lorsqu’il est indiqué, ce paramètre synchronise les informations sur les appartenances aux groupes. Si les appartenances définies dans les groupes mappés diffèrent entre l’annuaire d’entreprise et les systèmes Adobe, elles sont mises à jour côté Adobe pour correspondre à l’annuaire. Cela implique le retrait des appartenances aux groupes pour les utilisateurs Adobe qui ne figurent pas dans l’annuaire (sauf si l’option `--adobe-only-user-action exclude` est également sélectionnée). |
| `--adobe-only-user-action preserve`<br />`--adobe-only-user-action remove-adobe-groups`<br />`--adobe-only-user-action  remove`<br />`--adobe-only-user-action delete`<br /><br/>`--adobe-only-user-action  write-file`&nbsp;filename<br/><br/>`--adobe-only-user-action  exclude` | Lorsque ce paramètre est indiqué, si des comptes d’utilisateurs sont présents dans les systèmes Adobe mais absents de l’annuaire, prendre la mesure indiquée. <br/><br/>`preserve` : aucune mesure concernant la suppression de compte n’est prise. Il s’agit du comportement par défaut. Les appartenances aux groupes peuvent tout de même être modifiées si l’option `--process-groups` a été spécifiée.<br/><br/>`remove-adobe-groups` : le compte a été retiré des groupes d’utilisateurs et des configurations de produits, ce qui libère toute licence qu’il pouvait détenir, mais il reste un compte actif dans l’organisation.<br><br/>`remove` : outre remove-adobe-groups, le compte est également retiré de l’organisation, mais le compte d’utilisateur, avec ses actifs associés, reste dans le domaine et peut à nouveau être ajouté à l’organisation si vous le souhaitez.<br/><br/>`delete` : outre l’action de retrait, le compte est supprimé si son domaine est détenu par l’organisation.<br/><br/>`write-file` : aucune mesure n’est prise concernant la suppression de compte. La liste des comptes d’utilisateurs présents dans les systèmes Adobe, mais absents de l’annuaire, est écrite dans le fichier indiqué. Vous pouvez ensuite transmettre ce fichier à l’argument `--adobe-only-user-list` lors d’une exécution ultérieure. Les appartenances aux groupes peuvent tout de même être modifiées si l’option `--process-groups` a été spécifiée.<br/><br/>`exclude` : aucune mise à jour d’aucune sorte n’est appliquée aux utilisateurs présents uniquement dans les systèmes Adobe. Ce paramètre est utilisé lorsque vous effectuez des mises à jour d’utilisateurs spécifiques par le biais d’un fichier (--users file f), où seuls les utilisateurs qui ont besoin de mises à jour explicites sont répertoriés dans le fichier et où tous les autres utilisateurs doivent rester inchangés.<br/><br>Seules les actions autorisées seront appliquées. Les comptes de type adobeID sont la propriété de l’utilisateur. L’action delete sera donc équivalente à remove. Il en va de même pour les comptes Adobe détenus par d’autres organisations. |
| `adobe-only-user-list` _filename_ | Spécifie un fichier à partir duquel une liste d’utilisateurs est lue. Cette liste est utilisée comme liste définitive des comptes d’utilisateurs « Adobe uniquement » sur lesquels effectuer une action. Une des directives `--adobe-only-user-action` doit également être spécifiée, et son action sera appliquée aux comptes d’utilisateurs figurant dans la liste. L’option `--users` n’est pas autorisée si cette option est présente : uniquement les actions de retrait de compte peuvent être traitées. |
{: .bordertablestyle }

---

[Section précédente](configuring_user_sync_tool.md)  \| [Section suivante](usage_scenarios.md)
