---
layout: default
lang: es
nav_link: Prácticas recomendadas de implementación
nav_level: 2
nav_order: 70
---


# Prácticas recomendadas de implementación

## En esta sección
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Sección anterior](advanced_configuration.md)

---

La herramienta User Sync se ha diseñado para funcionar con poca o ninguna interacción humana, una vez configurada correctamente. Puede utilizar un programador en su entorno para ejecutar la herramienta con la frecuencia necesaria.

- La primera ejecuciones algunos de usuario sincronizar herramienta pueden tardar mucho tiempo, dependiendo de cuántos usuarios necesitan para su incorporación en Adobe Admin Console. Se recomienda realizar estas ejecuciones iniciales manualmente, antes de configurarlas para que se ejecuten como una tarea programada, con el fin de evitar tener varias instancias en ejecución.
- Las siguientes ejecuciones son normalmente más rápidas, ya que solo necesitan actualizar los datos de usuario necesarios. La frecuencia con que elija ejecutar User Sync variará en función de la frecuencia con que cambia el directorio de empresa, así como de la rapidez con que desea que los cambios aparezcan en la parte de Adobe.
- No se recomienda ejecutar User Sync más de una vez cada 2 horas.

## Recomendaciones de seguridad

Debido a la naturaleza de los datos de los archivos de configuración y de registro, un servidor debe estar dedicado a esta tarea y bloqueado con las mejores prácticas del sector. Se recomienda designar para esta aplicación un servidor que se encuentre detrás del firewall de la empresa. Solo los usuarios con privilegios han de poder conectarse a este equipo. Debe crear una cuenta de servicio de sistema con privilegios restringidos destinado específicamente a ejecutar la aplicación y escribir los archivos de registro en el sistema.

La aplicación hace peticiones GET y POST de la API de gestión de usuarios a un terminal HTTPS. Construye datos JSON para representar los cambios que deben escribirse en Admin Console y adjunta los datos en el cuerpo de una petición POST a la API de gestión de usuarios.

Para proteger la disponibilidad de los sistemas de identidad de usuario internos de Adobe, la API de gestión de usuarios impone límites en el acceso a los datos del cliente. Los límites se aplican al número de llamadas que puede hacer un cliente individual dentro de un intervalo de tiempo y los límites globales se aplican al acceso de todos los clientes dentro del período de tiempo. La herramienta User Sync implementa nuevamente y reintenta la lógica para evitar que el script afecte continuamente a la API de gestión de usuarios cuando se alcanza el límite de la tasa. Es normal ver mensajes en la consola indicando que el script ha estado en pausa por un breve período de tiempo antes de intentar ejecutarlo de nuevo.

A partir de User Sync 2.1, existen dos técnicas adicionales disponibles para proteger las credenciales. La primera utiliza el almacén de credenciales del sistema operativo para almacenar los valores de credenciales de configuración individuales. La segunda utiliza un mecanismo que debe proporcionarse para guardar el archivo de configuración completo para umapi y/o ldap que incluye todas las credenciales. Estas se describen con detalle en las secciones siguientes.

### Almacenar las credenciales en el almacenamiento de nivel de sistema operativo

Para configurar User Sync para extraer las credenciales del almacén de credenciales del sistema operativo Python Keyring, configure los archivos connector-umapi.yml y connector-ldap.yml como se indica a continuación:

connector-umapi.yml

	server:
	
	enterprise:
	  org_id: your org id
	  secure_api_key_key: umapi_api_key
	  secure_client_secret_key: umapi_client_secret
	  tech_acct: your tech account@techacct.adobe.com
	  secure_priv_key_data_key: umapi_private_key_data

Observe el cambio de `api_key`, `client_secret` y `priv_key_path` por `secure_api_key_key`, `secure_client_secret_key` y `secure_priv_key_data_key`, respectivamente. Estos valores de configuración alternativos dan los nombres clave que deben consultarse en la cadena de llave de usuario (o el servicio equivalente en otras plataformas) para recuperar los valores de credenciales reales. En este ejemplo, los nombres de clave de credenciales son `umapi_api_key`, `umapi_client_secret` y `umapi_private_key_data`.

El contenido del archivo de clave privada se utiliza como valor de `umapi_private_key_data` en el almacén de credenciales.

Los valores de credenciales se consultarán utilizando los nombres de clave especificados, siendo el usuario el valor org_id.


connector-ldap.yml

	username: "el nombre de usuario de cuenta ldap"
	secure_password_key: ldap_password 
	host: "ldap://nombre del servidor ldap"
	base_dn: "DC=nombre de dominio,DC=com"

La contraseña de acceso de LDAP se consultará utilizando el nombre de clave especificado
(`ldap_password` en este ejemplo), siendo el usuario el valor de configuración de nombre de usuario especificado.

Las credenciales se almacenan en el almacén seguro del sistema operativo subyacente. El sistema de almacenamiento específico depende del sistema operativo.

| OS | Almacén de credenciales |
|------------|--------------|
|Windows | Depósito de credenciales de Windows |
| Mac OS X | Cadena de llave |
| Linux | Servicio secreto de Freedesktop o KWallet |
{: .bordertablestyle }

En Linux, la aplicación de almacenamiento seguro la habría instalado y configurado el proveedor del sistema operativo.

Las credenciales se añaden al almacenamiento seguro del sistema operativo y con el nombre de usuario e identificador de credenciales que se utilizarán para especificar las credenciales. Para credenciales de umapi, el nombre de usuario es el identificador de la organización. Para las credenciales de contraseña de LDAP, el nombre de usuario es el nombre de usuario de LDAP. Puede elegir cualquier identificador que desee para las credenciales específicas; deben coincidir con lo que se encuentra en el almacén de credenciales y el nombre utilizado en el archivo de configuración. Los valores sugeridos para los nombres de clave se muestran en el ejemplo anterior.


### Almacenar archivos de credenciales en sistemas de administración externos

Como alternativa al almacenamiento de las credenciales en el almacén de credenciales local, es posible integrar User Sync con otro sistema o mecanismo de cifrado. Para ofrecer compatibilidad con tales integraciones, es posible almacenar los archivos de configuración completos para umapi y ldap externamente en algún otro sistema o formato.

Esto se consigue especificando, en el archivo de configuración principal de User Sync, un comando que se ejecutará y cuya salida se utiliza como contenido del archivo de configuración umapi o ldap. Deberá proporcionar el comando que recupera la información de configuración y la envía a la salida estándar en formato yaml, coincidiendo con lo que habría contenido el archivo de configuración.

Para establecer esta configuración, utilice los siguientes elementos en el archivo de configuración principal.


user-sync-config.yml (que muestra solo el archivo parcial)

	adobe_users:
	   connectors:
	      # umapi: connector-umapi.yml   # en lugar de esta referencia del archivo, utilice:
	      umapi: $(read_umapi_config_from_s3)
	
	directory_users:
	   connectors:
	      # ldap: connector-ldap.yml # en lugar de esta referencia del archivo, utilice:
	      ldap: $(read_ldap_config_from_server)
 
El formato general para referencias de comando externas es

	$(command args)

Los ejemplos anteriores presuponen que hay un comando con el nombre `read_umapi_config_from_s3` y `read_ldap_config_from_server` que se ha suministrado.

User Sync abre un shell de comandos que ejecuta el comando. La salida estándar del comando es capturada y esa salida se utiliza como archivo de configuración umapi o ldap.

El comando se ejecuta con el directorio de trabajo como directorio que contiene el archivo de configuración.

Si el comando finaliza de forma anómala, User Sync se cerrará con un error.

El comando puede hacer referencia a un programa nuevo o existente o un script.

Nota: si utiliza esta técnica para el archivo connector-umapi.yml, deberá integrar los datos de clave privada en conector-umapi-yml directamente utilizando la clave priv_key_data y el valor de clave privada. Si utiliza priv_key_path y el nombre del archivo que contiene la clave privada, también deberá almacenar la clave privada en algún lugar seguro y crear un comando que la recupere en la referencia del archivo.

## Ejemplos de la tarea programada

Puede utilizar un programador suministrado por el sistema operativo para ejecutar la herramienta User Sync periódicamente, según los requisitos de la empresa. Estos ejemplos ilustran cómo puede configurar los programadores Unix y Windows.

Podría querer configurar un archivo de comandos que ejecutara UserSync con parámetros específicos y luego extrajera un resumen de registro y lo enviara por correo electrónico a los encargados de supervisar el proceso de sincronización. Estos ejemplos funcionan mejor con el nivel de registro de la consola definidos en INFO.

```YAML
logging:
  console_log_level: info
```

### Ejecutar con análisis de registro en Windows

El siguiente ejemplo muestra cómo configurar un archivo por lotes `run_sync.bat` en Windows.

```sh
python C:\\...\\user-sync.pex --users file users-file.csv --process-groups | findstr /I "WARNING ERROR CRITICAL ---- ==== Number" > temp.file.txt
rem email the contents of temp.file.txt to the user sync administration
sendmail -s “Adobe User Sync Report for today” UserSyncAdmins@example.com < temp.file.txt
```

*NOTA*: aunque se muestra el uso de `sendmail` en este ejemplo, no hay ninguna herramienta de línea de comandos estándar de correo electrónico en Windows. Hay varias disponibles en el mercado.

### Ejecutar con análisis de registro en plataformas Unix

El siguiente ejemplo muestra cómo configurar un archivo shell `run_sync.sh` en Linux o Mac OS X:

```sh
user-sync --users file users-file.csv --process-groups | grep "CRITICAL\|WARNING\|ERROR\|=====\|-----\|number of\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” UserSyncAdmins@example.com
```

### Programar una tarea de UserSync

#### Cron

Esta entrada en el crontab de Unix ejecutará la herramienta User Sync a las 16.00 h cada día:

```text
0 4 * * * /path/to/run_sync.sh
```

También se puede configurar Cron para enviar los resultados por correo electrónico a un usuario o una lista de correo específicos. Consulte la documentación en Cron para su sistema para obtener más detalles.

#### Programador de tareas de Windows

Este comando utiliza al programador de tareas de Windows para ejecutar la herramienta User Sync cada día a partir de las 16.00 h:

```text
schtasks /create /tn "Adobe User Sync" /tr C:\path\to\run_sync.bat /sc DAILY /st 16:00
```

Consulte la documentación en el programador de tareas de Windows (`help schtasks`) para obtener más detalles.

También hay una GUI para la administración de las tareas programadas de Windows. Puede encontrar al Programador de tareas en el panel de control de administración de Windows.

---

[Sección anterior](advanced_configuration.md)
