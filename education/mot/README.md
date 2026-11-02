# Video de taller: cómo funciona una MOT de rubidio-87

Este proyecto genera una animación científica 16:9 que conecta, en una sola
secuencia, la referencia de frecuencia por SAS, el enfriamiento Doppler, el
campo cuadrupolar de bobinas anti-Helmholtz y la captura de una nube de
`87Rb` en una trampa magneto-óptica.

## Archivo principal

- `MOT_Rb87_workshop_1080p.mp4`: video final, 1920 × 1080, 30 fps, H.264.
- `render_mot_workshop.py`: fuente reproducible de la animación.
- `make_latex_assets.py`: genera todas las ecuaciones con LaTeX real.
- `assets/equations/`: fórmulas transparentes usadas por el renderizador.
- `preview_frames/`: fotogramas clave usados para la revisión visual.

El video contiene música ambiental original y discreta, sin narración. Los
rótulos están incrustados en español, de modo que puede reproducirse dentro de
PowerPoint, Google Slides u Overleaf/Beamer sin depender de subtítulos externos.

## Narrativa

1. **SAS:** una celda de vapor y haces pump/probe producen referencias
   Doppler-free; el servo fija la frecuencia del láser.
2. **Doppler:** la absorción preferente desde el haz contrapropagante genera
   una fuerza viscosa `F_D ≈ -αv` y estrecha la distribución de velocidades.
3. **Anti-Helmholtz:** corrientes opuestas crean un campo cuadrupolar con
   `B = 0` en el centro y un desplazamiento Zeeman dependiente de posición.
4. **MOT:** seis haces, polarizaciones opuestas, repumper y gradiente magnético
   producen `F ≈ -αv - κr`; una integración de Langevin escalada muestra la
   contracción del ensamble capturado.
5. **Nube final:** se muestran escalas típicas de tamaño y temperatura. La
   fluorescencia a 780 nm está deliberadamente realzada para hacerla visible.
6. **Escalas reales:** el cierre distingue el enfriamiento microscópico
   (milisegundos) de la carga de la población MOT (alrededor de un segundo en
   un punto de operación representativo) y muestra `N ≈ 5 × 10^7` átomos.

## Convenciones físicas

- Transición D2 de `87Rb`: `λ = 780.241 nm`.
- Ancho natural: `Γ/(2π) = 6.065 MHz`.
- Límite Doppler ideal de dos niveles: `T_D = 146 µK`.
- Ejemplo visual de operación: `δ = -2.5 Γ`, `b' = 12 G/cm`.
- El láser repumper evita la acumulación de población en el estado oscuro
  `5S1/2, F = 1`.

La animación es pedagógica: tamaños de haces, órbitas de partículas, intensidad
de la fluorescencia y geometría de campo no están dibujados a escala. Los valores
marcados como “típicos” dependen del montaje experimental.

El valor de cierre `N ≈ 5 × 10^7` con carga de aproximadamente `1 s` es un punto
de operación representativo, no un promedio universal. Un reloj atómico de
`87Rb` publicado obtuvo alrededor de `5 × 10^7` átomos con `1.0 s` de carga, y
otro sistema moderno reportó `4.9 × 10^7` átomos con una vida de `4.1 s`:

- <https://pmc.ncbi.nlm.nih.gov/articles/PMC6057979/>
- <https://link.springer.com/article/10.1134/S0021364023603391>

## Regenerar

Con Python, NumPy, Pillow e `imageio-ffmpeg` disponibles:

```powershell
python make_latex_assets.py
python render_mot_workshop.py --output MOT_Rb87_workshop_1080p.mp4
```

Para renderizar solamente fotogramas de control:

```powershell
python render_mot_workshop.py --stills preview_frames
```

Para una prueba corta a 720p:

```powershell
python render_mot_workshop.py --width 1280 --height 720 --fps 24 --start 59 --end 66 --output preview.mp4 --no-audio
```

## Uso en la presentación

Se recomienda reproducirlo a pantalla completa. En un taller, puede pausarse al
final de cada bloque para preguntar a los estudiantes qué ingrediente físico se
añade y qué variable —frecuencia, velocidad o posición— queda controlada.
