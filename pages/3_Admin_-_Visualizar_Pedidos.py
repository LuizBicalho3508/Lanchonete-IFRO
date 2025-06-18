# pages/3_Admin_-_Visualizar_Pedidos.py

import streamlit as st
import pandas as pd
from database import get_all_pedidos
import json

# --- VERIFICAÇÃO DE LOGIN E PERMISSÃO ---
if not st.session_state.get('logged_in') or st.session_state.get('role') != 'admin':
    st.error("Acesso negado. Esta página é restrita aos administradores.")
    st.page_link("Login.py", label="Ir para a página de Login")
    st.stop()

st.set_page_config(page_title="Visualizar Pedidos", layout="wide")
st.title("📋 Painel de Pedidos Recebidos")

if st.button("🔄 Atualizar Lista de Pedidos"):
    st.rerun()

pedidos = get_all_pedidos()

if not pedidos:
    st.info("Nenhum pedido foi feito até o momento.")
else:
    for pedido in pedidos:
        with st.expander(f"Pedido #{pedido['id']} - {pedido['cliente_username']} - {pd.to_datetime(pedido['data_pedido']).strftime('%d/%m/%Y %H:%M')}"):
            st.write(f"**Cliente:** {pedido['cliente_username']}")
            st.write(f"**Total do Pedido:** R$ {pedido['total']:.2f}")
            st.write(f"**Status:** {pedido['status']}")
            
            st.markdown("**Itens do Pedido:**")
            try:
                # O ideal é usar json.loads, pois salvamos como uma string JSON
                itens = json.loads(pedido['itens'].replace("'", '"'))
                itens_df = pd.DataFrame(itens)
                st.dataframe(itens_df, use_container_width=True)
            except (json.JSONDecodeError, TypeError):
                # Fallback para caso o formato seja diferente
                st.text(pedido['itens'])

            st.markdown("---")