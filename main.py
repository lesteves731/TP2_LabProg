import streamlit as st
import docx
import PyPDF2
import os
import re
from collections import Counter
from langdetect import detect
import requests

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
    # Remove caracteres de controlo (exceto newlines e tabs)
    texto = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", texto)
    # Remove sequências de encoding mal formadas (ex: Ã©, Ã£)
    texto = re.sub(r"[^\x00-\x7FÀ-ÿ\n\r\t]", " ", texto)
    # Remove múltiplos espaços deixados pelos removidos
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto

# c) Correção de quebras de linha incorretas
def corrigir_quebras_linha(texto):
    # Junta linha partida a meio de palavra (ex: "docu-\nmento" → "documento")
    texto = re.sub(r"-\n(\w)", r"\1", texto)
    # Junta quebra simples que não seja fim de parágrafo
    texto = re.sub(r"(?<![.\!?])\n(?!\n)", " ", texto)
    # Preserva parágrafos (dupla quebra)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
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
    # Espaços múltiplos → um só
    texto = re.sub(r"[ \t]+", " ", texto)
    # Espaço antes de pontuação
    texto = re.sub(r"\s+([.,;:!?])", r"\1", texto)
    # Espaço depois de pontuação (se não existir)
    texto = re.sub(r"([.,;:!?])(?=[^\s\d])", r"\1 ", texto)
    # Aspas inconsistentes → aspas normais
    texto = re.sub(r"[""«»]", """, texto)
    texto = re.sub(r"[""`´]", """, texto)
    # Reticências → símbolo correto
    texto = re.sub(r"\.{3,}", "…", texto)
    # Traços duplos → travessão
    texto = re.sub(r"\s*--\s*", " — ", texto)
    # Capitalizar início de frase
    texto = re.sub(r"(?<=[.!?]\s)([a-záàãâéêíóôõúç])", lambda m: m.group(1).upper(), texto)
    # Capitalizar primeira letra do texto
    if texto:
        texto = texto[0].upper() + texto[1:]
    return texto.strip()

# PIPELINE FINAL (COM OPÇÕES STREAMLIT)
def pipeline_limpeza(texto_bruto, opcoes):

    texto = texto_bruto

    # a) artefactos
    if opcoes.get("remover_artefactos"):
        texto = remover_artefactos(texto)

    # c) quebras de linha
    if opcoes.get("corrigir_quebras_linha"):
        texto = corrigir_quebras_linha(texto)

    # b) parágrafos
    if opcoes.get("reconstruir_paragrafos"):
        texto = reconstruir_paragrafos(texto)

    # e) headers/footers
    if opcoes.get("remover_headers_footers"):
        texto = remover_headers_footers(texto)

    # d) normalização
    if opcoes.get("normalizar_espacos"):
        texto = normalizar(texto)

    return texto

# =========================================================
# TAREFA 4: API SLM
# =========================================================
URL = "https://reality.utad.net/slm"
MODELO = "llama-3.2-1b-instruct"

def criar_prompt(chunk, idioma):

    prompt = f"Corrige erros ortográficos, melhora a pontuação e normaliza o seguinte texto em {idioma}. Mantem o significado original.Não alteres palavras corretas nem o significado.Devolve APENAS o texto corrigido, sem explicações.\nTexto:\n{chunk}"
    
    return prompt


def enviar_para_slm(prompt):
    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "model": MODELO,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(
        URL,
        headers=headers,
        json=body
    )

    return response

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
    prompt = f"Corrige erros ortográficos, melhora a pontuação e normaliza o seguinte texto. Mantem o significado original.Não alteres palavras corretas nem o significado.Devolve apenas o texto corrigido, sem explicações."
    return idioma, chunks, prompt

# =========================================================
# TAREFA 5: Criação de Relatórios Automáticos
# =========================================================
def gerar_relatorio_html(bruto, limpo, resultado_final, idioma, num_chunks, opcoes):
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Relatório de Normalização</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #2980b9; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
            pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; white-space: pre-wrap; }}
            table {{ border-collapse: collapse; width: 100%; }}
            td, th {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background: #2980b9; color: white; }}
        </style>
    </head>
    <body>
        <h1>Relatório de Normalização de Texto</h1>

        <h2>1. Parâmetros da Pipeline</h2>
        <table>
            <tr><th>Parâmetro</th><th>Valor</th></tr>
            <tr><td>Idioma detetado</td><td>{idioma}</td></tr>
            <tr><td>Número de chunks</td><td>{num_chunks}</td></tr>
            <tr><td>a) Remover artefactos</td><td>{"Sim" if opcoes.get("remover_artefactos") else "Não"}</td></tr>
            <tr><td>b) Reconstruir parágrafos</td><td>{"Sim" if opcoes.get("reconstruir_paragrafos") else "Não"}</td></tr>
            <tr><td>c) Corrigir quebras de linha</td><td>{"Sim" if opcoes.get("corrigir_quebras_linha") else "Não"}</td></tr>
            <tr><td>d) Normalizar espaços e pontuação</td><td>{"Sim" if opcoes.get("normalizar_espacos") else "Não"}</td></tr>
            <tr><td>e) Remover cabeçalhos e rodapés</td><td>{"Sim" if opcoes.get("remover_headers_footers") else "Não"}</td></tr>
            <tr><td>Modelo utilizado</td><td>{MODELO}</td></tr>
            <tr><td>API</td><td>{URL}</td></tr>
        </table>

        <h2>2. Texto Original (Bruto)</h2>
        <pre>{bruto}</pre>

        <h2>3. Texto após Limpeza</h2>
        <pre>{limpo}</pre>

        <h2>4. Texto Normalizado (Saída do Modelo)</h2>
        <pre>{resultado_final}</pre>

        <h2>5. Avaliação da Normalização</h2>
        <table>
            <tr><th>Métrica</th><th>Valor</th></tr>
            <tr><td>Caracteres originais</td><td>{len(bruto)}</td></tr>
            <tr><td>Caracteres após limpeza</td><td>{len(limpo)}</td></tr>
            <tr><td>Caracteres normalizados</td><td>{len(resultado_final.strip())}</td></tr>
            <tr><td>Redução na limpeza</td><td>{round((1 - len(limpo)/max(len(bruto),1)) * 100, 1)}%</td></tr>
            <tr><td>Redução total (bruto → normalizado)</td><td>{round((1 - len(resultado_final.strip())/max(len(bruto),1)) * 100, 1)}%</td></tr>
        </table>
    </body>
    </html>
    """



# =========================================================
# INTERFACE E INTEGRAÇÃO (Luís Esteves)
# Objetivo: Visualização Antes/Depois e Upload
# =========================================================
def main():
    st.set_page_config(layout="wide")
    st.header("Pipeline de Pré-Processamento")

    # Upload [cite: 11]
    f = st.file_uploader("Carregar PDF, DOCX ou TXT", type=["pdf", "docx", "txt"])

    if f:
        bruto = extrair_texto(f)
        
        # Interface de configuração [cite: 26]
        st.sidebar.subheader("Configurações da Pipeline")
        art = st.sidebar.checkbox("Remover Artefactos", value=True)
        esp = st.sidebar.checkbox("Normalizar Espaços", value=True)
        para = st.sidebar.checkbox("Reconstruir Parágrafos", value=True)
        queb = st.sidebar.checkbox("Corrigir Quebras de Linha", value=True)
        cabe = st.sidebar.checkbox("Remover Cabeçalhos e Rodapés repetidos", value=True)
        
        
        # Colunas para visualização Antes/Depois [cite: 33]
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Texto Bruto")
            st.text_area("Original", bruto, height=300)
            
        limpo = pipeline_limpeza(bruto, {"remover_artefactos": art, "normalizar_espacos": esp, "reconstruir_paragrafos" : para, "corrigir_quebras_linha" : queb, "remover_headers_footers" : cabe})
        
        with col2:
            st.subheader("Texto Limpo")
            st.text_area("Resultado", limpo, height=300)
            
        # Preparação SLM [cite: 36]
        st.divider()
        idioma, chunks, prompt = preparar_input(limpo)
        st.write(f"*Idioma:* {idioma} | *Chunks:* {len(chunks)}")
        st.info(f"*Prompt:* {prompt}")
        
        if st.button("Enviar para o SLM"):

            with st.spinner("A processar..."):
                resultado_final = ""
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
                
                
            #Relatório
            st.divider()
            st.subheader("Relatório")

            opcoes = {
                "remover_artefactos":     art,
                "reconstruir_paragrafos": para,
                "corrigir_quebras_linha": queb,
                "normalizar_espacos":     esp,
                "remover_headers_footers": cabe
            }
                
            html = gerar_relatorio_html(bruto, limpo, resultado_final, idioma, len(chunks), opcoes)

            st.download_button(
                label="📄 Exportar Relatório HTML",
                data=html,
                file_name="relatorio_normalizacao.html",
                mime="text/html"
            )
    
main()
