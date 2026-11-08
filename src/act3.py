"""Act three: the garage, and the second hospital visit."""
import math

from engine import (INK, H, W, Shot, bg, blink, blob, circle, curve, ellipse,
                    hatch, hexc, keys, lerp, limb, lin, line, poly, rect, seg,
                    set_col, shade, smooth, text, tf, vgrad)
from props import (CAR_COL, car_side, star_burst, stars_orbit)
from puppets import (COLIN, colin_face, duck, duck_head_big, lady, person, pose)
from act2 import ward
from props import hospital_bed

GARAGE_WALL = hexc('b9b2a2')
GARAGE_FLOOR = hexc('7d7a74')
HOSE = hexc('3f7a4a')


def garage_bg(ctx):
    vgrad(ctx, 0, 0, W, 560, shade(GARAGE_WALL, 1.05), shade(GARAGE_WALL, 0.9))
    for k in range(0, W, 160):
        line(ctx, [(k, 0), (k, 560)], lw=1.4, alpha=0.25)
    vgrad(ctx, 0, 560, W, H - 560, GARAGE_FLOOR, shade(GARAGE_FLOOR, 0.8))
    ellipse(ctx, 640, 616, 220, 14, shade(GARAGE_FLOOR, 0.7), lw=0, alpha=0.6)   # oil stain
    # bare bulb
    line(ctx, [(640, -10), (640, 60)], lw=2)
    circle(ctx, 640, 74, 14, hexc('fff4c0'), lw=2)
    circle(ctx, 640, 74, 60, (1, 0.95, 0.7), lw=0, alpha=0.2)
    # pegboard with tools
    with tf(ctx, 860, 0):
        rect(ctx, 60, 120, 260, 180, hexc('c8a77a'))
        for i in range(10):
            for j in range(7):
                circle(ctx, 76 + i * 25, 134 + j * 25, 2.2, INK, lw=0, alpha=0.5)
        limb(ctx, [(110, 150), (110, 260)], 8, hexc('8a8a8a'), lw=2)
        rect(ctx, 96, 140, 28, 20, hexc('c43b2d'), lw=2)
        limb(ctx, [(180, 150), (200, 250)], 6, hexc('8a8a8a'), lw=2)
        circle(ctx, 260, 210, 34, None, lw=8, ink=hexc('3a3a3a'))


def shelf(ctx, can_state=0.0, can_xy=None):
    rect(ctx, 180, 200, 330, 18, hexc('8b6a45'), r=3)
    for bx in (200, 480):
        poly(ctx, [(bx, 218), (bx + 14, 218), (bx + 14, 260)], hexc('6b4a33'), lw=2)
    # paint tins
    for k, c in enumerate(('3a5fa8', 'e8c45a')):
        rect(ctx, 200 + k * 60, 140, 50, 60, hexc(c), r=4)
        rect(ctx, 200 + k * 60, 138, 50, 10, hexc('9a9a9a'), lw=2)


def bug_can(ctx, x, y, rot=0.0, s=1.0):
    with tf(ctx, x, y, rot, s):
        rect(ctx, -22, -90, 44, 90, hexc('e8c43a'), r=6)
        rect(ctx, -22, -70, 44, 40, hexc('c43b2d'), lw=2)
        text(ctx, 'BUZKILL', 0, -44, 12, font='Abril Fatface', align='center', col=(1, 1, 1))
        rect(ctx, -10, -104, 20, 16, hexc('cfcfcf'), lw=2, r=3)
        rect(ctx, -4, -114, 8, 10, hexc('3a3a3a'), lw=1.6)


def broom(ctx, x, y, rot=0.0, helmet=True):
    """Broom leaning, origin at the bristle end on the floor; helmet hung on the top."""
    with tf(ctx, x, y, rot):
        limb(ctx, [(0, -20), (0, -330)], 9, hexc('b5884f'), lw=2.4)
        poly(ctx, [(-34, 0), (34, 0), (24, -30), (-24, -30)], hexc('d8b25a'))
        for k in range(-28, 30, 7):
            line(ctx, [(k, -2), (k * 0.85, -26)], lw=1.2, alpha=0.6)
        rect(ctx, -26, -42, 52, 14, hexc('8a5a3a'), r=3)
        if helmet:
            with tf(ctx, 0, -332):
                blob(ctx, [(-46, 10), (-44, -24), (0, -50), (44, -24), (46, 10), (0, 18)], hexc('e7e3d6'))
                rect(ctx, -48, 4, 96, 12, hexc('c43b2d'), lw=2.4, r=4)
                circle(ctx, -20, -22, 3, INK, lw=0)
                circle(ctx, 22, -22, 3, INK, lw=0)


def colin_in_car(eyes='open', mouth='frown', look=(1, 0), lid=0.3, brow=0.6, x=0, y=0):
    def inside(ctx):
        p = pose(x=-40 + x, y=-62 + y, s=0.55, face=1, th_n=84, sh_n=-62, th_f=80, sh_f=-60, ua_n=70,
                 fa_n=20, ua_f=66, fa_f=24, eyes=eyes, mouth=mouth, look=look, lid=lid, brow=brow)
        ctx.save()
        poly(ctx, [(-110, -150), (30, -156), (92, -110), (-150, -108)], None, lw=0)
        ctx.restore()
        ctx.save()
        ctx.rectangle(-200, -170, 400, 64)
        ctx.clip()
        # car_side is drawn mirrored (face=-1); undo so Colin faces the bonnet
        person(ctx, p, COLIN)
        ctx.restore()
    return inside


def draw_garage_wide(ctx, t, phase='setup'):
    """Storyboard 31 and the chain reaction (33-36)."""
    garage_bg(ctx)
    shelf(ctx)
    # car: bonnet towards the wall on the right
    hose_out = 0.0
    can_rot, can_x, can_y = 0.0, 440, 200
    broom_rot = 8.0
    helmet = True
    if phase == 'chain':
        # the duck shoves the can (0.2), it falls (0.5-0.9), hits the broom which topples (0.9-1.5)
        fall = lin(t, 0.45, 0.75)
        can_x = lerp(440, 452, fall)
        can_y = 200 + 120 * fall ** 2
        can_rot = 120 * fall
        if t > 0.75:   # bounces off the helmet and away to the floor
            k = lin(t, 0.75, 1.3)
            can_x = lerp(452, 250, k)
            can_y = lerp(320, 640, k) - math.sin(k * math.pi) * 80
            can_rot = 120 - 400 * k
            if t > 1.3:
                can_x, can_y, can_rot = 250, 640, -280
        broom_rot = keys(t, [(0.8, 8), (1.4, 58)], ease=lambda x: x * x)
        hose_out = seg(t, 1.2, 1.6)
    car_side(ctx, 680, 610, 1.0, face=1, lights=False, inside=colin_in_car(
        eyes='wide' if (phase == 'chain' and t > 1.3) else 'open',
        mouth='o' if (phase == 'chain' and t > 1.3) else 'frown', lid=0.0 if phase == 'chain' and t > 1.3 else 0.35))
    # hose from the exhaust up to the rear window (a simple garden hose)
    ex, ey = 680 - 205, 610 - 46
    if hose_out < 1:
        top = (lerp(560, 470, hose_out), lerp(470, 600, hose_out))
        curve(ctx, [(ex, ey), (ex - 60, ey + 10), (ex - 70, 520), (top[0] - 30, top[1] - 10), top],
              lw=12, ink=INK)
        curve(ctx, [(ex, ey), (ex - 60, ey + 10), (ex - 70, 520), (top[0] - 30, top[1] - 10), top],
              lw=7, ink=HOSE)
    else:
        curve(ctx, [(ex, ey), (ex - 80, ey + 20), (ex - 160, 640), (ex - 40, 660), (ex + 60, 650)], lw=12, ink=INK)
        curve(ctx, [(ex, ey), (ex - 80, ey + 20), (ex - 160, 640), (ex - 40, 660), (ex + 60, 650)], lw=7, ink=HOSE)
    # broom leaning by the back of the car, helmet hung on top
    broom(ctx, 380, 650, broom_rot, helmet)
    bug_can(ctx, can_x, can_y, can_rot)
    if phase == 'chain':
        # the duck on the shelf, giving it a determined shove with her bill
        shove = seg(t, 0.15, 0.4) - seg(t, 0.45, 0.7)
        duck(ctx, 350 + shove * 40, 200, 0.75, face=1, neck=0.2 + shove * 0.3, tilt=shove * 20,
             eyes='narrow' if t < 0.45 else 'open', look=(1, 0.5))
        if 0.72 < t < 0.9:
            star_burst(ctx, 452, 316, 30)
        if 1.35 < t < 1.6:
            star_burst(ctx, 560, 470, 34)


def draw_fly(ctx, t):
    """Storyboard 29: a dead fly on the dashboard. Colin stares at it."""
    bg(ctx, hexc('3b3530'))
    hatch(ctx, 0, 0, W, H, gap=14, alpha=0.08, col=(1, 1, 1))
    rect(ctx, -10, 360, W + 20, 400, hexc('4b443d'))
    with tf(ctx, 640, 420, 0, 2.2):
        ellipse(ctx, -30, -10, 50, 16, (0.85, 0.9, 0.95), lw=2, alpha=0.8)
        ellipse(ctx, 30, -10, 50, 16, (0.85, 0.9, 0.95), lw=2, alpha=0.8)
        ellipse(ctx, 0, -14, 26, 20, hexc('2a2a2e'))
        circle(ctx, 24, -12, 14, hexc('5a2a26'))
        for k, a in enumerate((-30, 0, 30)):
            twitch = 6 * math.sin(t * 20) if (k == 1 and 1.0 < t < 1.2) else 0
            curve(ctx, [(-8 + k * 8, -28), (-14 + k * 10 + a * 0.3, -60), (-20 + k * 14 + a * 0.6 + twitch, -78)], lw=2.4)


def draw_buster(ctx, t):
    """Storyboard 30: the dust-buster takes care of it."""
    bg(ctx, hexc('3b3530'))
    rect(ctx, -10, 360, W + 20, 400, hexc('4b443d'))
    suck = seg(t, 0.8, 1.2)
    if suck < 1:
        fx = lerp(560, 860, suck)
        with tf(ctx, fx, lerp(410, 330, suck), suck * 360, 1.0 - 0.6 * suck):
            ellipse(ctx, 0, 0, 24, 16, hexc('2a2a2e'))
            curve(ctx, [(0, -14), (-6, -40)], lw=2)
            curve(ctx, [(8, -14), (10, -40)], lw=2)
    bx = lerp(W + 200, 880, seg(t, 0.0, 0.6))
    with tf(ctx, bx, 300, -14):
        poly(ctx, [(-40, -70), (360, -110), (420, 60), (-20, 70)], hexc('6c7a86'))
        rect(ctx, 80, -40, 200, 60, hexc('4a5560'), r=12)
        poly(ctx, [(-40, -70), (-20, 70), (-70, 50), (-80, -50)], hexc('333'))
        for k in range(4):
            line(ctx, [(300 + k * 18, -80), (320 + k * 18, 40)], lw=3, alpha=0.4)
    if 0.8 < t < 1.6:
        for k in range(4):
            ph = (t * 3 + k / 4) % 1
            line(ctx, [(lerp(560, 840, ph), 400 - k * 20), (lerp(600, 860, ph), 380 - k * 20)], lw=2, alpha=1 - ph)


def draw_ignition(ctx, t):
    """Storyboard 32: the key."""
    bg(ctx, hexc('2e2a27'))
    hatch(ctx, 0, 0, W, H, gap=12, alpha=0.12, col=(1, 1, 1))
    circle(ctx, 640, 380, 130, hexc('3a3a3a'))
    circle(ctx, 640, 380, 90, hexc('9a9a9a'))
    for lbl, a in (('LOCK', -50), ('ACC', -10), ('ON', 30)):
        with tf(ctx, 640, 380, a):
            text(ctx, lbl, 0, -100, 22, font='DejaVu Sans', align='center', bold=True, col=(0.9, 0.9, 0.9))
    with tf(ctx, 640, 380, -50):
        rect(ctx, -10, -60, 20, 80, hexc('d4b648'), lw=2.4)
        circle(ctx, 0, 50, 34, hexc('d4b648'))
        circle(ctx, 0, 60, 10, hexc('2e2a27'))
    reach = seg(t, 0.2, 1.0)
    hx, hy = lerp(-200, 560, reach), lerp(760, 470, reach)
    limb(ctx, [(-300, 900), (hx - 40, hy + 60)], 110, COLIN['shirt'], lw=4)
    with tf(ctx, hx, hy, -20):
        blob(ctx, [(-60, -40), (30, -60), (90, -20), (80, 50), (-10, 70), (-60, 40)], COLIN['skin'], lw=4)
        limb(ctx, [(60, -40), (100, -60)], 24, COLIN['skin'], lw=4)


def draw_can_close(ctx, t):
    """Storyboard 33: the duck eyes the BUZKILL can. A nudge."""
    bg(ctx, GARAGE_WALL)
    hatch(ctx, 0, 0, W, H, gap=22, alpha=0.08)
    rect(ctx, -10, 520, W + 20, 40, hexc('8b6a45'), r=3)
    shove = seg(t, 1.2, 1.5)
    tip = seg(t, 1.5, 1.9)
    with tf(ctx, 700 + shove * 40 + tip * 200, 520 + tip * 300, 0, 2.6):
        bug_can(ctx, 0, 0, tip * 70)
    duck(ctx, 380 + shove * 60, 520, 2.2, face=1, neck=0.3, eyes='narrow' if t < 1.2 else 'content',
         tilt=keys(t, [(0.4, 0), (0.9, 10), (1.2, -10), (1.5, 6)]), look=(1, 0.4))


def draw_peck(ctx, t):
    """The duck lands on the bonnet and pecks at the windscreen. Colin, inside, loses it."""
    garage_bg(ctx)
    # head-on view of the car
    with tf(ctx, 640, 720):
        blob(ctx, [(-380, -40), (-370, -200), (-260, -420), (260, -420), (370, -200), (380, -40)], CAR_COL, tension=0.5)
        poly(ctx, [(-240, -400), (240, -400), (300, -230), (-300, -230)], hexc('a9bcc6'))
        # Colin behind the glass
        with tf(ctx, -80, -250):
            ctx.save()
            ctx.rectangle(-200, -160, 400, 160)
            ctx.clip()
            panic = t > 0.6
            colin_face(ctx, 0, -40, 0.62, eyes='wide' if panic else 'open', mouth='o' if panic else 'frown',
                       look=(0.6, 0.6) if panic else (0, 0), brow=-0.8 if panic else 0.6, lid=0 if panic else 0.4)
            ctx.restore()
        poly(ctx, [(-240, -400), (240, -400), (300, -230), (-300, -230)], (1, 1, 1), alpha=0.12)
        line(ctx, [(-180, -380), (-120, -260)], lw=4, ink=(1, 1, 1), alpha=0.5)
        rect(ctx, -330, -230, 660, 120, shade(CAR_COL, 0.95))
        for sx in (-1, 1):
            ellipse(ctx, sx * 270, -150, 50, 34, hexc('fff2b0'))
        rect(ctx, -110, -170, 220, 50, hexc('5a5a5a'), r=8)
        rect(ctx, -390, -80, 780, 50, hexc('8f8f8f'), r=12)
        # the duck lands on the bonnet (0.0-0.4) and pecks, pecks, pecks
        land = seg(t, 0.0, 0.35)
        peck = max(0, math.sin(t * 22)) if t > 0.5 else 0
        squash = 1.0 - 0.25 * (seg(t, 0.35, 0.42) - seg(t, 0.42, 0.55))
        duck(ctx, 120, lerp(-700, -230, land), 1.6, face=-1, fly=(land < 1), wing=(math.sin(t * 40) + 1) / 2,
             tilt=30 * peck, neck=0.4, squash=squash, eyes='narrow')
        if peck > 0.9:
            star_burst(ctx, 30, -330, 14, col=(1, 1, 1))


def draw_smash(ctx, t):
    """Into the wall. The airbag goes off."""
    garage_bg(ctx)
    lurch = seg(t, 0.15, 0.45)
    cx = lerp(680, 780, lurch)
    car_side(ctx, cx, 610, 1.0, face=1, lights=False, crumple=seg(t, 0.4, 0.5),
             inside=colin_in_car(eyes='wide', mouth='o', lid=0))
    # the end wall on the right
    rect(ctx, 1010, -10, 300, 740, shade(GARAGE_WALL, 0.85))
    for k in range(0, 740, 44):
        line(ctx, [(1010, k), (1290, k)], lw=1.4, alpha=0.3)
    if t > 0.45:
        # the airbag fills the cabin
        bag = seg(t, 0.45, 0.6)
        ellipse(ctx, cx + 30, 610 - 128, 70 * bag + 10, 34 * bag + 4, hexc('f4f4ef'))
        star_burst(ctx, 990, 480, 70 * (1 - seg(t, 0.5, 0.9)) + 10, rot=t * 300)
    if t < 0.4:
        duck(ctx, cx + 10, 610 - 168, 0.7, face=1, fly=(t > 0.2), wing=(math.sin(t * 40) + 1) / 2)
    else:
        k = seg(t, 0.4, 1.4)
        duck(ctx, lerp(cx + 40, 860, k), lerp(430, 120, k), 0.7, face=-1, fly=True, wing=(math.sin(t * 40) + 1) / 2)


def draw_hospital2(ctx, t):
    """Arm in plaster now. The cleaner, changing a bin liner, sees him: the same slow shake."""
    ward(ctx, t)
    # bin + the cleaner with a bin liner
    rect(ctx, 1040, 470, 70, 80, hexc('8a8f96'), r=6)
    shake = 0.0
    if 2.0 < t < 4.2:
        shake = math.sin((t - 2.0) * 2 * math.pi * 1.1) * seg(t, 2.0, 2.3) * (1 - seg(t, 3.8, 4.2))

    def liner(ctx, x, y):
        blob(ctx, [(x - 30, y), (x + 30, y), (x + 40, y + 70), (x, y + 90), (x - 40, y + 70)], hexc('2a2a2e'), lw=2)

    lady(ctx, 960, 545, 0.6, shake=shake, look=(-1, 0.2), mouth='tut' if 2.2 < t < 4.0 else 'flat',
         ua_l=16, fa_l=-60, ua_r=40, fa_r=10, prop_r=liner, blink=blink(t, 2.5))
    hospital_bed(ctx, 430, 640, 1.0)
    sigh = seg(t, 4.4, 4.9) - seg(t, 5.1, 5.6)

    def sling(ctx, x, y, a):
        pass

    p = pose(x=440, y=476 + sigh * 4, s=1.0, face=1, th_n=86, sh_n=-86, th_f=82, sh_f=-82, ua_n=10, fa_n=80,
             ua_f=6, fa_f=30, bandage=True, cast=True, mouth='frown', lid=0.45 + sigh * 0.3, brow=1.0,
             look=(1, -0.3) if 1.6 < t < 4.4 else (0.2, 0.6), head=-4 + sigh * 8)
    person(ctx, p, COLIN)
    # sling strap
    line(ctx, [(452, 340), (488, 432)], lw=6, ink=hexc('f4f4ef'))


def build():
    return [
        Shot('c01_garage', 4.0, lambda c, t: draw_garage_wide(c, t, 'setup'), fade_in=0.6,
             sfx=[(0.6, 'drip', 0.25)]),
        Shot('c02_fly', 2.4, draw_fly, sfx=[(1.0, 'buzz_tiny', 0.3)]),
        Shot('c03_buster', 2.2, draw_buster, sfx=[(0.6, 'dustbuster', 0.5)]),
        Shot('c04_key', 1.8, draw_ignition, sfx=[(1.0, 'keys', 0.4)]),
        Shot('c05_can', 2.2, draw_can_close, sfx=[(1.25, 'quack', 0.5)]),
        Shot('c06_chain', 2.6, lambda c, t: draw_garage_wide(c, t, 'chain'),
             sfx=[(0.85, 'clang', 0.8), (1.45, 'clatter', 0.7), (1.6, 'flump', 0.4)]),
        Shot('c07_peck', 3.0, draw_peck,
             sfx=[(0.35, 'thud', 0.5)] + [(0.6 + k * 0.285, 'peck', 0.6) for k in range(8)] + [(0.8, 'yelp', 0.5)]),
        Shot('c08_smash', 2.4, draw_smash, sfx=[(0.1, 'rev', 0.7), (0.45, 'crunch', 1.0), (0.5, 'bang', 0.9)],
             shake=[(0.45, 0.6, 20)], fade_out=0.6),
        Shot('c09_black', 0.8, lambda c, t: bg(c, (0, 0, 0)), paper=False),
        Shot('c10_hosp2', 6.2, draw_hospital2, fade_in=0.6, sfx=[(2.2, 'tut', 0.4), (4.4, 'sigh_swoop', 0.3)]),
    ]
