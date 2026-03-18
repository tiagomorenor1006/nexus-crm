import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# --- 1. FUNÇÃO PARA CONSERTAR O BANCO AUTOMATICAMENTE ---
def consertar_banco_automaticamente():
    # Links diretos que funcionam (.png)
    link_nexxus = "https://i.imgur.com/mOId99i.png"
    link_consenso = "https://i.imgur.com/vHqY7eK.png"
    
    try:
        conn = psycopg2.connect(st.secrets["postgres_url"])
        cur = conn.cursor()
        
        # Este comando verifica se o registro existe e atualiza os links se necessário
        cur.execute("""
            INSERT INTO configuracoes_layout (id, logo_sistema_url, logo_empresa_url, nome_empresa, cor_primaria, cor_fundo)
            VALUES (1, %s, %s, 'Consenso', '#1E4DB7', '#F0F2F6')
            ON CONFLICT (id) DO UPDATE 
            SET logo_sistema_url = %s, logo_empresa_url = %s;
        """, (link_nexxus, link_consenso, link_nexxus, link_consenso))
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        # Se der erro, apenas ignora e segue o jogo
        pass

# --- 2. CARREGAR LAYOUT ---
def carregar_layout():
    # Tenta consertar antes de carregar
    consertar_banco_automaticamente()
    
    try:
        conn = psycopg2.connect(st.secrets["postgres_url"])
        df = pd.read_sql("SELECT * FROM configuracoes_layout WHERE id = 1", conn)
        conn.close()
        return df.iloc[0].to_dict()
    except:
        return {
            "cor_primaria": "#1E4DB7", "cor_fundo": "#F0F2F6", 
            "logo_sistema_url": "https://i.imgur.com/mOId99i.png", 
            "logo_empresa_url": "https://i.imgur.com/vHqY7eK.png", 
            "nome_empresa": "Consenso"
        }

# --- 3. APLICAÇÃO DO LAYOUT ---
layout = carregar_layout()
st.markdown(f"""
    <style>
        .stApp {{ background-color: {layout['cor_fundo']}; }}
        [data-testid="stSidebar"] {{ background-color: white; border-right: 3px solid {layout['cor_primaria']}; }}
        h1, h2, h3 {{ color: {layout['cor_primaria']}; }}
        .stButton>button {{ background-color: {layout['cor_primaria']}; color: white; border-radius: 8px; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. TELA DE LOGIN ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, col_login, c3 = st.columns([1, 1.8, 1])
    with col_login:
        # AGORA VAI CARREGAR POIS O CÓDIGO CONSERTOU O LINK
        st.image(layout['logo_sistema_url'], use_container_width=True)
        with st.container(border=True):
            st.subheader("Nexus CRM - Acesso")
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("ACESSAR NEXXUS"):
                if u == "admin" and p == "consenso123":
                    st.session_state.usuario = {"nome": "Admin", "perfil": "admin"}
                    st.rerun()
                else:
                    st.error("Credenciais Inválidas")
        st.image(layout['logo_empresa_url'], width=150)
    st.stop()

# --- 5. INTERFACE PRINCIPAL COM MENU FIXO ---
with st.sidebar:
    st.image(layout['logo_sistema_url'], use_container_width=True)
    st.divider()
    
    # MENU COM LINKS APARECENDO DIRETO NA TELA
    menu = st.radio(
        "MENU DE NAVEGAÇÃO",
        ["📊 Dashboard", "⚙️ Nova Demanda APUC", "🏢 Gestão de Clientes", "👥 Usuários", "🎨 Configurar Layout"],
        index=1
    )
    
    st.markdown("<br>"*5, unsafe_allow_html=True)
    st.divider()
    st.image(layout['logo_empresa_url'], width=150)
    if st.button("Sair"):
        st.session_state.usuario = None
        st.rerun()

# --- TELAS ---
if menu == "⚙️ Nova Demanda APUC":
    st.title("⚙️ Calculadora Técnica APUC")
    st.write(f"Operação: **{layout['nome_empresa']}**")
    # Aqui amanhã colocaremos os campos de Levantamento, Dev, etc.
    st.info("Sistema pronto para as 5 etapas de cálculo.")

else:
    st.title(menu)
    st.write("Funcionalidade em desenvolvimento para amanhã.")
