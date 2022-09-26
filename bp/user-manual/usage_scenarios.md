---
layout: default
lang: bp
nav_link: Cenários de uso
nav_level: 2
nav_order: 50
parent: user-manual
page_id: usage
---

<a name="usage-scenarios"></a>
# Cenários de uso

## Nesta seção
{:."no_toc"}

* Marcador TOC
{:toc}

---

[Seção anterior](command_parameters.md)  \| [Próxima seção](advanced_configuration.md)

---

Existem várias maneiras para integrar a ferramenta User Sync nos
processos da empresa, como:

* **Atualizar usuários e associações a grupos.** Sincronize usuários e associações a
grupos adicionando, atualizando e removendo usuários no sistema de gestão
de usuários da Adobe.  Esse é o caso de uso mais geral e comum.
* **Sincronizar apenas as informações de usuários.** Use esta abordagem se o acesso
ao produto deve ser gerenciado usando o Admin Console.
* **Filtrar os usuários para sincronização.** É possível optar por limitar a sincronização-de informações
de usuários em certos grupos ou limitar a sincronização para usuários que correspondam
a um certo padrão. Também é possível sincronizar mediante um arquivo CSV em vez de um
sistema de diretórios.
* **Atualizar usuários e associações a grupos, mas gerenciar as remoções
separadamente.** Sincronize usuários e associações a grupos adicionando e
atualizando usuários, mas sem remover usuários na chamada
inicial. Em vez disso, mantenha uma lista de usuários para remoção e, em seguida, realize
as remoções em uma chamada separada.

Esta seção fornece instruções detalhadas para cada um desses cenários.

## Atualizar usuários e associações a grupos

Este é o tipo de invocação mais típico e comum. O User Sync
encontra todas as alterações nas informações de usuários e da associação a grupos 
no lado da
empresa. Ele sincroniza o lado da Adobe adicionando, atualizando e removendo
usuários e associações ao grupo de usuários e configuração do produto.

Por padrão, somente usuários com identidade do tipo Enterprise ID ou
Federated ID serão criados, removidos ou terão suas associações
a grupos gerenciadas pelo User Sync, pois, geralmente, os usuários do
Adobe ID não são gerenciados no diretório. Consulte a
[descrição abaixo](advanced_configuration.md#managing-users-with-adobe-ids) em
[Configuração avançada](advanced_configuration.md#advanced-configuration) se for assim
que a sua organização trabalha.

Esse exemplo presume que o arquivo de configuração,
user-sync-config.yml, contém um mapeamento de um grupo de diretórios
para uma configuração de produto da Adobe chamada **Default Acrobat Pro DC
configuration**.

### Comando

Essa invocação fornece os parâmetros users e process-groups,
e permite a remoção de usuários com o parâmetro `adobe-only-user-action remove`
.

```sh
./user-sync –c user-sync-config.yml --users all --process-groups --adobe-only-user-action remove
```

### Saída de registro durante a operação

```text
2017-01-20 16:51:02 6840 INFO main - ========== Start Run ==========
2017-01-20 16:51:04 6840 INFO processor - ---------- Start Load from Directory -----------------------
2017-01-20 16:51:04 6840 INFO connector.ldap - Loading users...
2017-01-20 16:51:04 6840 INFO connector.ldap - Total users loaded: 4
2017-01-20 16:51:04 6840 INFO processor - ---------- End Load from Directory (Total time: 0:00:00) ---
2017-01-20 16:51:04 6840 INFO processor - ---------- Start Sync Dashboard ----------------------------
2017-01-20 16:51:05 6840 INFO processor - Adding user with user key: fed_ccewin4@ensemble-systems.com 2017-01-20 16:51:05 6840 INFO dashboard.owning.action - Added action: {"do": \[{"createFederatedID": {"lastname": "004", "country": "CA", "email": "fed_ccewin4@ensemble-systems.com", "firstname": "!Fed_CCE_win", "option": "ignoreIfAlreadyExists"}}, {"add": {"product": \["default acrobat pro dc configuration"\]}}\], "requestID": "action_5", "user": "fed_ccewin4@ensemble-systems.com"}
2017-01-20 16:51:05 6840 INFO processor - Syncing trustee org1... /v2/usermanagement/action/82C654BDB41957F64243BA308@AdobeOrg HTTP/1.1" 200 77
2017-01-20 16:51:07 6840 INFO processor - ---------- End Sync Dashboard (Total time: 0:00:03) --------
2017-01-20 16:51:07 6840 INFO main - ========== End Run (Total time: 0:00:05) ==========
```

### Ver resultado

Quando a sincronização é finalizada com sucesso, o Adobe Admin Console é
atualizado.  Após a execução desse comando, a lista de usuários e 
a lista de usuários de configuração do produto no
Admin Console mostra que um usuário com uma identidade federada foi
adicionado à “Default Acrobat Pro DC configuration”.

![Figura 3: Captura de tela do Admin Console](media/edit-product-config.png)

### Sincronizar somente os usuários

Se fornecer apenas o parâmetro `users` para o comando, a ação
busca alterações nas informações do usuário no diretório corporativo e
atualiza o lado da Adobe com essas alterações. Você pode fornecer
argumentos ao parâmetro `users` que controlam quais usuários serão procurados
no lado da empresa.

Esta invocação não busca ou atualiza quaisquer alterações na associação a
grupos. Caso use a ferramenta desta forma, espera-se que você
controlará o acesso aos produtos da Adobe atualizando as associações do grupo de usuários e
da configuração de produto no Adobe Admin Console.

Isso também ignora os usuários que estão no lado da Adobe mas não
estão mais no lado do diretório, e não realiza qualquer gestão de
grupo de usuários ou configuração de produto.

```sh
./user-sync –c user-sync-config.yml --users all
```

### Filtrar os usuários para sincronização

Independente da escolha de sincronização das informações da associação a grupos,
é possível fornecer argumentos ao parâmetro “users” que filtram quais
usuários serão considerados no lado do diretório corporativo, ou que
obtêm informações do usuário a partir de um arquivo CSV em vez de obter diretamente do
diretório LDAP corporativo.

### Sincronizar somente os usuários de certos grupos

Esta ação busca apenas as alterações das informações de usuários
dos grupos especificados. Ela não busca nenhum outro usuário
no diretório corporativo, e não realiza qualquer gestão de
grupo de usuários ou configuração de produto.

```sh
./user-sync –c user-sync-config.yml --users groups "group1, group2, group3"
```

### Sincronizar somente os usuários de grupos mapeados

Esta ação é o mesma coisa que especificar `--users groups "..."`, onde `...` equivale a todos
os grupos que aparecem no mapeamento de grupos no arquivo de configuração.

```sh
./user-sync –c user-sync-config.yml --users mapped
```

### Sincronizar somente os usuários correspondentes

Esta ação busca apenas as alterações das informações de usuários
cujas IDs correspondam a um padrão. O padrão é especificado por meio de uma
expressão regular do Python.  Neste exemplo, também atualizamos associações
a grupos.

```sh
user-sync --users all --user-filter 'bill@forxampl.com' --process-groups
user-sync --users all --user-filter 'b.*@forxampl.com' --process-groups
```

### Sincronizar por um arquivo

Esta ação sincroniza as informações de usuário fornecidas em um arquivo CSV,
em vez de buscar no diretório corporativo. Um exemplo de
tal arquivo, users-file.csv, é fornecido no download de arquivos de configuração
de exemplo em `examples/csv inputs - user and remove lists/`.

```sh
./user-sync --users file user_list.csv
```

A sincronização por arquivo pode ser usada em duas situações.  Em primeiro lugar, os usuários da Adobe podem ser gerenciados 
por meio de uma planilha.  A planilha lista os usuários, os grupos nos quais estão inseridos e
e suas informações.  Em segundo lugar, se o diretório corporativo oferece notificações automáticas
para atualizações, essas notificações podem ser colocadas em um arquivo csv e usadas para guiar
as atualizações do User Sync.  Consulte a seção abaixo para saber mais esse cenário de uso.

### Atualizar usuários e associações a grupos, mas gerenciar as remoções separadamente

Se não fornecer o parâmetro `--adobe-only-user-action`,
é possível sincronizar as associações a grupos e usuários sem remover quaisquer
usuários do lado da Adobe.

Se desejar gerenciar as remoções separadamente, é possível instruir
a ferramenta para marcar os usuários que não existem mais no diretório
corporativo, mas que ainda existem no lado da Adobe. O
parâmetro `--adobe-only-user-action write-file exiting-users.csv` 
grava a lista de usuários que
estão marcados para remoção em um arquivo CSV.

Para realizar as remoções em uma chamada separada, é possível enviar o
arquivo gerado pelo parâmetro `--adobe-only-user-action write-file`, ou enviar
um arquivo CSV de usuários gerado de
outra maneira. Um exemplo de tal arquivo, `remove-list.csv`,
é fornecido no arquivo example-configurations.tar.gz na pasta `csv inputs - user and remove lists`.

#### Adicionar usuários e gerar uma lista de usuários para remoção

Esta ação sincroniza todos os usuários e também gera uma lista de usuários que não
existem mais no diretório, mas ainda existem no lado da
Adobe.

```sh
./user-sync --users all --adobe-only-user-action write-file users-to-remove.csv
```

#### Remover usuários de uma lista separada

Esta ação utiliza um arquivo CSV que contém uma lista de usuários
marcados para remoção e remove-os da organização
no lado da Adobe. Geralmente, o arquivo CSV é aquele gerado por uma
chamada anterior que usou o parâmetro `--adobe-only-user-action write-file`.

É possível criar um arquivo CSV de usuários para remoção de outras maneiras.
No entanto, se a lista incluir quaisquer usuários que ainda existam no
diretório, esses usuários serão adicionados de volta no
lado da Adobe durante a próxima ação de sincronização que adiciona usuários.

```sh
./user-sync --adobe-only-user-list users-to-remove.csv --adobe-only-user-action remove
```

### Excluir usuários que existem no lado da Adobe, mas não existem no diretório

Essa invocação fornece os parâmetros users e process-groups,
e permite a exclusão de contas de usuário com o parâmetro
adobe-only-user-action delete.

```sh
./user-sync --users all --process-groups --adobe-only-user-action delete
```

### Excluir usuários de uma lista separada

Semelhante ao exemplo de remoção de usuários acima, este exclui usuários que existem somente no lado da Adobe, com base
na lista gerada em um execução anterior do User Sync.

```sh
./user-sync --adobe-only-user-list users-to-delete.csv --adobe-only-user-action delete
```

<a name="handling-push-notifications"></a>
## Gestão de notificações automáticas

Se o sistema do diretório gerar notificações das atualizações é possível usar o User Sync para
processar tais atualizações de forma incremental.  A técnica mostrada nesta seção também pode ser 
usada para processar atualizações imediatas onde um administrador atualizou um usuário ou grupo de 
usuários e deseja incluir apenas essas atualizações imediatamente no sistema de gestão de usuários 
da Adobe.  Podem ser necessários alguns scripts para transformar a informação que chega por meio da 
notificação automática em um formato csv adequado para a introdução no User Sync, e para separar 
as exclusões de outras atualizações, que devem ser gerenciadas separadamente no User Sync.

Crie um arquivo, por exemplo, `updated_users.csv` com o formato da atualização de usuários ilustrado no 
arquivo de exemplo `users-file.csv` na pasta `csv inputs - user and remove lists`.  
Este é um arquivo csv básico com colunas para nome, sobrenome, e assim por diante.

    firstname,lastname,email,country,groups,type,username,domain
    John,Smith,jsmith@example.com,US,"AdobeCC-All",enterpriseID
    Jane,Doe,jdoe@example.com,US,"AdobeCC-All",federatedID
 
Este arquivo é, então, fornecido ao User Sync:

```sh
./user-sync --users file updated-users.csv --process-groups --update-users --adobe-only-user-action exclude
```

O --adobe-only-user-action exclude faz com que o User Sync atualize somente os usuários presentes no arquivo-users.csv atualizado e ignore todos os outros.

As exclusões são gerenciadas de forma semelhante.  Crie um arquivo `deleted-users.csv` com base no formato do `remove-list.csv` na mesma pasta de exemplo e execute o User Sync:

```sh
./user-sync --adobe-only-user-list deleted-users.csv --adobe-only-user-action remove
```

As exclusões serão gerenciadas com base na notificação e nenhuma outra ação será tomada.  Observe que `remove` pode ser substituída por uma das outras ações com base na forma como deseja gerenciar os usuários excluídos.

## Resumo da ação

Ao final da invocação, um resumo da ação será impresso no registro (se o nível for INFORMAÇÃO ou DEPURAÇÃO). 
O resumo fornece as estatísticas acumuladas durante a execução. 
As estatísticas coletadas incluem:

- **Total number of Adobe users:** o número total de usuários da Adobe no Admin Console
- **Number of Adobe users excluded:** o número de usuários da Adobe excluídos pelas operações por meio do exclude_parameters
- **Total number of directory users:** o número total de usuários lidos nos arquivos CSV ou LDAP
- **Number of directory users selected:** o número de usuários do diretório selecionados por meio do parâmetro user-filter
- **Number of Adobe users created:** o número de usuários da Adobe criados durante esta execução
- **Number of Adobe users updated:** o número de usuários da Adobe atualizados durante esta execução
- **Number of Adobe users removed:** o número de usuários da Adobe removidos da organização no lado da Adobe
- **Number of Adobe users deleted:** o número de usuários da Adobe removidos da organização e as contas de usuários de Enterprise ID/Federated ID excluídas no lado da Adobe
- **Number of Adobe users with updated groups:** o número de usuários da Adobe adicionados a um ou mais grupos de usuários
- **Number of Adobe users removed from mapped groups:** o número de usuários da Adobe removidos de um ou mais grupos de usuários
- **Number of Adobe users with no changes:** o número de usuários da Adobe que não sofreram alterações durante esta execução

### Amostra da saída do resumo da ação no registro
```text
2017-03-22 21:37:44 21787 INFO processor - ------------- Action Summary -------------
2017-03-22 21:37:44 21787 INFO processor -   Total number of Adobe users: 50
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users excluded: 0
2017-03-22 21:37:44 21787 INFO processor -   Total number of directory users: 10
2017-03-22 21:37:44 21787 INFO processor -   Number of directory users selected: 10
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users created: 7
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users updated: 1
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users removed: 1
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users deleted: 0
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users with updated groups: 2
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users removed from mapped groups: 5
2017-03-22 21:37:44 21787 INFO processor -   Number of Adobe users with no changes: 48
2017-03-22 21:37:44 21787 INFO processor - ------------------------------------------
```

---

[Seção anterior](command_parameters.md)  \| [Próxima seção](advanced_configuration.md)

