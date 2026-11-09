#!/usr/bin/env python3
# V7 technical QC: delivered MP4, nine web audio gates, rights/social-origin
# ledger, and objective sampled-frame checks against the V6 black/crop failure.
from __future__ import annotations
import hashlib
import json
import os
import subprocess
from pathlib import Path
import cv2
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/monarch-cam/short_ranking_raw_v7'
WORK = Path(os.environ.get('V7_WORK', str(ROOT / 'production/monarch-cam/work/short_ranking_raw_v7'))).resolve()
REVIEW = Path(os.environ.get('V7_REVIEW', str(BASE / 'review'))).resolve()
OUT = ROOT / json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))['deliverable']
SPEC = json.loads((BASE / 'ranking_short_spec.json').read_text(encoding='utf-8'))
SELECTED = json.loads((REVIEW / 'selected_windows.json').read_text(encoding='utf-8'))
NATIVE = json.loads((REVIEW / 'native_audio_ledger.json').read_text(encoding='utf-8'))
AUDIT = json.loads((REVIEW / 'source_audio_audit.json').read_text(encoding='utf-8'))
VISUAL = json.loads((REVIEW / 'visual_v7_qc.json').read_text(encoding='utf-8'))
EDIT = json.loads((REVIEW / 'visual_edit_ledger.json').read_text(encoding='utf-8'))
REVIEW_MANIFEST = json.loads((REVIEW / 'review-manifest.json').read_text(encoding='utf-8'))
CANDIDATE_MANIFEST = json.loads((REVIEW / 'candidates' / 'candidate_review_manifest.json').read_text(encoding='utf-8'))
LOCK = json.loads((REVIEW / 'visual_review_lock.json').read_text(encoding='utf-8'))
VERIFIED = json.loads((REVIEW / 'verified_sources.json').read_text(encoding='utf-8'))
LEDGER = json.loads((REVIEW / 'source_video_ledger.json').read_text(encoding='utf-8'))
META = json.loads((BASE / 'ranking_v7_metadata.json').read_text(encoding='utf-8'))
MANIFEST = json.loads((BASE / 'candidate_sources.json').read_text(encoding='utf-8'))
AUDIO_QC = json.loads((REVIEW / 'audio_qc.json').read_text(encoding='utf-8')) if (REVIEW / 'audio_qc.json').exists() else {}
LAYOUT = json.loads((REVIEW / 'layout_manifest.json').read_text(encoding='utf-8'))
SOCIAL = json.loads((REVIEW / 'social_origin_ledger.json').read_text(encoding='utf-8'))
RENDERER = (BASE / 'render_ranking_visual_v7.py').read_text(encoding='utf-8')


def run(cmd, **kw):
    return subprocess.run(list(map(str, cmd)), text=True, **kw)


def json_safe(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    raise TypeError('Unsupported JSON type: ' + type(obj).__name__)


def frame_metrics(rgb):
    top = rgb[:520]
    bottom = rgb[1450:]
    hook = rgb[180:470, 150:900]
    left = rgb[530:1380, 40:620]
    right = rgb[800:1620, 880:1030]
    center = rgb[600:1400, 250:850]
    def black_fraction(a):
        return float(np.mean(np.all(a < 14, axis=2)))
    return {
        'top_mean': round(float(top.mean()), 3), 'top_std': round(float(top.std()), 3),
        'top_black_fraction': round(black_fraction(top), 5),
        'bottom_mean': round(float(bottom.mean()), 3), 'bottom_std': round(float(bottom.std()), 3),
        'bottom_black_fraction': round(black_fraction(bottom), 5),
        'hook_mean': round(float(hook.mean()), 3), 'hook_std': round(float(hook.std()), 3),
        'hook_black_fraction': round(black_fraction(hook), 5),
        'left_std': round(float(left.std()), 3),
        'right_std': round(float(right.std()), 3),
        'center_std': round(float(center.std()), 3),
    }


def sample_frames():
    cap = cv2.VideoCapture(str(OUT))
    if not cap.isOpened():
        raise RuntimeError('Could not open delivered MP4 for sampled-frame QC')
    samples = [0, 90, 270, 450, 630, 810, 990, 1170, 1350, 1530, 1799]
    rows = []
    for idx in samples:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, raw = cap.read()
        if not ok:
            cap.release()
            raise RuntimeError('Could not read sampled frame ' + str(idx))
        rgb = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
        row = {'frame': idx, **frame_metrics(rgb)}
        rows.append(row)
    cap.release()
    return rows


def no_forbidden_phrases():
    files = [
        BASE / 'ranking_v7_metadata.json',
        BASE / 'RANKING_V7_UPLOAD_METADATA.md',
        REVIEW / 'UPLOAD_METADATA_RANKING_V7.txt',
    ]
    bad = ['@onlymeamro', '2.8M', '6,335', '3x', 'guaranteed viral', 'audience result guaranteed']
    for f in files:
        if not f.exists():
            return False
        text = f.read_text(encoding='utf-8').lower()
        if any(b.lower() in text for b in bad):
            return False
    return True


def main():
    probe = run(['ffprobe', '-v', 'error', '-count_frames', '-show_format', '-show_streams', '-of', 'json', OUT], capture_output=True, check=True)
    p = json.loads(probe.stdout)
    video = next(s for s in p['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in p['streams'] if s['codec_type'] == 'audio')
    wav = WORK / 'decoded_v7.wav'
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', OUT,
         '-map', '0:a:0', '-vn', '-ac', '2', '-ar', '48000', '-c:a', 'pcm_f32le', wav], check=True)
    x, sr = sf.read(wav, dtype='float32', always_2d=True)
    peak = float(np.max(np.abs(x)))
    clipping = int(np.count_nonzero(np.abs(x) >= 0.999))
    click_idx = np.where(np.max(np.abs(np.diff(x, axis=0)), axis=1) > 0.45)[0]
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
    frames = sample_frames()
    guardrail_keys = [
        'full_motion_review', 'native_audio_listening', 'human_approval', 'sign_off',
        'audience_result_promise', 'virality_guarantee', 'perfection_claim', 'retention_claim',
        'hypnosis_claim', 'three_x_claim', 'subscribe_claim', 'like_claim',
        'same_path_replacement', 'factual_superlative_claim', 'third_party_repost',
        'ai_audio', 'generated_calls', 'v3_audio_packages', 'audio_substitution',
        'earshot_claim', 'model_claim', 'sound_design_layers', 'sub_bloom_layers',
        'native_ambience_layers', 'ambience_layers', 'cue_layers',
        'current_trending_claim', 'unverified_social_repost',
    ]
    allowed_licenses = set(MANIFEST['policy']['allowed_license_ids'])
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
        'all_seven_native_audio_continuous': (
            bool(NATIVE.get('all_seven_native_audio_continuous', False))
            and int(NATIVE.get('quiet_full_block_count', -1)) == 0
        ),
        'continuous_native_audio_windows': all(
            bool(a.get('continuous_native_audio', False))
            and int(a.get('quiet_full_block_count', -1)) == 0
            and float(a.get('min_full_block_rms_dbfs', -120.0)) > float(SPEC['audio_policy']['native_audible_segment_rms_dbfs_min'])
            for a in AUDIT['assets'].values()
        ),
        'all_seven_selected_windows_audible': bool(AUDIT['all_seven_selected_windows_audible']),
        'seven_selected_scenes': len(SELECTED['scenes']) == 7 and int(SELECTED['frame_count']) == 1800,
        'seven_rights_cleared_social_origin_files': (
            len(LEDGER) == 7
            and all(e['license'] in allowed_licenses and e['audio_stream_present']
                    and e['no_unverified_reposts'] and e['api_license_verified'] for e in LEDGER)
        ),
        'api_license_verified_per_title': len(VERIFIED['assets']) == 7 and all(v['api_license_verified'] for v in VERIFIED['assets'].values()),
        'social_origin_per_title_verified': bool(SOCIAL['all_social_origin_verified']),
        'no_unverified_reposts': bool(SOCIAL['no_unverified_reposts']),
        'api_restrictions_recorded': bool(SOCIAL['api_restrictions_recorded']),
        'rights_not_legal_opinion': bool(SOCIAL['rights_not_legal_opinion']),
        'cc_by_attribution_recorded': bool(SOCIAL['cc_by_attribution_recorded']),
        'no_current_trending_claim': all(META['flags'].get(k) is False for k in ['current_trending_claim', 'unverified_social_repost']) and bool(SOCIAL['flags']['current_trending_claim'] is False),
        'no_v6_cover_crop': 'cover_crop(' not in RENDERER and bool(VISUAL['no_cover_crop']),
        'no_punchy_zoom': bool(VISUAL['no_punchy_zoom']) and all(float(s['zoom_start']) == 1.0 and float(s['zoom_end']) == 1.0 for s in SELECTED['scenes']),
        'full_frame_preserved': bool(VISUAL['full_frame_preserved'] and VISUAL['sharp_source_frame_uncut'] and VISUAL['source_aspect_preserved']),
        'blurred_background_fill': bool(VISUAL['blurred_background_fill'] and VISUAL['full_screen_blur_background']),
        'no_black_empty_top': all(f['top_black_fraction'] < 0.25 and f['top_mean'] > 15 and f['top_std'] > 5 for f in frames),
        'no_black_bars': all(f['bottom_black_fraction'] < 0.25 and f['top_black_fraction'] < 0.25 for f in frames),
        'no_hook_black_fill': all(f['hook_black_fraction'] < 0.20 and f['hook_std'] > 8 for f in frames),
        'reference_style_hook': bool(LAYOUT['hook']['visible'] and LAYOUT['hook']['centered'] and LAYOUT['hook']['colorful'] and LAYOUT['hook']['two_lines']),
        'colorful_hook_title': bool(VISUAL['colorful_hook_title']),
        'persistent_numbered_list': bool(VISUAL['persistent_numbered_list'] and len(LAYOUT['list']['row_bboxes']) == 7),
        'all_labels_visible_from_start': bool(VISUAL['all_labels_visible_from_start']),
        'left_list_fully_visible': bool(LAYOUT['list']['left_side'] and LAYOUT['list']['fully_visible'] and all(f['left_std'] > 12 for f in frames)),
        'progressive_active_rank_highlight': bool(VISUAL['progressive_labels']),
        'right_platform_ui_present': bool(LAYOUT['right_ui']['platform_ui'] and all(f['right_std'] > 5 for f in frames)),
        'bottom_comment_subscribe_present': bool(LAYOUT['bottom_bar']['comment_bubble'] and LAYOUT['bottom_bar']['subscribe']),
        'app_chrome_present': bool(VISUAL['app_chrome']),
        'no_third_party_handle': bool(VISUAL['no_third_party_handle'] and SPEC['visual']['handle'] == '@Monarch-Cam'),
        'no_fake_engagement_counts': bool(VISUAL['no_fake_engagement_counts'] and not LAYOUT['right_ui']['fake_counts']),
        'no_v6_boxed_list': bool(VISUAL['no_v6_boxed_list']),
        'no_v5_right_panel_or_bottom_burst': bool(VISUAL['no_v5_right_panel'] and VISUAL['no_v5_bottom_rank_burst']),
        'seven_moments_only': bool(VISUAL['seven_moments_only'] and len(EDIT['scenes']) == 7),
        'all_scenes_full_frame': all(bool(s['full_frame_preserved'] and s['no_crop'] and s['no_black_bars']) for s in EDIT['scenes']),
        'safe_area_check_recorded': bool(LAYOUT['flags']['safe_area_check'] and LAYOUT['all_primary_elements_inside_safe_area']),
        'social_origin_check_recorded': bool(LAYOUT['flags']['social_origin_check'] and SPEC['visual']['social_origin_check']),
        'runner_probe_passed': bool(CANDIDATE_MANIFEST['flags']['runner_probe_passed'] and SELECTED['runner_probe_passed']),
        'runner_audio_visual_probe_passed': bool(CANDIDATE_MANIFEST['flags']['runner_audio_visual_probe_passed'] and SELECTED['runner_audio_visual_probe_passed']),
        'runner_visual_motion_probe': bool(CANDIDATE_MANIFEST['flags']['runner_visual_motion_probe'] and SELECTED['runner_visual_motion_probe']),
        'contact_sheets_written': bool(REVIEW_MANIFEST['contact_sheets_written'] and CANDIDATE_MANIFEST['flags']['contact_sheets_written']),
        'selected_window_contact_sheets': len(REVIEW_MANIFEST['selected_window_sheets']) >= 7,
        'candidate_contact_sheets': len(CANDIDATE_MANIFEST['contact_sheets']) >= 7,
        'source_review_recorded': bool(REVIEW_MANIFEST['source_review_recorded'] and CANDIDATE_MANIFEST['flags']['source_review_recorded']),
        'visual_lock_written': bool(LOCK['visual_lock_written'] and REVIEW_MANIFEST['visual_lock_written']),
        'guardrails_false': all(META['flags'].get(k) is False for k in guardrail_keys),
        'no_forbidden_phrases': no_forbidden_phrases(),
        'workflow_failure_absent': not (REVIEW / 'workflow_failure.txt').exists(),
    }
    checks = {k: bool(v) for k, v in checks.items()}
    data = {
        'edition': 'social_origin_v7',
        'file': str(OUT.relative_to(ROOT)), 'sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
        'bytes': OUT.stat().st_size, 'probe': p,
        'decoded_audio_samples': int(len(x)), 'decoded_sample_rate': sr,
        'decoded_sample_peak_dbfs': round(float(20 * np.log10(max(peak, 1e-12))), 4),
        'clipping_runs': clipping, 'click_runs': clicks,
        'click_positions_s': [round(float(i / sr), 4) for i in click_idx[:50]],
        'dc_offset': round(dc, 6), 'channel_correlation': round(corr, 4),
        'mono_fold_loss_db': round(fold, 4),
        'loudnorm_input': {k: lj.get(k) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh')},
        'sampled_frames': frames,
        'checks': checks,
        'flags': {
            'runner_probe_passed': checks['runner_probe_passed'],
            'runner_audio_visual_probe_passed': checks['runner_audio_visual_probe_passed'],
            'runner_visual_motion_probe': checks['runner_visual_motion_probe'],
            'continuous_native_audio_windows': checks['continuous_native_audio_windows'],
            'all_seven_native_audio_continuous': checks['all_seven_native_audio_continuous'],
            'contact_sheets_written': checks['contact_sheets_written'],
            'source_review_recorded': checks['source_review_recorded'],
            'visual_lock_written': checks['visual_lock_written'],
            **{k: False for k in guardrail_keys},
        },
        'passed': all(checks.values()),
        'note': 'Technical, objective and rights-ledger checks only. No human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality or audience result is claimed.',
    }
    (REVIEW / 'technical_qc.json').write_text(json.dumps(data, indent=2, ensure_ascii=False, default=json_safe) + '\n', encoding='utf-8')
    if not data['passed']:
        raise RuntimeError('V7 technical QC failed: ' + json.dumps({k: v for k, v in checks.items() if not v}))
    print('V7 technical QC OK', data['sha256'], len(checks), 'checks', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
