# Changelog
 
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2025-07-23

- EndPoints da API criados
    - Upload de documentos
    - Disponibilizar para assinatura o documento
    - Enviar para assinatura o documento
- Integração com o google storage criado
    - Upload no google storage feito automático junto do upload do documento
    - No arquivo gcpstorage.py tem a classe do GCP
        - Upload
        - Download
        - Check - Verifica a existência do arquivo do blob selecionado
        - List - Lista o blob selecionado
        - Generate URL - Gera uma url pública para o arquivo ser visto - Duração padrão de 5 anos
- Integração com o PipeRun criada
    - No arquivo pipApi.py tem a classe das funções que interagem com o piperun
- Comentários no código
    - A maior parte deles é o processo de raciocinio que eu tive enquanto montava essa API
- WebHook criados e funcionais
    - Recebe um POST sempre que uma assinatura é feita em algum documento(isso é configurado dentro do piperun)
        - Com base no ID da oportunidade, pesquisa no models os arquivos que tem esse ID de oportunidade e verifica o models de assinaturas
        para realizar uma pesquisa em cada uma delas para saber qual foi assinada.
    - Recebe um POST assim que uma assinatura for completa, com base no ID da oportunidade pesquisa no models a quantidade de assinaturas com status=1(Assinado), e se a quantidade de assinatura com status=1 for igual a quantidade de signatarios no model de documento quer dizer que o documento está
    100% assinado(Pode colocar algum tipo de notificação por whatsapp caso queira avisar o cliente etc)

