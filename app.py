import streamlit as st

from backend.session import proteger_painel
from ui.pages import renderizar_painel

st.set_page_config(page_title="BotWhats · Workspace", page_icon="💬", layout="wide", initial_sidebar_state="auto")
proteger_painel()
renderizar_painel()
