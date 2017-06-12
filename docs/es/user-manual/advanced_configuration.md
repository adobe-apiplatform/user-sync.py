---
layout: default
lang: es
nav_link: Configuración avanzada
nav_level: 2
nav_order: 60
---


# Configuración avanzada

## En esta sección
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Sección anterior](usage_scenarios.md)  \| [Sección siguiente](deployment_best_practices.md)

---

User Sync requiere configuración adicional para sincronizar los datos de usuario en entornos con una estructura de datos más compleja.

- Cuando gestiona los usuarios de Adobe ID fuera de hojas de cálculo o del directorio de empresa, puede configurar la herramienta para que no los ignore.
- Si su empresa incluye varias organizaciones de Adobe, puede configurar la herramienta para añadir los usuarios de la organización en grupos definidos de otras organizaciones.
- Cuando los datos de usuario de empresa incluyen atributos y asignaciones personalizados, debe configurar la herramienta para poder reconocer dichas personalizaciones.
- Cuando desea utilizar inicios de sesión basados en nombre de usuario (en lugar de correo electrónico).
- Cuando desea gestionar algunas cuentas de usuario manualmente a través de Adobe Admin Console además de utilizar User Sync.

## Gestión de usuarios con Adobe ID

Hay una opción de configuración `exclude_identity_types` (en la sección `adobe_users` del archivo de configuración principal) que está configurada de forma predeterminada para ignorar a los usuarios de Adobe ID. Si desea que User Sync gestione algunos usuarios del tipo de Adobe ID, debe desactivar esta opción en el archivo de configuración quitando la entrada `adobeID` bajo `exclude_identity_types`.

Probablemente querrá configurar una tarea de sincronización separada específicamente para esos usuarios, posiblemente usando entradas de CSV en lugar de tomando entradas del directorio de empresa. Si lo hace, asegúrese de configurar esta tarea de sincronización para ignorar los usuarios de Enterprise ID y Federated ID, o tales usuarios probablemente se eliminarán del directorio.

La eliminación de usuarios de Adobe ID mediante User Sync podría no tener el efecto deseado:

* Si especifica que los usuarios de adobeID deben eliminarse de la organización, tendrá que volver a invitarlos
(y conseguir su nueva aceptación) si desea volver a añadirlos más adelante.
* Los administradores del sistema a menudo usan Adobe ID, por lo que la eliminación de los usuarios de Adobe ID puede quitar accidentalmente administradores del sistema (incluido usted mismo).

Una práctica mejor al gestionar usuarios de Adobe ID es simplemente añadirlos y gestionar sus miembros de grupo, pero nunca eliminarlos. Mediante la gestión de los miembros de grupo puede desactivar sus derechos sin necesidad de una nueva invitación, si más adelante desea volver a activarlos.

Recuerde que las cuentas de Adobe ID son propiedad del usuario final y no se pueden eliminar. Si aplica una acción de eliminación, User Sync sustituirá automáticamente la acción de quitar por la acción de eliminar.

También puede proteger usuarios específicos de Adobe ID contra la eliminación de User Sync utilizando los otros elementos de exclusión de la configuración. Consulte [Protección de cuentas específicas contra la eliminación de User Sync](#protección-de-cuentas-específicas-contra-la-eliminación-de-user-sync) para obtener más información.

## Acceso a usuarios de otras organizaciones

Una empresa grande puede incluir varias organizaciones de Adobe. Por ejemplo, supongamos que una empresa, Geometrixx, tiene varios departamentos, cada uno de los cuales tiene su propio ID de organización exclusivo y su propia Admin Console.

Si una organización utiliza Enterprise ID o Federated ID, debe reivindicar un dominio. En una empresa más pequeña, la sola organización reivindicaría el dominio **geometrixx.com**. No obstante, un dominio solo puede reivindicarlo una organización. Si varias organizaciones pertenecen a la misma empresa, algunas o todas ellas querrán incluir usuarios que pertenezcan al dominio empresarial.

En este caso, el administrador del sistema de cada uno de estos departamentos querría reivindicar este dominio para usar las identidades. Adobe Admin Console evita que varios departamentos reivindiquen el mismo dominio. Sin embargo, una vez lo ha reivindicado un departamento en concreto, el resto de departamentos pueden solicitar acceso al dominio de otro departamento. El primer departamento que reivindica el dominio es el *propietario* de ese dominio. Dicho departamento es responsable de aprobar las solicitudes de acceso del resto de departamentos, que, a continuación, pueden acceder a los usuarios del dominio sin requisitos de configuración especiales.

No es necesaria ninguna configuración especial para acceder a los usuarios de un dominio al que se le ha concedido acceso. Sin embargo, si desea añadir usuarios a grupos de usuarios o configuraciones de producto que se han definido en otras organizaciones, debe configurar User Sync para que pueda acceder a dichas organizaciones. La herramienta debe ser capaz de encontrar las credenciales de la organización que define los grupos y ser capaz de identificar los grupos como pertenecientes a una organización externa.


## Acceso a grupos de otras organizaciones

Para configurar el acceso a grupos de otras organizaciones, debe:

- Incluir archivos de configuración de la conexión de umapi adicionales.
- Indicar a User Sync la forma de acceder a estos archivos.
- Identificar los grupos que están definidos en otra organización.

### 1. Incluir archivos de configuración adicionales

Para cada organización adicional a los que necesite tener acceso, debe añadir un archivo de configuración que proporcione las credenciales de acceso para dicha organización. El archivo tiene el mismo formato que el archivo connector-umapi.yml. A cada organización adicional se hará referencia con un alias corto (que se definirá). Puede nombrar como quiera el archivo de configuración que tiene las credenciales de acceso para dicha organización. 

Supongamos, por ejemplo, que la organización adicional se denomina "Departamento 37". Su archivo de configuración podría llamarse: 

`department37-config.yml`

### 2. Configuración de User Sync para acceder a los archivos adicionales


La sección `adobe-users` del archivo de configuración principal debe incluir entradas que hagan referencia a estos archivos y asociar cada uno de ellos con el nombre corto de la organización. Por ejemplo:

```YAML
adobe-users:
  connectors:
    umapi:
      - connector-umapi.yml
      - org1: org1-config.yml
      - org2: org2-config.yml
      - d37: department37-config.yml  # d37 es el nombre corto del ejemplo anterior
```

Si se utilizan nombres de archivo no cualificados, los archivos de configuración deben estar en la misma carpeta que el archivo de configuración principal que hace referencia a ellos.

Tenga en cuenta que, al igual que su propio archivo de configuración de conexión, contienen información confidencial que debe ser protegida.

### 3. Identificación de grupos definidos externamente

Cuando especifica las asignaciones de grupo, puede asignar un grupo de directorio de empresa a un grupo de usuarios o configuración de producto de Adobe definidos en otra organización.

Para ello, utilice el identificador de la organización como prefijo del nombre del grupo. Únalos con "::". Por ejemplo:

```YAML
- directory_group: CCE Trustee Group
  adobe_groups:
    - "org1::Default Adobe Enterprise Support Program configuration"
    - "d37::Special Ops Group"
```

## Asignaciones y atributos personalizados

Es posible definir asignaciones de atributo de directorio personalizadas u otros valores en los campos utilizados para definir y actualizar los usuarios: nombre, apellido, dirección de correo electrónico, nombre de usuario, país y miembro de grupo. Normalmente, los atributos estándar del directorio se utilizan para obtener estos valores. Puede definir otros atributos para usarlos y especificar cómo deben calcularse los valores de los campos.

Para ello, debe configurar User Sync para reconocer las asignaciones no estándar entre los datos de usuario del directorio de empresa y los datos de usuario de Adobe. Las asignaciones no estándar incluyen:

- Valores de nombre de usuario, grupos, país o correo electrónico que se encuentran en o están basados en cualquier atributo no estándar del directorio.
- Los valores de nombre de usuario, grupos, país o correo electrónico deben calcularse a partir de la información del directorio.
- Grupos de usuarios o productos adicionales que deban añadirse o quitarse de la lista para algunos o todos los usuario.

El archivo de configuración debe especificar cualquier atributo personalizado que deba obtenerse del directorio. Además, debe especificar cualquier asignación personalizada para esos atributos y cualquier cálculo o acción que deba realizarse para sincronizar los valores. La acción personalizada se especifica mediante un pequeño bloque de código Python. Se proporcionan ejemplos y bloques estándar.

La configuración de los atributos personalizados y asignaciones van en un archivo de configuración independiente. Se hace referencia a ese archivo desde el archivo de configuración principal en la sección `directory_users`:

```
directory_users:
  extension: extenstions_config.yml  # referencia al archivo con información de asignación personalizada
```

La gestión de atributos personalizados se lleva a cabo para cada usuario, por lo que las personalizaciones se configuran en la subsección de cada usuario de la sección de extensiones del archivo de configuración principal de User Sync.

```
extensions:
  - context: per_user
    extended_attributes:
      - my-attribute-1
      - my-attribute-2
    extended_adobe_groups:
      - my-adobe-group-1
      - my-adobe-group-2
    after_mapping_hook: |
        pass # aquí va el código python personalizado
```

### Adición de atributos personalizados

De forma predeterminada, User Sync captura estos atributos estándar para cada usuario del sistema de directorio de empresa:

* `givenName`: se utiliza para el nombre de la parte de Adobe en el perfil
* `sn`: se utiliza para los apellidos de la parte de Adobe en el perfil
* `c`: se utiliza para el país de la parte de Adobe (código de país de dos letras)
* `mail`: se utiliza para el correo electrónico de la parte de Adobe
* `user`: se utiliza para el nombre de usuario de la parte de Adobe únicamente si se realiza Federated ID a través de nombre de usuario

Además, User Sync captura los nombres de atributos que aparecen en filtros de la configuración del conector LDAP.

Puede añadir atributos a este conjunto especificándolos en una clave `extended_attributes` en el archivo de configuración principal, como se muestra arriba. El valor de la clave `extended_attributes` es una lista YAML de cadenas en la que cada cadena indica el nombre de un atributo de usuario que se desea capturar. Por ejemplo:

```YAML
extensions:
  - context: per-user
    extended_attributes:
    - bc
    - subco
```

Este ejemplo indica a User Sync que capture los atributos `bc` y `subco` de cada usuario cargado.

Si uno o varios de los atributos especificados falta en la información de directorio de un usuario, se omiten los atributos. Las referencias de código a esos atributos devolverá el valor `None` de Python, un comportamiento normal que no es un error.

### Adición de asignaciones personalizadas

El código de asignación personalizada se configura con una sección de extensiones en el archivo de configuración principal (user sync). Dentro de las extensiones, una sección de cada usuario regirá el código personalizado que se invoca una vez por usuario.

El código especificado se ejecutaría una vez para cada usuario, después de que los atributos y miembros del grupo se hayan recuperado del sistema de directorio, pero antes de que se hayan generado acciones en Adobe.

```YAML
extensions:
  - context: per-user
    extended_attributes:
      - bc
      - subco
    extended_adobe_groups:
      - Acrobat_Sunday_Special
      - Group for Test 011 TCP
    after_mapping_hook: |
      bc = source_attributes['bc']
      subco = source_attributes['subco']
      if bc is not None:
          target_attributes['country'] = bc[0:2]
          target_groups.add(bc)
      if subco is not None:
          target_groups.add(subco)
      else:
          target_groups.add('Undefined subco')
```

En este ejemplo, dos atributos personalizados, bc y subco, se obtienen para cada usuario que se lee del directorio. El código personalizado procesa los datos para cada usuario:

- El código de país se toma de los 2 primeros caracteres del atributo bc.

    Esto muestra cómo se pueden utilizar los atributos de directorio personalizados para proporcionar valores para campos estándar que se envían a Adobe.

- El usuario se añade a grupos que provienen del atributo subco y del atributo bc (además de cualquier grupo asignado en la asignación de grupo en el archivo de configuración).

    Esto muestra cómo personalizar la lista de configuraciones de producto o grupo para que los usuarios se sincronicen en grupos adicionales.

Si el código de enlace hace referencia a grupos o configuraciones de producto de Adobe que ya no aparecen en la sección **groups** del archivo de configuración principal, se muestran en **extended_adobe_groups**. Esta lista amplía con eficacia el conjunto de grupos de Adobe que se consideran. Consulte [Gestión avanzada de grupos y productos](#gestión-avanzada-de-grupos-y-productos) para obtener más información.

### Conexión de variables de código

El código de `after_mapping_hook` está aislado del resto del programa User Sync excepto en las siguientes variables.

#### Valores de entrada

Las siguientes variables se pueden leer en el código personalizado. No se deben escribir y las escrituras en ellos no tienen ningún efecto; existen para expresar los datos del directorio de origen del usuario.

* `source_attributes`: un diccionario de cada usuario de los atributos de usuario obtenidos del sistema de directorio. Técnicamente, siendo un diccionario de Python, este valor es mutable, pero el cambio desde el código personalizado no tiene ningún efecto.

* `source_groups`: un conjunto congelado de grupos de directorio encontrados para un usuario específico mientras se atraviesan los grupos de directorio configurados.

#### Valores de entrada/salida

Las siguientes variables se pueden leer y escribir con el código personalizado. Provienen del transporte de los datos establecidos por el atributo predeterminado y de operaciones de asignación de grupo en el usuario actual del directorio, y se pueden escribir con el fin de modificar las acciones realizadas en el correspondiente usuario de Adobe.

* `target_attributes`: un diccionario de Python por usuario cuyas claves son los atributos de la parte de Adobe que se van a definir. Cambiar un valor en este diccionario cambiará el valor escrito en la parte de Adobe. Dado que Adobe predefine un conjunto fijo de atributos, la adición de una clave a este diccionario no tiene ningún efecto. Las claves de este diccionario son:
    * `firstName` - se omite para AdobeID y se utiliza en el resto de casos
    * `lastName` - se omite para AdobeID y se utiliza en el resto de casos
    * `email` - se utiliza en todas partes
    * `country` - se omite para AdobeID y se utiliza en el resto de casos
    * `username` - se omite para todos excepto Federated ID
      [configurado con inicio de sesión basado en el nombre de usuario](https://helpx.adobe.com/es/enterprise/help/configure-sso.html)
    * `domain` - se omite para todos excepto Federated ID [configurado con inicio de sesión basado en el nombre de usuario](https://helpx.adobe.com/es/enterprise/help/configure-sso.html)
* `target_groups`: un conjunto de Python de cada usuario que recopila los grupos de usuarios y configuraciones de productos del lado de Adobe a los que se añade el usuario cuando se especifica `process-groups` para la ejecución de sincronización. Cada valor es un conjunto de nombres. El conjunto se inicializa aplicando las asignaciones de grupo en el archivo de configuración principal y los cambios realizados en este conjunto (adiciones o eliminaciones) cambiarán el conjunto de grupos que se aplican al usuario en la parte de Adobe.
* `hook_storage`: un diccionario de Python por usuario que está vacío la primera vez que se pasa a código personalizado y que persiste en todas las llamadas. El código personalizado puede almacenar datos privados en este diccionario. Si utiliza archivos de script externos, es un lugar adecuado para almacenar los objetos de código creados compilando estos archivos.
* `logger`: un objeto de tipo `logging.logger` al que se da salida en la consola o el registro de archivos (según la configuración de registro).

## Gestión avanzada de grupos y productos

La sección **group** del archivo de configuración principal define una asignación de grupos de directorio a grupos de usuarios y configuraciones de producto de Adobe.

- En la parte del directorio de empresa, User Sync selecciona un conjunto de usuarios del directorio de empresa, en función de la consulta LDAP, el parámetro de línea de comandos `users` y el filtro de usuario, y examina estos usuarios para ver si están en alguno de los grupos de directorio asignados. Si están, User Sync utiliza la asignación de grupo para determinar a qué grupos de Adobe se deben añadir los usuarios.
- En la parte de Adobe, User Sync examina los miembros de los grupos asignados y las configuraciones de producto. Si algún usuario de esos grupos
_no_ está en el conjunto de usuarios de directorio seleccionado, User Sync elimina ese usuario del grupo. Este suele ser el comportamiento deseado porque, por ejemplo, si un usuario se encuentra en la configuración de producto de Adobe Photoshop y se elimina del directorio de empresa, se debe esperar que se eliminarán del grupo de manera que ya no se les asigne una licencia.

![Figure 4: Ejemplo de asignación de grupo](media/group-mapping.png)

Este flujo de trabajo puede presentar dificultades si desea dividir el proceso de sincronización en varias ejecuciones para reducir el número de usuarios de directorio consultados cada vez. Por ejemplo, podría hacer una ejecución para usuarios que comienzan con A-M y otra para los usuarios que comienzan con N-Z. Al hacer esto, cada ejecución debe dirigirse a grupos de usuarios y configuraciones de producto de Adobe diferentes. De lo contrario, la ejecución para A-M quitaría usuarios de grupos asignados que están en el conjunto de N-Z.

Para realizar esta configuración, utilice Admin Console para crear grupos de usuarios para cada subconjunto de usuarios (por ejemplo, **photoshop_A_M** y
**photoshop_N_Z**), y añada cada uno de los grupos de usuarios por separado a la configuración de producto (por ejemplo,  **photoshop_config**). En la configuración de User Sync, a continuación se asignan solo los grupos de usuarios, no las configuraciones de producto. Cada trabajo de sincronización está dirigido a un grupo de usuarios en su asignación de grupo. Actualiza los miembros del grupo de usuarios, lo que indirectamente actualiza los miembros de la configuración de producto.

## Eliminación de asignaciones de grupo

Puede producirse confusión al eliminar un grupo asignado. Digamos que un grupo de directorio, `acrobat_users`, está asignado al grupo de Adobe `Acrobat` y ya no desea asignar el grupo a `Acrobat` por lo que quita la entrada. El resultado es que todos los usuarios quedan en el grupo `Acrobat` porque `Acrobat` ya no es un grupo asignado, de modo que user sync lo deja como está. No se produce la eliminación de todos los usuarios de `Acrobat`, como cabría esperar.

Si desea también que los usuarios se eliminen del grupo `Acrobat`, puede eliminarlos manualmente mediante Admin Console o puede dejar la entrada (al menos temporalmente) en la asignación de grupo en el archivo de configuración, pero cambiar el grupo de directorio por un nombre que sepa que no existe en el directorio, como `no_directory_group`. La siguiente ejecución de sincronización notará que hay usuarios en el grupo de Adobe que no se encuentran en el grupo del directorio y los moverá todos. Una vez que esto ha ocurrido, puede eliminar toda la asignación del archivo de configuración.

## Trabajo con inicio de sesión basado en nombre de usuario

En Adobe Admin Console, puede configurar un dominio federado para utilizar los nombres de inicio de sesión de usuario basado en el correo electrónico o el inicio de sesión basado en el nombre de usuario (es decir, no basado en el correo electrónico). El inicio de sesión basado en el nombre de usuario se puede utilizar cuando se espera que las direcciones de correo electrónico cambien con frecuencia o la organización no permite el uso de direcciones de correo electrónico para iniciar sesión. En último término, el uso del inicio de sesión basado en el nombre de usuario o basado en el correo electrónico depende de la estrategia de identidad general de la empresa.

Para configurar User Sync para trabajar con inicios de sesión de nombre de usuario, debe establecer varios elementos de configuración adicionales.

En el archivo `connector-ldap.yml`:

- Establezca el valor de `user_username_format` en un valor como '{attrname}' donde attrname nombra el atributo de directorio cuyo valor se va a utilizar para el nombre de usuario.
- Establezca el valor de `user_domain_format` en un valor como '{attrname}' si el nombre de dominio proviene del atributo de directorio nombrado, o en un valor de cadena fijo como 'ejemplo.com'.

Al procesar el directorio, User Sync rellenará los valores de nombre de usuario y dominio a partir de esos campos (o valores).

Los valores dados para estos elementos de configuración pueden ser una combinación de caracteres de cadena y uno o más nombres de atributo entre corchetes "{}". Los caracteres fijos se combinan con el valor del atributo para formar la cadena utilizada al procesar el usuario.

Para los dominios que utilizan el inicio de sesión basado en el nombre de usuario, el elemento de configuración `user_username_format` no debe producir una dirección de correo electrónico; el carácter "@" no está permitido en nombres de usuario utilizados en el inicio de sesión basado en el nombre de usuario.

Si utiliza el inicio de sesión basado en el nombre de usuario, debe proporcionar igualmente una dirección de correo electrónico única para cada usuario y esa dirección de correo electrónico debe estar en un dominio reivindicado por la empresa y de su propiedad. User Sync no añadirá un usuario a la organización de Adobe sin una dirección de correo electrónico.

## Protección de cuentas específicas contra la eliminación de User Sync

Si realiza la creación y eliminación de cuentas a través de User Sync y desea crear manualmente algunas cuentas, podría necesitar esta función para evitar que User Sync elimine las cuentas creadas de forma manual.

En la sección `adobe_users` del archivo de configuración principal que puede incluir las siguientes entradas:

```YAML
adobe_users:
  exclude_adobe_groups: 
      - special_users       # User Sync no eliminará ni cambiará las cuentas de Adobe del grupo con nombre
  exclude_users:
      - ".*@example.com"    # User Sync conservará los usuarios cuyo nombre coincida con el patrón 
      - another@example.com # Puede tener más de un patrón
  exclude_identity_types:
      - adobeID             # Hace que User Sync no elimine las cuentas que son Adobe ID
      - enterpriseID
      - federatedID         # No las tendría todas puesto que se excluiría a todo el mundo  
```

Se trata de elementos de configuración opcionales. Identifican cuentas individuales o grupos de cuentas y las cuentas identificadas están protegidas contra la eliminación de User Sync. Estas cuentas pueden aun así añadirse o quitarse de los grupos de usuarios o configuraciones de producto en función de las entradas de asignación de grupo y la opción de línea de comandos `--process-groups`. 

Si desea evitar que User Sync elimine estas cuentas de los grupos, póngalas solo en grupos que no estén bajo el control de User Sync, es decir, en grupos que no estén nombrados en la asignación de grupo del archivo de configuración.

- `exclude_adobe_groups`: los valores de este elemento de configuración son una lista de cadenas que nombran los grupos de usuarios de Adobe o PC. Todos los usuarios de cualquiera de estos grupos se conservarán y nunca se eliminarán como usuarios solo de Adobe.
- `exclude_users`: los valores de este elemento de configuración son una lista de cadenas que son patrones que pueden coincidir con nombres de usuario de Adobe. Los usuarios coincidentes se conservarán y nunca se eliminarán como usuarios solo de Adobe.
- `exclude_identity_types`: los valores de este elemento de configuración son una lista de cadenas que pueden ser "adobeID", "enterpriseID" y "federatedID". Esto hace que cualquier cuenta que sea de los tipos enumerados se conserve y nunca se elimine como usuario solo de Adobe.


## Trabajo con grupos de directorio anidados de Active Directory

Nota: El enfoque originalmente definido en esta sección no funciona demasiado. Tendrá que esperar a una versión futura con los errores corregidos.

Si los grupos de directorio están estructurados de forma anidada para que los usuarios no se encuentren en un grupo de directorio con nombre simple, tendrá que ejecutar consultas LDAP más complejas para enumerar la lista de usuarios. Por ejemplo, puede tener una estructura de anidación de grupos parecida a esta:


    All_Divisions
		Blue_Division
		       User1@example.com
		       User2@example.com
		Green_Division
		       User3@example.com
		       User4@example.com

Una versión futura de User Sync será compatible con esto de manera transparente.


---

[Sección anterior](usage_scenarios.md)  \| [Sección siguiente](deployment_best_practices.md)

