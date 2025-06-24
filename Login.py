# Login.py

import streamlit as st
from database import criar_tabelas, add_user, verify_user
import os
import re # Módulo para expressões regulares (validação de e-mail)

# --- FUNÇÃO DE VALIDAÇÃO DE E-MAIL ---
def is_valid_email(email):
    """Verifica se o formato do e-mail é válido."""
    # Expressão regular para validar um e-mail
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email)

# --- FUNÇÃO PARA CARREGAR O CSS ---
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Lanchonete IFRO",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)
load_css("style.css")
criar_tabelas()

# --- ESTADO DA SESSÃO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- PÁGINA DE LOGIN ---
if st.session_state.logged_in:
    st.title(f"👋 Bem-vindo de volta, {st.session_state.username}!")
    st.page_link("pages/1_ Fazer_Pedido.py", label="Ir para a página de pedidos", icon="🍔")
else:
    st.title("🍔 Bem-vindo à Lanchonete IFRO")
    st.write("Use seu e-mail para entrar ou registrar-se.")
    st.info("Para acesso administrativo, use: `admin@ifro.edu.br` | senha: `admin123`", icon="🔑")


    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            tab1, tab2 = st.tabs(["➡️ Entrar", "✍️ Registrar-se"])

            with tab1:
                with st.form("login_form"):
                    email = st.text_input("Seu E-mail", key="login_email")
                    password = st.text_input("Senha", type="password", key="login_pass")
                    if st.form_submit_button("Entrar", use_container_width=True, type="primary"):
                        role = verify_user(email, password)
                        if role:
                            st.session_state.logged_in = True
                            st.session_state.username = email
                            st.session_state.role = role
                            st.switch_page("pages/1_ Fazer_Pedido.py")
                        else:
                            st.error("E-mail ou senha inválidos.")

            with tab2:
                with st.form("register_form"):
                    new_email = st.text_input("Seu melhor e-mail")
                    new_password = st.text_input("Crie uma senha", type="password")
                    confirm_password = st.text_input("Confirme a senha", type="password")
                    
                    if st.form_submit_button("Registrar", use_container_width=True):
                        if not is_valid_email(new_email):
                            st.warning("Por favor, insira um endereço de e-mail válido.")
                        elif not new_password:
                            st.warning("O campo de senha não pode ser vazio.")
                        elif new_password != confirm_password:
                            st.error("As senhas não coincidem.")
                        else:
                            if add_user(new_email, new_password):
                                st.success("Conta criada com sucesso! Faça o login na aba 'Entrar'.")
                            else:
                                st.error("Este e-mail já está cadastrado.")
