"""Articulated cut-out puppets. Each is a function of a pose dict.

Conventions: limb angles are in degrees, 0 = hanging straight down, positive =
swinging forward (towards the way the character faces). Side-view puppets face
right; pass face=-1 to mirror.
"""
import math

from engine import (INK, LW, blob, chain, circle, curve, ellipse, hexc, limb,
                    line, poly, rect, set_col, shade, tf)

SKIN = hexc('f1c39b')
COLIN = dict(
    skin=SKIN, hair=hexc('7b4a2b'), shirt=hexc('f3efe4'), tie=hexc('34466e'),
    trousers=hexc('5c5f69'), shoes=hexc('3b2a22'), coat=None, head='curly',
    nose=1.0,
)
DOCTOR = dict(
    skin=hexc('eab68f'), hair=hexc('d9d4cc'), shirt=hexc('b9d3e6'), tie=hexc('8a2d2d'),
    trousers=hexc('3f4552'), shoes=hexc('241b17'), coat=hexc('fbfbf7'), head='bald',
    nose=1.15,
)

DEFAULT = dict(
    x=0, y=0, s=1.0, face=1, lean=0.0, head=0.0,
    ua_n=8, fa_n=-14, ua_f=-6, fa_f=-12,
    th_n=0, sh_n=0, th_f=0, sh_f=0,
    eyes='open', look=(0, 0), lid=0.0, brow=0.0, mouth='flat',
    bandage=False, cast=False, prop_n=None, prop_f=None, sit=False,
)


def pose(**kw):
    p = dict(DEFAULT)
    p.update(kw)
    return p


def stand(**kw):
    return pose(**kw)


def walk_pose(phase, **kw):
    """Simple economical walk cycle; phase in cycles."""
    a = math.sin(phase * 2 * math.pi)
    b = math.sin(phase * 2 * math.pi + math.pi)
    kn = lambda v: -max(0.0, -v) * 25 - 4
    p = pose(th_n=22 * a, sh_n=kn(math.cos(phase * 2 * math.pi)),
             th_f=22 * b, sh_f=kn(-math.cos(phase * 2 * math.pi)),
             ua_n=-18 * a, ua_f=-18 * b, fa_n=-18, fa_f=-18)
    p['bob'] = abs(math.cos(phase * 2 * math.pi)) * 4
    p.update(kw)
    return p


# --------------------------------------------------------------- heads ------

def curls(ctx, centres, r, col):
    """A merged cluster of curls: strokes first, then fills = one silhouette."""
    for (x, y, *rr) in centres:
        rad = rr[0] if rr else r
        ctx.arc(x, y, rad, 0, 2 * math.pi)
        ctx.new_sub_path()
    set_col(ctx, INK)
    ctx.set_line_width(LW * 2)
    ctx.stroke()
    for (x, y, *rr) in centres:
        rad = rr[0] if rr else r
        ctx.arc(x, y, rad, 0, 2 * math.pi)
        ctx.new_sub_path()
    set_col(ctx, col)
    ctx.fill()
    # little curl marks
    set_col(ctx, shade(col, 0.7))
    ctx.set_line_width(1.6)
    for i, (x, y, *rr) in enumerate(centres):
        if i % 2 == 0:
            rad = (rr[0] if rr else r) * 0.5
            ctx.arc(x, y, rad, 0.4, 3.6)
            ctx.stroke()


def eye_profile(ctx, x, y, p, rx=7.0, ry=9.0):
    eyes = p['eyes']
    if eyes == 'closed':
        curve(ctx, [(x - rx, y + 1), (x, y + 4), (x + rx, y + 1)], lw=2.6)
        return
    if eyes == 'wide':
        rx, ry = rx * 1.35, ry * 1.4
    ellipse(ctx, x, y, rx, ry, (1, 1, 1), lw=2.2)
    lx, ly = p['look']
    pr = 3.4 if eyes != 'wide' else 2.6
    circle(ctx, x + 2 + lx * rx * 0.55, y + 1 + ly * ry * 0.5, pr, INK, lw=0)
    lid = p['lid']
    if lid > 0:
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(rx, ry)
        ctx.arc(0, 0, 1.02, 0, 2 * math.pi)
        ctx.restore()
        ctx.clip()
        top = y - ry + 2 * ry * lid
        rect(ctx, x - rx - 2, y - ry - 4, 2 * rx + 4, top - (y - ry - 4), p['_skin'], lw=0)
        ctx.reset_clip()
        line(ctx, [(x - rx, top + 1.5), (x + rx, top - 1.5)], lw=2.2)


def mouth_profile(ctx, x, y, m):
    if m == 'flat':
        line(ctx, [(x - 9, y), (x + 2, y)], lw=2.4)
    elif m == 'frown':
        curve(ctx, [(x - 10, y + 3), (x - 4, y - 1), (x + 2, y + 3)], lw=2.4)
    elif m == 'smile':
        curve(ctx, [(x - 11, y - 2), (x - 4, y + 4), (x + 3, y - 3)], lw=2.6)
    elif m == 'o':
        ellipse(ctx, x - 3, y + 1, 4.5, 6, hexc('5a2a26'), lw=2.2)
    elif m == 'grit':
        rect(ctx, x - 10, y - 3, 12, 7, (1, 1, 1), lw=2.0, r=2)
        line(ctx, [(x - 10, y + 0.5), (x + 2, y + 0.5)], lw=1.2)
    elif m == 'wobble':
        curve(ctx, [(x - 10, y + 1), (x - 7, y - 1), (x - 4, y + 2), (x - 1, y - 1), (x + 2, y + 1)], lw=2.2)


def head_profile(ctx, p, st):
    skin = st['skin']
    p['_skin'] = skin
    if st['head'] == 'curly':
        curls(ctx, [(-34, -6, 13), (-30, 12, 11), (-36, -24, 12)], 12, st['hair'])
    # face
    blob(ctx, [(-28, -34), (2, -42), (26, -34), (34, -12), (35, 8), (31, 26), (16, 38),
               (-6, 40), (-26, 28), (-34, 4)], skin)
    # ear
    ellipse(ctx, -12, 4, 7, 9.5, shade(skin, 0.95), lw=2.4)
    curve(ctx, [(-13, 0), (-9, 4), (-13, 9)], lw=1.6)
    # nose: big round Pugwash conk
    n = st['nose']
    ellipse(ctx, 38, 6, 11 * n, 10 * n, shade(skin, 0.97), lw=2.6)
    # cheek blush
    circle(ctx, 18, 14, 7, (0.95, 0.55, 0.5), lw=0, alpha=0.25)
    if st['head'] == 'curly':
        curls(ctx, [(-24, -36, 12), (-6, -44, 12), (12, -42, 11), (26, -34, 9),
                    (-36, -24, 11), (-30, -42, 10), (4, -52, 10), (-16, -52, 10)], 11, st['hair'])
    elif st['head'] == 'bald':  # bald with a fringe and specs (doctor)
        curls(ctx, [(-30, -2, 9), (-26, 12, 8), (-20, -14, 8)], 8, st['hair'])
        curve(ctx, [(0, -30), (8, -34)], lw=1.6)
    eye_profile(ctx, 17, -8, p)
    # brow
    b = p['brow']
    line(ctx, [(9, -22 + b * 3), (25, -24 - b * 2)], lw=3.0)
    if st['head'] == 'bald':
        circle(ctx, 18, -7, 10, None, lw=2.4)
        line(ctx, [(8, -9), (-10, -4)], lw=2.0)
        poly(ctx, [(26, 22), (40, 18), (44, 24), (28, 27)], st['hair'], lw=2.0)
    mouth_profile(ctx, 28, 26, p['mouth'])
    if p['bandage']:
        ctx.save()
        rect(ctx, -38, -36, 76, 16, hexc('fbfaf5'), lw=2.4, r=6)
        poly(ctx, [(-36, -30), (-52, -38), (-50, -22)], hexc('fbfaf5'), lw=2.2)
        poly(ctx, [(-36, -27), (-54, -20), (-46, -12)], hexc('fbfaf5'), lw=2.2)
        line(ctx, [(-30, -28), (30, -28)], lw=1.0, alpha=0.4)
        ctx.restore()


# --------------------------------------------------------------- people -----

def person(ctx, p, st=COLIN):
    """Side-view articulated person, origin at the hip."""
    s = p['s']
    with tf(ctx, p['x'], p['y'] - p.get('bob', 0) * s, 0, s * p['face'], s):
        dark = 0.82
        lean = p['lean']
        shoulder = chain(0, 0, [(112, 180 - lean)])[1]
        sx, sy = shoulder

        def arm(ua, fa, col, prop, cast=False):
            a1 = ua + lean
            a2 = a1 + fa
            pts = chain(sx, sy, [(56, a1), (52, a2)])
            sleeve = col
            limb(ctx, pts[:2], 21, sleeve)
            if cast:
                limb(ctx, pts[1:], 28, hexc('fbfaf3'))
                hx, hy = pts[2]
                circle(ctx, hx, hy, 9, st['skin'], lw=2.4)
            else:
                limb(ctx, pts[1:], 18, sleeve)
                hx, hy = pts[2]
                circle(ctx, hx, hy, 9.5, st['skin'], lw=2.6)
            if prop:
                prop(ctx, hx, hy, a2)
            return pts

        def leg(th, sh, col, shoe, ox=0):
            a1 = th
            a2 = th + sh
            pts = chain(ox, 0, [(76, a1), (76, a2)])
            limb(ctx, pts, 33, col)
            ax, ay = pts[2]
            fa = math.radians(a2)
            # shoe pointing forward, perpendicular to the shin
            with tf(ctx, ax, ay, -math.degrees(fa)):
                rect(ctx, -10, -2, 40, 15, shoe, lw=2.6, r=7)
            return pts

        sleeve_f = shade(st['coat'] or st['shirt'], dark)
        sleeve_n = st['coat'] or st['shirt']
        p['_far_arm'] = arm(p['ua_f'], p['fa_f'], sleeve_f, p['prop_f'])
        leg(p['th_f'], p['sh_f'], shade(st['trousers'], dark), shade(st['shoes'], dark), -6)

        # torso
        with tf(ctx, 0, 0, lean):
            if st['coat']:
                blob(ctx, [(-30, 52), (30, 52), (30, -10), (24, -112), (-22, -118), (-32, -40)], st['coat'])
            blob(ctx, [(-25, 10), (24, 10), (27, -55), (22, -114), (-18, -120), (-29, -58)],
                 st['shirt'] if not st['coat'] else st['coat'])
            if not st['coat']:
                rect(ctx, -26, -4, 52, 12, shade(st['trousers'], 0.8), lw=2.4, r=3)
            poly(ctx, [(16, -116), (26, -112), (26, -50), (20, -40), (15, -52)], st['tie'], lw=2.4)
            poly(ctx, [(6, -120), (24, -114), (10, -104)], st['shirt'], lw=2.2)
            if st['coat']:
                line(ctx, [(14, -110), (8, 40)], lw=2.0)
                rect(ctx, -8, -70, 16, 18, None, lw=1.8)
            # neck + head
            circle(ctx, 4, -122, 13, st['skin'], lw=0)
            with tf(ctx, 8, -158, p['head']):
                head_profile(ctx, p, st)
        leg(p['th_n'], p['sh_n'], st['trousers'], st['shoes'], 4)
        p['_near_arm'] = arm(p['ua_n'], p['fa_n'], sleeve_n, p['prop_n'], p['cast'])


def colin(ctx, **kw):
    p = pose(**kw)
    person(ctx, p, COLIN)
    return p


def doctor(ctx, **kw):
    p = pose(**kw)
    person(ctx, p, DOCTOR)
    return p


# ------------------------------------------------------ Colin close-ups ----

def colin_face(ctx, x, y, s=1.0, rot=0, eyes='open', look=(0, 0), lid=0.0, brow=0.0,
               mouth='flat', bandage=False, tear=0.0, blush=0.0, shirt=True):
    """Front-facing big head for close-ups."""
    skin = COLIN['skin']
    hair = COLIN['hair']
    with tf(ctx, x, y, rot, s):
        if shirt:
            blob(ctx, [(-150, 260), (-120, 140), (-40, 108), (40, 108), (120, 140), (150, 260)], COLIN['shirt'])
            poly(ctx, [(-40, 108), (0, 150), (-26, 176)], COLIN['shirt'])
            poly(ctx, [(40, 108), (0, 150), (26, 176)], COLIN['shirt'])
            poly(ctx, [(-10, 150), (10, 150), (16, 260), (0, 280), (-16, 260)], COLIN['tie'])
            poly(ctx, [(-10, 150), (10, 150), (6, 166), (-6, 166)], shade(COLIN['tie'], 0.8))
        rect(ctx, -26, 70, 52, 50, skin, lw=LW)
        curls(ctx, [(-86, -10, 22), (86, -10, 22), (-84, 22, 18), (84, 22, 18)], 20, hair)
        ellipse(ctx, -78, 18, 14, 22, skin)
        ellipse(ctx, 78, 18, 14, 22, skin)
        blob(ctx, [(-74, -40), (-40, -86), (40, -86), (74, -40), (72, 30), (50, 78), (0, 96),
                   (-50, 78), (-72, 30)], skin)
        if blush:
            circle(ctx, -46, 30, 16, (0.95, 0.4, 0.4), lw=0, alpha=0.45 * blush)
            circle(ctx, 46, 30, 16, (0.95, 0.4, 0.4), lw=0, alpha=0.45 * blush)
        curls(ctx, [(-70, -50, 20), (-50, -78, 22), (-18, -92, 22), (16, -94, 22), (48, -80, 22),
                    (70, -52, 20), (-30, -70, 18), (30, -72, 18), (0, -74, 18)], 20, hair)
        p = dict(eyes=eyes, look=look, lid=lid, _skin=skin)
        for ex in (-30, 30):
            eye_profile(ctx, ex, -6, p, rx=15, ry=17)
        # brows (sad = inner ends up)
        for sgn in (-1, 1):
            line(ctx, [(sgn * 14, -34 - brow * 8), (sgn * 46, -30 + brow * 4)], lw=4.5)
        # nose
        blob(ctx, [(-4, -2), (8, 10), (18, 30), (6, 40), (-14, 38), (-20, 28), (-8, 10)], shade(skin, 0.96), lw=2.8)
        mx, my = 0, 62
        if mouth == 'flat':
            line(ctx, [(mx - 18, my), (mx + 18, my)], lw=3.4)
        elif mouth == 'frown':
            curve(ctx, [(mx - 22, my + 8), (mx, my - 2), (mx + 22, my + 8)], lw=3.4)
        elif mouth == 'smile':
            curve(ctx, [(mx - 26, my - 6), (mx, my + 12), (mx + 26, my - 6)], lw=3.6)
        elif mouth == 'o':
            ellipse(ctx, mx, my + 4, 11, 15, hexc('5a2a26'), lw=3)
        elif mouth == 'wobble':
            curve(ctx, [(mx - 20, my + 2), (mx - 10, my - 3), (mx, my + 3), (mx + 10, my - 3), (mx + 20, my + 2)], lw=3)
        if tear > 0:
            ellipse(ctx, 34, 14 + tear * 40, 5, 7, (0.7, 0.85, 1.0), lw=1.8)
        if bandage:
            rect(ctx, -82, -66, 164, 30, hexc('fbfaf5'), lw=2.8, r=10)
            line(ctx, [(-70, -51), (70, -51)], lw=1.2, alpha=0.4)


# ------------------------------------------------------------------ duck ----

DUCK_W = hexc('fbfaf4')
DUCK_SHADE = hexc('dcdcd2')
BILL = hexc('f2a03a')


def duck(ctx, x, y, s=1.0, face=1, walk=None, neck=0.0, tilt=0.0, blink=False,
         wing=0.0, fly=False, look=(0, 0), rock=0.0, eyes='open', squash=1.0, quack=0.0):
    """White farmyard duck. Origin at the feet on the ground.

    walk: phase (cycles) or None; neck: 0 tucked .. 1 stretched up;
    wing: 0 folded .. 1 raised (flap); fly: flying pose; quack: bill open 0..1.
    """
    with tf(ctx, x, y, 0, s * face, s * squash):
        r = rock
        legs_up = fly
        lift = [0, 0]
        fwd = [0, 0]
        if walk is not None:
            ph = walk * 2 * math.pi
            fwd = [10 * math.sin(ph), 10 * math.sin(ph + math.pi)]
            lift = [max(0, math.cos(ph)) * 6, max(0, math.cos(ph + math.pi)) * 6]
            r += 5 * math.sin(ph)
        with tf(ctx, 0, -30, r):
            # legs (drawn under body)
            if not legs_up:
                for i, (lx, dk) in enumerate(((-8, 0.85), (8, 1.0))):
                    fx = lx + fwd[i]
                    fy = 30 - lift[i]
                    limb(ctx, [(lx, 6), (fx, fy - 2)], 5, shade(BILL, dk), lw=2.2)
                    poly(ctx, [(fx - 4, fy - 2), (fx + 16, fy + 1), (fx + 12, fy + 5), (fx - 4, fy + 4)],
                         shade(BILL, dk), lw=2.2)
            else:
                limb(ctx, [(-10, 2), (-26, 8)], 5, BILL, lw=2.2)
            if fly:
                # far wing behind body
                with tf(ctx, 6, -26, -50 * wing + 10):
                    blob(ctx, [(0, 0), (-20, -30), (-58, -48), (-70, -40), (-40, -10)], DUCK_SHADE, lw=2.6)
            # body
            blob(ctx, [(-60, -40), (-44, -26), (-34, 2), (0, 8), (30, 0), (42, -18), (36, -40),
                       (6, -48), (-30, -44)], DUCK_W)
            # neck
            nx, ny = (34 + 8 * (1 - neck), -76 - 30 * neck) if not fly else (72, -46)
            limb(ctx, [(26, -34), (nx - 4, (ny - 34) / 2 - 6), (nx, ny)], 24, DUCK_W, lw=LW)
            # repaint the joint so the neck melts into the chest
            ellipse(ctx, 26, -34, 14, 12, DUCK_W, lw=0)
            # head
            with tf(ctx, nx, ny, tilt):
                circle(ctx, 0, 0, 19, DUCK_W)
                circle(ctx, -4, 6, 12, DUCK_W, lw=0)
                qa = quack * 18
                with tf(ctx, 12, 2, -qa * 0.5):
                    poly(ctx, [(0, -6), (24, -5), (32, -1), (28, 2), (0, 2)], BILL, lw=2.4)
                with tf(ctx, 12, 3, qa):
                    poly(ctx, [(0, 0), (26, 1), (22, 5), (0, 6)], shade(BILL, 0.88), lw=2.4)
                circle(ctx, 22, -3, 1.3, INK, lw=0)
                if blink or eyes == 'closed':
                    curve(ctx, [(0, -6), (5, -3), (10, -6)], lw=2.2)
                elif eyes == 'content':
                    curve(ctx, [(0, -4), (5, -8), (10, -4)], lw=2.4)
                elif eyes == 'narrow':
                    circle(ctx, 5 + look[0] * 2, -5, 3.4, INK, lw=0)
                    line(ctx, [(-2, -11), (12, -7)], lw=3.0)
                else:
                    big = 4.2 if eyes == 'wide' else 3.4
                    circle(ctx, 5 + look[0] * 2.5, -5 + look[1] * 2, big, INK, lw=0)
                    circle(ctx, 6 + look[0] * 2.5, -6.5 + look[1] * 2, 1.1, (1, 1, 1), lw=0)
            # wing on body
            if fly:
                with tf(ctx, 6, -30, 60 * wing - 25):
                    blob(ctx, [(0, 0), (-14, -34), (-50, -60), (-78, -54), (-56, -24), (-26, -2)], DUCK_W, lw=2.8)
                    for k in (0.4, 0.65):
                        curve(ctx, [(-78 * k, -54 * k), (-60 * k, -20 * k)], lw=1.4)
            else:
                with tf(ctx, 12, -36, -45 * wing):
                    blob(ctx, [(4, 2), (-12, -8), (-48, -10), (-62, -6), (-44, 10), (-6, 14)], DUCK_SHADE, lw=2.6)
                    curve(ctx, [(-44, 0), (-58, -5)], lw=1.4)


def duck_head_big(ctx, x, y, s=1.0, look=(0, 0), blink=False, eyes='open', tilt=0, face=1):
    """Big close-up duck head, as in storyboard 40/47."""
    with tf(ctx, x, y, tilt, s * face, s):
        blob(ctx, [(60, 360), (40, 200), (20, 60), (-20, -60), (-110, -120), (-210, -90),
                   (-230, 0), (-170, 80), (-120, 200), (-130, 360)], DUCK_W, lw=4)
        poly(ctx, [(-190, -40), (-330, 40), (-350, 80), (-330, 96), (-160, 70)], BILL, lw=4)
        curve(ctx, [(-340, 82), (-250, 70), (-168, 62)], lw=2.6)
        circle(ctx, -300, 50, 3, INK, lw=0)
        if blink or eyes == 'closed':
            curve(ctx, [(-130, -50), (-110, -36), (-88, -50)], lw=4)
        elif eyes == 'content':
            curve(ctx, [(-132, -40), (-110, -58), (-88, -40)], lw=4.5)
        else:
            ellipse(ctx, -110 + look[0] * 6, -48 + look[1] * 6, 12, 15, INK, lw=0)
            circle(ctx, -106 + look[0] * 6, -54 + look[1] * 6, 4, (1, 1, 1), lw=0)


# ----------------------------------------------------------- cleaning lady --

LADY = dict(skin=hexc('9a6440'), hair=hexc('241915'), dress=hexc('4f9890'),
            apron=hexc('f2efe6'), collar=hexc('fbfaf4'), shoes=hexc('2c2220'))


def lady(ctx, x, y, s=1.0, shake=0.0, look=(0, 0), ua_l=10, fa_l=0, ua_r=10, fa_r=0,
         mouth='kind', blink=False, prop_l=None, prop_r=None, lean=0.0, eyes='open', blush=0.0):
    """Front-view cleaner. Origin between her feet. shake: head turn -1..1."""
    st = LADY
    with tf(ctx, x, y, 0, s):
        with tf(ctx, 0, 0, lean):
            # legs + shoes
            for sx in (-26, 26):
                limb(ctx, [(sx, -90), (sx, -14)], 30, st['skin'])
                rect(ctx, sx - 22, -18, 44, 18, st['shoes'], lw=2.6, r=8)
            # body / dress
            blob(ctx, [(-92, -84), (-104, -170), (-92, -250), (-58, -292), (58, -292), (92, -250),
                       (104, -170), (92, -84), (0, -76)], st['dress'])
            # apron
            blob(ctx, [(-62, -96), (-66, -200), (-50, -240), (50, -240), (66, -200), (62, -96), (0, -90)], st['apron'])
            rect(ctx, -30, -180, 60, 34, None, lw=2.0, r=4)       # pocket
            line(ctx, [(-46, -238), (-52, -288)], lw=6, ink=st['apron'])
            line(ctx, [(46, -238), (52, -288)], lw=6, ink=st['apron'])
            # arms (screen-left = her right)
            for side, ua, fa, prop in ((-1, ua_l, fa_l, prop_l), (1, ua_r, fa_r, prop_r)):
                shx = side * 82
                a1 = math.radians(ua)
                a2 = math.radians(ua + fa)
                ex = shx + side * 70 * math.sin(a1)
                ey = -270 + 70 * math.cos(a1)
                hx = ex + side * 66 * math.sin(a2)
                hy = ey + 66 * math.cos(a2)
                limb(ctx, [(shx, -270), (ex, ey)], 34, st['dress'])
                limb(ctx, [(ex, ey), (hx, hy)], 26, st['skin'])
                circle(ctx, hx, hy, 15, st['skin'], lw=2.8)
                if prop:
                    prop(ctx, hx, hy)
            # neck + collar
            rect(ctx, -20, -322, 40, 40, st['skin'], lw=LW)
            poly(ctx, [(-40, -296), (0, -280), (-14, -262)], st['collar'], lw=2.4)
            poly(ctx, [(40, -296), (0, -280), (14, -262)], st['collar'], lw=2.4)
            # head
            hx = shake * 10
            with tf(ctx, hx, -372, shake * 8):
                curls(ctx, [(-58, -20, 22), (58, -20, 22), (-62, 12, 20), (62, 12, 20), (-54, 38, 16), (54, 38, 16)],
                      20, st['hair'])
                blob(ctx, [(-50, -30), (-30, -64), (30, -64), (50, -30), (52, 20), (34, 56), (0, 68),
                           (-34, 56), (-52, 20)], st['skin'])
                curls(ctx, [(-46, -52, 20), (-20, -70, 22), (12, -72, 22), (40, -58, 20), (-56, -30, 16),
                            (56, -30, 16), (0, -60, 16)], 20, st['hair'])
                if blush:
                    circle(ctx, -30, 22, 11, (0.85, 0.3, 0.35), lw=0, alpha=0.5 * blush)
                    circle(ctx, 30, 22, 11, (0.85, 0.3, 0.35), lw=0, alpha=0.5 * blush)
                lx = look[0] + shake * 0.6
                for ex in (-20, 20):
                    if blink or eyes == 'closed':
                        curve(ctx, [(ex - 9, -2), (ex, 3), (ex + 9, -2)], lw=2.6)
                    elif eyes == 'soft':
                        curve(ctx, [(ex - 9, 0), (ex, -6), (ex + 9, 0)], lw=2.8)
                    else:
                        ellipse(ctx, ex, -2, 9, 10, (1, 1, 1), lw=2.2)
                        circle(ctx, ex + lx * 4, -1 + look[1] * 3, 4, INK, lw=0)
                    line(ctx, [(ex - 10, -18), (ex + 10, -20 + (2 if ex > 0 else -2))], lw=3.2)
                blob(ctx, [(-4, 4), (6, 18), (2, 26), (-10, 26), (-12, 20)], shade(st['skin'], 0.92), lw=2.4)
                if mouth == 'kind':
                    curve(ctx, [(-14, 40), (0, 46), (14, 40)], lw=3)
                elif mouth == 'tut':
                    ellipse(ctx, 0, 42, 7, 4, hexc('5a2a26'), lw=2.4)
                elif mouth == 'smile':
                    curve(ctx, [(-18, 36), (0, 50), (18, 36)], lw=3.2)
                elif mouth == 'flat':
                    line(ctx, [(-12, 42), (12, 42)], lw=3)


# ------------------------------------------------------------------- fox ----

FOX = hexc('d9762e')


def fox_flat(ctx, x, y, s=1.0):
    """Cartoon fox, flat out in the road: legs stiff, eyes crossed."""
    with tf(ctx, x, y, 0, s):
        blob(ctx, [(-70, -10), (-110, -40), (-150, -30), (-160, -12), (-130, -4)], FOX)    # tail
        blob(ctx, [(-150, -30), (-160, -12), (-138, -10)], hexc('f6f1e6'), lw=2.4)
        for lx in (-50, -30, 30, 50):
            limb(ctx, [(lx, -10), (lx + (lx > 0) * 30 - (lx < 0) * 30, -50)], 10, shade(FOX, 0.85))
            circle(ctx, lx + (lx > 0) * 30 - (lx < 0) * 30, -52, 6, INK, lw=0)
        blob(ctx, [(-74, -6), (-60, -30), (40, -34), (70, -20), (66, 0), (-60, 2)], FOX)
        blob(ctx, [(-20, -2), (30, -6), (50, 0), (-10, 4)], hexc('f6f1e6'), lw=0)
        with tf(ctx, 86, -16):
            blob(ctx, [(-24, -14), (10, -20), (52, -2), (10, 14), (-22, 10)], FOX)
            poly(ctx, [(-12, -16), (-24, -42), (2, -20)], FOX, lw=2.6)
            poly(ctx, [(4, -18), (0, -44), (18, -16)], FOX, lw=2.6)
            circle(ctx, 52, -2, 5, INK, lw=0)
            for dx in (0,):
                line(ctx, [(4 + dx, -10), (14 + dx, 0)], lw=2.6)
                line(ctx, [(14 + dx, -10), (4 + dx, 0)], lw=2.6)
            limb(ctx, [(30, 8), (36, 20)], 6, hexc('e86a8a'), lw=1.8)
