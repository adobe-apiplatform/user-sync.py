---
layout: page
title: Perguntas frequentes sobre o User Sync
advertise: FAQ
lang: bp
nav_link: FAQ
nav_level: 1
nav_order: 500
parent: root
page_id: faq
---
### Sumário
{:.“no_toc”}

* Marcador TOC
{:toc}


### O que é o User Sync?

Uma ferramenta que permite que empresas criem/gerenciem usuários 
e atribuições de direito da Adobe utilizando o Active Directory (ou outros 
serviços de diretório OpenLDAP testados).  Os usuários-alvo são administradores de identidade de TI
(administradores de diretórios corporativos/de sistemas) que poderão 
instalar e configurar a ferramenta.  A ferramenta-de código aberto é personalizável 
para que um desenvolvedor possa modificá-la para atender às 
necessidades particulares dos clientes. 

### Por que o User Sync é importante?

O User Sync, uma ferramenta-independente de nuvem (CC, EC, DC), serve como um catalisador 
para mover mais usuários para a implantação de usuários nomeados e aproveitar totalmente 
os recursos de produtos e serviços no Admin Console.
 
### Como funciona?

Quando o User Sync é executado, ele obtém uma lista de usuários do Active Directory 
da organização (ou de outra fonte de dados) e a compara com a lista de 
usuários no Admin Console.  Em seguida, ele chama a API de gerenciamento de usuários da Adobe 
para que o Admin Console seja sincronizado com o diretório da 
organização.  O fluxo de mudanças é totalmente-unidirecional; as edições feitas no 
no Admin Console não são enviadas para o diretório.

As ferramentas permitem que o administrador do sistema mapeie grupos de usuários no diretório do cliente 
com configuração de produto e grupos de usuários no Admin Console

Para configurar o User Sync, a organização precisa criar um conjunto de credenciais 
da mesma forma que faria para usar a API de gerenciamento de usuários.
 
### Onde posso obtê-lo?

O User Sync é de código aberto, distribuído sob a licença MIT e mantido pela Adobe. Ele está disponível [aqui](https://github.com/adobe-apiplatform/user-sync.py/releases/latest).


### O User Sync se aplica a-servidores locais e do Azure Active Directory?

O User Sync é compatível com servidores locais ou do AD (Active Directory) hospedados pelo Azure, bem como qualquer outro servidor LDAP.  Ele também pode ser executado a partir de um arquivo local.

### O AD é tratado como um servidor LDAP?

Sim, o AD é acessado por meio do protocolo LDAP v3, que é totalmente compatível com o AD.

### O User Sync coloca automaticamente todos os meus grupos de usuários do LDAP/AD no Adobe Admin Console?

Não. Nos casos 
em que os grupos do lado da empresa correspondam às configurações desejadas de acesso 
ao produto, o arquivo de configuração do User Sync pode ser configurado para mapear 
usuários para configurações de produtos (PCs) ou grupos de usuários no lado 
da Adobe com base na associação-da empresa.  Grupos de usuários e configurações de produtos devem ser configurados manualmente no Adobe Admin Console.

 
### O User Sync pode ser usado para gerenciar a associação em grupos de usuários ou apenas em configurações de produtos?

No User Sync, você pode usar grupos de usuários ou configurações de produtos no mapeamento de grupos de diretórios.  Dessa forma, os usuários podem ser adicionados ou removidos de grupos de usuários, bem como de PCs.  No entanto, não é possível criar novos grupos de usuários ou configurações de produtos; isso deve ser feito no Admin Console.

### Nos exemplos no manual do usuário, vejo que cada grupo de diretórios é mapeado exatamente para um grupo da Adobe; é possível mapear 1 grupo do AD para várias configurações de produtos?

A maioria dos exemplos mostra apenas um único grupo de usuários ou PC da Adobe, mas o mapeamento pode ser feito de um para vários.  Basta listar todos os grupos de usuários ou PCs, um por linha, com um hífen “-” na frente (e recuado para o nível adequado) de cada um, conforme o formato da lista YML.

### A limitação do servidor UMAPI pode interferir na operação do User Sync?

Não, o User Sync processa a limitação e as novas tentativas, de modo que 
essa limitação poderá causar lentidão no processo geral do User Sync, mas nenhum problema é causado pela limitação,  
e o User Sync concluirá todas as operações corretamente.

Os sistemas Adobe se protegem contra sobrecarga ao monitorar o volume 
de solicitações recebidas.  Se o volume exceder os limites, as solicitações retornarão 
um cabeçalho "retry-after", que indicará quando a capacidade estará disponível novamente.  O User Sync considera esses cabeçalhos e aguarda o tempo solicitado antes de tentar novamente.  Você pode obter mais informações, incluindo exemplos de código, na [documentação da API de gerenciamento de usuários](https://www.adobe.io/apis/cloudplatform/usermanagement/docs/gettingstarted.html).
 
###  Existe uma lista local de usuários criados/atualizados (no lado do User Sync) para reduzir as chamadas do servidor da Adobe?

Quando é executado, o User Sync sempre consulta os sistemas de gerenciamento de usuários da Adobe para obter 
informações atualizadas, exceto no caso a seguir.  Existe uma opção disponível na 
versão 2.2 ou posterior do User Sync para impedir essa consulta e enviar atualizações para a Adobe sem
considerar o estado atual dos usuários no sistema de gerenciamento de usuários da Adobe. Se você puder determinar
quais usuários mudaram no diretório local e tiver certeza de que outros usuários 
não foram alterados no sistema da Adobe, essa abordagem poderá reduzir o tempo de execução 
(e uso da rede) de seus trabalhos de sincronização.
 
### A ferramenta User Sync é limitada a federated IDs ou qualquer tipo de ID pode ser criada?

O User Sync é compatível com todos os tipos de ID (Adobe IDs, Federated IDs e Enterprise IDs).

### Uma organização Adobe pode ter acesso a usuários de domínios pertencentes a outras organizações.  O User Sync consegue lidar com esse caso?

Sim.  O User Sync pode tanto consultar quanto gerenciar 
a associação a grupos de usuários e o acesso a produtos para usuários em domínios próprios e acessados.  Entretanto, 
assim como o Admin Console, o User Sync só pode ser usado para criar e atualizar 
contas de usuários em domínios próprios e não em domínios pertencentes a outras organizações.  Os usuários desses
domínios podem receber acesso a produtos, mas não podem ser editados ou excluídos.

### Existe uma função de atualização ou só é possível adicionar/remover usuários (somente para Federated ID)?

Para todos os tipos de ID (Adobe, Enterprise e Federated), o User Sync suporta 
a atualização de associações a grupos sob o controle da opção --process-groups.  
Para Enterprise e Federated IDs, o User Sync suporta a atualização de campos de nome, 
sobrenome e email sob o controle da opção --update-user-info.  Quando houver 
atualizações de país disponíveis no Admin Console, elas também estarão 
disponíveis por meio da UMAPI.  E para Federated IDs cuja “Configuração de logon de usuário” 
for “Nome de usuário”, o User Sync oferecerá suporte a atualização de nome de usuário e de outros campos.

### A ferramenta User Sync é dedicada a um sistema operacional específico?

O User Sync é um projeto Python de código aberto.  Os usuários podem compilá-lo para qualquer plataforma de sistema operacional que desejarem.  Oferecemos compilações para as plataformas Windows, OS X, Ubuntu e Cent OS 7.

### Ele foi testado no Python 3.5?

O User Sync foi executado com sucesso no Python 3.x, mas na maioria das vezes, foi utilizado e testado no Python 2.7, portanto, você poderá se deparar com algum problema, e fornecemos compilações apenas no Python 2.7.  Você pode comunicar qualquer problema (e colaborar com correções) no site de código aberto em https://github.com/adobe-apiplatform/user-sync.py.

### Se algo mudar na API (por exemplo, um novo campo na criação de usuários), como a atualização será aplicada à ferramenta User Sync?

O User Sync é um projeto de código aberto.  Os usuários podem baixar e compilar as fontes mais recentes 
a seu critério.  A Adobe publicará novas versões com compilações periodicamente.  
Os usuários podem ser informados sobre elas por meio de notificações do git.  Ao adotar uma nova versão, 
apenas o arquivo pex único precisa ser atualizado pelo usuário.  Se houver alterações de configuração 
ou alterações de linhas de comando para suportar novos recursos, poderá haver atualizações nesses 
arquivos para que possam ser utilizadas.

Observe também que o User Sync é compilado sobre umapi-client, que é o único módulo com conhecimento direto da API. Quando há alterações da API, o umapi-client sempre é atualizado para manter a compatibilidade com ela. Se e quando as alterações da API fornecerem mais recursos relacionados ao User Sync,-o User Sync poderá ser atualizado para fornecê-los.

### O User Sync precisa de algum tipo de whitelist com as regras de firewall da máquina em que ele é executado?

Em geral, não. O User Sync é apenas um cliente de rede e não aceita conexões de entrada, portanto, as regras de firewall local da máquina-para conexões de entrada são irrelevantes.

No entanto, como cliente de rede, o User Sync requer acesso de saída SSL (porta 443) por meio de firewalls de rede do cliente para acessar os servidores da Adobe. Se configuradas dessa forma, as redes de clientes também precisam permitir que o User Sync acesse o servidor do LDAP/AD do cliente, na porta especificada na configuração do User Sync (porta 389, por padrão).

### O User Sync faz parte da oferta da Adobe para clientes EVIP?
 
Sim, todos os clientes corporativos têm acesso à UMAPI e ao User Sync, independentemente do programa de compra (E-VIP, ETLA ou Enterprise Agreement).
 
### Qual é a situação de internacionalização da ferramenta User Sync; ela está habilitada para internacionalização (compatível, pelo menos, com a entrada de caracteres-de byte duplo)?
 
As versões anteriores do User Sync ofereciam suporte errático a dados de caracteres 
internacionais, embora funcionassem de forma bastante confiável com-fontes de dados codificadas 
em utf8. A partir da versão 2.2, o User Sync foi totalmente habilitado para-Unicode e pode aceitar 
arquivos de configuração e fontes de dados de diretórios ou planilhas que usem qualquer 
codificação de caracteres (com uma expectativa padrão de utf8).

