import boto3

class PollyZator:
    def __init__(self, polly_client):
        self.polly_client = polly_client

    def sintetizar_texto_para_audio(self, texto: str, output_format: str = "mp3", voice_id: str = "Joanna") -> bytes:
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
