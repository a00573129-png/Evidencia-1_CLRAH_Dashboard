# CLRAH — Dashboard de Diagnóstico (v2)

Dashboard interactivo: mapa de toda América Latina y el Caribe, serie de tiempo 2025+2026,
concentración geográfica (Pareto), diversificación de socios, modal, costos, y relación ayuda-daño.
Filtros por mes, país y usuario en la barra lateral.

## Novedades de esta versión
- Mapa interactivo de TODA la región (antes solo mostraba el Top 5)
- Serie de tiempo extendida con 2026 (enero-julio)
- Gráfica de concentración geográfica (Pareto) con línea de 80%
- Gráfica de diversificación de socios (riesgo de continuidad)
- Sección de relación ayuda-daño (Huracán Dorian y Huracán Melissa)

## Cómo correrlo localmente
```
pip install -r requirements.txt
streamlit run app.py
```

## Cómo publicarlo gratis (para compartir con un link)
1. Sube estos archivos a un repositorio de GitHub (privado o público):
   - app.py
   - requirements.txt
   - master_clean_es.csv
2. Ve a https://share.streamlit.io e inicia sesión con GitHub.
3. "New app" → selecciona el repo y app.py → Deploy.
4. En 1-2 minutos tienes un link público (tuapp.streamlit.app) para compartir.

Si ya tenías la v1 publicada, solo reemplaza estos 3 archivos en el mismo repo — Streamlit Cloud
redeploya solo en cuanto detecta el cambio en GitHub.
