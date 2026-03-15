import streamlit as st
import json

def render_settings_page():
    # Estilos Estruturais Específicos da Página de Configurações
    st.markdown("""
        <style>
        /* Ajuste de botões no Streamlit para serem menores e sistemáticos (Sincronizado com Sidebar) */
        div.stButton > button {
            font-size: 0.4rem !important;
            padding: 0px 0px !important;
            min-height: 16px !important;
            border-radius: 4px !important;
        }
        /* Estilos do card de layout integrado */
        .layout-card {
            background: #ffffff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            text-align: left;
            margin: 10px 0;
        }
        .layout-card h2 {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 4px;
            color: #111827;
        }
        .layout-card p {
            font-size: 0.85rem;
            margin-bottom: 16px;
            line-height: 1.4;
            color: #4b5563;
        }
        .cta-button {
            background-color: #3b82f6;
            color: white !important;
            padding: 6px 16px;
            border-radius: 6px;
            border: none;
            font-weight: 500;
            font-size: 0.85rem;
            cursor: pointer;
            transition: background 0.2s;
            text-decoration: none;
            display: inline-block;
        }
        .cta-button:hover { background-color: #2563eb; }
        </style>
    """, unsafe_allow_html=True)

    st.title("Settings")
    st.divider()

    # Inicializa sub-página de configurações
    if 'settings_subpage' not in st.session_state:
        st.session_state.settings_subpage = 'json'

    # Layout em colunas para simular o menu lateral
    col_menu, col_content = st.columns([1, 5])

    with col_menu:
        st.markdown('<p style="font-size: 0.75rem; color: #6b7280; font-weight: 600; margin-bottom: 8px;">CATEGORIES</p>', unsafe_allow_html=True)
        
        # Botões do menu compactos
        st.button("📄 JSON", use_container_width=True, 
                  type="primary" if st.session_state.settings_subpage == 'json' else "secondary",
                  on_click=lambda: setattr(st.session_state, 'settings_subpage', 'json'))
            
        st.button("🎨 Layout", use_container_width=True, 
                  type="primary" if st.session_state.settings_subpage == 'layout' else "secondary",
                  on_click=lambda: setattr(st.session_state, 'settings_subpage', 'layout'))

    with col_content:
        if st.session_state.settings_subpage == 'json':
            st.subheader("Configuração JSON")
            st.markdown('<p style="font-size: 0.85rem; color: #4b5563;">Gerencie as regras de validação através de arquivos JSON.</p>', unsafe_allow_html=True)
            
            # Área de upload moderna
            with st.container(border=True):
                uploaded_config = st.file_uploader("Upload de arquivo de configuração", type=["json"], key="settings_json_uploader_v2")
                if uploaded_config:
                    try:
                        new_config = json.load(uploaded_config)
                        st.session_state.config = new_config
                        st.success("✅ Configuração aplicada globalmente!")
                    except Exception as e:
                        st.error(f"Erro ao ler JSON: {e}")
            
            st.markdown("### Visualização da Configuração Atual")
            st.json(st.session_state.config)

        elif st.session_state.settings_subpage == 'layout':
            st.markdown("""
                <div class="layout-card">
                    <h2>Configurar layout</h2>
                    <p>Clique para configurar o layout da carga de dados</p>
                    <button class="cta-button" onclick="console.log('Abrir tela de layouts')">
                        Layouts
                    </button>
                </div>
            """, unsafe_allow_html=True)
