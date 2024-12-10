from chalice import Chalice
from bootstrapCredentials import bootstrapCredentials
from rekogzator import RekogZator
from poemeiro import Poemeiro
from therepenter import PollyZator
import boto3

# Inicializa Chalice
app = Chalice(app_name='poemator')

# Inicializa os clients
cliente = bootstrapCredentials()
rekognition_client, s3_client, polly_client, cliente_openai = cliente.credentials()

# Configurações do bucket S3
BUCKET_NAME = "aula-unifor"

# Classes de funcionalidades
rekogZator = RekogZator(rekognition_client)
poemator = Poemeiro(cliente_openai)
polly_service = PollyZator(polly_client)


@app.route('/process-image', methods=['POST'])
def process_image():
    """
    Endpoint para processar imagem com Rekognition e gerar poema.
    """
    request = app.current_request.json_body
    file_name = request.get('file_name')

    if not file_name:
        return {"error": "Nome do arquivo não fornecido."}

    try:
        # Detecta rótulos com Rekognition
        labels = rekogZator.rekogDetect(BUCKET_NAME, file_name, cliente_openai, s3_client)

        if not labels:
            return {"error": "Nenhum rótulo detectado."}

        # Gera poema com base nos rótulos
        melhores_palavras = poemator.selecionar_palavras(labels)
        poema = poemator.generate_poema(melhores_palavras)

        return {"labels": labels, "poema": poema}
    except Exception as e:
        return {"error": str(e)}


@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    """
    Endpoint para gerar áudio com Polly.
    """
    request = app.current_request.json_body
    texto = request.get('texto')
    voice_id = request.get('voice_id', 'Camila')

    if not texto:
        return {"error": "Texto não fornecido."}

    try:
        # Gera áudio com Polly
        audio_data = polly_service.sintetizar_texto_para_audio(
            texto, output_format="mp3", voice_id=voice_id
        )
        audio_key = f"audio/{uuid.uuid4()}.mp3"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=audio_key,
            Body=audio_data
        )
        audio_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{audio_key}"
        return {"audio_url": audio_url}
    except Exception as e:
        return {"error": str(e)}
