"""Act two: the cleaning montage, the oven, the first hospital visit."""
import math

from engine import (INK, H, W, Shot, bg, blink, blob, circle, curve, ellipse,
                    hatch, hexc, keys, lerp, limb, lin, line, poly, rect, seg,
                    set_col, shade, smooth, step_keys, text, tf, vgrad)
from props import (FLOOR, HOSP_FLOOR, HOSP_WALL, LINO, WALL, hospital_bed,
                   room, screen_curtain, star_burst, stars_orbit, table_side,
                   vase, wall_clock, window)
from puppets import (COLIN, colin, colin_face, doctor, duck, lady, person,
                     pose, walk_pose)

KITCHEN_WALL = hexc('d9e2c4')
TILE = hexc('eef0e6')


# --------------------------------------------------------------- the list --

TODO = ['Alphabetise pantry', 'Soak door knobs', 'The final curtain', 'Synchronize clocks',
        'Vacuum', 'Empty lint traps', 'Wash the dishes (again)', 'Newspapers out']


def draw_list(ctx, t, ticks_until=0.0, final=False):
    """Storyboard 20. ticks appear on a schedule; 'The final curtain' is left until last."""
    bg(ctx, hexc('6b5a48'))
    hatch(ctx, 0, 0, W, H, gap=10, alpha=0.08)
    with tf(ctx, 640, 380, -4):
        poly(ctx, [(-420, -330), (420, -330), (430, 340), (-430, 340)], hexc('fbf7ea'))
        for k in range(14):
            line(ctx, [(-400, -170 + k * 46), (400, -170 + k * 46)], lw=1.2, ink=hexc('a9c0d6'), alpha=0.6)
        text(ctx, 'Things to Do', -300, -220, 86, font='Caveat', bold=True)
        text(ctx, 'Date  11/6', 170, -200, 30, font='Caveat')
        order = [4, 6, 7, 0, 1, 3, 5]          # everything except 'The final curtain'
        for i, item in enumerate(TODO):
            y = -150 + i * 46
            rect(ctx, -330, y - 30, 30, 30, None, lw=2.2)
            text(ctx, item, -280, y - 4, 40, font='Caveat', col=hexc('2b3a6a'))
            if i in order:
                k = order.index(i)
                at = ticks_until + k * 0.28
                if final and t >= at:
                    curve(ctx, [(-326, y - 18), (-316, y - 4), (-292, y - 40)], lw=4.5, ink=hexc('2b3a6a'))
        if final:
            # the pen comes in and hovers over the last box... then taps it, unticked
            y = -150 + 2 * 46
            ph = seg(t, ticks_until + 2.2, ticks_until + 2.8)
            px, py = lerp(520, -300, ph), lerp(200, y - 20, ph)
            with tf(ctx, px, py, 35):
                rect(ctx, -8, -170, 16, 160, hexc('34466e'), lw=2.4, r=6)
                poly(ctx, [(-8, -10), (8, -10), (0, 14)], hexc('e8d8b8'), lw=2)
            if t > ticks_until + 3.0:
                # a tiny full-stop of hesitation
                circle(ctx, -315, y - 15, 3, hexc('2b3a6a'), lw=0)


# ------------------------------------------------------------ vignettes ----

def draw_vacuum(ctx, t):
    room(ctx, wall=WALL, floor=FLOOR, horizon=560, paper='stripes')
    # lampshade hanging from the ceiling: the hardest-to-reach place in the house
    line(ctx, [(760, -10), (760, 150)], lw=2)
    poly(ctx, [(700, 150), (820, 150), (860, 230), (660, 230)], hexc('e8b75c'))
    # chair
    rect(ctx, 560, 440, 160, 22, hexc('8b6a45'), r=4)
    for lx in (572, 692):
        rect(ctx, lx, 460, 14, 100, shade(hexc('8b6a45'), 0.85))
    rect(ctx, 690, 300, 18, 150, hexc('8b6a45'), r=4)
    # vacuum canister
    ellipse(ctx, 420, 530, 70, 34, hexc('c43b2d'))
    circle(ctx, 380, 560, 12, hexc('333'))
    circle(ctx, 460, 560, 12, hexc('333'))
    # Colin on tiptoe on the chair, wand up into the lampshade
    tip = 6 * math.sin(t * 7)
    sway = keys(t, [(0, -4), (1.0, 5), (2.0, -5), (3.0, 4)])
    p = pose(x=640, y=440 - 0.85 * 152 - 5 + tip * 0.3, s=0.85, lean=-6 + sway * 0.5, ua_n=160, fa_n=10,
             ua_f=150, fa_f=20, head=-20, look=(0.6, -1), mouth='flat', lid=0.2, th_n=-4, th_f=4)
    person(ctx, p, COLIN)
    hx, hy = p['_near_arm'][2]
    hx, hy = 640 + hx * 0.85, 440 - 0.85 * 152 - 5 + tip * 0.3 + hy * 0.85
    # hose + wand
    limb(ctx, [(hx, hy), (hx + 50, 190)], 10, hexc('9a9a9a'), lw=2.2)
    rect(ctx, hx + 36, 170, 34, 22, hexc('555'), r=4)
    curve(ctx, [(460, 520), (520, 470), (600, 380), (hx - 10, hy + 30), (hx, hy)], lw=8, ink=hexc('3a3a3a'))


def draw_dishes(ctx, t):
    room(ctx, wall=KITCHEN_WALL, floor=LINO, horizon=470)
    for i in range(0, W, 60):
        for j in range(160, 470, 60):
            rect(ctx, i, j, 60, 60, TILE, lw=1, alpha=0.6)
    window(ctx, 470, 60, 340, 200, curtains=hexc('e8c45a'))
    rect(ctx, 200, 330, 880, 40, hexc('d9d2c0'))        # bench
    rect(ctx, 200, 370, 880, 200, hexc('b8b29a'))
    rect(ctx, 520, 330, 240, 30, hexc('9fb6c2'), r=6)   # sink
    # drying rack, getting fuller
    n = int(lin(t, 0, 3.0) * 6) + 3
    for k in range(n):
        ellipse(ctx, 860 + k * 18, 290, 8, 40, (1, 1, 1), lw=2)
    rect(ctx, 840, 320, 200, 10, hexc('9a9a9a'))
    # Colin from behind-ish (side), scrubbing furiously
    scrub = math.sin(t * 22)
    p = pose(x=600, y=420, s=1.0, ua_n=60 + scrub * 8, fa_n=40, ua_f=55 - scrub * 8, fa_f=45,
             mouth='flat', lid=0.3, head=10, look=(0.3, 1))
    person(ctx, p, COLIN)
    # bubbles
    for k in range(6):
        ph = (t * 0.8 + k / 6) % 1
        circle(ctx, 620 + 60 * math.sin(k * 3 + t), 330 - ph * 140, 6 + 8 * ph, (0.9, 0.95, 1), lw=1.6, alpha=1 - ph)


def draw_porch(ctx, t):
    """Storyboard 19: newspapers out on the porch, next to the bird ornament."""
    bg(ctx, hexc('d9cbb2'))
    for row in range(0, 14):
        off = 40 if row % 2 else 0
        for col in range(-1, 18):
            rect(ctx, col * 90 + off, row * 44, 86, 40, hexc('c87a5c') if (row + col) % 3 else hexc('b96a50'), lw=1.8)
    rect(ctx, 120, 0, 240, 520, hexc('5f4434'))        # door
    rect(ctx, 150, 30, 180, 220, hexc('6e5040'), lw=2)
    circle(ctx, 320, 300, 10, hexc('d4b648'))
    rect(ctx, -10, 520, W + 20, 220, hexc('9a9184'))
    # stack of tied newspapers, one more lands on top
    land = seg(t, 0.8, 1.2)
    for k in range(7):
        rect(ctx, 520 + (k % 2) * 6, 500 - k * 26, 300, 26, hexc('ece6d6'), lw=2.2)
    rect(ctx, 520, 318 - (1 - land) * 300, 300, 26, hexc('ece6d6'), lw=2.2)
    line(ctx, [(670, 318), (670, 526)], lw=2.6, ink=hexc('8a6a3a'))
    text(ctx, 'THE GAZETTE', 670, 312 - (1 - land) * 300 + 22, 22, font='Abril Fatface', align='center')
    # a teeter
    tt = seg(t, 1.2, 1.5) - seg(t, 1.5, 1.9)
    # the garden bird ornament (googly-eyed, deadpan)
    with tf(ctx, 1000, 520, tt * 4):
        limb(ctx, [(-14, 0), (-14, -120)], 6, hexc('6a5a4a'), lw=2)
        limb(ctx, [(14, 0), (14, -120)], 6, hexc('6a5a4a'), lw=2)
        blob(ctx, [(-60, -150), (0, -260), (60, -150), (0, -110)], hexc('7a7a72'))
        limb(ctx, [(0, -250), (-4, -340)], 14, hexc('7a7a72'))
        circle(ctx, -14, -350, 14, (1, 1, 1))
        circle(ctx, 14, -350, 14, (1, 1, 1))
        look = 4 * math.sin(t * 2)
        circle(ctx, -14 + look, -348, 6, INK, lw=0)
        circle(ctx, 14 + look, -348, 6, INK, lw=0)
        poly(ctx, [(-6, -336), (6, -336), (0, -280)], hexc('d0a040'))
    if t < 1.0:
        hy = lerp(-200, 260, seg(t, 0.2, 0.8))
        blob(ctx, [(640, hy - 40), (720, hy - 50), (740, hy), (660, hy + 10)], COLIN['skin'])
        limb(ctx, [(720, hy - 40), (900, -200)], 60, COLIN['shirt'])


PANTRY = ['Anchovies', 'Beans', 'Custard', 'Dates', 'Eggs', 'Flour', 'Gherkins']
PANTRY_START = [4, 1, 6, 0, 3, 5, 2]


def draw_pantry(ctx, t):
    bg(ctx, hexc('e9dcc0'))
    hatch(ctx, 0, 0, W, H, gap=20, alpha=0.08)
    for sy in (300, 560):
        rect(ctx, 60, sy, W - 120, 24, hexc('a8754a'), r=3)
    cols = [hexc(c) for c in ('d9483b', '6aa04c', 'f0c43c', '8a5a3a', 'f3efe4', 'e8e2d0', '4f7a3a')]
    for row, sy in enumerate((300, 560)):
        for i in range(7):
            item = i if row == 0 else (i + 3) % 7
            start = PANTRY_START.index(item) if row == 0 else PANTRY_START.index((item + 2) % 7)
            stagger = 0.25 * item + row * 0.4
            k = seg(t, 0.4 + stagger, 0.9 + stagger)
            x = lerp(140 + start * 160, 140 + item * 160, k)
            hop = math.sin(k * math.pi) * 60
            with tf(ctx, x, sy - hop):
                rect(ctx, -54, -170, 108, 170, (0.9, 0.95, 0.97), r=14)
                rect(ctx, -46, -110, 92, 104, cols[item], lw=2, r=8)
                rect(ctx, -58, -194, 116, 30, hexc('c9a24a'), r=6)
                rect(ctx, -44, -96, 88, 56, hexc('fbf7ea'), lw=2)
                text(ctx, PANTRY[item][0], 0, -54, 40, font='Abril Fatface', align='center')


def draw_knobs(ctx, t):
    room(ctx, wall=KITCHEN_WALL, floor=LINO, horizon=600, skirting=False)
    rect(ctx, -10, 500, W + 20, 40, hexc('d9d2c0'))
    rect(ctx, 760, -10, 300, 510, hexc('f2eee4'))       # a door with a hole where the knob was
    circle(ctx, 800, 300, 12, hexc('222'))
    ellipse(ctx, 440, 470, 230, 50, hexc('9fb6c2'))
    ellipse(ctx, 440, 452, 200, 34, hexc('cfe4ea'), lw=2)
    import random
    rnd = random.Random(2)
    for k in range(9):
        bx = 300 + rnd.random() * 280
        by = 440 + rnd.random() * 24
        bb = 3 * math.sin(t * 4 + k)
        circle(ctx, bx, by + bb, 20, hexc('d4b648'))
        circle(ctx, bx - 5, by - 5 + bb, 6, hexc('f6e7a0'), lw=0)
    for k in range(7):
        ph = (t * 0.7 + k / 7) % 1
        circle(ctx, 320 + k * 40, 440 - ph * 120, 5 + 6 * ph, (1, 1, 1), lw=1.6, alpha=1 - ph)
    rect(ctx, 600, 420, 70, 90, hexc('4fa3c9'), r=10)
    text(ctx, 'SUDZ', 635, 470, 20, font='Patrick Hand', align='center')


def draw_clocks(ctx, t):
    room(ctx, wall=hexc('e2d2ae'), floor=FLOOR, horizon=640, paper='diamonds')
    start = [(3, 10), (8, 45), (11, 5), (6, 50), (1, 20)]
    target = (7, 30)
    for i, (hh, mm) in enumerate(start):
        at = 0.6 + i * 0.45
        if t >= at:
            hh, mm = target
        x = 200 + i * 220
        y = 300 + (i % 2) * 80
        jolt = 6 if at <= t < at + 0.1 else 0
        wall_clock(ctx, x, y - jolt, 70 + (i % 3) * 10, hh, mm,
                   rim=hexc(('6b4a33', '3a5f8a', '8a3b34', '4f7a3a', '6b4a33')[i]))


# --------------------------------------------------------------- kitchen ---

def kitchen_bg(ctx, t, vase_state=0.0, water=0.0, win_open=True):
    room(ctx, wall=KITCHEN_WALL, floor=LINO, horizon=560)
    for i in range(0, W, 60):
        for j in range(200, 470, 60):
            rect(ctx, i, j, 60, 60, TILE, lw=1, alpha=0.5)
    # window over the bench (open: the duck's way in)
    window(ctx, 120, 90, 300, 210, curtains=hexc('e8c45a'))
    if win_open:
        poly(ctx, [(120, 90), (60, 70), (60, 320), (120, 300)], hexc('cfe0e8'), alpha=0.8)
    # oven + cupboards
    rect(ctx, 520, 360, 760, 200, hexc('b8b29a'))
    for cx in (900, 1080):
        rect(ctx, cx, 380, 160, 160, None, lw=2)
        circle(ctx, cx + 140, 460, 6, hexc('8a8a8a'))
    rect(ctx, 500, 340, 800, 24, hexc('d9d2c0'))
    rect(ctx, 600, 260, 240, 300, hexc('f2efe6'))     # oven body
    rect(ctx, 600, 230, 240, 40, hexc('e0dcd0'))
    for k in range(4):
        circle(ctx, 640 + k * 52, 300, 11, hexc('333'))
    # table with the vase
    table_side(ctx, 330, 560, w=300, top=hexc('a8754a'))
    if vase_state < 1:
        vase(ctx, 330 + vase_state * 40, 380, 1.2, rot=vase_state * 80)
    else:
        vase(ctx, 400, 368, 1.2, rot=90, flowers=True)
    if water > 0:
        blob(ctx, [(330, 560), (330 + 500 * water, 556), (330 + 560 * water, 572), (300, 576)],
             hexc('9fd0ec'), lw=2, alpha=0.85)


def oven_door(ctx, open_k):
    """Oven door hinged at the bottom; open_k 0..1"""
    with tf(ctx, 610, 540):
        h = 240 * math.cos(open_k * math.pi / 2)
        rect(ctx, 0, -h, 220, max(h, 10), hexc('e6e2d6'), r=4)
        if open_k > 0.6:
            poly(ctx, [(0, 0), (220, 0), (240, 22), (-20, 22)], hexc('e6e2d6'))
            rect(ctx, 80, 6, 60, 8, hexc('8a8a8a'))


def draw_oven_prep(ctx, t):
    """Storyboards 21-23: kneel, open the door, take the grills out, stack them neatly."""
    kitchen_bg(ctx, t)
    rect(ctx, 620, 290, 200, 230, hexc('2a2622'))       # oven cavity
    n_out = int(lin(t, 1.4, 4.0) * 3)
    for k in range(3 - n_out):
        line(ctx, [(630, 340 + k * 60), (810, 340 + k * 60)], lw=4, ink=hexc('9a9a9a'))
    oven_door(ctx, seg(t, 0.4, 1.0))
    # neat stack of racks on the floor
    for k in range(n_out):
        rect(ctx, 960, 590 - k * 8, 200, 6, hexc('9a9a9a'), lw=1.6)
    reach = (math.sin(t * 2.6) + 1) / 2 if t > 1.2 else 0
    p = pose(x=470, y=470, s=1.0, face=1, th_n=8, sh_n=-98, th_f=4, sh_f=-96, lean=28 + reach * 8,
             ua_n=70 + reach * 20, fa_n=10, ua_f=60 + reach * 20, fa_f=14, mouth='flat', lid=0.35,
             look=(0.5, 0.3))
    person(ctx, p, COLIN)


def draw_knob(ctx, t):
    """Storyboard 24: the knob."""
    bg(ctx, hexc('f2efe6'))
    rect(ctx, -10, 120, W + 20, 30, hexc('e0dcd0'))
    line(ctx, [(-10, 420), (W + 10, 420)], lw=3)
    for kx in (380, 760):
        circle(ctx, kx, 300, 90, hexc('e8e4d8'), lw=2)
    ang = keys(t, [(0.6, 0), (1.3, -90)])
    for kx, a in ((380, 0), (760, ang)):
        with tf(ctx, kx, 300, a):
            circle(ctx, 0, 0, 62, hexc('3a3a3a'))
            rect(ctx, -12, -58, 24, 60, hexc('555'), r=6)
            line(ctx, [(0, -50), (0, -20)], lw=4, ink=(1, 1, 1))
    for kx in (380, 760):
        rect(ctx, kx - 30, 180, 60, 16, hexc('cfc9b8'), lw=2, r=4)
    # the hand
    hx = lerp(W + 150, 800, seg(t, 0.0, 0.5))
    with tf(ctx, hx, 330, ang * 0.6):
        blob(ctx, [(-70, -70), (20, -90), (110, -40), (110, 60), (0, 90), (-60, 40)], COLIN['skin'], lw=4)
        limb(ctx, [(-40, -30), (-60, 10)], 26, COLIN['skin'], lw=4)
    limb(ctx, [(hx + 100, 330), (W + 300, 500)], 120, COLIN['shirt'], lw=4)


def colin_in_oven(ctx, t, jerk=0.0):
    """Storyboards 25-26: on hands and knees, head inside the oven (hidden by the door edge)."""
    p = pose(x=470, y=480, s=1.0, th_n=6, sh_n=-96, th_f=2, sh_f=-94, lean=72 + jerk * 10,
             ua_n=110, fa_n=-20, ua_f=104, fa_f=-16, head=20)
    person(ctx, p, COLIN)


def draw_head_in(ctx, t):
    kitchen_bg(ctx, t)
    rect(ctx, 620, 290, 200, 230, hexc('2a2622'))
    oven_door(ctx, 1.0)
    colin_in_oven(ctx, t)
    # the oven's front edge hides his head
    rect(ctx, 600, 260, 22, 300, hexc('f2efe6'))


def draw_head_close(ctx, t):
    """Storyboard 27: cheek on the oven floor. Resigned. Then... a crash, off."""
    bg(ctx, hexc('2a2622'))
    hatch(ctx, 0, 0, W, H, gap=16, alpha=0.2, col=(1, 1, 1))
    rect(ctx, -10, 560, W + 20, 200, hexc('3b3530'))
    for k in range(3):
        line(ctx, [(140 + k * 40, 0), (140 + k * 40, 560)], lw=5, ink=hexc('6a6a6a'))
    crash = t > 2.2
    colin_face(ctx, 700, 458, 1.1, rot=-90, eyes='wide' if crash else 'open',
               look=(1, 0) if crash else (0, 0.4), lid=0 if crash else 0.5, brow=-0.6 if crash else 0.9,
               mouth='o' if crash else 'flat', shirt=False)
    # bright doorway behind him
    poly(ctx, [(1180, -10), (W + 10, -10), (W + 10, H + 10), (1180, H + 10)], hexc('d9e2c4'))


def draw_crash(ctx, t):
    """The duck flies in through the window, takes out the vase. BONK. Out he scrambles,
    slips on the water, and meets the table."""
    vase_state = seg(t, 0.55, 0.85)
    water = seg(t, 0.85, 2.6) * 0.9
    kitchen_bg(ctx, t, vase_state=vase_state, water=water)
    rect(ctx, 620, 290, 200, 230, hexc('2a2622'))
    oven_door(ctx, 1.0)
    # duck: in through the window, clips the vase, lands on the bench, watches
    if t < 0.75:
        dk = lin(t, 0.0, 0.7)
        duck(ctx, lerp(40, 340, dk), lerp(220, 340, dk), 0.8, fly=True, wing=(math.sin(t * 40) + 1) / 2)
    else:
        sk = lin(t, 0.75, 1.3)
        dx, dy = lerp(340, 1000, sk), lerp(340, 340, sk) - math.sin(sk * math.pi) * 120
        if sk < 1:
            duck(ctx, dx, dy, 0.8, fly=True, wing=(math.sin(t * 40) + 1) / 2)
        else:
            duck(ctx, 1000, 340, 0.8, face=-1, look=(1, 0.5), blink=blink(t, 1.7), neck=0.5)
    # Colin
    bonk = 1.0
    backout = seg(t, 1.3, 1.9)
    slip = seg(t, 2.5, 2.8)
    if t < 1.3:
        colin_in_oven(ctx, t, jerk=1 if 1.0 < t < 1.15 else 0)
        rect(ctx, 600, 260, 22, 300, hexc('f2efe6'))
        if 1.0 < t < 1.3:
            star_burst(ctx, 640, 300, 50, alpha=1)
    elif t < 2.5:
        k = backout
        stagger = math.sin(t * 9) * 8
        p = pose(x=lerp(470, 380, k), y=lerp(480, 400, k), s=1.0, face=-1 if k > 0.5 else 1,
                 lean=lerp(72, 0, k) + stagger, th_n=lerp(6, 10, k), sh_n=lerp(-96, -10, k),
                 th_f=lerp(2, -6, k), sh_f=lerp(-94, -4, k), ua_n=lerp(110, 140, k), fa_n=30, ua_f=40, fa_f=40,
                 eyes='wide', mouth='o', bandage=False, head=stagger)
        person(ctx, p, COLIN)
        stars_orbit(ctx, p['x'], p['y'] - 175, t)
    else:
        # feet fly forward, he rotates back around his hips and hits the table edge
        rot = lerp(0, -80, slip)
        fall = seg(t, 2.6, 3.0)
        with tf(ctx, 380, 400 + fall * 70, -rot * 0 - slip * 0):
            p = pose(x=0, y=0, s=1.0, face=-1, lean=lerp(0, -60, slip), th_n=lerp(10, 80, slip),
                     sh_n=-10, th_f=lerp(-6, 70, slip), sh_f=-6, ua_n=lerp(140, 170, slip), fa_n=20,
                     ua_f=lerp(40, 160, slip), fa_f=20, eyes='wide' if t < 3.0 else 'closed', mouth='o')
            person(ctx, p, COLIN)
        if 2.95 < t < 3.25:
            star_burst(ctx, 470, 380, 60, rot=t * 200)


# -------------------------------------------------------------- hospital ---

def ward(ctx, t, window_x=880, curtain=True):
    room(ctx, wall=HOSP_WALL, floor=HOSP_FLOOR, horizon=540)
    rect(ctx, -10, 360, W + 20, 8, shade(HOSP_WALL, 0.85), lw=0)
    window(ctx, window_x, 80, 280, 200, curtains=None)
    if curtain:
        screen_curtain(ctx, 40, 40, 200, 420)


def draw_hospital1(ctx, t):
    """Doctor checks his pupils. Behind, the cleaner with the bedpans: a look, a slow shake."""
    ward(ctx, t)
    # the cleaner crosses behind, stops, looks, shakes her head, moves on
    lx = keys(t, [(0, 1400), (2.4, 980), (6.0, 980), (8.6, 1500)], ease=lambda x: x)
    walking = (t < 2.4) or (t > 6.0)
    shake = 0.0
    if 3.4 < t < 5.4:
        shake = math.sin((t - 3.4) * 2 * math.pi * 1.2) * seg(t, 3.4, 3.7) * (1 - seg(t, 5.0, 5.4))
    bobl = abs(math.sin(t * 6)) * 5 if walking else 0

    def pans(ctx, x, y):
        for k in range(3):
            ellipse(ctx, x, y - 10 - k * 14, 46, 12, hexc('c9ccd0'), lw=2.2)

    lady(ctx, lx, 545 - bobl, 0.6, shake=shake, look=(-1, 0.2) if not walking else (-0.4, 0),
         mouth='tut' if 3.6 < t < 5.2 else 'flat', ua_l=14, fa_l=-62, ua_r=14, fa_r=-62,
         prop_l=None, prop_r=pans, blink=blink(t, 2.9))
    hospital_bed(ctx, 430, 640, 1.0)
    # Colin sits on the edge of the bed, bandaged
    eye = 'wide' if (1.6 < t < 2.0 or 4.0 < t < 4.3) else 'open'
    p = pose(x=440, y=476, s=1.0, face=1, th_n=86, sh_n=-86, th_f=82, sh_f=-82, ua_n=10, fa_n=30,
             ua_f=6, fa_f=30, bandage=True, eyes=eye, mouth='flat', lid=0.25,
             look=(1, 0) if t < 3.2 else (0.2, 0) if t < 6.0 else (1, 0))
    if 2.8 < t < 6.2:
        p['look'] = (1.0, -0.6)           # a glance past the doctor, at the cleaner
        p['head'] = -5
    person(ctx, p, COLIN)
    # the doctor with his little torch
    lean = keys(t, [(0, 10), (1.0, 22), (6.2, 22), (7.0, 8)])

    def torch(ctx, x, y, a):
        with tf(ctx, x, y, -a + 90):
            rect(ctx, -4, -6, 30, 12, hexc('cfcfcf'), lw=2, r=3)
        if 1.0 < t < 6.2 and int(t * 4) % 2 == 0:
            circle(ctx, x - 20, y, 14, (1, 1, 0.7), lw=0, alpha=0.6)

    doctor(ctx, x=720, y=476, s=1.0, face=-1, lean=lean, ua_n=keys(t, [(0, 10), (1.0, 92)]), fa_n=8,
           ua_f=20, fa_f=20, prop_n=torch, mouth='flat', blink=False, look=(0, 0.2))


def build():
    return [
        Shot('b01_list', 2.6, lambda c, t: draw_list(c, t), fade_in=0.6, sfx=[(0.6, 'pen', 0.3)]),
        Shot('b02_vacuum', 3.0, draw_vacuum, sfx=[(0.0, 'vacuum', 0.35)]),
        Shot('b03_dishes', 2.6, draw_dishes, sfx=[(0.0, 'scrub', 0.4)]),
        Shot('b04_porch', 2.4, draw_porch, sfx=[(1.15, 'flump', 0.5)]),
        Shot('b05_pantry', 3.4, draw_pantry, sfx=[(0.5 + k * 0.25, 'clink', 0.25) for k in range(7)]),
        Shot('b06_knobs', 2.2, draw_knobs, sfx=[(0.2, 'bubbles', 0.3)]),
        Shot('b07_clocks', 3.2, draw_clocks, sfx=[(0.6 + k * 0.45, 'tick', 0.5) for k in range(5)]),
        Shot('b08_list2', 5.2, lambda c, t: draw_list(c, t, ticks_until=0.4, final=True),
             sfx=[(0.4 + k * 0.28, 'pen', 0.3) for k in range(7)]),
        Shot('b09_oven', 4.4, draw_oven_prep, sfx=[(0.4, 'creak', 0.4), (1.6, 'rattle', 0.3), (2.8, 'rattle', 0.3)]),
        Shot('b10_knob', 1.8, draw_knob, sfx=[(0.7, 'click', 0.4), (0.9, 'hiss', 0.25)]),
        Shot('b11_headin', 2.4, draw_head_in),
        Shot('b12_close', 3.0, draw_head_close, sfx=[(2.2, 'crash', 0.8)]),
        Shot('b13_crash', 3.9, draw_crash,
             sfx=[(0.0, 'flap', 0.5), (0.6, 'crash', 0.9), (1.05, 'bonk', 0.9), (1.4, 'quack', 0.5),
                  (2.5, 'slip', 0.6), (3.0, 'clonk', 1.0)],
             shake=[(1.0, 0.3, 10), (3.0, 0.4, 16)], fade_out=0.5),
        Shot('b14_black', 1.0, lambda c, t: bg(c, (0, 0, 0)), paper=False),
        Shot('b15_hosp1', 9.0, draw_hospital1, fade_in=0.6, fade_out=0.0, sfx=[(3.6, 'tut', 0.4)]),
    ]
