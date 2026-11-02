-- MONARCH® B2B Creative Studio & Safe Global Payment Portal OS (2026-11-02)
-- Adds public B2B service catalog, 24/7 lead intake, locked-preview client portals,
-- zero-P2P Desi + Foreign Fiat + Crypto payment submission/verification, and outreach CRM.

create or replace function public.is_studio_admin()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(lower((select auth.jwt()->>'email')), '') in (
    'workadilchandio@gmail.com',
    'aadialii424@gmail.com',
    'alipvip19@gmail.com',
    'pvip3026@gmail.com'
  )
$$;

revoke all on function public.is_studio_admin() from public;
grant execute on function public.is_studio_admin() to anon, authenticated;

-- 1. Proven B2B Services Catalog (Custom AI tools held in R&D with is_active = false)
create table if not exists public.agency_services (
  slug text primary key,
  sort_order smallint not null default 1,
  badge text not null default '',
  title text not null,
  subtitle text not null default '',
  description text not null default '',
  price_usd_label text not null,
  price_pkr_label text not null,
  turnaround_label text not null,
  deliverables jsonb not null default '[]'::jsonb,
  sample_preview_url text not null default '',
  sample_portal_code text not null default '',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 2. Zero-P2P Payment Rails Configuration (Singleton row id = 'default')
create table if not exists public.payment_rails_config (
  id text primary key default 'default' check (id = 'default'),
  studio_brand text not null default 'MONARCH® STUDIO',
  founder_name text not null default 'Adil Chandio',
  support_email text not null default 'workadilchandio@gmail.com',
  whatsapp_url text not null default '',
  -- Rail 1: Pakistan Local (SadaPay / Easypaisa / Raast)
  pkr_enabled boolean not null default true,
  pkr_account_title text not null default 'Adil Chandio',
  pkr_sadapay_number text not null default 'Request live number on Portal / Email confirmation',
  pkr_iban text not null default 'PK00 SADA 0000 0000 0000 0000 (Update in Founder OS -> Payment Rails)',
  pkr_easypaisa_number text not null default 'Available on request',
  pkr_instructions text not null default 'Transfer exact PKR milestone via Raast, SadaPay, or Easypaisa. Copy your 11-16 digit Transaction ID (TID) and submit below to unlock HD files.',
  -- Rail 2: Foreign Fiat (Contra 0% Card / nsave & Elevate Pay USD ACH / Wise->IBAN)
  fiat_enabled boolean not null default true,
  contra_profile_url text not null default 'https://contra.com',
  usd_ach_provider text not null default 'nsave / Elevate Pay Named USD Account',
  usd_ach_account_name text not null default 'Adil Chandio',
  usd_ach_routing_number text not null default 'Provided on Official USD Invoice (ACH / Wire)',
  usd_ach_account_number text not null default 'Provided on Official USD Invoice',
  intl_iban_remittance_note text not null default 'Direct Wise / Remitly / ACE transfer to Pakistani SadaPay IBAN also supported ($0 inbound fee).',
  fiat_instructions text not null default 'Pay via Apple Pay / Credit Card through Contra 0%-fee escrow link, or send domestic US ACH transfer to our named USD account. Paste receipt ID or reference below.',
  -- Rail 3: Global Instant Crypto (USDC Solana/Polygon + USDT TRC20 — Zero P2P)
  crypto_enabled boolean not null default true,
  usdc_solana_address text not null default 'Configure Solana USDC address in Founder OS -> Payment Rails',
  usdc_polygon_address text not null default 'Configure Polygon USDC (ERC20/Polygon) address in Founder OS',
  usdt_trc20_address text not null default 'Configure Tron USDT (TRC20) address in Founder OS',
  crypto_instructions text not null default 'Send exact USD value in USDC (Solana or Polygon recommended — <$0.01 network fee) or USDT (TRC20). Paste blockchain Transaction Hash (TxHash) below for fast verification.',
  updated_at timestamptz not null default now()
);

-- 3. 24/7 B2B Client Inquiries (Fed by MONARCH Hub + Portfolio #contactForm)
create table if not exists public.client_inquiries (
  id uuid primary key default gen_random_uuid(),
  client_name text not null check (char_length(trim(client_name)) between 1 and 140),
  client_email text not null check (char_length(trim(client_email)) between 3 and 180),
  company_or_brand text not null default '',
  whatsapp_or_telegram text not null default '',
  service_slug text not null default 'signature-websites',
  budget_tier text not null default '$280 - $650',
  preferred_rail text not null default 'foreign_fiat' check (preferred_rail in ('pkr_local', 'foreign_fiat', 'global_crypto')),
  project_brief text not null check (char_length(trim(project_brief)) between 5 and 5000),
  reference_links text not null default '',
  source text not null default 'monarch_hub',
  status text not null default 'new' check (status in ('new', 'replied', 'portal_sent', 'won', 'archived')),
  portal_id uuid,
  admin_notes text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists client_inquiries_status_idx on public.client_inquiries(status, created_at desc);

-- 4. Locked-Preview -> Pay-to-Unlock Client Portals
create table if not exists public.client_portals (
  id uuid primary key default gen_random_uuid(),
  portal_code text not null unique check (char_length(trim(portal_code)) between 4 and 32),
  client_name text not null,
  client_email text not null default '',
  client_company text not null default '',
  project_title text not null,
  service_type text not null default 'video' check (service_type in ('video', 'website', 'hybrid')),
  scope_summary text not null default '',
  deliverables jsonb not null default '[]'::jsonb,
  price_usd numeric(10,2) not null default 0 check (price_usd >= 0),
  price_pkr bigint not null default 0 check (price_pkr >= 0),
  milestone_label text not null default 'Final Delivery Unlock (100%)',
  preview_type text not null default 'video_watermarked' check (preview_type in ('video_watermarked', 'website_staging', 'storyboard_deck')),
  preview_url text not null default '',
  preview_notes text not null default '',
  watermark_label text not null default 'MONARCH® STUDIO · WATERMARKED PREVIEW',
  final_delivery_url text not null default '',
  secondary_delivery_url text not null default '',
  unlock_notes text not null default '',
  contra_invoice_url text not null default '',
  payment_status text not null default 'unpaid' check (payment_status in ('unpaid', 'proof_submitted', 'verified')),
  verified_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists client_portals_code_idx on public.client_portals(upper(portal_code));

-- 5. Client Payment Proofs (TID / ACH Reference / Contra Receipt / Blockchain TxHash)
create table if not exists public.payment_submissions (
  id uuid primary key default gen_random_uuid(),
  portal_id uuid not null references public.client_portals(id) on delete cascade,
  portal_code text not null,
  payment_rail text not null check (payment_rail in ('pkr_local', 'foreign_fiat', 'global_crypto')),
  method_label text not null default '',
  currency text not null default 'USD',
  amount_paid text not null default '',
  reference_or_tx_hash text not null check (char_length(trim(reference_or_tx_hash)) between 4 and 300),
  payer_name_or_wallet text not null default '',
  receipt_url text not null default '',
  notes text not null default '',
  status text not null default 'pending' check (status in ('pending', 'verified', 'rejected')),
  created_at timestamptz not null default now(),
  reviewed_at timestamptz
);
create index if not exists payment_submissions_portal_idx on public.payment_submissions(portal_id, created_at desc);

-- 6. B2B Outreach & Deal Pipeline CRM (Mobile-first for Tecno Spark Go 1)
create table if not exists public.outreach_campaigns (
  id uuid primary key default gen_random_uuid(),
  prospect_name text not null,
  company text not null default '',
  email_or_handle text not null default '',
  channel text not null default 'Email',
  service_pitched text not null default 'High-Retention Video + AI Reels',
  region text not null default 'US / UK / UAE',
  status text not null default 'drafted' check (status in ('queued', 'drafted', 'sent', 'replied', 'call_booked', 'won', 'closed')),
  deal_value_usd numeric(10,2) not null default 350,
  follow_up_at date,
  notes text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Enable RLS across all new B2B tables
alter table public.agency_services enable row level security;
alter table public.payment_rails_config enable row level security;
alter table public.client_inquiries enable row level security;
alter table public.client_portals enable row level security;
alter table public.payment_submissions enable row level security;
alter table public.outreach_campaigns enable row level security;

-- RLS Policies
create policy "Public reads active agency services"
  on public.agency_services for select to anon, authenticated
  using (is_active = true or public.is_studio_admin());

create policy "Studio admin manages agency services"
  on public.agency_services for all to authenticated
  using (public.is_studio_admin())
  with check (public.is_studio_admin());

create policy "Public reads payment rails config"
  on public.payment_rails_config for select to anon, authenticated
  using (true);

create policy "Studio admin manages payment rails config"
  on public.payment_rails_config for all to authenticated
  using (public.is_studio_admin())
  with check (public.is_studio_admin());

create policy "Studio admin manages client inquiries"
  on public.client_inquiries for all to authenticated
  using (public.is_studio_admin())
  with check (public.is_studio_admin());

create policy "Studio admin manages client portals"
  on public.client_portals for all to authenticated
  using (public.is_studio_admin())
  with check (public.is_studio_admin());

create policy "Studio admin manages payment submissions"
  on public.payment_submissions for all to authenticated
  using (public.is_studio_admin())
  with check (public.is_studio_admin());

create policy "Studio admin manages outreach campaigns"
  on public.outreach_campaigns for all to authenticated
  using (public.is_studio_admin())
  with check (public.is_studio_admin());

-- Security-Definer RPC 1: Public Lead Submission (Works from Storefront & Portfolio v37)
create or replace function public.submit_client_inquiry(
  p_client_name text,
  p_client_email text,
  p_company_or_brand text default '',
  p_whatsapp_or_telegram text default '',
  p_service_slug text default 'signature-websites',
  p_budget_tier text default '$280 - $650',
  p_preferred_rail text default 'foreign_fiat',
  p_project_brief text default '',
  p_reference_links text default '',
  p_source text default 'monarch_hub'
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_id uuid;
  v_rail text;
begin
  v_rail := case
    when p_preferred_rail in ('pkr_local', 'foreign_fiat', 'global_crypto') then p_preferred_rail
    else 'foreign_fiat'
  end;

  insert into public.client_inquiries (
    client_name,
    client_email,
    company_or_brand,
    whatsapp_or_telegram,
    service_slug,
    budget_tier,
    preferred_rail,
    project_brief,
    reference_links,
    source
  ) values (
    left(trim(coalesce(p_client_name, '')), 140),
    left(lower(trim(coalesce(p_client_email, ''))), 180),
    left(trim(coalesce(p_company_or_brand, '')), 140),
    left(trim(coalesce(p_whatsapp_or_telegram, '')), 100),
    left(trim(coalesce(nullif(p_service_slug, ''), 'signature-websites')), 80),
    left(trim(coalesce(p_budget_tier, '')), 80),
    v_rail,
    left(trim(coalesce(p_project_brief, '')), 5000),
    left(trim(coalesce(p_reference_links, '')), 1000),
    left(trim(coalesce(nullif(p_source, ''), 'monarch_hub')), 60)
  )
  returning id into v_id;

  return jsonb_build_object(
    'ok', true,
    'inquiry_id', v_id,
    'message', 'Project brief logged in MONARCH Studio cloud.'
  );
end;
$$;

revoke all on function public.submit_client_inquiry(text,text,text,text,text,text,text,text,text,text) from public;
grant execute on function public.submit_client_inquiry(text,text,text,text,text,text,text,text,text,text) to anon, authenticated;

-- Security-Definer RPC 2: Safe Portal Lookup (Redacts final HD URLs until verified!)
create or replace function public.get_client_portal(p_code text)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  p public.client_portals%rowtype;
  v_sub jsonb;
begin
  select *
    into p
    from public.client_portals
   where upper(trim(portal_code)) = upper(trim(coalesce(p_code, '')))
   limit 1;

  if not found then
    return jsonb_build_object('found', false);
  end if;

  select jsonb_build_object(
    'id', s.id,
    'payment_rail', s.payment_rail,
    'method_label', s.method_label,
    'currency', s.currency,
    'amount_paid', s.amount_paid,
    'reference_or_tx_hash', s.reference_or_tx_hash,
    'status', s.status,
    'created_at', s.created_at
  )
  into v_sub
  from public.payment_submissions s
  where s.portal_id = p.id
  order by s.created_at desc
  limit 1;

  return jsonb_build_object(
    'found', true,
    'id', p.id,
    'portal_code', p.portal_code,
    'client_name', p.client_name,
    'client_company', p.client_company,
    'project_title', p.project_title,
    'service_type', p.service_type,
    'scope_summary', p.scope_summary,
    'deliverables', p.deliverables,
    'price_usd', p.price_usd,
    'price_pkr', p.price_pkr,
    'milestone_label', p.milestone_label,
    'preview_type', p.preview_type,
    'preview_url', p.preview_url,
    'preview_notes', p.preview_notes,
    'watermark_label', p.watermark_label,
    'contra_invoice_url', p.contra_invoice_url,
    'payment_status', p.payment_status,
    'verified_at', p.verified_at,
    'updated_at', p.updated_at,
    'latest_submission', v_sub,
    -- STRICT PAYWALL REDACTION AT DATABASE LAYER:
    'final_delivery_url', case when p.payment_status = 'verified' then p.final_delivery_url else null end,
    'secondary_delivery_url', case when p.payment_status = 'verified' then p.secondary_delivery_url else null end,
    'unlock_notes', case when p.payment_status = 'verified' then p.unlock_notes else null end
  );
end;
$$;

revoke all on function public.get_client_portal(text) from public;
grant execute on function public.get_client_portal(text) to anon, authenticated;

-- Security-Definer RPC 3: Client Submits Payment Proof (TID / ACH Ref / TxHash)
create or replace function public.submit_portal_payment(
  p_code text,
  p_payment_rail text,
  p_method_label text,
  p_currency text,
  p_amount_paid text,
  p_reference_or_tx_hash text,
  p_payer_name_or_wallet text default '',
  p_receipt_url text default '',
  p_notes text default ''
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  p public.client_portals%rowtype;
  v_sub_id uuid;
begin
  select *
    into p
    from public.client_portals
   where upper(trim(portal_code)) = upper(trim(coalesce(p_code, '')))
   limit 1;

  if not found then
    raise exception 'Portal code not found';
  end if;

  if p_payment_rail not in ('pkr_local', 'foreign_fiat', 'global_crypto') then
    raise exception 'Invalid payment rail';
  end if;

  if char_length(trim(coalesce(p_reference_or_tx_hash, ''))) < 4 then
    raise exception 'Please enter a valid Transaction ID (TID), receipt ID, or blockchain TxHash';
  end if;

  insert into public.payment_submissions (
    portal_id,
    portal_code,
    payment_rail,
    method_label,
    currency,
    amount_paid,
    reference_or_tx_hash,
    payer_name_or_wallet,
    receipt_url,
    notes
  ) values (
    p.id,
    p.portal_code,
    p_payment_rail,
    left(trim(coalesce(p_method_label, '')), 100),
    left(trim(coalesce(nullif(p_currency, ''), 'USD')), 16),
    left(trim(coalesce(p_amount_paid, '')), 60),
    left(trim(p_reference_or_tx_hash), 300),
    left(trim(coalesce(p_payer_name_or_wallet, '')), 180),
    left(trim(coalesce(p_receipt_url, '')), 500),
    left(trim(coalesce(p_notes, '')), 1000)
  )
  returning id into v_sub_id;

  if p.payment_status <> 'verified' then
    update public.client_portals
       set payment_status = 'proof_submitted',
           updated_at = now()
     where id = p.id;
  end if;

  return jsonb_build_object(
    'ok', true,
    'submission_id', v_sub_id,
    'payment_status', case when p.payment_status = 'verified' then 'verified' else 'proof_submitted' end
  );
end;
$$;

revoke all on function public.submit_portal_payment(text,text,text,text,text,text,text,text,text) from public;
grant execute on function public.submit_portal_payment(text,text,text,text,text,text,text,text,text) to anon, authenticated;

-- Security-Definer RPC 4: 1-Tap Mobile Admin Verify & Unlock
create or replace function public.admin_verify_portal_payment(
  p_portal_id uuid,
  p_approve boolean default true
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
begin
  if not public.is_studio_admin() then
    raise exception 'Founder admin authorization required';
  end if;

  update public.client_portals
     set payment_status = case when p_approve then 'verified' else 'unpaid' end,
         verified_at = case when p_approve then now() else null end,
         updated_at = now()
   where id = p_portal_id;

  update public.payment_submissions
     set status = case when p_approve then 'verified' else 'rejected' end,
         reviewed_at = now()
   where portal_id = p_portal_id
     and status = 'pending';

  return jsonb_build_object(
    'ok', true,
    'payment_status', case when p_approve then 'verified' else 'unpaid' end
  );
end;
$$;

revoke all on function public.admin_verify_portal_payment(uuid, boolean) from public;
grant execute on function public.admin_verify_portal_payment(uuid, boolean) to authenticated;

-- Seed Default Payment Rails Singleton
insert into public.payment_rails_config (id)
values ('default')
on conflict (id) do nothing;

-- Seed 2 Active B2B High-Ticket Services + 1 R&D-Hold Service
insert into public.agency_services (
  slug, sort_order, badge, title, subtitle, description,
  price_usd_label, price_pkr_label, turnaround_label, deliverables,
  sample_preview_url, sample_portal_code, is_active
) values
(
  'signature-websites',
  1,
  'FLAGSHIP B2B WEB SYSTEM',
  'Signature Interactive Websites & Launch Hubs',
  'Cinematic dark-luxury & high-converting web architecture for founders, agencies, and SaaS brands.',
  'Custom-engineered interactive websites built with bespoke motion choreography, ultra-fast Vite/React or zero-bloat static architecture, cloud lead capture, and mobile-first precision.',
  '$280 – $650 USD',
  'PKR 78,000 – 180,000',
  '5 – 7 Days',
  '["Custom Obsidian/Editorial UI Direction & Motion System","Interactive Live Staging Link Before Final Payment","24/7 Cloud Lead Capture + CRM Wiring (Supabase)","100% Mobile-Responsive + SEO Performance Optimization","Full GitHub Source Code + Production Vercel Deployment"]'::jsonb,
  'https://adil-chandio.github.io/portfolio/',
  'MON-WEB26',
  true
),
(
  'cinematic-video-ai',
  2,
  'HIGH-RETENTION FILM & REELS',
  'High-Retention Video Editing & AI Commercials',
  ' Frame-accurate short-form reels, founder VSLs, and AI-directed brand commercials engineered to hold attention.',
  'Built on MONARCH Studio''s narrative hook architecture: razor-sharp pacing, custom kinetic captions, sound design (-14 LUFS broadcast master), and watermarked client review portals.',
  '$180 – $480 USD',
  'PKR 50,000 – 135,000',
  '48 – 72 Hours',
  '["Hook-Engineered Edit / AI Visual Direction (9:16 or 16:9)","Custom Sound Design, Foley & Broadcast Loudness (-14 LUFS)","Kinetic Typography + Retention Pacing Cuts","Watermarked Portal Review + 1 Fine-Tune Revision Round","Unwatermarked 60fps Master + Thumbnail Cover Pack"]'::jsonb,
  'https://adil-chandio.github.io/portfolio/',
  'MON-DEMO26',
  true
),
(
  'custom-ai-automation',
  3,
  'INTERNAL R&D LAB (HOLD)',
  'Custom AI Agents & Workflow Systems',
  'Currently in private internal stress-testing before public B2B release.',
  'Held in internal MONARCH R&D lab until 100% end-to-end reliability benchmarks pass.',
  'Private Beta',
  'Private Beta',
  'Invite Only',
  '["End-to-End Reliability Audit Required Before Sale"]'::jsonb,
  '',
  '',
  false
)
on conflict (slug) do update set
  title = excluded.title,
  subtitle = excluded.subtitle,
  description = excluded.description,
  price_usd_label = excluded.price_usd_label,
  price_pkr_label = excluded.price_pkr_label,
  turnaround_label = excluded.turnaround_label,
  deliverables = excluded.deliverables,
  sample_preview_url = excluded.sample_preview_url,
  sample_portal_code = excluded.sample_portal_code,
  is_active = excluded.is_active,
  updated_at = now();

-- Seed 2 Live Interactive Demo Client Portals (Video + Website)
insert into public.client_portals (
  portal_code, client_name, client_email, client_company, project_title,
  service_type, scope_summary, deliverables, price_usd, price_pkr,
  milestone_label, preview_type, preview_url, preview_notes, watermark_label,
  final_delivery_url, secondary_delivery_url, unlock_notes, contra_invoice_url, payment_status
) values
(
  'MON-DEMO26',
  'Demo Brand Partner',
  'partner@branddemo.io',
  'Vanguard Studio Labs',
  'Night Shift — 60s AI Brand Commercial & Reels Pack',
  'video',
  '3× high-retention vertical reels + 1× 60s hero AI brand film with custom sound design, kinetic captions, and -14 LUFS master audio.',
  '["60s Hero AI Commercial (1080x1920, 60fps Master)","3x Hook-Variant Cutdowns for Reels / TikTok / Shorts","4K Thumbnail & Cover Frame Pack","Worldwide Perpetual Commercial Usage License"]'::jsonb,
  240.00,
  67000,
  'Final Master Unlock (100% Milestone)',
  'video_watermarked',
  'https://adil-chandio.github.io/portfolio/',
  'Review pacing, sound mix, and caption timing inside the watermarked preview stage. Once approved, complete payment via Local PKR, Foreign USD/Card, or Instant USDC to unlock the unwatermarked master bundle.',
  'MONARCH® STUDIO · WATERMARKED CLIENT PREVIEW · DO NOT DISTRIBUTE',
  'https://drive.google.com/file/d/1XSlpaEmOdysqM8FpRmWUfNElz9IAxmXV/view?usp=drivesdk',
  'https://drive.google.com/drive/folders/1ULb_LwBLOHM9GdvPXf6KXsp0Do9n0Zr1',
  'Thank you! Your unwatermarked 60fps master pack and commercial license are unlocked above. Reply to workadilchandio@gmail.com within 7 days for any fine-tune adjustments.',
  'https://contra.com',
  'unpaid'
),
(
  'MON-WEB26',
  'Apex Ventures Team',
  'founder@apexventures.co',
  'Apex Ventures',
  'Obsidian Interactive B2B Launch Website',
  'website',
  'Bespoke dark-luxury B2B launch site with scroll choreography, mobile-first conversion funnel, and 24/7 Supabase cloud lead intake.',
  '["Custom Responsive Vite/React Source Repository","Live Cloud Lead Capture + Admin Dashboard","SEO Meta, OpenGraph & Core Web Vitals Optimization","Production Vercel Deployment + Custom Domain Wiring"]'::jsonb,
  450.00,
  125000,
  'Source Bundle & Domain Handover Unlock',
  'website_staging',
  'https://adil-chandio.github.io/portfolio/',
  'Inspect live interactive staging choreography on mobile and desktop. Production repository zip and custom domain transfer unlock immediately upon payment verification.',
  'MONARCH® STUDIO · STAGING PREVIEW · SOURCE LOCKED',
  'https://drive.google.com/drive/folders/1ULb_LwBLOHM9GdvPXf6KXsp0Do9n0Zr1',
  'https://drive.google.com/file/d/1XSlpaEmOdysqM8FpRmWUfNElz9IAxmXV/view?usp=drivesdk',
  'Production source bundle + deployment handover guide unlocked! Send your domain DNS registrar details to workadilchandio@gmail.com if you want us to complete live domain pointing.',
  'https://contra.com',
  'unpaid'
)
on conflict (portal_code) do nothing;

-- Seed Initial Outreach Targets/Templates for Tecno Spark Go 1 Mobile Pipeline
insert into public.outreach_campaigns (
  prospect_name, company, email_or_handle, channel, service_pitched, region, status, deal_value_usd, notes
) values
(
  'US / UK SaaS Founder Template',
  'Seed-Stage AI / SaaS Startups',
  'Draft ready in Gmail -> MONARCH/Outreach-Active',
  'Gmail + X DM',
  'Signature Interactive Website ($450)',
  'US / UK (USD ACH / Contra / USDC)',
  'drafted',
  450.00,
  'Pitch 5-day dark-luxury interactive site upgrade + show adil-chandio.github.io/portfolio/ + MON-WEB26 portal demo.'
),
(
  'YouTube / Agency Creator Retainer Template',
  'Personal Brands & Marketing Agencies',
  'Draft ready in Gmail -> MONARCH/Outreach-Active',
  'Gmail + Instagram',
  'High-Retention Reels & AI Commercials ($240)',
  'UAE / US / Global (USDC / USD ACH)',
  'drafted',
  240.00,
  'Pitch 48-hour hook-engineered reels pack + watermarked portal delivery (MON-DEMO26).'
),
(
  'Pakistan Premium Brand / Real Estate / E-Com',
  'Karachi / Lahore / Islamabad Growth Brands',
  'Draft ready in Gmail -> MONARCH/Outreach-Active',
  'Gmail + WhatsApp',
  'B2B Website + Launch Reel Combo (PKR 95,000)',
  'Pakistan (SadaPay / Raast)',
  'drafted',
  340.00,
  'Local PKR Raast / SadaPay instant settlement with locked-preview portal trust.'
);
