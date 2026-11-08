"""Render the whole film.

    python src/build.py            # render everything (cached shots are reused)
    python src/build.py --force    # re-render every shot
    python src/build.py a08 b13    # re-render shots whose names start with these prefixes
"""
import hashlib
import inspect
import os
import subprocess
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'build')
SHOTS = os.path.join(OUT, 'shots')
sys.path.insert(0, HERE)


def all_shots():
    import act1, act2, act3, act4
    shots = act1.build() + act2.build() + act3.build() + act4.build()
    return shots


def _render(i):
    shots = all_shots()
    s = shots[i]
    if s.dissolve and i > 0:
        s.prev = shots[i - 1].last_frame()
    path = os.path.join(SHOTS, f'{i:03d}_{s.name}.mp4')
    s.render(path)
    return s.name


def main():
    os.makedirs(SHOTS, exist_ok=True)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    force = '--force' in sys.argv
    shots = all_shots()
    todo = []
    for i, s in enumerate(shots):
        path = os.path.join(SHOTS, f'{i:03d}_{s.name}.mp4')
        if force or not os.path.exists(path) or any(s.name.startswith(a) for a in args):
            todo.append(i)
    print(f'{len(shots)} shots, rendering {len(todo)}')
    with Pool(max(1, os.cpu_count())) as pool:
        for name in pool.imap_unordered(_render, todo):
            print('  done', name, flush=True)

    # join the pictures
    lst = os.path.join(OUT, 'shots.txt')
    with open(lst, 'w') as f:
        for i, s in enumerate(shots):
            f.write(f"file 'shots/{i:03d}_{s.name}.mp4'\n")
    video = os.path.join(OUT, 'video.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-c', 'copy', video], check=True)

    # the soundtrack
    from audio import build_track, write_wav
    from engine import FPS
    starts, t = {}, 0.0
    for s in shots:
        starts[s.name] = t
        t += s.frame_count() / FPS
    wav = os.path.join(OUT, 'audio.wav')
    write_wav(wav, build_track(shots, starts, t))

    final = os.path.join(OUT, 'duck.mp4')
    tmp = final[:-4] + '.part.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-i', wav, '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmp],
                   check=True)
    os.replace(tmp, final)
    print(f'wrote {final}  ({t:.1f}s)')


if __name__ == '__main__':
    main()
