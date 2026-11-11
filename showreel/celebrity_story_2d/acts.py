"""The edit: every shot of the 60 second film, as data.

Each shot names a painted plate, a framing window into it, a camera move and the
cut-outs that live in it. Cue times come from script.json, which was built from
the recorded narration, so picture is locked to voice.
"""
from __future__ import annotations

import math

import film2d as F

CUE = [0.26, 7.14, 11.91, 17.24, 22.95, 29.81, 34.79, 40.12, 46.31, 50.54]
END = 60.0

# act windows, straight from the cue table
A_DAWN = (0.0, 11.91)
A_KITCHEN = (11.91, 17.24)
A_WINDOW = (17.24, 22.95)
A_STREET = (22.95, 29.81)
A_PRESS = (29.81, 34.79)
A_BARRIER = (34.79, 40.12)
A_REACH = (40.12, 46.31)
A_CAR = (46.31, 50.54)
A_NIGHT = (50.54, END)


def _cap(scene, idx, text):
    scene.caption = text
    return idx


def build():
    H = F.figure('hero_casual.png')
    HS = F.figure('hero_suit.png')
    HW = F.figure('hero_walk.png')
    G = F.figure('girl.png')
    ex = F.sheet_figures('extras.png')
    shots = []

    # ------------------------------------------------------------ 1 dawn
    t0, t1 = A_DAWN
    s = F.Scene('bg_bedroom.png', t0, 5.4, view=(.47, .66, 1.06))
    s.grade = dict(lift=(.008, .012, .028), contrast=1.10, sat=1.02,
                   tint=(.55, .72, 1.0), tint_amount=.055, vignette=.52)
    s.lights = [dict(origin=(430, 300), angle=-12, length=2300, width=230,
                     colour=(.55, .72, 1.0), power=.09)]
    s.add(H, 0.56, 0.985, 0.62, flip=True, depth=1.0,
          motion=dict(dx=-26, dy=-10, dur=5.0, sway_amp=.5, breath_amp=2.0, seed=.3),
          shadow=(.30, 96, 20))
    shots.append(dict(scene=s, cap=_cap(s, 0, 'At five forty in the morning, the city is still asleep. His phone is already awake.'),
                      cam=dict(x=(-18, 30), y=(4, -34), zoom=(1.06, 1.20), handheld=1.0)))

    # the phone on the nightstand, lit by its own screen
    s = F.Scene('bg_bedroom.png', 5.4, 8.6, view=(.20, .80, 2.05))
    s.grade = dict(lift=(.006, .010, .026), contrast=1.12, sat=1.0,
                   tint=(.50, .66, 1.0), tint_amount=.10, vignette=.60)
    phone = F.phone_layer()
    s.add(phone, 0.46, 0.60, 0.30, depth=1.0,
          motion=dict(dx=4, dy=-6, dur=3.0, breath_amp=.8),
          shadow=None)
    s.note = 'insert'
    shots.append(dict(scene=s, cap=_cap(s, 0, 'At five forty in the morning, the city is still asleep. His phone is already awake.'),
                      cam=dict(x=(14, -10), y=(-6, 8), zoom=(1.10, 1.02), handheld=1.2)))

    # ---------------------------------------------------------- 2 calls
    s = F.Scene('bg_bedroom.png', 8.6, 11.91, view=(.47, .62, 1.30))
    s.grade = dict(lift=(.006, .010, .024), contrast=1.12, sat=.98,
                   tint=(.52, .68, 1.0), tint_amount=.08, vignette=.56)
    s.add(H, 0.50, 0.995, 0.70, flip=False, depth=1.0,
          motion=dict(dx=-8, dy=0, dur=3.0, sway_amp=.35, breath_amp=2.4, seed=1.7),
          shadow=(.26, 90, 18))
    shots.append(dict(scene=s, cap=_cap(s, 1, 'Three missed calls. Two shoot days. One hour before the car arrives.'),
                      cam=dict(x=(10, -22), y=(-10, 6), zoom=(1.04, 1.12), handheld=.9)))

    # -------------------------------------------------------- 3 kitchen
    s = F.Scene('bg_kitchen.png', A_KITCHEN[0], 14.6, view=(.50, .58, 1.10))
    s.grade = dict(lift=(.010, .010, .012), contrast=1.06, sat=1.04,
                   tint=(1.0, .93, .80), tint_amount=.06, vignette=.46)
    s.lights = [dict(origin=(880, 260), angle=-24, length=1900, width=180,
                     colour=(1.0, .93, .78), power=.13)]
    s.add(H, 0.42, 0.995, 0.66, flip=False, depth=1.0,
          motion=dict(dx=30, dy=-4, dur=2.6, sway_amp=.4, breath_amp=2.2, seed=.9),
          shadow=(.28, 92, 18))
    shots.append(dict(scene=s, cap=_cap(s, 2, 'So he does what he always does. Coffee first. Everything else can wait a minute.'),
                      cam=dict(x=(-20, 18), y=(8, -8), zoom=(1.05, 1.14), handheld=1.1)))

    # the mug, close, steam catching the window light
    s = F.Scene('bg_kitchen.png', 14.6, 17.24, view=(.36, .60, 2.55))
    s.grade = dict(lift=(.012, .012, .014), contrast=1.05, sat=1.05,
                   tint=(1.0, .92, .78), tint_amount=.09, vignette=.52)
    mug = F.mug_layer()
    s.add(mug, 0.50, 0.74, 0.30, depth=1.0, motion=dict(breath_amp=.6))
    shots.append(dict(scene=s, cap=_cap(s, 2, 'So he does what he always does. Coffee first. Everything else can wait a minute.'),
                      cam=dict(x=(-6, 10), y=(0, -12), zoom=(1.02, 1.10), handheld=1.3)))

    # --------------------------------------------------------- 4 window
    s = F.Scene('bg_bedroom.png', A_WINDOW[0], 20.2, view=(.52, .44, 1.55))
    s.grade = dict(lift=(.010, .014, .026), contrast=1.10, sat=.96,
                   tint=(.62, .76, 1.0), tint_amount=.07, vignette=.50)
    s.lights = [dict(origin=(560, 380), angle=-6, length=2400, width=260,
                     colour=(.70, .80, 1.0), power=.12)]
    s.add(HS, 0.58, 0.99, 0.58, flip=True, depth=1.0,
          motion=dict(dx=-14, dur=2.8, sway_amp=.30, breath_amp=1.8, seed=2.2),
          shadow=(.26, 90, 18), tint=None)
    shots.append(dict(scene=s, cap=_cap(s, 3, 'By eight, the street outside his building has changed. They know the car. They know the windows.'),
                      cam=dict(x=(-12, 14), y=(10, -16), zoom=(1.05, 1.18), handheld=.9)))

    s = F.Scene('bg_street.png', 20.2, 22.95, view=(.50, .52, 1.05))
    s.grade = dict(lift=(.02, .026, .038), contrast=1.02, sat=.90,
                   tint=(.80, .88, 1.0), tint_amount=.10, vignette=.42)
    s.lights = [dict(origin=(300, 120), angle=18, length=2200, width=300,
                     colour=(1.0, .94, .82), power=.08)]
    for i in range(2):
        if i < len(ex):
            s.add(ex[i], 0.30 + 0.36 * i, 0.885, 0.26, depth=.94, blur=2.0, alpha=.9,
                  motion=dict(breath_amp=1.2, seed=i))
    shots.append(dict(scene=s, cap=_cap(s, 3, 'By eight, the street outside his building has changed. They know the car. They know the windows.'),
                      cam=dict(x=(-30, 26), y=(-8, 10), zoom=(1.0, 1.10), handheld=1.2)))

    # --------------------------------------------------------- 5 street
    s = F.Scene('bg_street.png', A_STREET[0], 26.4, view=(.48, .56, 1.18))
    s.grade = dict(lift=(.02, .024, .034), contrast=1.04, sat=1.02,
                   tint=(1.0, .94, .84), tint_amount=.05, vignette=.44)
    s.lights = [dict(origin=(250, 60), angle=22, length=2400, width=330,
                     colour=(1.0, .94, .80), power=.10)]
    s.add(HW, 0.52, 0.99, 0.64, depth=1.0,
          motion=dict(dy=-26, dur=3.4, sway_amp=.3, breath_amp=1.2, step_rate=7.2, step_amp=14),
          shadow=(.34, 120, 22), tint=None)
    shots.append(dict(scene=s, cap=_cap(s, 4, 'The door opens, and the noise hits him all at once. His name, from every direction.'),
                      cam=dict(x=(0, -18), y=(6, -6), zoom=(1.0, 1.16), handheld=1.4)))

    # the press line, seen from behind the crowd, flashes going off
    s = F.Scene('bg_barrier.png', 26.4, A_PRESS[1], view=(.46, .60, 1.12))
    s.grade = dict(lift=(.024, .024, .030), contrast=1.06, sat=1.0,
                   tint=(1.0, .95, .86), tint_amount=.05, vignette=.46)
    s.add(HS, 0.56, 0.95, 0.52, depth=.9, blur=1.4, tint=(.85, .80, .72),
          motion=dict(dx=-10, dur=3.0, breath_amp=1.4))
    for i, (bx, b, bh) in enumerate(((0.13, 7.0, .40), (0.87, 8.5, .44), (0.63, 6.0, .34))):
        if i < len(ex):
            s.add(ex[i], bx, 0.995, bh, depth=1.25, blur=b, alpha=.92,
                  motion=dict(breath_amp=1.0, seed=3 + i))
    shots.append(dict(scene=s, cap=_cap(s, 5, 'Then the flashes start, and the smile is not fake. It is just practiced.'),
                      cam=dict(x=(-30, 16), y=(10, -14), zoom=(1.06, 1.26), handheld=2.0,
                               shake=.6)))

    # -------------------------------------------------------- 6 barrier
    s = F.Scene('bg_barrier.png', A_BARRIER[0], 37.6, view=(.50, .56, 1.06))
    s.grade = dict(lift=(.016, .016, .020), contrast=1.10, sat=.96,
                   tint=(1.0, .92, .80), tint_amount=.06, vignette=.52)
    s.lights = [dict(origin=(120, 160), angle=28, length=2200, width=280,
                     colour=(1.0, .90, .74), power=.10)]
    s.add(G, 0.42, 0.97, 0.42, depth=1.06,
          motion=dict(dx=-18, dy=-4, dur=2.8, breath_amp=2.0, sway_amp=.5, seed=4.1),
          shadow=(.30, 70, 16))
    s.add(HS, 0.68, 0.985, 0.56, flip=True, depth=1.0, blur=.3,
          motion=dict(dx=-34, dy=-6, dur=3.0, breath_amp=1.6, sway_amp=.4, seed=5.2),
          shadow=(.26, 90, 18))
    shots.append(dict(scene=s, cap=_cap(s, 6, 'One girl at the barrier is not holding a phone. She is shaking. He stops walking.'),
                      cam=dict(x=(8, -14), y=(6, -4), zoom=(1.04, 1.16), handheld=1.0)))

    # ---------------------------------------------------------- 7 reach
    s = F.Scene('bg_barrier.png', 37.6, A_REACH[1], view=(.60, .62, 1.34))
    s.grade = dict(lift=(.014, .014, .018), contrast=1.12, sat=.94,
                   tint=(1.0, .90, .78), tint_amount=.08, vignette=.56)
    s.lights = [dict(origin=(940, 240), angle=-30, length=2000, width=240,
                     colour=(1.0, .86, .68), power=.14)]
    s.add(G, 0.34, 0.99, 0.50, depth=1.06,
          motion=dict(dx=26, dy=-10, dur=3.2, sway_amp=.6, breath_amp=2.6, seed=6.3),
          shadow=(.30, 76, 16))
    s.add(HS, 0.70, 0.995, 0.68, flip=True, depth=1.0,
          motion=dict(dx=-96, dur=3.4, breath_amp=1.8, sway_amp=.5, seed=7.1),
          shadow=(.26, 92, 18))
    shots.append(dict(scene=s, cap=_cap(s, 7, 'He reaches over the barrier, and for a second he is not a headline. He is just someone who listened.'),
                      cam=dict(x=(14, -6), y=(-4, 6), zoom=(1.02, 1.12), handheld=.8)))

    # ------------------------------------------------------------ 8 car
    s = F.Scene('bg_street.png', A_CAR[0], A_CAR[1], view=(.54, .58, 1.24))
    s.grade = dict(lift=(.014, .018, .028), contrast=1.06, sat=.86,
                   tint=(.72, .82, 1.0), tint_amount=.12, vignette=.54)
    s.add(HS, 0.44, 0.985, 0.54, flip=False, depth=1.0, blur=1.0,
          tint=(.55, .58, .66),
          motion=dict(dx=24, dur=3.6, breath_amp=1.0, seed=8.4),
          shadow=(.30, 90, 18))
    shots.append(dict(scene=s, cap=_cap(s, 8, 'Then the car door closes, and the street goes quiet again.'),
                      cam=dict(x=(-26, -6), y=(0, -12), zoom=(1.06, 1.22), handheld=.7)))

    # ---------------------------------------------------------- 9 night
    s = F.Scene('bg_night.png', A_NIGHT[0], 55.6, view=(.50, .50, 1.04))
    s.grade = dict(lift=(.004, .006, .014), contrast=1.14, sat=.92,
                   tint=(.50, .64, 1.0), tint_amount=.10, vignette=.62)
    s.add(HS, 0.40, 0.985, 0.56, flip=True, depth=1.0,
          motion=dict(dx=-10, dy=2, dur=4.0, sway_amp=.26, breath_amp=1.6, seed=9.1),
          shadow=(.34, 100, 20))
    shots.append(dict(scene=s, cap=_cap(s, 9, 'Hours later, the apartment is dark. He stands at the glass, the phone face down behind him. Nobody is watching.'),
                      cam=dict(x=(-8, 8), y=(4, -6), zoom=(1.0, 1.10), handheld=.6)))

    # the room, empty, the city still going
    s = F.Scene('bg_night.png', 55.6, END, view=(.46, .46, 1.30))
    s.grade = dict(lift=(.004, .005, .012), contrast=1.16, sat=.90,
                   tint=(.48, .62, 1.0), tint_amount=.12, vignette=.66)
    s.add(HS, 0.56, 0.96, 0.44, flip=True, depth=1.0, blur=1.2,
          tint=(.42, .48, .60),
          motion=dict(breath_amp=1.0, seed=10.2))
    shots.append(dict(scene=s, cap=_cap(s, 9, 'Hours later, the apartment is dark. He stands at the glass, the phone face down behind him. Nobody is watching.'),
                      cam=dict(x=(6, -20), y=(-4, 12), zoom=(1.22, 1.08), handheld=.5)))
    return shots
