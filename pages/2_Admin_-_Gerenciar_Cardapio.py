# pages/2_Admin_-_Gerenciar_Cardapio.py

import streamlit as st
import pandas as pd
from database import get_produtos, add_produto, update_produto, delete_produto

# --- VERIFICAÇÃO DE LOGIN E PERMISSÃO ---
if not st.session_state.get('logged_in') or st.session_state.get('role') != 'admin':
    st.error("Acesso negado. Esta página é restrita aos administradores.")
    st.page_link("Login.py", label="Ir para a página de Login")
    st.stop()

st.set_page_config(page_title="Gerenciar Cardápio", layout="centered")
st.title("🛠️ Gerenciamento do Cardápio")

# --- Exibir cardápio atual ---
st.subheader("Cardápio Atual")
try:
    produtos = get_produtos()
    df_produtos = pd.DataFrame(produtos, columns=["id", "nome", "categoria", "preco"])
    st.dataframe(df_produtos, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Não foi possível carregar os produtos: {e}")


# --- Abas para CRUD ---
tab1, tab2, tab3 = st.tabs(["➕ Adicionar Produto", "✏️ Editar Produto", "❌ Remover Produto"])

with tab1:
    st.subheader("Adicionar Novo Produto")
    with st.form("add_form", clear_on_submit=True):
        nome = st.text_input("Nome do Produto")
        categoria = st.selectbox("Categoria", ["Salgados", "Doces", "Bebidas", "Outros"])
        preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            add_produto(nome, categoria, preco)
            st.success(f"Produto '{nome}' adicionado com sucesso!")
            st.rerun()

with tab2:
    st.subheader("Editar um Produto Existente")
    produto_id_edit = st.selectbox("Selecione um produto para editar", 
                                   options=df_produtos['id'], 
                                   format_func=lambda x: f"{df_produtos.loc[df_produtos['id']==x, 'nome'].iloc[0]} (ID: {x})")
    
    if produto_id_edit:
        produto_selecionado = df_produtos.loc[df_produtos['id'] == produto_id_edit].iloc[0]
        
        with st.form("edit_form"):
            st.write(f"Editando: **{produto_selecionado['nome']}**")
            
            novo_nome = st.text_input("Novo Nome", value=produto_selecionado['nome'])
            nova_categoria = st.selectbox("Nova Categoria", 
                                          ["Salgados", "Doces", "Bebidas", "Outros"], 
                                          index=["Salgados", "Doces", "Bebidas", "Outros"].index(produto_selecionado['categoria']))
            novo_preco = st.number_input("Novo Preço", value=float(produto_selecionado['preco']), format="%.2f")
            
            edit_submitted = st.form_submit_button("Salvar Alterações")
            if edit_submitted:
                update_produto(produto_id_edit, novo_nome, nova_categoria, novo_preco)
                st.success("Produto atualizado com sucesso!")
                st.rerun()

with tab3:
    st.subheader("Remover um Produto")
    produto_id_delete = st.selectbox("Selecione um produto para remover",
                                     options=df_produtos['id'],
                                     format_func=lambda x: f"{df_produtos.loc[df_produtos['id']==x, 'nome'].iloc[0]} (ID: {x})",
                                     key="delete_select")
    
    if produto_id_delete:
        produto_a_remover = df_produtos.loc[df_produtos['id'] == produto_id_delete, 'nome'].iloc[0]
        st.warning(f"Você tem certeza que deseja remover **{produto_a_remover}**?")
        
        if st.button("Sim, remover este produto", type="primary"):
            delete_produto(produto_id_delete)
            st.success("Produto removido com sucesso!")
            st.rerun()