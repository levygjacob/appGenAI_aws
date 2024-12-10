import boto3
from openai import OpenAI
import os
import boto3.session

class bootstrapCredentials_:
    def __init__(self):
        self.secao = boto3.session.Session(
            aws_access_key_id="****",
            aws_secret_access_key="****"
        )
        
        self.session = boto3.session.Session()

    def credentials(self):
        rekognition_client = self.secao.client(
            'rekognition',
            region_name='us-east-1'            
        )

        s3_client = self.secao.client(
            's3',
            region_name='us-east-1'            
        )

        polly_client = self.secao.client(
            'polly',
            region_name='us-east-1'
        )

        cliente_openai = OpenAI(api_key="sk-proj-****")
        
        return rekognition_client, s3_client, polly_client, cliente_openai
