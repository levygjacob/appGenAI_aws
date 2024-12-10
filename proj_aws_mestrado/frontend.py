import streamlit as st
from openai import OpenAI
from rekogzator import RekogZator
from poemeiro import Poemeiro
from therepenter import PollyZator
from bootstrapCredentials import bootstrapCredentials
import boto3, uuid, botocore
import os

os.chdir(os.path.abspath(os.curdir))

# Clients
cliente = bootstrapCredentials()
rekognition_client, s3_client, polly_client, cliente_openai = cliente.credentials()

# Bucket S3
bucket_name = "aula-unifor"

# REKOGNITION AWS FEATURE
rekogZator = RekogZator(rekognition_client)

# Polly - The Repenter
polly_service = PollyZator(polly_client)

st.sidebar.title("Upload de Imagem")
uploaded_file = st.sidebar.file_uploader("Envie uma imagem", type=["jpg", "jpeg", "png"])

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inicializar session_state para controle do fluxo
if "s3_data" not in st.session_state:
    st.session_state.s3_data = False

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

if "labels" not in st.session_state:
    st.session_state.labels = None

if "poema" not in st.session_state:
    st.session_state.poema = None
    
col1, col2 = st.columns(2)
container1 = st.container()
container2 = st.container()

with col1:
    with container1:
        if uploaded_file:
            try:
                # Exibir a imagem no frontend
                st.image(uploaded_file, caption="Imagem carregada", use_column_width=True)

                # Gerar nome único para o arquivo no S3
                file_name = f"poemator-{uploaded_file.name}"

                # Verificar se o arquivo já existe no S3
                with st.spinner("Verificando se o arquivo já existe no S3..."):
                    if not st.session_state.s3_data:
                        try:
                            s3_client.head_object(Bucket=bucket_name, Key=file_name)
                            st.warning(f"Imagem '{uploaded_file.name}' já existe no bucket S3. Pulando upload...")
                            st.session_state.s3_data = True
                        except botocore.exceptions.ClientError as e:
                            if e.response['Error']['Code'] == "404":
                                with st.spinner("Fazendo upload para o S3..."):
                                    uploaded_file.seek(0)
                                    s3_client.upload_fileobj(uploaded_file, bucket_name, file_name)
                                    st.success(f"Arquivo {uploaded_file.name} enviado para o S3 com sucesso!")
                                    st.write(f"Arquivo salvo como: {file_name} no bucket {bucket_name}")
                                    st.session_state.s3_data = True
                            else:
                                st.error(f"Erro ao verificar a existência do arquivo no S3: {e}")
                                raise

                # Processar imagem com o Rekognition
                with st.spinner("Processando imagem com o Rekognition..."):
                    if st.session_state.labels is None:
                        try:
                            labels = rekogZator.rekogDetect(bucket_name, file_name, cliente_openai, s3_client)
                            if labels:
                                st.session_state.labels = labels
                                st.text_area("Resultados do Rekognition (Traduzidos)", value=", ".join(labels), height=200)
                            else:
                                st.error("Nenhum rótulo foi detectado com confiança suficiente.")
        
                        except Exception as e:
                            st.error(f"Erro ao processar a imagem: {e}")

                    else:
                        st.text_area("Resultados do Rekognition (Traduzidos)", value=", ".join(st.session_state.labels), height=200)

                # Gerar poema com base nos rótulos
                if st.session_state.labels and len(st.session_state.labels) >= 3 and not st.session_state.poema:
                    with st.spinner("Gerando o nosso Cordel..."):
                        poemator = Poemeiro(cliente_openai)
                        melhores_palavras = poemator.selecionar_palavras(st.session_state.labels)
                        poema = poemator.generate_poema(melhores_palavras)

                        if poema:
                            st.session_state.poema = poema
                            st.text_area("Poema Gerado", value=poema, height=200)
                        else:
                            st.error("Nenhum poema foi gerado. Por favor, tente novamente.")
                elif st.session_state.labels and len(st.session_state.labels) < 3:
                    st.error("Não há rótulos suficientes para gerar um poema.")
                else:
                    st.text_area("Poema Gerado", value=st.session_state.poema, height=200)

            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")
with col2:
    with container2:
        # Geração e reprodução de áudio
        if st.session_state.poema:
            st.write("Gerar áudio:")

            # Configurar seleção de voz
            voice_id = st.selectbox("Selecione a voz para o áudio", ["Camila (PT-BR)", "Ricardo (PT-BR)"], key="voice_select")
            voice_mapping = {
                "Camila (PT-BR)": "Camila",
                "Ricardo (PT-BR)": "Ricardo"
            }
            selected_voice = voice_mapping[voice_id]

            # Formulário para encapsular o botão de gerar áudio
            with st.form(key="audio_form"):
                gerar_audio = st.form_submit_button("Gerar Áudio")
                if gerar_audio:
                    try:
                        with st.spinner("Polly em ação..."):
                            audio_data = polly_service.sintetizar_texto_para_audio(
                                st.session_state.poema,
                                output_format="mp3",
                                voice_id=selected_voice
                            )
                            st.session_state.audio_data = audio_data
                            st.success("Áudio gerado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao gerar áudio: {e}")

            # Exibir player de áudio, se o áudio estiver disponível
            if st.session_state.audio_data:
                st.audio(st.session_state.audio_data, format="audio/mp3")
