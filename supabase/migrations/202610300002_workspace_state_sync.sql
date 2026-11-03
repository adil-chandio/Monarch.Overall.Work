-- Single-workspace document sync for Monarch's low-volume work records.
-- Large binaries stay in the private Storage bucket, not in JSONB.
create table public.workspace_state (
  workspace_id uuid primary key references public.workspaces(id) on delete cascade,
  data jsonb not null default '{}'::jsonb check (jsonb_typeof(data)='object'),
  revision bigint not null default 0 check (revision >= 0),
  updated_by uuid not null references auth.users(id),
  updated_at timestamptz not null default now()
);
alter table public.workspace_state enable row level security;
create policy "Workspace members read synced state" on public.workspace_state for select to authenticated
using(public.is_workspace_member(workspace_id));

create or replace function public.save_workspace_state(target_workspace uuid, expected_revision bigint, new_data jsonb)
returns table(saved_revision bigint, conflict boolean)
language plpgsql security definer set search_path = '' as $$
declare current_revision bigint;
begin
  if not public.has_workspace_role(target_workspace,array['owner','admin','editor','contributor']) then
    raise exception 'Workspace write access required';
  end if;
  if jsonb_typeof(new_data) <> 'object' then raise exception 'Workspace state must be a JSON object'; end if;
  perform pg_advisory_xact_lock(hashtext(target_workspace::text));
  select s.revision into current_revision from public.workspace_state s where s.workspace_id=target_workspace for update;
  if not found then
    if expected_revision <> 0 then return query select 0::bigint,true; return; end if;
    insert into public.workspace_state(workspace_id,data,revision,updated_by)
    values(target_workspace,new_data,1,(select auth.uid()));
    return query select 1::bigint,false; return;
  end if;
  if current_revision <> expected_revision then return query select current_revision,true; return; end if;
  update public.workspace_state s set data=new_data,revision=current_revision+1,updated_by=(select auth.uid()),updated_at=now()
  where s.workspace_id=target_workspace;
  return query select current_revision+1,false;
end;
$$;
revoke all on function public.save_workspace_state(uuid,bigint,jsonb) from public;
grant execute on function public.save_workspace_state(uuid,bigint,jsonb) to authenticated;
