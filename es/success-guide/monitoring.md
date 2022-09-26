---
layout: default
lang: es
nav_link: Supervisión
nav_level: 2
nav_order: 300
parent: success-guide
page_id: monitoring
---

# Control del proceso de User Sync

[Sección anterior](test_run.md) \| [Regresar al contenido](index.md) \| [Sección siguiente](command_line_options.md)

Si está usando User Sync como un proceso continuo, tendrá que identificar a alguien que pueda supervisar y mantener el proceso de User Sync. También deseará configurar un mecanismo de supervisión automatizado para que resulte más fácil ver lo que sucede y determinar si se han producido errores.

Hay varios métodos posibles de supervisión:

- Inspeccione los archivos de registro desde los que se ejecuta User Sync
- Envíe un correo electrónico con el resumen de registro de la última ejecución a los administradores que controlan los correos electrónicos para detectar errores (o no entrega)
- Enlace los archivos de registro a un sistema de supervisión y las notificaciones de configuración para cuando se produzcan errores

Para este paso, debe identificar quién será el responsable del funcionamiento de User Sync e identificar cómo se configurará la supervisión.

&#9744; Identifique la persona o el equipo responsable de la supervisión y asegúrese de que está listo para acelerar User Sync y lo que hace.

&#9744; Si tiene un análisis de registro y un sistema de alertas disponible, organice el registro de User Sync para enviarlo al sistema de análisis de registro y configure las alertas si en el registro aparecen errores o mensajes importantes. También puede que alerte sobre mensajes de advertencia.

[Sección anterior](test_run.md) \| [Regresar al contenido](index.md) \| [Sección siguiente](command_line_options.md)
