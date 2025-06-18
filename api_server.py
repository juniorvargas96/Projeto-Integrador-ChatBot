# api_server.py

# Importa 'os' para ler variáveis de ambiente do sistema.
import os
# Importa a função 'load_dotenv' para carregar nosso arquivo .env.
from dotenv import load_dotenv
# Importa 'FastAPI' para criar o servidor da API.
from fastapi import FastAPI
# Importa 'BaseModel' para definir a estrutura dos dados de entrada.
from pydantic import BaseModel
# Importa 'genai' para se comunicar com a IA do Google.
import google.generativeai as genai

# A mágica da conexão: importa a função do nosso outro arquivo, 'web_scraper.py'.
from web_scraper import buscar_conteudo_da_url

# Chama a função para carregar as variáveis do arquivo .env.
load_dotenv()
# Inicia um bloco 'try...except' para lidar com possíveis erros na configuração.
try:
    # Pega o valor da variável 'GOOGLE_API_KEY' do ambiente.
    api_key = os.getenv("GOOGLE_API_KEY")
    # Verifica se a chave foi encontrada.
    if not api_key:
        # Se não, levanta um erro para parar a execução.
        raise ValueError("Chave GOOGLE_API_KEY não encontrada no .env")
    # Configura a biblioteca do Google com a chave.
    genai.configure(api_key=api_key)
# Captura qualquer exceção que possa ocorrer.
except Exception as e:
    # Imprime uma mensagem de erro no terminal.
    print(f"ERRO: Falha ao configurar a API do Google. {e}")

# Define a URL do site que será lido.
URL_PROGRAMA = "https://www.jovemprogramador.com.br/duvidas.php"
# Chama a função importada para buscar o conteúdo e armazená-lo na variável de contexto.
contexto_do_programa = buscar_conteudo_da_url(URL_PROGRAMA)

# Se o contexto não for carregado (erro de scraping), o programa não pode continuar.
if not contexto_do_programa:
    # Levanta um erro que interromperá a execução da API.
    raise RuntimeError("Contexto não pôde ser carregado. A API não pode iniciar.")

# Cria a instância principal da aplicação FastAPI.
app_fastapi = FastAPI()
# Seleciona o modelo específico da IA do Gemini a ser usado.
model = genai.GenerativeModel('gemini-1.5-flash')

# Define a estrutura que a API espera receber: um JSON com um campo "texto".
class MensagemUsuario(BaseModel):
    # 'texto: str' especifica que o campo "texto" deve ser do tipo string (texto).
    texto: str

# O decorador '@app_fastapi.post("/responder")' cria a URL do nosso chatbot.
@app_fastapi.post("/responder")
# Define a função que será executada quando a URL for chamada. 'async' a torna mais eficiente.
async def responder_pergunta(mensagem: MensagemUsuario):
    # Inicia um bloco 'try' para lidar com erros durante a conversa com a IA.
    try:
        # 'model.start_chat' inicia uma sessão de conversa com a IA.
        chat = model.start_chat(history=[
            {
                "role": "user",
                # Esta é a instrução "secreta" para a IA, agora muito mais rígida.
                "parts": [f"""Sua única e exclusiva função é ser um assistente sobre o Programa Jovem Programador.
É PROIBIDO usar qualquer conhecimento externo que você tenha. Todas as suas respostas devem ser baseadas ESTRITAMENTE no CONTEÚDO DE REFERÊNCIA abaixo.
Se o usuário perguntar sobre qualquer outro tópico que não esteja no texto (como esportes, futebol, política, história, etc.), você DEVE responder exatamente com a frase: 'Desculpe, minha função é responder apenas sobre o Programa Jovem Programador.'

--- CONTEÚDO DE REFERÊNCIA ---
{contexto_do_programa}
--- FIM DO CONTEÚDO DE REFERÊNCIA ---
"""]
            },
            # A segunda mensagem é uma resposta inicial para guiar a conversa.
            {"role": "model", "parts": ["Olá! Como posso te ajudar?"]}
        ])
        # 'chat.send_message' envia a pergunta do usuário (que veio no JSON) para a IA.
        response = chat.send_message(mensagem.texto)
        # 'return {"resposta": ...}' envia a resposta da IA de volta em formato JSON.
        return {"resposta": response.text}
    # Captura qualquer erro que aconteça durante a interação com a IA.
    except Exception as e:
        # Retorna uma mensagem de erro também em JSON.
        return {"erro": f"Ocorreu um problema: {e}"}