---
layout: page
title: Preguntas frecuentes sobre User Sync
advertise: Preguntas frecuentes
lang: es
nav_link: Preguntas frecuentes
nav_level: 1
nav_order: 500
---
### Tabla de contenido
{:."no_toc"}

* TOC Placeholder
{:toc}


### ¿Qué es User Sync?

Una herramienta que permitirá a los clientes de empresas crear y administrar los usuarios de Adobe y los derechos de asignaciones utilizando Active Directory (u otros servicios de directorio de OpenLDAP probados). Los usuarios de destino son los administradores de identidad de TI (directorio de empresa/administradores del sistema) que podrán instalar y configurar la herramienta. La herramienta de código abierto es personalizable para que los clientes puedan tener un desarrollador que la modifique para adaptarla a sus propias necesidades particulares. 

### ¿Por qué es importante User Sync?

La herramienta User Sync independiente de la nube (CC, CE, DC) sirve como un catalizador para mover a más usuarios a la implementación de usuarios designados y aprovechar al máximo las funciones de los productos y servicios de la Admin Console.
 
### ¿Cómo funciona?

Cuando se ejecuta User Sync, recupera una lista de usuarios de Active Directory de la organización (u otra fuente de datos) y la compara con la lista de los usuarios de la Admin Console. A continuación, llama a la API de gestión de usuarios de Adobe para que la Admin Console se sincronice con el directorio de la organización. El flujo de cambios es totalmente unidireccional; los cambios realizados en la Admin Console no se expulsan del directorio.

Las herramientas permiten que el administrador del sistema asigne grupos de usuarios en el directorio del cliente con la configuración de producto y grupos de usuarios en la Admin Console.

Para configurar User Sync, la organización debe crear un conjunto de credenciales de la misma forma que lo haría para utilizar la API de administración de usuarios.
 
### ¿Dónde puedo obtenerlo?

User Sync es de código abierto, se distribuye bajo la licencia MIT y se mantiene por Adobe. Está disponible [aquí](https://github.com/adobe-apiplatform/user-sync.py/releases/latest).


### ¿Se aplica User Sync tanto en los servidores locales como en los servidores de Azure Active Directory?

User Sync admite servidores locales o de AD (Active Directory) alojados en Azure, así como otros servidores LDAP que también pueden impulsarse desde un archivo local.

### ¿Se trata AD como un servidor LDAP?

Sí, es posible acceder a AD mediante el protocolo LDAP v3, que es totalmente compatible con AD.

### ¿User Sync coloca automáticamente todos mis grupos de usuarios LDAP/AD en la Admin Console de Adobe?

No. En aquellos casos en los que los grupos de la empresa corresponden a las configuraciones de acceso de los productos deseados, el archivo de configuración de User Sync se puede configurar para asignar usuarios a configuraciones de producto (PC) o grupos de usuarios en Adobe en función de su abono de grupos de la empresa. Los grupos de usuarios y las configuraciones de productos se deben configurar manualmente en la Admin Console de Adobe.

 
### ¿Puede utilizarse User Sync para administrar el abono de grupos de usuarios o solo de configuraciones de producto?

En User Sync, puede utilizar grupos de usuarios o configuraciones de productos en la asignación de los grupos de directorio, por lo que los usuarios pueden añadirse o eliminarse de los grupos de usuarios, así como de las configuraciones de productos. Sin embargo, no puede crear nuevos grupos de usuarios ni configuraciones de productos, esto debe realizarse en la Admin Console.

### En los ejemplos del manual de usuario me aparece que cada grupo de directorio se ha asignado exactamente a un grupo de Adobe; ¿es posible tener 1 grupo de AD asignado a varias configuraciones de producto?

La mayoría de los ejemplos muestran a un solo grupo de usuarios o configuración de productos de Adobe, pero la asignación puede ser de uno a varios. Solo tiene que enumerar todos los grupos de usuarios o configuraciones de productos, uno por línea, con “-” delante (y con sangría en el nivel apropiado) en cada uno según el formato de lista YML.

### ¿Puede la limitación del servidor UMAPI interferir con el funcionamiento de User Sync?

No, User Sync se encarga de la limitación y lo vuelve a intentar para que la limitación pueda ralentizar el proceso de sincronización de usuarios, pero no hay ningún problema debido a la limitación y User Sync finalizará correctamente todas las operaciones.

Los sistemas de Adobe se protegen a sí mismos de la sobrecarga mediante el seguimiento del volumen de solicitudes entrantes. Si se empiezan a superar los límites, a continuación, las solicitudes devuelven un encabezado de "reintentar después" que indica cuándo estará disponible la capacidad. User Sync respeta estos encabezados y espera el tiempo solicitado antes de volver a intentarlo. Se pude obtener más información, como ejemplos de códigos, en la [Documentación de la API de administración de usuarios](https://www.adobe.io/apis/cloudplatform/usermanagement/docs/throttling.html).
 
## ¿Existe alguna lista local de los usuarios creados/actualizados (en User Sync) para reducir las llamadas de servidor de Adobe?

No, User Sync siempre consulta los sistemas de gestión de usuario de Adobe para obtener información actualizada cuando se ejecuta.
 
### ¿La herramienta User Sync está limitada a Federated ID o se puede crear cualquier tipo de ID?

User Sync es compatible con todos los tipos de ID (Adobe ID, Federated ID y Enterprise ID).

### Una organización de Adobe puede conceder acceso a los usuarios desde los dominios propiedad de otras organizaciones. ¿User Sync puede manejar este caso?

Sí, User Sync puede consultar y administrar el abono de grupos de usuarios y el acceso a los productos para los usuarios en dominios de propiedad y de acceso. Sin embargo, igual que la Admin Console, User Sync solo se puede utilizar para crear y actualizar las cuentas de usuario en los dominios de propiedad, y no en los dominios propiedad de otras organizaciones. Los usuarios de estos dominios pueden ser productos concedidos pero no editados ni eliminados.

### ¿Existe una función de actualización o solo de adición o eliminación de usuarios (solo para Federated ID)?

Para todos los tipos de ID (Adobe, Enterprise y Federated), User Sync es compatible con la actualización del abono de grupos bajo el control de la opción --process-groups para Enterprise ID y Federated ID. User Sync es compatible con la actualización del nombre, los apellidos y el correo electrónico bajo el control de la opción --update-user-inf. Cuando haya disponibles actualizaciones de país en la Admin Console, también estarán disponibles a través de la UMAPI y de los Federated ID cuya “Configuración de inicio de sesión de usuario” sea “Nombre de usuario”. User Sync es compatible con la actualización del nombre de usuario, así como del resto de campos.

### ¿La herramienta User Sync está dedicada a un sistema operativo particular?

User Sync es un proyecto de Python de código abierto que los usuarios pueden crear para cualquier plataforma de sistema operativo que deseen. Proporcionamos compilaciones para las plataformas de Windows, OS X, Ubuntu y Cent OS 7.

### ¿Se ha probado en Python 3.5?

User Sync se ha ejecutado correctamente en Python 3.x, pero la mayoría de nuestro uso y pruebas ha sido en Python 2.7, por lo que puede detectar problemas. Únicamente proporcionamos compilaciones en Python 2.7. Puede informar de los problemas (y aportar correcciones) en el sitio de código abierto en https://github.com/adobe-apiplatform/user-sync.py.

### Si algo cambia en la API (nuevo campo en la creación de los usuarios, por ejemplo), ¿cómo se aplicará la actualización a la herramienta User Sync?

User Sync es un proyecto de código abierto. Los usuarios pueden descargar y compilar las más recientes fuentes a su criterio. Adobe publicará las nuevas versiones con compilaciones periódicas. Los usuarios pueden estar informados de ellas a través de las notificaciones Git. Al adoptar una nueva versión, solo el archivo Pex debe actualizarse por el usuario. Si hay cambios en la configuración o la línea de comandos cambia para admitir nuevas funciones, puede haber actualizaciones en aquellos archivos que los utilicen.

Asimismo, tenga en cuenta que User Sync se ha diseñado en la parte superior umapi-cliente, que es el único módulo con conocimiento directo de la API. Cuando la API cambia, umapi-cliente siempre se actualiza para ser compatible con ella. Si la API cambia o cuando lo hace, proporciona más funciones relacionadas con User Sync; entonces, User Sync puede actualizarse para proporcionar dichas funciones.

### ¿User Sync requiere algún tipo de lista blanca con las reglas del cortafuegos del ordenador en el que se ejecuta?

Normalmente no. User Sync es exclusivamente un cliente de red y no acepta las conexiones entrantes, por lo que las reglas del cortafuegos del ordenador local para las conexiones entrantes son irrelevantes.

Sin embargo, como cliente de red, User Sync requiere acceso de salida SSL (puerto 443) a través de cortafuegos de red del cliente con el fin de llegar a los servidores de Adobe. Las redes de cliente también deben permitir User Sync, si se ha configurado de esta manera, para alcanzar el servidor LDAP/AD del cliente, sea el que sea el puerto que se especifique en la configuración de User Sync (puerto 389 de forma predeterminada).

### ¿User Sync forma parte de la oferta de Adobe a los clientes EVIP?
 
Sí, todos los clientes de empresas tienen acceso a la UMAPI y a User Sync, independientemente de su programa de compra (E-VIP, CLDE o Enterprise Agreement).
 
### ¿Cuál es la historia de internacionalización para la herramienta User Sync habilitada internacionalmente (compatibilidad con entrada de caracteres de doble byte)?
 
Python 2.7 (el idioma de la herramienta) distingue “str” (cadenas de caracteres de 8 bits) y “unicode” (cadenas de caracteres de 8 bits con codificación UTF-8 forzadas), y el código de User Sync utiliza “str” en lugar de “unicode” en todas partes. Sin embargo, todos los resultados de las herramientas tienen codificación UTF-8 y, siempre y cuando se utilice la codificación UTF-8 en la entrada, las cosas deberían funcionar correctamente. Esto se ha probado ligeramente y no se han encontrado problemas. Está prevista la realización de pruebas adicionales.

Disponemos de una mejora prevista para que la herramienta se ejecute en Python 3, así como en Python 2 
En ese momento podemos garantizar que Unicode funcionará correctamente, puesto que los tipos se fusionan en Python 3. Los clientes para los que resulta complicado deberán utilizar Python 3.
 
 
