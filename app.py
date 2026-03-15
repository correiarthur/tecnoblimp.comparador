import streamlit as st
import pandas as pd
import json
import io
import main  # Importa nossa lógica de negócio refatorada
from components.Settings import render_settings_page

# Configuração da Página
st.set_page_config(
    page_title="Validador de Dados",
    page_icon="🔍",
    layout="wide"
)

# Design Sistemático e Compacto (Baseado no Screenshot)
st.markdown("""
    <style>
    /* 1. Redução Global de Espaçamentos (Gaps) */
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    .element-container {
        margin-bottom: 0px !important;
    }

    /* 2. Títulos e Textos Compactos */
    h1 {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        margin: 0.5rem !important;
        padding: 0 !important;
        white-space: nowrap !important; /* Garante que o título não quebre */
    }
    h2 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 4px !important;
    }
    h3 {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    .stMarkdown p, .stText {
        font-size: 0.85rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 3. Sidebar Customizada */
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] [data-testid="stSidebarHeader"] {
        margin-bottom: 0px !important;
        height: 30px !important;
    }
    section[data-testid="stSidebar"] {
        width: 260px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.3rem !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        font-size: 0.4rem !important;
        padding: 0px 0px !important;
        min-height: 16px !important;
        border-radius: 4px !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    section[data-testid="stSidebar"] h1 {
        font-size: 1.3rem !important;
        margin-bottom: 15px !important;
    }

    /* 4. Layout e Containers */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    section[data-testid="stFileUploadDropzone"] {
        padding: 0.5rem 1rem !important;
    }
    
    /* 5. Ajuste do Divider */
    hr {
        margin: 10px 0 !important;
    }

    /* 6. Esconder Barra Superior (Toolbar/Header) */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0px;
    }
    footer {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização do Estado
if 'page' not in st.session_state:
    st.session_state.page = 'Inicio'

if 'config' not in st.session_state:
    try:
        st.session_state.config = main.carregar_configuracao()
    except:
        st.session_state.config = {
            "validacoes": [
                {"nome_verificacao": "ComparaCPF", "colunas_chave": ["CPF"]}
            ],
            "validacao_final": {
                "nome_coluna": "Resultado", 
                "colunas_chave": ["CPF"]
            }
        }

# Funções de Navegação
def navegar_para(pagina):
    st.session_state.page = pagina

# Sidebar de Navegação
with st.sidebar:
    st.title("🚀 Navegação")
    
    # Botões de Navegação com on_click para evitar atraso de estado
    st.button(
        "🏠 Início", 
        use_container_width=True, 
        type="primary" if st.session_state.page == 'Inicio' else "secondary",
        key="btn_nav_inicio",
        on_click=lambda: navegar_para('Inicio')
    )
    
    st.button(
        "⚙️ Configuração", 
        use_container_width=True, 
        type="primary" if st.session_state.page == 'Configuracao' else "secondary",
        key="btn_nav_config",
        on_click=lambda: navegar_para('Configuracao')
    )
            
    st.divider()
    
# Renderização das Páginas
if st.session_state.page == 'Inicio':
    st.title("🔍 Validador de Dados")
    st.markdown("Esta ferramenta compara uma base de **Carga (Novos Dados)** contra uma base de **Sistema (Referência)**. Faça o upload dos arquivos abaixo para iniciar a validação.")
    
    st.divider()

    # Área de Upload em Colunas
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 📂 Arquivo Carga (Origem)")
        file_carga = st.file_uploader("Selecione o arquivo Excel de Carga", type=["xlsx"], key="carga", help="Apenas arquivos .xlsx")

    with col2:
        st.markdown("##### 📂 Arquivo Sistema (Destino)")
        file_sistema = st.file_uploader("Selecione o arquivo Excel de Sistema", type=["xlsx"], key="sistema", help="Apenas arquivos .xlsx")

    # Botão de Processamento
    if file_carga and file_sistema:
        if st.button("🚀 Iniciar Validação", type="primary", use_container_width=True):
            with st.spinner("Processando dados..."):
                try:
                    df_carga = pd.read_excel(file_carga).astype(str)
                    df_sistema = pd.read_excel(file_sistema).astype(str)
                    df_analise, inconsistencias = main.processar_comparacao(df_carga, df_sistema, st.session_state.config)
                    
                    total_registros = len(df_analise)
                    col_final = st.session_state.config['validacao_final']['nome_coluna']
                    total_erros = len(df_analise[df_analise[col_final] == 'Não Localizado'])
                    
                    st.divider()
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Registros", total_registros)
                    m2.metric("Inconsistências", total_erros)
                    m3.metric("Sucesso", f"{(total_registros-total_erros)/total_registros:.1%}")
                    
                    if inconsistencias:
                        st.error(f"Divergências encontradas em {len(inconsistencias)} regras.")
                    else:
                        st.success("✅ Dados conciliados com sucesso!")
                    
                    st.dataframe(df_analise, use_container_width=True)
                    
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df_analise.to_excel(writer, index=False)
                    
                    st.download_button("📥 Baixar Relatório", buffer.getvalue(), "analise.xlsx", use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Erro: {e}")
    else:
        st.info("Por favor, faça o upload de ambos os arquivos para prosseguir.")

elif st.session_state.page == 'Configuracao':
    render_settings_page()
