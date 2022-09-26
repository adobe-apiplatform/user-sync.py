---
layout: default
lang: bp
nav_link: Integração Adobe.io
nav_level: 2
nav_order: 150
parent: success-guide
page_id: adobeio-setup
---

# Configuração de uma integração com o Adobe.io

[Seção anterior](decide_deletion_policy.md) \| [Voltar ao sumário](index.md) \| [Próxima seção](identify_server.md)

A Adobe desenvolveu um protocolo seguro para aplicativos integrarem-se com APIs da Adobe e o User Sync no aplicativo em questão.

As etapas de configuração estão documentadas.  Para obter informações completas sobre o processo de configuração de integração e requisitos de certificação, consulte [aqui](https://www.adobe.io/apis/cloudplatform/console/authentication.html)

- Você precisa criar ou obter um certificado digital para assinar as chamadas iniciais da API.
  - O certificado não é usado para SSL ou para qualquer outra finalidade, portanto, cadeias confiáveis e problemas de navegador não se aplicam.
  - Você mesmo pode criar o certificado usando ferramentas gratuitas ou comprando uma (ou conseguir uma com seu departamento de TI).
  - Você precisará de um arquivo de certificado de chave pública e um de chave privada.
  - Proteja o arquivo de chave privada como faria com uma senha de raiz.
- Depois de configurado, o console do Adobe.io exibe todos os valores necessários.  Você os copiará em seu arquivo de configuração do User Sync.
- Você também precisará adicionar o arquivo de chave privada à configuração do User Sync.

&#9744; Obtenha ou crie um certificado de assinatura digital.  Consulte [as instruções para criação de certificado](https://www.adobe.io/apis/cloudplatform/console/authentication/createcert.html).

&#9744; Use o [Adobe I/O Console](https://console.adobe.io) para adicionar o serviço de Gerenciamento de usuários a uma integração adobe.io nova ou existente para cada organização que precisar acessar (normalmente somente uma).  

&#9744; Anote os parâmetros de configuração para a sua integração (exemplos redigidos abaixo).  Eles serão usados em uma etapa posterior.


![img](images/setup_adobe_io_data.png)


[Seção anterior](decide_deletion_policy.md) \| [Voltar ao sumário](index.md) \| [Próxima seção](identify_server.md)
