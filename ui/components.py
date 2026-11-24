"""Componentes de apresentação; todo texto externo é escapado."""

import base64
from html import escape
from pathlib import Path
from urllib.parse import quote

import streamlit as st

CAMINHOS = {
    "message": '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9H13a8.5 8.5 0 0 1 8 8v.5Z"/><path d="M8 11h8M8 15h5"/>',
    "qr": '<rect x="3" y="3" width="6" height="6" rx="1"/><rect x="15" y="3" width="6" height="6" rx="1"/><rect x="3" y="15" width="6" height="6" rx="1"/><path d="M15 15h3v3h3M15 21h3M21 12v3M12 3v3M3 12h3M12 15v6"/>',
    "shield": '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="m8 12 3 3 5-6"/>',
    "spark": '<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
    "check": '<path d="m5 12 4 4L19 6"/>',
    "send": '<path d="m22 2-7 20-4-9-9-4 20-7ZM22 2 11 13"/>',
    "sliders": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
}


def svg_icone(nome, tamanho=22):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" viewBox="0 0 24 24" fill="none" stroke="#098356" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{CAMINHOS.get(nome, CAMINHOS["message"])}</svg>'

def icone(nome, tamanho=22):
    src = base64.b64encode(svg_icone(nome, tamanho).encode()).decode("ascii")
    return f'<img class="bw-icon" src="data:image/svg+xml;base64,{src}" width="{tamanho}" height="{tamanho}" alt="" aria-hidden="true">'


def avatar(nome, imagem=None, tamanho=40):
    if imagem:
        src = "data:image/webp;base64," + base64.b64encode(imagem).decode("ascii")
        return f'<img class="bw-avatar" style="width:{tamanho}px;height:{tamanho}px" src="{src}" alt="Foto do perfil">'
    return f'<span class="bw-avatar" style="width:{tamanho}px;height:{tamanho}px" aria-label="Avatar padrão">{icone("user", max(20, tamanho // 2))}</span>'


def estilos(tema):
    css = (Path(__file__).parent / "theme.css").read_text(encoding="utf-8")
    modo = {"Claro": "light", "Escuro": "dark"}.get(tema, "auto")
    for i, nome in enumerate(("qr", "message", "send", "sliders", "user"), 1):
        svg = quote(svg_icone(nome), safe="")
        css += f'[data-testid=stSidebar] [role=radiogroup] label[data-testid=stRadioOption]:has(input[value="{i-1}"])::before{{content:"";width:21px;height:21px;flex-shrink:0;background:currentColor;mask:url("data:image/svg+xml,{svg}") center/contain no-repeat}}'
    css += ':root:has(.bw-theme-dark) .bw-empty-icon .bw-icon,:root:has(.bw-theme-dark) .bw-checklist .bw-icon,:root:has(.bw-theme-dark) .bw-step-icon .bw-icon{filter:brightness(1.8)}'
    # CSS selecionado em servidor; nenhum script ou armazenamento do navegador.
    st.html(f'<div class="bw-theme-{modo}" style="display:none" aria-hidden="true"></div><style>{css}</style>')


def marca():
    return f'<div class="bw-brand"><span class="bw-brand-icon">{icone("message",28)}</span><span>BotWhats<small>WORKSPACE</small></span></div>'


def usuario_html(nome, imagem=None):
    return f'<a class="bw-account" href="/?pagina=perfil" target="_self" aria-label="Abrir Meu Perfil">{avatar(nome, imagem)}<span>{escape(nome)}<small>Meu perfil</small></span></a>'


def etiqueta(texto):
    st.html(f'<span class="bw-badge">{escape(texto)}</span>')


def vazio(titulo, descricao, icon="message"):
    st.html(f'<div class="bw-empty"><span class="bw-empty-icon">{icone(icon,32)}</span><h3>{escape(titulo)}</h3><p>{escape(descricao)}</p></div>')


def passo(numero, titulo, texto, icon):
    st.html(f'<div class="bw-step"><span class="bw-step-icon">{icone(icon,24)}</span><small>ETAPA {numero}</small><h3>{escape(titulo)}</h3><p>{escape(texto)}</p></div>')
