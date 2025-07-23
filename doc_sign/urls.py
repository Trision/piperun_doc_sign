from django.urls import path

from . import views

urlpatterns = [
    path('enviar_documento', views.recebe_doc, name='connect_upload_documento'),#Faz o upload na oportunidade do pipe
    path('liberar_assinatura', views.disponibilizar_assinatura, name="connect_libera_assinatura"),#Esse aqui fala que o documento é para ser assinar
    path('enviar_assinatura', views.assinar_documento, name="connect_assinar_documento"),#Aqui envia para o cliente/signatario assinar
    path('assinatura', views.webhook_assinatura, name='connect_webhook_assinatura'),
    path('assinatura_full', views.webhook_fullsign, name='connect_webhook_assinatura_full'),
    path('listar_documentos/<int:deal_id>', views.listar_docs, name='connect_listar_documentos'),
]