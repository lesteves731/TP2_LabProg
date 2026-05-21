import streamlit as st
import docx
import PyPDF2
import os
import re
from collections import Counter
from langdetect import detect

# =========================================================
# TAREFA 1: Extração Multi-formato (Luís Esteves)
# Objetivo: Suportar PDF, DOCX e TXT
# =========================================================
def extrair_texto(ficheiro):
    nome = ficheiro.name.lower()
    if nome.endswith(".txt"):
        return ficheiro.read().decode("utf-8")
    elif nome.endswith(".docx"):
        doc = docx.Document(ficheiro)
        return "\n".join([p.text for p in doc.paragraphs])
    elif nome.endswith(".pdf"):
        leitor = PyPDF2.PdfReader(ficheiro)
        return "\n".join([pagina.extract_text() for pagina in leitor.pages])
    return ""

# =========================================================
# TAREFA 2: Pipeline de Limpeza (Adriano Sousa)
# Objetivo: Criar pipeline configurável
# =========================================================
# a) Remoção de artefactos
def remover_artefactos(texto):
    # remove emojis e símbolos estranhos mantendo português
    texto = re.sub(r'[^\w\sÀ-ÿ.,;:!?()\-\']', ' ', texto)
    return texto

# c) Correção de quebras de linha incorretas
def corrigir_quebras_linha(texto):
    # transforma quebras isoladas em espaços
    texto = re.sub(r'(?<!\n)\n(?!\n)', ' ', texto)
    return texto

# b) Reconstrução de parágrafos
def reconstruir_paragrafos(texto):
    linhas = texto.splitlines()
    paragrafos = []
    buffer = ""

    for linha in linhas:
        linha = linha.strip()

        if not linha:
            if buffer:
                paragrafos.append(buffer.strip())
                buffer = ""
        else:
            if buffer:
                buffer += " " + linha
            else:
                buffer = linha

    if buffer:
        paragrafos.append(buffer.strip())

    return "\n\n".join(paragrafos)

# e) Remoção de headers e footers repetidos
def remover_headers_footers(texto):
    linhas = texto.splitlines()
    contagem = Counter(linhas)

    filtrado = [
        linha for linha in linhas
        if contagem[linha] < 3  # aparece muitas vezes = header/footer
    ]

    return "\n".join(filtrado)

# d) Normalização final
def normalizar(texto):
    texto = re.sub(r'\s+', ' ', texto).strip()
    texto = re.sub(r'\s+([.,;:!?])', r'\1', texto)
    return texto

# PIPELINE FINAL (COM OPÇÕES STREAMLIT)
def pipeline_limpeza(texto_bruto, opcoes):

    texto = texto_bruto

    # a) artefactos
    if opcoes.get("remover_artefactos"):
        texto = remover_artefactos(texto)

    # c) quebras de linha
    texto = corrigir_quebras_linha(texto)

    # b) parágrafos
    texto = reconstruir_paragrafos(texto)

    # e) headers/footers
    texto = remover_headers_footers(texto)

    # d) normalização
    if opcoes.get("normalizar_espacos"):
        texto = normalizar(texto)

    return texto
# TAREFA 4: API SLM 8B
# =========================================================
API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO = "llama-3.1-8b-instant"

def criar_prompt(chunk, idioma):

    prompt = f"""
    Corrige erros ortográficos, melhora a pontuação
    e normaliza o seguinte texto em {idioma}.

    Mantém o significado original.

    Texto:
    {chunk}
    """

    return prompt


def enviar_para_slm(prompt):

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": MODELO,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }

    response = requests.post(
        URL,
        headers=headers,
        json=body
    )

    return response

# =========================================================
# INTERFACE E INTEGRAÇÃO (Luís Esteves)
# Objetivo: Visualização Antes/Depois e Upload
# =========================================================

# =========================================================
# TAREFA 3: Preparação do Input (Adriano Sousa)
# Objetivo: Segmentação e Prompting
# =========================================================
def preparar_input(texto):
    try:
        idioma = detect(texto)
    except:
        idioma = "pt"
    chunks = [texto[i:i+1000] for i in range(0, len(texto), 1000)]
    prompt = f"Instrução: Normalize este texto em {idioma} mantendo o tom profissional."
    return idioma, chunks, prompt

# =========================================================
# INTERFACE E INTEGRAÇÃO (Luís Esteves)
# Objetivo: Visualização Antes/Depois e Upload
# =========================================================
def main():
    st.set_page_config(layout="wide")
    st.header("Pipeline de Pré-Processamento")

    # Upload [cite: 11]
    f = st.file_uploader("Carregar PDF, DOCX ou TXT", type=['pdf', 'docx', 'txt'])

    if f:
        bruto = extrair_texto(f)
        
        # Interface de configuração [cite: 26]
        st.sidebar.subheader("Configurações da Pipeline")
        art = st.sidebar.checkbox("Remover Artefactos", value=True)
        esp = st.sidebar.checkbox("Normalizar Espaços", value=True)
        
        # Colunas para visualização Antes/Depois [cite: 33]
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Texto Bruto")
            st.text_area("Original", bruto, height=300)
            
        limpo = pipeline_limpeza(bruto, {'remover_artefactos': art, 'normalizar_espacos': esp})
        
        with col2:
            st.subheader("Texto Limpo")
            st.text_area("Resultado", limpo, height=300)
            
        # Preparação SLM [cite: 36]
        st.divider()
        idioma, chunks, prompt = preparar_input(limpo)
        st.write(f"*Idioma:* {idioma} | *Chunks:* {len(chunks)}")
        st.info(f"*Prompt Gerado:* {prompt}")
        
     if st.button("Enviar para o Modelo 8B"):

        with st.spinner("A processar..."):
            for chunk in chunks:
                prompt_api = criar_prompt(chunk, idioma)
                response = enviar_para_slm(prompt_api)

            if response.status_code == 200:
                data = response.json()
                resultado_final += data["choices"][0]["message"]["content"] + "\n\n"
                else:
                st.error(response.text)

        st.subheader("Texto Normalizado")
        st.success("Concluído!")
        st.write(resultado_final)

main()