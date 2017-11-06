---
layout: default
lang: bp
nav_link: Configuração de User Sync
nav_level: 2
nav_order: 30
---

# Configuração da ferramenta User Sync

## Nesta seção
{:.“no_toc”}

* Marcador TOC
{:toc}

---

[Seção anterior](setup_and_installation.md)  \| [Próxima seção](command_parameters.md)

---

A operação da ferramenta User Sync é controlada por um conjunto de
arquivos de configuração com os seguinte nomes de arquivos, localizados (por padrão) na mesma
pasta que o executável da linha-de comando.

| Arquivo de configuração | Finalidade |
|:------|:---------|
| user-sync-config.yml | Obrigatório. Contém opções de configuração que definem o mapeamento de grupos de diretórios para configurações de produtos e grupos de usuários da Adobe e que controlam o comportamento da atualização.  Também contém referências a outros arquivos de configuração.|
| connector&#x2011;umapi.yml&nbsp;&nbsp; | Obrigatório. Contém credenciais e informações de acesso para chamar a API de gerenciamento de usuários da Adobe. |
| connector-ldap.yml | Obrigatório. Contém credenciais e informações para acessar o diretório corporativo. |
{: .bordertablestyle }


Se precisar configurar o acesso a grupos da Adobe em outras organizações que
lhe concederam acesso, você poderá incluir arquivos de configuração
adicionais. Para obter detalhes, consulte as
[instruções avançadas de configuração](advanced_configuration.md#accessing-groups-in-other-organizations)
abaixo.

## Definir arquivos de configuração

Exemplos dos três arquivos obrigatórios são fornecidos na pasta `config
files - basic` no artefato da versão
`example-configurations.tar.gz`:

```text
1 user-sync-config.yml
2 connector-umapi.yml
3 connector-ldap.yml
```

Para criar sua própria configuração, copie os arquivos de exemplo na
pasta raiz do User Sync e renomeie-os (para eliminar o número
à frente). Use um-editor de texto simples para personalizar os
arquivos de configuração copiados para o seu ambiente e modelo de uso. Os
exemplos contêm comentários que mostram todos os itens de configuração
possíveis. Você pode desfazer comentários de itens que precisar utilizar.

Os arquivos de configuração estão no [formato YAML](http://yaml.org/spec/)
e usam o sufixo `yml`. Ao editar o YAML, lembre-se de algumas
regras importantes:

- As seções e a hierarquia no arquivo são baseadas em
recuo. Você deve usar caracteres de ESPAÇO para o recuo. Não
use caracteres de TABULAÇÃO.
- O caractere de hífen (-) é usado para formar uma lista de valores. Por
exemplo, o parâmetro abaixo define uma lista chamada “adobe\_groups”
que contém dois itens.

```YAML
adobe_groups:
  - Photoshop Users
  - Lightroom Users
```

Observe que isso pode parecer confuso se a lista contiver apenas
um item.  Por exemplo:

```YAML
adobe_groups:
  - Photoshop Users
```

## Criar e proteger arquivos de configuração de conexão

Os dois arquivos de configuração de conexão armazenam as credenciais que
fornecem ao User Sync acesso ao Adobe Admin Console e ao seu
seu diretório LDAP corporativo. Para isolar as informações
confidenciais necessárias para se conectar aos dois sistemas, todos os
detalhes reais de credenciais são restritos a esses dois arquivos. **Mantenha-os
devidamente protegidos**, conforme descrito na seção
[Recomendações de segurança](deployment_best_practices.md#security-recommendations) deste
documento.

Existem três técnicas suportadas pelo User Sync para proteger as credenciais.

1. As credenciais podem ser colocadas diretamente nos arquivos connector-umapi.yml e connector-ldap.yml e os arquivos podem ser protegidos com controle de acesso do sistema operacional.
2. As credenciais podem ser colocadas no repositório protegido de credenciais do sistema operacional e referenciadas pelos dois arquivos de configuração.
3. Os dois arquivos na sua totalidade podem ser armazenados de forma segura ou criptografados, e um programa que retorna seus conteúdos é referenciado pelo arquivo de configuração principal.


Os arquivos de exemplos de configurações incluem entradas que ilustram cada uma
dessas técnicas.  Mantenha apenas um conjunto de itens de configuração
e comente ou remova os demais.

### Configurar conexão com o Adobe Admin Console (UMAPI)

Depois de obter acesso e configurar uma integração com o gerenciamento
de usuários no
[Portal do desenvolvedor](https://www.adobe.io/console/) do Adobe I/O, anote
os seguintes itens de configuração que você criou ou que
foram atribuídos à sua organização:

- ID da organização
- Chave de API
- Segredo do cliente
- ID da conta técnica
- Certificado particular

Abra a sua cópia do arquivo connector-umapi.yml em um editor de-texto
simples e insira esses valores na seção “enterprise”:

```YAML
enterprise:
  org_id: "Organization ID goes here"
  api_key: "API key goes here"
  client_secret: "Client Secret goes here"
  tech_acct: "Tech Account ID goes here"
  priv_key_path: "Path to Private Certificate goes here"
```

**Observação:** confirme se o arquivo de chave privada está no local
especificado em `priv_key_path` e se é somente leitura para a
conta de usuário que executar a ferramenta.

No User Sync 2.1 ou posterior, existe outra alternativa em vez de armazenar a chave privada em um arquivo separado; você pode colocar
a chave privada diretamente no arquivo de configuração.  Em vez de usar a chave
`priv_key_path`, use `priv_key_data` da seguinte forma:

	  priv_key_data: |
	    -----BEGIN RSA PRIVATE KEY-----
	    MIIJKAIBAAKCAge85H76SDKJ8273HHSDKnnfhd88837aWwE2O2LGGz7jLyZWSscH
	    ...
	    Fz2i8y6qhmfhj48dhf84hf3fnGrFP2mX2Bil48BoIVc9tXlXFPstJe1bz8xpo=
	    -----END RSA PRIVATE KEY-----

No User Sync 2.2 ou posterior, existem alguns parâmetros adicionais para controlar
o tempo limite e as novas tentativas de conexão.  Teoricamente, eles nunca precisariam ser usados; no entanto,
caso haja alguma situação incomum, você poderá defini-los na seção `server`:

  server:
    timeout: 120
    retries: 3

`timeout` define o tempo máximo de espera, em segundos, para que uma chamada seja concluída.
`retries` define o número de vezes para tentar uma operação novamente se ela falhar devido a um-problema não específico, como erro ou tempo limite do servidor.

### Configurar conexão com o seu diretório corporativo

Abra a sua cópia do arquivo connector-ldap.yml em um editor de-texto
simples e defina os seguintes valores para permitir o acesso ao sistema
de diretórios da sua empresa:

```
username: "username-goes-here"
password: "password-goes-here"
host: "FQDN.of.host"
base_dn: "base_dn.of.directory"
```

Consulte a seção [Recomendações de segurança](deployment_best_practices.md#security-recommendations) para
obter detalhes sobre como armazenar a senha de forma mais segura no User Sync versão 2.1 ou posterior.

## Opções de configuração

O arquivo de configuração principal, user-sync-config.yml, é dividido
em várias seções principais: **adobe_users**, **directory_users**,
**limits** e **logging**.

- A seção **adobe_users** especifica como a ferramenta User Sync
se conecta ao Adobe Admin Console por meio da API de gerenciamento
de usuários. Ela deve apontar para o arquivo de configuração separado e seguro
que armazena as credenciais de acesso.  Isso é definido no campo umapi do
campo conectores.
    - A seção adobe_users também pode conter exclude_identity_types, 
exclude_adobe_groups e exclude_users, que limitam o escopo de usuários
afetado pelo User Sync.  Consulte a seção
[Proteção de contas específicas contra exclusão do User Sync](advanced_configuration.md#protecting-specific-accounts-from-user-sync-deletion)
que descreve esse processo mais detalhadamente.
- A subseção **directory_users** contém duas subseções,
connectors e groups:
    - A subseção **connectors** aponta para o arquivo de configuração
separado e protegido que armazena as credenciais de acesso para o
seu diretório corporativo.
    - A seção **groups** define o mapeamento entre seus
grupos de diretórios e as configurações de produtos e grupos
de usuários da Adobe.
    - **directory_users** também pode conter chaves que definem o código do país
e o tipo de identidade padrão.  Consulte os arquivos de exemplos de configurações para obter detalhes.
- A seção **limits** define o valor `max_adobe_only_users` que 
impede o User Sync de atualizar ou excluir contas de usuários da Adobe se 
houver mais do que o valor especificado de contas que aparecem na 
organização Adobe, mas não no diretório. Esse
limite impede a remoção de um grande número de contas
em caso de erros de configuração ou outros erros.  Este item é obrigatório.
- A seção **logging** especifica um caminho de trilha de auditoria e
controla a quantidade de informações gravadas no registro.

### Configurar arquivos de conexão

O principal arquivo de configuração do User Sync contém apenas os nomes dos
arquivos de configuração de conexão que realmente contêm as
credenciais de conexão. Isso isola as informações confidenciais,
permitindo que você proteja os arquivos e limite o acesso a eles.

Forneça os apontadores para os arquivos de configuração de conexão nas seções
**adobe_users** e **directory_users** :

```
adobe_users:
  connectors:
    umapi: connector-umapi.yml

directory_users:
  connectors:
    ldap: connector-ldap.yml
```

### Configurar mapeamento de grupos

Antes de sincronizar grupos de usuários e direitos, você deve
criar grupos de usuários e configurações de produtos no
Adobe Admin Console e grupos correspondentes em seu
diretório corporativo, conforme descrito em
[Configurar sincronização de acesso ao produto](setup_and_installation.md#set-up-product-access-synchronization).

**OBSERVAÇÃO:** todos os grupos devem existir e ter os nomes especificados em
ambos os lados. O User Sync não cria grupos em nenhum dos lados;
se um grupo nomeado não for encontrado, o User Sync registrará um erro.

A seção **groups** em **directory_users** deve ter uma entrada para
cada grupo de diretórios corporativos que representa o acesso a um
produto ou produtos da Adobe. Para cada entrada de grupo, liste as configurações de produtos
para as quais os usuários desse grupo tenham acesso
concedido. Por exemplo:

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - "Default Acrobat Pro DC configuration"
  - directory_group: Photoshop
    adobe_groups:
      - "Default Photoshop CC - 100 GB configuration"
      - "Default All Apps plan - 100 GB configuration"
```

Os grupos de diretórios podem ser mapeados para *configurações de produtos*
ou *grupos de usuários*. Uma entrada `adobe_groups` pode nomear cada tipo
de grupo.

Por exemplo:

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - Default Acrobat Pro DC configuration
  - directory_group: Acrobat_Accounting
    adobe_groups:
      - Accounting_Department
```

### Configurar limites

As contas de usuários são removidas do sistema da Adobe quando
os usuários correspondentes não estão presentes no diretório e a ferramenta
é chamada com uma das opções

- `--adobe-only-user-action delete`
- `--adobe-only-user-action remove`
- `--adobe-only-user-action remove-adobe-groups`

Se a sua organização tiver um grande número de usuários no
diretório corporativo e o número de usuários lidos durante uma sincronização
for pequeno, isso poderá indicar um erro de configuração ou uma
situação de erro.  O valor de `max_adobe_only_users` é um limite
que faz com que o User Sync suspenda a exclusão e atualização de contas existentes da Adobe
e reporte um erro, se houver
menos usuários no diretório corporativo (conforme filtrado pelos parâmetros da consulta) do que no
Adobe Admin Console.

Aumente esse valor se você espera que o número de usuários caia
mais do que o valor atual.

Por exemplo:

```YAML
limits:
  max_adobe_only_users: 200
```

Essa configuração faz com que o User Sync verifique se mais de
200 contas de usuários presentes na Adobe não foram encontradas no diretório corporativo (como filtrado) e,
nesse caso, nenhuma conta existente da Adobe é atualizada e uma mensagem de erro é registrada.

###  Configurar registros

As entradas de registro são gravadas no console no qual a ferramenta foi
chamada e, opcionalmente, em um arquivo de registro. Uma nova
entrada com um-carimbo de data e hora é gravada no registro cada vez que o User Sync
é executado.

A seção **logging** permite ativar e
desativar o registro em um arquivo e controla a quantidade de informações
gravadas no registro e na saída do console.

```YAML
logging:
  log_to_file: True | False
  file_log_directory: "path to log folder"
  file_log_level: debug | info | warning | error | critical
  console_log_level: debug | info | warning | error | critical
```

O valor de log_to_file ativa ou desativa-o registro em arquivo. As mensagens de registro são sempre
gravadas no console, independentemente da configuração de log_to_file.

Quando o registro-em arquivo está ativado, o valor de file_log_directory é
obrigatório. Ele especifica a pasta na qual as entradas do registro devem ser
gravadas.

- Forneça um caminho absoluto ou relativo para a pasta
que contém esse arquivo de configuração.
- Verifique se o arquivo e a pasta têm permissões de leitura/gravação
apropriadas.

Os valores de Log-level determinam a quantidade de informações gravadas no
arquivo de registro ou no console.

- O nível mais baixo, debug, grava a maior quantidade de informações, e o
nível mais alto, critical, grava o mínimo.
- Você pode definir diferentes valores de log-level para o arquivo e
o console.

As entradas de registro que contêm WARNING, ERROR ou CRITICAL incluem uma
descrição que acompanha o status. Por exemplo:

> `2017-01-19 12:54:04 7516 WARNING
console.trustee.org1.action - Error requestID: action_5 code:
"error.user.not_found" message: "No valid users were found in the
request"`

Neste exemplo, foi registrado um aviso em 19-01-2017 às 12:54:04
durante a execução. Uma ação causou um erro com o código
“error.user.not_found”. A descrição associada a esse
código de erro está incluída.

Você pode usar o valor de requestID para pesquisar a solicitação exata
associada a um erro reportado. No exemplo, pesquisar
“action_5” retorna o seguinte detalhe:

> `2017-01-19 12:54:04 7516 INFO console.trustee.org1.action -
Added action: {"do":
\[{"add": {"product": \["default adobe enterprise support program configuration"\]}}\],
"requestID": "action_5", "user": "cceuser2@ensemble.ca"}`

Isso fornece mais informações sobre a ação que resultou na
mensagem de aviso. Nesse caso, o User Sync tentou adicionar
“default adobe enterprise support program configuration” ao
usuário “cceuser2@ensemble.ca”. A ação de adição falhou porque o
usuário não foi encontrado.

## Exemplos de configurações

Estes exemplos mostram as estruturas dos arquivos de configuração e
ilustram os possíveis valores de configuração.

### user-sync-config.yml

```YAML
adobe_users:
  connectors:
    umapi: connector-umapi.yml
  exclude_identity_types:
    - adobeID

directory_users:
  user_identity_type: federatedID
  default_country_code: US
  connectors:
    ldap: connector-ldap.yml
  groups:
    - directory_group: Acrobat
      adobe_groups:
        - Default Acrobat Pro DC configuration
    - directory_group: Photoshop
      adobe_groups:
        - "Default Photoshop CC - 100 GB configuration"
        - "Default All Apps plan - 100 GB configuration"
        - "Default Adobe Document Cloud for enterprise configuration"
        - "Default Adobe Enterprise Support Program configuration"

limits:
  max_adobe_only_users: 200

logging:
  log_to_file: True
  file_log_directory: userSyncLog
  file_log_level: debug
  console_log_level: debug
```

### connector-ldap.yml

```YAML
username: "LDAP_username"
password: "LDAP_password"
host: "ldap://LDAP_ host"
base_dn: "base_DN"

group_filter_format: "(&(objectClass=posixGroup)(cn={group}))"
all_users_filter: "(&(objectClass=person)(objectClass=top))"
```

### connector-umapi.yml

```YAML
server:
  # This section describes the location of the servers used for the Adobe user management. Default is:
  # host: usermanagement.adobe.io
  # endpoint: /v2/usermanagement
  # ims_host: ims-na1.adobelogin.com
  # ims_endpoint_jwt: /ims/exchange/jwt

enterprise:
  org_id: "Org ID goes here"
  api_key: "API key goes here"
  client_secret: "Client secret goes here"
  tech_acct: "Tech account ID goes here"
  priv_key_path: "Path to private.key goes here"
  # priv_key_data: "actual key data goes here" # This is an alternative to priv_key_path
```

## Testar a sua configuração

Use esses casos de teste para garantir que a sua configuração funcione
corretamente e que as configurações do produto estejam corretamente
mapeadas para os grupos de segurança do seu diretório corporativo. Execute a
ferramenta no modo de teste primeiro (fornecendo o parâmetro -t), para
ver o resultado antes de efetivar a configuração.

Os exemplos a seguir usam `--users all` para selecionar os usuários, mas você pode usar
`--users mapped` para selecionar apenas os usuários em grupos de diretórios listados no seu arquivo de configuração,
ou `--users file f.csv` para selecionar um conjunto menor de usuários de teste listados em um arquivo.

###  Criação de usuários

1. Crie um ou mais usuários de teste no diretório corporativo.

2. Adicione usuários a um ou mais grupos de diretórios/segurança configurados.

3. Execute o User Sync no modo de teste. (`./user-sync -t --users all --process-groups --adobe-only-user-action exclude`)

3. Execute o User Sync fora do modo de teste. (`./user-sync --users all --process-groups --adobe-only-user-action exclude`)

4. Verifique se os usuários de teste foram criados no Adobe Admin Console.

### Atualização de usuários

1. Modifique a associação a grupos de um ou mais usuários de teste no diretório.

1. Execute o User Sync. (`./user-sync --users all --process-groups --adobe-only-user-action exclude`)

2. Verifique se os usuários de teste no Adobe Admin Console foram atualizados para
refletir a nova associação à configuração de produto.

###  Remoção de usuários

1. Remova ou desabilite um ou mais usuários de teste existentes em seu
diretório corporativo.

2. Execute o User Sync. (`./user-sync --users all --process-groups --adobe-only-user-action remove-adobe-groups`)  É recomendável executar no modo de teste (-t) primeiro.

3. Verifique se os usuários foram removidos das configurações de produto
definidas no Adobe Admin Console.

4. Execute o User Sync para remover os usuários (`./user-sync -t --users all --process-groups --adobe-only-user-action delete`). Em seguida, execute sem -t.  Cuidado: verifique se apenas o usuário desejado foi removido ao executar com -t.  Essa execução (sem -t) realmente excluirá os usuários.

5. Verifique se as contas de usuários foram removidas do Adobe Admin Console.

---

[Seção anterior](setup_and_installation.md)  \| [Próxima seção](command_parameters.md)