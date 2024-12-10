# 📷🎙️ Aplicação de Processamento de Imagens, Geração de Texto e Transcrição de Áudio com Streamlit, AWS Rekognition e Polly

Esta aplicação demonstra a integração de tecnologias de **Machine Learning** e **Inteligência Artificial** para realizar tarefas avançadas como **reconhecimento de imagens**, **geração de texto criativo** e **conversão de texto para áudio**. A interface interativa foi desenvolvida com **Streamlit**, e os serviços da AWS, como **Rekognition** e **Polly**, são utilizados para processar imagens e gerar áudio.

---

## 🛠️ Funcionalidades

### 1. **Reconhecimento de Imagens com AWS Rekognition**
- Faz o upload de imagens para um bucket no **AWS S3**.
- Utiliza o **AWS Rekognition** para identificar rótulos (labels) e características presentes na imagem.
- Exibe os rótulos detectados diretamente na interface, com confidência mínima ajustável.

### 2. **Geração de Texto Criativo**
- Gera textos no estilo **Cordel** com base nos rótulos identificados pela AWS Rekognition.
- Integra a API do **OpenAI ChatCompletion** para criar poemas criativos e únicos utilizando as palavras detectadas nas imagens.
- Oferece uma experiência de personalização e criatividade alinhada ao contexto da imagem.

### 3. **Transcrição de Texto para Áudio (Text-to-Speech)**
- Converte o poema gerado em áudio utilizando o **AWS Polly**.
- Suporte a vozes em português do Brasil, como **Camila** e **Ricardo**.
- Reproduz o áudio diretamente na interface com o componente de player de áudio do Streamlit.
- O áudio gerado é armazenado no estado do Streamlit para evitar repetição desnecessária.

---

## 💡 Fluxo da Aplicação

1. **Upload da Imagem**:
   - O usuário faz o upload de uma imagem pela interface do Streamlit.
   - A imagem é enviada para o bucket no AWS S3.
   - A aplicação verifica se a imagem já existe no bucket para evitar uploads duplicados.

2. **Processamento com AWS Rekognition**:
   - O Rekognition analisa a imagem e retorna uma lista de rótulos detectados.
   - Os rótulos são exibidos na interface, e os melhores são selecionados para a próxima etapa.

3. **Geração de Poema**:
   - A aplicação utiliza os rótulos detectados para criar um poema no estilo Cordel.
   - O texto é gerado usando a API de ChatCompletion do OpenAI.

4. **Geração e Reprodução de Áudio**:
   - O poema gerado é convertido em áudio utilizando o AWS Polly.
   - O áudio pode ser reproduzido diretamente na interface.

---

## 📦 Tecnologias Utilizadas

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Serviços AWS**:
  - **Rekognition**: Para análise de imagens.
  - **S3**: Para armazenamento de imagens e áudios.
  - **Polly**: Para conversão de texto para áudio.
- **Inteligência Artificial**:
  - **OpenAI ChatCompletion**: Para geração de textos criativos.

---

## ⚙️ Pré-requisitos

1. Conta na AWS com permissões para usar os serviços:
   - S3
   - Rekognition
   - Polly
2. Chave da API do OpenAI.
3. Ambiente Python configurado com as dependências:
   - `boto3`
   - `openai`
   - `streamlit`

---

## 🚀 Como Executar

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio

2. Configure as credenciais da AWS:
    Certifique-se de que suas credenciais da AWS estão configuradas no ambiente ou via boto3.
    
3. Instale as dependências:
    ```bash
    pip install -r requirements.txt

4. Execute a aplicação
    ```bash
    streamlit run app.py

5. Acesse a interface no navegador:
    ```bash
    http://localhost:8501
    
    
<br/>

## Equipe de desenvolvimento:

<ul>
    <li>Camila</li>
    <li>Levy Jacob</li>
    <li>Glauber</li>
    <li>Thiago Bluhm</li>

</ul>

