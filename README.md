# CLRAH — Dashboard de Diagnóstico (v3)

Dashboard organizado en pestañas, con estilo visual propio (tarjetas KPI en azul marino,
colores consistentes con el documento). Cada gráfica indica explícitamente el año de sus datos.

## Pestañas
1. 🗺️ Cobertura geográfica — mapa de toda LATAM/Caribe + Pareto (2025)
2. 📈 Serie de tiempo — 2025→2026 continua + tipo de evento 2019-2026
3. 🚚 Transporte y costos — modal, costo por transporte, especialización por país (2025)
4. 🤝 Socios y organismos — diversificación de socios + traslape de organismos (2025)
5. 💰 Ayuda vs. Daño — Dorian y Melissa, con tarjetas de métricas

## Cómo correrlo localmente
```
pip install -r requirements.txt
streamlit run app.py
```

## Cómo publicarlo / actualizarlo en Streamlit Cloud
1. Sube app.py, requirements.txt y master_clean_es.csv a tu repo de GitHub (reemplaza los que ya tenías).
2. Si ya tenías la app desplegada en share.streamlit.io, se redeploya sola al detectar el cambio.
3. Si es la primera vez: share.streamlit.io → "New app" → selecciona el repo y app.py → Deploy.
