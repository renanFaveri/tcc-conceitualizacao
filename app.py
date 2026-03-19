import streamlit as st
from graphviz import Digraph
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conceitualização de Beck", layout="wide")

# --- SISTEMA DE AUTENTICAÇÃO COM 2 LOGINS ---
def check_password():
    def password_entered():
        # Login Administrador
        if st.session_state["username"] == "admin" and st.session_state["password"] == "admin123":
            st.session_state["password_correct"] = True
            st.session_state["user_role"] = "admin"
            del st.session_state["password"] 
        # Login Psicólogo (Sem troca de senha)
        elif st.session_state["username"] == "psicologo" and st.session_state["password"] == "tcc2026":
            st.session_state["password_correct"] = True
            st.session_state["user_role"] = "user"
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("Acesso ao Sistema de Conceitualização")
        st.text_input("Usuário:", key="username")
        st.text_input("Senha:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Acesso ao Sistema de Conceitualização")
        st.text_input("Usuário:", key="username")
        st.text_input("Senha:", type="password", on_change=password_entered, key="password")
        st.error("😕 Usuário ou senha incorretos.")
        return False
    else:
        return True

if check_password():
    # --- BARRA LATERAL (LOGOUT E CARREGAR) ---
    st.sidebar.write(f"Logado como: **{st.session_state['user_role'].upper()}**")
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.header("Importar Dados")
    arquivo_carregado = st.sidebar.file_uploader("Carregar arquivo JSON", type="json")

    dados_importados = {}
    if arquivo_carregado is not None:
        dados_importados = json.load(arquivo_carregado)
        st.sidebar.success("Dados carregados!")

    # --- CABEÇALHO DO PRONTUÁRIO ---
    col_header1, col_header2, col_header3 = st.columns(3)
    with col_header1:
        nome_paciente = st.text_input("Paciente:", dados_importados.get("paciente", "Abe"))
    with col_header2:
        data_sessao = st.text_input("Data:", dados_importados.get("data", "06/03/2026"))
    with col_header3:
        num_sessao = st.text_input("Número da Sessão:", dados_importados.get("sessao", "12"))

    st.markdown("---")

    # --- GERENCIAMENTO DE ESTADO ---
    if "situacoes" in dados_importados:
        st.session_state.n_situacoes = len(dados_importados["situacoes"])
    elif 'n_situacoes' not in st.session_state:
        st.session_state.n_situacoes = 1

    def adicionar_situacao():
        st.session_state.n_situacoes += 1

    # --- SIDEBAR: ESTRUTURA COGNITIVA ---
    st.sidebar.header("Estrutura Cognitiva")
    historia = st.sidebar.text_area("História de Vida", dados_importados.get("historia", ""))
    crenca_nuclear = st.sidebar.text_area("Crença(s) Nuclear(es)", dados_importados.get("crenca", ""))
    regras_input = st.sidebar.text_area("Crenças Intermediárias", dados_importados.get("regras", ""))
    estrategias = st.sidebar.text_area("Estratégias de Enfrentamento", dados_importados.get("estrategias", ""))

    st.sidebar.markdown("---")
    st.sidebar.header("Situações Atuais")

    dados_situacoes = []
    for i in range(st.session_state.n_situacoes):
        # Recupera dados da situação se houver importação
        sit_import = dados_importados["situacoes"][i] if "situacoes" in dados_importados and i < len(dados_importados["situacoes"]) else {}
        
        with st.sidebar.expander(f"Situação {i+1}", expanded=True):
            sit = st.text_input(f"Situação {i+1}", value=sit_import.get("sit", ""), key=f"sit_{i}")
            pa = st.text_input(f"Pensamento Automático {i+1}", value=sit_import.get("pa", ""), key=f"pa_{i}")
            significado = st.text_input(f"Significado do P.A. {i+1}", value=sit_import.get("sig", ""), key=f"sig_{i}")
            emocao = st.text_input(f"Emoção {i+1}", value=sit_import.get("emo", ""), key=f"emo_{i}")
            comportamento = st.text_input(f"Comportamento {i+1}", value=sit_import.get("comp", ""), key=f"comp_{i}")
            dados_situacoes.append({"sit": sit, "pa": pa, "sig": significado, "emo": emocao, "comp": comportamento})

    st.sidebar.button("➕ Adicionar Nova Situação", on_click=adicionar_situacao)

    # --- GERAÇÃO DO DIAGRAMA ---
    def gerar_diagrama_beck():
        dot = Digraph(format='png')
        dot.attr(rankdir='TB', nodesep='0.2', ranksep='0.4')
        dot.attr('node', shape='rectangle', style='filled', fontname='Arial', fillcolor='white', fontsize='11')

        nos_superiores = []
        if historia.strip():
            dot.node('HIST', f"HISTÓRIA DE VIDA E PRECIPITANTES:\n{historia}")
            nos_superiores.append('HIST')
        if crenca_nuclear.strip():
            dot.node('CN', f"CRENÇA(S) NUCLEAR(ES):\n{crenca_nuclear}")
            nos_superiores.append('CN')
        if regras_input.strip():
            dot.node('CI', f"CRENÇAS INTERMEDIÁRIAS:\n{regras_input}")
            nos_superiores.append('CI')
        if estrategias.strip():
            dot.node('EST', f"ESTRATÉGIAS DE ENFRENTAMENTO:\n{estrategias}")
            nos_superiores.append('EST')

        for i in range(len(nos_superiores) - 1):
            dot.edge(nos_superiores[i], nos_superiores[i+1])

        ultimo_no_superior = nos_superiores[-1] if nos_superiores else None

        for i, d in enumerate(dados_situacoes):
            if d['sit'].strip():
                prefix = f"S{i}"
                dot.node(f"{prefix}_S", f"SITUAÇÃO {i+1}:\n{d['sit']}")
                dot.node(f"{prefix}_PA", f"PENSAMENTO(S) AUTOMÁTICO(S):\n{d['pa']}")
                dot.node(f"{prefix}_SIG", f"SIGNIFICADO DO P.A.:\n{d['sig']}")
                dot.node(f"{prefix}_EMO", f"EMOÇÕES:\n{d['emo']}")
                dot.node(f"{prefix}_COMP", f"COMPORTAMENTO:\n{d['comp']}")

                if ultimo_no_superior:
                    dot.edge(ultimo_no_superior, f"{prefix}_S")

                dot.edge(f"{prefix}_S", f"{prefix}_PA", dir="none")
                dot.edge(f"{prefix}_PA", f"{prefix}_SIG", dir="none")
                dot.edge(f"{prefix}_SIG", f"{prefix}_EMO", dir="none")
                dot.edge(f"{prefix}_EMO", f"{prefix}_COMP", dir="none")
        return dot

    # --- EXIBIÇÃO ---
    st.subheader(f"Diagrama de Conceitualização: {nome_paciente}")
    st.graphviz_chart(gerar_diagrama_beck())

    # --- SALVAR DADOS ---
    # --- ÁREA DE DOWNLOAD (Sincronizada) ---
    st.markdown("---")
    st.subheader("💾 Salvar")

    dados_para_salvar = {
        "paciente": nome_paciente,
        "data": data_sessao,
        "sessao": num_sessao,
        "historia": historia,
        "crenca": crenca_nuclear,
        "regras": regras_input,
        "estrategias": estrategias,
        "situacoes": dados_situacoes  # Aqui estão os dados colhidos no loop acima
    }

    # Gerar o JSON
    json_dados = json.dumps(dados_para_salvar, indent=4, ensure_ascii=False)

    # O botão de download
    st.download_button(
        label="Baixar dados",
        data=json_dados,
        file_name=f"tcc_{nome_paciente.replace(' ', '_')}.json",
        mime="application/json",
        key="btn_download_json" # Chave única para evitar conflitos
    )