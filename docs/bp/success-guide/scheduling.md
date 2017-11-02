---
layout: default
lang: bp
nav_link: Scheduling
nav_level: 2
nav_order: 320
---

# Configuração da execução contínua agendada do User Sync


[Seção anterior](command_line_options.md) \| [Voltar ao sumário](index.md) 

## Configuração da execução agendada no Windows

Primeiro, crie um arquivo em lote com a invocação do user-sync transmitido para análise para retirar as entradas de registro relevantes para um resumo.  Crie o arquivo run_sync.bat para isso com conteúdo como:

	cd user-sync-directory
	Python user-sync.pex --users file example.users-file.csv --process-groups | findstr /I “==== ----- WARNING ERROR CRITICAL Number” > temp.file.txt
	rem email the contents of temp.file.txt to the user sync administration
	your-mail-tool –send file temp.file.txt


Não existe uma ferramenta de linha de comando padrão-no Windows, mas várias estão disponíveis comercialmente.
Você precisa preencher suas opções de linhas de comando específicas.

Esse código utiliza o agendador de tarefas do Windows para executar a ferramenta User Sync todos os dias às 16h:

	C:\> schtasks /create /tn “Adobe User Sync” /tr path_to_bat_file/run_sync.bat /sc DAILY /st 16:00

Verifique a documentação sobre o agendador de tarefas do Windows (help schtasks) para obter mais detalhes.

Note que geralmente, ao configurar tarefas agendadas, os comandos que funcionam a partir da linha de comando não funcionam na tarefa agendada porque o diretório ou ID de usuário atual é diferente.  É uma boa ideia executar um dos comandos no modo de teste (descritos na seção “Faça uma execução de teste”) na primeira utilização da tarefa agendada.


## Configuração da execução agendada em sistemas-baseados em Unix

Primeiro, crie um script de shell com a invocação do user-sync transmitido para uma análise para a retirada das entradas de registro relevantes para um resumo.  Crie o arquivo run_sync.sh para isso com conteúdo como:

	cd user-sync-directory
	./user-sync --users file example.users-file.csv --process-groups |  grep “CRITICAL\\|WARNING\\|ERROR\\|=====\\|-----\\|number of\\|Number of” | mail -s “Adobe User Sync Report for `date +%F-%a`” 
    Your_admin_mailing_list@example.com


Preencha suas opções específicas de linhas de comando do User Sync e o endereço de email para o qual o relatório deverá ser enviado.

Essa entrada no crontab do Unix executará a ferramenta User Sync às 4h todos os dias: 

	0 4 * * *  path_to_Sync_shell_command/run_sync.sh 

O cron também pode ser configurado para enviar os resultados por email para um usuário específico ou uma lista de emails.  Consulte a documentação sobre o cron para o seu sistema Unix para obter mais detalhes.

Note que geralmente, ao configurar tarefas agendadas, os comandos que funcionam a partir da linha de comando não funcionam na tarefa agendada porque o diretório ou ID de usuário atual é diferente.  Execute um dos comandos no modo de teste (descritos na seção “Faça uma execução de teste”) na primeira utilização da tarefa agendada.


[Seção anterior](command_line_options.md) \| [Voltar ao sumário](index.md) 

