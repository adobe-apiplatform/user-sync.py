---
layout: default
lang: es
title: Programación
nav_link: Programación
nav_level: 2
nav_order: 320
parent: success-guide
page_id: scheduling
---

# Configuración de la ejecución continuada programada de User Sync


[Sección anterior](command_line_options.md) \| [Regresar al contenido](index.md) 

## Configuración de ejecución programada en Windows

En primer lugar, cree un archivo por lotes con la invocación de User Sync conectado a un escáner para detectar las entradas relevantes para obtener un resumen. Para ello, cree el archivo run_sync.bat con contenido como:

	cd user-sync-directory
	python user-sync.pex --users file example.users-file.csv --process-groups | findstr /I "==== ----- WARNING ERROR CRITICAL Number" > temp.file.txt
	rem email the contents of temp.file.txt to the user sync administration
	your-mail-tool –send file temp.file.txt


No hay ninguna herramienta de línea de comandos de correo electrónico estándar en Windows, pero hay varias disponibles comercialmente.
Debe rellenar las opciones de la línea de comandos específicos.

Este código utiliza el programador de tareas de Windows para ejecutar la herramienta User Sync cada día a partir de las 16.00 h:

	C:\> schtasks /create /tn "User Sync de Adobe" /tr path_to_bat_file/run_sync.bat /sc DAILY /st 16:00

Consulte la documentación en el programador de tareas de Windows (help schtasks) para obtener más detalles.

Tenga en cuenta que, a menudo, cuando configure las tareas programadas, los comandos que funcionan desde la línea de comandos no funcionan en la tarea programada debido a que la identificación de directorio o de usuario actual es diferente. Es recomendable ejecutar uno de los comandos del modo de prueba (que se describen en la sección “Realizar una prueba de ejecución”) la primera vez que intente realizar la tarea programada.


## Configuración de la ejecución programada en sistemas basados en Unix

En primer lugar, cree un script de shell con la invocación de User Sync conectado a un escáner para detectar las entradas relevantes para obtener un resumen. Para ello, cree el archivo run_sync.sh con contenido como:

	cd user-sync-directory
	./user-sync --users file example.users-file.csv --process-groups |  grep "CRITICAL\\|WARNING\\|ERROR\\|=====\\|-----\\|number of\\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” 
    Your_admin_mailing_list@example.com


Debe rellenar las opciones de línea de comandos específicas de User Sync y la dirección de correo electrónico a la que debe enviarse el informe.

Esta entrada en el crontab de Unix ejecutará la herramienta User Sync a las 16.00 h cada día: 

	0 4 * * *  path_to_Sync_shell_command/run_sync.sh 

También se puede configurar Cron para enviar los resultados por correo electrónico a un usuario o una lista de correo específicos. Consulte la documentación en Cron para su sistema Unix para obtener más detalles.

Tenga en cuenta que, a menudo, cuando configure las tareas programadas, los comandos que funcionan desde la línea de comandos no funcionan en la tarea programada debido a que la identificación de directorio o de usuario actual es diferente. Es recomendable ejecutar uno de los comandos del modo de prueba (que se describen en la sección “Realizar una prueba de ejecución”) la primera vez que intente realizar la tarea programada.


[Sección anterior](command_line_options.md) \| [Regresar al contenido](index.md) 

