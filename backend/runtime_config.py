"""Opções efetivas do st.App com Uvicorn (sem depender do parser da CLI)."""

def configurar_streamlit(origem):
    from urllib.parse import urlsplit
    from streamlit import config
    # Nesta versão, variáveis STREAMLIT_* não sensíveis são processadas pela
    # CLI; iniciar.py usa ASGI diretamente. Aplicar o mesmo mapa de flags antes
    # de construir st.App mantém CORS/XSRF e remove ferramentas de desenvolvimento.
    config.get_config_options(force_reparse=True, options_from_flags={
        "server.corsAllowedOrigins": [origem],
        "browser.serverAddress": urlsplit(origem).hostname,
        "browser.gatherUsageStats": False,
        "server.enableAgentApi": False,
        "server.enableXsrfProtection": True,
        "server.headless": True,
        "client.toolbarMode": "minimal",
    })
