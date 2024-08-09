---
weight: 150
title: Instalação do User Sync
type: docs
---

# Instalação do User Sync

Quando tiver acesso ao servidor em que o User Sync será executado, escolha o diretório onde instalar e operar o User Sync.

No Windows, você precisará instalar o Python.  Na data deste documento, a versão 2.7.13 é a recomendável.  O Windows e o Python precisam ter a versão de 64 bits.

No Windows, é provável que você precise definir uma variável de ambiente PEX_ROOT em C:\user_sync\.pex.  Ela é necessária para resolver a questão de limites de comprimento de nomes de caminhos no Windows.

Etapas iniciais:

Defina um usuário e um diretório de arquivo para instalar e executar o User Sync.  Por exemplo, criaremos uma pasta /home/user_sync/user_sync_tool e um usuário user_sync.  No Windows, um exemplo seria C:\Users\user_sync\user_sync_tool.

Somente no Windows: defina a variável de ambiente **PEX\_ROOT** para **C:\user_sync\.pex**.

Somente no Windows: instale o Python 2.7.13 (ou posterior na série 2.7), 64 bits. 

As próximas seções mostram o processo de instalação.

Para encontrar a versão mais recente:  Comece aqui: 
[https://github.com/adobe-apiplatform/user-sync.py](https://github.com/adobe-apiplatform/user-sync.py)

![instalação](/user-sync.py/images/pt/install_finding_releases.png)

Selecione “release”

![instalação2](/user-sync.py/images/pt/install_release_screen.png)

Baixe example-configurations.tar.gz, Guia do User Sync e crie sua plataforma osx, ubuntu, windows ou centos.

Extraia o arquivo user-sync (ou user-sync.pex) do arquivo e coloque-o em seu SO na pasta.  No nosso exemplo, ficaria assim /home/user_sync/user_sync_tool/user-sync ou C:\Users\user_sync\user_sync_tool\user-sync.pex.

No arquivo example-configurations.tar.gz há um diretório **config files - basic**.  Desta pasta, extraia os três primeiros arquivos e coloque-os na pasta user_sync_tool.  

Em seguida, renomeie os três arquivos de exemplo de configurações removendo os números “1”, “2” e “3” do início de cada nome.  Editaremos esses arquivos para criar os arquivos de configuração reais do User Sync.

![instalação2](/user-sync.py/images/pt/install_config_files.png)
