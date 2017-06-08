---
layout: default
lang: es
nav_link: Parámetros de comandos
nav_level: 2
nav_order: 40
---


# Parámetros de comandos

---

[Sección anterior](configuring_user_sync_tool.md)  \| [Sección siguiente](usage_scenarios.md)

---
Una vez configurados los archivos de configuración, puede ejecutar la herramienta User Sync en la línea de comandos o un script. Para ejecutar la herramienta, ejecute el siguiente comando en un shell de comandos o desde un script:

`user-sync` \[ _optional parameters_ \]

La herramienta acepta parámetros opcionales que determinan su comportamiento específico en diferentes situaciones.


| Especificaciones de parámetros&nbsp;y&nbsp;argumentos&nbsp; | Descripción |
|------------------------------|------------------|
| `-h`<br />`--help` | Mostrar este mensaje de ayuda y salir. |
| `-v`<br />`--version` | Mostrar el número de versión del programa y salir. |
| `-t`<br />`--test-mode` | Ejecutar llamadas de acción de API en modo de prueba (no ejecuta cambios). Registra lo que se habría ejecutado. |
| `-c` _filename_<br />`--config-filename` _filename_ | La ruta de acceso completa al archivo de configuración principal, absoluta o relativa a la carpeta de trabajo. El nombre de archivo predeterminado es "user-sync-config.yml" |
| `--users` `all`<br />`--users` `file` _input_path_<br />`--users` `group` _grp1,grp2_<br />`--users` `mapped` | Especifique los usuarios que se seleccionarán para la sincronización. El valor predeterminado es `all`, es decir, todos los usuarios del directorio. Especificar `file` significa tomar las especificaciones de usuario de entrada del archivo CSV denominado por el argumento. Especificando `group` se interpreta el argumento como una lista separada por comas de los grupos del directorio de empresa y solo se seleccionan los usuarios de esos grupos. Especificar `mapped` es lo mismo que especificar `group` con todos los grupos que aparecen en la asignación de grupos en el archivo de configuración. Este es un caso muy común en el que solo se sincronizan los usuarios de los grupos asignados|
| `--user-filter` _regex\_pattern_ | Limite el conjunto de usuarios que se examinan para la sincronización a los que coincidan con un patrón especificado con una expresión regular. Consulte la [documentación de expresiones regulares de Python](https://docs.python.org/2/library/re.html) para obtener información sobre la construcción de expresiones regulares en Python. El nombre de usuario debe coincidir totalmente con la expresión regular|
| `--update-user-info` | Cuando se suministra, sincroniza la información de usuario. Si la información difiere entre el lado del directorio de empresa y el lado de Adobe, el lado de Adobe se actualiza para lograr que ambos coincidan. Esto incluye los campos firstname y lastname. |
| `--process-groups` | Cuando se suministra, sincroniza la información de pertenencia del grupo. Si la información de los grupos asignados difiere entre el lado del directorio de empresa y el lado de Adobe, la pertenencia a grupos se actualiza en el lado de Adobe para lograr que ambos coincidan. Esto incluye la eliminación de la pertenencia a grupos de los usuarios de Adobe que no aparece en el lado de directorio (a menos que la opción `--adobe-only-user-action exclude` esté seleccionada también) |
| `--adobe-only-user-action preserve`<br />`--adobe-only-user-action remove-adobe-groups`<br />`--adobe-only-user-action  remove`<br />`--adobe-only-user-action delete`<br /><br/>`--adobe-only-user-action  write-file`&nbsp;filename<br/><br/>`--adobe-only-user-action  exclude` | Cuando se suministra, si se encuentran cuentas de usuario en la parte de Adobe que no se encuentran en el directorio, realizar la acción indicada. <br/><br/>`preserve`: no se realiza ninguna acción relativa a la eliminación de la cuenta. Es el modo predeterminado. Aun así pueden producirse cambios de pertenencia a grupos si se ha especificado la opción `--process-groups`.<br/><br/>`remove-adobe-groups`: La cuenta se elimina de los grupos de usuarios y configuraciones de producto, liberando todas las licencias que tuvieran, pero queda como una cuenta de activa de la organización.<br><br/>`remove`: Además de remove-adobe-groups, la cuenta también se elimina de la organización, pero la cuenta del usuario, con sus activos asociados, se deja en el dominio y se puede volver a añadir a la organización si se desea.<br/><br/>`delete`: Además de la acción de eliminación, la cuenta se elimina si su dominio es propiedad de la organización.<br/><br/>`write-file`: No se realiza ninguna acción relativa a la eliminación de la cuenta. La lista de cuentas de usuario presente en la parte de Adobe pero no en el directorio se escribe en el archivo indicado. A continuación, puede pasar este archivo al argumento `--adobe-only-user-list` en una ejecución posterior. Aun así pueden producirse cambios de pertenencia a grupos si se ha especificado la opción `--process-groups`.<br/><br/>`exclude`: No se aplica ninguna actualización de ningún tipo a los usuarios que se encuentran solamente en la parte de Adobe. Esto se utiliza cuando se realizan actualizaciones de usuarios específicos a través de un archivo (--users file f) en el que solo los usuarios que necesitan actualizaciones explícitas se muestran en el archivo y los demás usuarios se deben dejar.<br/><br>Solo se aplicarán acciones permitidas. Las cuentas de tipo adobeID son propiedad del usuario por lo que la acción de eliminación tendrá un efecto equivalente a quitar. Lo mismo es válido para las cuentas de Adobe propiedad de otras organizaciones. |
| `adobe-only-user-list` _filename_ | Especifica un archivo desde el que se leerá una lista de usuarios. Esta lista se utiliza como la lista definitiva de cuentas de usuario "solo de Adobe" en las que se actuará. Una de las directrices `--adobe-only-user-action` también se deben especificar y su acción se aplicará a las cuentas de usuario de la lista. La opción `--users` no está permitida si esta opción está presente: pueden procesarse solo acciones de eliminación de cuentas. |
{: .bordertablestyle }

---

[Sección anterior](configuring_user_sync_tool.md)  \| [Sección siguiente](usage_scenarios.md)
