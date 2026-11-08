"""Act four: the hunt for the duck, the stairs, and a happy ending of sorts."""
import math

from engine import (INK, H, W, Shot, bg, blink, blob, circle, curve, ellipse,
                    hatch, hexc, keys, lerp, limb, lin, line, poly, rect, seg,
                    set_col, shade, smooth, text, tf, vgrad)
from props import (FLOOR, HOSP_FLOOR, HOSP_WALL, WALL, heart, hospital_bed,
                   room, star_burst, stars_orbit, thought_hearts, window)
from puppets import (COLIN, LADY, colin_face, curls, duck, duck_head_big,
                     head_profile, lady, person, pose, walk_pose)
from act2 import ward

HALL_WALL = hexc('d8c7a3')
STAIR = hexc('9b6b45')


# ------------------------------------------------------------- staircase ---

STEP_W, STEP_H = 62, 34
STAIR_X0, STAIR_Y0 = 330, 640       # bottom step front edge
N_STEPS = 8


def stair_xy(k):
    """Top-front corner of step k (0 = floor)."""
    return STAIR_X0 + k * STEP_W, STAIR_Y0 - k * STEP_H


def staircase(ctx, rope=True, rope_swing=0.0, rope_grab=None):
    room(ctx, wall=HALL_WALL, floor=FLOOR, horizon=640, paper='stripes')
    # landing + upper floor
    tx, ty = stair_xy(N_STEPS)
    rect(ctx, tx, ty, W - tx + 20, 24, STAIR)
    rect(ctx, tx, ty + 24, W - tx + 20, H, shade(HALL_WALL, 0.9), lw=0)
    # a picture on the upper wall
    rect(ctx, 1080, 90, 120, 90, hexc('8b6a45'))
    rect(ctx, 1094, 104, 92, 62, hexc('a9c7dd'), lw=2)
    poly(ctx, [(1094, 166), (1130, 130), (1160, 150), (1186, 120), (1186, 166)], hexc('6aa04c'), lw=1.6)
    # stringer + steps
    poly(ctx, [(STAIR_X0 - 10, STAIR_Y0 + 10), (tx, ty), (tx, ty + 60), (STAIR_X0 + 40, STAIR_Y0 + 10)], shade(STAIR, 0.8))
    for k in range(N_STEPS):
        x, y = stair_xy(k)
        rect(ctx, x, y - STEP_H, STEP_W + 6, STEP_H, STAIR, lw=2.4)
        line(ctx, [(x, y - STEP_H), (x + STEP_W + 6, y - STEP_H)], lw=4, ink=shade(STAIR, 0.7))
    # banister (in front)
    bx0, by0 = stair_xy(0)
    for k in range(1, N_STEPS, 1):
        x, y = stair_xy(k)
        limb(ctx, [(x + 20, y - STEP_H), (x + 20, y - STEP_H - 150)], 7, shade(STAIR, 1.1), lw=2)
    limb(ctx, [(bx0 - 20, by0 - 190), (tx + 20, ty - 190)], 16, shade(STAIR, 0.9))
    rect(ctx, bx0 - 34, by0 - 230, 28, 240, shade(STAIR, 0.9), r=4)     # newel post
    circle(ctx, bx0 - 20, by0 - 236, 18, shade(STAIR, 0.9))
    # landing balustrade
    for k in range(6):
        limb(ctx, [(tx + 30 + k * 60, ty), (tx + 30 + k * 60, ty - 150)], 7, shade(STAIR, 1.1), lw=2)
    limb(ctx, [(tx + 10, ty - 150), (W + 20, ty - 150)], 16, shade(STAIR, 0.9))
    if rope:
        # a rope tied off on the landing rail, dangling into the stairwell
        sw = rope_swing
        top = (tx + 40, ty - 150)
        bot = (tx + 40 + sw * 30, ty + 120)
        if rope_grab:
            bot = rope_grab
        mid = ((top[0] + bot[0]) / 2 + sw * 10, (top[1] + bot[1]) / 2)
        curve(ctx, [top, mid, bot], lw=7, ink=INK)
        curve(ctx, [top, mid, bot], lw=4, ink=hexc('c9a86a'))
        circle(ctx, top[0], top[1], 9, hexc('c9a86a'), lw=2)


def draw_stairs_intro(ctx, t):
    """He looks up at the rope... then thinks better of it. First: find that duck."""
    staircase(ctx)
    look_up = seg(t, 0.4, 1.0)
    think = t > 2.0
    p = pose(x=200, y=640 - 152, s=1.0, face=1, head=-14 * look_up if t < 2.2 else 0,
             look=(0.6, -1) if t < 2.2 else ((-1, 0) if t < 2.8 else (1, 0)),
             eyes='open', lid=0.3 if t < 2.0 else 0.5, brow=0.9 if t < 2.0 else -0.6,
             mouth='frown' if t < 2.0 else 'flat')
    if t > 3.2:
        # out comes the feather duster, held up like a sword
        k = seg(t, 3.2, 3.6)
        p['ua_n'] = lerp(8, 120, k)
        p['fa_n'] = lerp(-14, 30, k)

        def duster(ctx, x, y, a):
            with tf(ctx, x, y, 180 - a - 30):
                limb(ctx, [(0, 0), (0, -110)], 6, hexc('6b4a33'), lw=2)
                for j in range(9):
                    ang = -60 + j * 15
                    limb(ctx, [(0, -110), (40 * math.sin(math.radians(ang)), -110 - 50 * math.cos(math.radians(ang)))],
                         14, hexc('e88aa0') if j % 2 else hexc('f0c43c'), lw=1.8)
        p['prop_n'] = duster
    person(ctx, p, COLIN)


def duster_prop(ctx, x, y, a):
    with tf(ctx, x, y, 180 - a - 30):
        limb(ctx, [(0, 0), (0, -90)], 6, hexc('6b4a33'), lw=2)
        for j in range(9):
            ang = -60 + j * 15
            limb(ctx, [(0, -90), (34 * math.sin(math.radians(ang)), -90 - 42 * math.cos(math.radians(ang)))],
                 12, hexc('e88aa0') if j % 2 else hexc('f0c43c'), lw=1.8)


# ---------------------------------------------------------- the search -----

def draw_under_bed(ctx, t):
    """He checks under the bed. Behind him, the duck strolls across the room."""
    room(ctx, wall=hexc('c9d6e0'), floor=hexc('8b7a6a'), horizon=520, paper='diamonds')
    window(ctx, 200, 90, 260, 200, curtains=hexc('6a8fb5'))
    rect(ctx, 960, 180, 240, 340, hexc('8b6a45'))       # wardrobe
    line(ctx, [(1080, 190), (1080, 510)], lw=2)
    # duck crosses at the back of the room, vanishing behind the bed
    dx = keys(t, [(0.4, 60), (3.4, 1240)], ease=lambda x: x)
    if 0.4 < t < 3.4:
        duck(ctx, dx, 520, 0.8, face=1, walk=t * 2.2, look=(0.4, 0.4))
    # bed
    rect(ctx, 520, 380, 460, 120, hexc('e8e2d0'), r=10)
    rect(ctx, 520, 360, 460, 60, hexc('b5534a'), r=14)
    rect(ctx, 960, 300, 26, 260, hexc('6b4a33'), r=6)
    rect(ctx, 510, 330, 26, 230, hexc('6b4a33'), r=6)
    rect(ctx, 520, 500, 460, 30, hexc('3a2a22'), lw=0)  # dark gap under the bed
    # Colin on his knees, peering under, duster poking about
    poke = math.sin(t * 6) * 6
    p = pose(x=440, y=500, s=1.0, face=1, th_n=8, sh_n=-98, th_f=4, sh_f=-96, lean=80, head=30,
             ua_n=100 + poke, fa_n=-10, ua_f=95, fa_f=-10, look=(1, 0), eyes='narrow' if False else 'open',
             lid=0.4, prop_n=duster_prop)
    person(ctx, p, COLIN)


def draw_umbrella(ctx, t):
    """The umbrella stand: he peers in. The duck peeks out from behind the coats, ducks back."""
    room(ctx, wall=HALL_WALL, floor=FLOOR, horizon=560, paper='stripes')
    # the duck's head peeks out from behind the coats when his back is turned
    peek = seg(t, 1.0, 1.3) * (1 - seg(t, 2.1, 2.3))
    duck(ctx, 920 - 140 * peek, 470, 1.0, face=-1, neck=0.9, look=(1, 0), blink=blink(t, 1.3))
    # coat stand with coats
    limb(ctx, [(900, 560), (900, 140)], 12, hexc('6b4a33'))
    for (cx, c) in ((860, hexc('5a6a4a')), (940, hexc('8a3b34'))):
        blob(ctx, [(cx - 50, 170), (cx + 50, 170), (cx + 70, 420), (cx - 70, 420)], c, tension=0.4)
    # umbrella stand
    rect(ctx, 420, 420, 120, 140, hexc('4a5f7a'), r=10)
    limb(ctx, [(450, 420), (440, 250)], 6, hexc('2a2a2e'), lw=2)
    curve(ctx, [(440, 250), (430, 228), (412, 236)], lw=6)
    # Colin bending to peer into the stand, then whipping round at 2.2 (too late)
    turn = t > 2.2
    p = pose(x=330, y=560 - 152, s=1.0, face=-1 if turn else 1, lean=40 if not turn else 0,
             head=30 if not turn else 0, ua_n=60, fa_n=20, ua_f=40, fa_f=10,
             look=(1, 1) if not turn else (1, 0), eyes='wide' if turn else 'open', mouth='flat',
             prop_f=duster_prop)
    if turn:
        p['face'] = 1
        p['look'] = (1, 0)
        p['eyes'] = 'narrow'
        p['eyes'] = 'open'
        p['brow'] = -0.8
    person(ctx, p, COLIN)


def draw_behind(ctx, t):
    """The classic: he spins round, the duck stays exactly behind him."""
    room(ctx, wall=hexc('e2d2ae'), floor=FLOOR, horizon=560, paper='diamonds')
    rect(ctx, 820, 330, 180, 230, hexc('7a8f6a'), r=18)       # armchair
    rect(ctx, 800, 300, 40, 240, hexc('6a7f5a'), r=14)
    rect(ctx, 980, 300, 40, 240, hexc('6a7f5a'), r=14)
    line(ctx, [(320, -10), (320, 120)], lw=2)
    poly(ctx, [(270, 120), (370, 120), (400, 190), (240, 190)], hexc('e8b75c'))
    # Colin faces right, then spins left (1.2), right (2.4), left (3.4)
    face = 1
    for tt in (1.2, 2.4, 3.4):
        if t > tt:
            face = -face
    cx = 560
    p = pose(x=cx, y=560 - 152, s=1.0, face=face, ua_n=100, fa_n=40, prop_n=duster_prop,
             eyes='open', lid=0.0, brow=-0.6, look=(1, 0), mouth='flat',
             head=6 * math.sin(t * 6))
    person(ctx, p, COLIN)
    # the duck is always on the side he's not facing, sliding round with him
    side = -face
    dx = cx + side * 150
    hop = 0
    for tt in (1.2, 2.4, 3.4):
        if tt < t < tt + 0.25:
            k = (t - tt) / 0.25
            dx = lerp(cx - side * 150, cx + side * 150, k)
            hop = math.sin(k * math.pi) * 40
    duck(ctx, dx, 560 - hop, 0.8, face=face, look=(1, 0), blink=blink(t, 1.6), eyes='content' if t > 3.6 else 'open')


# --------------------------------------------------------------- the fall --

def draw_climb(ctx, t):
    """Convinced the duck has gone, he climbs, and leans over the banister for the rope."""
    staircase(ctx, rope_swing=0.4 * math.sin(t * 1.5))
    k_step = lin(t, 0.2, 2.2) * 5
    k = int(k_step)
    x, y = stair_xy(k)
    stepping = (k_step - k)
    p = walk_pose(t * 1.6, face=1, s=1.0) if t < 2.2 else pose(face=1, s=1.0)
    p['x'] = x + 30 + stepping * STEP_W
    p['y'] = y - STEP_H - 152 - stepping * STEP_H
    if t > 2.2:
        lean = seg(t, 2.3, 2.9)
        p.update(lean=18 * lean, ua_n=lerp(8, 120, lean), fa_n=0, look=(1, -0.6), head=-10 * lean,
                 mouth='flat', lid=0.4)
    person(ctx, p, COLIN)


def draw_grab(ctx, t):
    """Storyboards 37-38: the hand reaches... and closes on the rope."""
    bg(ctx, HALL_WALL)
    for i in range(0, W, 48):
        rect(ctx, i, 0, 20, H, shade(HALL_WALL, 0.95), lw=0)
    limb(ctx, [(560, -40), (560, H + 40)], 22, INK, lw=0)
    limb(ctx, [(560, -40), (560, H + 40)], 16, hexc('c9a86a'), lw=0)
    for k in range(10):
        line(ctx, [(552, k * 80), (568, k * 80 + 20)], lw=2, alpha=0.5)
    reach = keys(t, [(0, 0), (1.2, 1)])
    grab = t > 1.3
    hx, hy = lerp(-100, 520, reach), 330
    limb(ctx, [(-300, 420), (hx - 80, hy + 20)], 90, COLIN['shirt'], lw=4)
    rect(ctx, hx - 120, hy - 30, 40, 90, shade(COLIN['shirt'], 0.9), lw=3, r=8)
    with tf(ctx, hx, hy):
        if not grab:
            blob(ctx, [(-80, -30), (0, -50), (40, -40), (40, 40), (-60, 50)], COLIN['skin'], lw=4)
            for f in range(4):
                limb(ctx, [(30, -36 + f * 22), (90, -46 + f * 26)], 18, COLIN['skin'], lw=4)
        else:
            blob(ctx, [(-80, -30), (0, -50), (60, -40), (70, 40), (-60, 50)], COLIN['skin'], lw=4)
            for f in range(4):
                limb(ctx, [(46, -30 + f * 20), (62, -24 + f * 20)], 18, COLIN['skin'], lw=4)


def draw_duck_top(ctx, t):
    """Storyboard 40: at the top of the stairs, the duck. Just... looking."""
    bg(ctx, shade(HALL_WALL, 0.92))
    for i in range(0, W, 48):
        rect(ctx, i, 0, 20, H, shade(HALL_WALL, 0.88), lw=0)
    duck_head_big(ctx, 820, 330, 1.25, look=(-1, 0.3), blink=(1.2 < t < 1.32))


def draw_tumble(ctx, t):
    """He sees her. Windmills. Down he goes, step by step, into a heap."""
    staircase(ctx, rope_swing=math.sin(t * 6) * (1 - seg(t, 0, 3)))
    tx, ty = stair_xy(N_STEPS)
    duck(ctx, tx + 90, ty, 0.9, face=-1, look=(1, 0.6), blink=blink(t, 2.0),
         neck=0.6 + 0.3 * seg(t, 1.5, 2.2), tilt=10 * seg(t, 1.5, 2.2))
    x6, y6 = stair_xy(5)
    if t < 0.8:
        # windmilling at the top of his balance
        w = t * 22
        p = pose(x=x6 + 30, y=y6 - STEP_H - 152, s=1.0, face=1, lean=-14 + 6 * math.sin(w),
                 ua_n=150 + 40 * math.sin(w), fa_n=10, ua_f=150 + 40 * math.sin(w + 2), fa_f=10,
                 eyes='wide', mouth='o', look=(1, -1), th_n=10 * math.sin(w), th_f=-10 * math.sin(w))
        person(ctx, p, COLIN)
    elif t < 2.6:
        # tumbling: a spinning bundle that bounces down the steps
        k = lin(t, 0.8, 2.6)
        pos = 5 * (1 - k)
        i = int(pos)
        x, y = stair_xy(i)
        bounce = abs(math.sin((pos - i) * math.pi)) * 50
        rot = -k * 900
        with tf(ctx, x + 30, y - STEP_H - 70 - bounce, rot):
            p = pose(x=0, y=0, s=0.9, face=1, lean=60, th_n=110, sh_n=-130, th_f=100, sh_f=-120,
                     ua_n=160, fa_n=60, ua_f=140, fa_f=80, eyes='wide', mouth='o', head=30)
            person(ctx, p, COLIN)
        if int(t * 8) % 2 == 0:
            star_burst(ctx, x + 60, y - STEP_H - 20, 22, rot=t * 300)
    else:
        # the heap at the bottom
        bx, by = stair_xy(0)
        p = pose(x=bx - 160, y=by - 30, s=1.0, face=-1, lean=-80, th_n=140, sh_n=-60, th_f=170, sh_f=-30,
                 ua_n=200, fa_n=20, ua_f=-60, fa_f=-40, eyes='closed', mouth='wobble', head=-30)
        with tf(ctx, 0, 0):
            person(ctx, p, COLIN)
        stars_orbit(ctx, bx - 40, by - 90, t)


# ------------------------------------------------------------- hospital 3 --

CAST = hexc('fbfaf3')


def traction_frame(ctx):
    rect(ctx, 200, 70, 760, 14, hexc('c9ccd0'), r=6)
    rect(ctx, 200, 70, 14, 520, hexc('c9ccd0'), r=6)
    rect(ctx, 946, 70, 14, 540, hexc('c9ccd0'), r=6)


def cast_body(ctx, x, y, s=1.0, sip=0.0, eyes='open', look=(0, 0), mouth='flat', blush=0.0, lid=0.0):
    """Colin in a full body cast, lying with his head to the left (Storyboard 41)."""
    with tf(ctx, x, y, 0, s):
        # leg in traction
        line(ctx, [(330, -200), (330, -470)], lw=2)
        limb(ctx, [(60, -10), (200, -60), (330, -200)], 66, CAST)
        circle(ctx, 330, -205, 18, CAST)
        limb(ctx, [(60, 0), (300, 10)], 62, CAST)
        # torso
        blob(ctx, [(-160, -60), (80, -70), (110, -10), (80, 30), (-160, 30)], CAST)
        hatch(ctx, -150, -60, 240, 90, gap=26, alpha=0.08)
        # good arm up to the hand-grip
        limb(ctx, [(-90, -60), (-60, -200), (-60, -330)], 40, CAST)
        circle(ctx, -60, -340, 16, COLIN['skin'])
        # head: face up, wrapped in plaster
        with tf(ctx, -230, -40, -90):
            p = dict(eyes=eyes, look=look, lid=lid, brow=0.4, mouth=mouth, bandage=False,
                     _skin=COLIN['skin'])
            from puppets import COLIN as CST
            head_profile(ctx, p, dict(CST, head='none'))
            blob(ctx, [(-50, -10), (-40, -50), (0, -60), (30, -50), (20, -34), (6, -24), (-10, -6), (-14, 20),
                       (6, 40), (0, 56), (-40, 50)], CAST)
            if blush:
                circle(ctx, 16, 14, 9, (0.95, 0.35, 0.35), lw=0, alpha=0.5 * blush)


def draw_hosp3_wide(ctx, t):
    """He stares at the juice. Can't reach. The cleaner props her broom and comes to help."""
    ward(ctx, t, window_x=1000, curtain=False)
    traction_frame(ctx)
    hospital_bed(ctx, 560, 640, 1.25)
    grip_y = keys(t, [(0, 0), (1.0, -6), (1.4, 6), (1.8, -4)])
    # triangle hand-grip
    line(ctx, [(500, 84), (500, 200 + grip_y)], lw=2)
    poly(ctx, [(480, 230 + grip_y), (520, 230 + grip_y), (500, 196 + grip_y)], None, lw=5, ink=hexc('9a9a9a'))
    strain = math.sin(t * 18) * 2 if 0.6 < t < 2.0 else 0
    cast_body(ctx, 560 + strain, 440, 1.0, look=(1, 0.2), mouth='grit' if 0.6 < t < 2.0 else 'flat')
    line(ctx, [(890, 84), (890, 240)], lw=2)
    # bedside cabinet with the juice (out of reach)
    rect(ctx, 150, 410, 120, 230, hexc('d8d0bc'))
    rect(ctx, 166, 440, 88, 60, None, lw=2)
    circle(ctx, 210, 470, 5, hexc('8a8a8a'))
    juice(ctx, 210, 410, 0.6)
    # the cleaner, sweeping; notices at 2.2; leans broom; walks over
    lx = keys(t, [(0, 1120), (2.9, 1120), (4.6, 1120)], ease=lambda x: x)
    sweep = math.sin(t * 5) * 14 if t < 2.2 else 0
    notice = t > 2.2

    def broom_r(ctx, x, y):
        if t < 3.0:
            limb(ctx, [(x, y - 120), (x + sweep, y + 190)], 8, hexc('b5884f'), lw=2.2)
            rect(ctx, x + sweep - 40, y + 180, 80, 24, hexc('5a4a3a'), r=4)

    if t > 3.0:
        limb(ctx, [(1240, 620), (1210, 330)], 8, hexc('b5884f'), lw=2.2)
        rect(ctx, 1210, 610, 80, 24, hexc('5a4a3a'), r=4)
    walking = t > 3.3
    lx = keys(t, [(3.3, 1120), (5.6, 900)], ease=lambda x: x)
    bob = abs(math.sin(t * 6)) * 5 if 3.3 < t < 5.6 else 0
    lady(ctx, lx, 640 - bob, 0.85, look=(-1, 0.4) if notice else (0, 0.6), mouth='kind' if notice else 'flat',
         ua_l=20 if t > 3.0 else 30, fa_l=-50 if t > 3.0 else -40, ua_r=20, fa_r=-30,
         prop_r=broom_r if t < 3.0 else None, blink=blink(t, 3.1))


def juice(ctx, x, y, s=1.0, level=1.0):
    with tf(ctx, x, y, 0, s):
        poly(ctx, [(-50, -180), (50, -180), (40, 0), (-40, 0)], (0.9, 0.95, 0.98), lw=3, alpha=0.9)
        top = -170 * level
        poly(ctx, [(-40 - 10 * level, top), (40 + 10 * level, top), (40, -4), (-40, -4)], hexc('f2a33a'), lw=0)
        line(ctx, [(-40 - 10 * level, top), (40 + 10 * level, top)], lw=2)
        poly(ctx, [(-50, -180), (50, -180), (40, 0), (-40, 0)], None, lw=3)
        poly(ctx, [(10, -120), (30, -250), (36, -248), (16, -118)], (1, 1, 1), lw=2)
        poly(ctx, [(30, -250), (90, -262), (90, -254), (36, -242)], (1, 1, 1), lw=2)
        for k in range(4):
            line(ctx, [(30 + k * 2, -250 + k * 3), (34 + k * 2, -244 + k * 3)], lw=1.2, ink=hexc('e05a5a'))


def draw_sip(ctx, t):
    """She holds the straw to his lips. He sips, reluctantly."""
    bg(ctx, HOSP_WALL)
    rect(ctx, -10, 520, W + 20, 200, hexc('f4f6f2'))      # pillow/sheet
    blob(ctx, [(-50, 560), (200, 420), (700, 400), (900, 520), (900, 760), (-50, 760)], hexc('ffffff'))
    # his plastered head, face-up-ish, three-quarter
    colin_face(ctx, 470, 380, 1.15, rot=-12, eyes='open', look=(0.8, -0.3) if t < 2.0 else (0.9, -0.6),
               lid=0.2, brow=0.6, mouth='o', shirt=False)
    blob(ctx, [(330, 200), (420, 230), (390, 300), (360, 380), (380, 460), (450, 520), (360, 560), (290, 460),
               (280, 300)], CAST)
    blob(ctx, [(610, 200), (540, 230), (570, 300), (590, 380), (580, 460), (520, 520), (600, 560), (660, 460),
               (660, 300)], CAST)
    blob(ctx, [(330, 210), (420, 160), (560, 160), (620, 210), (540, 240), (420, 240)], CAST)
    # the glass in her hand, straw to his mouth; the level drops
    level = 1.0 - 0.6 * lin(t, 0.8, 3.4)
    gx = lerp(1100, 760, seg(t, 0.0, 0.7))
    juice(ctx, gx, 700, 1.4, level=level)
    blob(ctx, [(gx - 90, 520), (gx + 60, 500), (gx + 90, 600), (gx - 60, 640)], LADY['skin'], lw=3.5)
    limb(ctx, [(gx + 60, 580), (W + 200, 760)], 70, LADY['dress'])
    if t > 0.9:
        for k in range(3):
            ph = (t * 1.8 + k / 3) % 1
            circle(ctx, lerp(gx - 30, 520, ph), lerp(400, 445, ph), 4, hexc('f2a33a'), lw=0, alpha=0.6)


def draw_spill(ctx, t):
    """Storyboards 44-45: a little spill ring. She wipes it, gently."""
    bg(ctx, hexc('d8d0bc'))
    hatch(ctx, 0, 0, W, H, gap=24, alpha=0.06)
    fade = 1 - seg(t, 1.2, 2.8)
    ellipse(ctx, 640, 400, 120, 40, hexc('e8a03a'), lw=0, alpha=0.7 * fade)
    ellipse(ctx, 640, 400, 120, 40, None, lw=4, ink=hexc('b87a2a'), alpha=0.8 * fade)
    circle(ctx, 790, 390, 16, hexc('e8a03a'), lw=0, alpha=0.7 * fade)
    if t > 0.6:
        a = (t - 0.6) * 7
        cx, cy = 640 + 70 * math.cos(a), 400 + 24 * math.sin(a)
        with tf(ctx, cx, cy, 10 * math.sin(a)):
            poly(ctx, [(-150, -110), (120, -130), (160, 90), (-130, 110)], hexc('9fc6d6'))
            for k in range(5):
                line(ctx, [(-120 + k * 50, -110), (-110 + k * 54, 100)], lw=1.4, alpha=0.3)
            blob(ctx, [(-90, -60), (20, -90), (80, -60), (70, 40), (-60, 60)], LADY['skin'], lw=4)
            for f in range(4):
                limb(ctx, [(40, -60 + f * 26), (120, -80 + f * 32)], 22, LADY['skin'], lw=4)


def draw_cupid(ctx, t):
    """Close on Colin: struck by Cupid's arrow."""
    bg(ctx, HOSP_WALL)
    blob(ctx, [(-50, 560), (200, 440), (900, 420), (1330, 520), (1330, 760), (-50, 760)], hexc('ffffff'))
    soft = t > 0.9
    colin_face(ctx, 640, 380, 1.3, rot=-8, eyes='open' if not soft else 'open', look=(0.9, 0) if not soft else (0.9, -0.2),
               lid=0.0 if not soft else 0.35, brow=0.0 if not soft else -0.2,
               mouth='flat' if t < 1.4 else 'smile', blush=seg(t, 1.2, 2.2), shirt=False)
    blob(ctx, [(450, 180), (560, 200), (520, 300), (490, 400), (510, 500), (580, 570), (470, 610), (390, 500),
               (380, 300)], CAST)
    blob(ctx, [(830, 180), (720, 200), (760, 300), (790, 400), (780, 500), (700, 570), (800, 610), (880, 500),
               (880, 300)], CAST)
    blob(ctx, [(450, 190), (560, 120), (720, 120), (830, 190), (740, 220), (560, 220)], CAST)
    # a little arrow: thwip
    if 0.5 < t < 1.0:
        ax = lerp(-100, 520, lin(t, 0.5, 0.75))
        line(ctx, [(ax - 120, 300), (ax, 310)], lw=4)
        poly(ctx, [(ax, 302), (ax + 26, 312), (ax, 320)], hexc('e0485a'), lw=2)
    if t > 0.75:
        heart(ctx, 900, 620, 34 * (1 + 0.15 * math.sin(t * 12)))
    if t > 1.6:
        thought_hearts(ctx, 840, 220, t, n=4, s=1.4)


def draw_her(ctx, t):
    """...and her: a shy smile back. The two of them, gazing."""
    ward(ctx, t, window_x=1000, curtain=False)
    traction_frame(ctx)
    hospital_bed(ctx, 560, 640, 1.25)
    cast_body(ctx, 560, 440, 1.0, look=(1, 0), mouth='smile', blush=1.0, lid=0.3)
    line(ctx, [(890, 84), (890, 240)], lw=2)
    rect(ctx, 150, 410, 120, 230, hexc('d8d0bc'))
    juice(ctx, 210, 410, 0.6, level=0.4)
    shy = seg(t, 0.4, 1.0) - seg(t, 1.6, 2.2)
    lady(ctx, 900, 640, 0.85, look=(-1, 0.6 * shy - 0.1), mouth='smile', blush=1.0, eyes='open',
         ua_l=20, fa_l=-60, ua_r=20, fa_r=-60, lean=-3 * shy)
    thought_hearts(ctx, 560, 300, t, n=3)
    thought_hearts(ctx, 880, 200, t + 0.5, n=3)


def blinds(ctx, gap_open=0.0, sea=True):
    vgrad(ctx, 0, 0, W, 300, hexc('bcd8e8'), hexc('e6f0f2'))
    if sea:
        vgrad(ctx, 0, 300, W, 260, hexc('6a9fbf'), hexc('4a7f9f'))
        for k in range(8):
            line(ctx, [(k * 170 + 30, 330 + k % 3 * 50), (k * 170 + 90, 330 + k % 3 * 50)], lw=2, ink=(1, 1, 1), alpha=0.6)
    rect(ctx, -10, 560, W + 20, 30, hexc('f2eee4'))       # sill
    rect(ctx, -10, 590, W + 20, 200, HOSP_WALL)


def draw_window_duck(ctx, t):
    """Storyboards 46-48: behind the vertical blinds, the duck has watched it all."""
    blinds(ctx)
    duck(ctx, 830, 566, 2.2, face=-1, look=(1, 0.3) if t < 2.5 else (0, 0),
         eyes='open' if t < 2.0 else 'content', neck=0.7,
         tilt=keys(t, [(2.0, 0), (2.4, 12), (2.8, 0), (3.2, 12), (3.6, 0)]))    # two little nods
    # the blinds, with one pair nudged apart
    for k in range(-1, 12):
        x = k * 118 + 20
        if k in (5,):
            x -= 80
        if k in (6,):
            x += 60
        rect(ctx, x, -10, 92, 570, shade(hexc('f0ece0'), 0.98 if k % 2 else 1.0), lw=2.2)
        line(ctx, [(x + 46, -10), (x + 46, 560)], lw=1, alpha=0.2)


def draw_fly_away(ctx, t):
    """...and, satisfied, she flies off over the sea."""
    blinds(ctx)
    k = seg(t, 0.3, 4.5)
    duck(ctx, lerp(830, 1500, k), lerp(566, 60, k) - math.sin(k * math.pi) * 60, lerp(2.2, 0.5, k),
         face=1, fly=t > 0.3, wing=(math.sin(t * 16) + 1) / 2, eyes='content')
    for k2 in range(-1, 12):
        x = k2 * 118 + 20
        if k2 == 5:
            x -= 80
        if k2 == 6:
            x += 60
        sw = 6 * math.sin(t * 3 + k2) * (1 - seg(t, 0.4, 3.0)) if t > 0.3 else 0
        wd = 92 * (1 - 0.72 * seg(t, 0.1, 0.6))       # the slats turn open as she takes off
        with tf(ctx, x + 46, -10, sw * 0.4):
            rect(ctx, -wd / 2, 0, wd, 570, shade(hexc('f0ece0'), 0.98 if k2 % 2 else 1.0), lw=2.2)


def draw_end(ctx, t):
    bg(ctx, hexc('efe6d2'))
    rect(ctx, 60, 50, W - 120, H - 100, None, lw=5)
    rect(ctx, 76, 66, W - 152, H - 132, None, lw=1.6)
    text(ctx, 'The End', W / 2, 330, 140, font='Abril Fatface', align='center', alpha=seg(t, 0.3, 1.2))
    text(ctx, 'from the screenplay by Damian Gason', W / 2, 420, 32, font='Patrick Hand', align='center',
         alpha=seg(t, 1.0, 1.8) * 0.85)
    text(ctx, 'drawn entirely in code', W / 2, 466, 26, font='Caveat', align='center', alpha=seg(t, 1.6, 2.4) * 0.8)
    # a tiny duck silhouette flying across
    k = lin(t, 1.0, 5.0)
    duck(ctx, lerp(-80, 1360, k), 610 - 30 * math.sin(k * math.pi), 0.45, fly=True, wing=(math.sin(t * 14) + 1) / 2)


def build():
    return [
        Shot('d01_stairs', 4.2, draw_stairs_intro, fade_in=0.6, sfx=[(2.2, 'hmm_sting', 0.4), (3.3, 'swish', 0.5)]),
        Shot('d02_bed', 3.6, draw_under_bed, sfx=[(0.6, 'waddle', 0.4)]),
        Shot('d03_umbrella', 3.0, draw_umbrella, sfx=[(2.2, 'whip', 0.5)]),
        Shot('d04_behind', 4.4, draw_behind, sfx=[(1.2, 'whip', 0.5), (2.4, 'whip', 0.5), (3.4, 'whip', 0.5)]),
        Shot('d05_climb', 3.4, draw_climb, sfx=[(0.3 + k * 0.33, 'creak_step', 0.35) for k in range(6)]),
        Shot('d06_grab', 1.8, draw_grab, sfx=[(1.3, 'rope', 0.4)]),
        Shot('d07_ducktop', 2.0, draw_duck_top, sfx=[(0.2, 'sting', 0.6), (1.4, 'quack', 0.6)]),
        Shot('d08_tumble', 4.2, draw_tumble,
             sfx=[(0.0, 'yelp', 0.5)] + [(0.8 + k * 0.3, 'thump', 0.6) for k in range(6)] + [(2.6, 'crash_soft', 0.8)],
             shake=[(2.6, 0.4, 14)], fade_out=0.6),
        Shot('d09_black', 0.8, lambda c, t: bg(c, (0, 0, 0)), paper=False),
        Shot('d10_hosp3', 6.0, draw_hosp3_wide, fade_in=0.6, sfx=[(0.8, 'strain', 0.3), (3.0, 'clack', 0.3)]),
        Shot('d11_sip', 3.8, draw_sip, sfx=[(1.0, 'slurp', 0.5)]),
        Shot('d12_spill', 3.0, draw_spill, sfx=[(0.6, 'wipe', 0.4)]),
        Shot('d13_cupid', 3.6, draw_cupid, sfx=[(0.5, 'twang', 0.6), (0.8, 'harp', 0.6)]),
        Shot('d14_her', 4.0, draw_her),
        Shot('d15_window', 4.6, draw_window_duck),
        Shot('d16_flyaway', 5.0, draw_fly_away, sfx=[(0.3, 'flap', 0.5), (0.6, 'quack', 0.4)], fade_out=1.0),
        Shot('d17_end', 6.0, draw_end, fade_in=0.8, fade_out=1.2),
    ]
