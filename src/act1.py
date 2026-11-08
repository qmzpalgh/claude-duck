"""Act one: the drive home, the fox, the duck, the letter."""
import math

from engine import (INK, H, W, Shot, bg, blob, circle, curve, ellipse, hatch,
                    hexc, keys, lerp, limb, lin, line, poly, rect, seg, set_col,
                    shade, smooth, step_keys, text, tf, vgrad, blink)
from props import (CAR_COL, FLOOR, NIGHT_SKY, WALL, car_rear, car_side,
                   glass_drops, rain, room, table_side, vase)
from puppets import (COLIN, colin, colin_face, duck, fox_flat, pose, walk_pose)


# ------------------------------------------------------------------ title --

def draw_title(ctx, t):
    bg(ctx, hexc('efe6d2'))
    # double ruled border, silent-film style
    rect(ctx, 60, 50, W - 120, H - 100, None, lw=5)
    rect(ctx, 76, 66, W - 152, H - 132, None, lw=1.6)
    for (cx, cy) in ((76, 66), (W - 76, 66), (76, H - 66), (W - 76, H - 66)):
        circle(ctx, cx, cy, 9, hexc('efe6d2'), lw=2)
    a = seg(t, 0.3, 1.4)
    text(ctx, 'DUCK', W / 2, 360, 200, font='Abril Fatface', align='center', alpha=a)
    text(ctx, 'a silent picture', W / 2, 430, 40, font='Caveat', align='center', alpha=seg(t, 1.2, 2.0))
    # the duck waddles across underneath the title, stops, looks at us
    dx = keys(t, [(1.6, -80), (4.2, 640)], ease=lambda x: x)
    walking = 1.6 < t < 4.2
    look = (0, 0) if t < 4.4 else (-1, 0.3)
    duck(ctx, dx, 590, 0.75, walk=(t * 2.2) if walking else None, blink=blink(t, 2.3),
         look=look, quack=1.0 if 4.7 < t < 4.95 else 0.0)
    text(ctx, 'from the screenplay by Damian Gason', W / 2, 650, 26, font='Patrick Hand',
         align='center', alpha=seg(t, 2.2, 3.0) * 0.8)


# ------------------------------------------------------- windscreen (POV) --

def windscreen(ctx, t, fox_t=None, ahead=True, wiper_period=1.3):
    # road at night in the rain
    vgrad(ctx, 0, 0, W, 330, *NIGHT_SKY)
    vgrad(ctx, 0, 330, W, H - 330, hexc('3d4552'), hexc('22262e'))
    poly(ctx, [(560, 330), (720, 330), (1180, H), (100, H)], hexc('31353d'), lw=0)
    for k in range(6):  # centre dashes rushing towards us
        ph = (t * 1.4 + k / 6) % 1.0
        yy = 330 + (H - 330) * ph ** 2
        ww = 3 + 26 * ph ** 2
        rect(ctx, 640 - ww / 2, yy, ww, 6 + 40 * ph ** 2, hexc('e9e1c8'), lw=0, alpha=0.9)
    # roadside posts
    for k in range(4):
        ph = (t * 1.1 + k / 4) % 1.0
        for sx in (-1, 1):
            xx = 640 + sx * (90 + 700 * ph ** 2)
            yy = 330 + (H - 330) * ph ** 2
            rect(ctx, xx - 2 - 6 * ph, yy - 10 - 70 * ph, 4 + 12 * ph, 10 + 70 * ph, hexc('dcdcdc'), lw=1.5)
    # headlight pool
    poly(ctx, [(420, H), (860, H), (700, 360), (580, 360)], (1, 0.95, 0.7), lw=0, alpha=0.12)
    if ahead:
        car_rear(ctx, 640 + 14 * math.sin(t * 0.7), 400, 0.55, plate='', glow=True)
    if fox_t is not None and 0 <= fox_t < 0.9:
        k = fox_t / 0.6
        fx = lerp(330, 760, k)
        fs = 0.55 + 0.25 * k
        with tf(ctx, fx, 610, 0, fs):
            leg = math.sin(fox_t * 40) * 18
            blob(ctx, [(-150, -40), (-120, -70), (-70, -60), (-60, -40)], hexc('d9762e'))
            for lx, a in ((-40, leg), (-20, -leg), (40, -leg), (60, leg)):
                limb(ctx, [(lx, -40), (lx + a, 0)], 10, shade(hexc('d9762e'), 0.8))
            blob(ctx, [(-70, -40), (-50, -78), (60, -84), (80, -60), (60, -36)], hexc('d9762e'))
            with tf(ctx, 90, -80):
                blob(ctx, [(-24, -14), (10, -20), (48, 0), (10, 14), (-22, 10)], hexc('d9762e'))
                poly(ctx, [(-12, -16), (-20, -42), (2, -20)], hexc('d9762e'))
                ellipse(ctx, 6, -6, 7, 8, (1, 1, 1), lw=2)
                circle(ctx, 10, -4, 3.5, INK, lw=0)
    # glass, drops, wipers
    glass_drops(ctx, t, 0, 0, W, H - 120, n=60)
    rain(ctx, t, alpha=0.25, slant=0.05, speed=500)
    ph = (t % wiper_period) / wiper_period
    ang = -70 + 140 * (0.5 - 0.5 * math.cos(ph * 2 * math.pi))
    for px in (330, 860):
        with tf(ctx, px, H - 70, ang):
            limb(ctx, [(0, 0), (0, -460)], 6, hexc('222'), lw=1.5)
            rect(ctx, -5, -470, 10, 300, hexc('151515'), lw=1.5, r=4)
    # A-pillars, roof lining, dashboard
    poly(ctx, [(0, 0), (150, 0), (40, H), (0, H)], hexc('2b2e33'))
    poly(ctx, [(W, 0), (W - 150, 0), (W - 40, H), (W, H)], hexc('2b2e33'))
    poly(ctx, [(0, 0), (W, 0), (W, 34), (0, 34)], hexc('3a3d42'))
    rect(ctx, 590, 34, 100, 46, hexc('2b2e33'), r=8)    # mirror
    blob(ctx, [(-20, H), (-20, H - 110), (300, H - 140), (980, H - 140), (1300, H - 110), (1300, H)], hexc('3b3530'), tension=0.4)


def wiper_cues(dur, period=1.3, offset=0.0):
    out, t = [], period / 2 + offset
    while t < dur:
        out.append((t, 'wiper', 0.35))
        t += period / 2
    return out


def draw_pov(ctx, t):
    windscreen(ctx, t)


# ------------------------------------------------------------ Colin driving --

def car_interior(ctx, t, colin_kw=None, sway=True, zoom=1.55, focus=(500, 330)):
    bob = 2 * math.sin(t * 9) if sway else 0
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(zoom, zoom)
    ctx.translate(-focus[0], -focus[1])
    # outside, through the side window: night, passing street lamps
    vgrad(ctx, 0, 0, W, H, hexc('2f3b4e'), hexc('1d232c'))
    for k in range(3):
        ph = ((t * 0.45 + k / 3) % 1.0)
        lx = W + 200 - ph * (W + 600)
        circle(ctx, lx, 170, 70, (1, 0.85, 0.5), lw=0, alpha=0.15)
        circle(ctx, lx, 170, 14, (1, 0.92, 0.65), lw=0)
        rect(ctx, lx - 4, 180, 8, 400, hexc('3a3f48'), lw=1.5)
    rain(ctx, t, alpha=0.35, slant=-0.9, speed=700)
    glass_drops(ctx, t, 0, 0, W, 470, n=30, seed=5, alpha=0.35)
    # car body interior
    with tf(ctx, 0, bob):
        poly(ctx, [(-10, 470), (W + 10, 470), (W + 10, H + 10), (-10, H + 10)], hexc('4b4f58'))
        line(ctx, [(-10, 500), (W + 10, 500)], lw=2, alpha=0.6)
        poly(ctx, [(-10, -10), (W + 10, -10), (W + 10, 40), (-10, 60)], hexc('5b5f68'))
        poly(ctx, [(980, -10), (1100, -10), (1290, 470), (1180, 470)], hexc('3e4249'))   # A pillar
        # seat
        blob(ctx, [(240, 520), (230, 280), (300, 240), (360, 260), (380, 520)], hexc('6b4e3a'), tension=0.5)
        rect(ctx, 250, 470, 420, 70, hexc('6b4e3a'), r=20)
        rect(ctx, 270, 180, 90, 80, hexc('6b4e3a'), r=24)         # headrest
        kw = dict(x=420, y=470, s=1.05, th_n=84, sh_n=-62, th_f=80, sh_f=-60, ua_n=78, fa_n=22,
                  ua_f=74, fa_f=26, lean=4, mouth='frown', lid=0.45, brow=0.8)
        if colin_kw:
            kw.update(colin_kw)
        p = colin(ctx, **kw)
        hx, hy = p['_far_arm'][2]
        wx, wy = kw['x'] + hx * kw['s'] + 6, kw['y'] + hy * kw['s'] - 4
        # steering wheel (in front of hands, seen edge-on)
        with tf(ctx, wx, wy, 14):
            ellipse(ctx, 0, 0, 20, 96, None, lw=16, ink=hexc('1f1f22'))
            ellipse(ctx, 0, 0, 20, 96, None, lw=3, ink=hexc('3a3a40'))
        limb(ctx, [(wx + 8, wy + 20), (wx + 150, 470)], 18, hexc('1f1f22'))
        poly(ctx, [(760, 470), (1290, 420), (1290, H + 10), (760, H + 10)], hexc('3b3530'))
    ctx.restore()
    return bob


def draw_drive(ctx, t):
    sigh = seg(t, 1.6, 2.2) - seg(t, 2.4, 3.2)
    car_interior(ctx, t, dict(lean=4 - sigh * 6, head=-sigh * 6 + 4,
                              eyes='closed' if 1.9 < t < 2.6 else 'open', y=470 - sigh * 6))


def draw_box(ctx, t):
    """Storyboards 3-4: the box of office keepsakes on the passenger seat."""
    jig = 3 * math.sin(t * 9) + (6 if (t % 1.7) < 0.1 else 0)
    vgrad(ctx, 0, 0, W, H, hexc('2f3b4e'), hexc('1d232c'))
    rain(ctx, t, alpha=0.3, slant=-0.9, speed=700)
    poly(ctx, [(-10, 300), (W + 10, 300), (W + 10, H + 10), (-10, H + 10)], hexc('4b4f58'))
    blob(ctx, [(140, H + 20), (160, 420), (260, 380), (1100, 380), (1180, 430), (1200, H + 20)], hexc('6b4e3a'), tension=0.5)
    with tf(ctx, 640, 560 + jig):
        # plant
        for k in range(9):
            a = -60 + k * 15
            limb(ctx, [(70, -190), (70 + 90 * math.sin(math.radians(a)), -190 - 120 * math.cos(math.radians(a)))],
                 7, hexc('4f7a3a'), lw=2)
            ellipse(ctx, 70 + 100 * math.sin(math.radians(a)), -190 - 130 * math.cos(math.radians(a)), 16, 10,
                    hexc('6aa04c'), lw=2)
        rect(ctx, 30, -230, 80, 70, hexc('c0613f'), r=6)
        # desk lamp
        limb(ctx, [(-160, -170), (-110, -300), (-30, -330)], 8, hexc('c6463c'), lw=2.4)
        poly(ctx, [(-40, -350), (10, -330), (0, -300), (-60, -320)], hexc('c6463c'))
        # mug with pens + framed photo of Lily (the cat in the photo too)
        rect(ctx, -90, -220, 56, 60, hexc('f0e8d8'), r=6)
        for k, c in enumerate(('3a5fa8', 'c43b2d', '2a2a2a')):
            line(ctx, [(-80 + k * 16, -220), (-84 + k * 18, -270)], lw=5, ink=hexc(c))
        rect(ctx, 130, -260, 90, 100, hexc('8b6a45'), r=4)
        rect(ctx, 142, -248, 66, 76, hexc('cfe1e8'), lw=2)
        circle(ctx, 165, -218, 12, hexc('f1c39b'), lw=2)
        circle(ctx, 190, -196, 9, hexc('7a7a7a'), lw=2)
        # the box
        poly(ctx, [(-240, -180), (240, -180), (250, 60), (-250, 60)], hexc('c9a46a'))
        poly(ctx, [(-240, -180), (-280, -210), (200, -210), (240, -180)], hexc('b58f55'))
        ellipse(ctx, -190, -150, 26, 10, hexc('6b4e2a'), lw=2)
        # label: a little scottie dog with a balloon
        rect(ctx, -100, -140, 300, 160, hexc('f3ecd9'), r=6)
        with tf(ctx, -20, -40, 0, 0.9):
            blob(ctx, [(-40, 0), (-44, -40), (-20, -58), (10, -60), (24, -80), (40, -76), (44, -56),
                       (30, -46), (30, 0), (14, 0), (12, -20), (-20, -20), (-24, 0)], hexc('2a2a2e'))
            poly(ctx, [(22, -78), (26, -98), (34, -78)], hexc('2a2a2e'))
            rect(ctx, -6, -52, 30, 7, hexc('c43b2d'), lw=1.6)
            curve(ctx, [(40, -76), (56, -100), (60, -120)], lw=1.6)
            ellipse(ctx, 62, -142, 20, 24, hexc('d9483b'))
        text(ctx, 'Bonnie', 90, -80, 40, font='Caveat', align='center', bold=True)
        text(ctx, 'Balloons', 90, -36, 40, font='Caveat', align='center', bold=True)


def draw_paper(ctx, t):
    """Storyboard 6: the newspaper on the back seat."""
    vgrad(ctx, 0, 0, W, H, hexc('5a4a3c'), hexc('3b3028'))
    blob(ctx, [(-40, 200), (300, 150), (1000, 160), (1320, 220), (1320, H + 20), (-40, H + 20)], hexc('6b4e3a'), tension=0.5)
    sway = 2 * math.sin(t * 9)
    # passing lamp light sweeps across
    lx = keys(t, [(0, -300), (3.4, W + 300)], ease=lambda x: x)
    with tf(ctx, 640, 420 + sway, -6):
        poly(ctx, [(-300, -250), (300, -250), (310, 250), (-310, 250)], hexc('ece6d6'))
        text(ctx, 'The Evening Gazette', 0, -200, 46, font='Abril Fatface', align='center')
        line(ctx, [(-280, -184), (280, -184)], lw=2)
        text(ctx, 'BALLOON FACTORY GOES BUST', 0, -142, 38, font='Abril Fatface', align='center')
        rect(ctx, -270, -120, 300, 190, hexc('cfcabb'), lw=2.4)
        # photo: one sad deflated balloon outside the factory gates
        rect(ctx, -250, -60, 260, 120, hexc('a6a091'), lw=1.6)
        for gx in range(-240, 0, 22):
            line(ctx, [(gx, -60), (gx, 60)], lw=2, alpha=0.6)
        blob(ctx, [(-150, 50), (-110, 30), (-80, 44), (-100, 58)], hexc('d9483b'), lw=2)
        curve(ctx, [(-150, 52), (-170, 40), (-176, 20)], lw=1.4)
        for k in range(10):
            line(ctx, [(50, -110 + k * 20), (270, -110 + k * 20)], lw=3, alpha=0.35)
        for k in range(5):
            line(ctx, [(-270, 100 + k * 26), (270, 100 + k * 26)], lw=3, alpha=0.35)
    ctx.save()
    g_alpha = 0.18
    poly(ctx, [(lx - 120, 0), (lx + 120, 0), (lx + 260, H), (lx + 20, H)], (1, 0.9, 0.6), lw=0, alpha=g_alpha)
    ctx.restore()
    rain(ctx, t, alpha=0.15, slant=-0.9, speed=700)


def draw_radio(ctx, t):
    """Storyboard 9: he tries the radio. Jolly music. He turns it straight off."""
    on = 0.6 < t < 2.3
    vgrad(ctx, 0, 0, W, H, hexc('3b3530'), hexc('2a2522'))
    rect(ctx, 300, 160, 680, 420, hexc('2e2a27'), r=20)
    rect(ctx, 400, 220, 480, 110, hexc('1c1a19'), r=10)
    disp = hexc('9fdc8a') if on else hexc('2f3a2c')
    rect(ctx, 520, 240, 240, 70, disp, r=6)
    if on:
        text(ctx, 'FM 77.4', 640, 292, 46, font='DejaVu Sans Mono', align='center', bold=True)
        # little dancing notes escaping the speaker
        for k in range(3):
            ph = ((t - 0.6) * 1.3 + k / 3) % 1
            nx, ny = 860 + 80 * ph + 20 * math.sin(ph * 9), 420 - 200 * ph
            text(ctx, '♪', nx, ny, 50, font='DejaVu Sans', col=hexc('f0d27a'), alpha=1 - ph)
    for k in range(5):
        rect(ctx, 420 + k * 92, 380, 70, 34, hexc('5a5550'), r=6)
    for k in range(2):
        circle(ctx, 470 + k * 340, 490, 34, hexc('5a5550'))
    for k in range(12):
        line(ctx, [(830, 360 + k * 14), (950, 360 + k * 14)], lw=4, alpha=0.4)
    # Colin's hand: in, press, out ... back in, press, out
    reach = keys(t, [(0.0, 0), (0.45, 1), (0.6, 1.08), (0.9, 0.2), (1.6, 0.2), (2.05, 1), (2.3, 1.08), (2.7, 0)])
    hx = lerp(W + 200, 650, reach)
    hy = lerp(560, 410, reach)
    limb(ctx, [(W + 300, 700), (hx + 60, hy + 50)], 70, COLIN['shirt'])
    rect(ctx, hx + 30, hy + 10, 60, 70, COLIN['shirt'], r=8)
    with tf(ctx, hx, hy, -25):
        blob(ctx, [(0, 0), (40, -12), (80, 0), (86, 40), (40, 56), (0, 40)], COLIN['skin'])
        limb(ctx, [(0, 10), (-46, 4)], 18, COLIN['skin'])


def draw_fox_pov(ctx, t):
    windscreen(ctx, t, fox_t=(t - 1.0), ahead=False)
    if 1.6 < t < 1.75:
        set_col(ctx, (1, 1, 1), 0.6)
        ctx.paint()


def draw_gasp(ctx, t):
    """Storyboard 7: hand to mouth."""
    car_interior(ctx, t + 3, dict(eyes='wide', mouth='o', lid=0, brow=-0.5, lean=-6, head=-8,
                                  ua_n=keys(t, [(0.2, 78), (0.45, 60)]), fa_n=keys(t, [(0.2, 22), (0.45, 133)])),
                 sway=False)


# ------------------------------------------------------------- roadside -----

def roadside_bg(ctx, t):
    vgrad(ctx, 0, 0, W, 470, hexc('243145'), hexc('4a5a70'))
    # distant hills + trees
    blob(ctx, [(-50, 470), (-40, 380), (200, 340), (480, 370), (760, 330), (1050, 360), (1330, 330), (1330, 470)],
         hexc('2a3a44'), lw=2, tension=0.6)
    for k, tx in enumerate((90, 260, 980, 1170)):
        rect(ctx, tx - 6, 330, 12, 70, hexc('2b2622'), lw=2)
        circle(ctx, tx, 320, 46 + 8 * (k % 2), hexc('243a33'), lw=2)
    vgrad(ctx, 0, 470, W, 90, hexc('3a3f47'), hexc('31353c'))   # road
    for k in range(6):
        rect(ctx, k * 240 + 40, 512, 120, 8, hexc('d8d2bc'), lw=0, alpha=0.8)
    vgrad(ctx, 0, 560, W, H - 560, hexc('34452f'), hexc('26331f'))   # verge


def grass(ctx, t, x0, x1, base, height, col=hexc('4e6b3a'), n=60, seed=0, sway=1.0, part=None):
    import random
    rnd = random.Random(seed)
    for i in range(n):
        x = x0 + (x1 - x0) * rnd.random()
        h = height * (0.6 + 0.6 * rnd.random())
        lean = (rnd.random() - 0.5) * 40 + sway * 8 * math.sin(t * 1.6 + x * 0.02)
        if part:
            px, pw, amt = part
            d = x - px
            if abs(d) < pw:
                lean += amt * (1 if d > 0 else -1) * (1 - abs(d) / pw)
        c = shade(col, 0.75 + 0.35 * rnd.random())
        tip = (x + lean, base - h)
        poly(ctx, [(x - 7, base), (x + 7, base), ((x + tip[0]) / 2 + 3, base - h / 2), tip,
                   ((x + tip[0]) / 2 - 3, base - h / 2)], c, lw=1.8)


def draw_roadside(ctx, t):
    roadside_bg(ctx, t)
    # car pulls up, sits with hazards, then drives off left
    cx = keys(t, [(0, 1500), (1.3, 420), (9.2, 420), (10.6, -500)])
    fox_x = 860
    fox_flat(ctx, fox_x, 538, 0.55)
    # Colin: out of the car (2.2), walk to fox, look, clutch stomach, walk back
    walk_out = (2.4, 4.0)
    walk_back = (6.6, 8.0)
    cpos = keys(t, [(2.2, 470), (walk_out[0], 470), (walk_out[1], 760), (walk_back[0], 760), (walk_back[1], 470)],
                ease=lambda x: x)
    show_colin = 2.1 < t < 8.3
    car_side(ctx, cx, 540, 0.72, face=-1, t=t, hazard=(1.5 < t < 9.2),
             door=1.0 if (2.0 < t < 2.5 or 7.9 < t < 8.4) else 0.0,
             wheel_rot=-cx * 0.8)
    if show_colin:
        if walk_out[0] < t < walk_out[1]:
            p = walk_pose(t * 1.6, face=1, s=0.62)
        elif walk_back[0] < t < walk_back[1]:
            p = walk_pose(t * 1.6, face=-1, s=0.62)
        else:
            clutch = seg(t, 4.6, 5.0) * (1 - seg(t, 6.2, 6.5))
            look_dn = seg(t, 4.0, 4.3)
            p = pose(face=1 if t < 6.4 else -1, s=0.62, head=12 * look_dn + 10 * clutch, lean=22 * clutch,
                     ua_n=10 * clutch + 8, fa_n=100 * clutch - 14, ua_f=14 * clutch, fa_f=96 * clutch,
                     mouth='wobble' if clutch > 0.5 else 'frown', lid=0.2, eyes='wide' if 4.3 < t < 4.6 else 'open',
                     look=(0.3, 0.8), th_n=-6 * clutch, th_f=6 * clutch, sh_n=8 * clutch)
            p['bob'] = 3 * math.sin(t * 30) * clutch
        p['x'] = cpos
        p['y'] = 545 - 0.62 * 152
        from puppets import person
        person(ctx, p, COLIN)
    # exhaust puffs as he leaves
    if t > 9.2:
        for k in range(3):
            ph = (t - 9.2 - k * 0.2)
            if 0 < ph < 1.2:
                circle(ctx, cx + 160 + ph * 60, 500 - ph * 40, 12 + ph * 20, (0.75, 0.78, 0.82), lw=2, alpha=1 - ph / 1.2)
    rain(ctx, t, alpha=0.35)
    grass(ctx, t, 940, 1300, H + 10, 190, n=40, seed=4)


def draw_duck_grass(ctx, t):
    """Storyboard 12-13: the duck peers out, having seen everything."""
    vgrad(ctx, 0, 0, W, H, hexc('263447'), hexc('38483d'))
    # the departing tail lights, small on the road behind
    tl = keys(t, [(0, 900), (5.5, -100)], ease=lambda x: x)
    for dx in (0, 46):
        circle(ctx, tl + dx, 300, 10, hexc('ff4030'), lw=0)
        circle(ctx, tl + dx, 300, 26, (1, 0.25, 0.15), lw=0, alpha=0.25)
    line(ctx, [(0, 315), (W, 315)], lw=2, alpha=0.5)
    grass(ctx, t, -40, W + 40, H + 30, 520, col=hexc('3f5a33'), n=70, seed=11, sway=0.6)
    rise = seg(t, 0.8, 1.6)
    # follow the car with her eyes; then a resolute blink
    look = (keys(t, [(1.8, 0.4), (4.5, -1.0)]), 0)
    eyes = 'open' if t < 4.6 else 'narrow'
    duck(ctx, 700, H + 330 - rise * 250, 2.6, face=-1, neck=0.8, blink=(2.9 < t < 3.05) or (4.4 < t < 4.55),
         look=look, eyes=eyes, tilt=keys(t, [(1.6, 0), (2.2, -8), (3.6, 6), (4.6, 0)]))
    grass(ctx, t, -40, W + 40, H + 30, 400, col=hexc('4e6b3a'), n=110, seed=12, sway=0.6, part=(700, 250, 40 * rise))
    rain(ctx, t, alpha=0.3)


# --------------------------------------------------------------- home -------

def draw_keys(ctx, t):
    """Storyboard 14: keys into the bowl. (Dissolve in.)"""
    room(ctx, wall=WALL, horizon=430, paper='stripes')
    rect(ctx, 180, 430, 920, 40, hexc('8b6a45'), r=6)     # hall table top
    rect(ctx, 200, 470, 880, 300, hexc('7a5a3a'))
    ellipse(ctx, 640, 430, 260, 58, hexc('d8b77a'))
    ellipse(ctx, 640, 422, 210, 40, hexc('c9a45f'), lw=2)
    drop = keys(t, [(0, 0), (0.6, 0), (0.9, 1)], ease=lambda x: x * x)
    kx, ky = 660, lerp(130, 420, drop)
    with tf(ctx, kx, ky, 20 if drop >= 1 else 0):
        circle(ctx, 0, 0, 16, None, lw=5, ink=hexc('9c9c9c'))
        for a in (-12, 14):
            with tf(ctx, 0, 14, a):
                rect(ctx, -5, 0, 10, 60, hexc('d4b648'), lw=2)
                for k in range(3):
                    rect(ctx, 5, 30 + k * 9, 8, 5, hexc('d4b648'), lw=1.4)
    if drop < 1:
        # hand above
        with tf(ctx, kx + 30, ky - 70):
            blob(ctx, [(-40, -20), (30, -40), (60, -10), (40, 30), (-30, 30)], COLIN['skin'])
            limb(ctx, [(50, -30), (360, -200)], 60, COLIN['shirt'])


def draw_card(ctx, t):
    """Storyboard 15: the card propped against the vase."""
    room(ctx, wall=WALL, horizon=470, paper='diamonds')
    rect(ctx, -20, 470, W + 40, 60, hexc('a8754a'))
    rect(ctx, -20, 530, W + 40, 200, hexc('7a5a3a'))
    vase(ctx, 880, 470, 2.4)
    pick = seg(t, 1.6, 2.4)
    with tf(ctx, 560, 470 - pick * 260, -8 + 12 * pick):
        poly(ctx, [(-160, 0), (140, 0), (160, -200), (-140, -200)], hexc('fbf6ea'))
        poly(ctx, [(140, 0), (180, -10), (160, -200)], hexc('e8e0cc'))
        text(ctx, 'Colin', 0, -80, 74, font='Caveat', align='center', angle=-4)
    if t > 1.2:
        reach = seg(t, 1.2, 1.6)
        hx, hy = 560 + 200, 470 - 120 - pick * 260
        hx = lerp(W + 100, hx, reach)
        limb(ctx, [(W + 300, hy + 150), (hx + 40, hy + 20)], 64, COLIN['shirt'])
        blob(ctx, [(hx - 30, hy - 20), (hx + 30, hy - 30), (hx + 50, hy + 20), (hx - 20, hy + 40)], COLIN['skin'])


def draw_reading(ctx, t, phase='before'):
    """Storyboard 18: Colin reads. A long pause. The lip wobbles."""
    room(ctx, wall=shade(WALL, 0.92), horizon=H + 10, skirting=False, paper='diamonds')
    rect(ctx, 960, -10, 330, H + 20, hexc('8b6a45'))      # door frame edge
    hatch(ctx, 960, 0, 330, H, gap=18, alpha=0.15)
    if phase == 'before':
        lid = keys(t, [(0, 0.1), (2.0, 0.1), (2.6, 0.0)])
        colin_face(ctx, 560, 300, 1.15, eyes='open', look=(0, 0.9), lid=lid, brow=0.2, mouth='flat')
    else:
        wob = t > 1.2
        colin_face(ctx, 560, 300, 1.15, eyes='open', look=(0.0, 0.2 if t < 2.4 else -0.2),
                   lid=keys(t, [(0, 0.15), (2.0, 0.5)]), brow=keys(t, [(0, 0.3), (1.5, 1.2)]),
                   mouth='wobble' if wob else 'frown', tear=lin(t, 2.6, 4.2) if t > 2.6 else 0.0)
    # the card, held up
    with tf(ctx, 520, 640, -6):
        poly(ctx, [(-140, 0), (140, 0), (150, -230), (-130, -230)], hexc('fbf6ea'))
        text(ctx, 'Colin', 0, -100, 60, font='Caveat', align='center', angle=-84)
        blob(ctx, [(-170, -60), (-120, -80), (-110, -20), (-160, 10)], COLIN['skin'])
        blob(ctx, [(170, -70), (120, -90), (110, -30), (160, 0)], COLIN['skin'])


LETTER = [
    "Dear Colin,",
    "",
    "I'm writing this letter to tell you that I'm leaving you.",
    "You're a good man, but as they say you only live",
    "once and I think I may be a lesbian. Anyway thanks",
    "for everything, take care.",
    "",
    "                    P.S. I have taken the cat.",
    "",
    "Love,",
    "",
    "Lily XOX",
]


def draw_letter(ctx, t):
    """Storyboard 17: the letter, written out line by line as he reads it."""
    bg(ctx, hexc('3a2f28'))
    with tf(ctx, 640, 370, -1.2):
        poly(ctx, [(-470, -330), (470, -330), (480, 330), (-480, 330)], hexc('fbf7ec'))
        for k in range(16):
            line(ctx, [(-440, -250 + k * 38), (440, -250 + k * 38)], lw=1.2, ink=hexc('a9c0d6'), alpha=0.6)
        line(ctx, [(-380, -320), (-380, 320)], lw=1.4, ink=hexc('d98a8a'), alpha=0.7)
        reveal = t * 1.15         # lines per second (paced for reading)
        y = -262
        for i, s in enumerate(LETTER):
            if not s:
                y += 34
                continue
            a = seg(reveal, i * 0.55, i * 0.55 + 0.5)
            if a > 0:
                text(ctx, s, -360, y, 37 if i else 42, font='Caveat', col=hexc('2b3a6a'), alpha=a)
            y += 44
        # a little heart dotting the sign-off
        if reveal > 11 * 0.55 + 0.5:
            from props import heart
            heart(ctx, -200, 225, 10, alpha=seg(reveal, 6.6, 7.0))


def draw_cat_bed(ctx, t):
    """Gag: the empty cat basket. One hair left behind."""
    room(ctx, wall=WALL, floor=FLOOR, horizon=420, paper='stripes')
    ellipse(ctx, 640, 560, 260, 70, hexc('b08a4e'))
    ellipse(ctx, 640, 540, 210, 50, hexc('c94f4f'))
    ellipse(ctx, 640, 530, 150, 30, hexc('d76969'), lw=2)
    rect(ctx, 930, 560, 120, 40, hexc('d9d0c0'), r=14)     # bowl
    text(ctx, 'TIBBLES', 990, 588, 22, font='Patrick Hand', align='center')
    # the hair, drifting down
    hy = keys(t, [(0, 380), (2.6, 528)])
    hx = 600 + 30 * math.sin(t * 3)
    curve(ctx, [(hx, hy), (hx + 8, hy - 6), (hx + 16, hy + 2)], lw=1.6)


def build():
    return [
        Shot('a00_title', 5.6, draw_title, fade_in=0.8, fade_out=0.8, sfx=[(4.7, 'quack', 0.6)]),
        Shot('a01_pov', 5.0, draw_pov, fade_in=1.2, sfx=[(0, 'rain_start', 0.0)] + wiper_cues(5.0)),
        Shot('a02_drive', 4.2, draw_drive, sfx=[(1.6, 'sigh_swoop', 0.4)]),
        Shot('a03_box', 3.4, draw_box),
        Shot('a04_paper', 3.4, draw_paper),
        Shot('a05_radio', 3.0, draw_radio, sfx=[(0.6, 'click', 0.5), (0.6, 'radio_jolly', 0.55), (2.3, 'click', 0.6)]),
        Shot('a06_fox', 2.2, draw_fox_pov, sfx=wiper_cues(1.5) + [(1.62, 'thud', 1.0)], shake=[(1.62, 0.5, 18)]),
        Shot('a07_gasp', 2.2, draw_gasp, sfx=[(0.15, 'gasp_sting', 0.5)]),
        Shot('a08_roadside', 10.8, draw_roadside,
             sfx=[(0.2, 'brakes', 0.5), (2.0, 'door', 0.5), (2.4, 'steps', 0.4), (4.4, 'gulp', 0.4),
                  (6.6, 'steps', 0.4), (8.0, 'door', 0.6), (9.1, 'engine', 0.5)]),
        Shot('a09_duck', 5.6, draw_duck_grass, fade_out=0.0),
        Shot('a10_keys', 2.4, draw_keys, dissolve=1.0, sfx=[(0.9, 'keys', 0.6), (0.0, 'rain_stop', 0.0)]),
        Shot('a11_card', 3.0, draw_card),
        Shot('a12_read', 3.2, lambda c, t: draw_reading(c, t, 'before'), sfx=[(0.3, 'paper', 0.5)]),
        Shot('a13_letter', 9.0, draw_letter),
        Shot('a14_catbed', 2.8, draw_cat_bed),
        Shot('a15_read2', 4.8, lambda c, t: draw_reading(c, t, 'after'), fade_out=0.6),
    ]
