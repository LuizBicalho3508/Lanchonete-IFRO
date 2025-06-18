# Login.py

import streamlit as st
from database import criar_tabelas, add_user, verify_user

# Inicializa o banco e as tabelas
criar_tabelas()

st.set_page_config(page_title="Login - Lanchonete IFRO", layout="centered")

st.title("Bem-vindo à Lanchonete IFRO 🍔")

# Inicializa o estado de login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# Se o usuário já estiver logado, ofereça para ir para a página principal ou deslogar
if st.session_state.logged_in:
    st.write(f"Você já está logado como **{st.session_state.username}** ({st.session_state.role}).")
    if st.button("Ir para a página de pedidos"):
        st.switch_page("pages/1_ Fazer_Pedido.py")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.success("Você foi desconectado com sucesso!")
        st.rerun()

else:
    # Abas para Login e Registro
    tab1, tab2 = st.tabs(["Entrar", "Registrar-se"])

    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Usuário", key="login_user")
            password = st.text_input("Senha", type="password", key="login_pass")
            submitted = st.form_submit_button("Entrar")

            if submitted:
                role = verify_user(username, password)
                if role:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.success("Login realizado com sucesso!")
                    # Redireciona o usuário para a página de pedidos após o login
                    st.switch_page("pages/1_ Fazer_Pedido.py")
                else:
                    st.error("Usuário ou senha inválidos.")

    with tab2:
        st.subheader("Criar Nova Conta")
        with st.form("register_form"):
            new_username = st.text_input("Escolha um nome de usuário", key="reg_user")
            new_password = st.text_input("Escolha uma senha", type="password", key="reg_pass")
            confirm_password = st.text_input("Confirme a senha", type="password", key="reg_conf_pass")
            
            reg_submitted = st.form_submit_button("Registrar")

            if reg_submitted:
                if not new_username or not new_password:
                    st.warning("Usuário e senha são obrigatórios.")
                elif new_password != confirm_password:
                    st.error("As senhas não coincidem.")
                else:
                    if add_user(new_username, new_password):
                        st.success("Conta criada com sucesso! Agora você pode fazer o login na aba 'Entrar'.")
                    else:
                        st.error("Este nome de usuário já existe.")

# A LINHA ABAIXO FOI REMOVIDA:
# st.info("Usuário administrador padrão: `admin`, senha: `admin123`")
