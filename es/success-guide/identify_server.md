---
layout: default
lang: es
nav_link: Servidor de configuración
nav_level: 2
nav_order: 160
parent: success-guide
page_id: identify-server
---

# Identificar y establecer el servidor en el lugar en el que se ejecutará User Sync

[Sección anterior](setup_adobeio.md) \| [Regresar al contenido](index.md) \|  [Sección siguiente](install_sync.md)


User Sync se puede ejecutar manualmente, pero la mayoría de las empresas utilizarán la configuración automática en el lugar en el que User Sync se ejecute de una a algunas veces al día automáticamente.

Debe instalarse y ejecutarse en un servidor que:

  - Pueda acceder a Adobe a través de Internet
  - Pueda acceder a los servicios de directorio como LDAP o AD
  - Esté protegido y sea seguro (sus credenciales administrativas se almacenarán allí o se podrán utilizar para el acceso)
  - Permanezca conectado y sea fiable
  - Tenga algunas capacidades de copia de seguridad y recuperación
  - Pueda enviar idealmente correo electrónico para que los informes se puedan enviar mediante User Sync a los administradores

Tendrá que trabajar con el Departamento de TI para identificar un servidor de este tipo y obtener acceso a él.
Unix, OSX o Windows son compatibles con User Sync.

&#9744; Obtenga un servidor asignado con el fin de ejecutar User Sync. Tenga en cuenta que es posible llevar a cabo la configuración inicial y los ensayos con User Sync en algunos otros equipos como su portátil u ordenador de sobremesa, siempre y cuando se cumplan los criterios anteriores.

&#9744; Obtenga un inicio de sesión en ese ordenador que tenga la capacidad suficiente para instalar y ejecutar la sincronización. Normalmente, puede ser una cuenta sin privilegios.




[Sección anterior](setup_adobeio.md) \| [Regresar al contenido](index.md) \|  [Sección siguiente](install_sync.md)

