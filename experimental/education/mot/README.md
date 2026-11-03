# Workshop video: how a rubidium-87 MOT works

This project generates a 16:9 scientific animation connecting SAS frequency
referencing, Doppler cooling, the quadrupole field of anti-Helmholtz coils,
and capture of a cloud of `87Rb` atoms in a magneto-optical trap.

## Main files

- `MOT_Rb87_workshop_1080p.mp4`: final video, 1920 × 1080, 30 fps, H.264.
- `render_mot_workshop.py`: reproducible animation source.
- `make_latex_assets.py`: typesets all equations using LaTeX.
- `assets/equations/`: transparent equation images used by the renderer.
- `preview_frames/`: key frames used for visual review.

The video includes an original, restrained ambient soundtrack without narration.
All captions are embedded in English, so it can be played in PowerPoint,
Google Slides or Overleaf/Beamer without external subtitle files.

## Narrative

1. **SAS:** a vapor cell and pump/probe beams provide Doppler-free references;
   the servo locks the laser frequency.
2. **Doppler:** preferential absorption from the counterpropagating beam produces
   a viscous force `F_D ≈ -αv` and narrows the velocity distribution.
3. **Anti-Helmholtz:** opposing currents create a quadrupole field with `B = 0`
   at the center and a position-dependent Zeeman shift.
4. **MOT:** six beams, opposite polarizations, a repumper and a magnetic-field
   gradient produce `F ≈ -αv - κr`; a scaled Langevin integration illustrates
   contraction of the captured ensemble.
5. **Final cloud:** typical size and temperature scales are shown. Fluorescence
   at 780 nm is deliberately enhanced to make it visible.
6. **Physical scales:** the closing section distinguishes microscopic cooling
   (milliseconds) from population loading (about one second at a representative
   operating point) and shows `N ≈ 5 × 10^7` atoms.

## Physical conventions

- `87Rb` D2 transition: `λ = 780.241 nm`.
- Natural linewidth: `Γ/(2π) = 6.065 MHz`.
- Ideal two-level Doppler limit: `T_D = 146 µK`.
- Illustrated operating point: `δ = -2.5 Γ`, `b' = 12 G/cm`.
- The repumper prevents population accumulation in the dark `5S1/2, F = 1` state.

The animation is educational: beam sizes, particle paths, fluorescence intensity
and field geometry are not drawn to scale. Values marked as “typical” depend
on the experimental setup.

The final value `N ≈ 5 × 10^7`, with about `1 s` loading time, is a representative
operating point rather than a universal average. A published `87Rb` atomic clock
obtained about `5 × 10^7` atoms with `1.0 s` loading, while another modern system
reported `4.9 × 10^7` atoms and a `4.1 s` lifetime:

- <https://pmc.ncbi.nlm.nih.gov/articles/PMC6057979/>
- <https://link.springer.com/article/10.1134/S0021364023603391>

## Regeneration

With Python, NumPy, Pillow and `imageio-ffmpeg` installed, run from this directory:

```powershell
python make_latex_assets.py
python render_mot_workshop.py --output MOT_Rb87_workshop_1080p.mp4
```

Render only review frames:

```powershell
python render_mot_workshop.py --stills preview_frames
```

For a short 720p preview:

```powershell
python render_mot_workshop.py --width 1280 --height 720 --fps 24 --start 59 --end 66 --output preview.mp4 --no-audio
```

## Workshop use

Play the video full-screen. Pause after each section to ask students which
physical ingredient has been added and which variable — frequency, velocity
or position — it controls.
