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
    # TODO: Implementar lógica para identificar extensão
    # TODO: Extrair texto preservando quebras originais
    # TODO: Capturar artefactos e erros de encoding
    return "Texto bruto extraído aqui"

# =========================================================
# TAREFA 2: Pipeline de Limpeza (Adriano Sousa)
# Objetivo: Criar pipeline configurável
# =========================================================
def pipeline_limpeza(texto_bruto, opcoes):
    # TODO: Implementar remoção de artefactos
    # TODO: Implementar normalização de espaços e pontuação
    # TODO: Implementar lógica para cabeçalhos/rodapés repetidos
    return "Texto limpo aqui"

# =========================================================
# TAREFA 3: Preparação do Input (Adriano Sousa)
# Objetivo: Segmentação e Prompting
# =========================================================
def preparar_input(texto_limpo):
    # TODO: Implementar deteção de idioma
    # TODO: Implementar chunking (segmentação)
    # TODO: Gerar prompt automático
    return "Idioma, Chunks e Prompt"

# =========================================================
# INTERFACE E INTEGRAÇÃO (Luís Esteves)
# Objetivo: Visualização Antes/Depois e Upload
# =========================================================
def main():
    st.title("Normalização de Texto - Etapa 1")
    
    # 1. Widget de Upload
    
    # 2. Sidebar com Opções da Pipeline
    
    # 3. Mostrar Texto Bruto (Antes)
    
    # 4. Mostrar Texto Limpo (Depois)
    
    # 5. Mostrar Preparação para SLM

if __name__ == "__main__":
    main()