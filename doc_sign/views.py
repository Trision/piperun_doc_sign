from django.shortcuts import render, get_object_or_404
from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from num2words import num2words
from .models import Documento, Assinatura
from django.views.decorators.csrf import csrf_exempt
from .pipApi import PipeApi
import json
from datetime import datetime


pipe    = PipeApi()# Colocar como arg uma API_KEY para outras empresas consiguirem usar
agora   = datetime.now()

def cria_arquivo(bytes, destination, filename):
    path_file = destination + filename
    with open(path_file, 'wb') as arquivo:
        arquivo.write(bytes)
        arquivo.close()
    return path_file

@csrf_exempt
def recebe_doc(request):#Recebe os dados para criar um doc, ou um doc completo
    if request.method == "POST":
        # {'success': True, 'message': 'OK', 'data': [{'id': 38961785, 'account_id': 10216, 'user_id': 51859, 'deal_id': 49589772, 'email_id': None, 'template_email_id': None, 'call_id': None, 'name': 'teste.pdf', 'url': 'https://api.pipe.run/v1/files/izgot4pni9wgk880oogwo4wg84o8gww/download', 'url_aws': 'https://assets.pipe.run/account/10216/deals/49589772/files/hpebcm24v808ckgwg404wo0w4gsw4gk.pdf', 'format': 'pdf', 'description': None, 'size': 15576, 'hash': 'izgot4pni9wgk880oogwo4wg84o8gww', 'public_form_file': None, 'created_at'w', 'public_form_file': None, 'created_at': '2025-07-03 15:48:20'}]}
        post_body       = request.POST
        cpf             = post_body.get('cpf')
        deal_id         = post_body.get('id_oportunidade')
        arquivo         = request.FILES.get('minuta')
        conteudo        = arquivo.read()
        filename        = arquivo.name
        local_path      = cria_arquivo(conteudo, './media/', filename)
        upload_return   = pipe.upload_documento(local_path, deal_id, filename)
        pipe_info       = upload_return.get('api_response')
        pipe_data       = pipe_info.get('data')[0]
        deal_id         = pipe_data.get('deal_id')
        doc_id          = pipe_data.get('id')
        doc_name        = pipe_data.get('name')
        doc_hash        = pipe_data.get('hash')
        data_cria       = str(pipe_data.get('created_at')).split(' ')
        aws_url         = pipe_data.get('url_aws')
        if pipe_info.get('success'):
            Documento.objects.create(
                cpf=cpf,
                file_name=doc_name,
                file_id=doc_id,
                file_hash=doc_hash,
                deal_id=deal_id,
                criado_em=data_cria[0],
                gcp_path=upload_return.get('gpc_path'),
                aws_url=aws_url
            )
            return JsonResponse({'message':'Arquivo processado'},status=200)
        else:
            return JsonResponse({'message':'Erro na importação para o PipeRun!'}, status=204)
    return HttpResponse('Método não permitido!', status=415)

@csrf_exempt
def disponibilizar_assinatura(request):#Aponta para o pipe, que esse é um documento para assinar
    if request.method == "POST":
        post_body       = json.loads(request.body.decode('utf-8'))
        documento       = get_object_or_404(Documento, id=post_body.get('id_documento'))
        id_documento    = documento.file_id
        deal_id         = documento.deal_id
        filename        = documento.file_name
        assinatura      = pipe.enviar_documento(filename, id_documento, deal_id)
        if assinatura.get('success'):
            dados_assinatura        = assinatura.get('data')
            documento.signature_id  = dados_assinatura.get('id')
            documento.is_to_sign    = True
            documento.save()
            return JsonResponse({'mensagem':'Documento pronto para assinar'},status=200)
        else:
            return JsonResponse({'mensagem':'Erro ao disponibilzar para assinatura!'}, status=204)
    return HttpResponse('Método não permitido!', status=415)

@csrf_exempt
def assinar_documento(request):
    if request.method == 'POST':
        post_body           = json.loads(request.body.decode('utf-8'))
        lista_signatarios   = post_body.get('lista_signatarios')
        doc_id              = post_body.get('doc_id')
        documento           = get_object_or_404(Documento, id=doc_id)
        sign_id             = documento.signature_id
        documento.qtd_signs = len(lista_signatarios)
        documento.save()
        for signatario in lista_signatarios:
            email       = signatario.get('email')
            type_sign   = signatario.get('type')
            assinatura  = pipe.assinar_documento(sign_id, email, type_sign)
            if assinatura.get('success'):
                dados_assinatura = assinatura.get("data")
                Assinatura.objects.create(
                    email=email,
                    tipo=type_sign,
                    id_sign=sign_id,
                    id_signatario=dados_assinatura.get('id'),
                    documento=documento,
                    send_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    ip_assinatura=dados_assinatura.get('ip'),
                    status=dados_assinatura.get('status'),
                    sign_hash=dados_assinatura.get('hash')
                ).save()
            else:
                return JsonResponse({"mensagem":"Erro na hora de enviar para assinarem", "response_pipe":assinatura}, status=204)
        return JsonResponse({"mensagem":"Documento enviado para assinarem."}, status=200)
    return HttpResponse('Método não permitido!', status=415)

def listar_docs(request, deal_id):
    #Com base no models do arquivo, puxar a lista deles, e utilizar o GCP.URL para criar uma url pública para os operadores visualizarem o documento
    #Esse arquivo vai ser exibido numa parte que dá pra configurar a assinatura e as pessoas que vão assinar o documento
    if request.method == 'GET':
        documentos      = Documento.objects.filter(deal_id=deal_id)
        documentos_json = serialize('json', documentos)
        return JsonResponse({"message":"True", "documentos":json.loads(documentos_json)}, status=200)
    return HttpResponse("Método não permitido!", status=415)

@csrf_exempt
def webhook_assinatura(request):
    if request.method == 'POST':
        post_body   = json.loads(request.body.decode('utf-8'))
        #Ao receber o webhook pegar os arquivos da oportunidade e verificar as assinaturas do documento
        #Se tiver o ID desse documento no banco, atualizar a assinatura nova
        #dar um get com base no documento da oportunidade e ver se tem uma nova assinatura
        # arquivos  = post_body.get('files_data')
        deal_id     = post_body.get('oportunidade')
        documentos  = Documento.objects.filter(deal_id=deal_id, is_to_sign=1, full_signed=0)
        for documento in documentos:
            assinaturas = Assinatura.objects.filter(documento=documento.id, status=2)
            for assinatura in assinaturas:
                status_assinatura   = pipe.verificar_assinaturas(assinatura.id_signatario)
                dados_assinatura    = status_assinatura.get('data')
                if dados_assinatura.get('status') == 1:
                    assinatura.status           = dados_assinatura.get('status')
                    assinatura.cpf              = dados_assinatura.get('document_id')
                    assinatura.nascimento       = dados_assinatura.get('birth_day')
                    assinatura.signed_at        = dados_assinatura.get('sign_date')
                    assinatura.updated_at       = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    assinatura.ip_assinatura    = dados_assinatura.get('ip')
                    assinatura.nome             = dados_assinatura.get('name')
                    assinatura.save()
        return JsonResponse({'message':'WebHook recebido com sucesso!'}, status=200)
    return HttpResponse('Método não permitido!', status=415)

@csrf_exempt
def webhook_fullsign(request):#Esse webhook só é acionado quando todas as assinnaturas foram feitas no documento
    if request.method == 'POST':#Ao receber marcar o documento como "FULLSIGNED"
        post_body   = json.loads(request.body.decode('utf-8'))#Aqui eu verifico quantas assinatura já tem no documento, caso a LEN de retorno seja igual a LEN de pessoas a assinar, o documento está completamente assinado
        deal_id     = post_body.get('oportunidade')
        documentos  = Documento.objects.filter(deal_id=deal_id, is_to_sign=1, full_signed=0)
        for documento in documentos:
            assinaturas = Assinatura.objects.filter(documento=documento.id, status=1)
            if len(assinaturas) == documento.qtd_signs:
                documento.full_signed = True
                documento.save()
                return JsonResponse({'message':f'Assinatura do documento {documento.file_id} concluida!'}, status=200)
    return HttpResponse('Método não permitido', status=405)
