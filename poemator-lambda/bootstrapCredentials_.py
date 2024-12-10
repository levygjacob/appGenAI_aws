import boto3
from openai import OpenAI
import os
import boto3.session

class AWSClients:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AWSClients, cls).__new__(cls)
            cls._instance._initialize_clients()

            print(f'AQUIIIII: {cls._instance._initialize_clients()}')

        return cls._instance

    def _initialize_clients(self):
        # Inicializar as credenciais AWS
        self.cliente_openai = OpenAI(api_key="********")
        self.secao = boto3.session.Session(
            aws_access_key_id="*********",
            aws_secret_access_key="*********",
            region_name="us-east-1"
        )

    # Singleton para capturar clientes 
    def get_client(self, service_name, region_name='us-east-1'):
         if service_name != 'openai': 
            return self.secao.client(service_name, region_name=region_name)
         else:
             return self.cliente_openai