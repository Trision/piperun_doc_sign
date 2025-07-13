from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from num2words import num2words
from .models import Documento, Assinatura
from django.views.decorators.csrf import csrf_exempt
from .pipApi import PipeApi
import json
from datetime import datetime


pipe = PipeApi()
agora = datetime.now()

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
        post_body   = request.POST
        cpf         = post_body.get('cpf')
        deal_id     = post_body.get('id_oportunidade')
        arquivo     = request.FILES.get('minuta')
        conteudo    = arquivo.read()
        filename    = arquivo.name
        local_path  = cria_arquivo(conteudo, './media/', filename)
        upload_return   = pipe.upload_documento(local_path, deal_id, filename)
        pipe_info   = upload_return.get('api_response')
        pipe_data   = pipe_info.get('data')[0]
        deal_id     = pipe_data.get('deal_id')
        doc_id      = pipe_data.get('id')
        doc_name    = pipe_data.get('name')
        doc_hash    = pipe_data.get('hash')
        data_cria   = str(pipe_data.get('created_at')).split(' ')
        aws_url     = pipe_data.get('url_aws')
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
            return JsonResponse({'message':'Erro na importação para o PipeRun!'})
    return HttpResponse('Método não permitido!', status=415)

@csrf_exempt
def disponibilizar_assinatura(request):#Aponta para o pipe, que esse é um documento para assinar
    if request.method == "POST":
        post_body = json.loads(request.body.decode('utf-8'))
        documento = get_object_or_404(Documento, id=post_body.get('id_documento'))
        id_documento = documento.file_id
        deal_id = documento.deal_id
        filename = documento.file_name
        assinatura = pipe.enviar_documento(filename, id_documento, deal_id)
        if assinatura.get('success'):
            dados_assinatura = assinatura.get('data')
            documento.signature_id = dados_assinatura.get('id')
            documento.save()
            return JsonResponse({'mensagem':'Documento pronto para assinar'},status=200)
        else:
            return JsonResponse({'mensagem':'Erro ao disponibilzar para assinatura!'}, status=204)
    return HttpResponse('Método não permitido!', status=415)

@csrf_exempt
def assinar_documento(request):
    if request.method == 'POST':
        post_body = json.loads(request.body.decode('utf-8'))
        lista_signatarios = post_body.get('lista_signatarios')
        doc_id = post_body.get('doc_id')
        documento = get_object_or_404(Documento, id=doc_id)
        sign_id = documento.signature_id
        documento.qtd_signs = len(lista_signatarios)
        documento.save()
        for signatario in lista_signatarios:
            email = signatario.get('email')
            type_sign = signatario.get('type')
            assinatura = True
            if assinatura:
                Assinatura.objects.create(
                    email=email,
                    tipo=type_sign,
                    id_sign=sign_id,
                    documento=documento
                ).save()
            else:
                return JsonResponse({"mensagem":"Erro na hora de enviar para assinarem", "response_pipe":assinatura}, status=204)
        return JsonResponse({"mensagem":"Documento enviado para assinarem."}, status=200)
    return HttpResponse('Método não permitido!', status=415)

def listar_docs(request):
    #Com base no models do arquivo, puxar a lista deles, e utilizar o GCP.URL para criar uma url pública para os operadores visualizarem o documento
    #Esse arquivo vai ser exibido numa parte que dá pra configurar a assinatura e as pessoas que vão assinar o documento
    return

@csrf_exempt
def webhook_assinatura(request):
    if request.method == 'POST':
        post_body = json.loads(request.body.decode('utf-8'))
        print(post_body)#Ao receber o webhook pegar os arquivos da oportunidade e verificar as assinaturas do documento
        #Se tiver o ID desse documento no banco, atualizar a assinatura nova
        #dar um get com base no documento da oportunidade e ver se tem uma nova assinatura
        return JsonResponse({'message':'WebHook recebido com sucesso!'}, status=200)
    return HttpResponse('Método não permitido!', status=415)

@csrf_exempt
def webhook_fullsign(request):
    if request.method == 'POST':
        id_doc = ''
        return JsonResponse({'message':f'Assinatura do documento {id_doc} concluida!'})
    return HttpResponse('Método não permitido', status=405)

@csrf_exempt
def apaga(request):
    if request.method == 'DELETE':
        Assinatura.objects.all().delete()
        return JsonResponse({'msg':'Deletado mesmo'})