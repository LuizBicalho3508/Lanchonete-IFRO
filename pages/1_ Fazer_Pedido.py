# pages/1_ Fazer_Pedido.py (Versão Melhorada)

import streamlit as st
import pandas as pd
from database import get_produtos, salvar_pedido
import json

# --- VERIFICAÇÃO DE LOGIN (essencial para segurança da página) ---
if not st.session_state.get('logged_in'):
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")
    st.page_link("Login.py", label="Ir para a página de Login", icon="🏠")
    st.stop()

# --- INICIALIZAÇÃO DO CARRINHO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- FUNÇÃO DE LOGOUT ---
def logout():
    # Limpa todas as chaves da sessão relacionadas ao login
    keys_to_delete = ['logged_in', 'username', 'role', 'carrinho']
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.switch_page("Login.py")

# --- BARRA LATERAL DE NAVEGAÇÃO (SIDEBAR) ---
with st.sidebar:
    st.title(f"Olá, {st.session_state.username}!")
    st.write(f"**Perfil:** {st.session_state.role.capitalize()}")
    st.divider()

    # Navegação principal
    st.page_link("pages/1_ Fazer_Pedido.py", label="Fazer Pedido", icon="🍔")
    
    # Navegação do Administrador
    if st.session_state.role == 'admin':
        st.subheader("Painel Admin")
        st.page_link("pages/2_Admin_-_Gerenciar_Cardapio.py", label="Gerenciar Cardápio", icon="⚙️")
        st.page_link("pages/3_Admin_-_Visualizar_Pedidos.py", label="Visualizar Pedidos", icon="📋")
        st.page_link("pages/4_Admin_-_Gerenciar_Usuarios.py", label="Gerenciar Usuários", icon="👥")
    
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# --- CONTEÚDO PRINCIPAL DA PÁGINA ---
st.title("Lanchonete IFRO Zona Norte")
st.subheader("Escolha os itens para o seu pedido")

# --- LAYOUT DA APLICAÇÃO (CARDÁPIO E CARRINHO) ---
col1, col2 = st.columns([0.6, 0.4])

with col1:
    st.header("🍔 Cardápio")
    produtos = get_produtos()
    if not produtos:
        st.warning("Nenhum produto cadastrado no momento.")
    else:
        df_produtos = pd.DataFrame(produtos, columns=["id", "nome", "categoria", "preco"])
        categorias = df_produtos["categoria"].unique()
        
        for categoria in categorias:
            st.subheader(categoria)
            produtos_categoria = df_produtos[df_produtos["categoria"] == categoria]
            
            for _, produto in produtos_categoria.iterrows():
                # Usando container para criar um "card" para cada produto
                with st.container(border=True):
                    item_col1, item_col2, item_col3 = st.columns([4, 2, 2])
                    with item_col1:
                        st.markdown(f"**{produto['nome']}**")
                    with item_col2:
                        st.markdown(f"R$ {produto['preco']:.2f}")
                    with item_col3:
                        if st.button("➕ Adicionar", key=f"add_{produto['id']}", use_container_width=True):
                            item_encontrado = next((item for item in st.session_state.carrinho if item['id'] == produto['id']), None)
                            if item_encontrado:
                                item_encontrado['quantidade'] += 1
                            else:
                                st.session_state.carrinho.append({"id": produto['id'], "nome": produto['nome'], "preco": produto['preco'], "quantidade": 1})
                            st.rerun()

with col2:
    st.header("🛒 Seu Pedido")
    if not st.session_state.carrinho:
        st.info("Seu carrinho está vazio. Adicione itens do cardápio ao lado.")
    else:
        # Exibindo itens do carrinho em "cards"
        for index, item in enumerate(st.session_state.carrinho):
            with st.container(border=True):
                cart_col1, cart_col2, cart_col3 = st.columns([4, 2, 2])
                with cart_col1:
                    st.markdown(f"**{item['nome']}**")
                    st.markdown(f"Qtd: {item['quantidade']}")
                with cart_col2:
                    st.markdown(f"R$ {(item['preco'] * item['quantidade']):.2f}")
                with cart_col3:
                    if st.button("➖ Remover", key=f"rem_{item['id']}", use_container_width=True):
                        # Lógica para remover item ou diminuir quantidade
                        item_no_carrinho = st.session_state.carrinho[index]
                        item_no_carrinho['quantidade'] -= 1
                        if item_no_carrinho['quantidade'] == 0:
                            st.session_state.carrinho.pop(index)
                        st.rerun()
        
        st.divider()
        
        # Cálculo e exibição do total
        carrinho_df = pd.DataFrame(st.session_state.carrinho)
        total_pedido = (carrinho_df['preco'] * carrinho_df['quantidade']).sum()
        st.markdown(f"<h3 style='text-align: right;'>Total: R$ {total_pedido:.2f}</h3>", unsafe_allow_html=True)
        
        st.divider()

        # Botão para finalizar o pedido
        if st.button("✅ Confirmar e Finalizar Pedido", use_container_width=True, type="primary"):
            itens_pedido = json.dumps([{"item": i["nome"], "qtd": i["quantidade"]} for i in st.session_state.carrinho])
            salvar_pedido(st.session_state.username, itens_pedido, total_pedido)
            
            st.success("Seu pedido foi enviado com sucesso!")
            st.balloons()
            # Limpa o carrinho após o sucesso
            del st.session_state.carrinho
            st.rerun()
