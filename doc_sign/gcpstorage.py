from google.cloud import storage
import os


PATH = os.environ.get('ROOTPATH')


class StorageGCP:
    
    def __init__(self):
        self.bucket_name = "resolve-contas-docs" #
        self.credentials = "" + 'mythical-runner-350501-79f85db1d3dd.json'
        self.client      = storage.Client.from_service_account_json(self.credentials)
        self.bucket      = self.client.bucket(self.bucket_name)
    
    
    def list(self, prefix):
        blobs_list = []
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix, delimiter='/')
        for blob in blobs:
            blobs_list.append(blob.name)
        return blobs_list
    
    
    def upload(self, source, destination):
        blob = self.bucket.blob(destination)
        blob.upload_from_filename(source)
        print(f"File {source} uploaded to gs://{self.bucket_name}/{destination}")
        return destination
    
        
    def download(self, source, destination):
        blob = self.bucket.blob(source)
        blob.download_to_filename(destination)
        print(f"File gs://{self.bucket_name}/{source} downloaded to {destination}")
    
    
    def check(self, source): #Verifica a existencia do 'SOURCE'
        blob = self.bucket.blob(source)
        result = blob.exists()
        return result
    
    def generate_url(self, source): #Gera a URL para abrir o source na web
        blob = self.bucket.blob(source)
        url = blob.generate_signed_url(2538065454) #Duração de 5 anos, talvez seja bom diminuir essa duração
        return url
    
        