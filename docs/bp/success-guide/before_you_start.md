---
layout: default
lang: bp
nav_link: Before You Start
nav_level: 2
nav_order: 110
---

# O que você precisa saber antes de começar

[Voltar ao sumário](index.md) \| [Próxima seção](layout_orgs.md)

## Introdução ao User Sync

O Adobe User Sync é uma ferramenta-de linha de comando que transfere informações de usuários e grupos do sistema de diretórios corporativo da sua organização (como o Active Directory ou outro sistema LDAP) ou de outras fontes para o sistema de gerenciamento de usuários da Adobe.  O User Sync baseia-se na ideia de que o sistema de diretórios corporativo é a fonte autoritativa de informações sobre os usuários, por meio do qual as informações são movidas para o sistema de gerenciamento de usuários da Adobe sob o controle de um conjunto de arquivos de configuração do User Sync e opções de linhas de comando.

Cada vez que você executa a ferramenta, ela procura diferenças entre as informações de usuários nos dois sistemas e atualiza o sistema da Adobe para corresponder ao diretório corporativo.

Com o User Sync, você pode criar novas contas da Adobe quando novos usuários aparecerem no diretório, atualizar informações das contas quando determinados campos no diretório mudarem, atualizar grupo de usuários e associação de configuração de produtos (PC) para controlar a alocação de licenças aos usuários.  Você também pode gerenciar a exclusão de contas da Adobe quando o usuário é removido do diretório corporativo.

Também existem recursos para usar atributos de diretório personalizados para controlar os valores que entram na conta da Adobe.

Além de sincronizar com sistemas de diretórios corporativos, também é possível sincronizar com um arquivo csv simples.  Isso pode ser útil para pequenas organizações ou departamentos que não executam sistemas de diretório gerenciados centralmente.

Por fim, para aqueles com grandes diretórios, é possível executar o User Sync por meio de notificações automáticas sobre mudanças no sistema de diretórios, em vez de fazer comparações de grandes números de contas de usuários.

## Terminologia

- Grupo de usuários: um grupo de usuários nomeado no sistema de gerenciamento de usuários da Adobe
- PC: uma configuração de produto.  Um mecanismo semelhante-a grupos da Adobe, no qual, quando os usuários são adicionados à configuração de produto (PC), eles recebem acesso a um produto específico da Adobe.
- Diretório: um termo geral para um sistema de diretórios de usuários, como Active Directory (AD), LDAP ou um arquivo csv que lista usuários
- Grupo de diretórios: um grupo de usuários nomeado no diretório

 

## Diversas configurações
O User Sync é uma ferramenta geral que pode acomodar uma grande variedade de configurações e necessidades de processos.

Dependendo do tamanho da sua organização e de quais produtos da Adobe você tiver comprado, provavelmente terá um ou mais consoles administrativos e organizações na sua configuração da Adobe.  Cada organização tem um ou mais administradores e você deverá ser um deles para configurar as credenciais de acesso para o User Sync.

Cada organização Adobe tem um conjunto de usuários.  Os usuários podem ser de um dos três tipos:

- Adobe ID: uma conta que pertence ao usuário e que foi criada por ele.  A conta e o acesso a ela são gerenciados usando recursos da Adobe.  Um administrador não pode controlar a conta.

- Enterprise ID: uma conta que pertence à empresa e que foi criada por ela.  A conta e o acesso a ela são gerenciados usando recursos da Adobe.  Um administrador pode controlar a conta.

- Federated ID: uma conta que pertence à empresa e que foi criada por ela.  A conta é parcialmente gerenciada usando recursos da Adobe, mas o acesso (senha e logon) é controlado e operado pela empresa.

Enterprise e Federated IDs devem estar em um domínio reivindicado e pertencente à empresa e configuradas na organização Adobe usando o Adobe Admin Console.

Se você tiver mais de uma organização Adobe, precisará entender quais domínios e usuários estão em quais organizações e como esses grupos correspondem às contas definidas pelo seu sistema de diretórios.  Você pode ter uma configuração simples com um único sistema de diretórios e uma única organização Adobe.  Se você tiver mais de uma, de cada, será necessário traçar um mapa de quais sistemas estão enviando informações do usuário para quais organizações Adobe.  Talvez sejam necessárias várias instâncias do User Sync, cada uma delas visando a uma organização Adobe diferente.

O User Sync pode processar a criação e a atualização de usuários, bem como o gerenciamento de licenças.  O uso do User Sync para o gerenciamento de licenças é opcional e independente de outras funções do User Sync.  O gerenciamento de licenças pode ser processado manualmente usando o Adobe Admin Console ou por meio de outro aplicativo.

Existem várias opções disponíveis para processar a exclusão de contas.  Você pode querer que as contas da Adobe sejam excluídas imediatamente quando a conta corporativa correspondente for removida, ou pode ter outro processo em vigor para deixar a conta da Adobe ativa até que alguém verifique se há ativos a serem recuperados nessa conta.  O User Sync pode lidar com uma série de processos de exclusão, incluindo esses.


## O User Sync é executado em seus sistemas.  
Você precisará de um servidor no qual hospedá-lo.  O User Sync é um aplicativo Python de código aberto.  Você pode usar um-pacote Python pré-compilado ou compilá-lo a partir da fonte.

## O que você precisará saber e fazer

----------

### Sistema de diretórios
Entender seu diretório e saber como acessá-lo.

Entender quais usuários no diretório devem ser usuários da Adobe.

### Questões do processo
Estabelecer um processo contínuo e ter alguém para monitorá-lo.

Entender como os produtos devem ser gerenciados (quem obtém acesso e como, por exemplo) em sua empresa.

Decidir se gerenciará apenas usuários ou usuários e licenças de produtos.

Decidir como deseja processar a exclusão de contas quando usuários forem removidos do diretório.

### Ambiente da Adobe
Compreender quais produtos da Adobe você tem.

Entender quais organizações da Adobe estão configuradas e quais usuários pertencem a quais organizações.

Ter acesso administrativo às suas organizações Adobe.

[Voltar ao sumário](index.md) \|  [Próxima seção](layout_orgs.md)
