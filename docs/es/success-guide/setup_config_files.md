---
layout: default
lang: es
nav_link: Archivos de configuración
nav_level: 2
nav_order: 280
---

# Configurar archivos de configuración


[Sección anterior](install_sync.md) \| [Regresar al contenido](index.md) \| [Sección siguiente](test_run.md)


Ahora viene el paso en el que se reúnen todos los datos. Necesitará:

- Los valores de acceso a la integración de Adobe.io en la consola de Adobe.io
- El archivo de clave privada
- Las credenciales de acceso al sistema de directorio y la información acerca de cómo se organizan los usuarios
- La decisión de si está gestionando el acceso a los productos a través de User Sync
  - Los nombres de configuración de producto y los nombres de grupo de usuario de cómo desea que se organicen las licencias en Adobe
  - Las configuraciones de producto y los grupos de usuarios ya tienen que haberse creado en la Admin Console de Adobe.

Asegúrese de utilizar un editor de texto, no un editor de procesamiento de textos.

Asegúrese de usar espacios, no fichas en los archivos .yml.


## Vamos a configurar los archivos de configuración

En los pasos anteriores, ha configurado un directorio de sistema de archivos del código Python y los archivos de configuración de la herramienta User Sync. Hay tres archivos de configuración para configurar ahora. Uno es para acceder al sistema de directorio, otro es para acceder a su organización de Adobe y el otro define la asignación de grupo y configura otras funciones de User Sync. 

### Archivo de configuración de acceso al directorio

Si ejecuta User Sync desde un archivo, puede omitir la configuración de connector-ldap.yml y, en lugar de eso, crear un archivo csv con la lista de usuario completa siguiendo el ejemplo de archivo “csv inputs - user and remove lists/1 users-file.csv”. Este archivo se encuentra en la descarga de example-configurations.tar.gz de la versión.

&#9744; Edite el archivo connector-ldap.yml. Este archivo tiene información de acceso al sistema de directorio. Introduzca los valores de nombre de usuario, contraseña, host y base_dn.

&#9744; Lea el resto del archivo para ver todo lo demás que podría especificarse que es posible que se aplique en su instalación. Por lo general, no se requiere nada más.

![](images/setup_config_directory.png)

Si desea realizar una consulta de LDAP no predeterminada para seleccionar el conjunto de usuarios deseado, está configurado en este archivo como parte del parámetro de configuración all\_users\_filter.


### Credenciales de UMAPI Adobe 

&#9744; Edite el connector-umapi.yml. Coloque la información de la integración de adobe.io que ha creado con anterioridad. Esto sería el org\_id, api\_key, client\_secret y el tech\_acct.

&#9744; Coloque el archivo de clave privado en la carpeta user_sync_tool. El elemento del archivo de configuración priv\_key\_path se define a continuación en el nombre de este archivo.

![](images/setup_config_umapi.png)

### Archivo de configuración de User Sync principal 

Edite el archivo user-sync-config.yml.

#### Código de país predeterminado

	directorio:
	  # (opcional) El código de país predeterminado que utilizar si el directorio no proporciona uno para el usuario [debe ser un código de dos letras ISO 3166, consulte https://en.wikipedia.org/wiki/ISO_3166-1]
	  #
	  # ejemplo:
	  # default_country_code: US


&#9744; Si el directorio no enumera un país para cada usuario, puede establecer aquí un país de forma predeterminada. Quite la “# ” desde la línea de código del país predeterminado, de modo que tiene este aspecto

	  default_country_code: US

y defina el código para el país correspondiente. No cambie el nivel de sangría de la línea.

El código de país es **OBLIGATORIO** para los Federated ID y se recomienda para los Enterprise ID. Si no se proporcionan para los Enterprise ID, se pedirá al usuario que elija un país cuando se registre por primera vez.

### Conectores

	  conectores:
	    # especifica las configuraciones para los conectores de directorio de la diferencia
	    # El formato es el nombre: valor, donde valor puede ser:
	    # un diccionario para la configuración actual, o 
	    # una cadena para el archivo que contiene la configuración, o
	    # una lista que contiene una mezcla de diccionarios y cadenas
	    #
	    # ejemplos:   
	    # ldap: example.connector-ldap.yml
	    # ldap: 
	    #   - host: LDAP_host_URL_goes_here
	    #     base_dn: base_DN_goes_here
	    #   - connector-ldap-credentials.yml

No tiene que realizar ningún cambio aquí. La línea de LDAP se utiliza si emplea un nombre no predeterminado para el archivo de configuración de acceso de directorio de LDAP.

#### Asignación de grupo

Si no gestiona las licencias a través de User Sync, puede omitir esta sección donde definimos la asignación de grupo.

Puede proporcionar las cuentas de usuario añadiéndolas a un grupo de directorio de empresa con las herramientas LDAP y Active Directory en lugar de la Admin Console de Adobe. A continuación, el archivo de configuración define una asignación de los grupos de directorio para las configuraciones de productos de Adobe. Si un usuario es un abonado de un grupo de directorio, User Sync las añadirá a la configuración de producto correspondiente Igual para la eliminación.


&#9744; Edición de la parte de la asignación de grupo del archivo. Para cada D de grupo de directorio que deba asignarse a una configuración de producto de Adobe o P de grupo de usuario, añada una entrada después de “grupos:” del formulario

	    - directory_group: D
	      adobe_groups: 
	        - P

Un ejemplo más realista es:

	  groups:
	    - directory_group: acrobat_pro_dc
	      adobe_groups: 
	        - Default Acrobat_Users
	    - directory_group: all_apps
	      adobe_groups:
	        - All Apps



![](images/setup_config_group_map.png)

#### Límites de usuario no coincidentes 

Los límites de eliminación evitan la eliminación accidental de la cuenta en caso de error de configuración o algún otro problema que provoque que User Sync no obtenga los datos apropiados del sistema de directorio.

&#9744; Si espera que el número de usuarios de directorio descienda en más de 200 entre las ejecuciones de User Sync, entonces tendrá que aumentar el valor `max_adobe_only_users`. Esta entrada del archivo de configuración evita la eliminación incontrolada en caso de error de configuración u otros problemas.

	límites:
	    max_adobe_only_users: 200      número de actualizaciones de cancelación si desaparece esta cantidad de usuarios de directorio



#### Eliminar Protección

Si desea realizar la creación y la eliminación de cuentas a través de User Sync y desea crear manualmente algunas cuentas, podría necesitar esta función para evitar que User Sync elimine las cuentas que ha creado de forma manual.

&#9744; Si desea utilizar esta función, agregue líneas como abajo al archivo de configuración en adobe_users. Para proteger a los usuarios en la Admin Console de las actualizaciones, cree un grupo de usuarios y coloque los usuarios protegidos en dicho grupo; a continuación, indique dicho grupo como excluido del procesamiento de User Sync. También puede indicar usuarios específicos o un patrón que coincida con los nombres de usuarios específicos para proteger a dichos usuarios. También puede proteger a los usuarios en función de su tipo de identidad. Por ejemplo, a menudo User Sync se utiliza únicamente para administrar los tipos de usuario Federated ID o Enterprise ID y puede excluir a los usuarios de tipo Adobe ID de la administración por parte de User Sync. Solo tiene que incluir los elementos de configuración para las exclusiones que desea utilizar.

```YAML
adobe_users:
  exclude_adobe_groups: 
    - administrators   # Denomina un grupo de usuarios o una configuración de producto de Adobe cuyos miembros no deben modificarse ni eliminarse por parte de User Sync
    - contractors      # Puede tener más de un grupo en una lista
  exclude_users:
    - ".*@example.com"
    - important_user@gmail.com
  exclude_identity_types:
    - adobeID          # Adobe ID, Enterprise ID o Federated ID
```


Arriba, los nombres de los administradores, los contratistas y el usuario son valores de ejemplo. Se utilizan los nombres de los grupos de usuarios, las configuraciones de producto o los usuarios de Adobe que ha creado.

`exclude_groups` define una lista de los grupos de usuarios, las configuraciones de productos o ambas cosas de Adobe. Los usuarios de Adobe que son miembros de los grupos que se enumeran no se eliminan, ni se actualizan, ni tampoco se cambia su abono de grupo.

`exclude_users` le ofrece una lista de patrones. Los usuarios de Adobe con nombres de usuario que coincidan (valor predeterminado que no distingue entre mayúsculas y minúsculas, a menos que el patrón especifique la distinción entre mayúsculas y minúsculas) con cualquiera de los patrones especificados no se eliminan, ni se actualizan, ni tampoco se cambia su abono de grupo.

`exclude_identity_types` le ofrece una lista de los tipos de identidad. Los usuarios de Adobe que tienen uno de estos tipos de identidad no se eliminan, ni se actualizan, ni tampoco se cambia su abono de grupo.

Tenga en cuenta que:

- Normalmente no utilizará las tres opciones de exclusión.

- Los usuarios del directorio todavía se crean en Adobe incluso si uno de los parámetros de exclusión excluye al usuario en Adobe desde las actualizaciones en las ejecuciones siguientes. Es decir, estos parámetros solo se aplican a los usuarios de Adobe que existen cuando el directorio de Adobe coincide con el directorio del cliente.

- Las cuentas que se habrían eliminado o actualizado pero que no lo han hecho debido a esta función se muestran como entradas del registro de nivel de “depuración”.

- En cualquier caso, las cuentas federadas que no se encuentran en el directorio o que están desactivadas en el directorio no pueden iniciar sesión (debido a que el inicio de sesión lo controla el proveedor de ID y el usuario ya no está en la lista), aunque la cuenta siga activa en Adobe.
- Es probable que quiera excluir las identidades de tipo Adobe ID debido a que normalmente no se enumeran en el directorio de la empresa.



#### Registros

User Sync genera entradas de registro que se imprimen a la salida estándar y también se escriben en un archivo de registro. El conjunto de registro de los parámetros de configuración controla los detalles de dónde y qué cantidad de información de registro se obtiene.

log\_to\_file activa o desactiva el registro del archivo. 

Los mensajes pueden tener un nivel de importancia sobre 5 y se puede elegir la menor importancia que se incluirá para el registro de archivo o el registro de salida estándar de la consola. Los valores predeterminados son para producir el registro de archivo y para incluir mensajes de nivel “info” o superior. Este es el ajuste recomendado.

&#9744; Revisa la configuración de registros y realice los cambios que desee. El nivel de registro recomendado es info (que es el valor predeterminado).

	logging:
	  # especifica si desea generar un archivo de registro
	  # 'True' o 'False'
	  log_to_file: True
	  # ruta de salida de registros
	  file_log_directory: logs
	  # Nivel de registro de archivo: puede ser “debug”,“info”,“warning”,“error” o “critical”. 
	  # Es en orden ascendente, es decir “debug“ &lt; “critical”.
	  file_log_level: debug
	  # Nivel de registro de consola: puede ser “debug”,“info”,“warning”,“error” o “critical”. 
	  # Es en orden ascendente, es decir “debug“ &lt; “critical”. El valor predeterminado es:
	  # console_log_level: debug




[Sección anterior](install_sync.md) \| [Regresar al contenido](index.md) \| [Sección siguiente](test_run.md)
