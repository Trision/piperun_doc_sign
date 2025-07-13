import requests
import os
from .gcpstorage import StorageGCP

class PipeApi:

    def __init__(self):
        self.api_key = "0c79e1eb5a167724a3c4675cd40b9a22"
        self.url     = "https://api.pipe.run/"
        self.headers = {"token": self.api_key}
        self.storage = StorageGCP()

    def upload_documento(self, doc_path, deal_id, doc_name):
        api_url = self.url + "v1/files/upload"
        payload = {"deal_id": deal_id}
        try:
            with open(doc_path, "rb") as file:
                files = {"files[]": (doc_name, file, "application/pdf")}
                response = requests.post(api_url, headers=self.headers, files=files, data=payload).json()
                if response.get('success'):
                    file.close()#Fecha o arquivo após o upload dele
                    gpc = self.storage.upload(doc_path, f'/judicial/documentos/{doc_name}')#Faz o upload no gcp
                    os.remove(doc_path)#Remove do ambiente local
                    json_paths = {'gpc_path':gpc, 'api_response':response}   
                    print(response)      
                    return json_paths
                else:
                    return response
        except Exception as e:
            response = {"error": f'O exception é: {e}'}
            return response

    def enviar_documento(self, doc_name, doc_id, deal_id):#Aponta que o documento precisa ser assinado
        api = "v1/signatureDocuments"
        url_full = self.url + api
        payload = {"file_id":doc_id, "name":doc_name, "deal_id":deal_id}
        headers = {"accept": "application/json", "content-type": "application/json", "token": self.api_key}
        try:
            response = requests.post(url_full, json=payload, headers=headers).json()
            print(response)
            return response #Retorna outro ID, que é o ID para assinatura, esse ID é o importante para adicionar assinatura
        except requests.exceptions as e:
            response = {"error":e}
            return response
    
    def assinar_documento(self, sign_id, email, sign_type):
        api = "v1/signatures"
        url_full = self.url + api
        payload = {"signature_document_id":sign_id, "email":email, "witness":sign_type, "type":2}
        headers = {"accept": "application/json", "content-type": "application/json", "token": self.api_key}
        try:
            response = requests.post(url_full, json=payload, headers=headers).json()
            print(response)
            return response
        except requests.exceptions as e:
            response = {'error':e}
            return response
    
    def listar_documentos(self, deal_id):
        api = f"v1/files?deal_id={deal_id}"
        url_full = self.url + api + "?deal_id=" + deal_id
        try:
            response = requests.get(url_full, headers=self.headers).json()
            print(response)
            return response
        except requests.exceptions as e:
            return e
    
    def verificar_assinaturas(self, id_sign):
        api     = f"v1/signatures?show=3&signature_document_id={id_sign}" 
        url_full = self.url + api
        headers = {"accept": "application/json", "token": self.api_key}
        try:
            response = requests.get(url_full, headers=headers).json()
            print(response)
            return response
        except Exception as e:
            response = {'error':e}
            return response
    
if __name__ == "__main__":
    pi = PipeApi()# 38843361
    pi.upload_documento("./TESTANDO ASSINATURA PIPE.pdf", "49589772", "teste.pdf")
    # pi.enviar_documento('teste.pdf', '38989637', '49589772')
    # pi.assinar_documento("972170", "lfernando@acruxcapital.com", 1)
    # pi.verificar_assinaturas('972170')
    # pi.listar_documentos('37832041')