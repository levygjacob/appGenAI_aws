import streamlit as st
import os


class RekogZator:
    def __init__(self, rekognition_client, bucket_name):
        self.rekognition_client = rekognition_client
        self.bucket_name = bucket_name

    def rekogDetect(self, uploaded_file):
        try:
            if uploaded_file:
                rotulos = self.rekognition_client.detect_labels(
                    Image={"S3Object": {"Bucket": self.bucket_name, "Name": uploaded_file.name}},
                    MaxLabels=10
                )

                try:
                    rotulos_traduzidos = self.cliente.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": """Você é um tradutor.
                                                            Traduza para português do Brasil."""},

                            {"role": "user", "content": f"""Sua tarefa é traduzir estas palavras {rotulos}"""}
                        ],

                        max_tokens=50,
                        temperature=0.1
                    )

                    response = rotulos_traduzidos.choices[0].message.content
                    return response
                
                except Exception as e:
                    raise RuntimeError(f"Erro ao selecionar palavras: {e}")            
        
        except Exception as e:
            print(f'Erro no rekognition ao tentar detectar: {e}')
            return None

            
        
