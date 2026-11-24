# Redesign do BotWhats e Meu Perfil

## Interface e componentes

O painel mantém Streamlit 1.67.0 e o gateway ASGI. `app.py` aplica a proteção e
delega a apresentação a `ui/pages.py`. Os componentes de marca, avatar, cartões,
estados vazios e ícones ficam em `ui/components.py`; os tokens CSS em
`ui/theme.css`. Login e confirmação de saída usam `ui/auth.py`, preservando os
formulários POST, Origin e CSRF existentes.

A direção visual usa sidebar verde-petróleo, superfícies claras, cartões
arredondados, hierarquia tipográfica Inter, detalhes verdes e estados vazios.
A fonte Inter é servida localmente de `assets/fonts`, com licença OFL incluída.
As telas HTTP de autenticação usam Inter quando disponível e fallback do sistema.
Os ícones lineares são SVGs locais próprios e Material Symbols nativos; nenhum
componente depende de CDN ou scripts de terceiros.

As quatro páginas mantêm a preparação de QR, regras, campanhas CSV/Excel e
opções de marca. Os comportamentos continuam demonstrativos: não há QR fictício,
envio real, métricas inventadas ou confirmação de persistência inexistente.
Meu Perfil é a quinta página, acessível também pelos avatares.

## Tema

Claro, Escuro e Automático são preferências pessoais. Automático reage a
`prefers-color-scheme`, inclusive sem um novo login. A preferência fica em RAM
no servidor, indexada pelo UID confirmado no Supabase Auth, e sobrevive ao F5 e
à navegação enquanto o processo/entrada existir. Não usa tokens em URLs,
localStorage ou cookies de JavaScript. A memória tem limite LRU de 256 usuários;
reinício ou descarte da entrada redefine a preferência. Não é uma gravação remota.

O tema pessoal não modifica as opções de marca da empresa. A sidebar pode ser
recolhida pelo controle nativo e fica compacta em telas pequenas. As colunas
empilham no tablet/celular. O CSS usa alguns `data-testid` da versão fixada do
Streamlit; upgrades exigem repetir a suíte e a matriz visual.

## Identidade, nome e avatar

O e-mail e UID vêm do usuário retornado por `get_user`, depois da autorização
Dono. Não são aceitos do formulário, query string ou metadata de papel. A API
interna de identidade retorna somente id/e-mail/nome, nunca tokens ou cliente.

**O salvamento definitivo está desabilitado.** Sem autorização para modificar o
Supabase remoto, `Salvar alterações` explica a pendência. `Aplicar prévia local`
permite avaliar nome e foto, com mensagem explícita de que não foram salvos no
Supabase. Essas prévias ficam em RAM, por UID, dentro do mesmo limite LRU; podem
ser compartilhadas entre logins da mesma conta, mas não entre usuários diferentes.
São perdidas no reinício/descarte. Não se chama tabela, Storage ou update de Auth.

O upload de avatar limita a 2 MB tanto no widget quanto no backend. PNG, JPEG e
WEBP precisam ter extensão coerente com o conteúdo decodificado. SVG, arquivos
inválidos, animação, lados acima de 4096 px e mais de 8 megapixels são rejeitados.
O Pillow valida, orienta por EXIF, recorta no centro para 256 × 256 e recodifica
em WEBP de até 128 KB sem EXIF. Só essa versão preparada chega ao avatar. Nome
tem 1–80 caracteres e texto externo é escapado ao renderizar HTML.

Cabeçalho, sidebar e perfil usam a mesma prévia. Substituir/remover a foto
restaura o avatar padrão quando aplicável. `Sair` e `Sair da conta BotWhats`
abrem o logout seguro POST do gateway; nenhuma ação desconecta o WhatsApp.

## Persistência Supabase: proposta pendente

A análise local consultou `docs/MODELO_DE_DADOS.md`, permissões e código do
Supabase. Esse modelo descreve `usuarios` como planejamento; o repositório não
trazia migração de perfil. O esquema remoto não foi consultado ou modificado;
é preciso reconciliá-lo antes de aplicar a proposta.

`database/003_perfil_usuario_PROPOSTA.sql` prepara uma tabela separada
`perfis_usuario`, com UID referenciando `auth.users`, nome, tema e caminho de
avatar. E-mail continua sendo dado de identidade do Auth. RLS permite somente
o próprio UID em SELECT/INSERT/UPDATE/DELETE. O bucket `botwhats-avatars` é
privado, limitado a WEBP normalizado de até 128 KB, com caminhos `UID/UUID.webp`
e políticas por proprietário. Não há `service_role` no painel.

O SQL não foi aplicado, nem executado contra banco local. A revisão é estática.
Antes de habilitar persistência real:

1. Revisar/aprovar a migração e reconciliar nomes/tabelas/políticas existentes.
2. Aplicar em ambiente aprovado e testar RLS com duas contas e acesso anônimo.
3. Implementar o repositório remoto com JWT do próprio usuário, sempre obtendo
   UID no backend depois da validação de Dono.
4. Fazer upload do arquivo preparado com novo UUID, atualizar o perfil e só então
   remover a foto anterior; limpar upload órfão se a atualização falhar.
5. Buscar bytes com autenticação ou URL assinada de curta duração, sem registrá-la.
   Testar upload, substituição, remoção, expiração e falhas antes de habilitar Save.

## Configuração e preservação

`backend/runtime_config.py` aplica efetivamente o mapa de opções à inicialização
direta ASGI. Nesta versão, variáveis STREAMLIT_* não sensíveis não são suficientes
fora da CLI. Mantém XSRF e CORS ativos, a origem configurada, API de agentes
desligada e modo headless/toolbar mínimo, sem ferramentas de desenvolvimento
sobre o painel. A integração permanece fixada na versão testada.

Cookies HttpOnly/SameSite/Secure, CSRF, Origin, Dono, prazos 30 min/8 h, refresh,
revogação e isolamento foram mantidos. O encerramento de tarefas WebSocket foi
ajustado para shield de cleanup sob cancelamento ASGI, sem autorizar tráfego
depois do fechamento. O teste de Chrome agora encerra o processo graciosamente
e aguarda a liberação dos arquivos temporários no Windows.

## Iniciar e homologar

Na raiz do repositório, branch `desenvolvimento-saas`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe iniciar.py --origin http://127.0.0.1:8501 --allow-http-local
```

Use exatamente esse host. A exceção HTTP é exclusiva de loopback. Para HTTPS,
use `--origin https://localhost:8501 --tls-cert caminho\cert.pem --tls-key caminho\key.pem`,
com certificado confiável, ou o proxy TLS já aprovado conforme o README.

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q app.py iniciar.py backend ui tests
.\.venv\Scripts\python.exe -m pip check
git diff --check
```

Homologar login, cinco páginas, três temas, F5, avatar PNG/JPG/WEBP válido/inválido,
prévia, substituição/remoção e Sair. Compare contas em contextos separados; o
segundo não deve herdar cookie ou preferências do primeiro. Nunca exporte HAR,
cookies, corpo do login ou tokens. Não altere permissões remotas para simular
negativas; use a suíte local.

O QA automatizado visual usa identidades simuladas e testa 320, 360, 390, 768,
1280 e 1440 px em cada uma das cinco páginas nos dois temas. Contrastes críticos
de tokens são verificados numericamente; isso não substitui auditoria completa
WCAG com tecnologias assistivas. Fotos/dados das capturas são apenas fixtures.
