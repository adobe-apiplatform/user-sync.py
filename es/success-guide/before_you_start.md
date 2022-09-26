---
layout: default
lang: es
nav_link: Antes de empezar
nav_level: 2
nav_order: 110
parent: success-guide
page_id: before-you-start
---

# Lo que necesita saber antes de empezar

[Regresar al contenido](index.md) \| [Sección siguiente](layout_orgs.md)

## Introducción a User Sync

User Sync de Adobe es una herramienta de línea de comandos que mueve la información de usuario y de grupo desde el sistema de directorio de empresas de su organización (por ejemplo, un Active Directory u otro sistema LDAP) u otras fuentes al sistema de gestión del usuario de Adobe. User Sync se basa en la noción de que el sistema de directorios de empresas es la fuente autorizada de información sobre los usuarios y esta se traslada al sistema de gestión de usuarios de Adobe bajo el control de un conjunto de archivos de configuración de User Sync y las opciones de la línea de comandos.

Cada vez que se ejecuta la herramienta, busca las diferencias entre la información de usuario y de grupo en los dos sistemas y actualiza el sistema de Adobe para que coincida con el directorio de empresas.

Con User Sync, puede crear nuevas cuentas de Adobe cuando aparecen nuevos usuarios en el directorio, actualizar la información de la cuenta cuando cambian determinados campos en el directorio y actualizar el abono de los grupos de usuarios y de configuración de producto (PC) para controlar la asignación de licencias a los usuarios. También puede gestionar la eliminación de las cuentas de Adobe cuando el usuario se elimine del directorio de la empresa.

Asimismo, se pueden utilizar los atributos del directorio personalizado para controlar los valores que van a la cuenta de Adobe.

Además de sincronizar con los sistemas de directorio de empresa, también es posible sincronizar con un archivo csv simple. Esto puede resultar útil para pequeñas organizaciones o departamentos que no pueden ejecutar sistemas de directorio gestionados centralizados.

Por último, para los directorios de gran tamaño, es posible ejecutar User Sync a través de notificaciones automáticas de los cambios en el sistema de directorio, en lugar de hacer comparaciones de un gran número de cuentas de usuario.

## Terminología

- Grupo de usuarios: un grupo con nombre de los usuarios que aparecen en el sistema de administración de usuarios de Adobe
- PC: una configuración de producto. Un mecanismo similar a un grupo de Adobe en el que, cuando los usuarios se añaden a la PC, se les concede acceso a un determinado producto de Adobe
- Directorio: un término general para un sistema de directorio de usuarios, como Active Directory (AD), LDAP o un archivo csv que enumera los usuarios
- Grupo de directorios: un grupo con nombre de los usuarios que aparecen en el directorio

 

## Gama de configuraciones
User Sync es una herramienta muy general que puede dar cabida a una amplia variedad de configuraciones y necesidades del proceso.

Dependiendo del tamaño de su organización y de los productos de Adobe haya adquirido, es probable que disponga de una o más consolas de administración y de organizaciones en su configuración de Adobe. Cada organización tiene un administrador o administradores y debe ser uno de ellos el que configure las credenciales de acceso a User Sync.

Cada organización de Adobe tiene un conjunto de usuarios. Los usuarios pueden ser de uno de estos tres tipos:

- Adobe ID: una cuenta creada por el usuario y que es de su propiedad. La cuenta y el acceso a esta cuenta se administran mediante los servicios de Adobe. Un administrador no puede controlar la cuenta.

- Entreprise ID: una cuenta creada por el usuario y que es propiedad de la empresa. La cuenta y el acceso a esta cuenta se administran mediante los servicios de Adobe. Un administrador puede controlar la cuenta.

- Federated ID: una cuenta creada por el usuario y que es propiedad de la empresa. La cuenta está parcialmente administrada por los servicios de Adobe, pero el acceso (la contraseña y el inicio de sesión) están controlados y dirigidos por la empresa.

Enterprise ID y Federated ID deben encontrarse en un dominio que esté reivindicado por la empresa y sea de su propiedad y se configurarán en la organización de Adobe utilizando la Admin Console de Adobe.

Si tiene más de una organización de Adobe, tendrá que comprender qué dominios y usuarios están en qué organizaciones y cómo esos grupos se corresponden con las cuentas definidas por el sistema de directorio. Es posible que disponga de una configuración simple con un solo sistema de directorio y una sola organización de Adobe. Si tiene más de uno, de cada, deberá dibujar un mapa de los sistemas que están enviando la información de los usuarios a las organizaciones de Adobe. Es posible que deban ser varias instancias de User Sync, cada una con una organización diferente de Adobe como destino.

User Sync puede manejar la creación de usuarios y actualizar también la gestión de licencias. El uso de User Sync para la gestión de licencias es opcional e independiente de otras funciones de User Sync. La gestión de licencias se puede realizar manualmente mediante la Admin Console de Adobe, o mediante otra aplicación.

Hay varias opciones disponibles para la gestión de la eliminación de cuentas. Es recomendable que las cuentas de Adobe se eliminen inmediatamente cuando se elimine la cuenta correspondiente de la empresa, o es posible que tenga algún otro proceso preparado para abandonar la cuenta de Adobe hasta que alguien compruebe si hay activos en esa cuenta para recuperarla. User Sync puede manejar una serie de procesos de eliminación que incluye estos.


## User Sync se ejecuta en sus sistemas
Necesitará un servidor en el que alojarlo. User Sync es una aplicación de Python de código abierto. Puede utilizar un paquete de Python anterior a la compilación o crearlo usted mismo a partir de la fuente.

## Qué debe saber y hacer

----------

### Sistema de directorio
Tendrá que entender el directorio y cómo acceder a él.

Deberá entender que los usuarios del directorio deben ser usuarios de Adobe.

### Temas del proceso
Tendrá que establecer un proceso continuo y tener a alguien que lo supervise.

Tendrá que entender cómo deben manejarse los productos (quién puede acceder y cómo, por ejemplo) en su empresa.

Tendrá que decidir si gestionará únicamente a los usuarios, o a los usuarios y las licencias de productos.

Tendrá que decidir cómo desea controlar la eliminación de cuentas cuando se eliminan los usuarios desde el directorio.

### Entorno de Adobe
Deberá tener un buen conocimiento de los productos de Adobe de que dispone.

Tendrá que entender qué organizaciones de Adobe están configuradas y qué usuarios entrarán en qué organizaciones.

Necesitará acceso administrativo a sus organizaciones de Adobe.

[Regresar al contenido](index.md) \|  [Sección siguiente](layout_orgs.md)
