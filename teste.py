import os
import requests
from urllib.parse import urlparse, unquote

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

# URL do arquivo de áudio
audio_url = "https://aula-unifor.s3.amazonaws.com/audio-4cebab9337df48a2a3b5cd11492d9d9b.mp3?AWSAccessKeyId=AKIA3QWYVJWJT64TMEEZ&Signature=b3BPqVGpoVnkPJba0CE6t4LhUk8%3D&Expires=1733856586"

# Diretório local onde o arquivo será salvo
download_dir = "downloads"

# Fazer o download
download_audio(audio_url, save_dir=download_dir)
