"""Seekable, layered Blender NLA actions for the Quaternius prototype rig.

This is an experiment in sequencing, not a football motion-capture system.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Clip:
    action: str
    start: float
    end: float
    blend: float = 0.25
    loop: bool = False


def validate(clips):
    if not clips:
        raise ValueError('at least one clip required')
    for c in clips:
        if c.start < 0 or c.end <= c.start or c.blend < 0 or 2*c.blend > c.end-c.start:
            raise ValueError(f'invalid clip timing: {c}')


def apply(rig, clips, fps=24):
    """Replace rig animation with overlapping, explicit-time NLA clips.

    Later clips have higher layer priority. Small overlaps allow crossfades.
    Times are seconds on the master timeline, so arbitrary frame seeking works.
    """
    import bpy
    validate(clips)
    actions = []
    for clip in clips:
        action = bpy.data.actions.get(clip.action)
        if action is None:
            raise ValueError(f'missing action {clip.action}')
        if action.frame_range[1] <= action.frame_range[0]:
            raise ValueError(f'empty action {clip.action}')
        actions.append(action)
    rig.animation_data_clear()
    rig.animation_data_create()
    for i, (clip, action) in enumerate(zip(clips, actions)):
        track = rig.animation_data.nla_tracks.new()
        track.name = f'{i:02} {clip.action}'
        start = round(clip.start*fps)
        strip = track.strips.new(clip.action, start, action)
        strip.action_frame_start, strip.action_frame_end = action.frame_range
        length = strip.action_frame_end - strip.action_frame_start
        duration = (clip.end-clip.start)*fps
        if clip.loop:
            strip.repeat = max(1, duration/length)
        else:
            strip.scale = duration/length
        strip.frame_end = clip.end*fps
        strip.extrapolation = 'NOTHING'
        strip.blend_type = 'REPLACE'
        strip.blend_in = strip.blend_out = clip.blend*fps
    return rig
