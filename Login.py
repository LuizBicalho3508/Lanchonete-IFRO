# Login.py

import streamlit as st
from database import criar_tabelas, add_user, verify_user
import os

# --- FUNÇÃO PARA CARREGAR O CSS ---
def load_css(file_name):
    """Carrega um arquivo CSS local."""
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA PÁGINA ---
# A configuração de tema (base, primaryColor) foi movida para o .streamlit/config.toml
# Mantemos apenas as configurações de layout aqui.
st.set_page_config(
    page_title="Lanchonete IFRO",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carrega o nosso CSS customizado
load_css("style.css")

# Inicializa o banco e as tabelas na primeira execução
criar_tabelas()

# --- ESTADO DA SESSÃO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- PÁGINA DE LOGIN ---
if st.session_state.logged_in:
    # Se já estiver logado, mostra uma mensagem e um botão para navegar
    st.title(f"👋 Bem-vindo de volta, {st.session_state.username}!")
    st.write("Você já está conectado ao sistema.")
    st.page_link("pages/1_ Fazer_Pedido.py", label="Ir para a página de pedidos", icon="🍔")
else:
    # Layout centralizado para o formulário de login/registro
    st.title("🍔 Bem-vindo à Lanchonete IFRO")
    st.write("Faça login ou registre-se para continuar.")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            tab1, tab2 = st.tabs(["➡️ Entrar", "✍️ Registrar-se"])

            with tab1:
                with st.form("login_form"):
                    st.text_input("Usuário", key="login_user")
                    st.text_input("Senha", type="password", key="login_pass")
                    if st.form_submit_button("Entrar", use_container_width=True, type="primary"):
                        role = verify_user(st.session_state.login_user, st.session_state.login_pass)
                        if role:
                            st.session_state.logged_in = True
                            st.session_state.username = st.session_state.login_user
                            st.session_state.role = role
                            st.switch_page("pages/1_ Fazer_Pedido.py")
                        else:
                            st.error("Usuário ou senha inválidos.")

            with tab2:
                with st.form("register_form"):
                    new_username = st.text_input("Escolha um nome de usuário")
                    new_password = st.text_input("Escolha uma senha", type="password")
                    confirm_password = st.text_input("Confirme a senha", type="password")
                    
                    if st.form_submit_button("Registrar", use_container_width=True):
                        if not new_username or not new_password:
                            st.warning("Usuário e senha são obrigatórios.")
                        elif new_password != confirm_password:
                            st.error("As senhas não coincidem.")
                        else:
                            if add_user(new_username, new_password):
                                st.success("Conta criada com sucesso! Faça o login na aba 'Entrar'.")
                            else:
                                st.error("Este nome de usuário já existe.")
