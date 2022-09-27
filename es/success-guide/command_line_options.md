---
layout: default
lang: es
title: Línea de comandos
nav_link: Línea de comandos
nav_level: 2
nav_order: 310
parent: success-guide
page_id: command-line-options
---

# Elegir las opciones definitivas de la línea de comandos

[Sección anterior](monitoring.md) \| [Regresar al contenido](index.md) \|  [Sección siguiente](scheduling.md)

La línea de comandos de User Sync selecciona el conjunto de los usuarios que se procesará, especifica si debe gestionarse el abono de la PC y el grupo de usuarios, precisa cómo debe manejarse la eliminación de cuentas e indica algunas opciones adicionales.

## Usuarios


| Opción de la línea de comandos de los usuarios  | Utilícela cuando           |
| ------------- |:-------------| 
|   `--users all` |    Se incluyan todos los usuarios que aparecen en el directorio. |
|   `--users group "g1,g2,g3"`  |    Los grupos de directorio designados se usen para formar la selección de usuarios. <br>Se incluyan los usuarios que son miembros de cualquiera de los grupos. |
|   `--users mapped`  |    Lo mismo que `--users group g1,g2,g3,...`, donde `g1,g2,g3,...` son todos los grupos de directorio especificados en la asignación de grupos de archivos de configuración.|
|   `--users file f`  |    El archivo f se lee para formar el conjunto seleccionado de usuarios. El directorio LDAP no se utiliza en este caso. |
|   `--user-filter pattern`    |  Pueden combinarse con las opciones anteriores para filtrar y reducir la selección de usuario. <br>'pattern' es una cadena en el formato de expresiones regulares de Python. <br>El nombre de usuario debe coincidir con el patrón con el fin de ser incluido. <br>Los patrones de escritura pueden ser una especie de arte. Consulte los siguientes ejemplos o consulte la Documentación de Python [aquí](https://docs.python.org/2/library/re.html). |


Si todos los usuarios que aparecen en el directorio deben sincronizarse con Adobe, utilice `--users all`. Si son solo algunos usuarios, puede limitar el conjunto modificando la consulta LDAP en el archivo de configuración 'connector-ldap.yml' (y utilizar `--users all`), o puede limitar los usuarios a aquellos que se encuentran en los grupos específicos (utilizando -- grupo de usuarios). Puede combinar cualquiera de estas opciones con un `--user-filter pattern` para limitar más el conjunto seleccionado de usuarios que se sincronizarán.

Si no utiliza un sistema de directorio, puede utilizar `--users file f` para seleccionar los usuarios de un archivo csv. Consulte el archivo de usuarios de ejemplo (`csv inputs - user and remove lists/users-file.csv`) para ver el formato. Los grupos que aparecen en los archivos csv son nombres que puede elegir. Se asignan a grupos de usuarios o configuraciones de productos de Adobe de la misma forma que con los grupos de directorio.

## Grupos

Si no gestiona licencias de productos con la sincronización, no tiene que especificar la asignación de grupos en el archivo de configuración y no es necesario que añada ningún parámetro de la línea de comandos para el procesamiento de los grupos.

Si gestiona licencias con User Sync, incluya la opción `--process-groups` en la línea de comandos.


## Eliminación de cuenta


Hay varias opciones de la línea de comandos que le permiten especificar la acción que se llevará a cabo cuando se encuentre una cuenta de Adobe con ninguna cuenta de directorio correspondiente (un usuario de “solo Adobe”).
Tenga en cuenta que solo los usuarios devueltos por la consulta del directorio y el filtro se considerarán como “existentes” en el directorio de la empresa. Estas opciones van de “ignorar completamente” a “eliminar completamente” con varias posibilidades entremedio.



| Opción de la línea de comandos       ...........| Utilícela cuando           |
| ------------- |:-------------| 
|   `--adobe-only-user-action exclude`                        |  No sea necesaria ninguna acción en las cuentas que existen solo en Adobe y que no tienen ninguna cuenta de directorio correspondiente. Los abonos del grupo de Adobe no se actualizan aunque `--process-groups` esté presente. |
|   `--adobe-only-user-action preserve`                        |  No se eliminen ni se supriman las cuentas que existen solo en Adobe y que no tienen ninguna cuenta de directorio correspondiente. Los abonos del grupo de Adobe se actualizan si `--process-groups` está presente. |
|   `--adobe-only-user-action remove-adobe-groups` |    La cuenta de Adobe permanece pero los abonos de licencias y grupos <br>se han eliminado. |
|   `--adobe-only-user-action remove`  |    La cuenta de Adobe permanece, pero se eliminan los abonos de licencias y grupos y los listados de la Admin Console de Adobe.   |
|   `--adobe-only-user-action delete`  |    Cuenta de Adobe que se va a eliminar: quítela de las configuraciones de producto de Adobe y los grupos de usuarios; se ha eliminado la cuenta y se ha liberado todo el almacenamiento y la configuración.|
|   `--adobe-only-user-action write-file f.csv`    |  No debe realizarse ninguna acción en la cuenta. Se ha escrito el nombre de usuario en el archivo para la acción posterior. |




## Otras opciones

`--test-mode`: hace que User Sync se ejecute en todos los procesamientos, incluidos la consulta del directorio y la llamada de las API de administración de usuarios de Adobe para procesar la solicitud, pero no se lleva a cabo ninguna acción real. No se ha creado, eliminado ni modificado ningún usuario.

`--update-user-info`: hace que User Sync compruebe los cambios en el nombre, los apellidos o la dirección de correo electrónico de los usuarios y realiza las actualizaciones a la información de Adobe si no coincide con la información del directorio. Si se especifica esta opción puede aumentar el tiempo de ejecución.


## Ejemplos

Algunos ejemplos:

`user-sync --users all --process-groups --adobe-only-user-action remove`

- Procese todos los usuarios en función de los ajustes de configuración, actualice el abono del grupo de Adobe y, si hay algún usuario de Adobe que no se encuentre en el directorio, elimínelo de Adobe y libere las licencias que pueda tener asignadas. La cuenta de Adobe no se eliminará de modo que la podrá añadir de nuevo o almacenar los activos recuperados.
    
`user-sync --users file users-file.csv --process-groups --adobe-only-user-action remove`

- El archivo “users-file.csv” se lee como la lista de usuarios principal. No se hace ningún intento para ponerse en contacto con un servicio de directorio como AD o LDAP en este caso. El abono del grupo de Adobe se actualiza según la información del archivo y se eliminan las cuentas de Adobe que no aparecen en el archivo (véase la definición de eliminar, arriba).

## Definición de la línea de comandos

Es posible que quiera realizar sus primeras series sin las opciones de eliminación.

&#9744;Coloque juntas las opciones de la línea de comandos que necesita para la ejecución de User Sync.


[Sección anterior](monitoring.md) \| [Regresar al contenido](index.md) \|  [Sección siguiente](scheduling.md)
