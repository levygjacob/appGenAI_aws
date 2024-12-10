import gradio as gr
from rekogzator import RekogZator
from poemeiro import Poemeiro
from therepenter import PollyZator
from bootstrapCredentials import bootstrapCredentials
import boto3
import os

# Clients
cliente = bootstrapCredentials()
rekognition_client, s3_client, polly_client, cliente_openai = cliente.credentials()

# Bucket S3
bucket_name = "aula-unifor"

# REKOGNITION AWS FEATURE
rekogZator = RekogZator(rekognition_client)

# Polly - The Repenter
polly_service = PollyZator(polly_client)

# Função para processar a imagem, gerar rótulos e poema
def process_image(file_path):
    try:
        if not os.path.exists(file_path):
            return "Erro: Arquivo não encontrado.", "", None
        
        file_name = f"poemator-{os.path.basename(file_path)}"
        try:
            s3_client.head_object(Bucket=bucket_name, Key=file_name)
        except boto3.exceptions.botocore.exceptions.ClientError:
            with open(file_path, "rb") as f:
                s3_client.upload_fileobj(f, bucket_name, file_name)

        labels = rekogZator.rekogDetect(bucket_name, file_name, cliente_openai, s3_client)
        if not labels:
            return "Nenhum rótulo detectado.", "", None

        poemator = Poemeiro(cliente_openai)
        melhores_palavras = poemator.selecionar_palavras(labels)
        poema = poemator.generate_poema(melhores_palavras)

        return ", ".join(labels), poema, None
    except Exception as e:
        return f"Erro ao processar: {e}", "", None

# Função para gerar áudio com Polly
def generate_audio(poema, voice_display_name):
    try:
        voice_mapping = {
            "Camila (PT-BR)": "Camila",
            "Ricardo (PT-BR)": "Ricardo"
        }
        voice_id = voice_mapping.get(voice_display_name)
        if voice_id:
            audio_data = polly_service.sintetizar_texto_para_audio(poema, output_format="mp3", voice_id=voice_id)
            return audio_data
        else:
            return f"Erro: Voz '{voice_display_name}' não encontrada."
    except Exception as e:
        return f"Erro ao gerar áudio: {e}"

# Interface do Gradio
with gr.Blocks(css=r"body {background-image: url('projetoFinal\bg.jpg'); background-size: cover;}") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(type="filepath", label="Faça o upload da sua imagem")
        with gr.Column(scale=2):
            labels_output = gr.Textbox(label="Rótulos Detectados", interactive=False)
            result_text = gr.Textbox(label="Poema Gerado", interactive=False)
            submit_button = gr.Button("Processar Imagem e Gerar Poema")
            voice_selector = gr.Dropdown(choices=["Camila (PT-BR)", "Ricardo (PT-BR)"], label="Selecione a Voz")
            audio_output = gr.Audio(label="Áudio Gerado")
            audio_button = gr.Button("Gerar Áudio")

    # Ações dos botões
    submit_button.click(
        fn=process_image,
        inputs=[image_input],
        outputs=[labels_output, result_text, audio_output]
    )
    audio_button.click(
        fn=generate_audio,
        inputs=[result_text, voice_selector],
        outputs=[audio_output]
    )

# Rodar a interface
demo.launch()

