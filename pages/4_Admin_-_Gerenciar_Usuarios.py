# pages/4_Admin_-_Gerenciar_Usuarios.py

import streamlit as st
import pandas as pd
from database import get_all_users, get_user_by_id, update_user_by_admin, reset_user_password, delete_user
import re # Módulo para validação de e-mail

# --- FUNÇÃO DE VALIDAÇÃO DE E-MAIL ---
def is_valid_email(email):
    """Verifica se o formato do e-mail é válido."""
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email)

# --- VERIFICAÇÃO DE LOGIN E PERMISSÃO DE ADMIN ---
if not st.session_state.get('logged_in') or st.session_state.get('role') != 'admin':
    st.error("Acesso negado. Esta página é restrita aos administradores.")
    st.page_link("Login.py", label="Ir para a página de Login")
    st.stop()

st.title("🔑 Gerenciamento de Usuários")

# --- Exibir lista de usuários ---
st.header("Lista de Usuários Ativos")

try:
    all_users = get_all_users()
    df_users = pd.DataFrame(all_users, columns=['ID', 'E-mail (Usuário)', 'Perfil'])
    st.dataframe(df_users, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Não foi possível carregar os usuários: {e}")
    st.stop()

st.divider()

# --- Abas para Editar e Excluir ---
tab1, tab2 = st.tabs(["✏️ Editar Usuário", "❌ Excluir Usuário"])

with tab1:
    st.subheader("Alterar Informações de um Usuário")

    user_id_to_edit = st.selectbox(
        "Selecione um usuário para editar",
        options=df_users['ID'],
        format_func=lambda x: f"{df_users.loc[df_users['ID']==x, 'E-mail (Usuário)'].iloc[0]} (ID: {x})",
        key="edit_select"
    )

    if user_id_to_edit:
        selected_user = get_user_by_id(user_id_to_edit)
        
        with st.form("edit_user_form"):
            st.write(f"Editando o usuário: **{selected_user['username']}**")
            
            new_email = st.text_input("E-mail do Usuário", value=selected_user['username'])
            new_role = st.selectbox("Perfil", ["cliente", "admin"], index=["cliente", "admin"].index(selected_user['role']))

            st.markdown("---")
            st.write("Redefinir Senha (opcional)")
            new_password = st.text_input("Nova Senha", type="password", placeholder="Deixe em branco para não alterar")

            if st.form_submit_button("Salvar Alterações", use_container_width=True, type="primary"):
                if not is_valid_email(new_email):
                    st.error("O formato do e-mail inserido é inválido.")
                else:
                    update_success = update_user_by_admin(user_id_to_edit, new_email, new_role)
                    if not update_success:
                        st.error("O e-mail escolhido já está em uso. Tente outro.")
                    else:
                        if new_password:
                            reset_user_password(user_id_to_edit, new_password)
                        st.success(f"Informações do usuário '{new_email}' atualizadas com sucesso!")
                        st.rerun()

with tab2:
    st.subheader("Excluir um Usuário")
    st.warning("ATENÇÃO: Esta ação é permanente e não pode ser desfeita.", icon="⚠️")

    user_id_to_delete = st.selectbox(
        "Selecione um usuário para excluir",
        options=df_users['ID'],
        format_func=lambda x: f"{df_users.loc[df_users['ID']==x, 'E-mail (Usuário)'].iloc[0]} (ID: {x})",
        key="delete_select"
    )

    if user_id_to_delete:
        user_to_delete_info = get_user_by_id(user_id_to_delete)
        
        if user_to_delete_info and user_to_delete_info['username'] == st.session_state.get('username'):
            st.error("Você não pode excluir a sua própria conta de administrador enquanto está logado.")
        else:
            st.markdown(f"Você está prestes a excluir o usuário: **{user_to_delete_info['username']}**.")
            
            if st.button("Excluir Usuário Permanentemente", type="primary"):
                delete_user(user_id_to_delete)
                st.success(f"Usuário '{user_to_delete_info['username']}' foi excluído com sucesso.")
                st.rerun()
