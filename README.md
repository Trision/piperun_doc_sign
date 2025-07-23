# Módulo para assinatura utilizando o PipeRun

Esse projeto foi criado para ser integrado a um projeto django já existente.

---
## Descrição

Este módulo fornece uma **API** para assinatura digital de documentos utilizando o PipeRun. Foi projetado para ser adicionado a um projeto Django existente, mas pode ser executado sozinho para ser testado via POSTMAN. Não tem front pois o objetivo era apenas criar os endpoints necessários para o funcionamento da API.

---

## Tecnologias utilizadas

 - Python 3.10.11
 - Django framework
 - Outras libs listadas em 'requirements.txt'

## Instalação

### 1 - Clonar o projeto
    ```bash
    git clone https://github.com/Trision/piperun_doc_sign.git
    cd piperun_doc_sign
    ```
### 2 - Criar o seu venv
    ```bash
    python -m venv .venv
    source .venv/bin/activate #Linux/macOS
    .venv\Scripts\activate
    ```
### 3 - Instalar as dependências
    ```bash
    pip install -r requirements.txt
    ```

    A partir daqui o projeto está pronto para ser rodado e testado utilizando postman.

## Integração com um projeto django já existente

### 1 - Configuração

Na pasta principal do seu projeto django, dentro de settings.py o seguinte deve ser feito.
        INSTALLED_APPS = [
            # ...
            'rest_framework',
            'doc_sign.apps.DocSignConfig',
        ]
Agora dentro do arquivo urls.py o seguinte deve ser feito

    urlpatterns = [
        # ...
        path('admin/', admin.site.urls),
        path('api/pipe/', include("doc_sign.urls"))#Adicione essa linha lá
    ]

### 2 - Adição da KEY no .ENV

    PIPE_KEY=A SUA KEY AQUI

# Uso da API

- Endpoint para fazer o upload do arquivo da oportunidade do pipe
    ```bash
        http://localhost:8000/api/pipe/enviar_documento
    ```
- Endpoint para disponibilzar o documento para assinatura
    ```bash
        http://localhost:8000/api/pipe/liberar_assinatura
    ```
- Endpoint para enviar para assinarem
    ```bash
        http://localhost:8000/api/pipe/enviar_assinatura
    ```
- Endpoint para listar os documentos da oportunidade
    ```bash
        http://localhost:8000/api/pipe/listar_documentos/<int:id_oportunidade>
    ```