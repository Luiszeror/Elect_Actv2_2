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

## Publicar en Streamlit Community Cloud (gratis)
1. Sube esta carpeta a un repositorio de **GitHub** (público).
2. Ingresa a https://share.streamlit.io/ con tu cuenta de GitHub.
3. Clic en **"New app"** → selecciona el repositorio, la rama y el archivo `app.py`.
4. Clic en **Deploy**. En 1-2 minutos obtendrás una URL pública tipo:
   `https://<tu-app>.streamlit.app`
5. Comparte esa URL con tus compañeros.
