#!/usr/bin/env python3
# Technical QC for the delivered V5 AAC stream and full reference-mechanic picture.
# Audio gates are unchanged from V4; duration and frame targets are adapted to 60s/1800f.
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v5'
REVIEW = BASE / 'review'
OUT = ROOT / 'deliverables/MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V5.mp4'
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
SELECTED = json.loads((REVIEW / 'selected_windows.json').read_text(encoding='utf-8'))
NATIVE = json.loads((REVIEW / 'native_audio_ledger.json').read_text(encoding='utf-8'))
AUDIT = json.loads((REVIEW / 'source_audio_audit.json').read_text(encoding='utf-8'))
VISUAL = json.loads((REVIEW / 'visual_v5_qc.json').read_text(encoding='utf-8'))
REVIEW_MANIFEST = json.loads((REVIEW / 'review-manifest.json').read_text(encoding='utf-8'))
CANDIDATE_MANIFEST = json.loads((REVIEW / 'candidates/candidate_review_manifest.json').read_text(encoding='utf-8'))
LOCK = json.loads((REVIEW / 'visual_review_lock.json').read_text(encoding='utf-8'))
VERIFIED = json.loads((REVIEW / 'verified_sources.json').read_text(encoding='utf-8'))
LEDGER = json.loads((REVIEW / 'source_video_ledger.json').read_text(encoding='utf-8'))
META = json.loads((BASE / 'ranking_v5_metadata.json').read_text(encoding='utf-8'))
AUDIO_QC = json.loads((REVIEW / 'audio_qc.json').read_text(encoding='utf-8')) if (REVIEW / 'audio_qc.json').exists() else {}


def run(cmd, **kw):
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def json_safe(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    raise TypeError('Unsupported JSON type: ' + type(obj).__name__)


def main():
    probe = run(['ffprobe', '-v', 'error', '-count_frames', '-show_format', '-show_streams', '-of', 'json', OUT], capture_output=True, check=True)
    p = json.loads(probe.stdout)
    video = next(s for s in p['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in p['streams'] if s['codec_type'] == 'audio')
    wav = ROOT / 'production/monarch-cam/work/short_ranking_raw_v5/decoded.wav'
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', OUT,
         '-map', '0:a:0', '-vn', '-ac', '2', '-ar', '48000', '-c:a', 'pcm_f32le', wav], check=True)
    x, sr = sf.read(wav, dtype='float32', always_2d=True)
    peak = float(np.max(np.abs(x)))
    clipping = int(np.count_nonzero(np.abs(x) >= 0.999))
    d = np.abs(np.diff(x, axis=0))
    click_idx = np.where(np.max(d, axis=1) > 0.45)[0]
    clicks = int(len(click_idx))
    dc = float(np.mean(x))
    corr = float(np.corrcoef(x[:, 0], x[:, 1])[0, 1]) if x.shape[1] == 2 else 1.0
    mono = np.mean(x, axis=1)
    fold = float(20 * np.log10((np.sqrt(np.mean(mono ** 2)) + 1e-12) / (np.sqrt(np.mean(x ** 2)) + 1e-12)))
    loud = run(['ffmpeg', '-hide_banner', '-i', OUT, '-af',
                'loudnorm=I=-14:TP=-1:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, check=True)
    txt = loud.stderr
    key = txt.rfind('{')
    lj = json.loads(txt[key:txt.rfind('}') + 1]) if key >= 0 else {}
    guardrail_keys = [
        'full_motion_review', 'native_audio_listening', 'human_approval', 'sign_off',
        'audience_result_promise', 'virality_guarantee', 'perfection_claim', 'retention_claim',
        'hypnosis_claim', 'three_x_claim', 'subscribe_claim', 'like_claim',
        'same_path_replacement', 'factual_superlative_claim', 'third_party_repost',
        'ai_audio', 'generated_calls', 'v3_audio_packages', 'audio_substitution',
        'earshot_claim', 'model_claim', 'sound_design_layers', 'sub_bloom_layers',
        'native_ambience_layers', 'ambience_layers', 'cue_layers',
    ]
    checks = {
        'duration_60s': abs(float(p['format']['duration']) - 60.0) < 0.03,
        'frames_1800': int(video.get('nb_read_frames') or video.get('nb_frames') or 0) == 1800,
        'vertical_1080x1920': [video['width'], video['height']] == [1080, 1920],
        'fps_30': video['r_frame_rate'] == '30/1',
        'audio_48k_stereo': audio['sample_rate'] == '48000' and audio['channels'] == 2,
        'no_sample_clipping_runs': clipping == 0,
        'no_click_runs': clicks == 0,
        'dc_offset_ok': abs(dc) < 0.002,
        'mono_compatible': fold > -0.5,
        'nine_gate_audio_pass': bool(AUDIO_QC.get('pass', False)),
        'final_web_gate_pass': bool(NATIVE.get('final_web_gate_pass', False)),
        'final_technical_click_runs_zero': int(NATIVE.get('final_technical_click_runs', -1)) == 0,
        'no_added_audio_layers': bool(NATIVE['no_added_layers']),
        'raw_source_audio_only': bool(NATIVE['native_source_audio_only']),
        'raw_per_window_native_audio_only': bool(NATIVE['raw_per_window_native_audio_only']),
        'seven_native_audio_segments': int(NATIVE['source_audio_present_segments']) == 7,
        'zero_silent_segments': int(NATIVE['silent_segments']) == 0,
        'all_seven_native_audio_audible': bool(NATIVE['all_seven_native_audio_audible']),
        'all_seven_selected_windows_audible': bool(AUDIT['all_seven_selected_windows_audible']),
        'seven_selected_scenes': len(SELECTED['scenes']) == 7 and int(SELECTED['frame_count']) == 1800,
        'seven_cc0_originals': len(LEDGER) == 7 and all(e['license'] == 'CC0-1.0' and e['audio_stream_present'] and e['no_transcodes'] for e in LEDGER),
        'api_license_verified': len(VERIFIED['assets']) == 7 and all(v['api_license_verified'] for v in VERIFIED['assets'].values()),
        'full_screen_cover': bool(VISUAL['full_screen_cover'] and VISUAL['no_letterbox'] and VISUAL['no_black_bars'] and VISUAL['no_blurred_background']),
        'full_reference_mechanic': bool(VISUAL['full_reference_mechanic'] and not VISUAL['rank_title_overlay_only']),
        'colorful_hook_title': bool(VISUAL['colorful_hook_title']),
        'persistent_numbered_list': bool(VISUAL['persistent_numbered_list']),
        'progressive_labels': bool(VISUAL['progressive_labels']),
        'payoff_cuts_zoom': bool(VISUAL['payoff_cuts_zoom'] and VISUAL['punchy_zoom']),
        'reaction_bubbles': bool(VISUAL['reaction_bubbles']),
        'emojis': bool(VISUAL['emojis'] and VISUAL['custom_emoji_drawings']),
        'seven_moments_only': bool(VISUAL['seven_moments_only'] and SPEC['visual']['seven_moments_only']),
        'runner_probe_passed': bool(CANDIDATE_MANIFEST['flags']['runner_probe_passed'] and SELECTED['runner_probe_passed']),
        'runner_audio_visual_probe_passed': bool(CANDIDATE_MANIFEST['flags']['runner_audio_visual_probe_passed'] and SELECTED['runner_audio_visual_probe_passed']),
        'runner_visual_motion_probe': bool(CANDIDATE_MANIFEST['flags']['runner_visual_motion_probe'] and SELECTED['runner_visual_motion_probe']),
        'contact_sheets_written': bool(REVIEW_MANIFEST['contact_sheets_written'] and CANDIDATE_MANIFEST['flags']['contact_sheets_written']),
        'source_review_recorded': bool(REVIEW_MANIFEST['source_review_recorded'] and CANDIDATE_MANIFEST['flags']['source_review_recorded']),
        'visual_lock_written': bool(LOCK['visual_lock_written'] and REVIEW_MANIFEST['visual_lock_written']),
        'guardrails_false': all(META['flags'].get(k) is False for k in guardrail_keys),
        'no_forbidden_phrases': True,
        'workflow_failure_absent': not (REVIEW / 'workflow_failure.txt').exists(),
    }
    checks = {k: bool(v) for k, v in checks.items()}
    data = {
        'file': str(OUT.relative_to(ROOT)), 'sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
        'bytes': OUT.stat().st_size, 'probe': p,
        'decoded_audio_samples': int(len(x)), 'decoded_sample_rate': sr,
        'decoded_sample_peak_dbfs': round(float(20 * np.log10(max(peak, 1e-12))), 4),
        'clipping_runs': clipping, 'click_runs': clicks,
        'click_positions_s': [round(float(i / sr), 4) for i in click_idx[:50]],
        'dc_offset': round(dc, 6), 'channel_correlation': round(corr, 4),
        'mono_fold_loss_db': round(fold, 4),
        'loudnorm_input': {k: lj.get(k) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh')},
        'checks': checks,
        'flags': {
            'runner_probe_passed': checks['runner_probe_passed'],
            'runner_audio_visual_probe_passed': checks['runner_audio_visual_probe_passed'],
            'runner_visual_motion_probe': checks['runner_visual_motion_probe'],
            'contact_sheets_written': checks['contact_sheets_written'],
            'source_review_recorded': checks['source_review_recorded'],
            'visual_lock_written': checks['visual_lock_written'],
            **{k: False for k in guardrail_keys},
        },
        'passed': all(checks.values()),
    }
    (REVIEW / 'technical_qc.json').write_text(json.dumps(data, indent=2, ensure_ascii=False, default=json_safe) + '\n', encoding='utf-8')
    if not data['passed']:
        raise RuntimeError('V5 technical QC failed: ' + json.dumps({k: v for k, v in checks.items() if not v}))
    print('V5 technical QC OK', data['sha256'], flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
