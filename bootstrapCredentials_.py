import boto3
from openai import OpenAI
import os
import boto3.session

class bootstrapCredentials_:
    def __init__(self):
        
        self.cliente_openai = OpenAI(api_key="*********************")
        self.secao = boto3.session.Session(
            aws_access_key_id="**********************",
            aws_secret_access_key="****************************"
        ) 
    # Singleton para capturar clientes 
    def get_client(self, service_name, region_name='us-east-1'):
         if service_name != 'openai': 
            return self.secao.client(service_name, region_name=region_name)
         else:
             return self.cliente_openai
