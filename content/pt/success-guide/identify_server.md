---
weight: 140
title: Configuração do Servidor
type: docs
---

# Identificação e configuração do servidor em que o User Sync será executado

O User Sync pode ser executado manualmente, mas a maioria das empresas automatiza o User Sync para ser executado pelo menos uma vez por dia.

Ele precisa ser instalado e executado em um servidor que:

  - Possa acessar a Adobe por meio da internet
  - Possa acessar seu serviço de diretório como LDAP ou AD
  - Esteja protegido e seguro (suas credenciais administrativas serão armazenadas ou acessadas nele)
  - Permaneça funcionando e seja confiável
  - Tenha recursos de backup e recuperação
  - Possa enviar emails para envio de relatórios pelos administradores do User Sync

Você precisará trabalhar com seu departamento de TI para identificar tal servidor e acessá-lo.
Unix, OSX ou Windows são todos compatíveis com o User Sync.

Aloque um servidor para a execução do User Sync.  Observe que você pode fazer configurações e testes iniciais usando o User Sync em outros computadores, como seu laptop ou desktop, desde que atenda aos critérios acima.

Faça logon no computador com recursos suficientes para instalar e executar o User Sync.  Normalmente, pode ser uma conta-sem privilégios.
