import streamlit as st
import docx
import PyPDF2
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
def pipeline_limpeza(texto_bruto, opcoes):
        if config.get('remover_artefactos'):
        texto = re.sub(r'[^\x00-\x7F]+', ' ', texto) # Remove caracteres não-ASCII
    if config.get('normalizar_espacos'):
        texto = re.sub(r'\s+', ' ', texto).strip() # Normaliza espaços e quebras
    return texto

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

main()