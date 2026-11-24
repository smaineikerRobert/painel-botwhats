"""Páginas do painel, com widgets nativos e identidade verificada no servidor."""
from html import escape
import streamlit as st
from backend import session_runtime
from backend.profile import TEMAS, preferencias, preparar_avatar
from ui.components import avatar, estilos, etiqueta, icone, marca, passo, usuario_html, vazio

PAGINAS = ["Início / QR Code", "Regras de Conversa", "Disparo em Massa", "Personalização", "Meu Perfil"]
SLUGS = ["inicio", "regras", "campanhas", "marca", "perfil"]
TITULOS = ["Conexão do WhatsApp", "Regras de Resposta", "Envio de Mensagens em Massa", "Configurações Visuais (White Label)", "Meu Perfil"]
SUBTITULOS = ["Seu ponto de partida para conversas mais próximas.", "Dê o seu tom às conversas com os clientes.", "Prepare sua próxima campanha, em um só lugar.", "Uma experiência com a identidade da sua empresa.", "Sua identidade e suas preferências no BotWhats."]

def identidade_atual():
    sid = st.context.headers.get("x-botwhats-session", "")
    if session_runtime.sessoes is None:
        raise PermissionError("Sessão indisponível.")
    return session_runtime.sessoes.identidade(sid)

def navegar():
    st.query_params["pagina"] = SLUGS[PAGINAS.index(st.session_state["pagina_menu"])]

def trocar_tema(uid):
    try:
        if identidade_atual()["id"] == uid:
            preferencias.tema(uid, st.session_state["tema_pessoal"])
    except PermissionError:
        st.session_state.clear()

def inicio():
    esquerda, direita = st.columns([1.8, 1], gap="large")
    with esquerda, st.container(key="card_connection"):
        st.html('<div class="bw-hero"><span class="bw-badge">SEU WHATSAPP, MAIS PRÓXIMO</span><h2>Boas conversas começam<br>com uma boa conexão.</h2><p>Organize o atendimento e prepare sua operação, sem perder o toque humano.</p></div>')
        st.subheader("Sua conexão")
        etiqueta("Integração pendente")
        vazio("O QR Code aparecerá aqui", "A conexão será disponibilizada após a integração da Evolution API. Nenhuma instância foi conectada.", "qr")
        if st.button("Gerar QR Code para Conectar", type="primary", icon=":material/qr_code_2:", width="stretch"):
            st.info("Demonstração: a Evolution API ainda não está conectada. Nenhum QR Code foi gerado.")
        st.caption("Sair do BotWhats encerra seu login no painel. Não desconecta uma instância WhatsApp.")
    with direita, st.container(key="card_setup"):
        st.subheader("Seu próximo passo")
        st.write("Prepare sua operação enquanto a conexão está em desenvolvimento.")
        st.html('<ul class="bw-checklist">' + ''.join(f'<li>{icone(icon)}<span><strong>{escape(t)}</strong><br>{escape(d)}</span></li>' for icon, t, d in (
            ("sliders", "Defina suas respostas", "Explore palavras-chave e mensagens."),
            ("spark", "Dê a sua identidade", "Organize nome, cores e marca."),
            ("shield", "Mantenha o acesso seguro", "Sua conta e sua sessão são individuais."),
        )) + '</ul><div class="bw-divider"></div>')
        st.caption("Ambiente de desenvolvimento")
        st.info("Os recursos de WhatsApp ainda são demonstrativos. Não há envios reais neste painel.")
    st.subheader("Tudo no seu ritmo")
    colunas = st.columns(3, gap="medium")
    for coluna, dados in zip(colunas, ((1, "Conecte seu canal", "O QR Code será o ponto de entrada para sua instância WhatsApp.", "qr"), (2, "Prepare as conversas", "Defina as respostas que fazem sentido para o seu negócio.", "message"), (3, "Planeje suas campanhas", "Organize contatos e mensagens antes de começar.", "send"))):
        with coluna:
            passo(*dados)

def regras():
    esquerda, direita = st.columns([1.7, 1], gap="large")
    with esquerda, st.container(key="card_rules"):
        st.subheader("Uma resposta para cada intenção")
        st.write("Prepare uma palavra-chave e a mensagem que o cliente receberia antes de uma resposta da IA.")
        with st.form("nova_regra"):
            palavra = st.text_input("Se o cliente digitar:", placeholder="Ex.: horário de atendimento")
            resposta = st.text_area("O bot deve responder:", placeholder="Escreva uma resposta acolhedora e objetiva.", height=150)
            salvar = st.form_submit_button("Salvar Regra", type="primary", icon=":material/add:")
        if salvar:
            if not palavra.strip() or not resposta.strip():
                st.warning("Preencha a palavra-chave e a resposta para simular a regra.")
            else:
                st.info(f"Simulação: '{palavra}' → '{resposta}'. Nenhuma regra foi gravada no banco.")
    with direita, st.container(key="card_setup"):
        etiqueta("Demonstração")
        vazio("Suas regras, aqui", "A lista ficará disponível quando o armazenamento de regras for integrado. Não há regras persistidas para exibir.", "message")

def campanhas():
    esquerda, direita = st.columns([1.7, 1], gap="large")
    with esquerda, st.container(key="card_campaign"):
        st.subheader("Prepare uma nova campanha")
        st.write("Comece com sua lista de contatos e uma mensagem que mereça ser recebida.")
        arquivo = st.file_uploader("Subir arquivo (CSV ou Excel)", type=["csv", "xlsx"], help="Somente preparação demonstrativa. Nenhum contato será importado.")
        mensagem = st.text_area("Digite a mensagem da campanha:", placeholder="Olá! Temos uma novidade para compartilhar…", height=170)
        if st.button("Iniciar Disparo", type="primary", icon=":material/send:"):
            if arquivo is None or not mensagem.strip():
                st.warning("Selecione uma lista e escreva uma mensagem para preparar a demonstração.")
            else:
                st.info("Demonstração: o disparo será ativado após a integração com o servidor. Nenhuma mensagem foi enviada.")
    with direita, st.container(key="card_setup"):
        st.subheader("Antes de enviar")
        st.write("Use contatos com consentimento e revise a mensagem antes de iniciar uma campanha.")
        vazio("Nenhum envio iniciado", "O acompanhamento ficará disponível junto com a integração de disparos.", "send")

def personalizacao():
    esquerda, direita = st.columns([1.7, 1], gap="large")
    with esquerda, st.container(key="card_brand"):
        st.subheader("A marca da sua empresa")
        st.write("Essas opções representam a identidade da empresa. Seu tema pessoal é independente.")
        st.text_input("Nome da sua Empresa", "Minha Empresa Bot", key="marca_nome")
        st.color_picker("Cor principal do painel", "#00c300", key="marca_cor")
        st.file_uploader("Upload da Logomarca (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if st.button("Salvar Alterações Visuais", type="primary", icon=":material/palette:"):
            st.info("Demonstração: as opções estão preenchidas nesta página, mas a marca não foi persistida nem aplicada à empresa.")
    with direita, st.container(key="card_preferences"):
        etiqueta("Preferência pessoal")
        st.subheader("Um espaço confortável para você")
        st.write("Use o seletor de tema no topo. Claro, escuro ou automático: isso muda apenas sua experiência, não a marca da empresa.")
        st.caption("A preferência fica na memória deste servidor por usuário e sobrevive ao F5. Reiniciar o servidor a redefine.")
        st.link_button("Abrir Meu Perfil", "/?pagina=perfil", icon=":material/person:")

def perfil(identidade, prefs):
    esquerda, direita = st.columns([1.5, 1], gap="large")
    with esquerda, st.container(key="card_profile"):
        st.subheader("Informações pessoais")
        st.write("Como você prefere ser chamado?")
        st.text_input("E-mail da conta autenticada", value=identidade["email"] or "E-mail indisponível", disabled=True)
        nome = st.text_input("Nome de preferência", value=prefs.nome or identidade["nome"], max_chars=80, placeholder="Seu nome", key="perfil_nome")
        st.info("Prévia local: nome e foto ainda não são salvos no Supabase. As alterações temporárias valem neste servidor, para esta conta.")
        st.button("Salvar alterações", disabled=True, help="A persistência definitiva aguarda revisão e aplicação da migração Supabase.", type="primary")
    novo_avatar = prefs.avatar
    with direita, st.container(key="card_avatar"):
        st.subheader("Sua foto")
        st.html('<div style="display:flex;justify-content:center;padding:.5rem 0 1rem">' + avatar(nome, prefs.avatar, 88) + '</div>')
        foto = st.file_uploader("Escolher foto de perfil", type=["png", "jpg", "jpeg", "webp"], max_upload_size=2, help="Até 2 MB. Foto estática, até 4096 px por lado e 8 megapixels. Recorte central 256 × 256.", key="perfil_foto")
        remover = st.checkbox("Remover foto na prévia", key="perfil_remover_foto")
        invalido = False
        if remover:
            novo_avatar = None
        elif foto is not None:
            try:
                novo_avatar = preparar_avatar(foto.getvalue(), foto.name)
                st.image(novo_avatar, width=128, caption="Prévia do recorte · ainda não aplicada")
            except ValueError as erro:
                invalido = True
                st.error(str(erro))
        if st.button("Aplicar prévia local", disabled=invalido, icon=":material/visibility:", width="stretch"):
            try:
                atual = identidade_atual()
                if atual["id"] != identidade["id"]:
                    raise PermissionError()
                preferencias.previa(atual["id"], nome, novo_avatar)
                st.session_state["perfil_feedback"] = True
                st.rerun()
            except ValueError as erro:
                st.error(str(erro))
            except PermissionError:
                st.error("Sua sessão precisa ser confirmada novamente.")
    if st.session_state.get("perfil_feedback", False):
        st.info("Prévia atualizada neste servidor. Nome e foto não foram salvos no Supabase; serão perdidos ao reiniciar.")
    with st.container(key="card_security"):
        st.subheader("Acesso e segurança")
        st.write("Seu e-mail identifica a conta. O nome e a foto não alteram sua permissão de acesso.")
        st.caption("Sair encerra apenas o login BotWhats deste navegador. Não desconecta o WhatsApp.")
        st.link_button("Sair da conta BotWhats", "/auth/logout", icon=":material/logout:")

def renderizar_painel():
    try:
        identidade = identidade_atual()
    except PermissionError:
        st.error("Não foi possível confirmar sua identidade. Entre novamente.")
        st.link_button("Entrar", "/auth/login")
        st.stop()
    prefs = preferencias.obter(identidade["id"])
    nome = prefs.nome or identidade["nome"] or "Sua conta"
    if "pagina_menu" not in st.session_state:
        slug = st.query_params.get("pagina", "inicio")
        st.session_state["pagina_menu"] = PAGINAS[SLUGS.index(slug)] if slug in SLUGS else PAGINAS[0]
    with st.sidebar:
        st.html(marca())
        st.caption("SEU PAINEL")
        menu = st.radio("Navegação", PAGINAS, key="pagina_menu", on_change=navegar, label_visibility="collapsed")
        with st.container(key="sidebar_profile"):
            st.html(usuario_html(nome, prefs.avatar))
            st.caption("Acesso administrativo · Dono")
            st.link_button("Sair", "/auth/logout", icon=":material/logout:", width="stretch")
    indice = PAGINAS.index(menu)
    if menu != "Meu Perfil":
        st.session_state.pop("perfil_feedback", None)
    titulo, tema, conta = st.columns([3.3, 1.2, 1.3], vertical_alignment="center", gap="medium")
    with titulo:
        st.html('<div class="bw-eyebrow">WORKSPACE / ' + escape(menu.upper()) + '</div>')
        st.title(TITULOS[indice])
    with tema:
        if "tema_pessoal" not in st.session_state:
            st.session_state["tema_pessoal"] = prefs.tema
        st.selectbox("Tema", TEMAS, key="tema_pessoal", on_change=trocar_tema, args=(identidade["id"],))
    with conta:
        st.html(usuario_html(nome, prefs.avatar))
    estilos(preferencias.obter(identidade["id"]).tema)
    st.write(SUBTITULOS[indice])
    (inicio, regras, campanhas, personalizacao, lambda: perfil(identidade, prefs))[indice]()
    st.html('<div class="bw-footer">BotWhats Workspace · Conversas com mais propósito.</div>')
