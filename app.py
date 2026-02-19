import streamlit as st
import pandas as pd
import json
import io
import main  # Importa nossa lógica de negócio refatorada

# Configuração da Página
st.set_page_config(
    page_title="Validador de Dados",
    page_icon="🔍",
    layout="wide"
)

# Título e Descrição
st.title("🔍 Validador e Reconciliação de Dados")
st.markdown("""
Esta ferramenta compara uma base de **Carga (Novos Dados)** contra uma base de **Sistema (Referência)**.
Faça o upload dos arquivos abaixo para iniciar a validação.
""")

# Sidebar para Configurações
st.sidebar.header("⚙️ Configurações")
uploaded_config = st.sidebar.file_uploader("Carregar Configuração (JSON)", type=["json"])

# Carregar Configuração
if uploaded_config:
    config = json.load(uploaded_config)
    st.sidebar.success("Configuração personalizada carregada!")
else:
    # Tenta carregar do arquivo padrão se existir, senão usa padrão hardcoded
    try:
        config = main.carregar_configuracao()
        if not config: raise Exception("Config vazia")
    except:
        st.sidebar.warning("Usando configuração padrão interna.")
        # Configuração de fallback mínima
        config = {
            "validacoes": [
                {"nome_verificacao": "ComparaCPF", "colunas_chave": ["CPF"]}
            ],
            "validacao_final": {
                "nome_coluna": "Resultado", 
                "colunas_chave": ["CPF"]
            }
        }

# Exibir regras ativas na sidebar
st.sidebar.markdown("### Regras Ativas")
for v in config.get("validacoes", []):
    st.sidebar.text(f"- {v['nome_verificacao']}")

# Área de Upload
col1, col2 = st.columns(2)

with col1:
    st.subheader("📂 Arquivo Carga (Origem)")
    file_carga = st.file_uploader("Selecione o arquivo Excel de Carga", type=["xlsx"], key="carga")

with col2:
    st.subheader("📂 Arquivo Sistema (Destino)")
    file_sistema = st.file_uploader("Selecione o arquivo Excel de Sistema", type=["xlsx"], key="sistema")

# Botão de Processamento
if file_carga and file_sistema:
    st.divider()
    if st.button("🚀 Iniciar Validação", type="primary"):
        with st.spinner("Processando dados..."):
            try:
                # Carregar DataFrames (força string para evitar incompatibilidade de tipos)
                df_carga = pd.read_excel(file_carga).astype(str)
                df_sistema = pd.read_excel(file_sistema).astype(str)
                
                # Executar Lógica
                df_analise, inconsistencias = main.processar_comparacao(df_carga, df_sistema, config)
                
                # Métricas
                total_registros = len(df_analise)
                total_erros = len(df_analise[df_analise[config['validacao_final']['nome_coluna']] == 'Não Localizado'])
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Registros", total_registros)
                m2.metric("Inconsistências Finais", total_erros, delta=-total_erros if total_erros > 0 else 0)
                m3.metric("Taxa de Sucesso", f"{(total_registros-total_erros)/total_registros:.1%}")
                
                if inconsistencias:
                    st.error(f"Foram encontradas {len(inconsistencias)} regras com divergências.")
                    with st.expander("Ver detalhes das inconsistências"):
                        for inc in inconsistencias:
                            st.write(f"❌ {inc}")
                else:
                    st.success("✅ Nenhuma inconsistência encontrada! Os dados estão conciliados.")
                
                # Visualização dos Dados
                st.subheader("📊 Prévia da Análise")
                
                # Filtro rápido para ver erros
                mostrar_apenas_erros = st.checkbox("Mostrar apenas linhas com divergências")
                if mostrar_apenas_erros:
                    col_final = config['validacao_final']['nome_coluna']
                    st.dataframe(df_analise[df_analise[col_final] == 'Não Localizado'])
                else:
                    st.dataframe(df_analise)
                
                # Preparar Download
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_carga.to_excel(writer, sheet_name='DadosCarga', index=False)
                    df_sistema.to_excel(writer, sheet_name='DadosSistema', index=False)
                    df_analise.to_excel(writer, sheet_name='Analise', index=False)
                
                st.download_button(
                    label="📥 Baixar Relatório Completo (.xlsx)",
                    data=buffer.getvalue(),
                    file_name="analise_completa.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            except Exception as e:
                st.error(f"Erro durante o processamento: {e}")
                st.exception(e)

else:
    st.info("Por favor, faça o upload de ambos os arquivos para prosseguir.")
