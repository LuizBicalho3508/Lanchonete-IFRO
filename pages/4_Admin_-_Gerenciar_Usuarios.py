# pages/4_Admin_-_Gerenciar_Usuarios.py

import streamlit as st
import pandas as pd
from database import get_all_users, get_user_by_id, update_user_by_admin, reset_user_password, delete_user

# --- VERIFICAÇÃO DE LOGIN E PERMISSÃO DE ADMIN ---
if not st.session_state.get('logged_in') or st.session_state.get('role') != 'admin':
    st.error("Acesso negado. Esta página é restrita aos administradores.")
    st.page_link("Login.py", label="Ir para a página de Login")
    st.stop()

st.set_page_config(page_title="Gerenciar Usuários", layout="wide")
st.title("🔑 Gerenciamento de Usuários")

# --- Exibir lista de usuários ---
st.header("Lista de Usuários Ativos")

try:
    all_users = get_all_users()
    df_users = pd.DataFrame(all_users, columns=['ID', 'Usuário', 'Perfil'])
    st.dataframe(df_users, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Não foi possível carregar os usuários: {e}")
    st.stop()


# --- Abas para Editar e Excluir ---
tab1, tab2 = st.tabs(["✏️ Editar Usuário", "❌ Excluir Usuário"])

with tab1:
    st.subheader("Alterar Informações de um Usuário")

    # Selecionar usuário para editar
    user_id_to_edit = st.selectbox(
        "Selecione um usuário para editar",
        options=df_users['ID'],
        format_func=lambda x: f"{df_users.loc[df_users['ID']==x, 'Usuário'].iloc[0]} (ID: {x})",
        key="edit_select"
    )

    if user_id_to_edit:
        selected_user = get_user_by_id(user_id_to_edit)
        
        with st.form("edit_user_form"):
            st.write(f"Editando o usuário: **{selected_user['username']}**")
            
            new_username = st.text_input("Nome de Usuário", value=selected_user['username'])
            new_role = st.selectbox("Perfil", ["cliente", "admin"], index=["cliente", "admin"].index(selected_user['role']))

            st.markdown("---")
            st.write("Redefinir Senha (opcional)")
            new_password = st.text_input("Nova Senha", type="password", placeholder="Deixe em branco para não alterar")

            submitted = st.form_submit_button("Salvar Alterações")
            if submitted:
                # Atualizar username e perfil
                update_success = update_user_by_admin(user_id_to_edit, new_username, new_role)
                if not update_success:
                    st.error("O nome de usuário escolhido já está em uso. Tente outro.")
                else:
                    # Resetar a senha se uma nova foi fornecida
                    if new_password:
                        reset_user_password(user_id_to_edit, new_password)
                        st.success(f"Informações e senha do usuário '{new_username}' atualizadas com sucesso!")
                    else:
                        st.success(f"Informações do usuário '{new_username}' atualizadas com sucesso!")
                    
                    # Força a atualização da lista de usuários na tela
                    st.rerun()

with tab2:
    st.subheader("Excluir um Usuário")
    st.warning("ATENÇÃO: Esta ação é permanente e não pode ser desfeita.", icon="⚠️")

    # Selecionar usuário para excluir
    user_id_to_delete = st.selectbox(
        "Selecione um usuário para excluir",
        options=df_users['ID'],
        format_func=lambda x: f"{df_users.loc[df_users['ID']==x, 'Usuário'].iloc[0]} (ID: {x})",
        key="delete_select"
    )

    if user_id_to_delete:
        user_to_delete_info = get_user_by_id(user_id_to_delete)
        
        # Impede que o admin logado se auto-delete
        admin_logado_id = get_user_by_id(st.session_state['username'])
        if user_to_delete_info and user_to_delete_info['username'] == st.session_state.get('username'):
            st.error("Você não pode excluir a sua própria conta de administrador enquanto está logado.")
        else:
            st.markdown(f"Você está prestes a excluir o usuário: **{user_to_delete_info['username']}**.")
            
            confirm_delete = st.checkbox("Sim, eu entendo as consequências e quero excluir este usuário.")

            if st.button("Excluir Usuário Permanentemente", disabled=not confirm_delete, type="primary"):
                delete_user(user_id_to_delete)
                st.success(f"Usuário '{user_to_delete_info['username']}' foi excluído com sucesso.")
                st.rerun()
