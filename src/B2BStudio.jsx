import React, { useCallback, useEffect, useState } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  Check,
  Copy,
  CreditCard,
  ExternalLink,
  Film,
  Globe,
  LockKeyhole,
  Mail,
  Plus,
  RefreshCw,
  Send,
  ShieldCheck,
  Sparkles,
  Unlock,
  Wallet,
  Zap,
} from 'lucide-react';
import './b2b.css';
import { supabase } from './lib/supabase';

const INTAKE_EDGE_URL = 'https://oeqeqlgatdlqbuywktnu.supabase.co/functions/v1/public-intake';
const PORTFOLIO_URL = 'https://adil-chandio.github.io/portfolio/';

const DEFAULT_SERVICES = [
  {
    slug: 'signature-websites',
    badge: 'FLAGSHIP B2B WEB SYSTEM',
    title: 'Signature Interactive Websites & Launch Hubs',
    subtitle: 'Cinematic dark-luxury & high-converting web architecture for founders, agencies, and SaaS brands.',
    description:
      'Custom-engineered interactive websites built with bespoke motion choreography, ultra-fast Vite/React or zero-bloat static architecture, 24/7 cloud lead capture, and mobile-first precision.',
    price_usd_label: '$280 – $650 USD',
    price_pkr_label: 'PKR 78,000 – 180,000',
    turnaround_label: '5 – 7 Days',
    deliverables: [
      'Custom Obsidian/Editorial UI Direction & Motion System',
      'Interactive Live Staging Link Before Final Payment',
      '24/7 Cloud Lead Capture + CRM Wiring (Supabase)',
      '100% Mobile-Responsive + SEO Performance Optimization',
      'Full GitHub Source Code + Production Vercel Deployment',
    ],
    sample_preview_url: PORTFOLIO_URL,
    sample_portal_code: 'MON-WEB26',
  },
  {
    slug: 'cinematic-video-ai',
    badge: 'HIGH-RETENTION FILM & REELS',
    title: 'High-Retention Video Editing & AI Commercials',
    subtitle: 'Frame-accurate short-form reels, founder VSLs, and AI-directed brand commercials engineered to hold attention.',
    description:
      'Built on MONARCH Studio’s narrative hook architecture: razor-sharp pacing, custom kinetic captions, sound design (-14 LUFS broadcast master), and watermarked client review portals.',
    price_usd_label: '$180 – $480 USD',
    price_pkr_label: 'PKR 50,000 – 135,000',
    turnaround_label: '48 – 72 Hours',
    deliverables: [
      'Hook-Engineered Edit / AI Visual Direction (9:16 or 16:9)',
      'Custom Sound Design, Foley & Broadcast Loudness (-14 LUFS)',
      'Kinetic Typography + Retention Pacing Cuts',
      'Watermarked Portal Review + 1 Fine-Tune Revision Round',
      'Unwatermarked 60fps Master + Thumbnail Cover Pack',
    ],
    sample_preview_url: PORTFOLIO_URL,
    sample_portal_code: 'MON-DEMO26',
  },
];

const DEFAULT_RAILS = {
  studio_brand: 'MONARCH® STUDIO',
  founder_name: 'Adil Chandio',
  support_email: 'workadilchandio@gmail.com',
  pkr_enabled: true,
  pkr_account_title: 'Adil Chandio',
  pkr_sadapay_number: 'Request live number on Portal / Email confirmation',
  pkr_iban: 'PK00 SADA 0000 0000 0000 0000 (Update in Founder OS -> Payment Rails)',
  pkr_easypaisa_number: 'Available on request',
  pkr_instructions:
    'Transfer exact PKR milestone via Raast, SadaPay, or Easypaisa. Copy your 11–16 digit Transaction ID (TID) and submit below to unlock HD files.',
  fiat_enabled: true,
  contra_profile_url: 'https://contra.com',
  usd_ach_provider: 'nsave / Elevate Pay Named USD Account',
  usd_ach_account_name: 'Adil Chandio',
  usd_ach_routing_number: 'Provided on Official USD Invoice (ACH / Wire)',
  usd_ach_account_number: 'Provided on Official USD Invoice',
  intl_iban_remittance_note:
    'Direct Wise / Remitly / ACE transfer to Pakistani SadaPay IBAN also supported ($0 inbound fee).',
  fiat_instructions:
    'Pay via Apple Pay / Credit Card through Contra 0%-fee escrow link, or send domestic US ACH transfer to our named USD account. Paste receipt ID or reference below.',
  crypto_enabled: true,
  usdc_solana_address: 'Configure Solana USDC address in Founder OS -> Payment Rails',
  usdc_polygon_address: 'Configure Polygon USDC (ERC20/Polygon) address in Founder OS',
  usdt_trc20_address: 'Configure Tron USDT (TRC20) address in Founder OS',
  crypto_instructions:
    'Send exact USD value in USDC (Solana or Polygon recommended — <$0.01 network fee) or USDT (TRC20). Paste blockchain Transaction Hash (TxHash) below for fast verification.',
};

function CopyRow({ label, value }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    if (!value) return;
    navigator.clipboard?.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };
  return (
    <div className="m-copy-box">
      <div>
        <small>{label}</small>
        <code>{value || '—'}</code>
      </div>
      <button type="button" className="m-copy-btn" onClick={copy}>
        {copied ? <Check size={13} /> : <Copy size={13} />}
        {copied ? 'Copied' : 'Copy'}
      </button>
    </div>
  );
}

/* ============================================================================
   1. PUBLIC B2B CREATIVE STUDIO & SERVICES STOREFRONT (/)
   ============================================================================ */
export function MonarchPublicStudio({ onOpenPortal, onOpenWorkspace }) {
  const [services, setServices] = useState(DEFAULT_SERVICES);
  const [portalInput, setPortalInput] = useState('');
  const [brief, setBrief] = useState({
    client_name: '',
    client_email: '',
    company_or_brand: '',
    whatsapp_or_telegram: '',
    service_slug: 'signature-websites',
    budget_tier: '$280 – $650 USD',
    preferred_rail: 'foreign_fiat',
    project_brief: '',
    reference_links: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState(null);

  useEffect(() => {
    if (!supabase) return;
    supabase
      .from('agency_services')
      .select('*')
      .eq('is_active', true)
      .order('sort_order', { ascending: true })
      .then(({ data }) => {
        if (Array.isArray(data) && data.length > 0) setServices(data);
      })
      .catch(() => {});
  }, []);

  const selectServiceForBrief = (slug, defaultBudget) => {
    setBrief((prev) => ({
      ...prev,
      service_slug: slug,
      budget_tier: defaultBudget || prev.budget_tier,
    }));
    document.getElementById('brief')?.scrollIntoView({ behavior: 'smooth' });
  };

  const handlePortalLookup = (e) => {
    e.preventDefault();
    const cleaned = portalInput.trim().toUpperCase();
    if (!cleaned) return;
    onOpenPortal(cleaned);
  };

  const handleBriefSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitResult(null);
    try {
      if (supabase) {
        const { error } = await supabase.rpc('submit_client_inquiry', {
          p_client_name: brief.client_name,
          p_client_email: brief.client_email,
          p_company_or_brand: brief.company_or_brand,
          p_whatsapp_or_telegram: brief.whatsapp_or_telegram,
          p_service_slug: brief.service_slug,
          p_budget_tier: brief.budget_tier,
          p_preferred_rail: brief.preferred_rail,
          p_project_brief: brief.project_brief,
          p_reference_links: brief.reference_links,
          p_source: 'monarch_hub',
        });
        if (error) throw error;
      } else {
        const res = await fetch(INTAKE_EDGE_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...brief, source: 'monarch_hub' }),
        });
        const body = await res.json();
        if (!res.ok || !body.ok) throw new Error(body.error || 'Could not submit brief');
      }

      setSubmitResult({
        ok: true,
        text: 'Project brief logged in MONARCH Studio Cloud! Adil Chandio will review your scope and issue your private MON-XXXX Client Portal link within 12–24 hours.',
      });
      setBrief((prev) => ({
        ...prev,
        client_name: '',
        client_email: '',
        company_or_brand: '',
        whatsapp_or_telegram: '',
        project_brief: '',
        reference_links: '',
      }));
    } catch (err) {
      setSubmitResult({
        ok: false,
        text: err.message || 'Submission failed. Please email workadilchandio@gmail.com directly.',
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="monarch-public-root">
      <header className="m-nav">
        <div className="m-container m-nav-inner">
          <button type="button" className="m-brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <span className="m-brand-mark">M</span>
            <span className="m-brand-copy">
              <b>MONARCH® STUDIO</b>
              <small>ADIL CHANDIO · B2B SYSTEMS</small>
            </span>
          </button>

          <nav className="m-nav-links">
            <a href="#services">Services</a>
            <a href="#delivery">Safe Delivery</a>
            <a href="#brief">Start Brief</a>
            <a href={PORTFOLIO_URL} target="_blank" rel="noopener noreferrer">
              Portfolio v37 ↗
            </a>
          </nav>

          <div className="m-nav-actions">
            <button type="button" className="m-btn m-btn-ghost" onClick={() => onOpenPortal('MON-DEMO26')}>
              <LockKeyhole size={14} /> Client Portal
            </button>
            <button type="button" className="m-btn m-btn-subtle" onClick={onOpenWorkspace} title="Founder Workspace">
              Founder OS
            </button>
          </div>
        </div>
      </header>

      <main>
        {/* HERO */}
        <section className="m-hero">
          <div className="m-container">
            <div className="m-kicker">
              <Sparkles size={13} /> MONARCH® B2B CREATIVE ARCHITECTURE · GLOBAL & PAKISTAN
            </div>

            <div className="m-hero-grid">
              <div>
                <h1>
                  Signature Websites &amp; <span>High-Retention Films</span> Built to Convert.
                </h1>
                <p className="m-hero-lead">
                  Two specialized B2B production engines by Adil Chandio. Review watermarked 60fps cuts and live
                  interactive web staging inside your private <b>MONARCH Client Portal</b> — settle via US Bank (ACH),
                  Card, Instant USDC, or Local PKR to unlock master deliverables immediately.
                </p>

                <div className="m-hero-ctas">
                  <a href="#brief" className="m-btn m-btn-crimson">
                    Start Project Brief <ArrowRight size={15} />
                  </a>
                  <a
                    href={PORTFOLIO_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="m-btn m-btn-ghost"
                  >
                    Inspect Flagship Portfolio <ArrowUpRight size={15} />
                  </a>
                </div>

                <div className="m-trust-strip">
                  <span className="m-trust-pill">
                    <ShieldCheck size={14} /> Watermarked Preview Before Final Payment
                  </span>
                  <span className="m-trust-pill">
                    <Globe size={14} /> US ACH · Apple Pay/Card · USDC · Raast PKR
                  </span>
                </div>
              </div>

              {/* CLIENT PORTAL QUICK ACCESS */}
              <aside className="m-portal-box">
                <div className="m-portal-box-top">
                  <small>LOCKED-PREVIEW CLIENT VAULT</small>
                  <h2>Open Your Client Portal</h2>
                  <p>
                    Have a project code from MONARCH®? Enter it below to inspect your live preview, submit milestone
                    settlement, and unlock unwatermarked master files.
                  </p>
                  <form className="m-code-form" onSubmit={handlePortalLookup}>
                    <input
                      value={portalInput}
                      onChange={(e) => setPortalInput(e.target.value)}
                      placeholder="Enter code e.g. MON-DEMO26"
                      aria-label="Client Portal Code"
                    />
                    <button type="submit" className="m-btn m-btn-crimson">
                      Open <ArrowRight size={14} />
                    </button>
                  </form>
                </div>

                <div className="m-demo-chips">
                  <span>Live Interactive Demos:</span>
                  <button type="button" onClick={() => onOpenPortal('MON-DEMO26')}>
                    MON-DEMO26 (Film)
                  </button>
                  <button type="button" onClick={() => onOpenPortal('MON-WEB26')}>
                    MON-WEB26 (Website)
                  </button>
                </div>
              </aside>
            </div>

            {/* EMBEDDED 60FPS COMMERCIAL SHOWREEL */}
            <div
              style={{
                marginTop: 28,
                padding: '18px 20px',
                borderRadius: 20,
                background: 'rgba(16, 16, 20, 0.92)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: 10,
                  marginBottom: 12,
                }}
              >
                <div>
                  <small
                    style={{
                      fontFamily: 'JetBrains Mono, monospace',
                      fontSize: 11,
                      color: '#ff8e96',
                      letterSpacing: '0.12em',
                    }}
                  >
                    LIVE 60FPS BROADCAST SHOWREEL · -14 LUFS STEREO
                  </small>
                  <h3 style={{ margin: '4px 0 0', fontFamily: 'Syne, sans-serif', fontSize: 19 }}>
                    Night Shift — MONARCH® Commercial &amp; Locked-Preview Vault Demo
                  </h3>
                </div>
                <button
                  type="button"
                  className="m-btn m-btn-crimson"
                  onClick={() => onOpenPortal('MON-DEMO26')}
                >
                  Inspect Inside Client Vault (MON-DEMO26) <ArrowRight size={14} />
                </button>
              </div>
              <video
                src="/demo-preview.mp4"
                poster="/demo-poster.jpg"
                controls
                playsInline
                preload="metadata"
                controlsList="nodownload"
                style={{
                  width: '100%',
                  borderRadius: 14,
                  border: '1px solid rgba(210, 31, 43, 0.35)',
                  background: '#050507',
                  display: 'block',
                  maxHeight: 520,
                }}
              />
            </div>
          </div>
        </section>

        {/* 2 PROVEN B2B SERVICES */}
        <section id="services" className="m-section">
          <div className="m-container">
            <div className="m-section-head">
              <div>
                <small>FOCUSED EXECUTION · ZERO FLUFF</small>
                <h2>Two High-Impact B2B Production Engines</h2>
                <p>
                  Every deliverable is crafted for measurable brand authority, retention, and conversion — backed by
                  verified cloud delivery.
                </p>
              </div>
              <a href={PORTFOLIO_URL} target="_blank" rel="noopener noreferrer" className="m-btn m-btn-ghost">
                View Full Work Archive <ExternalLink size={14} />
              </a>
            </div>

            <div className="m-services-grid">
              {services.map((svc, idx) => {
                const list = Array.isArray(svc.deliverables) ? svc.deliverables : [];
                return (
                  <article className="m-service-card" key={svc.slug}>
                    <div>
                      <div className="m-service-badge">
                        {idx === 0 ? <Globe size={14} /> : <Film size={14} />}
                        <span>{svc.badge}</span>
                      </div>
                      <h3>{svc.title}</h3>
                      <p className="m-service-sub">{svc.subtitle}</p>
                      <p className="m-service-desc">{svc.description}</p>

                      <div className="m-price-band">
                        <div>
                          <small>Global Rate</small>
                          <b>{svc.price_usd_label}</b>
                        </div>
                        <div>
                          <small>Pakistan Local</small>
                          <b>{svc.price_pkr_label}</b>
                        </div>
                        <div>
                          <small>Turnaround</small>
                          <b>{svc.turnaround_label}</b>
                        </div>
                      </div>

                      <ul className="m-deliverable-list">
                        {list.map((item, i) => (
                          <li key={i}>
                            <Check size={15} />
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="m-service-actions">
                      <button
                        type="button"
                        className="m-btn m-btn-crimson"
                        onClick={() => selectServiceForBrief(svc.slug, svc.price_usd_label)}
                      >
                        Scope This Service <ArrowRight size={14} />
                      </button>
                      {svc.sample_portal_code && (
                        <button
                          type="button"
                          className="m-btn m-btn-ghost"
                          onClick={() => onOpenPortal(svc.sample_portal_code)}
                        >
                          Live Portal Demo ({svc.sample_portal_code})
                        </button>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        {/* 3-STEP SAFE DELIVERY ARCHITECTURE */}
        <section id="delivery" className="m-section">
          <div className="m-container">
            <div className="m-section-head">
              <div>
                <small>ZERO-RISK CLIENT PROTOCOL</small>
                <h2>Locked-Preview → Safe Settlement → Instant Unlock</h2>
                <p>
                  No guesswork and zero P2P risk. Clients inspect real work inside a dedicated portal before unlocking
                  master deliverables.
                </p>
              </div>
            </div>

            <div className="m-steps-grid">
              <div className="m-step-card">
                <span className="m-step-num">STEP 01 · ARCHITECTURE</span>
                <h3>Submit Scope &amp; Get Portal Code</h3>
                <p>
                  Send your brief below. Within 12–24h you receive a fixed USD/PKR quote, timeline, and your dedicated
                  <code> MON-XXXX </code> tracking portal.
                </p>
              </div>
              <div className="m-step-card">
                <span className="m-step-num">STEP 02 · LOCKED PREVIEW</span>
                <h3>Inspect Watermarked Cut or Live Staging</h3>
                <p>
                  Review frame-accurate pacing, sound design, or live mobile/desktop website choreography directly
                  inside your portal and request fine-tune adjustments.
                </p>
              </div>
              <div className="m-step-card">
                <span className="m-step-num">STEP 03 · INSTANT UNLOCK</span>
                <h3>Pay via USD, Crypto, or PKR &amp; Download</h3>
                <p>
                  Settle safely via Contra Card/Apple Pay, Named US ACH, Instant USDC/USDT, or Local Raast/SadaPay.
                  Master unwatermarked files &amp; source code unlock immediately.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* 24/7 CLOUD BRIEF FORM */}
        <section id="brief" className="m-section">
          <div className="m-container">
            <div className="m-section-head">
              <div>
                <small>24/7 DIRECT CLOUD INTAKE</small>
                <h2>Start Your Project Brief</h2>
                <p>
                  Logged directly into MONARCH Studio Cloud. Pick your preferred service and payment rail for a fast,
                  structured proposal.
                </p>
              </div>
            </div>

            <div className="m-brief-wrap">
              <aside className="m-rail-summary-card">
                <h3 style={{ margin: 0, fontFamily: 'Syne, sans-serif' }}>Supported Safe Payment Rails</h3>
                <div className="m-rail-item">
                  <b>🌍 Foreign Fiat (US / UK / EU / UAE)</b>
                  <small>
                    Apple Pay &amp; Credit/Debit Card via Contra (0% commission escrow), Named US ACH Bank Transfer
                    (nsave / Elevate Pay), or Wise/Remitly to IBAN.
                  </small>
                </div>
                <div className="m-rail-item">
                  <b>⚡ Instant Global Crypto (24/7 Borderless)</b>
                  <small>
                    Direct USDC (Solana / Polygon — under $0.01 fee) or USDT (TRC20) with Explorer TxHash verification.
                  </small>
                </div>
                <div className="m-rail-item">
                  <b>🇵🇰 Pakistan Local Business Rail</b>
                  <small>
                    Instant PKR transfer via Raast, SadaPay IBAN, or Easypaisa with Transaction ID (TID) unlock.
                  </small>
                </div>
                <div className="m-rail-item">
                  <b>Direct Studio Contact</b>
                  <small>workadilchandio@gmail.com · Response within 12–24h</small>
                </div>
              </aside>

              <form className="m-brief-form" onSubmit={handleBriefSubmit}>
                <div className="m-form-row">
                  <div className="m-field">
                    <label>Your Name *</label>
                    <input
                      required
                      value={brief.client_name}
                      onChange={(e) => setBrief({ ...brief, client_name: e.target.value })}
                      placeholder="Alex Rivera"
                    />
                  </div>
                  <div className="m-field">
                    <label>Work Email *</label>
                    <input
                      required
                      type="email"
                      value={brief.client_email}
                      onChange={(e) => setBrief({ ...brief, client_email: e.target.value })}
                      placeholder="alex@company.com"
                    />
                  </div>
                </div>

                <div className="m-form-row">
                  <div className="m-field">
                    <label>Company / Brand / Channel</label>
                    <input
                      value={brief.company_or_brand}
                      onChange={(e) => setBrief({ ...brief, company_or_brand: e.target.value })}
                      placeholder="Vanguard Labs"
                    />
                  </div>
                  <div className="m-field">
                    <label>WhatsApp or Telegram (Optional)</label>
                    <input
                      value={brief.whatsapp_or_telegram}
                      onChange={(e) => setBrief({ ...brief, whatsapp_or_telegram: e.target.value })}
                      placeholder="+1 555 ... or @handle"
                    />
                  </div>
                </div>

                <div className="m-form-row">
                  <div className="m-field">
                    <label>Service Needed *</label>
                    <select
                      value={brief.service_slug}
                      onChange={(e) => setBrief({ ...brief, service_slug: e.target.value })}
                    >
                      <option value="signature-websites">Signature Interactive Website ($280 – $650)</option>
                      <option value="cinematic-video-ai">High-Retention Video / AI Commercial ($180 – $480)</option>
                      <option value="website-plus-video-bundle">Full Launch Bundle: Website + Hero Film ($650+)</option>
                    </select>
                  </div>
                  <div className="m-field">
                    <label>Preferred Payment Rail *</label>
                    <select
                      value={brief.preferred_rail}
                      onChange={(e) => setBrief({ ...brief, preferred_rail: e.target.value })}
                    >
                      <option value="foreign_fiat">Foreign USD Bank (ACH) / Card (Contra)</option>
                      <option value="global_crypto">Instant Crypto (USDC Solana/Polygon · USDT)</option>
                      <option value="pkr_local">Pakistan Local PKR (SadaPay / Raast / Easypaisa)</option>
                    </select>
                  </div>
                </div>

                <div className="m-form-row">
                  <div className="m-field">
                    <label>Estimated Budget</label>
                    <select
                      value={brief.budget_tier}
                      onChange={(e) => setBrief({ ...brief, budget_tier: e.target.value })}
                    >
                      <option value="$180 – $300 USD (PKR 50k – 85k)">$180 – $300 USD (PKR 50k – 85k)</option>
                      <option value="$280 – $650 USD (PKR 78k – 180k)">$280 – $650 USD (PKR 78k – 180k)</option>
                      <option value="$650 – $1,500+ USD (Custom Retainer)">$650 – $1,500+ USD (Custom Retainer)</option>
                    </select>
                  </div>
                  <div className="m-field">
                    <label>Reference Links (Optional)</label>
                    <input
                      value={brief.reference_links}
                      onChange={(e) => setBrief({ ...brief, reference_links: e.target.value })}
                      placeholder="Current site, YouTube/IG, or inspiration URL"
                    />
                  </div>
                </div>

                <div className="m-field">
                  <label>Project Goals, Deliverables &amp; Timeline *</label>
                  <textarea
                    required
                    value={brief.project_brief}
                    onChange={(e) => setBrief({ ...brief, project_brief: e.target.value })}
                    placeholder="Tell us what you're launching, target audience, desired style, and deadline…"
                  />
                </div>

                {submitResult && (
                  <div className={submitResult.ok ? 'm-alert-ok' : 'm-alert-err'}>{submitResult.text}</div>
                )}

                <button type="submit" className="m-btn m-btn-crimson" disabled={submitting}>
                  <Send size={15} />
                  {submitting ? 'Sending to MONARCH Cloud…' : 'Submit Project Brief & Request Portal'}
                </button>
              </form>
            </div>
          </div>
        </section>
      </main>

      <footer className="m-footer">
        <div className="m-container m-footer-inner">
          <span>© 2026 MONARCH® STUDIO · Engineered by Adil Chandio (`workadilchandio@gmail.com`)</span>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <a href={PORTFOLIO_URL} target="_blank" rel="noopener noreferrer" style={{ color: 'inherit' }}>
              Portfolio v37 ↗
            </a>
            <button
              type="button"
              onClick={() => onOpenPortal('MON-DEMO26')}
              style={{ background: 'none', border: 0, color: 'inherit', cursor: 'pointer', padding: 0 }}
            >
              Demo Portal
            </button>
            <button
              type="button"
              onClick={onOpenWorkspace}
              style={{ background: 'none', border: 0, color: 'inherit', cursor: 'pointer', padding: 0 }}
            >
              Founder OS
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

/* ============================================================================
   2. LOCKED-PREVIEW -> SAFE CHECKOUT -> INSTANT UNLOCK CLIENT PORTAL (/?portal=CODE)
   ============================================================================ */
export function ClientPortalView({ portalCode, onBackToStudio, onSwitchPortal, onOpenWorkspace }) {
  const [portal, setPortal] = useState(null);
  const [rails, setRails] = useState(DEFAULT_RAILS);
  const [loading, setLoading] = useState(true);
  const [lookupCode, setLookupCode] = useState(portalCode || '');
  const [activeRail, setActiveRail] = useState('foreign_fiat');
  const [proof, setProof] = useState({
    method_label: 'Contra Card / USD ACH',
    currency: 'USD',
    amount_paid: '',
    reference_or_tx_hash: '',
    payer_name_or_wallet: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const fetchPortal = useCallback(async (codeToLoad) => {
    setLoading(true);
    setFeedback(null);
    try {
      if (!supabase) throw new Error('Cloud connection unavailable');
      const [{ data: portalData, error: portalErr }, { data: railData }] = await Promise.all([
        supabase.rpc('get_client_portal', { p_code: codeToLoad }),
        supabase.from('payment_rails_config').select('*').eq('id', 'default').maybeSingle(),
      ]);
      if (portalErr) throw portalErr;
      if (railData) setRails({ ...DEFAULT_RAILS, ...railData });
      setPortal(portalData);
      if (portalData?.found) {
        setProof((prev) => ({
          ...prev,
          amount_paid: prev.amount_paid || `$${Number(portalData.price_usd || 0).toFixed(0)}`,
        }));
      }
    } catch (err) {
      setPortal({ found: false, error: err.message });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setLookupCode(portalCode || '');
    if (portalCode) fetchPortal(portalCode);
  }, [portalCode, fetchPortal]);

  const selectRailTab = (railKey) => {
    setActiveRail(railKey);
    if (railKey === 'pkr_local') {
      setProof((p) => ({
        ...p,
        method_label: 'SadaPay / Raast / Easypaisa',
        currency: 'PKR',
        amount_paid: portal?.price_pkr ? `PKR ${Number(portal.price_pkr).toLocaleString()}` : p.amount_paid,
      }));
    } else if (railKey === 'global_crypto') {
      setProof((p) => ({
        ...p,
        method_label: 'USDC (Solana/Polygon) / USDT',
        currency: 'USDC',
        amount_paid: portal?.price_usd ? `${Number(portal.price_usd).toFixed(2)} USDC` : p.amount_paid,
      }));
    } else {
      setProof((p) => ({
        ...p,
        method_label: 'Contra Card / Named USD ACH',
        currency: 'USD',
        amount_paid: portal?.price_usd ? `$${Number(portal.price_usd).toFixed(2)} USD` : p.amount_paid,
      }));
    }
  };

  const submitPaymentProof = async (e) => {
    e.preventDefault();
    if (!portal?.portal_code) return;
    setSubmitting(true);
    setFeedback(null);
    try {
      const { error } = await supabase.rpc('submit_portal_payment', {
        p_code: portal.portal_code,
        p_payment_rail: activeRail,
        p_method_label: proof.method_label,
        p_currency: proof.currency,
        p_amount_paid: proof.amount_paid,
        p_reference_or_tx_hash: proof.reference_or_tx_hash,
        p_payer_name_or_wallet: proof.payer_name_or_wallet,
        p_receipt_url: '',
        p_notes: proof.notes,
      });
      if (error) throw error;
      setFeedback({
        ok: true,
        text: 'Payment proof logged! MONARCH Studio has been alerted — as soon as your TID / ACH / TxHash is verified, refresh this portal to download your unwatermarked master bundle.',
      });
      setProof((p) => ({ ...p, reference_or_tx_hash: '', notes: '' }));
      await fetchPortal(portal.portal_code);
    } catch (err) {
      setFeedback({ ok: false, text: err.message || 'Could not submit payment reference.' });
    } finally {
      setSubmitting(false);
    }
  };

  const deliverables = Array.isArray(portal?.deliverables) ? portal.deliverables : [];

  return (
    <div className="monarch-public-root">
      <header className="m-nav">
        <div className="m-container m-nav-inner">
          <button type="button" className="m-brand" onClick={onBackToStudio}>
            <span className="m-brand-mark">M</span>
            <span className="m-brand-copy">
              <b>MONARCH® PORTAL</b>
              <small>LOCKED-PREVIEW &amp; SAFE ESCROW VAULT</small>
            </span>
          </button>

          <div className="m-nav-actions">
            <button type="button" className="m-btn m-btn-ghost" onClick={onBackToStudio}>
              <ArrowLeft size={14} /> Studio Home
            </button>
            <button type="button" className="m-btn m-btn-subtle" onClick={onOpenWorkspace}>
              Founder OS
            </button>
          </div>
        </div>
      </header>

      <main className="m-portal-shell">
        <div className="m-container">
          {/* Quick Portal Switcher */}
          <form
            className="m-code-form"
            style={{ maxWidth: 520, marginBottom: 20 }}
            onSubmit={(e) => {
              e.preventDefault();
              if (lookupCode.trim()) onSwitchPortal(lookupCode.trim().toUpperCase());
            }}
          >
            <input
              value={lookupCode}
              onChange={(e) => setLookupCode(e.target.value)}
              placeholder="Switch portal code (MON-DEMO26 / MON-WEB26)"
            />
            <button type="submit" className="m-btn m-btn-ghost">
              Load Portal
            </button>
            <button
              type="button"
              className="m-btn m-btn-subtle"
              onClick={() => fetchPortal(portalCode)}
              title="Refresh verification status"
            >
              <RefreshCw size={14} /> Refresh
            </button>
          </form>

          {loading ? (
            <div className="m-portal-header">
              <div>
                <small style={{ color: '#ff8e96', fontFamily: 'JetBrains Mono, monospace' }}>CONNECTING TO VAULT…</small>
                <h2 style={{ margin: '6px 0 0', fontFamily: 'Syne, sans-serif' }}>Loading {portalCode}…</h2>
              </div>
            </div>
          ) : !portal?.found ? (
            <div className="m-portal-header">
              <div>
                <small style={{ color: '#ff8e96', fontFamily: 'JetBrains Mono, monospace' }}>PORTAL NOT FOUND</small>
                <h2 style={{ margin: '8px 0', fontFamily: 'Syne, sans-serif' }}>
                  No active project found for code “{portalCode}”
                </h2>
                <p style={{ color: 'var(--m-muted)', margin: '0 0 14px' }}>
                  Double-check your invite code or test one of our live interactive demo portals below:
                </p>
                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                  <button type="button" className="m-btn m-btn-crimson" onClick={() => onSwitchPortal('MON-DEMO26')}>
                    Open Film Demo (MON-DEMO26)
                  </button>
                  <button type="button" className="m-btn m-btn-ghost" onClick={() => onSwitchPortal('MON-WEB26')}>
                    Open Website Demo (MON-WEB26)
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* PORTAL HEADER */}
              <div className="m-portal-header">
                <div>
                  <small style={{ fontFamily: 'JetBrains Mono, monospace', color: '#ff8e96' }}>
                    PORTAL CODE: {portal.portal_code} · CLIENT: {portal.client_name}
                    {portal.client_company ? ` (${portal.client_company})` : ''}
                  </small>
                  <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(1.5rem, 3vw, 2.2rem)', margin: '8px 0' }}>
                    {portal.project_title}
                  </h1>
                  <p style={{ color: 'var(--m-muted)', margin: 0, maxWidth: 680 }}>{portal.scope_summary}</p>
                </div>

                <div>
                  <div className={`m-status-pill m-status-${portal.payment_status}`}>
                    {portal.payment_status === 'verified' ? (
                      <>
                        <Unlock size={14} /> PAYMENT VERIFIED · MASTER UNLOCKED
                      </>
                    ) : portal.payment_status === 'proof_submitted' ? (
                      <>
                        <Sparkles size={14} /> PROOF SUBMITTED · STUDIO VERIFYING
                      </>
                    ) : (
                      <>
                        <LockKeyhole size={14} /> LOCKED PREVIEW · AWAITING MILESTONE
                      </>
                    )}
                  </div>
                  <div style={{ marginTop: 10, textAlign: 'right', fontSize: 13, color: 'var(--m-muted)' }}>
                    Milestone: <b style={{ color: 'var(--m-ivory)' }}>${Number(portal.price_usd).toFixed(0)} USD</b> ·{' '}
                    <span>PKR {Number(portal.price_pkr).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* MAIN PORTAL 2-COLUMN LAYOUT */}
              <div className="m-portal-grid">
                {/* LEFT: WATERMARKED PREVIEW STAGE & DELIVERABLES */}
                <section className="m-preview-stage">
                  <div className="m-preview-frame">
                    <div className="m-watermark-ribbon">
                      {portal.watermark_label || 'MONARCH® STUDIO · LOCKED PREVIEW'}
                    </div>
                    <span className="m-kicker" style={{ position: 'relative', zIndex: 2 }}>
                      {portal.preview_type === 'website_staging'
                        ? 'INTERACTIVE WEB STAGING PREVIEW'
                        : 'WATERMARKED 60FPS REVIEW STAGE'}
                    </span>
                    <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: 22, margin: '6px 0 10px', zIndex: 2 }}>
                      {portal.project_title}
                    </h3>
                    <p style={{ color: '#d2cec4', fontSize: 13.5, maxWidth: 460, margin: '0 0 16px', zIndex: 2 }}>
                      {portal.preview_notes}
                    </p>
                    {portal.preview_url && /\.(mp4|webm|mov)(\?|$)/i.test(portal.preview_url) ? (
                      <div style={{ width: '100%', position: 'relative', zIndex: 2 }}>
                        <video
                          src={portal.preview_url}
                          poster="/demo-poster.jpg"
                          controls
                          playsInline
                          preload="metadata"
                          controlsList="nodownload"
                          onContextMenu={(e) => e.preventDefault()}
                          style={{
                            width: '100%',
                            borderRadius: 12,
                            border: '1px solid rgba(210, 31, 43, 0.45)',
                            background: '#050507',
                            display: 'block',
                          }}
                        />
                      </div>
                    ) : (
                      portal.preview_url && (
                        <a
                          href={portal.preview_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="m-btn m-btn-crimson"
                          style={{ position: 'relative', zIndex: 2 }}
                        >
                          Launch Live Preview Stage <ExternalLink size={14} />
                        </a>
                      )
                    )}
                  </div>

                  <div className="m-preview-body">
                    <small
                      style={{
                        display: 'block',
                        fontFamily: 'JetBrains Mono, monospace',
                        fontSize: 11,
                        color: 'var(--m-muted)',
                        marginBottom: 10,
                      }}
                    >
                      INCLUDED MASTER DELIVERABLES (UNLOCKED UPON SETTLEMENT)
                    </small>
                    <ul className="m-deliverable-list">
                      {deliverables.map((d, idx) => (
                        <li key={idx}>
                          <Check size={15} />
                          <span>{d}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </section>

                {/* RIGHT: UNLOCKED VAULT OR 3-RAIL SAFE PAYMENT CHECKOUT */}
                <aside className="m-paywall-card">
                  {portal.payment_status === 'verified' ? (
                    <div className="m-unlocked-vault">
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <ShieldCheck size={24} color="#10b981" />
                        <div>
                          <small style={{ fontFamily: 'JetBrains Mono, monospace', color: '#6ee7b7', fontSize: 11 }}>
                            MILESTONE VERIFIED
                          </small>
                          <h3 style={{ margin: 0, fontFamily: 'Syne, sans-serif', fontSize: 21 }}>
                            Master Deliverables Unlocked
                          </h3>
                        </div>
                      </div>

                      <p style={{ margin: 0, fontSize: 13.5, color: '#d7f7e9' }}>
                        {portal.unlock_notes ||
                          'Your unwatermarked master deliverables and full commercial license are ready below.'}
                      </p>

                      {portal.final_delivery_url && (
                        <a
                          href={portal.final_delivery_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="m-btn m-btn-emerald"
                        >
                          Download Master Bundle (HD / Source) <ArrowUpRight size={16} />
                        </a>
                      )}

                      {portal.secondary_delivery_url && (
                        <a
                          href={portal.secondary_delivery_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="m-btn m-btn-ghost"
                        >
                          Open Cloud Delivery Vault Folder <ExternalLink size={14} />
                        </a>
                      )}
                    </div>
                  ) : (
                    <>
                      <small style={{ fontFamily: 'JetBrains Mono, monospace', color: '#ff8e96', fontSize: 11 }}>
                        {portal.milestone_label}
                      </small>
                      <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 22, margin: '6px 0 6px' }}>
                        Unlock Unwatermarked Master Files
                      </h2>
                      <p style={{ color: 'var(--m-muted)', fontSize: 13.5, margin: 0 }}>
                        Choose your preferred safe settlement rail below (zero P2P risk), then paste your Transaction ID
                        or blockchain TxHash to unlock master files.
                      </p>

                      {portal.latest_submission && (
                        <div className="m-alert-ok" style={{ marginTop: 14 }}>
                          <b>Latest Proof Logged:</b> {portal.latest_submission.method_label} · Ref:{' '}
                          <code>{portal.latest_submission.reference_or_tx_hash}</code> (
                          {portal.latest_submission.status.toUpperCase()})
                        </div>
                      )}

                      {/* 3 SAFE RAILS TABS */}
                      <div className="m-rail-tabs">
                        <button
                          type="button"
                          className={`m-rail-tab ${activeRail === 'foreign_fiat' ? 'active' : ''}`}
                          onClick={() => selectRailTab('foreign_fiat')}
                        >
                          <CreditCard size={13} style={{ verticalAlign: '-2px', marginRight: 5 }} />
                          USD / Card
                        </button>
                        <button
                          type="button"
                          className={`m-rail-tab ${activeRail === 'global_crypto' ? 'active' : ''}`}
                          onClick={() => selectRailTab('global_crypto')}
                        >
                          <Zap size={13} style={{ verticalAlign: '-2px', marginRight: 5 }} />
                          USDC / Crypto
                        </button>
                        <button
                          type="button"
                          className={`m-rail-tab ${activeRail === 'pkr_local' ? 'active' : ''}`}
                          onClick={() => selectRailTab('pkr_local')}
                        >
                          <Wallet size={13} style={{ verticalAlign: '-2px', marginRight: 5 }} />
                          Pakistan PKR
                        </button>
                      </div>

                      {/* RAIL 1: FOREIGN FIAT */}
                      {activeRail === 'foreign_fiat' && (
                        <div style={{ marginBottom: 16 }}>
                          <p style={{ fontSize: 12.5, color: '#d5d1c8', marginTop: 0 }}>{rails.fiat_instructions}</p>
                          {(portal.contra_invoice_url || rails.contra_profile_url) && (
                            <a
                              href={portal.contra_invoice_url || rails.contra_profile_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="m-btn m-btn-ghost"
                              style={{ width: '100%', marginBottom: 10 }}
                            >
                              Pay ${Number(portal.price_usd).toFixed(0)} via Contra (Apple Pay / Card · 0% Fee){' '}
                              <ExternalLink size={14} />
                            </a>
                          )}
                          <CopyRow label="Named USD Account (ACH)" value={`${rails.usd_ach_account_name} · ${rails.usd_ach_provider}`} />
                          <CopyRow label="ACH Routing / Account" value={`${rails.usd_ach_routing_number} / ${rails.usd_ach_account_number}`} />
                          <small style={{ display: 'block', fontSize: 11.5, color: 'var(--m-muted)' }}>
                            {rails.intl_iban_remittance_note}
                          </small>
                        </div>
                      )}

                      {/* RAIL 2: GLOBAL CRYPTO */}
                      {activeRail === 'global_crypto' && (
                        <div style={{ marginBottom: 16 }}>
                          <p style={{ fontSize: 12.5, color: '#d5d1c8', marginTop: 0 }}>{rails.crypto_instructions}</p>
                          <CopyRow label="USDC · Solana Network (Fastest · <$0.01 Fee)" value={rails.usdc_solana_address} />
                          <CopyRow label="USDC · Polygon Network" value={rails.usdc_polygon_address} />
                          <CopyRow label="USDT · Tron (TRC20)" value={rails.usdt_trc20_address} />
                        </div>
                      )}

                      {/* RAIL 3: PAKISTAN LOCAL PKR */}
                      {activeRail === 'pkr_local' && (
                        <div style={{ marginBottom: 16 }}>
                          <p style={{ fontSize: 12.5, color: '#d5d1c8', marginTop: 0 }}>{rails.pkr_instructions}</p>
                          <CopyRow label="Account Title" value={rails.pkr_account_title} />
                          <CopyRow label="SadaPay / Raast IBAN" value={rails.pkr_iban} />
                          <CopyRow label="SadaPay / Easypaisa Number" value={`${rails.pkr_sadapay_number} · ${rails.pkr_easypaisa_number}`} />
                        </div>
                      )}

                      {/* SUBMIT PAYMENT PROOF FORM */}
                      <form onSubmit={submitPaymentProof} style={{ display: 'grid', gap: 11 }}>
                        <div className="m-form-row">
                          <div className="m-field">
                            <label>Amount Sent *</label>
                            <input
                              required
                              value={proof.amount_paid}
                              onChange={(e) => setProof({ ...proof, amount_paid: e.target.value })}
                              placeholder="$240 USD or PKR 67,000"
                            />
                          </div>
                          <div className="m-field">
                            <label>Sender Name / Wallet</label>
                            <input
                              value={proof.payer_name_or_wallet}
                              onChange={(e) => setProof({ ...proof, payer_name_or_wallet: e.target.value })}
                              placeholder="Company or wallet suffix"
                            />
                          </div>
                        </div>

                        <div className="m-field">
                          <label>Transaction ID (TID) / Receipt Ref / Blockchain TxHash *</label>
                          <input
                            required
                            value={proof.reference_or_tx_hash}
                            onChange={(e) => setProof({ ...proof, reference_or_tx_hash: e.target.value })}
                            placeholder="Paste Raast TID, Contra/ACH Ref, or Solana/Polygon TxHash"
                          />
                        </div>

                        {feedback && (
                          <div className={feedback.ok ? 'm-alert-ok' : 'm-alert-err'}>{feedback.text}</div>
                        )}

                        <button type="submit" className="m-btn m-btn-crimson" disabled={submitting}>
                          <ShieldCheck size={15} />
                          {submitting ? 'Submitting Verification…' : 'Submit Payment Proof & Request Unlock'}
                        </button>
                      </form>
                    </>
                  )}
                </aside>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

/* ============================================================================
   3. FOUNDER OS — MOBILE B2B REVENUE CENTER (Tecno Spark Go 1 Optimized)
   ============================================================================ */
export function B2BRevenueCenter({ section, user, notify, onOpenPortal }) {
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  const [inquiries, setInquiries] = useState([]);
  const [portals, setPortals] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [rails, setRails] = useState(DEFAULT_RAILS);
  const [outreach, setOutreach] = useState([]);
  const [newPortal, setNewPortal] = useState({
    portal_code: `MON-${Math.floor(1000 + Math.random() * 9000)}`,
    client_name: '',
    client_email: '',
    client_company: '',
    project_title: '',
    service_type: 'video',
    scope_summary: '',
    price_usd: '240',
    price_pkr: '67000',
    preview_type: 'video_watermarked',
    preview_url: PORTFOLIO_URL,
    final_delivery_url: '',
    contra_invoice_url: '',
  });
  const [newLeadOutreach, setNewLeadOutreach] = useState({
    prospect_name: '',
    company: '',
    email_or_handle: '',
    service_pitched: 'Signature Interactive Website ($450)',
    region: 'US / UK / UAE',
    deal_value_usd: '450',
  });

  const loadAdminData = useCallback(async () => {
    if (!supabase || !user) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const { data: adminFlag } = await supabase.rpc('is_studio_admin');
      setIsAdmin(Boolean(adminFlag));
      if (!adminFlag) {
        setLoading(false);
        return;
      }

      const [inqRes, porRes, subRes, railRes, outRes] = await Promise.all([
        supabase.from('client_inquiries').select('*').order('created_at', { ascending: false }),
        supabase.from('client_portals').select('*').order('created_at', { ascending: false }),
        supabase.from('payment_submissions').select('*').order('created_at', { ascending: false }),
        supabase.from('payment_rails_config').select('*').eq('id', 'default').maybeSingle(),
        supabase.from('outreach_campaigns').select('*').order('created_at', { ascending: false }),
      ]);

      setInquiries(inqRes.data || []);
      setPortals(porRes.data || []);
      setSubmissions(subRes.data || []);
      if (railRes.data) setRails({ ...DEFAULT_RAILS, ...railRes.data });
      setOutreach(outRes.data || []);
    } catch (err) {
      console.error('Admin load error', err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadAdminData();
  }, [loadAdminData]);

  const copyPortalLink = (code) => {
    const link = `${window.location.origin}/?portal=${encodeURIComponent(code)}`;
    navigator.clipboard?.writeText(link);
    notify(`Copied client portal link: ${code}`);
  };

  const convertInquiryToPortal = async (inq) => {
    const code = `MON-${Math.floor(1000 + Math.random() * 9000)}`;
    const isWeb = inq.service_slug?.includes('web');
    const payload = {
      portal_code: code,
      client_name: inq.client_name,
      client_email: inq.client_email,
      client_company: inq.company_or_brand || '',
      project_title: `${inq.company_or_brand || inq.client_name} — ${isWeb ? 'Interactive Website' : 'Brand Film'}`,
      service_type: isWeb ? 'website' : 'video',
      scope_summary: inq.project_brief,
      deliverables: isWeb ? DEFAULT_SERVICES[0].deliverables : DEFAULT_SERVICES[1].deliverables,
      price_usd: isWeb ? 450 : 240,
      price_pkr: isWeb ? 125000 : 67000,
      preview_type: isWeb ? 'website_staging' : 'video_watermarked',
      preview_url: PORTFOLIO_URL,
      final_delivery_url: 'https://drive.google.com/drive/folders/1ULb_LwBLOHM9GdvPXf6KXsp0Do9n0Zr1',
    };
    const { data, error } = await supabase.from('client_portals').insert(payload).select().single();
    if (error) {
      notify(error.message);
      return;
    }
    await supabase
      .from('client_inquiries')
      .update({ status: 'portal_sent', portal_id: data.id })
      .eq('id', inq.id);
    copyPortalLink(code);
    await loadAdminData();
  };

  const createCustomPortal = async (e) => {
    e.preventDefault();
    const isWeb = newPortal.service_type === 'website';
    const { error } = await supabase.from('client_portals').insert({
      ...newPortal,
      portal_code: newPortal.portal_code.trim().toUpperCase(),
      price_usd: Number(newPortal.price_usd || 0),
      price_pkr: Number(newPortal.price_pkr || 0),
      deliverables: isWeb ? DEFAULT_SERVICES[0].deliverables : DEFAULT_SERVICES[1].deliverables,
    });
    if (error) {
      notify(error.message);
      return;
    }
    copyPortalLink(newPortal.portal_code.trim().toUpperCase());
    setNewPortal((p) => ({
      ...p,
      portal_code: `MON-${Math.floor(1000 + Math.random() * 9000)}`,
      client_name: '',
      client_email: '',
      client_company: '',
      project_title: '',
      scope_summary: '',
    }));
    await loadAdminData();
  };

  const togglePortalVerification = async (portalId, approve) => {
    const { error } = await supabase.rpc('admin_verify_portal_payment', {
      p_portal_id: portalId,
      p_approve: approve,
    });
    if (error) {
      notify(error.message);
      return;
    }
    notify(approve ? 'Payment verified! Final HD files unlocked for client.' : 'Portal reset to Locked Preview.');
    await loadAdminData();
  };

  const saveRails = async (e) => {
    e.preventDefault();
    const { error } = await supabase
      .from('payment_rails_config')
      .upsert({ ...rails, id: 'default', updated_at: new Date().toISOString() });
    if (error) {
      notify(error.message);
      return;
    }
    notify('All 3 Payment Rails saved live!');
  };

  const addOutreachRow = async (e) => {
    e.preventDefault();
    if (!newLeadOutreach.prospect_name.trim()) return;
    const { error } = await supabase.from('outreach_campaigns').insert({
      ...newLeadOutreach,
      deal_value_usd: Number(newLeadOutreach.deal_value_usd || 350),
      status: 'sent',
    });
    if (error) {
      notify(error.message);
      return;
    }
    setNewLeadOutreach((p) => ({ ...p, prospect_name: '', company: '', email_or_handle: '' }));
    notify('Outreach prospect logged!');
    await loadAdminData();
  };

  const updateOutreachStatus = async (id, status) => {
    await supabase.from('outreach_campaigns').update({ status }).eq('id', id);
    await loadAdminData();
  };

  if (!user) {
    return (
      <div className="b2b-card">
        <b>Sign in to Founder Cloud OS</b>
        <p style={{ margin: 0 }}>
          Sign in with <code>workadilchandio@gmail.com</code> at <code>/?workspace=1</code> to manage live B2B client
          leads, generate locked-preview portals, edit payment rails, and unlock client files in 1 tap.
        </p>
      </div>
    );
  }

  if (loading) {
    return <div className="b2b-card">Loading MONARCH B2B Cloud Engine…</div>;
  }

  if (!isAdmin) {
    return (
      <div className="b2b-card">
        <b>Founder Admin Access Required</b>
        <p style={{ margin: 0 }}>
          You are signed in as <code>{user.email}</code>. B2B Revenue OS is restricted at the Postgres RLS layer to
          Adil Chandio’s verified founder emails (<code>workadilchandio@gmail.com</code>).
        </p>
      </div>
    );
  }

  const pendingProofs = submissions.filter((s) => s.status === 'pending').length;
  const verifiedRevenueUsd = portals
    .filter((p) => p.payment_status === 'verified')
    .reduce((acc, p) => acc + Number(p.price_usd || 0), 0);

  return (
    <div className="b2b-admin-grid">
      {/* KPI BAR */}
      <div className="b2b-kpi-row">
        <div className="b2b-kpi-card">
          <small>Client Leads</small>
          <b>{inquiries.length}</b>
        </div>
        <div className="b2b-kpi-card">
          <small>Active Portals</small>
          <b>{portals.length}</b>
        </div>
        <div className="b2b-kpi-card">
          <small>Proofs to Verify</small>
          <b>{pendingProofs}</b>
        </div>
        <div className="b2b-kpi-card">
          <small>Unlocked USD</small>
          <b>${verifiedRevenueUsd.toFixed(0)}</b>
        </div>
      </div>

      {/* TAB 1: CLIENT LEADS */}
      {section === 'b2b-leads' && (
        <>
          <div className="b2b-card">
            <div className="b2b-card-top">
              <div>
                <b>24/7 Incoming Client Briefs</b>
                <div style={{ fontSize: 12.5, color: '#64695f' }}>
                  Captured automatically from MONARCH Studio Hub &amp; Portfolio v37
                </div>
              </div>
              <button type="button" className="b2b-btn" onClick={loadAdminData}>
                <RefreshCw size={14} /> Refresh
              </button>
            </div>
          </div>

          {inquiries.length === 0 ? (
            <div className="b2b-card">No client inquiries yet. Test the public form on Studio Home!</div>
          ) : (
            inquiries.map((inq) => (
              <article className="b2b-card" key={inq.id}>
                <div className="b2b-card-top">
                  <div>
                    <b>
                      {inq.client_name} {inq.company_or_brand ? `· ${inq.company_or_brand}` : ''}
                    </b>
                    <div style={{ fontSize: 12.5, color: '#5d6358' }}>
                      {inq.client_email} {inq.whatsapp_or_telegram ? `· ${inq.whatsapp_or_telegram}` : ''}
                    </div>
                  </div>
                  <span className={`b2b-badge ${inq.status}`}>{inq.status.toUpperCase()}</span>
                </div>
                <div style={{ fontSize: 13 }}>
                  <b>Service:</b> {inq.service_slug} · <b>Budget:</b> {inq.budget_tier} · <b>Rail:</b>{' '}
                  {inq.preferred_rail}
                </div>
                <p style={{ margin: 0, fontSize: 13.5, background: '#f6f7f3', padding: 10, borderRadius: 10 }}>
                  {inq.project_brief}
                </p>
                <div className="b2b-action-row">
                  <button type="button" className="b2b-btn primary" onClick={() => convertInquiryToPortal(inq)}>
                    <Plus size={14} /> 1-Tap Create Client Portal &amp; Copy Link
                  </button>
                  <a
                    className="b2b-btn"
                    href={`mailto:${inq.client_email}?subject=${encodeURIComponent(
                      'MONARCH Studio — Your Project Scope & Portal'
                    )}`}
                  >
                    <Mail size={14} /> Reply via Email
                  </a>
                </div>
              </article>
            ))
          )}
        </>
      )}

      {/* TAB 2: CLIENT PORTALS & 1-TAP PAYMENT UNLOCK */}
      {section === 'b2b-portals' && (
        <>
          <form className="b2b-card" onSubmit={createCustomPortal}>
            <b>+ Generate New Locked-Preview Client Portal</b>
            <div className="b2b-form-grid">
              <label>
                Portal Code
                <input
                  required
                  value={newPortal.portal_code}
                  onChange={(e) => setNewPortal({ ...newPortal, portal_code: e.target.value })}
                />
              </label>
              <label>
                Client Name *
                <input
                  required
                  value={newPortal.client_name}
                  onChange={(e) => setNewPortal({ ...newPortal, client_name: e.target.value })}
                  placeholder="Client or Founder Name"
                />
              </label>
              <label>
                Project Title *
                <input
                  required
                  value={newPortal.project_title}
                  onChange={(e) => setNewPortal({ ...newPortal, project_title: e.target.value })}
                  placeholder="e.g. SaaS Launch Website / 3 Reels Pack"
                />
              </label>
              <label>
                Service Type
                <select
                  value={newPortal.service_type}
                  onChange={(e) =>
                    setNewPortal({
                      ...newPortal,
                      service_type: e.target.value,
                      preview_type: e.target.value === 'website' ? 'website_staging' : 'video_watermarked',
                    })
                  }
                >
                  <option value="video">Video / AI Commercial</option>
                  <option value="website">Signature Website</option>
                </select>
              </label>
              <label>
                Price (USD)
                <input
                  type="number"
                  value={newPortal.price_usd}
                  onChange={(e) => setNewPortal({ ...newPortal, price_usd: e.target.value })}
                />
              </label>
              <label>
                Price (PKR)
                <input
                  type="number"
                  value={newPortal.price_pkr}
                  onChange={(e) => setNewPortal({ ...newPortal, price_pkr: e.target.value })}
                />
              </label>
              <label>
                Watermarked Preview / Staging URL
                <input
                  value={newPortal.preview_url}
                  onChange={(e) => setNewPortal({ ...newPortal, preview_url: e.target.value })}
                  placeholder="Staging URL or Watermarked Preview Link"
                />
              </label>
              <label>
                Final Unwatermarked HD / Source URL (Hidden until verified!)
                <input
                  required
                  value={newPortal.final_delivery_url}
                  onChange={(e) => setNewPortal({ ...newPortal, final_delivery_url: e.target.value })}
                  placeholder="Google Drive / Dropbox Final Link"
                />
              </label>
            </div>
            <label className="b2b-stack-label">
              Scope Summary
              <input
                value={newPortal.scope_summary}
                onChange={(e) => setNewPortal({ ...newPortal, scope_summary: e.target.value })}
                placeholder="Deliverables summary shown inside client portal"
              />
            </label>
            <div>
              <button type="submit" className="b2b-btn primary">
                <Plus size={14} /> Create Portal &amp; Copy Client Link
              </button>
            </div>
          </form>

          {portals.map((p) => {
            const portalSubs = submissions.filter((s) => s.portal_id === p.id);
            return (
              <article className="b2b-card" key={p.id}>
                <div className="b2b-card-top">
                  <div>
                    <b>
                      [{p.portal_code}] {p.project_title}
                    </b>
                    <div style={{ fontSize: 12.5, color: '#5d6358' }}>
                      Client: {p.client_name} · ${Number(p.price_usd).toFixed(0)} USD / PKR{' '}
                      {Number(p.price_pkr).toLocaleString()}
                    </div>
                  </div>
                  <span className={`b2b-badge ${p.payment_status}`}>{p.payment_status.toUpperCase()}</span>
                </div>

                {portalSubs.length > 0 && (
                  <div style={{ background: '#f6f7f3', padding: 11, borderRadius: 11, fontSize: 12.5 }}>
                    <b>Submitted Payment Proof:</b> {portalSubs[0].method_label} · Paid: {portalSubs[0].amount_paid} ·
                    TID/TxHash: <code>{portalSubs[0].reference_or_tx_hash}</code>
                  </div>
                )}

                <div className="b2b-action-row">
                  {p.payment_status !== 'verified' ? (
                    <button
                      type="button"
                      className="b2b-btn verify"
                      onClick={() => togglePortalVerification(p.id, true)}
                    >
                      <Unlock size={14} /> 1-Tap Verify &amp; Unlock HD Files
                    </button>
                  ) : (
                    <button type="button" className="b2b-btn" onClick={() => togglePortalVerification(p.id, false)}>
                      <LockKeyhole size={14} /> Re-Lock Portal
                    </button>
                  )}
                  <button type="button" className="b2b-btn" onClick={() => copyPortalLink(p.portal_code)}>
                    <Copy size={14} /> Copy Client Link
                  </button>
                  <button type="button" className="b2b-btn" onClick={() => onOpenPortal(p.portal_code)}>
                    <ExternalLink size={14} /> Open Portal
                  </button>
                </div>
              </article>
            );
          })}
        </>
      )}

      {/* TAB 3: PAYMENT RAILS MOBILE EDITOR */}
      {section === 'b2b-rails' && (
        <form className="b2b-card" onSubmit={saveRails}>
          <b>Zero-P2P Global &amp; Local Payment Rails Configuration</b>
          <div style={{ fontSize: 12.5, color: '#5d6358' }}>
            Update your live SadaPay/Raast IBAN, Contra/nsave/Elevate USD details, and Solana/Polygon USDC wallets from
            your Tecno Spark Go 1 anytime.
          </div>

          <div className="b2b-form-grid">
            <label>
              PKR Account Title
              <input
                value={rails.pkr_account_title}
                onChange={(e) => setRails({ ...rails, pkr_account_title: e.target.value })}
              />
            </label>
            <label>
              SadaPay / Raast IBAN
              <input value={rails.pkr_iban} onChange={(e) => setRails({ ...rails, pkr_iban: e.target.value })} />
            </label>
            <label>
              SadaPay Number
              <input
                value={rails.pkr_sadapay_number}
                onChange={(e) => setRails({ ...rails, pkr_sadapay_number: e.target.value })}
              />
            </label>
            <label>
              Easypaisa Number
              <input
                value={rails.pkr_easypaisa_number}
                onChange={(e) => setRails({ ...rails, pkr_easypaisa_number: e.target.value })}
              />
            </label>
            <label>
              Contra 0%-Fee Profile / Invoice Link
              <input
                value={rails.contra_profile_url}
                onChange={(e) => setRails({ ...rails, contra_profile_url: e.target.value })}
              />
            </label>
            <label>
              USD ACH Provider (nsave / Elevate Pay)
              <input
                value={rails.usd_ach_provider}
                onChange={(e) => setRails({ ...rails, usd_ach_provider: e.target.value })}
              />
            </label>
            <label>
              USD ACH Routing Number
              <input
                value={rails.usd_ach_routing_number}
                onChange={(e) => setRails({ ...rails, usd_ach_routing_number: e.target.value })}
              />
            </label>
            <label>
              USD ACH Account Number
              <input
                value={rails.usd_ach_account_number}
                onChange={(e) => setRails({ ...rails, usd_ach_account_number: e.target.value })}
              />
            </label>
            <label>
              USDC Address (Solana — Recommended)
              <input
                value={rails.usdc_solana_address}
                onChange={(e) => setRails({ ...rails, usdc_solana_address: e.target.value })}
              />
            </label>
            <label>
              USDC Address (Polygon)
              <input
                value={rails.usdc_polygon_address}
                onChange={(e) => setRails({ ...rails, usdc_polygon_address: e.target.value })}
              />
            </label>
            <label>
              USDT Address (Tron TRC20)
              <input
                value={rails.usdt_trc20_address}
                onChange={(e) => setRails({ ...rails, usdt_trc20_address: e.target.value })}
              />
            </label>
          </div>

          <div>
            <button type="submit" className="b2b-btn primary">
              <Check size={14} /> Save Payment Rails Live
            </button>
          </div>
        </form>
      )}

      {/* TAB 4: OUTREACH CRM + PORTFOLIO V37 BRIDGE */}
      {section === 'b2b-outreach' && (
        <>
          <div className="b2b-card">
            <b>Portfolio v37 (`adil-chandio.github.io/portfolio/`) Cloud Bridge</b>
            <div style={{ fontSize: 12.5, color: '#5d6358' }}>
              Paste this single line before <code>&lt;/body&gt;</code> in <code>adil-chandio/portfolio</code> to route
              <code> #contactForm </code> 24/7 into Client Leads + show the floating Client Portal button:
            </div>
            <pre className="b2b-code-snippet">{`<script src="https://monarch-workspace-beryl.vercel.app/portfolio-intake.js" defer></script>`}</pre>
            <div>
              <button
                type="button"
                className="b2b-btn"
                onClick={() => {
                  navigator.clipboard?.writeText(
                    '<script src="https://monarch-workspace-beryl.vercel.app/portfolio-intake.js" defer></script>'
                  );
                  notify('Copied Portfolio Cloud Bridge snippet!');
                }}
              >
                <Copy size={14} /> Copy 1-Line Portfolio Script
              </button>
            </div>
          </div>

          <form className="b2b-card" onSubmit={addOutreachRow}>
            <b>+ Log Daily Outreach Prospect (Phone Tracker)</b>
            <div className="b2b-form-grid">
              <label>
                Prospect / Founder Name *
                <input
                  required
                  value={newLeadOutreach.prospect_name}
                  onChange={(e) => setNewLeadOutreach({ ...newLeadOutreach, prospect_name: e.target.value })}
                  placeholder="e.g. Sam — Founder @ FinFlow"
                />
              </label>
              <label>
                Email or Handle
                <input
                  value={newLeadOutreach.email_or_handle}
                  onChange={(e) => setNewLeadOutreach({ ...newLeadOutreach, email_or_handle: e.target.value })}
                  placeholder="sam@finflow.io / @sam"
                />
              </label>
              <label>
                Service Pitched
                <input
                  value={newLeadOutreach.service_pitched}
                  onChange={(e) => setNewLeadOutreach({ ...newLeadOutreach, service_pitched: e.target.value })}
                />
              </label>
              <label>
                Deal Value (USD)
                <input
                  type="number"
                  value={newLeadOutreach.deal_value_usd}
                  onChange={(e) => setNewLeadOutreach({ ...newLeadOutreach, deal_value_usd: e.target.value })}
                />
              </label>
            </div>
            <div>
              <button type="submit" className="b2b-btn primary">
                <Plus size={14} /> Log Outreach
              </button>
            </div>
          </form>

          {outreach.map((item) => (
            <article className="b2b-card" key={item.id}>
              <div className="b2b-card-top">
                <div>
                  <b>
                    {item.prospect_name} {item.company ? `· ${item.company}` : ''}
                  </b>
                  <div style={{ fontSize: 12.5, color: '#5d6358' }}>
                    {item.service_pitched} · ${Number(item.deal_value_usd || 0).toFixed(0)} · {item.region}
                  </div>
                </div>
                <select
                  value={item.status}
                  onChange={(e) => updateOutreachStatus(item.id, e.target.value)}
                  style={{ padding: '6px 10px', borderRadius: 9, fontWeight: 700 }}
                >
                  {['queued', 'drafted', 'sent', 'replied', 'call_booked', 'won', 'closed'].map((s) => (
                    <option key={s} value={s}>
                      {s.toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
              {item.notes && <div style={{ fontSize: 12.5, color: '#4d5248' }}>{item.notes}</div>}
            </article>
          ))}
        </>
      )}
    </div>
  );
}
