import botocore 

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
                MinConfidence=90
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
                        max_tokens=50,
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
