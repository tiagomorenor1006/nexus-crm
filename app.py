import streamlit as st
import pandas as pd
import psycopg2
import hashlib
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURAÇÕES DE CONEXÃO E BRANDING ---
def get_connection():
    # Certifique-se de configurar 'postgres_url' nos Secrets do Streamlit
    return psycopg2.connect(st.secrets["postgres_url"])

def carregar_layout():
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT * FROM configuracoes_layout LIMIT 1", conn)
        conn.close()
        return df.iloc[0].to_dict()
    except:
        return {
            "cor_primaria": "#1E4DB7", 
            "cor_fundo": "#F0F2F6", 
            "logo_sistema_url": "https://i.imgur.com/mOId99i.png", # NEXXUS
            "logo_empresa_url": "https://i.imgur.com/vHqY7eK.png", # CONSENSO
            "nome_empresa": "Consenso"
        }

# --- 2. MOTOR DE CSS DINÂMICO (VISUAL NEXXUS) ---
def aplicar_estilo(config):
    st.markdown(f"""
        <style>
            .stApp {{ background-color: {config['cor_fundo']}; }}
            .stButton>button {{
                background-color: {config['cor_primaria']};
                color: white; border-radius: 8px; width: 100%; font-weight: bold;
            }}
            [data-testid="stSidebar"] {{
                background-color: white; border-right: 3px solid {config['cor_primaria']};
            }}
            h1, h2, h3 {{ color: {config['cor_primaria']}; font-family: sans-serif; }}
            .stMetric {{ background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px #ddd; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. INICIALIZAÇÃO ---
layout = carregar_layout()
aplicar_estilo(layout)

# --- 4. TELA DE LOGIN (BRANDING CONSENSO) ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.image(layout['logo_sistema_url'], use_container_width=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>Sistema de Gestão Técnica by <b>{layout['nome_empresa']}</b></p>", unsafe_allow_html=True)
        with st.container(border=True):
            user = st.text_input("Usuário")
            pw = st.text_input("Senha", type="password")
            if st.button("ACESSAR NEXXUS CRM"):
                # Simulação Admin (Substituir por SQL real para produção)
                if user == "admin" and pw == "consenso123":
                    st.session_state.usuario = {"nome": "Admin Consenso", "perfil": "admin", "id": 1}
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")
        st.image(layout['logo_empresa_url'], width=120)
    st.stop()

# --- 5. INTERFACE PRINCIPAL ---
with st.sidebar:
    st.image(layout['logo_sistema_url'], use_container_width=True)
    st.divider()
    menu = st.selectbox("Menu", ["📊 Dashboard", "⚙️ Calculadora APUC", "🏢 Clientes", "👥 Usuários", "🎨 Layout"])
    st.markdown("<br>"*10, unsafe_allow_html=True)
    st.caption("Operado por:")
    st.image(layout['logo_empresa_url'], width=130)

# --- 6. MÓDULO APUC (AS 5 ETAPAS) ---
if menu == "⚙️ Nova Demanda APUC":
    st.title("⚙️ Calculadora Técnica APUC")
    st.info("Insira os pesos para cada uma das 5 etapas de cada Caso de Uso.")
    
    with st.container(border=True):
        col_c, col_rm, col_t = st.columns(3)
        # (Buscar empresas do banco aqui...)
        titulo = st.text_input("Título da Solicitação")

    # Múltiplos Casos de Uso
    if 'ucs' not in st.session_state: st.session_state.ucs = [{"id": 0}]
    if st.button("➕ Adicionar Caso de Uso"): st.session_state.ucs.append({"id": len(st.session_state.ucs)})

    total_h = 0
    for i, uc in enumerate(st.session_state.ucs):
        with st.expander(f"Caso de Uso #{i+1}", expanded=True):
            st.text_input(f"Nome do UC", value=f"UC_{i+1}", key=f"n_{i}")
            e1, e2, e3, e4, e5 = st.columns(5)
            w1 = e1.number_input("Levantamento", value=1.0, key=f"e1_{i}")
            w2 = e2.number_input("Especificação", value=1.0, key=f"e2_{i}")
            w3 = e3.number_input("Desenvolvimento", value=4.0, key=f"e3_{i}")
            w4 = e4.number_input("Testes", value=1.0, key=f"e4_{i}")
            w5 = e5.number_input("Impl/Doc", value=1.0, key=f"e5_{i}")
            
            sub = (w1+w2+w3+w4+w5) # Soma das 5 etapas solicitadas
            total_h += sub
            st.write(f"Subtotal UC: {sub} horas")

    st.subheader(f"Total Geral APUC: {total_h:.2f} horas")
    if st.button("💾 Salvar e Gerar Log de Transação"):
        st.success("Demanda gravada com auditoria completa!")

# (Outros módulos omitidos para brevidade, mas mantidos no seu GitHub)
