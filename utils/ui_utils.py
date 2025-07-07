# ==============================================================================
# ARQUIVO: utils/ui_utils.py
# DESCRIÇÃO: Funções de ajuda para criar elementos de UI padronizados.
# ==============================================================================
import streamlit as st

def card(title, content, background_color="#009c3b", border_color="#fecb00"):
    """Renderiza um componente de "card" customizado com CSS."""
    st.markdown(f"""
    <div style="
        border: 2px solid {border_color};
        border-radius: 10px;
        padding: 25px;
        background-color: {background_color};
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.3);
        margin-bottom: 25px;
        color: #FFFFFF;
    ">
        <h2 style="color: #FFFFFF; border-bottom: 2px solid {border_color}; padding-bottom: 10px; margin-top: 0;">{title}</h2>
        <div style="color: #FFFFFF; font-size: 16px;">{content}</div>
    </div>
    """, unsafe_allow_html=True)

def page_header(title, icon="⚽"):
    """Renderiza um cabeçalho de página padronizado."""
    st.markdown(f"<h1 style='text-align: center; color: #fecb00;'>{icon} {title}</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #fecb00;'>", unsafe_allow_html=True)