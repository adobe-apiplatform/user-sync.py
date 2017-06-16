---
layout: default
lang: es
nav_link: Configuración de User Sync
nav_level: 2
nav_order: 30
---

# Configuración de la herramienta User Sync

## En esta sección
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Sección anterior](setup_and_installation.md)  \| [Sección siguiente](command_parameters.md)

---

El funcionamiento de la herramienta User Sync lo controlan un conjunto de archivos de configuración con estos nombres de archivo, situados (de forma predeterminada) en la misma carpeta que el ejecutable de línea de comandos.

| Archivo de configuración | Propósito |
|:------|:---------|
| user-sync-config.yml | Necesario. Contiene opciones de configuración que definen la asignación de grupos de directorio a grupos de usuarios y configuraciones de producto de Adobe, y que controlan el comportamiento de actualización. También contiene referencias a los otros archivos de configuración.|
| connector&#x2011;umapi.yml&nbsp;&nbsp; | Necesario. Contiene credenciales e información de acceso para llamar la API de la gestión de usuarios de Adobe. |
| connector-ldap.yml | Necesario. Contiene credenciales e información de acceso para acceder al directorio de empresa. |


Si necesita configurar el acceso a grupos de Adobe en otras organizaciones que le han concedido el acceso, puede incluir archivos de configuración adicionales. Para obtener más información, consulte las [instrucciones de configuración avanzada](advanced_configuration.md#acceso-a-grupos-de-otras-organizaciones) a continuación.

## Configuración de los archivos de configuración

Se ofrecen ejemplos de los tres archivos requeridos en la carpeta `config files - basic` del artefacto de lanzamiento `example-configurations.tar.gz`:

```text
1 user-sync-config.yml
2 connector-umapi.yml
3 connector-ldap.yml
```

Para crear su propia configuración, copie los archivos de ejemplo a la carpeta raíz de User Sync y cambie el nombre (para quitar el número inicial). Utilice un editor de texto para personalizar los archivos de configuración copiados para su entorno y modelo de uso. Los ejemplos contienen comentarios que muestran todos los elementos de configuración posibles. Puede eliminar el comentario de los artículos que necesite utilizar.

Los archivos de configuración están en [formato YAML](http://yaml.org/spec/) y usan el sufijo `yml`. Al editar YAML, debe recordar algunas reglas importantes:

- Las secciones y la jerarquía del archivo se basan en sangrías. Debe utilizar caracteres de espacio para la sangría. No utilice caracteres de tabulación.
- El carácter de guion (-) se utiliza para formar una lista de valores. Por ejemplo, aquí se define una lista llamada "adobe\_groups" con dos elementos.

```YAML
adobe_groups:
  - Photoshop Users
  - Lightroom Users
```

Tenga en cuenta que esto puede resultar confuso si la lista tiene un solo elemento. Por ejemplo:

```YAML
adobe_groups:
  - Photoshop Users
```

## Creación y protección de archivos de configuración de la conexión

En los archivos de configuración de la conexión se almacenan las credenciales que dan acceso a User Sync a Adobe Admin Console y al directorio LDAP de la empresa. Para aislar la información confidencial necesaria para conectar a los dos sistemas, todos los datos de credenciales reales se encierran en estos dos archivos. **Asegúrese de protegerlos adecuadamente**, como se describe en la sección [Consideraciones de seguridad](deployment_best_practices.md#consideraciones-de-seguridad) de este documento.

User Sync admite tres técnicas para proteger las credenciales.


1. Las credenciales se pueden poner directamente en los archivos connector-umapi.yml y connector-ldap.yml, y proteger los archivos con el control de acceso del sistema operativo.

2. Las credenciales se pueden poner en el almacén de credenciales seguro del sistema operativo y referenciarse desde los archivos de configuración.

3. Los dos archivos en su totalidad pueden almacenarse de manera segura o cifrarse y se hace referencia a un programa que devuelve su contenido desde el archivo de configuración principal.


Los archivos de configuración de ejemplo incluyen entradas que ilustran cada una de estas técnicas. Deberá conservar solo un conjunto de elementos de configuración y comentar o eliminar los otros.

### Configuración de la conexión a Adobe Admin Console (UMAPI)

Cuando haya obtenido acceso y establecido una integración con la gestión de usuarios en el [Portal del programador](https://www.adobe.io/console/) de Adobe I/O, tome nota de los siguientes elementos de configuración que ha creado o que ha sido asignado a su organización:

- ID de organización
- Clave API
- Secreto de cliente
- ID de cuenta técnica
- Certificado privado

Abra su copia del archivo connector-umapi.yml en un editor de texto y escriba estos valores en la sección "enterprise":

```YAML
enterprise:
  org_id: "Aquí va el ID de la organización"
  api_key: "Aquí va la clave API"
  client_secret: "Aquí va el secreto de cliente"
  tech_acct: "Aquí va el ID de cuenta técnica"
  priv_key_path: "Aquí va la ruta del certificado privado"
```

**Nota:** asegúrese de poner el archivo de clave privada en la ubicación especificada en `priv_key_path` y de que sea legible únicamente por la cuenta de usuario que ejecuta la herramienta.

En User Sync 2.1 o posterior existe una alternativa al almacenamiento de la clave privada en un archivo separado; puede poner la clave privada directamente en el archivo de configuración. En lugar de usar la clave `priv_key_path`, use `priv_key_data` como sigue:

	  priv_key_data: |
	    -----BEGIN RSA PRIVATE KEY-----
	    MIIJKAIBAAKCAge85H76SDKJ8273HHSDKnnfhd88837aWwE2O2LGGz7jLyZWSscH
	    ...
	    Fz2i8y6qhmfhj48dhf84hf3fnGrFP2mX2Bil48BoIVc9tXlXFPstJe1bz8xpo=
	    -----END RSA PRIVATE KEY-----



### Configuración de la conexión al directorio de empresa

Abra la copia del archivo connector-ldap.yml en un editor de texto y establezca estos valores para permitir el acceso a su sistema de directorio de empresa:

```
username: "aquí-va-el-nombre-de-usuario"
password: "aquí-va-la-contraseña"
host: "FQDN.de.host"
base_dn: "nd_base.de.directorio"
```

## Opciones de configuración

El archivo de configuración principal, user-sync-config.yml, se divide en varias secciones principales: **adobe_users**,  **directory_users**,
**limits** y  **logging**.

- La sección **adobe_users** especifica cómo la herramienta User Sync se conecta a Adobe Admin Console a través de la API de gestión de usuarios. Debe apuntar al archivo de configuración seguro separado que almacena las credenciales de acceso. Se define en el campo umapi del campo de conectores.
    - La sección adobe_users también puede contener exclude_identity_types, exclude_adobe_groups y exclude_users que limitan el grupo de usuarios afectados por User Sync. Consulte la sección [Protección de cuentas específicas contra la eliminación de User Sync](advanced_configuration.md#protección-de-cuentas-específicas-contra-la-eliminación-de-user-sync) donde se describe esto con más detalle.
- La subsección **directory_users** contiene dos subsecciones, conectores y grupos:
    - La subsección **connectors** apunta al archivo de configuración seguro separado que almacena las credenciales de acceso para el directorio de empresa.
    - La sección **groups** define la asignación entre los grupos de directorio y las configuraciones de producto y grupos de usuario de Adobe.
    - **directory_users** también puede contener claves que establecen el código de país y tipo de identidad predeterminados. Consulte los archivos de configuración de ejemplo para obtener más información.
- La sección **limits** establece el valor `max_adobe_only_users` que evita que User Sync actualice o elimine las cuentas de usuario de Adobe si hay más cuentas que el valor de cuentas especificado en la organización de Adobe, pero no en el directorio. Este límite evita la eliminación de una gran cantidad de cuentas en caso de error de configuración o de otro tipo. Este campo es obligatorio.
- La sección **logging** especifica una ruta de registro de auditoría y controla la cantidad de información que se escribe en el registro.

### Configuración de los archivos de conexión

El archivo de configuración principal de User Sync contiene solo los nombres de los archivos de la configuración de conexión que contienen en realidad las credenciales de conexión. De este modo se aísla la información confidencial, lo que permite proteger los archivos y limitar el acceso a ellos.

Proporcionan punteros a los archivos de la configuración de conexión en las
secciones **adobe_users** y  **directory_users**:

```
adobe_users:
  connectors:
    umapi: connector-umapi.yml

directory_users:
  connectors:
    ldap: connector-ldap.yml
```

### Configuración de la asignación de grupos

Para poder sincronizar grupos de usuarios y derechos, debe crear grupos de usuarios y configuraciones de producto en Adobe Admin Console y los grupos correspondientes en el directorio de empresa, tal como se ha descrito anteriormente en [Configuración de la sincronización de acceso a los productos](setup_and_installation.md#configuración-de-la-sincronización-de-acceso-a-los-productos).

**Nota:** todos los grupos deben existen y tener los nombres especificados en ambos lados. User Sync no crea ningún grupo en ningún lado; si no se encuentra un grupo con un nombre, User Sync registra un error.

La **groups** sección de  **directory_users** debe tener una entrada para cada grupo de directorio de empresa que representa el acceso a uno o varios productos de Adobe. Para cada entrada de grupo, enumere las configuraciones de producto a las que tienen acceso los usuarios de dicho grupo. Por ejemplo:

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - "Default Acrobat Pro DC configuration"
  - directory_group: Photoshop
    adobe_groups:
      - "Default Photoshop CC - 100 GB configuration"
      - "Default All Apps plan - 100 GB configuration"
```

Los grupos de directorio se pueden asignar a *configuraciones de producto* o a *grupos de usuarios*. Una entrada `adobe_groups` puede dar nombre a ambos tipos de grupo.

Por ejemplo:

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - Default Acrobat Pro DC configuration
  - directory_group: Acrobat_Accounting
    adobe_groups:
      - Accounting_Department
```

### Configuración de los límites

Las cuentas de usuario se eliminan del sistema de Adobe cuando los usuarios correspondientes no están presentes en el directorio y se invoca la herramienta con una de las opciones.

- `--adobe-only-user-action delete`
- `--adobe-only-user-action remove`
- `--adobe-only-user-action remove-adobe-groups`

Si su organización tiene una gran cantidad de usuarios en el directorio de empresa y el número de usuarios leído durante una sincronización es repentinamente pequeño. Esto podría indicar un error de configuración o una situación de error. El valor de `max_adobe_only_users` es un umbral que hace que User Sync suspenda la eliminación y actualización de las cuentas de Adobe existentes e informe de un error si hay muchos menos usuarios en el directorio de empresa (filtrados por los parámetros de la consulta) que en Adobe Admin Console.

Aumente este valor si prevé que el número de usuarios disminuya por debajo del valor actual.

Por ejemplo:

```YAML
limits:
  max_adobe_only_users: 200
```

Esta configuración hace que User Sync compruebe si más de 200 cuentas de usuario presentes en Adobe no se encuentran en el directorio de empresa (según el filtrado) y, si es así, no se actualiza ninguna de las cuentas de Adobe existentes y se registra un mensaje de error.

###  Configuración del registro

Las entradas de registro se escriben en la consola desde la que se ha invocado la herramienta y opcionalmente en un archivo de registro. Se escribe una nueva entrada con una marca de fecha y hora en el registro de cada vez que se ejecuta User Sync.

La sección **logging** le permite activar y desactivar el registro en un archivo, y controla la cantidad de información que se escribe en el registro y la salida de la consola.

```YAML
logging:
  log_to_file: True | False
  file_log_directory: "path to log folder"
  file_log_level: debug | info | warning | error | critical
  console_log_level: debug | info | warning | error | critical
```

El valor log_to_file activa o desactiva el registro en archivo. Los mensajes de registro se escriben siempre en la consola independientemente de la configuración de log_to_file.

Cuando se activa el registro en archivo, el valor file_log_directory es necesario. Especifica la carpeta donde deben escribirse las entradas de registro.

- Proporcione una ruta absoluta o una ruta relativa a la carpeta que contiene este archivo de configuración.
- Asegúrese de que el archivo y la carpeta tienen permisos de lectura/escritura adecuados.

Los valores de nivel de registro determinan la cantidad de información que se escribe en el archivo de registro o la consola.

- El nivel más bajo, depurar, escribe la mayoría de la información y el nivel más alto, crítico, escribe la menor cantidad.
- Puede definir diferentes valores de nivel de registro para el archivo y la consola.

Las entradas de registro que contienen ADVERTENCIA, ERROR o CRÍTICO incluyen una descripción que acompaña el estado. Por ejemplo:

> `2017-01-19 12:54:04 7516 WARNING
console.trustee.org1.action - Error requestID: action_5 code: `"error.user.not_found" message: "No valid users were found in the request"`

En este ejemplo, se registró un aviso el 19/01/2017 a las 12:54:04 durante la ejecución. Una acción provocó un error con el código "error.user.not_found". Se incluye la descripción asociada a ese código de error.

Puede utilizar el valor requestID para buscar la solicitud exacta asociada a un error detectado. Por ejemplo, la búsqueda de "action_5" devuelve el siguiente detalle:

> `2017-01-19 12:54:04 7516 INFO console.trustee.org1.action -
Added action: {"do":
\[{"add": {"product": \["default adobe enterprise support program configuration"\]}}\],
"requestID": "action_5", "user": "cceuser2@ensemble.ca"}`

Esto le da más información sobre la acción que causó el mensaje de advertencia. En este caso, User Sync intentó añadir la "configuración predeterminada de programa de soporte a empresas de adobe" al usuario "cceuser2@ensemble.ca". La acción de adición no se pudo realizar porque no se encontró el usuario.

## Configuraciones de ejemplo

Estos ejemplos muestran las estructuras de archivos de configuración e ilustran los valores de configuración posibles.

### user-sync-config.yml

```YAML
adobe_users:
  connectors:
    umapi: connector-umapi.yml
  exclude_identity_types:
    - adobeID

directory_users:
  user_identity_type: federatedID
  default_country_code: US
  connectors:
    ldap: connector-ldap.yml
  groups:
    - directory_group: Acrobat
      adobe_groups:
        - Default Acrobat Pro DC configuration
    - directory_group: Photoshop
      adobe_groups:
        - "Default Photoshop CC - 100 GB configuration"
        - "Default All Apps plan - 100 GB configuration"
        - "Default Adobe Document Cloud for enterprise configuration"
        - "Default Adobe Enterprise Support Program configuration"

limits:
  max_adobe_only_users: 200

logging:
  log_to_file: True
  file_log_directory: userSyncLog
  file_log_level: debug
  console_log_level: debug
```

### connector-ldap.yml

```YAML
username: "LDAP_username"
password: "LDAP_password"
host: "ldap://LDAP_ host"
base_dn: "base_DN"

group_filter_format: "(&(objectClass=posixGroup)(cn={group}))"
all_users_filter: "(&(objectClass=person)(objectClass=top))"
```

### connector-umapi.yml

```YAML
server:
  # Esta sección describe la ubicación de los servidores utilizados para la gestión de usuarios de Adobe. El valor predeterminado es:
  # host: usermanagement.adobe.io
  # endpoint: /v2/usermanagement
  # ims_host: ims-na1.adobelogin.com
  # ims_endpoint_jwt: /ims/exchange/jwt

enterprise:
  org_id: "Aquí va el ID de la organización"
  api_key: "Aquí va la clave API"
  client_secret: "Aquí va el secreto de cliente"
  tech_acct: "Aquí va el ID de cuenta técnica"
  priv_key_path: "Aquí va la ruta de la clave privada"
  # priv_key_data: "aquí van los datos de la clave real" # Esta es una alternativa a priv_key_path
```

## Probar la configuración

Utilice estos casos de prueba para asegurarse de que la configuración está funcionando correctamente, y que las configuraciones de producto están correctamente asignadas a los grupos de seguridad del directorio de empresa. Ejecute primero la herramienta en modo de prueba (suministrando el parámetro -t) para poder ver el resultado antes de la ejecución real.

###  Creación de usuarios


1. Cree uno o varios usuarios de prueba en el directorio de empresa.


2. Añada usuarios a uno o más grupos de directorio/seguridad configurados.


3. Ejecute User Sync en modo de prueba. (`./user-sync -t --users all --process-groups --adobe-only-user-action exclude`)


3. Ejecute User Sync fuera del modo de prueba. (`./user-sync --users all --process-groups --adobe-only-user-action exclude`)


4. Compruebe que los usuarios de prueba se han creado en Adobe Admin Console.

### Actualización de usuarios


1. Modifique la pertenencia a grupos de uno o varios usuarios de prueba en el directorio.


1. Ejecute User Sync. (`./user-sync -t --users all --process-groups --adobe-only-user-action exclude`)


2. Compruebe que los usuarios de prueba de Adobe Admin Console se hayan actualizado para reflejar la nueva pertenencia a configuración de producto.

###  Desactivación de usuarios


1. Quite o desactive uno o varios usuarios de prueba existentes del directorio de empresa.


2. Ejecute User Sync. (`./user-sync -t --users all --process-groups --adobe-only-user-action exclude`)


3. Compruebe que se hayan eliminado los usuarios de las configuraciones de producto configuradas en Adobe Admin Console.


4. Ejecute User Sync para quitar los usuarios (`./user-sync -t --users all --process-groups --adobe-only-user-action delete`) y, a continuación, ejecute sin -t. Precaución: compruebe que solo se haya quitado el usuario deseado al ejecutar la aplicación con -t. Esta ejecución (sin -t) eliminará realmente los usuarios.


5. Compruebe que las cuentas de usuario se hayan eliminado de Adobe Admin Console.

---

[Sección anterior](setup_and_installation.md)  \| [Sección siguiente](command_parameters.md)
