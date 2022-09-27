---
layout: default
lang: es
title: Escenarios de uso
nav_link: Escenarios de uso
nav_level: 2
nav_order: 50
parent: user-manual
page_id: usage
---

# Escenarios de uso

## En esta sección
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Sección anterior](command_parameters.md)  \| [Sección siguiente](advanced_configuration.md)

---

Hay varias formas de integrar la herramienta User Sync en los procesos de la empresa, como:

* **Actualizar los usuarios y miembros de grupos.** Sincronizar los usuarios y miembros de grupos agregando, actualizando o eliminando usuarios en el sistema de gestión de usuarios de Adobe. Este es el caso de uso más general y común.
* **Sincronizar solo la información de usuario.** Utilice este método si el acceso a los productos debe gestionarse con Admin Console.
* **Filtrar usuarios para sincronizar.** Puede optar por limitar la sincronización de la información de usuario a los usuarios de determinados grupos o limitar la sincronización a los usuarios que coincidan con un patrón determinado. También puede sincronizar con un archivo CSV en lugar de un sistema de directorio.
* **Actualizar los usuarios y miembros de grupo, pero gestionar las eliminaciones por separado.** Sincronizar los usuarios y miembros de grupo añadiendo y actualizando los usuarios, pero sin quitar usuarios en la ejecución inicial. En lugar de eso, mantener una lista de usuarios que se eliminarán y, a continuación, realizar las eliminaciones en una ejecución independiente.

Esta sección proporciona instrucciones detalladas de cada uno de estos escenarios.

## Actualizar los usuarios y miembros de grupos

Este es el tipo más típico y común de invocación. User Sync busca todos los cambios en la información de usuario y la información de miembros de grupo en la parte de la empresa. Sincroniza la parte de Adobe añadiendo, actualizando o eliminando usuarios y pertenencias a grupos de usuarios y configuraciones de producto.

De forma predeterminada, User Sync solo creará, eliminará o gestionará los miembros del grupo de los usuarios cuyo tipo de identidad sea Enterprise ID o Federated ID, ya que normalmente los usuarios de Adobe ID no se gestionan en el directorio. Consulte la [descripción que aparece a continuación](advanced_configuration.md#gestión-de-usuarios-con-adobe-id) en 
[Configuración avanzada](advanced_configuration.md#configuración-avanzada) si así es como funciona su organización.

En este ejemplo se presupone que el archivo de configuración, user-sync-config.yml, contiene una asignación de un grupo de directorio a una configuración de producto de Adobe que se denomina **Default Acrobat Pro DC configuration**.

### Comando

Esta invocación proporciona tanto los usuarios como los parámetros de grupos de proceso y permite la eliminación de usuarios con el parámetro `adobe-only-user-action remove`.

```sh
./user-sync –c user-sync-config.yml --users all --process-groups --adobe-only-user-action remove
```

### Salida de registro durante la operación

```text
2017-01-20 16:51:02 6840 INFO main - ========== Start Run ==========
2017-01-20 16:51:04 6840 INFO processor - ---------- Start Load from Directory -----------------------
2017-01-20 16:51:04 6840 INFO connector.ldap - Loading users...
2017-01-20 16:51:04 6840 INFO connector.ldap - Total users loaded: 4
2017-01-20 16:51:04 6840 INFO processor - ---------- End Load from Directory (Total time: 0:00:00) ---
2017-01-20 16:51:04 6840 INFO processor - ---------- Start Sync Dashboard ----------------------------
2017-01-20 16:51:05 6840 INFO processor - Adding user with user key: fed_ccewin4@ensemble-systems.com 2017-01-20 16:51:05 6840 INFO dashboard.owning.action - Added action: {"do": \[{"createFederatedID": {"lastname": "004", "country": "CA", "email": "fed_ccewin4@ensemble-systems.com", "firstname": "!Fed_CCE_win", "option": "ignoreIfAlreadyExists"}}, {"add": {"product": \["default acrobat pro dc configuration"\]}}\], "requestID": "action_5", "user": "fed_ccewin4@ensemble-systems.com"}
2017-01-20 16:51:05 6840 INFO processor - Syncing trustee org1... /v2/usermanagement/action/82C654BDB41957F64243BA308@AdobeOrg HTTP/1.1" 200 77
2017-01-20 16:51:07 6840 INFO processor - ---------- End Sync Dashboard (Total time: 0:00:03) --------
2017-01-20 16:51:07 6840 INFO main - ========== End Run (Total time: 0:00:05) ==========
```

### Ver resultado

Cuando la sincronización se lleva a cabo satisfactoriamente, se actualiza Adobe Admin Console. Después de que se ejecute este comando, la lista de usuarios y la lista de usuarios de configuración de producto de Admin Console muestra que se ha añadido un usuario con una identidad federada a la "Default Acrobat Pro DC configuration."

![Figure 3: Captura de pantalla de Admin Console](media/edit-product-config.png)

### Sincronizar solo usuarios

Si solo se suministra el parámetro `users` al comando, la acción busca cambios en la información de usuario en el directorio de empresa y actualiza la parte de Adobe con dichos cambios. Puede proporcionar argumentos al parámetro `users` que controlen los usuarios que se buscarán en la parte de la empresa.

Esta invocación no busca ni actualiza los cambios en los miembros de grupos. Si utiliza la herramienta de esta manera, se espera que controlará el acceso a los productos de Adobe actualizando los miembros de grupos de usuarios y configuración de producto en Adobe Admin Console.

También ignora los usuarios que están en la parte de Adobe, pero ya no están en la parte de directorio, y no realiza ninguna gestión de miembros de grupos de usuario o de configuración de producto.

```sh
./user-sync –c user-sync-config.yml --users all
```

### Filtrar usuarios para sincronizar

Tanto si opta por sincronizar la información de miembros de grupo como si no, puede proporcionar argumentos para el parámetro de usuarios que filtren los usuarios que se considerarán en la parte de directorio de empresa, o que obtengan información de los usuarios de un archivo CSV en vez de obtenerla directamente del directorio LDAP de la empresa.

### Sincronizar solo usuarios de grupos determinados

Esta acción solo busca cambios en la información de usuario para los usuarios de los grupos especificados. No busca en ningún otro usuario del directorio de empresa y no realiza ninguna gestión de grupos de usuario o configuración de producto.

```sh
./user-sync –c user-sync-config.yml --users groups "group1, group2, group3"
```

### Sincronizar solo usuarios de grupos asignados

Esta acción es la misma que especificar `--users groups "..."`, donde `...` equivale a todos los grupos que aparecen en la asignación de grupos del archivo de configuración.

```sh
./user-sync –c user-sync-config.yml --users mapped
```

### Sincronizar solo usuarios coincidentes

Esta acción solo busca cambios en la información de usuario para los usuarios cuyo ID de usuario coincide con un patrón. El patrón se especifica con una expresión regular de Python. En este ejemplo, también se actualizarán los miembros del grupo.

```sh
user-sync --users all --user-filter 'bill@forxampl.com' --process-groups
user-sync --users all --user-filter 'b.*@forxampl.com' --process-groups
```

### Sincronizar desde un archivo

Esta acción sincroniza a la información de usuario suministrada desde un archivo CSV, en lugar de buscar en el directorio de empresa. Se ofrece un ejemplo de un archivo de este tipo, users-file.csv, en la descarga de archivos de configuración de ejemplo de `examples/csv inputs - user and remove lists/`.

```sh
./user-sync --users file user_list.csv
```

La sincronización desde un archivo puede utilizarse en dos situaciones. En primer lugar, se pueden gestionar los usuarios de Adobe mediante una hoja de cálculo. La hoja de cálculo muestra una lista de usuarios, los grupos en los que están e información sobre ellos. En segundo lugar, si el directorio de empresa puede proporcionar notificaciones automáticas sobre actualizaciones, estas notificaciones se pueden colocar en un archivo csv y utilizarlas para guiar actualizaciones de User Sync. Consulte la siguiente sección para obtener más información sobre esta situación de uso.

### Actualizar los usuarios y miembros de grupo, pero gestionar las eliminaciones por separado

Si no proporciona el parámetro `--adobe-only-user-action`, puede sincronizar los usuarios y miembros de grupos sin quitar usuarios de la parte de Adobe.

Si desea gestionar las eliminaciones por separado, puede indicar a la herramienta que marque los usuarios que ya no existen en el directorio de empresa, pero todavía existen en la parte de Adobe. El parámetro `--adobe-only-user-action write-file exiting-users.csv` escribe la lista de los usuarios marcados para la eliminación en un archivo CSV.

Para realizar las eliminaciones en una ejecución separada, puede pasar el archivo generado por el parámetro `--adobe-only-user-action write-file` o pasar un archivo CSV de usuarios que ha generado por otros medios. Se ofrece un ejemplo de un archivo de este tipo, `remove-list.csv`, en el archivo example-configurations.tar.gz de la carpeta `csv inputs - user and remove lists`.

#### Añadir usuarios y generar una lista de usuarios para eliminar

Esta acción sincroniza todos los usuarios y también genera una lista de usuarios que ya no existen en el directorio, pero todavía existen en la parte de Adobe.

```sh
./user-sync --users all --adobe-only-user-action write-file users-to-remove.csv
```

#### Quitar usuarios de una lista separada

Esta acción toma un archivo CSV que contiene una lista de usuarios que se han marcado para la eliminación y elimina esos usuarios de la organización en la parte de Adobe. Normalmente, el archivo CSV es el que se ha generado en una ejecución anterior con el parámetro `--adobe-only-user-action write-file`.

Puede crear un archivo CSV de usuarios para eliminar por otros medios. Sin embargo, si su lista contiene usuarios que todavía existen en el directorio, esos usuarios se añadirán en la parte de Adobe en la siguiente acción de sincronización que añade usuarios.

```sh
./user-sync --adobe-only-user-list users-to-remove.csv --adobe-only-user-action remove
```

### Eliminar usuarios existentes en la parte de Adobe, pero no en el directorio

Esta invocación proporciona tanto los usuarios como los parámetros de grupos de proceso y permite la eliminación de cuentas de usuario con el parámetro adobe-only-user-action.

```sh
./user-sync --users all --process-groups --adobe-only-user-action delete
```

### Eliminar usuarios de una lista separada

Similar al ejemplo de eliminación de usuarios anterior, este elimina los usuarios que solo existen en la parte de Adobe, a partir de la lista generada en una ejecución anterior de User Sync.

```sh
./user-sync --adobe-only-user-list users-to-delete.csv --adobe-only-user-action delete
```

## Trabajo con notificaciones automáticas

Si el sistema de directorio puede generar notificaciones de actualizaciones, puede utilizar User Sync para procesar las actualizaciones de forma gradual. La técnica que se muestra en esta sección también puede utilizarse para procesar actualizaciones inmediatas en las que un administrador ha actualizado un usuario o un grupo de usuarios y quiere incluir solo esas actualizaciones inmediatamente en el sistema de gestión de usuarios de Adobe. Algunos scripts pueden ser necesarios para transformar la información procedente de la notificación automática en un csv adecuado para la introducción en User Sync y para separar las eliminaciones de otras actualizaciones, que deben tratarse por separado en User Sync.

Cree un archivo, digamos, `updated_users.csv` con el formato de actualización de usuarios ilustrado en el archivo de ejemplo `users-file.csv` de la carpeta `csv inputs - user and remove lists`. Se trata de un archivo csv básico con columnas para firstname, lastname, etc.

    firstname,lastname,email,country,groups,type,username,domain
    John,Smith,jsmith@example.com,US,"AdobeCC-All",enterpriseID
    Jane,Doe,jdoe@example.com,US,"AdobeCC-All",federatedID
 
Este archivo, a continuación, se proporciona a User Sync:

```sh
./user-sync --users file updated-users.csv --process-groups --update-users --adobe-only-user-action exclude
```

--adobe-only-user-action exclude hace que User Sync actualice solo los usuarios que se encuentran en el archivo updated-users.csv y omita todos los demás.

Las eliminaciones se procesan del mismo modo. Cree un archivo `deleted-users.csv` basado en el formato de `remove-list.csv` en la misma carpeta de ejemplo y ejecute User Sync:

```sh
./user-sync --adobe-only-user-list deleted-users.csv --adobe-only-user-action remove
```

Esto hará que se traten las eliminaciones en función de la notificación y no se realizarán otras acciones. Tenga en cuenta que `remove` podría sustituirse por una de las otras acciones en función de cómo se desee tratar los usuarios eliminados.

## Resumen de acciones

Al final de la invocación, se imprimirá un resumen de acciones en el registro (si el nivel es INFORMACIÓN o DEPURACIÓN). 
Este resumen proporciona estadísticas acumuladas durante la ejecución. 
Las estadísticas recopiladas incluyen:

- **Total number of Adobe users:** El número total de usuarios de Adobe en admin console
- **Number of Adobe users excluded:** El número de usuarios de Adobe que estaban excluidos de las operaciones mediante exclude_parameters
- **Total number of directory users:** El número total de usuarios leídos del archivo LDAP o CSV
- **Number of directory users selected:** El número de usuarios de directorio seleccionados mediante el parámetro user-filter
- **Number of Adobe users created:** El número de usuarios de Adobe creados durante esta ejecución
- **Number of Adobe users updated:** El número de usuarios de Adobe actualizados durante esta ejecución
- **Number of Adobe users removed:** El número de usuarios de Adobe eliminados de la organización en la parte de Adobe
- **Number of Adobe users deleted:** El número de usuarios de Adobe quitados de la organización y las cuentas de usuario Enterprise/Federated eliminadas de la parte de Adobe
- **Number of Adobe users with updated groups:** El número de usuarios de Adobe que se añaden a uno o varios grupos de usuarios
- **Number of Adobe users removed from mapped groups:** El número de usuarios de Adobe que se quitan de uno o varios grupos de usuarios
- **Number of Adobe users with no changes:** El número de usuarios de Adobe que no han cambiado durante esta ejecución

### Salida de resumen de acciones de muestra en el registro
```text
2017-03-22 21:37:44 21787 INFO processor - ------------- Action Summary -------------
2017-03-22 21:37:44 21787 INFO processor -   Total number of Adobe users: 50
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users excluded: 0
2017-03-22 21:37:44 21787 INFO processor -   Total number of directory users: 10
2017-03-22 21:37:44 21787 INFO processor -   Number of directory users selected: 10
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users created: 7
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users updated: 1
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users removed: 1
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users deleted: 0
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users with updated groups: 2
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users removed from mapped groups: 5
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users with no changes: 48
2017-03-22 21:37:44 21787 INFO processor - ------------------------------------------
```

---

[Sección anterior](command_parameters.md)  \| [Sección siguiente](advanced_configuration.md)

