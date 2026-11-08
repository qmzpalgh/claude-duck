"""Tiny cut-out animation engine on top of Cairo.

Everything is drawn with vector shapes: a fill plus a dark ink outline, in the
spirit of 1950s/70s British cut-out cartoons. Motion is held "on twos"
(12 drawings a second on a 24 fps timeline) for that economical, jerky charm.
"""
import math
import os
import subprocess

import cairo
import numpy as np

W, H = 1280, 720
FPS = 24
STEP = 2                     # animate on twos
INK = (0.12, 0.09, 0.08)
LW = 3.2                     # standard outline width

# ----------------------------------------------------------------- timing ---

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def seg(t, t0, t1):
    """0..1 progress of t through [t0, t1], eased."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return smooth((t - t0) / (t1 - t0))


def lin(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def lerp(a, b, x):
    if isinstance(a, (tuple, list)):
        return tuple(lerp(p, q, x) for p, q in zip(a, b))
    return a + (b - a) * x


def keys(t, ks, ease=smooth):
    """Interpolate through [(time, value), ...]. Values may be numbers or tuples."""
    if t <= ks[0][0]:
        return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t <= t1:
            return lerp(v0, v1, ease((t - t0) / (t1 - t0)) if t1 > t0 else 1)
    return ks[-1][1]


def step_keys(t, ks):
    """Hold values: the last key whose time has passed."""
    v = ks[0][1]
    for tk, vk in ks:
        if t >= tk:
            v = vk
    return v


def wobble(t, rate=1.0, amp=1.0, seed=0.0):
    return amp * math.sin(t * rate * 2 * math.pi + seed)


def blink(t, period=3.7, seed=0.0):
    """True for a brief moment every `period` seconds."""
    return ((t + seed) % period) < 0.12


# ------------------------------------------------------------- colour/path --

def hexc(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def shade(c, k):
    return tuple(clamp(v * k) for v in c)


def mix(c1, c2, k):
    return tuple(a + (b - a) * k for a, b in zip(c1, c2))


def set_col(ctx, c, a=1.0):
    if len(c) == 4:
        ctx.set_source_rgba(*c)
    else:
        ctx.set_source_rgba(c[0], c[1], c[2], a)


def fill_stroke(ctx, fill, lw=LW, ink=INK, alpha=1.0):
    if fill is not None:
        set_col(ctx, fill, alpha)
        if lw:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if lw:
        set_col(ctx, ink, alpha)
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.new_path()


def ellipse(ctx, x, y, rx, ry, fill=None, lw=LW, ink=INK, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    fill_stroke(ctx, fill, lw, ink, alpha)


def circle(ctx, x, y, r, fill=None, lw=LW, ink=INK, alpha=1.0):
    ellipse(ctx, x, y, r, r, fill, lw, ink, alpha)


def rect(ctx, x, y, w, h, fill=None, lw=LW, ink=INK, r=0, alpha=1.0):
    if r:
        r = min(r, w / 2, h / 2)
        ctx.new_sub_path()
        ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        ctx.close_path()
    else:
        ctx.rectangle(x, y, w, h)
    fill_stroke(ctx, fill, lw, ink, alpha)


def poly(ctx, pts, fill=None, lw=LW, ink=INK, close=True, alpha=1.0):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()
    fill_stroke(ctx, fill if close else None, lw, ink, alpha)


def _catmull(pts, closed=True, tension=0.5):
    n = len(pts)
    segs = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else pts[(i + 1) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
        segs.append((c1, c2, p2))
    return segs


def blob(ctx, pts, fill=None, lw=LW, ink=INK, closed=True, tension=1.0, alpha=1.0):
    """Smooth curve through points (Catmull-Rom)."""
    ctx.move_to(*pts[0])
    for c1, c2, p in _catmull(pts, closed, tension):
        ctx.curve_to(*c1, *c2, *p)
    if closed:
        ctx.close_path()
        fill_stroke(ctx, fill, lw, ink, alpha)
    else:
        fill_stroke(ctx, None, lw, ink, alpha)


def line(ctx, pts, lw=LW, ink=INK, alpha=1.0):
    poly(ctx, pts, None, lw, ink, close=False, alpha=alpha)


def curve(ctx, pts, lw=LW, ink=INK, alpha=1.0, tension=1.0):
    blob(ctx, pts, None, lw, ink, closed=False, tension=tension, alpha=alpha)


def limb(ctx, pts, width, fill, ink=INK, lw=LW):
    """A cut-out limb: a thick polyline with an ink outline and round ends."""
    for col, wd in ((ink, width + 2 * lw), (fill, width)):
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        set_col(ctx, col)
        ctx.set_line_width(wd)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()


def chain(x, y, segs):
    """Forward kinematics: segs = [(length, absolute_angle_deg), ...] -> points.
    Angle 0 points straight down, positive swings forward (towards +x)."""
    pts = [(x, y)]
    for L, a in segs:
        r = math.radians(a)
        x, y = x + L * math.sin(r), y + L * math.cos(r)
        pts.append((x, y))
    return pts


def text(ctx, s, x, y, size, font='Caveat', col=INK, align='left', alpha=1.0,
         bold=False, angle=0.0):
    ctx.save()
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    ctx.translate(x, y)
    ctx.rotate(math.radians(angle))
    dx = {'left': 0, 'center': -ext.x_advance / 2, 'right': -ext.x_advance}[align]
    ctx.move_to(dx, 0)
    set_col(ctx, col, alpha)
    ctx.show_text(s)
    ctx.restore()
    return ext.x_advance


class tf:
    """Context manager: save/translate/rotate/scale/restore."""

    def __init__(self, ctx, x=0, y=0, rot=0, sx=1, sy=None):
        self.ctx, self.a = ctx, (x, y, rot, sx, sx if sy is None else sy)

    def __enter__(self):
        x, y, rot, sx, sy = self.a
        self.ctx.save()
        self.ctx.translate(x, y)
        if rot:
            self.ctx.rotate(math.radians(rot))
        if sx != 1 or sy != 1:
            self.ctx.scale(sx, sy)
        return self.ctx

    def __exit__(self, *a):
        self.ctx.restore()


def bg(ctx, col):
    set_col(ctx, col)
    ctx.paint()


def vgrad(ctx, x, y, w, h, c1, c2):
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *c1)
    g.add_color_stop_rgb(1, *c2)
    ctx.rectangle(x, y, w, h)
    ctx.set_source(g)
    ctx.fill()


def hatch(ctx, x, y, w, h, gap=14, col=None, lw=1.2, alpha=0.25, angle=1.0):
    """Light pencil hatching, a nod to the storyboards."""
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    set_col(ctx, col or INK, alpha)
    ctx.set_line_width(lw)
    for i in range(int(-h / gap) - 2, int(w / gap) + 2):
        x0 = x + i * gap
        ctx.move_to(x0, y + h)
        ctx.line_to(x0 + h * angle, y)
    ctx.stroke()
    ctx.restore()


# ------------------------------------------------------------ paper / grade --

_PAPER = None


def paper_surface():
    """A subtle paper-grain + vignette overlay, generated once."""
    global _PAPER
    if _PAPER is not None:
        return _PAPER
    rng = np.random.default_rng(7)
    n = rng.normal(0, 1, (H // 2, W // 2))
    # soften the grain a little
    k = np.ones((3, 3)) / 9
    from scipy.signal import convolve2d
    n = convolve2d(n, k, mode='same', boundary='wrap')
    n = np.kron(n, np.ones((2, 2)))
    fib = rng.normal(0, 1, (H, W // 8)).repeat(8, axis=1)[:, :W] * 0.25
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    vig = np.clip(d - 0.55, 0, 1) ** 1.6 * 0.9
    dark = np.clip(0.035 + 0.05 * (n + fib) + vig, 0, 1)
    a = (dark * 255).astype(np.uint8)
    buf = np.zeros((H, W, 4), np.uint8)
    buf[..., 0] = 20   # warm brown grain (BGRA, premultiplied)
    buf[..., 1] = 28
    buf[..., 2] = 40
    buf[..., 0] = (buf[..., 0].astype(int) * a // 255).astype(np.uint8)
    buf[..., 1] = (buf[..., 1].astype(int) * a // 255).astype(np.uint8)
    buf[..., 2] = (buf[..., 2].astype(int) * a // 255).astype(np.uint8)
    buf[..., 3] = a
    surf = cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, W, H)
    _PAPER = (surf, buf)
    return _PAPER


def apply_paper(ctx):
    surf, _ = paper_surface()
    ctx.save()
    ctx.set_source_surface(surf, 0, 0)
    ctx.paint()
    ctx.restore()


# --------------------------------------------------------------- shots ------

class Shot:
    """One continuous piece of film. draw(ctx, t) paints a frame at time t.

    fade_in/fade_out: seconds from/to black.
    dissolve: seconds of cross-dissolve from the previous shot's last frame.
    sfx: list of (time, name, gain) cues, relative to the shot start.
    """

    def __init__(self, name, dur, draw, fade_in=0.0, fade_out=0.0, dissolve=0.0,
                 sfx=None, shake=None, paper=True):
        self.name, self.dur, self.draw = name, dur, draw
        self.fade_in, self.fade_out, self.dissolve = fade_in, fade_out, dissolve
        self.sfx = sfx or []
        self.shake = shake or []          # [(t, duration, amplitude)]
        self.paper = paper
        self.prev = None

    def frame_count(self):
        return int(round(self.dur * FPS))

    def render_frame(self, surf, i):
        ctx = cairo.Context(surf)
        t = (i // STEP) * STEP / FPS      # hold drawings for two frames
        ox = oy = 0.0
        for (t0, d, amp) in self.shake:
            if t0 <= t < t0 + d:
                k = 1 - (t - t0) / d
                ox += amp * k * math.sin(t * 91.0)
                oy += amp * k * math.cos(t * 73.0)
        ctx.save()
        ctx.translate(ox, oy)
        if ox or oy:
            ctx.translate(W / 2, H / 2)
            ctx.scale(1.03, 1.03)
            ctx.translate(-W / 2, -H / 2)
        self.draw(ctx, t)
        ctx.restore()
        if self.paper:
            apply_paper(ctx)
        if self.dissolve and t < self.dissolve and self.prev is not None:
            a = 1 - smooth(t / self.dissolve)
            ctx.set_source_surface(self.prev, 0, 0)
            ctx.paint_with_alpha(a)
        fade = 0.0
        if self.fade_in and t < self.fade_in:
            fade = 1 - t / self.fade_in
        tt = t + STEP / FPS
        if self.fade_out and tt > self.dur - self.fade_out:
            fade = max(fade, clamp((tt - (self.dur - self.fade_out)) / self.fade_out))
        if fade > 0:
            ctx.set_source_rgba(0, 0, 0, smooth(fade))
            ctx.paint()

    def last_frame(self):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        n = self.frame_count()
        saved = self.fade_out
        self.fade_out = 0
        self.render_frame(surf, n - 1)
        self.fade_out = saved
        return surf

    def still(self, t, path):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.render_frame(surf, int(t * FPS))
        surf.write_to_png(path)

    def render(self, path):
        tmp = path[:-4] + '.part.mp4'
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra',
               '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264',
               '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
               '-r', str(FPS), tmp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        n = self.frame_count()
        last = None
        for i in range(n):
            if i % STEP == 0 or last is None:
                self.render_frame(surf, i)
                surf.flush()
                last = bytes(surf.get_data())
            p.stdin.write(last)
        p.stdin.close()
        if p.wait() != 0:
            raise RuntimeError('ffmpeg failed for ' + path)
        os.replace(tmp, path)
