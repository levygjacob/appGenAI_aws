import gradio as gr
import requests
import os
import json
from urllib.parse import urlparse, unquote

# Configurações da API
UPLOAD_API_URL = "https://alxap143ba.execute-api.us-east-1.amazonaws.com/api/upload"
PROCESS_API_URL = "https://alxap143ba.execute-api.us-east-1.amazonaws.com/api/process-image"

def download_audio(audio_url, save_dir="downloads"):
    try:
        # Parse o URL para extrair o nome do arquivo
        parsed_url = urlparse(audio_url)
        file_name_with_params = os.path.basename(parsed_url.path)
        file_name = file_name_with_params.split("?")[0]  # Remove os parâmetros após o "?"

        # Decodificar caracteres especiais no nome do arquivo
        file_name = unquote(file_name)

        # Criar o diretório de destino, se não existir
        os.makedirs(save_dir, exist_ok=True)

        # Fazer o download do áudio
        response = requests.get(audio_url, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(save_dir, file_name)

            # Salvar o arquivo em chunks para evitar consumo excessivo de memória
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Arquivo salvo em: {file_path}")
            return file_path
        else:
            print(f"Erro ao baixar o arquivo: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao processar o download: {e}")
        return None

# Função para fazer upload da imagem para a API
def upload_image(file_path):
    try:
        file_name = os.path.basename(file_path)
        headers = {"Content-Type": "application/octet-stream"}
        with open(file_path, "rb") as f:
            response = requests.put(f"{UPLOAD_API_URL}/{file_name}", data=f, headers=headers)

        if response.status_code == 200:
            return file_name, None
        else:
            return None, f"Erro no upload: {response.text}"
    except Exception as e:
        return None, f"Erro ao enviar a imagem: {e}"

# Função para processar a imagem na API
def process_image(file_path):
    try:
        # Fazer upload da imagem
        file_name, error = upload_image(file_path)
        if error:
            return error, "", None

        # Enviar requisição para processar a imagem
        payload = {"file_name": file_name}
        headers = {"Content-Type": "application/json"}
        response = requests.post(PROCESS_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()

            # Obter os dados do resultado
            labels = result.get("labels", [])
            best_labels = result.get("melhores_palavras", [])
            poema = result.get("poema", "")
            audio_url = result.get("audio_url", None)
            
            try:
                audio_url_ = download_audio(audio_url)
            except Exception as e:
                print(f"Algum problema com o download: {e}")

            # Retornar os resultados formatados
            formatted_labels = ", ".join(labels)
            return formatted_labels, best_labels, poema, audio_url_
        else:
            return f"Erro no processamento: {response.text}", "", None
    except Exception as e:
        return f"Erro ao processar a imagem: {e}", "", None

# Interface do Gradio
with gr.Blocks(css="body {background-image: url('bg.jpg'); background-size: cover;}") as demo:
    gr.Markdown("# 🌟 Gerador de Poemas e Áudios 🎤", elem_id="titulo")
    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(type="filepath", label="Faça o upload da sua imagem")
        with gr.Column(scale=2):
            labels_output = gr.Textbox(label="Rótulos Detectados", interactive=False)
            best_labels_output = gr.Textbox(label="Melhores Rótulos", interactive=False)
            result_text = gr.Textbox(label="Poema Gerado", interactive=False)
            submit_button = gr.Button("Gerar Poema")
            audio_output = gr.Audio(label="Áudio Gerado", type="filepath")

    # Ações dos botões
    def handle_audio_playback(file_path):
        # Certifique-se de que o arquivo esteja na pasta `downloads`
        file_name = os.path.basename(file_path)
        local_audio_path = os.path.join("downloads", file_name)

        # Verifica se o arquivo existe antes de retornar o caminho
        if os.path.exists(local_audio_path):
            return local_audio_path
        else:
            return None

    submit_button.click(
        fn=process_image,
        inputs=[image_input],
        outputs=[labels_output, best_labels_output, result_text, audio_output]
    )


# Rodar a interface
demo.launch()
