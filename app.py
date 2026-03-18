import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CRM Pro - Gestão de Manutenção", layout="wide")

# --- INICIALIZAÇÃO DO BANCO DE DADOS (SESSION STATE) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        'empresas': pd.DataFrame(columns=['ID', 'Nome', 'CNPJ', 'Valor_Hora']),
        'contatos': pd.DataFrame(columns=['ID', 'Empresa', 'Nome', 'Email']),
        'demandas': pd.DataFrame(columns=['ID', 'Empresa', 'RM', 'Tipo', 'Horas', 'Valor', 'Status', 'Titulo']),
        'logs': []
    }

# --- BARRA LATERAL (NAVEGAÇÃO) ---
st.sidebar.title("🛠️ CRM de Serviços")
menu = st.sidebar.selectbox("Navegação", ["📊 Dashboard", "🏢 Empresas & Contatos", "⚙️ Nova Demanda (APUC)", "📧 Mailing (Gmail)"])

# ------------------------------------------------------------------
# MÓDULO 1: DASHBOARD (FATURAMENTO E ANDAMENTO)
# ------------------------------------------------------------------
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Financeiro Analítico")
    
    df_d = st.session_state.db['demandas']
    
    if df_d.empty:
        st.info("Nenhuma demanda registrada para gerar o dashboard.")
    else:
        # KPIs Superiores
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Faturado (Evolutivas)", f"R$ {df_d[df_d['Tipo']=='Evolutiva']['Valor'].sum():,.2f}")
        c2.metric("Horas Totais no Mês", f"{df_d['Horas'].sum():,.1f} h")
        c3.metric("Demandas em Aberto", len(df_d[df_d['Status'] != 'Faturado']))
        c4.metric("Ticket Médio/RM", f"R$ {df_d[df_d['Tipo']=='Evolutiva']['Valor'].mean():,.2f}" if not df_d[df_d['Tipo']=='Evolutiva'].empty else "0")

        # Gráfico Mensal (Sintético)
        st.subheader("📈 Faturamento Mensal (Evolutivas)")
        df_mensal = df_d[df_d['Tipo']=='Evolutiva'].groupby('RM')['Valor'].sum().reset_index()
        fig = px.bar(df_mensal, x='RM', y='Valor', color='RM', title="Receita por Mês de Referência (RM)")
        st.plotly_chart(fig, use_container_width=True)

        # Visão Analítica
        st.subheader("📑 Visão Analítica de Demandas")
        # Filtros de Dashboard
        filtro_rm = st.multiselect("Filtrar por RM", df_d['RM'].unique())
        df_filtrado = df_d[df_d['RM'].isin(filtro_rm)] if filtro_rm else df_d
        st.dataframe(df_filtrado, use_container_width=True)

# ------------------------------------------------------------------
# MÓDULO 2: EMPRESAS E CONTATOS
# ------------------------------------------------------------------
elif menu == "🏢 Empresas & Contatos":
    st.title("🏢 Gestão de Clientes")
    
    tab1, tab2 = st.tabs(["Cadastrar Empresa", "Cadastrar Contatos"])
    
    with tab1:
        with st.form("cad_empresa"):
            nome = st.text_input("Nome da Empresa / Cliente")
            cnpj = st.text_input("CNPJ")
            v_hora = st.number_input("Valor da Hora Técnica (R$)", value=150.0)
            if st.form_submit_button("Salvar Empresa"):
                new_row = {"ID": len(st.session_state.db['empresas'])+1, "Nome": nome, "CNPJ": cnpj, "Valor_Hora": v_hora}
                st.session_state.db['empresas'] = pd.concat([st.session_state.db['empresas'], pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Empresa {nome} cadastrada!")

    with tab2:
        if st.session_state.db['empresas'].empty:
            st.warning("Cadastre uma empresa primeiro.")
        else:
            with st.form("cad_contato"):
                emp = st.selectbox("Selecione a Empresa", st.session_state.db['empresas']['Nome'])
                c_nome = st.text_input("Nome do Contato")
                c_email = st.text_input("E-mail")
                if st.form_submit_button("Salvar Contato"):
                    new_c = {"ID": len(st.session_state.db['contatos'])+1, "Empresa": emp, "Nome": c_nome, "Email": c_email}
                    st.session_state.db['contatos'] = pd.concat([st.session_state.db['contatos'], pd.DataFrame([new_c])], ignore_index=True)
                    st.success(f"Contato {c_nome} vinculado à {emp}!")

# ------------------------------------------------------------------
# MÓDULO 3: APUC (DEMANDAS E CÁLCULOS)
# ------------------------------------------------------------------
elif menu == "⚙️ Nova Demanda (APUC)":
    st.title("⚙️ Calculadora APUC e Lançamento de RM")
    
    if st.session_state.db['empresas'].empty:
        st.error("Cadastre uma empresa antes de criar demandas.")
    else:
        with st.form("lancamento_apuc"):
            col1, col2, col3 = st.columns(3)
            cliente = col1.selectbox("Cliente", st.session_state.db['empresas']['Nome'])
            rm = col2.selectbox("Mês de Referência (RM)", ["2024/03", "2024/04", "2024/05", "2024/06"])
            tipo = col3.radio("Classificação", ["Corretiva", "Evolutiva"])
            
            titulo = st.text_input("Título do Chamado / Caso de Uso")
            
            st.write("---")
            c1, c2, c3 = st.columns(3)
            comp_base = c1.selectbox("Complexidade (Peso)", [("Baixa", 8), ("Média", 20), ("Alta", 40)])
            perc_alt = c2.slider("% de Alteração no Caso de Uso", 0, 100, 100)
            fator_equipe = c3.selectbox("Equipe/Momento (Fator)", [("Sênior", 0.8), ("Pleno", 1.0), ("Júnior", 1.4)])
            
            justificativa = st.text_area("Justificativa (Obrigatório para Log)")
            
            if st.form_submit_button("Calcular e Registrar"):
                # Cálculo da Lógica APUC
                h_base = comp_base[1]
                h_calculadas = (h_base * (perc_alt/100)) * fator_equipe[1]
                
                # Busca valor da hora da empresa
                v_hora_cli = st.session_state.db['empresas'].loc[st.session_state.db['empresas']['Nome'] == cliente, 'Valor_Hora'].values[0]
                valor_total = h_calculadas * v_hora_cli if tipo == "Evolutiva" else 0.0
                
                # Salva a demanda
                new_d = {
                    "ID": len(st.session_state.db['demandas'])+1,
                    "Empresa": cliente, "RM": rm, "Tipo": tipo,
                    "Horas": round(h_calculadas, 2), "Valor": round(valor_total, 2),
                    "Status": "A Faturar", "Titulo": titulo
                }
                st.session_state.db['demandas'] = pd.concat([st.session_state.db['demandas'], pd.DataFrame([new_d])], ignore_index=True)
                
                # Log de Alteração
                log_entry = f"{datetime.now()}: {titulo} registrado como {tipo} para {cliente}. Motivo: {justificativa}"
                st.session_state.db['logs'].append(log_entry)
                
                st.success(f"Registrado! {h_calculadas:.1f} horas calculadas. Total: R$ {valor_total:,.2f}")

# ------------------------------------------------------------------
# MÓDULO 4: MAILING INTEGRADO (GMAIL)
# ------------------------------------------------------------------
elif menu == "📧 Mailing (Gmail)":
    st.title("📧 Mailing Interado Gmail")
    
    if st.session_state.db['contatos'].empty:
        st.warning("Não há contatos cadastrados para mailing.")
    else:
        with st.expander("Configurar Acesso Gmail"):
            user_mail = st.text_input("Seu E-mail Gmail")
            user_pass = st.text_input("Senha de App Gmail", type="password")
            st.info("Obtenha sua 'Senha de App' nas configurações de Segurança do Google.")

        destinos = st.multiselect("Para:", st.session_state.db['contatos']['Email'])
        assunto = st.text_input("Assunto do E-mail")
        mensagem = st.text_area("Corpo do E-mail (HTML permitido)")
        
        if st.button("Enviar em Massa"):
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(user_mail, user_pass)
                
                for destino in destinos:
                    msg = MIMEMultipart()
                    msg['From'] = user_mail
                    msg['To'] = destino
                    msg['Subject'] = assunto
                    msg.attach(MIMEText(mensagem, 'html'))
                    server.sendmail(user_mail, destino, msg.as_string())
                
                server.quit()
                st.success(f"Sucesso! E-mail enviado para {len(destinos)} contatos.")
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")

# EXIBIÇÃO DE LOGS NO RODAPÉ
st.sidebar.divider()
if st.sidebar.checkbox("Ver Logs do Sistema"):
    st.write("### 📜 Logs de Alteração (Audit)")
    for l in reversed(st.session_state.db['logs']):
        st.caption(l)
