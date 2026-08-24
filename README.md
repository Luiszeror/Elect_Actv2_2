# Taller de Bases de Datos — Plataforma de Educación Virtual (Contexto 13)

App en **Streamlit** + **SQLite (con columnas JSON)** que responde a las 4 consultas del taller.

## Archivos
- `app.py` → aplicación Streamlit (interfaz y consultas).
- `generar_datos.py` → crea `plataforma_educativa.db` con 20 estudiantes de ejemplo (perfiles JSON).
- `requirements.txt` → dependencias.

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

