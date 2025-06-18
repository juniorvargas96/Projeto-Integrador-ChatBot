# Importa a biblioteca 'requests' para fazer o download de páginas da web.
import requests
# Importa a biblioteca 'BeautifulSoup' para "entender" e extrair dados do código HTML.
from bs4 import BeautifulSoup

# Define a função que será nosso "robô" para ler o conteúdo do site.
def buscar_conteudo_da_url(url: str) -> str | None:
    # A anotação '-> str | None' indica que esta função retornará uma string (texto) ou None (nada).
    """
    Esta função recebe uma URL (como string), tenta acessá-la, extrai o texto principal
    e retorna o texto. Se algo der errado, ela retorna None.
    """
    # Imprime uma mensagem no terminal (não na tela do usuário) para sabermos que o processo começou.
    print(f"Buscando conteúdo da URL: {url}...")
    # O bloco 'try...except' serve para tentar executar um código que pode dar erro, como uma falha de conexão.
    try:
        # 'requests.get' faz a requisição para a URL e baixa o conteúdo da página. 'timeout' evita espera infinita.
        response = requests.get(url, timeout=10)
        # 'raise_for_status' verifica se a resposta foi bem-sucedida (ex: código 200). Se não, gera um erro.
        response.raise_for_status()
        # 'BeautifulSoup' analisa o conteúdo HTML baixado para que possamos navegá-lo facilmente.
        soup = BeautifulSoup(response.content, 'html.parser')
        # Procura por tags como <main> ou <article> para focar no conteúdo principal. Se não achar, usa o <body> inteiro.
        main_content = soup.find('main') or soup.find('article') or soup.body
        # '.get_text()' extrai todo o texto do conteúdo selecionado, limpando espaços extras e separando por linhas.
        texto_limpo = main_content.get_text(separator='\n', strip=True)
        # Imprime no terminal que a extração foi um sucesso.
        print("Conteúdo extraído com sucesso!")
        # Retorna o texto limpo para quem chamou a função.
        return texto_limpo
    # Se ocorrer um erro durante a requisição (ex: sem internet, site fora do ar), este bloco é executado.
    except requests.RequestException as e:
        # Imprime o erro no terminal para sabermos o que aconteceu.
        print(f"ERRO: Falha ao acessar o site. {e}")
        # Retorna 'None' para sinalizar que a operação falhou.
        return None