from django.db import models

# Create your models here.


class Documento(models.Model):

    id              = models.AutoField(primary_key=True, blank=False, null=False, unique=True)
    cpf             = models.TextField(blank=True, null=True)
    file_name       = models.TextField(blank=True, null=True)
    file_id         = models.IntegerField(blank=True, null=True)
    file_hash       = models.TextField(blank=True, null=True)
    signature_id    = models.IntegerField(null=True, blank=True)
    deal_id         = models.TextField(blank=True, null=True)
    criado_em       = models.DateField(blank=True, null=True)
    qtd_signs       = models.IntegerField(blank=True, null=True)
    gcp_path        = models.TextField(blank=True, null=True)
    full_signed     = models.BooleanField(null=False, blank=False, default=False)
    aws_url         = models.TextField(null=True, blank=True)
    is_to_sign      = models.BooleanField(null=False, blank=False, default=False)

class Assinatura(models.Model):

    id              = models.AutoField(primary_key=True, blank=False, null=False, unique=True)
    nome            = models.TextField(blank=True, null=True)
    email           = models.TextField(blank=True, null=True)
    tipo            = models.IntegerField(blank=True, null=True)
    documento       = models.ForeignKey(Documento, null=False, blank=False, on_delete=models.CASCADE)
    signed_at       = models.DateTimeField(blank=True, null=True)
    id_signatario   = models.IntegerField(blank=True, null=True)
    id_sign         = models.IntegerField(blank=True, null=True)
    sign_hash       = models.TextField(blank=True, null=True)
    cpf             = models.TextField(blank=True, null=True)
    nascimento      = models.DateField(blank=True, null=True)
    status          = models.IntegerField(blank=True, null=True)
    ip_assinatura   = models.TextField(blank=True, null=True)
    send_at         = models.DateTimeField(blank=True, null=True)
    updated_at      = models.DateTimeField(blank=True, null=True)

    
