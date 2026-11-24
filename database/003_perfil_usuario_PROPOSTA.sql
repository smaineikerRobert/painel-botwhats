-- PROPOSTA LOCAL. NÃO APLICADA. Revisar o esquema remoto e aprovar antes de executar.
-- Nenhuma chave service_role é necessária no painel. Usar JWT do próprio usuário.
begin;

create table public.perfis_usuario (
    user_id uuid primary key references auth.users(id) on delete cascade,
    nome_preferido text not null check (char_length(btrim(nome_preferido)) between 1 and 80),
    tema text not null default 'automatico' check (tema in ('automatico','claro','escuro')),
    avatar_path text,
    updated_at timestamptz not null default now(),
    constraint avatar_do_proprio_usuario check (
      avatar_path is null or (avatar_path like user_id::text || '/%'
      and avatar_path ~ '^[a-f0-9-]{36}/[a-f0-9-]{36}\.webp$'))
);
alter table public.perfis_usuario enable row level security;
revoke all on public.perfis_usuario from anon;
grant select, insert, update, delete on public.perfis_usuario to authenticated;
create policy perfil_select on public.perfis_usuario for select to authenticated using ((select auth.uid()) = user_id);
create policy perfil_insert on public.perfis_usuario for insert to authenticated with check ((select auth.uid()) = user_id);
create policy perfil_update on public.perfis_usuario for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy perfil_delete on public.perfis_usuario for delete to authenticated using ((select auth.uid()) = user_id);

-- Bucket privado, apenas imagem já normalizada pelo backend; não guardar URL pública.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('botwhats-avatars', 'botwhats-avatars', false, 131072, array['image/webp']);
create policy avatar_select on storage.objects for select to authenticated using (
  bucket_id = 'botwhats-avatars' and (storage.foldername(name))[1] = (select auth.uid())::text);
create policy avatar_insert on storage.objects for insert to authenticated with check (
  bucket_id = 'botwhats-avatars' and (storage.foldername(name))[1] = (select auth.uid())::text
  and name ~ '^[a-f0-9-]{36}/[a-f0-9-]{36}\.webp$');
create policy avatar_update on storage.objects for update to authenticated using (
  bucket_id = 'botwhats-avatars' and (storage.foldername(name))[1] = (select auth.uid())::text)
  with check (bucket_id = 'botwhats-avatars' and (storage.foldername(name))[1] = (select auth.uid())::text
  and name ~ '^[a-f0-9-]{36}/[a-f0-9-]{36}\.webp$');
create policy avatar_delete on storage.objects for delete to authenticated using (
  bucket_id = 'botwhats-avatars' and (storage.foldername(name))[1] = (select auth.uid())::text);
commit;

-- Integração futura: validar Dono; obter UID do Auth; gerar nome UUID.webp;
-- fazer upload privado e update do perfil com JWT desse usuário; remover órfãos
-- e imagem substituída. Carregar bytes autenticados no servidor ou URL assinada
-- curta, sem registrá-la. Nunca confiar em UID/caminho recebido do navegador.
-- RLS é defesa adicional; MIME não substitui validação e recodificação pelo Pillow.
