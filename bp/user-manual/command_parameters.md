---
layout: default
lang: bp
nav_link: Parâmetros de comando
nav_level: 2
nav_order: 40
parent: user-manual
page_id: command-params
---


# Parâmetros de comando

---

[Seção anterior](configuring_user_sync_tool.md)  \| [Próxima seção](usage_scenarios.md)

---
Assim que os arquivos de configuração estiverem preparados, você poderá executar a ferramenta User
Sync na linha de comando ou em um script. Para executar a ferramenta,
execute o seguinte comando em um shell de comando ou a partir de um
script:

`user-sync` \[ _optional parameters_ \]

A ferramenta aceita parâmetros opcionais que determinam o seu
comportamento específico em diversas situações.


| Especificações de parâmetros e argumentos | Descrição |
|------------------------------|------------------|
| `-h`<br />`--help` | Exibir uma mensagem de ajuda e sair.  |
| `-v`<br />`--version` | Exibir o número da versão do programa e sair.  |
| `-t`<br />`--test-mode` | Executar chamadas de ações da API no modo de testes (não executa alterações). Registra o que teria sido executado.  |
| `-c` _filename_<br />`--config-filename` _filename_ | O caminho completo para o arquivo de configuração principal, absoluto ou relativo, até à pasta de trabalho. O nome de arquivo padrão é “user-sync-config.yml” |
| `--users` `all`<br />`--users` `file` _input_path_<br />`--users` `group` _grp1,grp2_<br />`--users` `mapped` | Especificar os usuários a serem selecionados para a sincronização. O padrão é `all`, que se refere a todos os usuários encontrados no diretório. A especificação de `file` significa inserir as especificações do usuário do arquivo CSV nomeado pelo argumento. Especificar `group` interpreta o argumento como uma-lista de grupos separados por vírgulas no diretório corporativo, e apenas os usuários desses grupos são selecionados. Especificar `mapped` é o mesmo que especificar `group` com todos os grupos listados no mapeamento de grupos no arquivo de configuração. Este caso é muito comum quando apenas os usuários nos grupos mapeados devem ser sincronizados.|
| `--user-filter` _regex\_pattern_ | Limitar o conjunto de usuários examinados para a sincronização àqueles que correspondem a um padrão especificado com uma expressão regular. Consulte a [documentação de expressões regulares para Python](https://docs.python.org/2/library/re.html) para obter informações sobre a construção de expressões regulares no Python. O nome de usuário deve corresponder exatamente à expressão regular.|
| `--update-user-info` | Quando fornecido, sincroniza as informações do usuário. Se as informações diferirem entre o diretório corporativo e a Adobe, o lado da Adobe será atualizado para que correspondam. Isso inclui os campos de nome e sobrenome. |
| `--process-groups` | Quando fornecido, sincroniza as informações da associação a grupos. Se a associação nos grupos mapeados diferirem entre o diretório corporativo e a Adobe, a associação a grupos será atualizada no lado da Adobe para que correspondam. Isso inclui a remoção da associação a grupos para os usuários da Adobe não listados no diretório (exceto se a opção `--adobe-only-user-action exclude` também estiver selecionada).|
| `--adobe-only-user-action preserve`<br />`--adobe-only-user-action remove-adobe-groups`<br />`--adobe-only-user-action  remove`<br />`--adobe-only-user-action delete`<br /><br/>`--adobe-only-user-action  write-file`&nbsp;filename<br/><br/>`--adobe-only-user-action  exclude` | Quando fornecido, se existirem contas de usuários no lado da Adobe que não estejam no diretório, realize a ação indicada.  <br/><br/>`preserve`: nenhuma ação relacionada à exclusão da conta é realizada. Esse é o padrão.  Ainda poderão existir alterações na associação a grupos se a opção `--process-groups` tiver sido especificada.<br/><br/>`remove-adobe-groups`: a conta é removida dos grupos de usuários e das configurações de produtos, liberando quaisquer licenças retidas, mas é mantida como uma conta ativa na organização.<br><br/>`remove`: além de remove-adobe-groups, a conta também é removida da organização, mas a conta do usuário, junto com os seus ativos associados, é mantida no domínio e pode ser-adicionada novamente à organização se desejado.<br/><br/>`delete`: além da ação de remoção, a conta será excluída se o seu domínio pertencer à organização.<br/><br/>`write-file`: nenhuma ação relacionada à exclusão da conta é realizada. A lista de contas de usuários presente no lado da Adobe, mas que não esteja no diretório, é gravada no arquivo indicado.  Em seguida, é possível transferir esse arquivo para o argumento `--adobe-only-user-list` em uma execução posterior.  Ainda poderão existir alterações na associação a grupos se a opção `--process-groups` tiver sido especificada.<br/><br/>`exclude`: nenhum tipo de atualização será aplicado aos usuários encontrados apenas no lado da Adobe.  Isso é usado quando são feitas atualizações de usuários específicos por meio de um arquivo (`--users file f`) em que apenas os usuários que precisam de atualizações explícitas estão listados no arquivo e todos os outros usuários devem ser ignorados.<br/><br>Apenas as ações permitidas serão aplicadas.  As contas do tipo Adobe ID pertencem ao usuário, portanto a ação de exclusão será equivalente à de remoção.  O mesmo vale para as contas da Adobe pertencentes a outras organizações. |
| `--adobe-only-user-list` _filename_ | Especifica um arquivo a partir do qual será lida uma lista de usuários.  Essa lista é usada como a lista definitiva de contas de usuários “somente da Adobe”, sobre a qual se atuará.  Uma das diretivas `--adobe-only-user-action` também deve ser especificada e a sua ação será aplicada às contas de usuários da lista.  A opção `--users` é anulada caso essa opção esteja presente: apenas as ações de remoção de conta podem ser processadas.  |
| `--config-file-encoding` _encoding_name_ | Opcional.  Especifica a codificação de caracteres do conteúdo dos arquivos de configuração.  Isso inclui o arquivo de configuração principal, “user-sync-config.yml”, bem como outros arquivos de configuração referenciados por ele.  O padrão é `utf8` para o User Sync 2.2 e posterior, e `ascii` para versões mais antigas.<br />A codificação de caracteres nos dados de origem do usuário (csv ou ldap) é declarada pelas configurações de conectores, podendo ser diferente daquela usada para os arquivos de configuração (por exemplo, você pode ter um arquivo de configuração latin-1, mas um arquivo de origem CSV que utiliza codificação utf-8).<br />As codificações disponíveis dependem da versão do Python; consulte a documentação [aqui](https://docs.python.org/2.7/library/codecs.html#standard-encodings) para obter mais informações.  |
| `--strategy sync`<br />`--strategy push` | Disponível na versão 2.2 e posteriores. Opcional.  O modo de operação padrão é `--strategy sync`.   Controla se o User Sync lê as informações de usuários da Adobe e as compara às informações do diretório e para emitir atualizações para a Adobe, ou se simplesmente força a entrada do diretório para a Adobe sem considerar as informações de usuários já existentes lá.  `sync` é o padrão e o objeto da descrição da maior parte dessa documentação.  `push` é útil quando existe um grande número de usuários no lado da Adobe (>30.000), você deseja realizar uma série de adições ou alterações conhecidas em poucos usuários, e a lista desses usuários está disponível em um arquivo csv ou em um grupo de diretórios específico.<br />Se `--strategy push` estiver especificado, `--adobe-only-user-action` não poderá ser especificado, pois a determinação de usuários adobe-only não foi realizada.<br/>`--strategy push` cria novos usuários, modifica suas associações a grupos apenas para os grupos mapeados (se `--process-groups` estiver presente), atualiza as informações de usuários (se `--update-user-info` estiver presente) e não remove usuários da organização ou exclui suas contas.  Consulte [Gestão de notificações automáticas](usage_scenarios.md#handling-push-notifications) para obter informações sobre como remover usuários por meio de notificações automáticas. |
{: .bordertablestyle }

---

[Seção anterior](configuring_user_sync_tool.md)  \| [Próxima seção](usage_scenarios.md)
