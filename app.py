import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# --- LINKS REAIS E TESTADOS (DIRETOS) ---
LINK_NEXXUS = "https://i.imgur.com/mOId99i.png"
LINK_CONSENSO = "https://i.imgur.com/vHqY7eK.png"

# --- 1. FUNÇÃO DE CONEXÃO ---
def get_connection():
    try:
        return psycopg2.connect(st.secrets["postgres_url"])
    except:
        return None

# --- 2. CONFIGURAÇÃO DE LAYOUT (BRUTALMENTE SIMPLES) ---
st.set_page_config(page_title="NEXXUS CRM", layout="wide")

# CSS para forçar o visual Consenso
st.markdown(f"""
    <style>
        .stApp {{ background-color: #F0F2F6; }}
        [data-testid="stSidebar"] {{ background-color: white; border-right: 3px solid #1E4DB7; }}
        .stButton>button {{ background-color: #1E4DB7; color: white; border-radius: 8px; font-weight: bold; width: 100%; }}
        h1, h2, h3 {{ color: #1E4DB7; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. TELA DE LOGIN ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, col_login, c3 = st.columns([1, 1.8, 1])
    
    with col_login:
        # Forçando o link direto aqui
        st.image(LINK_NEXXUS, caption="Sistema de Gestão Técnica", use_container_width=True)
        
        with st.container(border=True):
            st.subheader("Acesso Nexus CRM")
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("ENTRAR NO SISTEMA"):
                if u == "admin" and p == "consenso123":
                    st.session_state.usuario = {"nome": "Admin", "perfil": "admin"}
                    st.rerun()
                else:
                    st.error("Usuário ou Senha incorretos.")
        
        # Logo da Consenso no rodapé do login
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image(LINK_CONSENSO, width=150)
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. INTERFACE PRINCIPAL (MENU LATERAL FIXO) ---
with st.sidebar:
    # Logo Nexxus no topo da barra lateral
    st.image(LINK_NEXXUS, use_container_width=True)
    st.divider()
    
    # MENU COM LINKS APARECENDO DIRETO (Como você pediu)
    st.write("📌 **NAVEGAÇÃO**")
    menu = st.radio(
        "Selecione a opção:",
        ["📊 Dashboard", "⚙️ Nova Demanda APUC", "🏢 Gestão de Clientes", "👥 Usuários", "🎨 Configurações"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br>"*5, unsafe_allow_html=True)
    st.divider()
    
    # Logo Consenso no final da barra lateral
    st.caption("Desenvolvido por:")
    st.image(LINK_CONSENSO, width=150)
    
    if st.button("Sair"):
        st.session_state.usuario = None
        st.rerun()

# --- 5. TELAS DO SISTEMA ---
if menu == "⚙️ Nova Demanda APUC":
    st.title("⚙️ Calculadora APUC (5 Etapas)")
    st.write("---")
    st.info("Pronto para configurar os pesos de Levantamento, Especificação, Dev, Testes e Doc.")
    # Aqui amanhã colocaremos os campos técnicos

elif menu == "📊 Dashboard":
    st.title("📊 Painel de Controle Consenso")
    st.write("Resumo de faturamento e horas faturáveis.")

else:
    st.title(menu)
    st.write("Funcionalidade em desenvolvimento.")
