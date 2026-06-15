# 05 · Sound Design (synthesized, royalty-free)

`sound_gen.py` builds the intro soundtrack entirely from **ffmpeg oscillators +
noise + filters** — no sample library, no licensing. The vibe is
**cinematic-restrained**: a quiet pad bed with a few deliberate accents.

> You can't hear it while building — synthesize with sane levels, then the **human
> is the ear**. Tweak by adjusting per-element `volume=` and the `items` start times.

## Run

```bash
python vo/sound_gen.py        # -> intro_audio.wav (stereo, 48k, matches the intro length)
```

## Elements (and how they're made)

| Element | When | ffmpeg recipe |
|---------|------|---------------|
| **Pad bed** | whole clip | 3 sines (C3/G3/C4) `amix` → `lowpass=1300` → `volume=0.13` → `afade` in/out → `aecho` (reverb) |
| **Riser** | into the seal | linear chirp via `aevalsrc='sin(2*PI*(f0*t + k*t*t))'` |
| **Convergence swell** | just before seal | `anoisesrc=color=brown` → `bandpass` → swell envelope |
| **Confirm chime** | on the seal | 3 sines (G5/D6/G6) `amix` → `volume='exp(-3.4*t)':eval=frame` (exp decay) → `aecho` |
| **Sub-bass thump** | on the seal | `sine=55` → `volume='exp(-8*t)':eval=frame` → `lowpass=160` |
| **Settle shimmer** | logo settles | `anoisesrc=white` → `highpass=4200` → very low volume |
| **Capability blips** | as pills appear | short rising sines, `volume='exp(-26*t)':eval=frame` |

## Mixing

Each element is rendered to its own `.wav`, then placed on the timeline with
`adelay=<ms>:all=1` and combined:
```
amix=inputs=N:duration=longest:normalize=0 → loudnorm=I=-15:TP=-1.5:LRA=11
```
The `items` list at the bottom of `sound_gen.py` is `(file, start_ms)` — **this is
where you re-time** to match the animation. Master `loudnorm I=-15` (a touch hotter
than the -17 used for narration, because it's a music bed not speech).

## Key techniques

- **Time-varying volume** (decay/swell): `volume='<expr in t>':eval=frame`.
- **Pitch sweep** (riser/whoosh): `aevalsrc` with a chirp phase
  `sin(2*PI*(f0*t + (f1-f0)/(2*dur)*t*t))`.
- **Reverb**: `aecho=0.8:0.85:55|110:0.3|0.2` (in_gain:out_gain:delays:decays).
- Keep peaks under 0 dB; check with
  `ffmpeg -i a.wav -af astats=metadata=1 -f null -` → `Peak level dB`.
