-- Monarch foundation: private workspaces, role-based membership, modular work data,
-- Vault metadata and private object storage policies. Apply only to a NEW Monarch
-- Supabase project after reviewing plan limits and the production setup guide.

create extension if not exists pgcrypto with schema extensions;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null default '',
  created_at timestamptz not null default now()
);

create table if not exists public.workspaces (
  id uuid primary key default gen_random_uuid(),
  name text not null check (char_length(name) between 1 and 100),
  created_by uuid not null references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists public.workspace_members (
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('owner','admin','editor','contributor','viewer')),
  joined_at timestamptz not null default now(),
  primary key (workspace_id,user_id)
);
create index if not exists workspace_members_user_idx on public.workspace_members(user_id,workspace_id);

create or replace function public.is_workspace_member(target_workspace uuid)
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.workspace_members m where m.workspace_id=target_workspace and m.user_id=(select auth.uid()))
$$;
create or replace function public.has_workspace_role(target_workspace uuid, allowed_roles text[])
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.workspace_members m where m.workspace_id=target_workspace and m.user_id=(select auth.uid()) and m.role=any(allowed_roles))
$$;
revoke all on function public.is_workspace_member(uuid) from public;
revoke all on function public.has_workspace_role(uuid,text[]) from public;
grant execute on function public.is_workspace_member(uuid) to authenticated;
grant execute on function public.has_workspace_role(uuid,text[]) to authenticated;

alter table public.profiles enable row level security;
create policy "Users can view workspace colleagues" on public.profiles for select to authenticated using(
  id=(select auth.uid()) or exists(select 1 from public.workspace_members mine join public.workspace_members colleague on colleague.workspace_id=mine.workspace_id where mine.user_id=(select auth.uid()) and colleague.user_id=id)
);
create policy "Users can update their profile" on public.profiles for update to authenticated using(id=(select auth.uid())) with check(id=(select auth.uid()));

create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  name text not null, description text not null default '', kind text not null default 'Personal project',
  status text not null default 'Planning', color text not null default '#799a62', progress smallint not null default 0 check(progress between 0 and 100),
  created_by uuid not null references auth.users(id), created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists projects_workspace_idx on public.projects(workspace_id,updated_at desc);

create table if not exists public.tasks (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  project_id uuid references public.projects(id) on delete set null, title text not null, area text not null default 'Personal',
  status text not null default 'open' check(status in ('open','in_progress','done','archived')),
  priority text not null default 'medium' check(priority in ('low','medium','high')), due_at timestamptz,
  assigned_to uuid references auth.users(id) on delete set null, created_by uuid not null references auth.users(id),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists tasks_workspace_status_idx on public.tasks(workspace_id,status,due_at);

create table if not exists public.channels (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  platform text not null check(platform in ('youtube','instagram','tiktok','facebook','other')),
  name text not null, handle text not null default '', focus text not null default '', color text not null default '#799a62', archived_at timestamptz,
  created_by uuid not null references auth.users(id), created_at timestamptz not null default now()
);
create index if not exists channels_workspace_idx on public.channels(workspace_id,platform);

create table if not exists public.content_items (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  channel_id uuid references public.channels(id) on delete set null, project_id uuid references public.projects(id) on delete set null,
  title text not null, format text not null default 'Long-form', stage text not null default 'Idea',
  idea text not null default '', research jsonb not null default '[]'::jsonb, hook text not null default '', script text not null default '',
  thumbnail_notes text not null default '', checklist jsonb not null default '[]'::jsonb, planned_for timestamptz,
  created_by uuid not null references auth.users(id), created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index if not exists content_items_workspace_stage_idx on public.content_items(workspace_id,stage,planned_for);

create table if not exists public.saved_conversations (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  project_id uuid references public.projects(id) on delete set null, title text not null, source text not null default '', source_url text not null default '',
  summary text not null default '', tags text[] not null default '{}', saved_by uuid not null references auth.users(id), created_at timestamptz not null default now()
);

create table if not exists public.knowledge_notes (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  project_id uuid references public.projects(id) on delete set null, title text not null, body text not null default '', tags text[] not null default '{}',
  created_by uuid not null references auth.users(id), created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);

-- A lightweight Discord-like internal discussion layer. Keep each channel scoped to a workspace.
create table if not exists public.vault_spaces (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  name text not null, description text not null default '', created_by uuid not null references auth.users(id), created_at timestamptz not null default now()
);
create table if not exists public.vault_channels (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  space_id uuid not null references public.vault_spaces(id) on delete cascade, name text not null, kind text not null default 'discussion' check(kind in ('discussion','files','docs')),
  created_at timestamptz not null default now()
);
create table if not exists public.vault_posts (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  channel_id uuid not null references public.vault_channels(id) on delete cascade, author_id uuid not null references auth.users(id),
  body text not null default '', pinned boolean not null default false, created_at timestamptz not null default now(), edited_at timestamptz
);
create index if not exists vault_posts_channel_idx on public.vault_posts(channel_id,created_at desc);

-- Object bytes live in the private Storage bucket. This table stores searchable metadata only.
create table if not exists public.vault_files (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  channel_id uuid references public.vault_channels(id) on delete set null, project_id uuid references public.projects(id) on delete set null,
  object_path text not null unique, original_name text not null, mime_type text not null default 'application/octet-stream',
  size_bytes bigint not null check(size_bytes >= 0), folder text not null default 'Everything', uploaded_by uuid not null references auth.users(id),
  created_at timestamptz not null default now(), deleted_at timestamptz
);
create index if not exists vault_files_workspace_idx on public.vault_files(workspace_id,created_at desc) where deleted_at is null;

create table if not exists public.workspace_invitations (
  id uuid primary key default gen_random_uuid(), workspace_id uuid not null references public.workspaces(id) on delete cascade,
  email text not null, role text not null check(role in ('admin','editor','contributor','viewer')),
  invited_by uuid not null references auth.users(id), status text not null default 'pending' check(status in ('pending','accepted','revoked','expired')),
  expires_at timestamptz not null default (now()+interval '7 days'), created_at timestamptz not null default now(),
  unique(workspace_id,email)
);

-- Seed every new account with a private workspace. Team members are added later through trusted invitations.
create or replace function public.bootstrap_monarch_user()
returns trigger language plpgsql security definer set search_path = '' as $$
declare new_workspace_id uuid; display text;
begin
  display := coalesce(nullif(new.raw_user_meta_data->>'full_name',''), split_part(coalesce(new.email,'Monarch user'),'@',1));
  insert into public.profiles(id,display_name) values(new.id,display) on conflict(id) do nothing;
  insert into public.workspaces(name,created_by) values('My workspace',new.id) returning id into new_workspace_id;
  insert into public.workspace_members(workspace_id,user_id,role) values(new_workspace_id,new.id,'owner');
  return new;
end;
$$;
drop trigger if exists monarch_user_bootstrap on auth.users;
create trigger monarch_user_bootstrap after insert on auth.users for each row execute function public.bootstrap_monarch_user();

-- Enable RLS for every workspace-owned table.
do $$ declare t text; begin
  foreach t in array array['workspaces','workspace_members','projects','tasks','channels','content_items','saved_conversations','knowledge_notes','vault_spaces','vault_channels','vault_posts','vault_files','workspace_invitations'] loop
    execute format('alter table public.%I enable row level security',t);
  end loop;
end $$;

create policy "Members can view their workspace" on public.workspaces for select to authenticated using(public.is_workspace_member(id));
create policy "Signed-in users can create a workspace" on public.workspaces for insert to authenticated with check(created_by=(select auth.uid()));
create policy "Owners and admins update workspace" on public.workspaces for update to authenticated using(public.has_workspace_role(id,array['owner','admin'])) with check(public.has_workspace_role(id,array['owner','admin']));

create policy "Members can view membership" on public.workspace_members for select to authenticated using(public.is_workspace_member(workspace_id));
create policy "Owners and admins invite members" on public.workspace_members for insert to authenticated with check(
  public.has_workspace_role(workspace_id,array['owner']) or (role<>'owner' and public.has_workspace_role(workspace_id,array['admin']))
);
create policy "Owners and admins update membership safely" on public.workspace_members for update to authenticated
using(public.has_workspace_role(workspace_id,array['owner']) or (role<>'owner' and public.has_workspace_role(workspace_id,array['admin'])))
with check(public.has_workspace_role(workspace_id,array['owner']) or (role<>'owner' and public.has_workspace_role(workspace_id,array['admin'])));
create policy "Owners and admins remove non-owners" on public.workspace_members for delete to authenticated
using(public.has_workspace_role(workspace_id,array['owner']) or (role<>'owner' and public.has_workspace_role(workspace_id,array['admin'])));

-- Standard workspace data: visible to members, writable by all non-viewer roles.
do $$ declare t text; begin
 foreach t in array array['projects','tasks','channels','content_items','saved_conversations','knowledge_notes','vault_spaces','vault_channels','vault_posts','vault_files'] loop
  execute format('create policy %I on public.%I for select to authenticated using(public.is_workspace_member(workspace_id))',t||'_member_read',t);
  execute format('create policy %I on public.%I for insert to authenticated with check(public.has_workspace_role(workspace_id,array[''owner'',''admin'',''editor'',''contributor'']))',t||'_editor_insert',t);
  execute format('create policy %I on public.%I for update to authenticated using(public.has_workspace_role(workspace_id,array[''owner'',''admin'',''editor'',''contributor''])) with check(public.has_workspace_role(workspace_id,array[''owner'',''admin'',''editor'',''contributor'']))',t||'_editor_update',t);
  execute format('create policy %I on public.%I for delete to authenticated using(public.has_workspace_role(workspace_id,array[''owner'',''admin'',''editor'']))',t||'_editor_delete',t);
 end loop;
end $$;

create policy "Owners and admins manage invitations" on public.workspace_invitations for all to authenticated using(public.has_workspace_role(workspace_id,array['owner','admin'])) with check(public.has_workspace_role(workspace_id,array['owner','admin']));

-- Private bucket. Object paths begin with workspace UUID, then a random file UUID.
insert into storage.buckets(id,name,public,file_size_limit)
values('monarch-vault','monarch-vault',false,null)
on conflict(id) do update set public=false;
create policy "Workspace members read vault objects" on storage.objects for select to authenticated
using(bucket_id='monarch-vault' and public.is_workspace_member((storage.foldername(name))[1]::uuid));
create policy "Editors and contributors upload vault objects" on storage.objects for insert to authenticated
with check(bucket_id='monarch-vault' and public.has_workspace_role((storage.foldername(name))[1]::uuid,array['owner','admin','editor','contributor']));
create policy "Editors and contributors update vault objects" on storage.objects for update to authenticated
using(bucket_id='monarch-vault' and public.has_workspace_role((storage.foldername(name))[1]::uuid,array['owner','admin','editor','contributor']))
with check(bucket_id='monarch-vault' and public.has_workspace_role((storage.foldername(name))[1]::uuid,array['owner','admin','editor','contributor']));
create policy "Editors delete vault objects" on storage.objects for delete to authenticated
using(bucket_id='monarch-vault' and public.has_workspace_role((storage.foldername(name))[1]::uuid,array['owner','admin','editor']));

-- No automated cleanup/expiry is configured for vault files. Physical storage quotas, provider limits,
-- backups and billing are controlled by the chosen cloud plan and must be set before production.
