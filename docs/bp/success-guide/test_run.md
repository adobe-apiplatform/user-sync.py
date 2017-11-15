---
layout: default
lang: bp
nav_link: Execução de Teste
nav_level: 2
nav_order: 290
---

# Execução de um teste para verificar a configuração

[Seção anterior](setup_config_files.md) \| [Voltar ao sumário](index.md) \| [Próxima seção](monitoring.md)

Para invocar o User Sync:

Windows:      **Python user-sync.pex ….**

Unix, OSX:     **./user-sync ….**


Faça um teste:

	./user-sync –v            Report version
	./user-sync –h            Help on command line args

&#9744; Use os dois comandos acima e verifique se estão funcionando. (No Windows, o comando é ligeiramente diferente.)


![img](images/test_run_screen.png)

&#9744; Em seguida, tente sincronizar apenas um usuário e execute no modo de teste.  Você precisa saber o nome de um usuário em seu diretório.  Por exemplo, se o usuário for bart@example.com, tente:


	./user-sync -t --users all --user-filter bart@example.com --adobe-only-user-action exclude

	./user-sync -t --users all --user-filter bart@example.com --process-groups --adobe-only-user-action exclude

O primeiro comando acima fará a sincronização de um único usuário (por causa do filtro de usuário) que deverá resultar em uma tentativa de criar o usuário.  Como está no modo de teste (-t), a execução do user-sync só tentará criar o usuário, mas não o criará de fato.  A opção `--adobe-only-user-action exclude` impedirá a atualização de qualquer conta de usuário já existente na organização da Adobe.

O segundo comando acima (com a opção --process-groups) tentará criar o usuário e adicioná-lo a grupos que estejam mapeados, a partir de seus grupos de diretórios.  Novamente, isso é feito no modo de teste, portanto não será executada uma ação real.  Se os usuários já existirem e os grupos tiverem usuários já adicionados a eles, o user-sync poderá tentar removê-los.  Se for esse o caso, ignore o próximo teste.  Além disso, se você não estiver usando grupos de diretórios para gerenciar o acesso ao produto, ignore os testes que envolvem --process-groups.

&#9744; Em seguida, tente fazer a sincronização limitada a um único usuário e não a execute no modo de teste.  Isso deverá de fato criar o usuário e adicioná-lo a grupos (quando mapeados). 

	./user-sync --users all --user-filter bart@example.com --process-groups --adobe-only-user-action exclude

	./user-sync --users all --user-filter bart@example.com --process-groups --adobe-only-user-action exclude

&#9744; Em seguida, verifique no Adobe Admin Console se o usuário apareceu e se as associações a grupos foram adicionadas.

&#9744; Em seguida, execute o mesmo comando novamente.  O User Sync não deverá tentar recriar nem adicionar novamente-o usuário a grupos.  Ele deverá detectar que o usuário já existe e que é membro do grupo de usuários ou PC e não fazer nada.

Se tudo isso funcionar como o esperado, você estará pronto para fazer uma execução completa (sem filtro de usuário).  Se você tiver poucos usuários no diretório, poderá testar agora.  Se tiver centenas, poderá levar muito tempo, portanto só execute quando estiver pronto para que um comando seja executado durante muitas horas.  Além disso, consulte as próximas seções antes de fazer isso para verificar se há outras opções de linhas de comando relevantes.




[Seção anterior](setup_config_files.md) \| [Voltar ao sumário](index.md) \| [Próxima seção](monitoring.md)

