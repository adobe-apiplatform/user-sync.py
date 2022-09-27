---
layout: default
lang: bp
title: Monitoramento
nav_link: Monitoramento
nav_level: 2
nav_order: 300
parent: success-guide
page_id: monitoring
---

# Monitoramento do processo do User Sync

[Seção anterior](test_run.md) \| [Voltar ao sumário](index.md) \| [Próxima seção](command_line_options.md)

Se você estiver usando o User Sync como um processo contínuo, precisará nomear alguém que possa monitorar e manter esse processo.  Você também definirá alguns mecanismos automatizados de monitoramento para facilitar a visualização do que está acontecendo e determinar se ocorreram erros.

Há diversas abordagens possíveis para o monitoramento:

- Inspecionar arquivos de registro de execução do User Sync
- Enviar um email do registro da última execução aos administradores que acompanham erros de email (ou-não enviados)
- Vincular arquivos de registro a um sistema de monitoramento e configurar notificações no caso de erros

Para esta etapa, você precisa nomear o responsável pela operação do User Sync e identificar a configuração do monitoramento.

&#9744; Identifique a pessoa ou equipe responsável pelo monitoramento e certifique-se de que possam executar e acompanhar o funcionamento do User Sync.

&#9744; Se você tiver um sistema de análise e alerta de registro disponível, configure o envio do registro do User Sync ao sistema de análise de registro e alertas para mensagens importantes ou de erros presentes no registro.  Você também pode criar alertas para mensagens de advertências.

[Seção anterior](test_run.md) \| [Voltar ao sumário](index.md) \| [Próxima seção](command_line_options.md)
