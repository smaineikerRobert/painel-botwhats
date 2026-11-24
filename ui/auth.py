"""Formulários HTTP de autenticação: apresentação sem alterar o protocolo."""
from html import escape


def renderizar_auth(destino, csrf, campos, titulo, botao, erro, politica):
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <meta name="referrer" content="{politica}"><title>BotWhats · {titulo}</title>
    <style>
    :root{{color-scheme:light;--bg:#f5f8f6;--card:#fff;--text:#172925;--muted:#586e65;--border:#d9e9e2;--input:#fff}}
    *{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:16px Inter,system-ui,sans-serif;min-height:100svh;display:grid;place-items:center;padding:24px}}
    main{{display:grid;grid-template-columns:1fr 1fr;max-width:1060px;width:100%;min-height:620px;border:1px solid var(--border);border-radius:28px;overflow:hidden;box-shadow:0 20px 80px #062d2c09;background:var(--card)}}
    .story{{background:radial-gradient(circle at 100% 0,#15895a,#062d2c 65%);padding:48px;color:#edf9f2;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}}
    .brand{{display:flex;gap:12px;align-items:center;font-size:23px;font-weight:750;letter-spacing:-1px}}.logo{{background:#19b775;width:44px;height:44px;display:grid;place-items:center;border-radius:14px;color:#062d2c}}
    .story h2{{font-size:clamp(30px,4vw,44px);line-height:1.18;letter-spacing:-2px;margin:35px 0 20px}}.story p{{color:#bfdccf;line-height:1.8;max-width:350px}}.story small{{color:#bfdccf;line-height:1.7}}
    .content{{padding:64px 48px;align-self:center}}h1{{font-size:29px;letter-spacing:-1px;margin:16px 0 10px}}.lead{{color:var(--muted);line-height:1.65;margin-bottom:30px}}.badge{{font-size:11px;letter-spacing:2px;color:#08794d;font-weight:700}}
    label{{display:block;font-size:14px;font-weight:600;margin:20px 0}}input{{width:100%;border:1px solid var(--border);background:var(--input);color:var(--text);border-radius:12px;padding:14px;font:inherit;margin-top:9px;min-height:48px}}input:focus{{outline:3px solid #19b77555;border-color:#08794d}}
    button{{margin-top:10px;width:100%;background:#08794d;color:white;border:0;border-radius:12px;font:600 16px Inter,system-ui;padding:15px;cursor:pointer;min-height:48px}}button:hover{{background:#05613c}}button:focus-visible,a:focus-visible{{outline:3px solid #19b775;outline-offset:4px}}a{{color:var(--muted);font-size:14px;text-underline-offset:4px}}.back{{margin-top:24px}}.error{{color:#a11c32;font-size:14px;line-height:1.6}}.safe{{border-top:1px solid var(--border);margin-top:32px;padding-top:20px;font-size:13px;color:var(--muted);line-height:1.6}}
    @media(prefers-color-scheme:dark){{:root{{color-scheme:dark;--bg:#101b1a;--card:#1d302d;--text:#eaf6f0;--muted:#b1c9be;--border:#344943;--input:#162724}}.badge{{color:#5bdba3}}.error{{color:#ffb4bf}}}}
    @media(max-width:700px){{body{{padding:14px}}main{{grid-template-columns:1fr;min-height:0}}.story{{padding:24px}}.story h2{{font-size:28px;margin:24px 0 10px}}.story p{{margin-bottom:0}}.story small{{display:none}}.content{{padding:28px 24px}}}}
    </style></head><body><main><section class="story" aria-label="BotWhats">
    <div class="brand"><span class="logo"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M21 11a9 9 0 0 1-13 8L3 21l2-5A9 9 0 1 1 21 11Z"/><path d="M8 10h8M8 14h5"/></svg></span>BotWhats</div>
    <div><h2>Mais proximidade.<br>Melhores conversas.</h2><p>Um espaço para organizar seu atendimento e construir conexões com mais propósito.</p></div><small>Seu workspace de conversas.<br>Acesso individual, experiência conectada.</small></section>
    <section class="content"><span class="badge">SEU WORKSPACE</span><h1>{escape(titulo)}</h1><p class="lead">{"Entre para continuar no seu painel." if destino.endswith("login") else "Você está saindo da conta BotWhats. Seu WhatsApp não será desconectado."}</p>
    <p class="error" role="alert">{escape(erro)}</p><form method="post" action="{destino}" target="_self" accept-charset="UTF-8" enctype="application/x-www-form-urlencoded">
    <input type="hidden" name="csrf" value="{escape(csrf)}">{campos}<button>{escape(botao)}</button></form>
    <p class="back"><a href="/">Voltar ao painel</a></p><div class="safe">Acesso administrativo · Sua sessão é protegida.<br>Não compartilhe suas credenciais.</div></section></main></body></html>'''
