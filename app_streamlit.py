# Importa a biblioteca para criar a interface visual.
import streamlit as st
# Importa a biblioteca para fazer requisições web (para falar com nossa API).
import requests
# Importa as ferramentas para rodar tarefas em segundo plano.
import threading
import uvicorn

# A mágica da conexão: importa o objeto 'app_fastapi' do nosso arquivo 'api_server.py'.
from api_server import app_fastapi

# --- LÓGICA PARA INICIAR A API EM SEGUNDO PLANO ---

# Define a função que será executada na tarefa de segundo plano.
def iniciar_api():
    """Esta função simplesmente liga o servidor Uvicorn para nossa API FastAPI."""
    # 'uvicorn.run' é o comando em Python para iniciar o servidor, passando nosso app como alvo.
    uvicorn.run(app_fastapi, host="127.0.0.1", port=8000)

# 'st.session_state' é a memória do Streamlit. Verificamos se já iniciamos a API antes para não fazer de novo.
if "api_thread_started" not in st.session_state:
    # 'threading.Thread' cria o objeto da tarefa que rodará em segundo plano.
    # 'target=iniciar_api' diz qual função a tarefa deve executar.
    # 'daemon=True' garante que esta tarefa feche automaticamente quando o app Streamlit for fechado.
    thread = threading.Thread(target=iniciar_api, daemon=True)
    # 'thread.start()' efetivamente inicia a execução da tarefa em segundo plano.
    thread.start()
    # 'st.session_state.api_thread_started = True' guarda na memória que a API já foi iniciada.
    st.session_state.api_thread_started = True

# --- INTERFACE DO STREAMLIT (O VISUAL) ---

# 'st.set_page_config' define o título e o ícone que aparecem na aba do navegador.
st.set_page_config(page_title="Chatbot JP", page_icon="🤖")

# 'st.title' define o título principal da página.
st.title("🤖 Chatbot Jovem Programador")
# 'st.caption' define um subtítulo.
st.caption("Arquitetura Profissional: Streamlit + FastAPI")

# 'if "messages" not in ...' verifica se o histórico de mensagens visíveis já foi criado na memória.
if "messages" not in st.session_state:
    # Se não, cria o histórico com a primeira mensagem de boas-vindas do assistente.
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Estou pronto para ajudar com suas dúvidas sobre o Jovem Programador."}
    ]

# Define a função "mensageira" que conversa com nossa API em segundo plano.
def obter_resposta_da_api(pergunta: str):
    # A URL do nosso próprio servidor FastAPI.
    url_api = "http://127.0.0.1:8000/responder"
    # O corpo da mensagem (payload) que enviaremos, no formato JSON.
    payload = {"texto": pergunta}
    try:
        # 'requests.post' envia a pergunta do front-end (Streamlit) para o back-end (FastAPI).
        response = requests.post(url_api, json=payload, timeout=60)
        # Verifica se a API respondeu com sucesso (código 200).
        response.raise_for_status()
        # '.json().get(...)' pega a resposta do JSON e retorna o texto.
        return response.json().get("resposta", "Erro na resposta da API.")
    # Captura erros de conexão com a API.
    except requests.exceptions.RequestException as e:
        return f"Erro de conexão com a API: {e}"

# 'for message in ...:' percorre cada mensagem no histórico da memória.
for message in st.session_state.messages:
    # 'with st.chat_message(...)' cria um balão de chat para o autor da mensagem.
    with st.chat_message(message["role"]):
        # 'st.markdown' escreve o texto da mensagem dentro do balão.
        st.markdown(message["content"])

# 'if prompt := st.chat_input(...)' cria a caixa de texto e espera o usuário digitar.
if prompt := st.chat_input("Qual sua dúvida?"):
    # 'st.session_state.messages.append(...)' adiciona a nova mensagem do usuário ao histórico.
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 'with st.chat_message("user"):' cria um balão de chat para a mensagem do usuário.
    with st.chat_message("user"):
        # 'st.markdown(prompt)' escreve a pergunta do usuário na tela.
        st.markdown(prompt)
    
    # 'with st.chat_message("assistant"):' cria um balão para a resposta da IA.
    with st.chat_message("assistant"):
        # 'with st.spinner(...)' mostra uma animação de "carregando" enquanto esperamos a resposta.
        with st.spinner("Pensando..."):
            # 'resposta = obter_resposta_da_api(prompt)' chama nossa função para obter a resposta da IA.
            resposta = obter_resposta_da_api(prompt)
        # 'st.markdown(resposta)' escreve a resposta final da IA na tela.
        st.markdown(resposta)
    
    # Adiciona a resposta da IA ao histórico para que ela permaneça na tela.
    st.session_state.messages.append({"role": "assistant", "content": resposta})

    # pra rodar o chatbot - streamlit run app_streamlit.py