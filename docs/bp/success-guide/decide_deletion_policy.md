---
layout: default
lang: en
nav_link: Account Deletion
nav_level: 2
nav_order: 140
---

# Decisão sobre como lidar com exclusão de conta

[Seção anterior](layout_products.md) \| [Voltar ao sumário](index.md) \|  [Próxima seção](setup_adobeio.md)


Quando as contas são desativadas ou excluídas do diretório, geralmente deseja-se remover a conta da Adobe correspondente, mas a remoção da conta da Adobe pode resultar na exclusão de ativos, configurações etc. que podem ser necessários posteriormente.  Além disso, as contas de Adobe ID que podem estar em sua organização não podem ser excluídas pois pertencem ao usuário final.  No entanto, as licenças que você conceder ao usuário de Adobe ID poderão ser recuperadas quando você quiser remover aquele usuário de sua organização.


Opções disponíveis para lidar com a exclusão de conta da Adobe por meio do User Sync:

  - Não executar nenhuma ação.  A limpeza da conta deverá ser feita manualmente.

  - Gerar a lista de contas a serem excluídas, mas não executar nenhuma ação agora.  A lista pode ser editada e usada posteriormente para excluir a conta por meio do User Sync.

  - Recuperar todas as licenças dadas por sua organização à conta, mas deixar a conta ativa. (remove-adobe-groups)

  - Recuperar todas as licenças e removê-las da sua organização, mas manter a conta ativa.  (remove)

  - Recuperar todas as licenças e excluir a conta.  (delete)


Alguns aspectos sobre a exclusão de contas:

  - A remoção da conta da Adobe pode excluir ativos, configurações etc. que podem ser necessários posteriormente
 
  - Você só poderá “excluir” contas que estiverem em um domínio de propriedade da sua organização.
  - Você pode ter usuários em sua organização que estejam em domínios de propriedade de outra organização.  Isso acontece quando se solicita acesso a outro domínio de propriedade de outra organização, que depois permite que você adicione usuários daquele domínio à sua própria organização e conceda a eles licenças de sua propriedade.
    - Você pode recuperar as licenças que concedeu a esses usuários
    - É possível removê-las de sua organização, mas você não pode excluir essas contas pois elas são de propriedade de outra organização.
    - Se você tentar excluir essa conta, terá o mesmo efeito de remover o usuário de sua organização

![orgs](images/decide_deletion_multi_org.png)

&#9744; Decida quais serão suas políticas e seus processos para exclusão de usuários do lado da Adobe quando forem removidos do diretório.  Essa decisão influenciará como você invocará o User Sync em uma etapa posterior.

Observe que usuários com Federated ID não conseguirão fazer logon depois de terem sido removidos do diretório, pois o logon e o acesso são controlados pelo provedor de identidade-de execução da empresa e não pela Adobe.  Usuários Enterprise ID ainda podem fazer logon, a menos que a conta seja de fato excluída mesmo que não tenham licenças concedidas para nenhum produto.  Usuários de Adobe ID sempre podem fazer logon, pois eles têm a propriedade da conta.  Se tiverem sido removidos da sua organização, não terão mais as licenças que você possa ter-lhes concedido.


[Seção anterior](layout_products.md) \| [Voltar ao sumário](index.md) \|  [Próxima seção](setup_adobeio.md)

