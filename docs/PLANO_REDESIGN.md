# Plano do redesign

1. Registrar suíte inicial e hashes; preservar app_backup.py e criar backup do estado pré-redesign.
2. Manter gateway/Supabase como autoridade de login; expor apenas identidade verificada ao painel.
3. Criar tokens CSS, componentes e páginas reutilizáveis, fonte Inter local e temas claro/escuro/automático.
4. Manter as quatro operações demonstrativas e adicionar Meu Perfil com prévias locais honestas.
5. Preferências por UID no servidor sobrevivem ao F5 durante o processo. Nome/foto remotos dependem de migração proposta, não aplicada; salvamento definitivo fica desabilitado.
6. Reestilizar login e confirmação de saída sem alterar Origin, CSRF, cookies ou seus contratos.
7. Ampliar testes de identidade/perfil/avatar/tema/navegação; executar suíte inteira e navegador nos seis tamanhos e dois temas.
8. Revisar diff, preservar backups, documentar estado da persistência e entregar evidências visuais e comando de início.

Estado inicial: 138 testes executados, 137 aprovados e 1 erro de limpeza do perfil descartável Chrome no Windows (WinError 32), registrado em redesign-baseline.txt. Correção do encerramento incluída antes da validação final.
