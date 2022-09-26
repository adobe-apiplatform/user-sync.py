---
layout: default
lang: bp
nav_link: Configuração avançada
nav_level: 2
nav_order: 60
parent: user-manual
page_id: advanced-config
---


# Configuração avançada

## Nesta seção
{:."no_toc"}

* Marcador TOC
{:toc}

---

[Seção anterior](usage_scenarios.md)  \| [Próxima seção](deployment_best_practices.md)

---

<a name="advanced-configuration"></a>
O User Sync precisa de uma configuração adicional para sincronizar dados de usuários
em ambientes com uma estrutura de dados mais complexa.

- Ao gerenciar usuários do Adobe ID fora das planilhas ou do
diretório corporativo, você pode configurar a ferramenta para que ela não
os ignore.
- Quando sua empresa incluir diversas organizações da Adobe, você
poderá configurar a ferramenta para adicionar usuários da sua organização a
grupos definidos em outras organizações.
- Quando os dados de usuários da sua empresa incluírem atributos e
mapeamentos personalizados, configure a ferramenta para que ela reconheça
essas personalizações.
- Ao usar logon com base no nome de usuário (em vez do email).
- Ao gerenciar algumas contas de usuário manualmente pelo Adobe Admin Console, além do User Sync.

<a name="managing-users-with-adobe-ids"></a>
## Gerenciamento de usuários com Adobe IDs

Existe uma opção de configuração `exclude_identity_types` (na 
seção `adobe_users` do arquivo de configuração principal), que é
definida por padrão para ignorar usuários do Adobe ID.  Se você quiser que o User Sync 
gerencie alguns usuários tipo de Adobe ID, desative essa opção no 
arquivo de configuração, removendo a entrada `adobeID` embaixo de `exclude_identity_types`.

Você pode configurar um trabalho de sincronização separado
especificamente para esses usuários, possivelmente usando entradas CSV
em vez de usar entradas de seu diretório corporativo. Se for fazer isso,
configure esse trabalho de sincronização para ignorar usuários de Enterprise ID e Federated
ID, senão eles poderão ser removidos do
diretório!

A remoção de usuários de Adobe ID pelo User Sync pode não acontecer como você espera:

* Se você especificar que usuários de adobeID devem ser
removidos da organização, precisará-convidá-los novamente
(e eles precisarão-aceitar novamente) se quiser adicioná-los novamente.
* Os administradores do sistema costumam usar Adobe IDs, por isso, remover usuários de Adobe ID
poderá causar a remoção errônea de administradores do sistema (incluindo
você mesmo)

A melhor prática ao gerenciar usuários de Adobe ID é adicioná-los
e gerenciar suas associações a grupos, mas nunca
removê-los.  Ao gerenciar suas associações a grupos, você poderá desativar seus
direitos, eliminado a necessidade de enviar novos convites, caso deseje
que eles voltem posteriormente.

As contas de Adobe ID são de propriedade do usuário final e 
não podem ser excluídas.  Se você aplicar uma ação de exclusão, o User Sync 
automaticamente substituirá a ação de remoção pela ação de exclusão.

Também é possível evitar que usuários específicos do Adobe ID sejam removidos pelo User Sync 
utilizando outros itens de configuração de exclusão.  Consulte
[Proteção de contas específicas contra exclusão do User Sync](#protecting-specific-accounts-from-user-sync-deletion)
para obter mais informações.

## Acesso aos usuários de outras organizações

Uma empresa grande pode incluir diversas organizações da Adobe. Por
exemplo, imagine que uma empresa, a Geometrixx, tenha diversos departamentos,
cada um com sua própria ID de organização exclusiva e
Admin Console.

Se uma organização usar IDs de usuários Enterprise ou Federated,
ela deverá solicitar um domínio. Em uma empresa menor,
uma organização única solicitaria o domínio **geometrixx.com**. Entretanto,
cada domínio pode ser solicitado por apenas uma organização. Se diversas
organizações pertencerem à mesma empresa, algumas ou todas
desejarão incluir os usuários pertencentes ao mesmo domínio corporativo.

Neste caso, o administrador de sistema de cada
departamento poderá solicitar esse domínio para uso de identidade. O
Adobe Admin Console impede que diversos departamentos solicitem
o mesmo domínio.  Entretanto, após o domínio ser solicitado por um único departamento,
outros departamentos poderão solicitar acesso ao domínio de outro
departamento. O primeiro departamento a solicitar o domínio será o *proprietário*
dele. Esse departamento será responsável por aprovar
todas as solicitações de acesso de outros departamentos, os quais poderão então
acessar os usuários no domínio sem configurações
especiais.

Não é necessária nenhuma configuração especial para acessar os usuários em um domínio
para o qual você recebeu acesso. No entanto, se você quiser adicionar
usuários a grupos de usuários ou configurações de produtos definidos
em outras organizações, configure o User Sync para que ele
acesse essas organizações. A ferramenta deve encontrar as
credenciais da organização que define os grupos, além de
identificar grupos como pertencentes a uma organização externa.

<a name="accessing-groups-in-other-organizations"></a>
## Acesso a grupos de outras organizações

Para configurar o acesso a grupos em outras organizações
:

- Inclua arquivos de configuração de conexão umapi adicionais.
- Informe ao User Sync como acessar esses arquivos.
- Identifique os grupos definidos em outra organização.

### 1. Incluir arquivos de configuração adicionais

Para cada organização adicional à qual você precisa de acesso,
adicione um arquivo de configuração que forneça as
credenciais de acesso a ela. O arquivo tem o
mesmo formato do arquivo conector-umapi.yml.  Para cada organização adicional será atribuído um apelido curto (que você definirá).  Você poderá nomear como quiser o arquivo de configuração com as credenciais de acesso dessa organização.  

Por exemplo, se o nome de uma organização adicional for “department 37”.  O arquivo de configuração correspondente poderá ter o seguinte nome: 

`department37-config.yml`

### 2. Configurar o User Sync para acessar os arquivos adicionais


A seção `adobe-users` do arquivo de configuração principal deve
incluir entradas que façam referência a esses arquivos e
associar cada uma ao nome abreviado da organização. Por
exemplo:

```YAML
adobe-users:
  connectors:
    umapi:
      - connector-umapi.yml
      - org1: org1-config.yml
      - org2: org2-config.yml
      - d37: department37-config.yml  # d37 is short name for example above
```

Se forem usados nomes de arquivos não qualificados, os arquivos de configuração deverão estar na mesma pasta que o arquivo de configuração principal que faz referência a eles.

Assim como o seu próprio arquivo
de configuração de conexão, eles contêm informações confidenciais que devem
ser protegidas.

### 3. Identificar grupos definidos externamente

Ao especificar os mapeamentos de grupos, você pode mapear um grupo de
diretório corporativo para um grupo de usuários da Adobe ou uma configuração de produto definida em outra
organização.

Para isso, use o identificador da organização como um prefixo do
nome do grupo. Junte-os com o símbolo "::". Por exemplo:

```YAML
- directory_group: CCE Trustee Group
  adobe_groups:
    - "org1::Default Adobe Enterprise Support Program configuration"
    - "d37::Special Ops Group"
```

## Atributos e mapeamentos personalizados

É possível definir mapeamentos personalizados do atributo de diretório
ou outros valores aos campos usados para definir e atualizar os usuários:
nome, sobrenome, endereço de email, nome de usuário, país e associação do grupo.
Geralmente, os atributos predefinidos no diretório são usados para
obter esses valores.  Você pode definir outros atributos para serem usados e
especificar como os valores dos campos devem ser calculados.

Para isso, configure o User Sync para reconhecer todos os-mapeamentos
não predefinidos entre os dados de usuário do diretório corporativo e os
dados de usuário da Adobe.  Os-mapeamentos não predefinidos incluem:

- Valores de nome de usuário, grupos, país ou email que estejam ou
se baseiem em-atributos não predefinidos no diretório.
- Valores de nome de usuário, grupos, país ou email devem ser
calculados a partir de informações do diretório.
- Outros grupos de usuários ou produtos que precisem ser adicionados ou
removidos da lista para alguns ou todos os usuários.

Seu arquivo de configuração deve especificar todos os atributos personalizados a serem
extraídos do diretório. Além disso, é preciso especificar todos os
mapeamentos personalizados para esses atributos e todos os cálculos ou
ações a serem realizados para sincronizar os valores. A ação personalizada é
especificada com o uso de um pequeno bloco de código Python. Exemplos e
blocos predefinidos são fornecidos.

A configuração dos atributos e mapeamentos personalizados aparece em
um arquivo de configuração separado.  Esse arquivo é referenciado pelo
arquivo de configuração principal na seção `directory_users`:

```
directory_users:
  extension: extenstions_config.yml  # reference to file with custom mapping information
```

O gerenciamento dos atributos personalizados é realizado para cada usuário, portanto as
personalizações são configuradas na-subseção por usuário da
seção de extensões do arquivo de configuração principal do User Sync.

```
extensions:
  - context: per_user
    extended_attributes:
      - my-attribute-1
      - my-attribute-2
    extended_adobe_groups:
      - my-adobe-group-1
      - my-adobe-group-2
    after_mapping_hook: |
        pass # custom python code goes here
```

### Adição de atributos personalizados

Por padrão, o User Sync captura esses atributos predefinidos para cada
usuário do sistema de diretórios corporativos:

* `givenName` - usado para o nome-no perfil no lado da Adobe
* `sn` - usado para o sobrenome-no perfil no lado da Adobe
* `c` - usado para o país-no lado da Adobe (código de país-com duas letras)
* `mail` - usado para o email-no lado da Adobe
* `user` - usado para o nome de usuário-no lado da Adobe apenas para Federated ID via nome de usuário

Além disso, o User Sync captura todos os nomes de atributos que aparecem nos
filtros na configuração do conector LDAP.

Para adicionar atributos a este conjunto, especifique-os em uma
chave `extended_attributes` no arquivo de configuração principal, conforme mostrado acima. O
valor da chave `extended_attributes` é uma lista de strings YAML, onde
cada string informa o nome de um atributo de usuário a ser
capturado. Por exemplo:

```YAML
extensions:
  - context: per-user
    extended_attributes:
    - bc
    - subco
```

Este exemplo direciona o User Sync a capturar os atributos `bc` e `subco`
de cada usuário carregado.

Se um ou mais atributos especificados não estiverem presentes entre as
informações de diretório de um usuário, eles serão
ignorados. As referências de códigos para esses atributos retornarão o
valor Python `None`, que é normal, não um erro.

### Adição de mapeamentos personalizados

A configuração de um código de mapeamento personalizado usa uma seção de extensões no
arquivo de configuração principal (User Sync). Dentro das extensões, uma-seção por usuário
controlará o código personalizado que é chamado uma vez por usuário.

O código especificado é executado uma vez para cada usuário, após
a extração dos atributos e das associações a grupos do
sistema de diretório, porém antes da geração das ações para a
Adobe.

```YAML
extensions:
  - context: per-user
    extended_attributes:
      - bc
      - subco
    extended_adobe_groups:
      - Acrobat_Sunday_Special
      - Group for Test 011 TCP
    after_mapping_hook: |
      bc = source_attributes['bc']
      subco = source_attributes['subco']
      if bc is not None:
          target_attributes['country'] = bc[0:2]
          target_groups.add(bc)
      if subco is not None:
          target_groups.add(subco)
      else:
          target_groups.add('Undefined subco')
```

Neste exemplo, dois atributos personalizados, bc e subco, são
extraídos para cada usuário lido pelo diretório. O código
personalizado processa os dados de cada usuário:

- O código do país é extraído dos dois primeiros caracteres no
atributo bc.

    Esse é um exemplo de como você pode usar os atributos personalizados do diretório para fornecer
valores de campos predefinidos sendo enviados à Adobe.

- O usuário é adicionado a grupos provenientes do atributo subco e
do atributo bc (além de todos os grupos mapeados do mapa
de grupos no arquivo de configuração).

    Esse exemplo mostra como personalizar a lista de configuração do grupo ou produto
para sincronizar os usuários com grupos adicionais.

Se o código gancho fizer referência a configurações de grupos ou produtos da Adobe
que ainda não apareçam na seção de **grupos**
do arquivo de configuração principal, elas serão listadas abaixo de
**extended_adobe_groups**. Essa lista efetivamente estende o
conjunto de grupos considerados da Adobe. Consulte
[Gerenciamento avançado de grupos e produtos](#advanced-group-and-product-management)
para obter mais informações.

### Variáveis de código gancho

O código no `after_mapping_hook` é isolado do restante do
programa User Sync, exceto pelas seguintes variáveis.

#### Valores de entrada

É possível ler as seguintes variáveis no código personalizado.  Elas
não devem ser gravadas e gravar nelas não surte qualquer efeito; elas
existem para expressar os dados do diretório de origem sobre o usuário.

* `source_attributes`: um-dicionário por usuário de atributos de usuário
  extraídos do sistema de diretórios. Como um dicionário Python,
  tecnicamente, este valor é mutável, mas não adianta alterá-lo
  do código personalizado.

* `source_groups`: um conjunto congelado de grupos de diretórios encontrado para um
usuário específico ao percorrer grupos de diretórios configurados.

#### Valores de entrada/saída

É possível ler e gravar as seguintes variáveis no código
personalizado. Elas são fornecidas em dados de carregamento definidos pelas operações predefinidas de mapeamento
de atributos e grupos sobre o atual usuário do diretório e podem ser
gravadas com a finalidade de alterar as ações realizadas no
usuário correspondente da Adobe.

* `target_attributes`: um-dicionário Python por usuário, cujas chaves
são os atributos no lado da Adobe-que precisam ser definidos. Alterar um
valor nesse dicionário alterará o valor gravado no
lado da Adobe. Como a Adobe predefine-um conjunto fixo de atributos,
adicionar uma chave a esse dicionário não surte efeito.  As chaves neste
dicionário são:
    * `firstName` - ignorado para AdobeID, usado em outro lugar
    * `lastName` - ignorado para AdobeID, usado em outro lugar
    * `email` - usado em outro lugar
    * `country` - ignorado para AdobeID, usado em outro lugar
    * `username` - ignorado para tudo, exceto o Federated ID
      [configurado com logon baseado em nome de usuário](https://helpx.adobe.com/enterprise/help/configure-sso.html)
    * `domain` - ignorado para tudo, exceto Federated ID [configurado com o logon baseado em nome de usuário](https://helpx.adobe.com/enterprise/help/configure-sso.html)
* `target_groups`: um-conjunto Python por usuário que coleta as
configurações de grupos de usuários e produtos no lado da Adobe-e às quais o
usuário é adicionado quando `process-groups` é especificado para a
execução de sincronização.  Cada valor é um conjunto de nomes. O conjunto é inicializado
aplicando os mapeamentos de grupos no arquivo de configurações principal e as
alterações feitas nesse conjunto (adições ou remoções) mudam o
conjunto de grupos aplicado ao usuário no lado da Adobe.
* `hook_storage`: um-dicionário Python por usuário que fica vazio na
primeira passagem para o código personalizado e persiste entre as
chamadas.  O código personalizado pode armazenar todos os dados privados neste
dicionário. Caso você use arquivos de script externos, este é um lugar adequado
para armazenar os objetos de códigos criados ao compilar esses arquivos.
* `logger`: um objeto do tipo `logging.logger` que produz registros para o
console e/ou log do arquivo (conforme as configurações de registro em log).

<a name="advanced-group-and-product-management"></a>
## Gerenciamento avançado de grupos e produtos

A **seção de grupos** do arquivo de configuração principal define um
mapeamento de grupos de diretórios para configurações de grupos
de usuários e produtos da Adobe.

- No lado do diretório corporativo, o User Sync seleciona um conjunto de
usuários de seu diretório corporativo, com base na consulta LDAP,
no parâmetro da linha de comando `users` e no filtro de usuário e depois
examina esses usuários para ver se eles estão em um dos
grupos de diretórios mapeados. Se estiverem, o User Sync usará o mapa de grupos para
determinar a quais grupos da Adobe esses usuários devem ser adicionados.
- No lado da Adobe, o User Sync examina a associação das configurações
de grupos e produtos mapeados. Se qualquer usuário nesses grupos
_não_ estiver no conjunto de usuários selecionados do diretório, o User Sync removerá
esse usuário do grupo. Esse costuma ser o comportamento desejado
porque, por exemplo, se um usuário estiver na configuração do produto Adobe Photoshop
e for removido do diretório corporativo,
você espera que ele seja removido do grupo e perca a
licença atribuída.

![Figura 4: Exemplo de mapeamento de grupo](media/group-mapping.png)

Este fluxo de trabalho pode apresentar dificuldades caso você queira dividir o
processo de sincronização em várias execuções para reduzir o número de
usuários de diretório consultados simultaneamente. Por exemplo, você pode iniciar uma execução
para usuários que comecem com A-M e outra para usuários N-Z. Quando você
faz isso, cada execução deve atingir diferentes configurações de grupos de usuários
e produtos da Adobe.  Caso contrário, a execução de A-M removerá
os usuários dos grupos mapeados presentes no conjunto N-Z.

Para configurar esse caso, use o Admin Console para criar grupos de usuários
para cada subconjunto de usuários (por exemplo, **photoshop_A_M** e
**photoshop_N_Z**), depois adicione cada grupo de usuários separadamente à
configuração do produto (por exemplo, **photoshop_config**). Em
sua configuração do User Sync, você então mapeia somente os grupos de usuários,
não as configurações de produtos. Cada trabalho de sincronização é destinado a um
grupo de usuários em seu mapa de grupos.  Ele atualiza a associação no grupo de usuários,
que indiretamente atualiza a associação na
configuração do produto.

## Remoção de mapeamentos de grupos

Pode haver confusão na hora de remover um grupo mapeado. Imagine que 
um grupo de diretórios `acrobat_users` seja mapeado para o grupo da Adobe `Acrobat` 
e que você não queira mais mapear o grupo para `Acrobat`, então remove 
a entrada. O resultado é que todos os usuários são deixados no 
grupo `Acrobat`, pois `Acrobat` deixou de ser um grupo mapeado, então o User 
Sync não o utiliza. Isso não resulta na remoção de todos os usuários 
do `Acrobat`, conforme o desejado.

Se você também quisesse remover os usuários do grupo `Acrobat`, poderia
fazer isso manualmente usando o Admin Console ou (pelo menos 
temporariamente) deixar a entrada no mapa de grupos no arquivo de configuração,
mas alteraria o nome do grupo de diretórios para algo que você sabe
que não existe no diretório, como `no_directory_group`.  A próxima execução de sincronização 
detectaria que existem usuários no grupo Adobe que não estão 
no grupo de diretórios e todos 
eles seriam movidos.  Depois, você poderia remover
todo o mapeamento do arquivo de configuração.

## Trabalho com nomes de usuários-Com base em logon

No Adobe Admin Console, você pode configurar um domínio federado para usar nomes de-logon de usuários com base em email ou logon com base em-nome de usuário (ou seja, não baseado em-email-).   O logon com base em nome de usuário-pode ser usado quando os endereços de email mudam com frequência ou quando sua organização não permite o uso de endereços de email para fazer logon.  Na verdade, usar logon com base em nome de usuário-ou em email-depende da estratégia global de identidade da empresa.

Para configurar o User Sync de forma que ele funcione com logons de nome de usuário, é necessário definir diversos outros itens de configuração.

No arquivo `connector-ldap.yml`:

- Defina o valor de `user_username_format` para algo como '{attrname}', em que attrname nomeia o atributo de diretório cujo valor deverá ser usado para o nome de usuário.
- Defina o valor de `user_domain_format` para algo como '{attrname}' se o nome de domínio vier do atributo de diretório nomeado, ou então como um valor de string fixo, como 'example.com'.

Durante o processamento do diretório, o User Sync preencherá os valores de nome de usuário e domínio a partir desses campos (ou valores).

Os valores informados para esses itens de configuração podem ser uma combinação de caracteres de string e um ou mais nomes de atributos que aparecem entre-chaves "{}".  Os caracteres fixos são combinados com o valor de atributo para formar a string usada no processamento do usuário.

Para domínios que usam logon com base em nome de usuário,-o item de configuração `user_username_format` não deve produzir um endereço de email; o caractere "@" não é permitido em nomes de usuário usados em logon-com base em nome de usuário.

Se você usar um logon com base em nome de usuário,-ainda precisará informar um endereço de email exclusivo para cada usuário, algo que esteja dentro de um domínio solicitado e detido pela organização. O User Sync não adicionará usuários à organização da Adobe sem um endereço de email.

<a name="protecting-specific-accounts-from-user-sync-deletion"></a>
## Proteção de contas específicas contra exclusão do User Sync

Se você cria e remove contas pelo User Sync e quer criar manualmente algumas contas, use este recurso para que ele não exclua essas contas criadas manualmente.

Na seção `adobe_users` do arquivo de configuração principal, você pode incluir
as seguintes entradas:

```YAML
adobe_users:
  exclude_adobe_groups: 
      - special_users       # Adobe accounts in the named group will not be removed or changed by user sync
  exclude_users:
      - ".*@example.com"    # users whose name matches the pattern will be preserved by user sync 
      - another@example.com # can have more than one pattern
  exclude_identity_types:
      - adobeID             # causes user sync to not remove accounts that are AdobeIds
      - enterpriseID
      - federatedID         # you wouldn’t have all of these since that would exclude everyone  
```

Esses itens de configuração são opcionais.  Eles identificam contas individuais ou grupos de contas,
e as contas identificadas são protegidas contra exclusão por parte do 
User Sync.  Essas contas ainda podem ser adicionadas ou removidas de grupos de usuários
ou de configurações de produtos com base nas entradas de mapas de grupos e na
opção de linha de comando `--process-groups`.  

Se você quiser impedir que o User Sync remova essas contas, simplesmente as coloque em grupos que não estejam sob o controle do User Sync, ou seja, grupos 
que não estejam nomeados no mapa de grupos do arquivo de configuração.

- `exclude_adobe_groups`: os valores deste item de configuração são uma lista de cadeias de caracteres que nomeiam grupos de usuários ou configurações de produtos (PCs) da Adobe.  Todos os usuários em qualquer um desses grupos serão preservados e nunca excluídos como-usuários somente da Adobe.
- `exclude_users`: os valores deste item de configuração são uma lista de strings que são padrões e podem ser associadas a nomes de usuários da Adobe.  Todos os usuários correspondentes são preservados e nunca excluídos como-usuários somente da Adobe.
- `exclude_identity_types`:  os valores deste item de configuração são uma lista de strings que podem ser "adobeID", "enterpriseID" e "federatedID".  Isso faz com que qualquer conta dos tipos listados seja preservada e nunca excluída como-usuários somente da Adobe.


## Trabalho com grupos de diretórios aninhados no Active Directory

Observação: antes da versão 2.2, grupos aninhados não eram compatíveis com o User Sync.

A partir da versão 2.2, o User Sync pode ser configurado para reconhecer todos os usuários 
em grupos de diretórios aninhados e os arquivos de exemplo de configurações mostram como 
fazer isso.  Especificamente, no arquivo de configuração `connector-ldap.yml`, defina 
`group_member_filter` da seguinte maneira:

    group_member_filter_format: "(memberOf:1.2.840.113556.1.4.1941:={group_dn})"

Esse parâmetro localiza membros do grupo que estejam diretamente em um grupo nomeado ou que estejam indiretamente no grupo.

Você pode ter uma estrutura de aninhamento de grupo como esta:

    All_Divisions
      Blue_Division
             User1@example.com
             User2@example.com
      Green_Division
             User3@example.com
             User4@example.com

Você pode mapear All_Divisions para um grupo de usuários da Adobe ou uma configuração de produto na seção
`groups:` do arquivo de configuração principal e definir group_member_filter 
conforme mostrado acima.  O efeito disso é tratar todos os usuários contidos diretamente em All_Divisions ou em qualquer grupo contido direta ou indiretamente em All_Divisions como membros do grupo de diretórios All_Divisions.

## Uso de técnicas de notificações automáticas para ativar o User Sync

A partir do User Sync versão 2.2, é possível ativar notificações automáticas diretamente para o
sistema de gerenciamento de usuários da Adobe sem precisar ler todas as informações da Adobe e do
seu diretório corporativo.  O uso de notificações automáticas minimiza o 
tempo de processamento e o tráfego de comunicações, porém a desvantagem de não ser-autocorretivo
quanto a alterações feitas de outras formas ou no caso de alguns erros.  É necessário
um gerenciamento mais cauteloso das alterações a serem feitas.

Use uma estratégia de notificações automáticas se:

- Você tiver uma base de usuários da Adobe extremamente grande.
- Você precisar fazer algumas adições/alterações/exclusões referentes à população total de usuários.
- Você tiver um processo ou ferramentas capazes de identificar usuários que tenham sido alterados (adicionados, 
removidos, mudanças de atributos ou de grupos) de maneira automatizada.
- Você tiver um processo que primeiro remova direitos de produtos dos usuários extintos, e depois 
(após um período de espera) exclua totalmente suas contas.

A estratégia de notificações automáticas evita a sobrecarga de leitura de grandes quantidades de usuários dos dois lados, mas
você só poderá fazer isso se conseguir isolar os usuários específicos que precisem de atualização (por exemplo,
colocando-os em um grupo especial).

Para usar notificações automáticas, você precisa reunir as atualizações a serem feitas 
incondicionalmente em um arquivo ou grupo de diretórios separados.  As exclusões de usuários também devem 
ser separadas de adições e atualizações de usuários.  Assim, as atualizações e exclusões serão executadas
em invocações separadas da ferramenta User Sync.

O User Sync possibilita muitas abordagens com o uso de técnicas de notificações automáticas.  As próximas seções
descrevem uma abordagem recomendada.  Para concretizá-la, vamos imaginar dois
produtos da Adobe que tenham sido comprados e devam ser gerenciados com o uso do User Sync: Creative Cloud
e Acrobat Pro.  Para conceder acesso, imagine que você tenha criado duas configurações de produtos chamadas
Creative_Cloud e Acrobat_Pro e dois grupos de diretórios chamados cc_users e acrobat_users.
O mapa no arquivo de configuração do User Sync ficaria assim:

    grupos:
      - directory_group: acrobat_users
        adobe_groups:
          - "Acrobat_Pro"
      - directory_group: cc_users
        adobe_groups:
          - "Creative_Cloud"



### Uso de um grupo especial de diretórios para ativar notificações automáticas do User Sync

Outro grupo de diretórios é criado para coletar os usuários que serão atualizados.  Por exemplo, 
use um grupo de diretórios `updated_adobe_users` para usuários novos ou atualizados (cuja associação a grupos
tenha mudado).  A remoção de usuários dos dois grupos mapeados revoga qualquer acesso ao produto
e libera as licenças detidas pelos usuários. 

A linha de comando-para processar as adições e as atualizações é:

    user-sync –t --strategy push --process-groups --users group updated_adobe_users

Repare no `--strategy push` na linha de comando: ele IMPEDE que o User Sync
tente ler primeiro o diretório-no lado da Adobe, mas envie as atualizações
para a Adobe.

Repare também no `-t` na linha de comando para executar em "modo de teste".  Se as ações aparecerem
conforme o esperado, remova -t para que o User Sync faça as alterações.

Quando `--strategy push` for especificado, os usuários serão enviados para a Adobe com todos os seus 
grupos mapeados *adicionados* e todos os grupos mapeados em que eles não devem estar são *removidos*.  
Dessa forma, mover um usuário de um grupo de diretórios para outro, quando eles têm diferentes 
mapeamentos, fará com que o usuário seja ativado no lado da Adobe no próximo envio.

Essa abordagem não exclui nem remove contas, mas revoga
o acesso a todos os produtos e licenças gratuitas.  Para excluir contas, é necessária uma abordagem diferente, 
descrita na próxima seção.

O processo que sustenta essa abordagem consiste nas seguintes etapas:

- Sempre que você adiciona um novo usuário ou altera os grupos de um usuário no diretório (incluindo 
a remoção de todos os grupos, o que basicamente desativa todos os direitos do produto), também
adiciona esse usuário ao grupo “updated_adobe_users”.
- Uma vez por dia (ou na frequência de sua preferência), você executa um trabalho de sincronização com os parâmetros
mostrados acima.
- Esse trabalho faz com que todos os usuários atualizados sejam criados, se necessário, e tenham seus grupos 
mapeados atualizados no lado da Adobe.
- Depois que o trabalho é executado, você remove os usuários do grupo updated_adobe_users (porque 
suas alterações foram enviadas).

A qualquer momento, você também pode executar um trabalho do User Sync em modo regular (sem-push) para obter todas as
funcionalidades do User Sync.  Isso coletará todas as alterações que possam ter faltado,
corrigirá alterações feitas sem usar o User Sync e/ou fará exclusões reais de contas.  
A linha de comando ficaria assim:

    user-sync --process-groups --users mapped --adobe-only-user-action remove


### Uso de um arquivo para ativar notificações automáticas do User Sync

Você pode usar um arquivo como a entrada para o User Sync.  Neste caso, o próprio diretório
não é acessado pelo User Sync.  Você pode criar os arquivos (um para adições e atualizações,
outro para exclusões) manualmente ou usando um script que obtenha informações de
alguma outra fonte.

Crie um arquivo “users-file.csv” com informações sobre os usuários a serem adicionados ou atualizados. Um exemplo do
arquivo é:

    firstname,lastname,email,country,groups,type,username,domain
    Jane 1,Doe,jdoe1+1@example.com,US,acrobat_users
    Jane 2,Doe,jdoe2+2@example.com,US,"cc_users,acrobat_users"

A linha de comando para fazer o push de atualizações do arquivo é:

    user-sync –t --strategy push --process-groups --users file users-file.csv

Quando quiser que as ações surtam efeito, execute sem o `-t`.

Para remover usuários, é criado um arquivo separado com formato diferente.  Um exemplo de conteúdo seria:

    type,username,domain
    adobeID,jimbo@gmail.com,
    enterpriseID,jsmith1@ent-domain-example.com,
    federatedID,jsmith2,user-login-fed-domain.com
    federatedID,jsmith3@email-login-fed-domain.com,

Cada entrada deve incluir o tipo de identidade, o email ou nome do usuário e, para um tipo de identidade federada
definida para fazer logon com o nome de usuário, o domínio.

A linha de comando para processar exclusões com base em um arquivo como este (por exemplo, remove-list.csv) é:

    user-sync -t --adobe-only-user-list remove-list.csv --adobe-only-user-action remove

A ação "remove" pode ser "remove-adobe-groups" ou "delete", para manter a conta na organização
ou excluí-la, respectivamente.  Repare também no `-t` do modo de teste.

O processo que sustenta essa abordagem consiste nas seguintes etapas:

- Sempre que você adiciona um novo usuário ou altera os grupos de um usuário no diretório (incluindo 
a remoção de todos os grupos, o que basicamente desativa todos os direitos do produto), também
adiciona uma entrada ao "users-file.csv" que inclui os grupos em que o usuário deve estar. Podem ser
mais ou menos grupos do que o número atual.
- Sempre que um usuário precisar ser removido, adicione uma entrada ao arquivo "remove-list.csv".
- Uma vez por dia (ou na frequência de sua preferência), você executa os dois trabalhos de sincronização com os parâmetros
mostrados acima (um para adições e atualizações, outro para exclusões).
- Esses trabalhos fazem com que todos os usuários atualizados tenham seus grupos mapeados atualizados no lado da Adobe 
e com que os usuários removidos sejam removidos do lado da Adobe.
- Depois que o trabalho for executado, limpe os arquivos (porque suas alterações foram enviadas) para se preparar para o
próximo lote.

---

[Seção anterior](usage_scenarios.md)  \| [Próxima seção](deployment_best_practices.md)

