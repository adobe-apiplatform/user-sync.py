---
weight: 130
title: Integração Adobe.io
type: docs
---

# Configuração de uma integração com o Adobe.io

A Adobe desenvolveu um protocolo seguro para aplicativos integrarem-se com APIs da Adobe e o User Sync no aplicativo em questão.

As etapas de configuração estão documentadas.  Para obter informações completas sobre o processo de configuração de integração e requisitos de certificação, consulte [aqui](https://www.adobe.io/apis/cloudplatform/console/authentication.html)

- Você precisa criar ou obter um certificado digital para assinar as chamadas iniciais da API.
  - O certificado não é usado para SSL ou para qualquer outra finalidade, portanto, cadeias confiáveis e problemas de navegador não se aplicam.
  - Você mesmo pode criar o certificado usando ferramentas gratuitas ou comprando uma (ou conseguir uma com seu departamento de TI).
  - Você precisará de um arquivo de certificado de chave pública e um de chave privada.
  - Proteja o arquivo de chave privada como faria com uma senha de raiz.
- Depois de configurado, o console do Adobe.io exibe todos os valores necessários.  Você os copiará em seu arquivo de configuração do User Sync.
- Você também precisará adicionar o arquivo de chave privada à configuração do User Sync.

Obtenha ou crie um certificado de assinatura digital.  Consulte [as instruções para criação de certificado](https://www.adobe.io/apis/cloudplatform/console/authentication/createcert.html).

Use o [Adobe I/O Console](https://console.adobe.io) para adicionar o serviço de Gerenciamento de usuários a uma integração adobe.io nova ou existente para cada organização que precisar acessar (normalmente somente uma).

Anote os parâmetros de configuração para a sua integração (exemplos redigidos abaixo).  Eles serão usados em uma etapa posterior.

![img](/user-sync.py/images/setup_adobe_io_data.png)
