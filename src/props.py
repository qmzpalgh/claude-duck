"""Shared set dressing and props."""
import math
import random

from engine import (INK, LW, H, W, blob, circle, curve, ellipse, hatch, hexc,
                    limb, line, mix, poly, rect, set_col, shade, text, tf, vgrad)

NIGHT_SKY = (hexc('2c3a4f'), hexc('5a6b80'))
CAR_COL = hexc('7f9a86')       # Colin's tired little green hatchback
WALL = hexc('e6d6b4')
WALL2 = hexc('cdbb98')
FLOOR = hexc('9b7652')
WOOD = hexc('a8754a')
LINO = hexc('c9c3a6')
HOSP_WALL = hexc('cfe0d6')
HOSP_FLOOR = hexc('a9b8ae')


# ------------------------------------------------------------------ weather --

_RAIN = None


def _rain_drops(n=220):
    global _RAIN
    if _RAIN is None:
        rnd = random.Random(3)
        _RAIN = [(rnd.random() * (W + 300), rnd.random() * H, 0.6 + rnd.random() * 0.8) for _ in range(n)]
    return _RAIN


def rain(ctx, t, alpha=0.5, slant=0.25, speed=900, length=34, col=(0.85, 0.9, 1.0), lw=1.6):
    for (x0, y0, k) in _rain_drops():
        y = (y0 + t * speed * k) % (H + 80) - 40
        x = (x0 - y * slant) % (W + 300) - 150
        set_col(ctx, col, alpha * (0.5 + 0.5 * k))
        ctx.set_line_width(lw * k)
        ctx.move_to(x, y)
        ctx.line_to(x - slant * length * k, y - length * k)
        ctx.stroke()


def glass_drops(ctx, t, x, y, w, h, n=40, seed=1, alpha=0.45):
    rnd = random.Random(seed)
    for i in range(n):
        dx, dy = rnd.random() * w, rnd.random() * h
        r = 2 + rnd.random() * 4
        life = (t * 0.7 + rnd.random()) % 1.0
        ellipse(ctx, x + dx, y + dy + life * 12, r, r * 1.2, (0.85, 0.92, 1.0), lw=1.0,
                ink=(0.6, 0.7, 0.8), alpha=alpha * (1 - life * 0.5))


# --------------------------------------------------------------------- cars --

def car_side(ctx, x, y, s=1.0, face=-1, col=CAR_COL, t=0.0, hazard=False, door=0.0, wheel_rot=0.0,
             lights=True, inside=None, crumple=0.0):
    """Little 1980s hatchback, side view. Origin at the ground under the middle.
    face=-1 points the bonnet left. door: 0 shut .. 1 open (drawn as a dark gap).
    inside(ctx): optional callback to draw someone in the cabin (before glass)."""
    with tf(ctx, x, y, 0, s * face, s):
        # body
        bonnet = 210 - crumple * 30
        blob(ctx, [(-200, -40), (-205, -80), (-170, -100), (-120, -160), (40, -168), (110, -112),
                   (bonnet, -96), (bonnet + 10, -60), (bonnet, -36), (-190, -34)], col, tension=0.6)
        # windows
        if inside:
            ctx.save()
            poly(ctx, [(-110, -150), (30, -156), (92, -110), (-150, -108)], hexc('b9c8cf'), lw=0)
            ctx.restore()
            inside(ctx)
        poly(ctx, [(-110, -150), (-30, -154), (-30, -110), (-150, -108)], hexc('9fb3be'), alpha=0.85 if not inside else 0.35)
        poly(ctx, [(-22, -154), (30, -156), (92, -110), (-22, -110)], hexc('9fb3be'), alpha=0.85 if not inside else 0.35)
        line(ctx, [(-100, -146), (-70, -120)], lw=3, ink=(1, 1, 1), alpha=0.5)
        # door line + handle
        line(ctx, [(-28, -152), (-28, -40)], lw=2.2)
        line(ctx, [(96, -106), (96, -40)], lw=2.2)
        rect(ctx, 0, -100, 22, 7, shade(col, 0.7), lw=1.8, r=3)
        if door > 0:
            poly(ctx, [(-26, -150), (94, -108), (94, -42), (-26, -42)], (0.12, 0.12, 0.16), alpha=0.85 * door)
        # bumpers + lights
        rect(ctx, -212, -56, 30, 18, hexc('8f8f8f'), lw=2.4, r=6)
        rect(ctx, bonnet - 12, -56, 30, 18, hexc('8f8f8f'), lw=2.4, r=6)
        rect(ctx, -205, -94, 16, 22, hexc('c43b2d'), lw=2.2, r=3)
        rect(ctx, bonnet - 8, -92, 14, 18, hexc('fff2b0'), lw=2.2, r=3)
        if hazard and (t % 0.8) < 0.4:
            circle(ctx, -197, -83, 24, (1.0, 0.65, 0.1), lw=0, alpha=0.35)
            rect(ctx, -205, -94, 16, 22, hexc('ffae2a'), lw=2.2, r=3)
            circle(ctx, bonnet, -83, 24, (1.0, 0.65, 0.1), lw=0, alpha=0.35)
        if lights:
            g_alpha = 0.18
            poly(ctx, [(bonnet + 6, -88), (bonnet + 420, -150), (bonnet + 420, 10)], (1, 0.95, 0.7), lw=0, alpha=g_alpha)
        # wheels
        for wx in (-130, 130):
            circle(ctx, wx, -30, 32, hexc('2a2a2e'))
            circle(ctx, wx, -30, 16, hexc('b5b5b5'), lw=2.2)
            with tf(ctx, wx, -30, wheel_rot):
                line(ctx, [(-10, 0), (10, 0)], lw=2)
                line(ctx, [(0, -10), (0, 10)], lw=2)


def car_rear(ctx, x, y, s=1.0, col=hexc('8a3b34'), glow=True, plate='YGR 486', hazard=False, t=0.0):
    """Hatchback seen from behind."""
    with tf(ctx, x, y, 0, s):
        blob(ctx, [(-120, -10), (-126, -90), (-100, -170), (100, -170), (126, -90), (120, -10)], col, tension=0.5)
        poly(ctx, [(-92, -160), (92, -160), (106, -104), (-106, -104)], hexc('6f8495'))
        rect(ctx, -110, -92, 220, 54, shade(col, 0.9), lw=2.4, r=6)
        for sx in (-1, 1):
            on = hazard and (t % 0.8) < 0.4
            c = hexc('ffae2a') if on else hexc('d83a2a')
            rect(ctx, sx * 96 - 18, -88, 36, 22, c, lw=2.2, r=4)
            if glow or on:
                circle(ctx, sx * 96, -77, 46, (1, 0.25, 0.15) if not on else (1, 0.6, 0.1), lw=0, alpha=0.22)
        rect(ctx, -44, -64, 88, 22, hexc('f2e9a8'), lw=2.2, r=3)
        text(ctx, plate, 0, -47, 19, font='DejaVu Sans Mono', align='center', bold=True)
        rect(ctx, -126, -34, 252, 18, hexc('6d6d6d'), lw=2.4, r=6)
        for sx in (-1, 1):
            rect(ctx, sx * 96 - 20, -18, 40, 22, hexc('222226'), lw=2.2, r=4)


# ---------------------------------------------------------------- interiors --

def room(ctx, wall=WALL, floor=FLOOR, horizon=520, skirting=True, paper=None):
    vgrad(ctx, 0, 0, W, horizon, shade(wall, 1.03), shade(wall, 0.93))
    if paper == 'stripes':
        for i in range(0, W, 48):
            rect(ctx, i, 0, 20, horizon, shade(wall, 0.95), lw=0)
    elif paper == 'diamonds':
        set_col(ctx, shade(wall, 0.9))
        for i in range(-10, W // 60 + 2):
            for j in range(0, horizon // 60 + 1):
                cx, cy = i * 60 + (j % 2) * 30, j * 60
                ctx.move_to(cx, cy - 8)
                ctx.line_to(cx + 6, cy)
                ctx.line_to(cx, cy + 8)
                ctx.line_to(cx - 6, cy)
                ctx.close_path()
        ctx.fill()
    vgrad(ctx, 0, horizon, W, H - horizon, shade(floor, 1.0), shade(floor, 0.8))
    if skirting:
        rect(ctx, -10, horizon - 18, W + 20, 20, shade(wall, 0.75), lw=2.4)


def window(ctx, x, y, w, h, sky=None, t=0.0, rain_on=False, curtains=hexc('b5534a'), night=False):
    sky = sky or ((hexc('2c3a4f'), hexc('4d5d72')) if night else (hexc('a9c7dd'), hexc('dfe9ec')))
    rect(ctx, x - 12, y - 12, w + 24, h + 24, hexc('f2eee4'))
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    vgrad(ctx, x, y, w, h, *sky)
    if rain_on:
        ctx.save()
        ctx.translate(x, y)
        rain(ctx, t, alpha=0.35)
        ctx.restore()
    ctx.restore()
    rect(ctx, x, y, w, h, None)
    line(ctx, [(x + w / 2, y), (x + w / 2, y + h)], lw=6, ink=hexc('f2eee4'))
    line(ctx, [(x, y + h / 2), (x + w, y + h / 2)], lw=6, ink=hexc('f2eee4'))
    rect(ctx, x, y, w, h, None)
    rect(ctx, x - 24, y + h + 8, w + 48, 16, hexc('f2eee4'))
    if curtains:
        for sx, d in ((x - 50, 1), (x + w + 10, -1)):
            blob(ctx, [(sx, y - 30), (sx + 40, y - 30), (sx + 40 + d * 6, y + h * 0.5), (sx + 44, y + h + 30),
                       (sx - 4, y + h + 30), (sx + 2, y + h * 0.5)], curtains, tension=0.6)
            for k in (12, 26):
                line(ctx, [(sx + k, y - 26), (sx + k + 2, y + h + 26)], lw=1.4, alpha=0.5)
        rect(ctx, x - 70, y - 40, w + 140, 12, hexc('6b4a33'), r=6)


def table_side(ctx, x, y, w=420, top=hexc('a8754a'), cloth=None):
    """Simple side-on table; y is the floor line."""
    rect(ctx, x - w / 2, y - 180, w, 22, top, r=4)
    for lx in (x - w / 2 + 24, x + w / 2 - 40):
        rect(ctx, lx, y - 160, 16, 160, shade(top, 0.85))
    if cloth:
        poly(ctx, [(x - w / 2 - 10, y - 182), (x + w / 2 + 10, y - 182), (x + w / 2 + 16, y - 120), (x - w / 2 - 16, y - 120)], cloth)


def vase(ctx, x, y, s=1.0, rot=0.0, flowers=True, col=hexc('5f88b8')):
    with tf(ctx, x, y, rot, s):
        if flowers:
            for (fx, fy, c) in ((-26, -118, hexc('f0c43c')), (0, -138, hexc('e8735c')), (26, -116, hexc('f0f0f0')),
                                (-12, -100, hexc('d65a8a')), (14, -96, hexc('f0c43c'))):
                line(ctx, [(0, -50), (fx, fy)], lw=4, ink=hexc('4f7a3a'))
                for k in range(5):
                    a = k * 2 * math.pi / 5
                    circle(ctx, fx + 9 * math.cos(a), fy + 9 * math.sin(a), 7, c, lw=2)
                circle(ctx, fx, fy, 5, hexc('f2a33a'), lw=2)
        blob(ctx, [(-16, -60), (16, -60), (12, -48), (28, -20), (22, 0), (-22, 0), (-28, -20), (-12, -48)], col)


def wall_clock(ctx, x, y, r, hh, mm, col=hexc('f4efe2'), rim=hexc('6b4a33')):
    circle(ctx, x, y, r + 6, rim)
    circle(ctx, x, y, r, col, lw=2)
    for k in range(12):
        a = k * math.pi / 6
        line(ctx, [(x + r * 0.82 * math.sin(a), y - r * 0.82 * math.cos(a)),
                   (x + r * 0.95 * math.sin(a), y - r * 0.95 * math.cos(a))], lw=2)
    am = mm / 60 * 2 * math.pi
    ah = (hh % 12 + mm / 60) / 12 * 2 * math.pi
    line(ctx, [(x, y), (x + r * 0.5 * math.sin(ah), y - r * 0.5 * math.cos(ah))], lw=4)
    line(ctx, [(x, y), (x + r * 0.78 * math.sin(am), y - r * 0.78 * math.cos(am))], lw=2.6)
    circle(ctx, x, y, 3, INK, lw=0)


def star_burst(ctx, x, y, r, col=hexc('fff2a0'), n=10, rot=0, alpha=1.0):
    pts = []
    for k in range(2 * n):
        a = math.radians(rot) + k * math.pi / n
        rr = r if k % 2 == 0 else r * 0.5
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    poly(ctx, pts, col, lw=3, alpha=alpha)


def stars_orbit(ctx, x, y, t, r=40, n=4):
    """Classic cartoon dizzy stars circling a head."""
    for k in range(n):
        a = t * 5 + k * 2 * math.pi / n
        star_burst(ctx, x + r * math.cos(a), y + r * 0.35 * math.sin(a), 9, n=5, rot=a * 40)


def motion_lines(ctx, pts_list, lw=2.2, alpha=0.7):
    for pts in pts_list:
        line(ctx, pts, lw=lw, alpha=alpha)


def hospital_bed(ctx, x, y, s=1.0, sheet=hexc('f4f6f2'), blanket=hexc('9cbad0')):
    """Side-on hospital bed, origin at floor centre."""
    with tf(ctx, x, y, 0, s):
        for lx in (-170, 160):
            rect(ctx, lx, -120, 10, 120, hexc('c9ccd0'))
            circle(ctx, lx + 5, -4, 8, hexc('555555'))
        rect(ctx, -190, -260, 14, 250, hexc('c9ccd0'), r=6)    # head rail
        rect(ctx, 176, -200, 14, 190, hexc('c9ccd0'), r=6)     # foot rail
        rect(ctx, -180, -140, 360, 24, hexc('d8dade'), r=4)
        rect(ctx, -176, -168, 352, 30, sheet, r=10)
        rect(ctx, -170, -176, 90, 26, hexc('ffffff'), r=12)  # pillow


def screen_curtain(ctx, x, y, w, h, col=hexc('a8c8bd')):
    rect(ctx, x - 10, y - 10, w + 20, 8, hexc('9aa0a6'), r=3)
    n = int(w // 40)
    for i in range(n):
        poly(ctx, [(x + i * 40, y), (x + i * 40 + 40, y), (x + i * 40 + 44, y + h), (x + i * 40 - 4, y + h)],
             shade(col, 0.95 if i % 2 else 1.0), lw=2)


def thought_hearts(ctx, x, y, t, n=3, s=1.0):
    for k in range(n):
        ph = (t * 0.6 + k / n) % 1.0
        hx = x + 30 * math.sin(ph * 6 + k)
        hy = y - ph * 120
        heart(ctx, hx, hy, 14 * s * (0.6 + ph * 0.6), alpha=1 - ph)


def heart(ctx, x, y, r, col=hexc('e0485a'), alpha=1.0):
    with tf(ctx, x, y):
        ctx.move_to(0, r * 0.9)
        ctx.curve_to(-r * 1.6, -r * 0.2, -r * 0.6, -r * 1.3, 0, -r * 0.4)
        ctx.curve_to(r * 0.6, -r * 1.3, r * 1.6, -r * 0.2, 0, r * 0.9)
        ctx.close_path()
        set_col(ctx, col, alpha)
        ctx.fill_preserve()
        set_col(ctx, INK, alpha)
        ctx.set_line_width(2.4)
        ctx.stroke()
