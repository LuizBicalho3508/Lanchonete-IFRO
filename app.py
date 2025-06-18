# app.py

import streamlit as st
import pandas as pd
from database import criar_tabelas, get_produtos, salvar_pedido
import json

# Função para carregar o CSS customizado
def carregar_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    # --- CONFIGURAÇÕES DA PÁGINA E ESTADO ---
    st.set_page_config(page_title="Lanchonete IFRO", page_icon="🍔", layout="wide")
    carregar_css("style.css")
    
    # Inicializa o banco de dados e as tabelas
    criar_tabelas()

    # Inicializa o 'carrinho' na sessão do usuário se não existir
    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []

    # --- CABEÇALHO ---
    st.title("🍔 Lanchonete do IFRO - Campus Zona Norte")
    st.write("Bem-vindo! Monte seu pedido abaixo.")

    # --- LAYOUT DA APLICAÇÃO (CARDÁPIO E CARRINHO) ---
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        # --- SEÇÃO DO CARDÁPIO ---
        st.header("Cardápio")
        
        produtos = get_produtos()
        if not produtos:
            st.warning("A lanchonete está sem produtos cadastrados no momento.")
            return

        df_produtos = pd.DataFrame(produtos, columns=["id", "nome", "categoria", "preco"])
        categorias = df_produtos["categoria"].unique()

        for categoria in categorias:
            st.subheader(f"▎ {categoria}")
            produtos_categoria = df_produtos[df_produtos["categoria"] == categoria]
            
            for _, produto in produtos_categoria.iterrows():
                # Layout para cada item do cardápio
                item_col1, item_col2, item_col3 = st.columns([2.5, 1, 1.2])
                with item_col1:
                    st.markdown(f"**{produto['nome']}**")
                with item_col2:
                    st.markdown(f"R$ {produto['preco']:.2f}")
                with item_col3:
                    if st.button("Adicionar", key=f"add_{produto['id']}"):
                        # Adiciona o item ao carrinho
                        item_encontrado = next((item for item in st.session_state.carrinho if item['id'] == produto['id']), None)
                        if item_encontrado:
                            item_encontrado['quantidade'] += 1
                        else:
                            st.session_state.carrinho.append({
                                "id": produto['id'],
                                "nome": produto['nome'],
                                "preco": produto['preco'],
                                "quantidade": 1
                            })
                        st.rerun() # Atualiza a página para refletir a mudança no carrinho

    with col2:
        # --- SEÇÃO DO CARRINHO ---
        st.header("🛒 Seu Pedido")

        if not st.session_state.carrinho:
            st.info("Seu carrinho está vazio. Adicione itens do cardápio.")
        else:
            carrinho_df = pd.DataFrame(st.session_state.carrinho)
            total_pedido = (carrinho_df['preco'] * carrinho_df['quantidade']).sum()

            # Exibe os itens do carrinho
            for index, item in carrinho_df.iterrows():
                cart_col1, cart_col2, cart_col3 = st.columns([2.5, 1.5, 0.8])
                with cart_col1:
                    st.markdown(f"**{item['nome']}** (x{item['quantidade']})")
                with cart_col2:
                    st.markdown(f"R$ {(item['preco'] * item['quantidade']):.2f}")
                with cart_col3:
                    if st.button("➖", key=f"rem_{item['id']}"):
                        # Reduz a quantidade ou remove o item
                        item_no_carrinho = next((i for i in st.session_state.carrinho if i['id'] == item['id']), None)
                        if item_no_carrinho:
                            item_no_carrinho['quantidade'] -= 1
                            if item_no_carrinho['quantidade'] == 0:
                                st.session_state.carrinho.remove(item_no_carrinho)
                        st.rerun()

            st.markdown("---")
            # Exibe o total formatado
            st.markdown(f"<h3 style='text-align: right;'>Total: R$ {total_pedido:.2f}</h3>", unsafe_allow_html=True)

            # --- FORMULÁRIO PARA FINALIZAR PEDIDO ---
            with st.form("formulario_pedido", clear_on_submit=True):
                st.subheader("Informações para Retirada")
                nome_cliente = st.text_input("Seu nome completo:", placeholder="Digite seu nome aqui...")
                id_cliente = st.text_input("Sua Matrícula ou SIAPE (Opcional):", placeholder="Ex: 2021...")
                
                submitted = st.form_submit_button("✅ Finalizar Pedido")
                
                if submitted:
                    if not nome_cliente:
                        st.error("Por favor, preencha seu nome para finalizar o pedido.")
                    else:
                        # Prepara os dados e salva no banco
                        itens_pedido = json.dumps([{"item": i["nome"], "qtd": i["quantidade"]} for i in st.session_state.carrinho])
                        salvar_pedido(nome_cliente, id_cliente, itens_pedido, total_pedido)
                        
                        # Limpa o carrinho e exibe mensagem de sucesso
                        st.session_state.carrinho = []
                        st.success(f"Obrigado, {nome_cliente.split()[0]}! Seu pedido foi enviado com sucesso.")
                        st.balloons()

if __name__ == '__main__':
    main()