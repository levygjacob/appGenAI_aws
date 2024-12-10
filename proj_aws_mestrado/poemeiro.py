from openai import OpenAI
import openai

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
            raise ValueError("É necessário exatamente 3 palavras para gerar o poema.")
        
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