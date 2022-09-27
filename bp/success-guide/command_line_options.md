---
layout: default
lang: bp
title: Linha de Comando
nav_link: Linha de Comando
nav_level: 2
nav_order: 310
parent: success-guide
page_id: command-line-options
---

# Escolha das opções finais da linha de comando

[Seção anterior](monitoring.md) \| [Voltar ao sumário](index.md) \|  [Próxima seção](scheduling.md)

A linha de comando do User Sync seleciona o conjunto de usuários a ser processado, especifica se a associação ao PC e ao grupo de usuários deve ser gerenciada, especifica como a exclusão da conta deve ser processada, entre outras opções.

## Usuários


| Opção da linha de comando de usuários  | Usar quando           |
| ------------- |:-------------| 
|   `--users all` |    Todos os usuários listados no diretório forem incluídos.  |
|   `--users group "g1,g2,g3"`  |    Os grupos de diretórios indicados forem usados para formar a seleção de usuários. <br>Os usuários que sejam membros de qualquer um dos grupos forem incluídos.  |
|   `--users mapped`  |    O mesmo que `--users group g1,g2,g3,...`, em que `g1,g2,g3,...` são todos os grupos de diretórios especificados no mapeamento de grupos de arquivos de configuração.|
|   `--users file f`  |    O arquivo f é lido para formar o conjunto selecionado de usuários.  O diretório LDAP não é usado neste caso. |
|   `--user-filter pattern`    |  Pode ser combinado com as opções acima para filtrar e reduzir ainda mais a seleção de usuários. <br>`pattern` é uma cadeia de caracteres no formato de expressão regular do Python.  <br>O nome do usuário precisa coincidir com o padrão para poder ser incluído.  <br>Padrões de escrita podem ser uma espécie de arte.  Veja os exemplos abaixo ou consulte a documentação do Python [aqui](https://docs.python.org/2/library/re.html). |


Se todos os usuários listados no diretório precisarem ser sincronizados com a Adobe, use `--users all`.  Se forem apenas alguns usuários, você poderá limitar o conjunto alterando a consulta LDAP no arquivo de configuração `connector-ldap.yml` (e usar `--users all`) ou limitar os usuários àqueles em grupos específicos (usando --grupo de usuários).  Você pode combinar uma dessas opções com `--user-filter pattern` para limitar ainda mais o conjunto selecionado de usuários a ser sincronizado.

Se você não estiver usando um sistema de diretórios, poderá usar `--users file f` para selecionar os usuários de um arquivo csv.  Consulte o arquivo de exemplos de usuários (`csv inputs - user and remove lists/users-file.csv`) para ver o formato.  Os grupos listados nos arquivos csv são nomes que podem ser selecionados.  Eles são mapeados para os grupos de usuários ou PCs da Adobe do mesmo modo que com os grupos de diretórios.

## Grupos

Se você não estiver gerenciando licenças de produtos com o User Sync, não precisará especificar o mapa de grupos no arquivo de configuração nem adicionar nenhum parâmetro de linha de comando para o processamento de grupos.

Se você estiver gerenciando licenças com o User Sync, inclua a opção `--process-groups` na linha de comando.


## Exclusão de conta


Há várias opções de linhas de comando que permitem especificar a ação a ser executada quando uma conta da Adobe sem conta de diretório correspondente for encontrada (um usuário “somente Adobe”).
Observe que apenas os usuários retornados pela consulta e pelo filtro do diretório são considerados como “existentes” no diretório corporativo.  Essas opções variam de “ignorar completamente” a “excluir completamente”, com diversas possibilidades entre elas.



| Opção de linha de comando       ...........| Usar quando           |
| ------------- |:-------------| 
|   `--adobe-only-user-action exclude`                        |  Nenhuma ação desejada nas contas que existem somente na Adobe e que não têm conta de diretório correspondente. As associações a grupos da Adobe não serão atualizadas mesmo se `--process-groups` estiver presente. |
|   `--adobe-only-user-action preserve`                        |  Nenhuma remoção ou exclusão de contas que existem somente na Adobe e que não têm conta de diretório correspondente. As associações a grupos da Adobe serão atualizadas se `--process-groups` estiver presente. |
|   `--adobe-only-user-action remove-adobe-groups` |    A conta da Adobe deve permanecer, mas as associações a <br>grupos e licenças são removidas.  |
|   `--adobe-only-user-action remove`  |    A conta da Adobe deve permanecer, mas associações a grupos, licenças e listagens no Adobe Admin Console são removidas.   |
|   `--adobe-only-user-action delete`  |    Conta da Adobe será excluída: remover de<br>configurações de produtos da Adobe e dos grupos de usuários; conta excluída e todos os armazenamentos e configurações liberados. |
|   `--adobe-only-user-action write-file f.csv`    |  Nenhuma ação a ser executada na conta.  Nome de usuário gravado no arquivo para ação posterior. |




## Outras opções

`--test-mode`:  faz com que o User Sync seja executado durante todo o processamento, inclusive consultando o diretório e chamando as APIs de gerenciamento de usuários da Adobe para processar a solicitação, mas nenhuma ação de fato é executada.  Nenhum usuário é criado, excluído nem alterado.

`--update-user-info`: faz com que o User Sync verifique as alterações em nome, sobrenome ou endereço de email dos usuários e faz atualizações nas informações da Adobe caso não correspondam às informações do diretório.  A especificação dessa opção pode aumentar o tempo de execução.


## Exemplos

Alguns exemplos:

`user-sync --users all --process-groups --adobe-only-user-action remove`

- Processa todos os usuários com base nas definições de configurações, atualiza a associação a grupos da Adobe e, se houver usuários da Adobe que não estejam no diretório, remove-os do lado da Adobe, liberando as licenças que eles possam ter recebido.  A conta da Adobe não é excluída, para que possa ser-adicionada novamente e/ou ter os ativos armazenados recuperados.
    
`user-sync --users file users-file.csv --process-groups --adobe-only-user-action remove`

- O arquivo “users-file.csv” é lido como a lista mestra de usuários. Nesse caso, não é feita nenhuma tentativa de contatar um serviço de diretório, como AD ou LDAP.  A associação a grupos da Adobe é atualizada com as informações do arquivo, e todas as contas da Adobe não listadas no arquivo são removidas (veja a definição de remoção, acima).

## Definir sua linha de comando

Talvez seja conveniente fazer suas primeiras execuções sem nenhuma opção de exclusão.

&#9744; Prepare as suas opções de linhas de comando necessárias para executar o User Sync.


[Seção anterior](monitoring.md) \| [Voltar ao sumário](index.md) \|  [Próxima seção](scheduling.md)
