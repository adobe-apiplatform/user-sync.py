---
layout: default
lang: bp
nav_link: Práticas recomendadas de implantação
nav_level: 2
nav_order: 70
parent: user-manual
page_id: deployment
---


# Práticas recomendadas de implantação

## Nesta seção
{:."no_toc"}

* Marcador TOC
{:toc}

---

[Seção anterior](advanced_configuration.md)

---

A ferramenta User Sync foi desenvolvida para funcionar com pouca ou nenhuma
interação humana, desde que configurada corretamente. É possível utilizar um
agendador em seu ambiente para executar a ferramenta com a
frequência necessária.

- As primeiras execuções da ferramenta User Sync podem demorar,
dependendo de quantos usuários precisam ser adicionados no Adobe
Admin Console. Recomendamos realizar essas execuções iniciais
manualmente, antes de configurar para execução como uma tarefa agendada,
para evitar a execução de várias instâncias.
- As execuções posteriores são, geralmente, mais rápidas, uma vez que só precisam
atualizar os dados do usuário conforme necessário. A frequência escolhida para
executar o User Sync depende da frequência com que o seu
diretório corporativo é alterado, e da rapidez com que você deseja que as alterações
sejam exibidas no lado da Adobe.
- Não é recomendado executar o User Sync em intervalos inferiores a 2 horas.

<a name="security-recommendations"></a>
## Recomendações de segurança

Dada a natureza dos dados nos arquivos de registro e configuração,
um servidor deve estar dedicado para essa tarefa e bloqueado com
as práticas recomendadas do setor. Para este aplicativo, é recomendável
usar um servidor que esteja protegido pelo firewall
corporativo. Apenas os usuários com privilégios devem poder se conectar
a essa máquina. Deve-se criar uma conta de serviço do sistema com
privilégios restritos, destinada especificamente para executar o
aplicativo e gravar arquivos de registro no sistema.

O aplicativo realiza solicitações GET e POST da API de gerenciamento
de usuários a um terminal HTTPS. Ele constrói dados JSON
para representar as alterações que precisam ser gravadas no Admin
Console, e anexa os dados ao corpo de uma solicitação POST para a
API de gerenciamento de usuários.

Para proteger a disponibilidade dos sistemas de identidade do usuário back-end da Adobe,
a API de gerenciamento de usuários limita o acesso do cliente
aos dados.  Os limites se aplicam ao número de chamadas que um
cliente individual pode realizar dentro de um intervalo de tempo,
e os limites globais se aplicam ao acesso de todos os clientes no período. A
ferramenta User Sync implementa lógica de retirada e de repetição para evitar que o
script atinja continuamente a API de gerenciamento de usuários ao
alcançar o limite de taxa. É comum ver mensagens no
console indicando que o script foi pausado por um curto período
antes de tentar executar novamente.

A partir do User Sync 2.1, existem duas técnicas adicionais disponíveis
para proteção das credenciais.  A primeira utiliza o repositório de credenciais do sistema operacional
para armazenar valores de credenciais de configuração individuais.  A segunda usa
um mecanismo que você deve definir para armazenar com segurança todo o arquivo de configuração para umapi
e/ou ldap, que inclui todas as credenciais necessárias.  Isso será
explicado em mais detalhes nas próximas duas seções.

### Armazenar as credenciais no repositório de nível do SO

Para configurar o User Sync para extrair as credenciais do repositório de credenciais do SO Python Keyring, defina os arquivos connector-umapi.yml e connector-ldap.yml da seguinte forma:

connector-umapi.yml

	server:
	
	enterprise:
	  org_id: sua id da organização
	  secure_api_key_key: umapi_api_key
	  secure_client_secret_key: umapi_client_secret
	  tech_acct: sua conta técnica account@techacct.adobe.com
	  secure_priv_key_data_key: umapi_private_key_data

Observe as alterações de `api_key`, `client_secret` e `priv_key_path` para `secure_api_key_key`, `secure_client_secret_key` e `secure_priv_key_data_key`, respectivamente.  Esses valores alternativos de configuração fornecem os nomes de chaves a serem pesquisados no conjunto de chaves do usuário (ou serviço equivalente em outras plataformas) para recuperar os valores reais das credenciais.  Neste exemplo, os nomes de chaves das credenciais são `umapi_api_key`, `umapi_client_secret` e `umapi_private_key_data`.

O conteúdo do arquivo de chave privada é usado como valor para `umapi_private_key_data` no repositório de credenciais.  Isso só pode ser feito em plataformas diferentes do Windows.  Consulte abaixo para saber como proteger o
arquivo de chave privada no Windows.

Os valores das credenciais serão pesquisados no repositório seguro usando org_id como o valor do nome de usuário e os nomes das chaves no arquivo de configuração como o nome de chave.

Uma variação dessa abordagem está disponível (na versão 2.1.1 do User Sync ou posterior) para criptografar o
arquivo de chave privada usando a representação criptografada RSA padrão para chaves privadas (conhecida como
formato PKCS#8).  Essa abordagem deve ser usada no Windows pois o repositório seguro do Windows não é
capaz de armazenar strings maiores do que 512 bytes, o que impede o seu uso com chaves privadas. Essa abordagem
também pode ser usada nas outras plataformas, se desejado.

Para armazenar a chave privada em formato criptografado, proceda conforme mostrado a seguir.  Primeiro, crie uma versão
criptografada do arquivo de chave privada.  Selecione uma frase secreta e criptografe o
arquivo de chave privada:

    openssl pkcs8 -in private.key -topk8 -v2 des3 -out private-encrypted.key

No Windows, é necessário executar openssl a partir do Cygwin ou outro provedor; ele não está incluso
na distribuição padrão do Windows.

Depois, use os itens de configuração a seguir no connector-umapi.yml.  Os dois últimos itens abaixo fazem com que
a frase secreta de descriptografia seja obtida a partir do repositório de credenciais seguro, e referencia o arquivo
de chave privada criptografado, respectivamente:

	server:
	
	enterprise:
	  org_id: sua id da organização
	  secure_api_key_key: umapi_api_key
	  secure_client_secret_key: umapi_client_secret
	  tech_acct: sua conta técnica account@techacct.adobe.com
	  secure_priv_key_pass_key: umapi_private_key_passphrase
	  priv_key_path: private-encrypted.key

Por último, adicione a frase secreta ao repositório seguro como uma entrada com o nome de usuário, ou o url, como a Id da organização, o nome de
chave como `umapi_private_key_passphrase` para corresponder à entrada do arquivo de configuração `secure_priv_key_pass_key`, e o valor
como a frase secreta.  (Também é possível embutir a chave privada criptografada colocando os dados no arquivo
connector-umapi.yml sob a chave `priv_key_data` em vez de usar `priv_key_path`.)

Isso encerra a descrição da variante na qual a criptografia de chave privada RSA é usada.

connector-ldap.yml

	username: "o nome de usuário da conta ldap"
	secure_password_key: ldap_password 
	host: "ldap://ldap server name"
	base_dn: "DC=nome do domínio,DC=com"

A senha de acesso LDAP será consultada usando o nome de chave especificado
(`ldap_password` nesse exemplo) com o usuário sendo o valor de configuração do
nome de usuário especificado.

As credenciais são armazenadas no repositório seguro subjacente do sistema operacional.  O sistema de armazenamento específico depende do sistema operacional.

| SO | Repositório de credenciais |
|------------|--------------|
| Windows | Cofre de credenciais do Windows |
| Mac OS X | Conjunto de chaves |
| Linux | Serviço secreto de Freedesktop ou KWallet |
{: .bordertablestyle }

No Linux, o aplicativo de armazenamento seguro geralmente é instalado e configurado pelo fornecedor do SO.

As credenciais são adicionadas ao armazenamento seguro do SO e recebem o nome de usuário e a id da credencial que serão usados para especificar a credencial.  Para credenciais umapi, o nome de usuário é a id da organização.  Para a credencial da senha LDAP, o nome de usuário é o nome de usuário LDAP.  Escolha qualquer identificador desejado para as credenciais específicas; deve haver correspondência entre o que está no repositório de credenciais e o nome usado no arquivo de configuração.  Sugestões de valores para os nomes de chaves são mostrados nos exemplos acima.


### Armazenar arquivos de credenciais em sistemas de gerenciamento externos

Como alternativa para o armazenamento de credenciais no repositório de credenciais local, é possível integrar o User Sync a outro sistema ou mecanismo de criptografia.  Para oferecer suporte a essas integrações, você pode armazenar todos os arquivos de configuração para umapi e ldap externamente em outro sistema ou formato.

Isso é feito especificando no arquivo de configuração principal do User Sync um comando para execução cuja saída é usada como conteúdo do arquivo de configuração umapi ou ldap.  É necessário fornecer o comando que coleta as informações da configuração e as envia para a saída padrão no formato yaml, correspondendo com os dados que o arquivo de configuração contém.

Para fazer essa configuração, use os itens a seguir no arquivo de configuração principal.


user-sync-config.yml (mostrando apenas parcialmente o arquivo)

	adobe_users:
	   connectors:
	      # umapi: connector-umapi.yml   # em vez dessa referência de arquivo, use:
	      umapi: $(read_umapi_config_from_s3)
	
	directory_users:
	   connectors:
	      # ldap: connector-ldap.yml # em vez dessa referência de arquivo, use:
	      ldap: $(read_ldap_config_from_server)
 
O formato geral para as referências de comandos externos é

	$(command args)

Os exemplos acima pressupõem que existem comandos com os nomes `read_umapi_config_from_s3`
e `read_ldap_config_from_server` fornecidos por você.

O User Sync inicia um shell que
executa o comando.  A saída padrão do comando é capturada e
usada como arquivo de configuração umapi ou ldap.

O comando é executado com o diretório de trabalho como diretório que contém o arquivo de configuração.

Se o comando for finalizado de forma anormal, o User Sync será encerrado com um erro.

O comando pode fazer referência a um programa, ou script, novo ou existente.

Observação: ao usar essa técnica para o arquivo connector-umapi.yml, incorpore os dados da chave privada no connector-umapi-yml diretamente usando a chave priv_key_data e o valor da chave privada.  Se você usar priv_key_path e o nome de arquivo que contém a chave privada, também será necessário armazenar a chave privada em algum local 
seguro e ter um comando que a recupere na referência do arquivo.

## Exemplos de tarefas agendadas

Use um agendador fornecido pelo sistema operacional para executar
a ferramenta User Sync periodicamente, conforme exigido pela sua
empresa. Esses exemplos ilustram como pode ser feita a configuração dos
agendadores do Unix e Windows.

É possível configurar um arquivo de comando para executar a UserSync com
parâmetros específicos e, em seguida, extrair um resumo do registro e enviá-lo por email
para os responsáveis pelo monitoramento do processo de sincronização. Esses
exemplos funcionam melhor com o nível de registro do console definido como INFO

```YAML
logging:
  console_log_level: info
```

### Executar com análise de registro no Windows

O exemplo a seguir mostra como configurar um arquivo em lotes `run_sync.bat` no
Windows.

```sh
python C:\\...\\user-sync.pex --users file users-file.csv --process-groups | findstr /I "WARNING ERROR CRITICAL ---- ==== Number" > temp.file.txt
rem email the contents of temp.file.txt to the user sync administration
sendmail -s “Adobe User Sync Report for today” UserSyncAdmins@example.com < temp.file.txt
```

*OBSERVAÇÃO*: embora seja mostrado o uso do `sendmail` nesse exemplo, não
existe uma ferramenta padrão de linha-de comando de email no Windows.  Há diversas
disponíveis comercialmente.

### Executar com análise de registro nas plataformas Unix

O exemplo a seguir mostra como configurar um arquivo shell
`run_sync.sh` no Linux ou Mac OS X:

```sh
user-sync --users file users-file.csv --process-groups | grep "CRITICAL\|WARNING\|ERROR\|=====\|-----\|number of\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” UserSyncAdmins@example.com
```

### Programar uma tarefa do UserSync

#### Cron

Esta entrada no crontab do Unix executa a ferramenta User Sync às 4h,
todo dia:

```text
0 4 * * * /path/to/run_sync.sh
```

O cron também pode ser configurado para enviar os resultados por email para um usuário específico ou para uma
lista de emails. Consulte a documentação do cron para o seu sistema
para obter mais detalhes.

#### Agendador de tarefas do Windows

Este comando utiliza o agendador de tarefas do Windows para executar a ferramenta
User Sync todo dia a partir das 16h:

```text
schtasks /create /tn "Adobe User Sync" /tr C:\path\to\run_sync.bat /sc DAILY /st 16:00
```

Consulte a documentação do agendador de tarefas do Windows (`help
schtasks`) para obter mais detalhes.

Existe também uma interface gráfica do usuário (GUI) para gerenciar tarefas agendadas do Windows. É possível
encontrar o Agendador de tarefas no painel de controle administrativo
do Windows.

---

[Seção anterior](advanced_configuration.md)
