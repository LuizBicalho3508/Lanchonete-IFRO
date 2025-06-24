# pages/2_Admin_-_Gerenciar_Cardapio.py

import streamlit as st
import pandas as pd
from database import get_produtos, add_produto, update_produto, delete_produto

# --- VERIFICAÇÃO DE LOGIN E PERMISSÃO ---
if not st.session_state.get('logged_in') or st.session_state.get('role') != 'admin':
    st.error("Acesso negado. Esta página é restrita aos administradores.")
    st.page_link("Login.py", label="Ir para a página de Login", icon="🏠")
    st.stop()

st.title("⚙️ Gerenciamento do Cardápio")

# --- Exibir cardápio atual em um container ---
with st.container(border=True):
    st.subheader("Cardápio Atual")
    try:
        produtos = get_produtos()
        df_produtos = pd.DataFrame(produtos, columns=["id", "nome", "categoria", "preco"])
        st.dataframe(df_produtos, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Não foi possível carregar os produtos: {e}")
        st.stop()

st.divider()

# --- Abas para CRUD ---
st.subheader("Operações do Cardápio")
tab1, tab2, tab3 = st.tabs(["➕ Adicionar", "✏️ Editar", "❌ Remover"])

with tab1:
    with st.form("add_form", clear_on_submit=True):
        st.markdown("##### Adicionar Novo Produto")
        nome = st.text_input("Nome do Produto")
        categoria = st.selectbox("Categoria", ["Salgados", "Doces", "Bebidas", "Outros"])
        preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Adicionar Produto", use_container_width=True, type="primary"):
            add_produto(nome, categoria, preco)
            st.success(f"Produto '{nome}' adicionado!")
            st.rerun()

with tab2:
    st.markdown("##### Editar um Produto Existente")
    produto_id_edit = st.selectbox("Selecione um produto", 
                                   options=df_produtos['id'], 
                                   format_func=lambda x: f"{df_produtos.loc[df_produtos['id']==x, 'nome'].iloc[0]} (ID: {x})")
    
    if produto_id_edit:
        produto_selecionado = df_produtos.loc[df_produtos['id'] == produto_id_edit].iloc[0]
        with st.form("edit_form"):
            novo_nome = st.text_input("Novo Nome", value=produto_selecionado['nome'])
            nova_categoria = st.selectbox("Nova Categoria", 
                                          options=["Salgados", "Doces", "Bebidas", "Outros"], 
                                          index=["Salgados", "Doces", "Bebidas", "Outros"].index(produto_selecionado['categoria']))
            novo_preco = st.number_input("Novo Preço", value=float(produto_selecionado['preco']), format="%.2f")
            
            if st.form_submit_button("Salvar Alterações", use_container_width=True):
                update_produto(produto_id_edit, novo_nome, nova_categoria, novo_preco)
                st.success("Produto atualizado!")
                st.rerun()

with tab3:
    st.markdown("##### Remover um Produto")
    produto_id_delete = st.selectbox("Selecione um produto para remover",
                                     options=df_produtos['id'],
                                     format_func=lambda x: f"{df_produtos.loc[df_produtos['id']==x, 'nome'].iloc[0]} (ID: {x})",
                                     key="delete_select")
    
    if produto_id_delete:
        produto_a_remover = df_produtos.loc[df_produtos['id'] == produto_id_delete, 'nome'].iloc[0]
        st.warning(f"Você tem certeza que deseja remover **{produto_a_remover}**? Esta ação é permanente.")
        
        if st.button("Sim, remover este produto", type="primary", use_container_width=True):
            delete_produto(produto_id_delete)
            st.success("Produto removido!")
            st.rerun()
