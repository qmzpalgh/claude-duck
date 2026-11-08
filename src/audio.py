"""Code-synthesised score and sound effects (numpy only). No voices: it's a silent picture.

The music is a little concertina waltz with pizzicato bass and a glockenspiel,
in the spirit of the hornpipes that accompanied British cut-out cartoons.
"""
import math

import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
RNG = np.random.default_rng(11)


# ------------------------------------------------------------------ basics --

def t_axis(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.01, r=0.08, curve=1.0):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    na, nr = min(na, n), min(nr, n)
    e[:na] = np.linspace(0, 1, na)
    e[n - nr:] *= np.linspace(1, 0, nr) ** curve
    return e


def decay(n, tau):
    return np.exp(-np.arange(n) / SR / tau)


def noise(d):
    return RNG.normal(0, 1, int(d * SR))


def bp(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], btype='band')
    return lfilter(b, a, x)


def lp(x, f, order=2):
    b, a = butter(order, min(f / (SR / 2), 0.99), btype='low')
    return lfilter(b, a, x)


def hp(x, f, order=2):
    b, a = butter(order, f / (SR / 2), btype='high')
    return lfilter(b, a, x)


def sweep_sine(f0, f1, d, curve=1.0):
    t = t_axis(d)
    f = f0 + (f1 - f0) * (t / d) ** curve
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def saw_from_freq(f):
    ph = np.cumsum(f) / SR
    return 2 * (ph % 1.0) - 1


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) if len(x) else 0
    return x * (peak / m) if m > 0 else x


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def ntom(s):
    """'A4', 'C#5', 'Bb3' -> midi"""
    n = NOTE[s[0]]
    i = 1
    if s[i] == '#':
        n += 1
        i += 1
    elif s[i] == 'b':
        n -= 1
        i += 1
    return n + 12 * (int(s[i:]) + 1)


# ------------------------------------------------------------- instruments --

def reed(f, d, vol=1.0, vib=0.004, bright=1.0):
    """Concertina-ish free reed: two detuned voices, rich harmonics, a little bellows swell."""
    t = t_axis(d)
    n = len(t)
    out = np.zeros(n)
    vibr = 1 + vib * np.sin(2 * np.pi * 5.2 * t)
    for det in (0.9985, 1.0015):
        ff = f * det * vibr
        ph = np.cumsum(ff) / SR
        for h, amp in enumerate((1.0, 0.55, 0.42, 0.26, 0.18, 0.12, 0.08, 0.05), start=1):
            if f * h > 9000:
                break
            out += amp * (bright ** (h - 1)) * np.sin(2 * np.pi * h * ph)
    swell = 0.85 + 0.15 * np.sin(np.pi * np.clip(t / max(d, 1e-3), 0, 1))
    return out * env(n, 0.025, min(0.09, d * 0.4)) * swell * vol * 0.18


def pluck(f, d, vol=1.0, damp=0.996):
    """Karplus-Strong pizzicato."""
    n = int(d * SR)
    period = max(2, int(SR / f))
    buf = RNG.uniform(-1, 1, period)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = damp * 0.5 * (buf[i % period] + buf[(i + 1) % period])
    return lp(out, 2500) * env(n, 0.002, 0.03) * vol * 0.8


def pluck_fast(f, d, vol=1.0):
    """Cheap pizz: decaying harmonic stack (much quicker than KS for many notes)."""
    t = t_axis(d)
    n = len(t)
    out = np.zeros(n)
    for h, amp in enumerate((1.0, 0.5, 0.3, 0.18, 0.1), start=1):
        out += amp * np.sin(2 * np.pi * f * h * t) * decay(n, 0.35 / h)
    return out * env(n, 0.003, 0.03) * vol * 0.35


def bell(f, d, vol=1.0):
    t = t_axis(d)
    n = len(t)
    out = (np.sin(2 * np.pi * f * t) * decay(n, 0.9) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * decay(n, 0.35)
           + 0.18 * np.sin(2 * np.pi * f * 5.4 * t) * decay(n, 0.15))
    return out * env(n, 0.001, 0.05) * vol * 0.3


def bassoon(f, d, vol=1.0):
    t = t_axis(d)
    n = len(t)
    ph = np.cumsum(f * (1 + 0.003 * np.sin(2 * np.pi * 5 * t))) / SR
    sq = np.sign(np.sin(2 * np.pi * ph)) * 0.6 + 0.4 * (2 * (ph % 1) - 1)
    return lp(sq, 900) * env(n, 0.02, 0.05) * vol * 0.22


def timp(f, d, vol=1.0):
    t = t_axis(d)
    n = len(t)
    out = np.sin(2 * np.pi * f * t) * decay(n, 0.5) + 0.4 * lp(noise(d), 400) * decay(n, 0.08)
    return out * vol * 0.5


# --------------------------------------------------------------- sequencer --

def seq(notes, bpm, inst, vol=1.0, transpose=0, legato=0.92):
    """notes: 'A4/1 r/0.5 C5/0.5 ...'  (durations in beats). Chords: 'A3+C4+E4/1'."""
    beat = 60.0 / bpm
    items = notes.split()
    total = sum(float(it.split('/')[1]) for it in items) * beat
    out = np.zeros(int(total * SR) + SR)
    pos = 0.0
    for it in items:
        name, dur = it.split('/')
        d = float(dur) * beat
        if name != 'r':
            for nn in name.split('+'):
                f = mtof(ntom(nn) + transpose)
                x = inst(f, d * legato + 0.05, vol)
                i0 = int(pos * SR)
                out[i0:i0 + len(x)] += x[:len(out) - i0]
        pos += d
    return out[:int(total * SR)]


def mixin(dst, src, at, gain=1.0):
    i0 = int(at * SR)
    if i0 >= len(dst) or i0 + len(src) <= 0:
        return
    if i0 < 0:
        src = src[-i0:]
        i0 = 0
    n = min(len(src), len(dst) - i0)
    dst[i0:i0 + n] += src[:n] * gain


def fit(x, d, fade_in=0.05, fade_out=0.6):
    n = int(d * SR)
    if len(x) < n:
        x = np.concatenate([x, np.zeros(n - len(x))])
    x = x[:n].copy()
    x *= env(n, fade_in, fade_out)
    return x


def loop(x, d):
    n = int(d * SR)
    reps = n // max(1, len(x)) + 1
    return np.tile(x, reps)[:n]


# ---------------------------------------------------------------- the score --
# Main theme: a melancholy little waltz in A minor (3/4).
THEME_A = ('E5/3 A5/1 G5/1 E5/1 D5/2 C5/1 B4/3 C5/1 D5/1 E5/1 F5/1 E5/1 D5/1 E5/3 r/3 '
           'E5/3 A5/1 B5/1 C6/1 B5/1 A5/1 G5/1 E5/3 F5/1 E5/1 D5/1 C5/1 B4/1 G4/1 A4/3 r/3')
CHORDS_A = ['A2', 'A2', 'D3', 'E2', 'A2', 'D3', 'E2', 'E2', 'A2', 'A2', 'G2', 'E2', 'F2', 'G2', 'A2', 'A2']
TRIADS = {'A2': 'A3+C4+E4', 'D3': 'D4+F4+A4', 'E2': 'E3+G#3+B3', 'G2': 'G3+B3+D4', 'F2': 'F3+A3+C4',
          'C3': 'C4+E4+G4'}


def to_major(notes):
    """A minor -> A major (raise C, F, G)."""
    out = []
    for it in notes.split():
        name, d = it.split('/')
        if name != 'r':
            parts = []
            for nn in name.split('+'):
                if nn[0] in 'CFG' and nn[1] != '#':
                    nn = nn[0] + '#' + nn[1:]
                parts.append(nn)
            name = '+'.join(parts)
        out.append(name + '/' + d)
    return ' '.join(out)


MAJOR_TRIADS = {'A2': 'A3+C#4+E4', 'D3': 'D4+F#4+A4', 'E2': 'E3+G#3+B3', 'G2': 'F#3+A3+D4',
                'F2': 'D3+F#3+A3', 'C3': 'C#4+E4+A4'}
MAJOR_BASS = {'A2': 'A2', 'D3': 'D3', 'E2': 'E2', 'G2': 'F#2', 'F2': 'D3', 'C3': 'A2'}


def oompah(chords, bpm, major=False, vol=1.0, bass_inst=None):
    bass_inst = bass_inst or pluck_fast
    bass = ' '.join(f'{(MAJOR_BASS[c] if major else c)}/1 r/2' for c in chords)
    tri = MAJOR_TRIADS if major else TRIADS
    chord = ' '.join(f'r/1 {tri[c]}/1 {tri[c]}/1' for c in chords)
    b = seq(bass, bpm, bass_inst, vol * 1.3)
    c = seq(chord, bpm, lambda f, d, v: reed(f, min(d, 0.22), v * 0.45, bright=0.7), vol, legato=0.5)
    n = min(len(b), len(c))
    return b[:n] + c[:n]


def waltz(bpm=96, major=False, melody_vol=1.0, acc_vol=0.7, inst=reed):
    mel = to_major(THEME_A) if major else THEME_A
    m = seq(mel, bpm, inst, melody_vol)
    a = oompah(CHORDS_A, bpm, major, acc_vol)
    n = min(len(m), len(a))
    return m[:n] + a[:n]


HORNPIPE = ('A4/0.5 C5/0.5 E5/0.5 A5/0.5 G5/0.5 E5/0.5 C5/0.5 E5/0.5 F5/0.5 D5/0.5 A4/0.5 D5/0.5 '
            'E5/0.5 C5/0.5 B4/0.5 G#4/0.5 A4/0.5 C5/0.5 E5/0.5 A5/0.5 B5/0.5 G#5/0.5 E5/0.5 B4/0.5 '
            'C5/0.5 A4/0.5 E5/0.5 C5/0.5 A4/1 r/1 '
            'E5/0.5 F5/0.5 E5/0.5 D5/0.5 C5/0.5 D5/0.5 C5/0.5 B4/0.5 A4/0.5 B4/0.5 C5/0.5 D5/0.5 '
            'E5/1 E4/1 F5/0.5 E5/0.5 D5/0.5 C5/0.5 B4/0.5 C5/0.5 D5/0.5 B4/0.5 A4/0.5 E5/0.5 C5/0.5 E5/0.5 A4/1 r/1')
HORN_BASS = ('A2/1 E3/1 A2/1 E3/1 D3/1 A2/1 E2/1 B2/1 A2/1 E3/1 E2/1 B2/1 A2/1 E3/1 A2/1 r/1 '
             'C3/1 G2/1 A2/1 E2/1 F2/1 C3/1 E2/1 B2/1 F2/1 C3/1 E2/1 B2/1 A2/1 E3/1 A2/1 r/1')


def hornpipe(bpm=150, vol=1.0):
    m = seq(HORNPIPE, bpm, lambda f, d, v: reed(f, d, v, bright=1.1), vol, legato=0.8)
    b = seq(HORN_BASS, bpm, pluck_fast, vol * 1.4, legato=0.5)
    n = min(len(m), len(b))
    return m[:n] + b[:n]


def hospital_motif(vol=1.0):
    """The running gag: a deadpan little glockenspiel phrase for each hospital visit."""
    g = seq('E6/1 C6/1 A5/2 B5/1 G#5/1 E5/2 r/1 A5/1 r/2', 100, bell, vol)
    b = seq('A3+E4/2 r/2 E3+B3/2 r/2 A2+E3/2 r/2', 100, lambda f, d, v: reed(f, d, v * 0.4, bright=0.6), vol)
    n = min(len(g), len(b))
    return g[:n] + b[:n]


def sneaky(bpm=120, vol=1.0, bars=8):
    """Tiptoe pizzicato for the duck hunt."""
    pat = 'A2/0.5 r/0.5 C3/0.5 r/0.5 B2/0.5 r/0.5 Bb2/0.5 r/0.5 A2/0.5 r/0.5 E3/0.5 r/0.5 E2/0.5 r/1.5 '
    melody = ('r/4 E4/0.5 r/0.5 F4/0.5 r/0.5 E4/0.5 r/0.5 D#4/0.5 r/0.5 E4/1 r/3 '
              'r/4 C5/0.5 r/0.5 B4/0.5 r/0.5 Bb4/0.5 r/0.5 A4/0.5 r/0.5 E4/1 r/3 ')
    p = seq(pat * (bars // 2), bpm, pluck_fast, vol * 1.6, legato=0.4)
    m = seq(melody * (bars // 4), bpm, bassoon, vol * 1.2, legato=0.6)
    n = min(len(p), len(m))
    return p[:n] + m[:n]


def ostinato(d, vol=1.0):
    """Garage suspense: a pizzicato figure that speeds up."""
    out = np.zeros(int(d * SR) + SR)
    t = 0.0
    notes = ['E2', 'E2', 'F2', 'E2', 'E2', 'E2', 'G2', 'F2']
    i = 0
    while t < d:
        k = t / d
        gap = 0.32 - 0.16 * k
        x = pluck_fast(mtof(ntom(notes[i % 8])), 0.3, vol * (0.8 + 0.6 * k))
        mixin(out, x, t)
        if i % 4 == 0:
            mixin(out, reed(mtof(ntom(notes[i % 8]) + 12), gap * 3, vol * 0.25, bright=0.5), t)
        t += gap
        i += 1
    return out[:int(d * SR)]


def tremolo(d, notes=('E3', 'F3'), vol=1.0):
    out = np.zeros(int(d * SR))
    for nn in notes:
        f = mtof(ntom(nn))
        x = reed(f, d, vol * 0.5, bright=0.6)
        tt = t_axis(d)
        x = x * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * tt)) * np.linspace(0.3, 1, len(x))
        out += x[:len(out)]
    return out


def sting(chord=('E3', 'F3', 'Bb3', 'B3'), d=1.2, vol=1.0):
    out = np.zeros(int(d * SR))
    for nn in chord:
        out += reed(mtof(ntom(nn)), d, vol * 0.6, bright=1.2)[:len(out)]
    out += timp(82, d, vol)[:len(out)]
    return out * decay(len(out), d * 0.6)


def duck_motif(vol=1.0):
    return seq('G3/0.5 r/0.25 G3/0.25 B3/0.5 r/0.5 D4/0.25 r/0.25 C4/1', 110, bassoon, vol * 1.4)


def hmm_motif(vol=1.0):
    return seq('C4/0.5 r/0.25 Eb4/1', 100, bassoon, vol * 1.4)


def harp_gliss(d=1.2, vol=1.0, root=57):
    out = np.zeros(int(d * SR) + SR)
    steps = [0, 4, 7, 12, 16, 19, 24, 28, 31, 36]
    for k, s in enumerate(steps):
        mixin(out, pluck_fast(mtof(root + s), 1.2, vol * 0.7), k * d / len(steps) * 0.8)
    return out


def drone(d, f=55, vol=1.0):
    t = t_axis(d)
    x = reed(f, d, vol * 0.5, vib=0.002, bright=0.5) + reed(f * 1.5, d, vol * 0.25, bright=0.5)
    return x * (0.7 + 0.3 * np.sin(2 * np.pi * 0.3 * t))


# ---------------------------------------------------------------- effects ---

def fx_rain(d):
    x = lp(hp(noise(d), 400), 5000) * 0.12
    # occasional heavier drops
    for _ in range(int(d * 12)):
        at = RNG.uniform(0, d)
        drop = bp(noise(0.03), 1500, 6000) * decay(int(0.03 * SR), 0.008)
        mixin(x, drop * 0.25, at)
    return x


def fx_wiper():
    a = bp(noise(0.12), 200, 900) * decay(int(0.12 * SR), 0.04) * 0.6
    b = sweep_sine(900, 1300, 0.12) * env(int(0.12 * SR), 0.02, 0.05) * 0.08
    return a + b


def fx_thud():
    d = 0.5
    x = sweep_sine(90, 38, d) * decay(int(d * SR), 0.12) + lp(noise(d), 300) * decay(int(d * SR), 0.05) * 0.8
    return norm(x, 0.95)


def fx_click():
    return hp(noise(0.012), 2000) * decay(int(0.012 * SR), 0.002) * 0.8


def fx_radio_jolly():
    x = hornpipe(176, 0.9)[:int(1.7 * SR)]
    x = bp(x, 500, 3200, 3)
    return norm(x, 0.6) * env(len(x), 0.01, 0.02)


def fx_brakes():
    d = 0.8
    t = t_axis(d)
    x = np.sin(2 * np.pi * (2100 + 60 * np.sin(2 * np.pi * 13 * t)) * t) * 0.25
    x += bp(noise(d), 300, 2000) * 0.25
    return x * env(len(x), 0.05, 0.3)


def fx_door():
    d = 0.3
    x = sweep_sine(120, 60, d) * decay(int(d * SR), 0.06) + bp(noise(d), 800, 3000) * decay(int(d * SR), 0.015) * 0.6
    return norm(x, 0.8)


def fx_steps(n=4, gap=0.36, wet=True):
    out = np.zeros(int((n * gap + 0.3) * SR))
    for k in range(n):
        s = bp(noise(0.08), 200, 2500 if wet else 1200) * decay(int(0.08 * SR), 0.02)
        mixin(out, s * (0.5 + 0.1 * (k % 2)), k * gap)
    return out


def fx_gulp():
    return sweep_sine(320, 140, 0.16) * env(int(0.16 * SR), 0.01, 0.06) * 0.6


def fx_engine(d=1.8):
    t = t_axis(d)
    f = 40 + 30 * np.clip(t / 0.8, 0, 1)
    x = lp(saw_from_freq(f), 400) * (0.8 + 0.2 * np.sin(2 * np.pi * 18 * t))
    return x * env(len(x), 0.1, 0.9) * 0.6


def fx_keys():
    d = 0.5
    out = np.zeros(int(d * SR))
    for _ in range(9):
        f = RNG.uniform(3000, 7500)
        at = RNG.uniform(0, 0.25)
        x = np.sin(2 * np.pi * f * t_axis(0.15)) * decay(int(0.15 * SR), 0.03)
        mixin(out, x * 0.25, at)
    return out


def fx_paper():
    d = 0.5
    x = bp(noise(d), 1500, 7000) * (np.abs(RNG.normal(0, 1, int(d * SR))) > 1.2) * 0.4
    return lp(x, 6000) * env(len(x), 0.02, 0.2)


def fx_pen():
    d = 0.18
    return bp(noise(d), 2500, 7000) * env(int(d * SR), 0.01, 0.06) * 0.35


def fx_vacuum(d=3.0):
    t = t_axis(d)
    x = lp(saw_from_freq(np.full(len(t), 185.0) * (1 + 0.01 * np.sin(2 * np.pi * 3 * t))), 1800) * 0.3
    x += bp(noise(d), 1000, 4000) * 0.15
    return x * env(len(x), 0.3, 0.4)


def fx_scrub(d=2.6):
    t = t_axis(d)
    return bp(noise(d), 1500, 5000) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t)) ** 2 * 0.4 * env(len(t), 0.1, 0.3)


def fx_flump():
    d = 0.3
    return norm(lp(noise(d), 500) * decay(int(d * SR), 0.06), 0.7)


def fx_clink():
    d = 0.4
    t = t_axis(d)
    return (np.sin(2 * np.pi * 2400 * t) + 0.5 * np.sin(2 * np.pi * 5100 * t)) * decay(len(t), 0.07) * 0.3


def fx_bubbles(d=1.6):
    out = np.zeros(int(d * SR))
    for _ in range(14):
        at = RNG.uniform(0, d - 0.1)
        f0 = RNG.uniform(500, 1200)
        x = sweep_sine(f0, f0 * 1.8, 0.05) * env(int(0.05 * SR), 0.005, 0.02)
        mixin(out, x * 0.25, at)
    return out


def fx_tick():
    d = 0.08
    t = t_axis(d)
    return (np.sin(2 * np.pi * 1900 * t) * decay(len(t), 0.012) + hp(noise(d), 3000) * decay(len(t), 0.003)) * 0.6


def fx_creak(d=0.6, f0=260, f1=420):
    t = t_axis(d)
    f = f0 + (f1 - f0) * t / d + 30 * np.sin(2 * np.pi * 7 * t)
    pulses = (np.sin(2 * np.pi * 38 * t) > 0.6).astype(float)
    x = bp(saw_from_freq(f), 300, 2000) * (0.4 + 0.6 * pulses)
    return x * env(len(t), 0.05, 0.15) * 0.35


def fx_rattle(d=0.4):
    out = np.zeros(int(d * SR))
    for _ in range(10):
        mixin(out, hp(noise(0.02), 1500) * decay(int(0.02 * SR), 0.004) * 0.4, RNG.uniform(0, d - 0.03))
    return out


def fx_hiss(d=1.0):
    return hp(noise(d), 3000) * env(int(d * SR), 0.1, 0.5) * 0.12


def fx_crash():
    d = 1.0
    out = hp(noise(d), 1500) * decay(int(d * SR), 0.12) * 0.6
    for _ in range(14):
        f = RNG.uniform(2500, 7000)
        at = RNG.uniform(0, 0.4)
        x = np.sin(2 * np.pi * f * t_axis(0.3)) * decay(int(0.3 * SR), 0.05)
        mixin(out, x * 0.2, at)
    mixin(out, fx_thud() * 0.4, 0)
    return norm(out, 0.9)


def fx_flap(n=6, gap=0.09):
    out = np.zeros(int((n * gap + 0.2) * SR))
    for k in range(n):
        mixin(out, lp(noise(0.07), 900) * env(int(0.07 * SR), 0.02, 0.04) * 0.5, k * gap)
    return out


def fx_bonk():
    d = 0.4
    t = t_axis(d)
    f = 520 * (1 - 0.35 * t / d)
    ph = np.cumsum(f) / SR
    x = np.sin(2 * np.pi * ph) + 0.4 * np.sin(2 * np.pi * 2.4 * ph)
    return x * decay(len(t), 0.09) * 0.8


def fx_slip():
    d = 0.4
    t = t_axis(d)
    f = 380 * 2 ** (2 * t / d) * (1 + 0.02 * np.sin(2 * np.pi * 9 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.02, 0.08) * 0.45


def fx_clonk():
    d = 1.0
    t = t_axis(d)
    x = fx_bonk() * 1.0
    out = np.zeros(len(t))
    mixin(out, x * 1.2, 0)
    boing = np.sin(2 * np.pi * np.cumsum(170 * (1 + 0.25 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 3))) / SR)
    out += boing * decay(len(t), 0.35) * 0.4
    mixin(out, fx_thud() * 0.6, 0)
    return norm(out, 0.95)


def fx_tut():
    out = np.zeros(int(0.5 * SR))
    for at in (0.0, 0.22):
        d = 0.05
        t = t_axis(d)
        mixin(out, np.sin(2 * np.pi * 1300 * t) * decay(len(t), 0.01) * 0.35, at)
    return out


def fx_quack():
    out = np.zeros(int(0.45 * SR))
    for at, f0 in ((0.0, 560), (0.2, 520)):
        d = 0.17
        t = t_axis(d)
        f = f0 * (1 - 0.25 * t / d)
        src = saw_from_freq(f)
        x = bp(src, 900, 1500) * 1.0 + bp(src, 2200, 3000) * 0.5
        e = np.minimum(1, t / 0.015) * np.exp(-t / 0.09)
        mixin(out, x * e, at)
    return norm(out, 0.7)


def fx_drip():
    return sweep_sine(1400, 2600, 0.04) * env(int(0.04 * SR), 0.002, 0.02) * 0.4


def fx_buzz_tiny():
    d = 0.35
    t = t_axis(d)
    x = np.sign(np.sin(2 * np.pi * 230 * t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * t))
    return lp(x, 2500) * env(len(t), 0.01, 0.1) * 0.15


def fx_dustbuster():
    d = 1.4
    t = t_axis(d)
    f = 300 + 400 * np.clip(t / 0.3, 0, 1)
    x = lp(saw_from_freq(f), 2500) * 0.3 + bp(noise(d), 1000, 5000) * 0.2
    return x * env(len(t), 0.05, 0.3)


def fx_clang():
    d = 0.9
    t = t_axis(d)
    x = sum(a * np.sin(2 * np.pi * f * t) * decay(len(t), tau)
            for f, a, tau in ((523, 1, 0.3), (1480, 0.6, 0.2), (2710, 0.4, 0.12), (3900, 0.2, 0.08)))
    return x * 0.4


def fx_clatter():
    out = np.zeros(int(0.8 * SR))
    for k in range(6):
        d = 0.06
        t = t_axis(d)
        f = RNG.uniform(250, 600)
        mixin(out, (np.sin(2 * np.pi * f * t) + bp(noise(d), 500, 3000) * 0.5) * decay(len(t), 0.02) * (0.7 - k * 0.08),
              k * 0.1 + RNG.uniform(0, 0.03))
    return out


def fx_peck():
    d = 0.05
    t = t_axis(d)
    return (np.sin(2 * np.pi * 3100 * t) + 0.6 * np.sin(2 * np.pi * 1250 * t)) * decay(len(t), 0.008) * 0.6


def fx_yelp():
    d = 0.3
    t = t_axis(d)
    f = 500 * 2 ** (1.6 * t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.01, 0.06) * 0.4


def fx_rev():
    d = 0.6
    t = t_axis(d)
    return lp(saw_from_freq(50 + 110 * t / d), 600) * env(len(t), 0.05, 0.1) * 0.6


def fx_crunch():
    d = 0.6
    x = lp(noise(d), 1500) * decay(int(d * SR), 0.12)
    x += (np.abs(noise(d)) > 2.2) * noise(d) * 0.5 * decay(int(d * SR), 0.2)
    mixin(x, fx_thud() * 0.6, 0)
    return norm(x, 0.95)


def fx_bang():
    d = 0.6
    x = lp(noise(d), 3000) * decay(int(d * SR), 0.08)
    mixin(x, fx_thud() * 0.5, 0)
    return norm(x, 0.95)


def fx_swish():
    d = 0.25
    t = t_axis(d)
    x = noise(d)
    out = np.zeros(len(x))
    for k in range(5):
        lo = 400 * 2 ** (k * 0.6)
        seg_ = slice(int(k * len(x) / 5), int((k + 1) * len(x) / 5))
        out[seg_] = bp(x, lo, lo * 2)[seg_]
    return out * env(len(t), 0.05, 0.1) * 0.4


def fx_whip():
    return fx_swish()[: int(0.16 * SR)] * env(int(0.16 * SR), 0.01, 0.05) * 1.2


def fx_waddle(n=10, gap=0.23):
    out = np.zeros(int((n * gap + 0.2) * SR))
    for k in range(n):
        d = 0.05
        mixin(out, lp(noise(d), 1200) * decay(int(d * SR), 0.01) * 0.4, k * gap)
    return out


def fx_creak_step():
    return fx_creak(0.25, 200, 260) * 0.8


def fx_rope():
    return fx_creak(0.35, 120, 160) * 0.8


def fx_thump():
    d = 0.25
    return norm(sweep_sine(110, 50, d) * decay(int(d * SR), 0.06) + lp(noise(d), 600) * decay(int(d * SR), 0.03), 0.8)


def fx_crash_soft():
    out = fx_thump() * 1.2
    out = np.concatenate([out, np.zeros(SR)])
    mixin(out, fx_rattle(0.5), 0.05)
    mixin(out, fx_clonk() * 0.5, 0.0)
    return out


def fx_clack():
    d = 0.08
    t = t_axis(d)
    return (np.sin(2 * np.pi * 700 * t) + bp(noise(d), 800, 3000) * 0.4) * decay(len(t), 0.015) * 0.6


def fx_slurp():
    d = 1.0
    t = t_axis(d)
    x = noise(d)
    lo = 400 + 1200 * t / d
    out = np.zeros(len(x))
    for k in range(10):
        s = slice(int(k * len(x) / 10), int((k + 1) * len(x) / 10))
        out[s] = bp(x, lo[s.start], lo[s.start] * 1.6)[s]
    gate = (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)) ** 2
    return out * gate * env(len(t), 0.05, 0.2) * 0.5


def fx_wipe():
    out = np.zeros(int(1.4 * SR))
    for k in range(3):
        mixin(out, sweep_sine(1600, 2100, 0.22) * env(int(0.22 * SR), 0.03, 0.08) * 0.12, k * 0.42)
    return out


def fx_twang():
    d = 0.9
    t = t_axis(d)
    x = pluck_fast(110, d, 1.2) * 1.0
    f = 220 * (1 - 0.3 * t / d)
    x += np.sin(2 * np.pi * np.cumsum(f) / SR) * decay(len(t), 0.25) * 0.3
    return x


def fx_strain():
    return fx_creak(1.2, 150, 210) * 0.6


SFX = {
    'wiper': fx_wiper, 'thud': fx_thud, 'click': fx_click, 'radio_jolly': fx_radio_jolly,
    'brakes': fx_brakes, 'door': fx_door, 'steps': fx_steps, 'gulp': fx_gulp, 'engine': fx_engine,
    'keys': fx_keys, 'paper': fx_paper, 'pen': fx_pen, 'vacuum': fx_vacuum, 'scrub': fx_scrub,
    'flump': fx_flump, 'clink': fx_clink, 'bubbles': fx_bubbles, 'tick': fx_tick, 'creak': fx_creak,
    'rattle': fx_rattle, 'hiss': fx_hiss, 'crash': fx_crash, 'flap': fx_flap, 'bonk': fx_bonk,
    'slip': fx_slip, 'clonk': fx_clonk, 'tut': fx_tut, 'quack': fx_quack, 'drip': fx_drip,
    'buzz_tiny': fx_buzz_tiny, 'dustbuster': fx_dustbuster, 'clang': fx_clang, 'clatter': fx_clatter,
    'peck': fx_peck, 'yelp': fx_yelp, 'rev': fx_rev, 'crunch': fx_crunch, 'bang': fx_bang,
    'swish': fx_swish, 'whip': fx_whip, 'waddle': fx_waddle, 'creak_step': fx_creak_step,
    'rope': fx_rope, 'thump': fx_thump, 'crash_soft': fx_crash_soft, 'clack': fx_clack,
    'slurp': fx_slurp, 'wipe': fx_wipe, 'twang': fx_twang, 'strain': fx_strain,
    'harp': lambda: harp_gliss(1.2, 1.0),
    'gasp_sting': lambda: sting(d=1.0, vol=0.8),
    'sting': lambda: sting(('D3', 'Ab3', 'D4', 'Eb4'), 1.4, 0.9),
    'hmm_sting': lambda: hmm_motif(1.0),
    'sigh_swoop': lambda: seq('E4/1 C4/2', 90, bassoon, 1.2),
}


# ------------------------------------------------------------------ mixing --

def build_track(shots, starts, total):
    """shots: list of Shot; starts: dict name -> start time (s)."""
    music = np.zeros(int((total + 2) * SR))
    fx = np.zeros_like(music)

    def S(name, off=0.0):
        return starts[name] + off

    def E(name):
        return starts[name] + next(s.dur for s in shots if s.name == name)

    def place(x, at, end=None, fade_in=0.05, fade_out=0.8, gain=1.0):
        if end is not None:
            x = fit(x, end - at, fade_in, fade_out)
        mixin(music, x, at, gain)

    # ---- music cues
    place(seq(THEME_A.split(' r/3')[0], 100, reed, 0.8), S('a00_title', 0.4), E('a00_title') + 0.4, fade_out=1.2, gain=0.8)
    drive = waltz(84, False, 0.6, 0.5)
    place(drive, S('a01_pov', 0.6), S('a06_fox', 1.62), fade_in=1.5, fade_out=0.02, gain=0.55)
    place(drone(E('a08_roadside') - S('a08_roadside', 1.0), 55), S('a08_roadside', 1.0), E('a08_roadside'), 1.0, 1.0, 0.5)
    place(duck_motif(1.0), S('a09_duck', 1.1), gain=0.8)
    place(duck_motif(1.0), S('a09_duck', 4.6), gain=0.6)
    letter = seq('E5/3 D5/1.5 C5/1.5 B4/3 A4/3 C5/3 B4/1.5 A4/1.5 G#4/6 A4/6', 72, reed, 0.6)
    place(letter, S('a10_keys', 0.4), E('a15_read2'), 1.5, 1.5, 0.6)
    place(oompah(['A2', 'D3', 'E2', 'A2', 'A2', 'D3', 'E2', 'A2'], 72, False, 0.35), S('a12_read'), E('a15_read2'), 1.0, 1.5, 0.5)
    hp_ = hornpipe(150, 1.0)
    hp_ = np.concatenate([hp_, hp_])
    place(hp_, S('b01_list', 0.2), S('b08_list2', 2.6), 0.1, 0.4, 0.6)
    place(sting(('A3', 'C4', 'E4', 'F4'), 2.6, 0.6), S('b08_list2', 2.6), gain=0.7)
    place(drone(E('b11_headin') - S('b09_oven'), 49, 0.8), S('b09_oven'), S('b12_close', 2.2), 1.0, 0.05, 0.45)
    for name in ('b15_hosp1', 'c10_hosp2', 'd10_hosp3'):
        place(hospital_motif(1.0), S(name, 0.6), gain=0.75)
    place(ostinato(S('c08_smash', 0.45) - S('c01_garage', 0.3), 1.0), S('c01_garage', 0.3), S('c08_smash', 0.45), 0.5, 0.02, 0.6)
    sn = sneaky(120, 1.0, 8)
    place(sn, S('d01_stairs', 3.4), E('d04_behind'), 0.1, 0.6, 0.65)
    place(tremolo(S('d07_ducktop') - S('d05_climb'), ('D3', 'Eb3'), 0.8), S('d05_climb'), S('d07_ducktop', 0.2), 0.5, 0.05, 0.5)
    love = waltz(88, True, 0.75, 0.6)
    love = np.concatenate([love, love])
    place(love, S('d13_cupid', 0.9), E('d16_flyaway'), 1.0, 1.5, 0.6)
    fin = seq(to_major('E5/3 A5/1 G5/1 E5/1 D5/2 C5/1 B4/3 A4/6'), 96, reed, 0.8)
    place(fin, S('d17_end', 0.5), E('d17_end'), 0.2, 1.5, 0.75)
    place(seq('A2+E3+A3+C#4/4', 96, lambda f, d, v: reed(f, d, v * 0.4, bright=0.6)), S('d17_end', 3.3), E('d17_end'), 0.1, 1.5, 0.6)

    # ---- rain bed
    r0, r1 = S('a01_pov'), S('a10_keys', 0.6)
    rain = fit(fx_rain(r1 - r0), r1 - r0, 1.0, 1.0)
    mixin(fx, rain, r0, 0.8)

    # ---- spot effects
    cache = {}
    for s in shots:
        for (tt, name, gain) in s.sfx:
            if name not in SFX or gain <= 0:
                continue
            if name not in cache or name in ('quack', 'crash', 'keys'):
                cache[name] = SFX[name]()
            mixin(fx, cache[name], starts[s.name] + tt, gain)

    mix = music * 0.8 + fx * 0.9
    mix = np.tanh(mix * 1.1) * 0.9
    n = int(total * SR)
    mix = mix[:n]
    # subtle stereo: music slightly wide via short delay
    left = mix
    right = np.concatenate([np.zeros(int(0.0006 * SR)), mix])[:n]
    return np.stack([left, right], axis=1)


def write_wav(path, stereo):
    import wave
    data = (np.clip(stereo, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
