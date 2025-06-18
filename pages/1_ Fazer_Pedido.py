# pages/1_ Fazer_Pedido.py

import streamlit as st
import pandas as pd
from database import get_produtos, salvar_pedido
import json

# --- VERIFICAÇÃO DE LOGIN ---
if not st.session_state.get('logged_in'):
    st.error("Você precisa estar logado para acessar esta página.")
    st.page_link("Login.py", label="Ir para a página de Login")
    st.stop()

# --- INICIALIZAÇÃO E CONFIGURAÇÃO ---
st.set_page_config(page_title="Fazer Pedido", layout="wide")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- FUNÇÃO DE LOGOUT ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.switch_page("Login.py")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title(f"Olá, {st.session_state.username}!")
    st.write(f"Perfil: {st.session_state.role.capitalize()}")
    st.markdown("---")
    if st.session_state.role == 'admin':
        st.page_link("pages/2_Admin_-_Gerenciar_Cardapio.py", label="Gerenciar Cardápio")
        st.page_link("pages/3_Admin_-_Visualizar_Pedidos.py", label="Visualizar Pedidos")
        # ADICIONE A LINHA ABAIXO
        st.page_link("pages/4_Admin_-_Gerenciar_Usuarios.py", label="Gerenciar Usuários") 
        st.markdown("---")
    
    if st.button("Logout"):
        logout()

# --- TÍTULO PRINCIPAL ---
st.title("Faça seu Pedido")

# --- LAYOUT DA APLICAÇÃO (CARDÁPIO E CARRINHO) ---
col1, col2 = st.columns([0.6, 0.4])

with col1:
    st.header("Cardápio")
    produtos = get_produtos()
    if not produtos:
        st.warning("Nenhum produto cadastrado.")
    else:
        df_produtos = pd.DataFrame(produtos, columns=["id", "nome", "categoria", "preco"])
        # ... (O resto do código do cardápio é igual ao app.py anterior) ...
        for categoria in df_produtos["categoria"].unique():
            st.subheader(f"▎ {categoria}")
            produtos_categoria = df_produtos[df_produtos["categoria"] == categoria]
            
            for _, produto in produtos_categoria.iterrows():
                item_col1, item_col2, item_col3 = st.columns([2.5, 1, 1.2])
                with item_col1:
                    st.markdown(f"**{produto['nome']}**")
                with item_col2:
                    st.markdown(f"R$ {produto['preco']:.2f}")
                with item_col3:
                    if st.button("Adicionar", key=f"add_{produto['id']}"):
                        item_encontrado = next((item for item in st.session_state.carrinho if item['id'] == produto['id']), None)
                        if item_encontrado:
                            item_encontrado['quantidade'] += 1
                        else:
                            st.session_state.carrinho.append({"id": produto['id'], "nome": produto['nome'], "preco": produto['preco'], "quantidade": 1})
                        st.rerun()

with col2:
    st.header("🛒 Seu Pedido")
    if not st.session_state.carrinho:
        st.info("Seu carrinho está vazio.")
    else:
        # ... (O resto do código do carrinho é igual ao app.py anterior) ...
        carrinho_df = pd.DataFrame(st.session_state.carrinho)
        total_pedido = (carrinho_df['preco'] * carrinho_df['quantidade']).sum()

        for index, item in carrinho_df.iterrows():
            cart_col1, cart_col2, cart_col3 = st.columns([2.5, 1.5, 0.8])
            with cart_col1:
                st.markdown(f"**{item['nome']}** (x{item['quantidade']})")
            with cart_col2:
                st.markdown(f"R$ {(item['preco'] * item['quantidade']):.2f}")
            with cart_col3:
                if st.button("➖", key=f"rem_{item['id']}"):
                    item_no_carrinho = next((i for i in st.session_state.carrinho if i['id'] == item['id']), None)
                    if item_no_carrinho:
                        item_no_carrinho['quantidade'] -= 1
                        if item_no_carrinho['quantidade'] == 0:
                            st.session_state.carrinho.remove(item_no_carrinho)
                    st.rerun()
        
        st.markdown("---")
        st.markdown(f"<h3 style='text-align: right;'>Total: R$ {total_pedido:.2f}</h3>", unsafe_allow_html=True)

        if st.button("✅ Confirmar e Finalizar Pedido", use_container_width=True):
            itens_pedido = json.dumps([{"item": i["nome"], "qtd": i["quantidade"]} for i in st.session_state.carrinho])
            salvar_pedido(st.session_state.username, itens_pedido, total_pedido)
            st.session_state.carrinho = []
            st.success("Seu pedido foi enviado com sucesso!")
            st.balloons()
            st.rerun()
