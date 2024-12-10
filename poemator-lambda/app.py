# BIBLIOTECAS PYTHON ***********************************************************************************
from openai import OpenAI
from chalice import Chalice, Response
import boto3, uuid, botocore
import os
import json
import boto3.session
from PIL import Image  # Para validação mais robusta
from io import BytesIO
from imghdr import what
import cgi
import base64

###### INIT CHALISE ************************************************************************************
app = Chalice(app_name='poemator-lambda')
app.debug = True

app.api.binary_types.append("image/*")
app.api.binary_types = [
    'image/png',
    'image/jpeg',
    'image/gif',
    'application/octet-stream'
]

###### Credentials Clients ******************************************************************************
# Configurar credenciais no ambiente
os.environ["AWS_ACCESS_KEY_ID"] = "*******"
os.environ["AWS_SECRET_ACCESS_KEY"] = "*******"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

class AWSClients:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AWSClients, cls).__new__(cls)
            cls._instance._initialize_clients()

        return cls._instance

    def _initialize_clients(self):
        # Inicializar as credenciais AWS
        self.cliente_openai = OpenAI(api_key="*******")
        self.secao = boto3.session.Session(
            aws_access_key_id="****",
            aws_secret_access_key="****",
            region_name="us-east-1"
        )

    # Singleton para capturar clientes 
    def get_client(self, service_name, region_name='us-east-1'):
         if service_name != 'openai': 
            return self.secao.client(service_name, region_name=region_name)
         else:
             return self.cliente_openai

###### REGOKNITION ******************************************************************************
class RekogZator:
    def __init__(self, rekognition_client):
        self.rekognition_client = rekognition_client

    def rekogDetect(self, bucket_name, file_name, cliente_openai, s3_client):
        try:
            # Verifique se o arquivo existe no S3
            try:
                s3_client.head_object(Bucket=bucket_name, Key=file_name)
            except botocore.exceptions.ClientError as e:
                raise RuntimeError(f"O arquivo {file_name} não foi encontrado no S3 ou não é acessível: {e}")

            # Detecta rótulos com o AWS Rekognition
            response = self.rekognition_client.detect_labels(
                Image={"S3Object": {"Bucket": bucket_name, "Name": file_name}},
                MaxLabels=10,
                MinConfidence=80
            )

            # Extrair nomes dos rótulos
            labels = [label['Name'] for label in response.get("Labels", [])]

            # Traduzir rótulos usando OpenAI
            if labels:
                prompt = f"Traduza as seguintes palavras para português do Brasil: {', '.join(labels)}"
                try:
                    rotulos_traduzidos = cliente_openai.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "Você é um tradutor de palavras."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=300,
                        temperature=0.1
                    )

                    # Retorna as palavras traduzidas
                    translated_labels = rotulos_traduzidos.choices[0].message.content
                    return translated_labels.split(", ")
                except Exception as e:
                    raise RuntimeError(f"Erro ao traduzir palavras: {e}")
            else:
                return []

        except Exception as e:
            raise RuntimeError(f"Erro no Rekognition: {e}")

###### POEMEIRO *********************************************************************************
class Poemeiro:
    def __init__(self, cliente):
        """
        Inicializa a classe Poemeiro com a chave da API OpenAI.
        """
        self.cliente = cliente
       
    def selecionar_palavras(self, labels: list[str]) -> list[str]:
        """
        Seleciona os melhores rótulos para gerar o poema usando a OpenAI.

        Args:
            labels (list[str]): Lista de rótulos vindos do Rekognition.

        Returns:
            list[str]: Lista com três palavras selecionadas.
        """
        prompt = (
            f"""Eu tenho uma lista de palavras extraídas de uma imagem: {', '.join(labels)}.\n
            Escolha as 3 melhores palavras dessa lista que combinam bem para criar um poema curto e criativo no estilo Cordel.
            Responda apenas com as 3 palavras separadas por vírgulas."""
        )

        try:
            response = self.cliente.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """Você é um poeta que adora Cordel e sabe escolher palavras criativas para compor versos.
                                                     Responda em português do Brasil."""},

                    {"role": "user", "content": prompt}
                ],

                max_tokens=300,
                temperature=0.1
            )

            selected_words = response.choices[0].message.content
            return [word.strip() for word in selected_words.split(',')]
        
        except Exception as e:
            raise RuntimeError(f"Erro ao selecionar palavras: {e}")
        

    def generate_poema(self, words: list[str]) -> str:
        """
        Gera um poema usando as palavras fornecidas.

        Args:
            words (list[str]): Lista com três palavras para criar o poema.

        Returns:
            str: O poema gerado pela OpenAI.
        """

        if len(words) != 3:
            raise ValueError(f"É necessário exatamente 3 palavras para gerar o poema. {words}")
        
        prompt = (
            f"""Sua tarefa é criar um poema curto e criativo no estilo Cordel usando as palavras:
            {words[0]}, {words[1]} e {words[2]}.\n
            Certifique-se de que o poema tenha no máximo 3 estrofes com 5 linhas cada estrofe no máximo, 
            seja bem estruturado e inclua humor e irreverência típicos do Cordel.
            Traduza todas as palavras para o Português do Brasil."""
        )

        try:
            response = self.cliente.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um excelente escritor do estilo Cordel."},
                    {"role": "user", "content": prompt }
                ],
                max_tokens=500,
                temperature=0.7
            )
            poem = response.choices[0].message.content
            return poem.strip()
        
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar o poema: {e}")

###### THEREPENTER ******************************************************************************
class PollyZator:
    def __init__(self, polly_client):
        self.polly_client = polly_client

    def sintetizar_texto_para_audio(self, texto: str, output_format: str = "mp3", voice_id: str = "Camila") -> bytes:
        """
        Gera um arquivo de áudio a partir de um texto usando AWS Polly.

        Args:
            texto (str): Texto a ser convertido em áudio.
            output_format (str): Formato do arquivo de saída (padrão: 'mp3').
            voice_id (str): Voz a ser utilizada (padrão: 'Joanna').

        Returns:
            bytes: Dados binários do arquivo de áudio gerado.
        """
        try:
            response = self.polly_client.synthesize_speech(
                Text=texto,
                OutputFormat=output_format,
                VoiceId=voice_id
            )
            return response['AudioStream'].read()  # Retorna os dados do áudio como binário
        except Exception as e:
            raise RuntimeError(f"Erro ao sintetizar texto: {e}")

# Clients
credencial = AWSClients()
rekognition_client =  credencial.get_client('rekognition')
s3_client = credencial.get_client('s3')
polly_client = credencial.get_client('polly')
cliente_openai = credencial.get_client('openai')

# Configurações do bucket S3
BUCKET_NAME = "aula-unifor"

# Classes de funcionalidades
rekogZator = RekogZator(rekognition_client)
poemator = Poemeiro(cliente_openai)
polly_service = PollyZator(polly_client)

#####/// ROTEIRIZACAO DA API *********************************************************************************///

def generate_presigned_url(_client, bucket_name, object_name, expiration=3600):
    """
    Gera uma URL pré-assinada para o objeto no S3.
    """
    try:
        response = _client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=expiration
        )
    except Exception as e:
        raise RuntimeError(f"Erro ao gerar URL pré-assinada: {e}")
    return response

def _get_parts():
    """
    Processa multipart/form-data e extrai as partes usando o módulo cgi.
    """
    rfile = BytesIO(app.current_request.raw_body)
    content_type = app.current_request.headers.get('content-type', '')
    _, parameters = cgi.parse_header(content_type)

    if 'boundary' not in parameters:
        raise ValueError("Boundary não encontrado no cabeçalho Content-Type.")

    parameters['boundary'] = parameters['boundary'].encode('utf-8')
    return cgi.parse_multipart(rfile, parameters)


@app.route('/upload/{file_name}', methods=['PUT'], content_types=['application/octet-stream'])
def upload_image(file_name):
    """
    Endpoint para receber, validar e fazer upload da imagem para o S3.
    """
    try:
        # Obter o corpo binário da requisição
        body = app.current_request.raw_body

        # Criar arquivo temporário no diretório /tmp
        tmp_file_name = f"/tmp/{file_name}"
        with open(tmp_file_name, "wb") as tmp_file:
            tmp_file.write(body)

        # Fazer upload do arquivo para o S3
        s3_client.upload_file(tmp_file_name, BUCKET_NAME, file_name)

        # Retornar sucesso
        return {"message": f"The file {file_name} was uploaded successfully."}

    except Exception as e:
        # Log e retorno do erro
        app.log.debug(f"Erro ao fazer upload: {str(e)}")
        return Response(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )




@app.route('/process-image', methods=['POST'], content_types=['application/json'])
def process_image():
    """
    Endpoint para processar imagem no Rekognition, gerar poema e áudio.
    """
    try:
        # Obter o nome do arquivo enviado no JSON
        request = app.current_request.json_body
        file_name = request.get("file_name")

        if not file_name:
            return Response(
                body=json.dumps({"error": "Nome do arquivo não fornecido."}),
                status_code=400,
                headers={'Content-Type': 'application/json'}
            )

        # Validar se o arquivo existe no S3
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=file_name)
        except botocore.exceptions.ClientError as e:
            raise RuntimeError(f"O arquivo {file_name} não foi encontrado no S3 ou não é acessível: {e}")

        # Validar se o conteúdo é uma imagem válida usando RekogZator
        labels = rekogZator.rekogDetect(BUCKET_NAME, file_name, cliente_openai, s3_client)

        if not labels:
            return {"error": "Nenhum rótulo detectado."}

        # Selecionar as melhores palavras com o método selecionar_palavras
        melhores_palavras = poemator.selecionar_palavras(labels)

        # Gerar poema usando as palavras selecionadas
        poema = poemator.generate_poema(melhores_palavras)

        # Gerar áudio usando Polly e fazer upload para o S3
        audio_data = polly_service.sintetizar_texto_para_audio(poema)
        audio_file_name = f"audio-{uuid.uuid4().hex}.mp3"

        # Upload do áudio para o S3
        s3_client.put_object(Bucket=BUCKET_NAME, Key=audio_file_name, Body=audio_data)

        # Gerar URL público para o áudio
        audio_url = generate_presigned_url(s3_client, BUCKET_NAME, audio_file_name) #f"https://{BUCKET_NAME}.s3.amazonaws.com/{audio_file_name}"

        return {
            "labels": labels,
            "melhores_palavras": melhores_palavras,
            "poema": poema,
            "audio_url": audio_url
        }

    except Exception as e:
        return Response(
            body=json.dumps({"error": str(e)}),
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )
