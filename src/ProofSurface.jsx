import React, { useEffect, useMemo, useState } from 'react';
import { ArrowUpRight, Check, Download, Minus, X } from 'lucide-react';

/**
 * ProofSurface — the Portfolio space's case-study view.
 *
 * It exists to make one rule visible in the product itself: the studio may only publish
 * numbers that came out of a file in this repo. Every figure below is READ at runtime
 * from a JSON that a script generated:
 *
 *   public/showreel/audio_qc.json   <- showreel/audio_qc/gates.py (BS.1770 + delivery gates)
 *   public/showreel/ctr_report.json <- showreel/ctr (thumbnail, title and hook scoring)
 *
 * If a file is missing, the row says "not measured yet". It never falls back to a
 * made-up number, and it never shows a green tick it did not earn.
 */

const DELIVERY = {
  title: 'Proof Over Promises',
  version: 'v4',
  client: 'MON-DEMO26',
  runtime: '36.00 s',
  frames: 2160,
  spec: '1920×1080 · 60.000 fps · H.264 High · 48 kHz stereo AAC',
  download: 'https://drive.google.com/uc?id=1UngK7-tUHYn4kXR9S05ACX9SeJymYpjX&export=download',
  watch: 'https://drive.google.com/file/d/1UngK7-tUHYn4kXR9S05ACX9SeJymYpjX/view',
  repo: 'deliverables/MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4',
  doc: 'docs/MON-DEMO26_v4_Showreel_Delivery.md',
};

const pick = (obj, path) => path.split('.').reduce((a, k) => (a == null ? a : a[k]), obj);

function useJson(url) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  useEffect(() => {
    let live = true;
    fetch(url, { cache: 'no-cache' })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((d) => live && setState({ data: d, error: null, loading: false }))
      .catch((e) => live && setState({ data: null, error: e.message, loading: false }));
    return () => { live = false; };
  }, [url]);
  return state;
}

function State({ ok, label }) {
  const Icon = ok === true ? Check : ok === false ? X : Minus;
  return <span className={`proof-state ${ok === true ? 'ok' : ok === false ? 'bad' : 'unknown'}`}><Icon size={12} />{label}</span>;
}

/** A metric row: label, measured value, what it was measured against. */
function Metric({ label, value, target, ok, note }) {
  return (
    <div className="proof-metric">
      <span className="proof-metric-label">{label}</span>
      <b className="proof-metric-value mono">{value}</b>
      <span className="proof-metric-target mono">{target}</span>
      <State ok={ok} label={ok === true ? 'pass' : ok === false ? 'fail' : 'not measured'} />
      {note && <small>{note}</small>}
    </div>
  );
}

export function ProofSurface({ onOpenPage }) {
  const qc = useJson('/showreel/audio_qc.json');
  const ctr = useJson('/showreel/ctr_report.json');

  const audio = qc.data;
  const measured = audio?.measured || {};
  const checks = audio?.checks || {};
  const thumbs = ctr.data?.thumbnails || {};
  const titles = ctr.data?.titles || [];
  const hooks = ctr.data?.hooks || [];

  const thumbRows = useMemo(
    () => Object.entries(thumbs).sort((a, b) => b[1].score - a[1].score),
    [thumbs],
  );

  return (
    <div className="proof-surface">
      <header className="proof-head">
        <div>
          <div className="mono proof-eyebrow">CASE STUDY · {DELIVERY.client}</div>
          <h1>{DELIVERY.title} <em>{DELIVERY.version}</em></h1>
          <p>{DELIVERY.spec} · {DELIVERY.runtime} · {DELIVERY.frames.toLocaleString()} frames</p>
        </div>
        <div className="proof-actions">
          <a className="button primary" href={DELIVERY.download} target="_blank" rel="noreferrer"><Download size={14} /> Download master</a>
          <a className="button secondary" href={DELIVERY.watch} target="_blank" rel="noreferrer"><ArrowUpRight size={14} /> Watch</a>
        </div>
      </header>

      <section className="proof-panel">
        <div className="proof-panel-head">
          <div>
            <h2>Audio delivery gates</h2>
            <p>BS.1770-4 loudness, true peak, clicks, mono fold, harshness — computed by <code>showreel/audio_qc/gates.py</code>.</p>
          </div>
          <State
            ok={qc.loading ? null : audio ? Boolean(audio.pass) : false}
            label={qc.loading ? 'loading…' : audio ? (audio.pass ? 'all gates pass' : 'gate failure') : 'not measured yet'}
          />
        </div>
        {audio ? (
          <>
            <div className="proof-metrics">
              <Metric label="Integrated loudness" value={`${measured.integrated_lufs} LUFS`} target="−14.0 ± 0.7" ok={checks.loudness_in_range} />
              <Metric label="True peak" value={`${measured.sample_peak_dbfs} dBFS`} target="≤ −1.0" ok={checks.true_peak_ok} />
              <Metric label="Loudness range" value={`${measured.lra_lu} LU`} target="1.0 – 10.0" ok={checks.lra_in_range} note="EBU LRA cannot exceed ~2 LU on a 36 s bed; sectional movement is the real test" />
              <Metric label="Sectional movement" value={`${measured.movement_db} dB`} target="≥ 3.0" ok={checks.has_dynamics} />
              <Metric label="Mono fold loss" value={`${measured.mono_loss_db ?? '—'} dB`} target="> −3.0" ok={checks.mono_compatible} />
              <Metric label="Clipped samples" value={measured.clipped_samples ?? '—'} target="0" ok={checks.no_clipping} />
            </div>
            <div className="proof-checks">
              {Object.entries(checks).map(([k, v]) => <State key={k} ok={Boolean(v)} label={k.replace(/_/g, ' ')} />)}
            </div>
          </>
        ) : (
          <div className="proof-empty">
            {qc.loading ? 'Reading the measurement file…' : `No measurement file at public/showreel/audio_qc.json (${qc.error}). Run the gate step before publishing numbers.`}
          </div>
        )}
      </section>

      <section className="proof-panel">
        <div className="proof-panel-head">
          <div>
            <h2>Click system — thumbnails</h2>
            <p>Scored at 168×94 px, the size a phone actually shows. Generated by <code>showreel/ctr</code>.</p>
          </div>
          <State ok={thumbRows.length ? true : null} label={thumbRows.length ? `${thumbRows.length} archetypes scored` : 'not rendered yet'} />
        </div>
        {thumbRows.length ? (
          <div className="proof-thumbs">
            {thumbRows.map(([name, r]) => (
              <figure className="proof-thumb" key={name}>
                <img src={`/showreel/thumbs/${name}.jpg`} alt={`${name} thumbnail`} loading="lazy" />
                <figcaption>
                  <div className="proof-thumb-top">
                    <b>{name.split('-').slice(1).join(' ')}</b>
                    <span className={`proof-grade grade-${r.grade}`}>{r.score} · {r.grade}</span>
                  </div>
                  <div className="proof-thumb-subs mono">
                    {Object.entries(r.subscores).map(([k, v]) => (
                      <span key={k}>{k.replace('_', ' ')} {Math.round(v)}</span>
                    ))}
                  </div>
                  {r.hard_fails?.length > 0 && <p className="proof-thumb-fail">{r.hard_fails.join(' · ')}</p>}
                </figcaption>
              </figure>
            ))}
          </div>
        ) : (
          <div className="proof-empty">No thumbnails rendered yet. Run <code>python -m showreel.ctr</code>.</div>
        )}
      </section>

      {(titles.length > 0 || hooks.length > 0) && (
        <section className="proof-panel">
          <div className="proof-panel-head"><div><h2>Titles &amp; hooks</h2><p>Each candidate scored before it is used, with hard fails for clickbait and fake urgency.</p></div></div>
          <div className="proof-two">
            <div className="proof-list">
              <div className="proof-list-head mono">TITLES · score · chars</div>
              {titles.slice(0, 5).map((t) => (
                <div className="proof-list-row" key={t.title}>
                  <b>{t.title}</b>
                  <span className="mono">{t.score} {t.grade} · {t.chars}c</span>
                </div>
              ))}
            </div>
            <div className="proof-list">
              <div className="proof-list-head mono">HOOKS · spoken length</div>
              {hooks.map((h) => (
                <div className="proof-list-row" key={h.script}>
                  <b>{h.script}</b>
                  <span className="mono">{h.score} {h.grade} · {h.spoken_seconds}s</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="proof-panel proof-panel-slim">
        <div className="proof-panel-head">
          <div><h2>Reproducibility</h2><p>Nothing here is typed by hand into a slide.</p></div>
          <button className="subtle-link" onClick={() => onOpenPage?.()}>Open the public surface <ArrowUpRight size={14} /></button>
        </div>
        <div className="proof-paths mono">
          <span>{DELIVERY.repo}</span>
          <span>{DELIVERY.doc}</span>
          <span>showreel/audio_qc/gates.py --profile web</span>
          <span>python -m showreel.ctr</span>
        </div>
      </section>
    </div>
  );
}
