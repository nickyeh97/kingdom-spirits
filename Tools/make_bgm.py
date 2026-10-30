# 靈獸之家的背景音樂（原創、程式合成，沒有版權問題）
# 用法（repo 根目錄；需要 numpy 與 ffmpeg，Blender 內建的 Python 就有 numpy）：
#   <blender>/4.2/python/bin/python3.11 Tools/make_bgm.py Assets/Resources/Audio/bgm_home.ogg
#
# 風格：慵懶、溫暖的 lo-fi（組長 2026-10-30：「舒服很 chill」）。
#   速度 72 BPM、F 大調；和弦 Fmaj7 → Am7 → Dm7 → B♭maj7（I–iii–vi–IV），每個和弦 2 小節，兩輪共 16 小節（約 53 秒）
#   樂器：柔和的鋪底（pad）、電鋼琴分解和弦（帶一點搖擺）、圓圓的低音、很輕的鼓（大鼓＋刷聲）、
#         後半段加音樂盒旋律（五聲音階，簡單好記）
#   無縫循環：多算一段殘響尾巴，再疊回開頭，循環播放時聽不出接縫
# 想改：改下面的 BPM、CHORDS、MELODY，再跑一次即可（同一個亂數種子，結果固定）
import sys, wave, subprocess, os
import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else "bgm_home.ogg"
SR = 32000                      # 取樣率：背景音樂用 32 kHz 就夠，檔案小
BPM = 72
BEAT = 60.0 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)

def midi(n):                    # MIDI 音高 → 頻率
    return 440.0 * 2 ** ((n - 69) / 12)

# 和弦（MIDI 音高）：低音、和弦音
CHORDS = [
    (41, [53, 57, 60, 64]),     # Fmaj7：F | F A C E
    (45, [52, 55, 57, 60]),     # Am7：A | E G A C
    (38, [53, 57, 60, 62]),     # Dm7：D | F A C D
    (46, [53, 57, 58, 62]),     # B♭maj7：B♭ | F A B♭ D
]
BARS_PER_CHORD = 2
ROUNDS = 2
N_BARS = len(CHORDS) * BARS_PER_CHORD * ROUNDS
LOOP = N_BARS * BAR
TAIL = 4.0                      # 殘響尾巴（疊回開頭）
N = int((LOOP + TAIL) * SR)
mix = {k: np.zeros(N) for k in ("pad", "keys", "bass", "drums", "melody")}

def env(n, a, r, sustain=1.0):
    """簡單包絡：a 秒漸強、r 秒漸弱。"""
    e = np.full(n, sustain)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, sustain, na)
    if nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e

def add(track, t0, sig):
    i = int(t0 * SR)
    j = min(N, i + len(sig))
    mix[track][i:j] += sig[: j - i]

def lowpass(x, cutoff):
    """一階低通（讓聲音柔和，不刺耳）。"""
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y

# ---------- 樂器 ----------
def pad_note(f, dur):
    t = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(2 * np.pi * f * d * t) for d in (0.997, 1.0, 1.003)) / 3      # 三個略為走音的音疊起來＝合唱般的溫暖
    s += 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return s * env(len(t), 1.2, 1.5) * (0.9 + 0.1 * np.sin(2 * np.pi * 0.2 * t))

def epiano(f, dur, vel):
    """電鋼琴（FM 合成）：敲下去亮一點、很快變圓潤。"""
    t = np.arange(int(dur * SR)) / SR
    mod_index = 1.6 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * f * t + mod_index * np.sin(2 * np.pi * f * t))
    s += 0.15 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 12)               # 敲擊的亮點
    return vel * s * np.exp(-t * 1.6) * env(len(t), 0.004, 0.08)

def bass_note(f, dur):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 2 * f * t)
    return 0.8 * s * np.exp(-t * 0.9) * env(len(t), 0.01, 0.2)

def musicbox(f, dur, vel):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 5)
    return vel * s * np.exp(-t * 2.2) * env(len(t), 0.003, 0.1)

def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 50 + 70 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

def brush(length=0.12):
    n = int(length * SR)
    return lowpass(rng.standard_normal(n), 5000) * np.exp(-np.arange(n) / SR * 35)

# ---------- 編曲 ----------
SWING = 0.06 * BEAT             # 反拍稍微晚一點＝搖擺感
for r in range(ROUNDS):
    for ci, (root, tones) in enumerate(CHORDS):
        bar0 = (r * len(CHORDS) + ci) * BARS_PER_CHORD
        t_chord = bar0 * BAR
        dur = BARS_PER_CHORD * BAR
        for n in tones:                                                  # 鋪底：整個和弦長音
            add("pad", t_chord, 0.10 * pad_note(midi(n + 12), dur + 1.2))
        for b in range(BARS_PER_CHORD):                                  # 低音：每小節第 1、3 拍
            for beat, k in ((0, root), (2, root + (7 if b == 1 else 0))):
                add("bass", t_chord + b * BAR + beat * BEAT, 0.35 * bass_note(midi(k), 1.6 * BEAT))
        pattern = [0, 1, 2, 3, 2, 1, 2, 3]                               # 電鋼琴：八分音符分解和弦
        for b in range(BARS_PER_CHORD):
            for i8 in range(8):
                t = t_chord + b * BAR + i8 * BEAT / 2 + (SWING if i8 % 2 else 0)
                if rng.random() < 0.18:                                  # 偶爾空一拍，比較鬆
                    continue
                vel = 0.18 * (1.0 if i8 % 2 == 0 else 0.7) * rng.uniform(0.8, 1.05)
                add("keys", t, epiano(midi(tones[pattern[i8]] + 12), 1.2, vel))
        for b in range(BARS_PER_CHORD):                                  # 鼓：很輕
            t_bar = t_chord + b * BAR
            for beat in (0, 2.5):
                add("drums", t_bar + beat * BEAT, 0.35 * kick())
            for i8 in range(8):
                add("drums", t_bar + i8 * BEAT / 2 + (SWING if i8 % 2 else 0),
                    (0.05 if i8 % 2 else 0.03) * rng.uniform(0.7, 1.0) * brush())

# 音樂盒旋律：第二輪才出現（F 大調五聲音階：F G A C D），像在旁邊輕輕哼
MELODY = [  # (小節內第幾拍, 音高, 拍長)；每兩小節一句
    [(0, 72, 1.5), (1.5, 74, 0.5), (2, 77, 2), (5, 76, 1), (6, 74, 2)],
    [(0, 72, 1), (1, 69, 1), (2, 72, 2), (4.5, 74, 0.5), (5, 72, 3)],
    [(0, 69, 1.5), (1.5, 72, 0.5), (2, 74, 2), (5, 77, 1), (6, 74, 2)],
    [(0, 74, 1), (1, 72, 1), (2, 70, 2), (4, 69, 1), (5, 72, 3)],
]
for ci, phrase in enumerate(MELODY):
    t0 = (len(CHORDS) + ci) * BARS_PER_CHORD * BAR
    for beat, n, length in phrase:
        add("melody", t0 + beat * BEAT, musicbox(midi(n + 12), max(1.5, length * BEAT * 1.5), 0.10))

# ---------- 混音 ----------
GAIN = {"pad": 1.0, "keys": 1.0, "bass": 1.0, "drums": 0.8, "melody": 1.0}
dry = sum(GAIN[k] * lowpass(v, 6500 if k != "drums" else 9000) for k, v in mix.items())

# 殘響：用衰減的雜訊當空間（卷積），只加一點點
ir_n = int(2.2 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 3.2)
ir = lowpass(ir, 4000); ir /= np.sqrt(np.sum(ir ** 2))
nfft = 1 << int(np.ceil(np.log2(N + ir_n)))
wet = np.fft.irfft(np.fft.rfft(dry, nfft) * np.fft.rfft(ir, nfft), nfft)[:N]
out = dry + 0.18 * wet

# 無縫循環：把超出 LOOP 的尾巴疊回開頭
L = int(LOOP * SR)
loop = out[:L].copy()
loop[: N - L] += out[L:]

# 立體聲：電鋼琴與鼓稍微左右分開，聽起來比較寬
stereo = np.stack([loop, loop], axis=1)
loop_keys = np.zeros(L); k = GAIN["keys"] * lowpass(mix["keys"], 6500); loop_keys += k[:L]; loop_keys[: N - L] += k[L:]
stereo[:, 0] += 0.12 * loop_keys; stereo[:, 1] -= 0.12 * loop_keys
stereo /= np.max(np.abs(stereo)) / 0.6        # 音量留很多空間（背景音樂要小聲）

pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
tmp = OUT + ".wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-c:a", "libvorbis", "-q:a", "3", OUT], check=True)
os.remove(tmp)
print(f"bgm {OUT}: {LOOP:.1f} s loop, {os.path.getsize(OUT) / 1024:.0f} KB")
