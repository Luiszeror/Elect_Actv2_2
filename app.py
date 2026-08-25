import sqlite3
import json
import os

import pandas as pd
import streamlit as st

from generar_datos import crear_base_datos, DB_PATH

st.set_page_config(
    page_title="Plataforma de Educación Virtual - Taller BD",
    page_icon="🎓",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Conexión / inicialización de la base de datos
# ---------------------------------------------------------------------------
if not os.path.exists(DB_PATH):
    crear_base_datos()


@st.cache_resource
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


conn = get_connection()


def run_query(sql, params=()):
    return pd.read_sql_query(sql, conn, params=params)


# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
st.title("🎓 Plataforma de Educación Virtual")
st.caption(
    "Taller de Bases de Datos — Contexto 13 — Perfiles de estudiantes con "
    "información flexible en JSON (intereses, cursos, competencias, "
    "actividades y preferencias de aprendizaje)."
)

with st.expander("ℹ️ Acerca de esta base de datos", expanded=False):
    st.markdown(
        """
Esta aplicación usa **SQLite** con una tabla `estudiantes` que contiene una
columna `perfil` en formato **JSON**, lo que permite guardar información
**semiestructurada y flexible** por estudiante (cada uno puede tener un
número distinto de cursos, competencias, intereses, etc., sin necesidad de
un esquema rígido de columnas).

Las consultas usan las funciones nativas **JSON1** de SQLite
(`json_extract`, `json_each`) para "abrir" ese JSON y consultarlo con SQL
normal.
        """
    )

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1️⃣ Competencia Python",
    "2️⃣ Actividades por curso",
    "3️⃣ Nivel intermedio",
    "4️⃣ Preferencias de aprendizaje",
    "📋 Datos crudos (perfiles)",
])

# ---------------------------------------------------------------------------
# Consulta 1: Estudiantes con competencia "Python"
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("Estudiantes que tienen la competencia \"Python\"")
    st.markdown("Recorre el arreglo JSON `competencias` de cada estudiante con `json_each`.")

    sql1 = """
        SELECT DISTINCT e.id, e.nombre, e.correo
        FROM estudiantes e, json_each(e.perfil, '$.competencias') AS comp
        WHERE comp.value = ?
        ORDER BY e.nombre
    """
    df1 = run_query(sql1, ("Python",))
    st.dataframe(df1, use_container_width=True, hide_index=True)
    st.caption(f"Total de estudiantes encontrados: **{len(df1)}**")

    with st.expander("Ver consulta SQL"):
        st.code(sql1, language="sql")

# ---------------------------------------------------------------------------
# Consulta 2: Estudiantes con más de N actividades en un curso específico
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("Estudiantes que han completado más de N actividades en un curso")

    from generar_datos import CURSOS
    curso_sel = st.selectbox("Selecciona el curso", CURSOS)
    n_actividades = st.slider("Más de cuántas actividades completadas", 0, 8, 3)

    sql2 = """
        SELECT DISTINCT e.id, e.nombre, e.correo,
               json_extract(curso.value, '$.actividades_completadas') AS actividades_completadas,
               json_extract(curso.value, '$.progreso_porcentaje') AS progreso_porcentaje
        FROM estudiantes e, json_each(e.perfil, '$.cursos_inscritos') AS curso
        WHERE json_extract(curso.value, '$.curso') = ?
          AND json_extract(curso.value, '$.actividades_completadas') > ?
        ORDER BY actividades_completadas DESC
    """
    df2 = run_query(sql2, (curso_sel, n_actividades))
    st.dataframe(df2, use_container_width=True, hide_index=True)
    st.caption(
        f"Estudiantes con más de {n_actividades} actividades completadas en "
        f"**{curso_sel}**: **{len(df2)}**"
    )

    with st.expander("Ver consulta SQL"):
        st.code(sql2, language="sql")

# ---------------------------------------------------------------------------
# Consulta 3: Cursos asociados a estudiantes con nivel "intermedio"
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("Cursos asociados a estudiantes con nivel de experiencia \"intermedio\"")

    sql3 = """
        SELECT e.nombre AS estudiante,
               json_extract(curso.value, '$.curso') AS curso,
               json_extract(curso.value, '$.nivel_experiencia') AS nivel_experiencia
        FROM estudiantes e, json_each(e.perfil, '$.cursos_inscritos') AS curso
        WHERE json_extract(curso.value, '$.nivel_experiencia') = 'intermedio'
        ORDER BY curso, estudiante
    """
    df3 = run_query(sql3)
    st.dataframe(df3, use_container_width=True, hide_index=True)

    st.markdown("**Cursos únicos con estudiantes de nivel intermedio:**")
    st.write(sorted(df3["curso"].unique().tolist()) if not df3.empty else "Sin resultados")

    with st.expander("Ver consulta SQL"):
        st.code(sql3, language="sql")

# ---------------------------------------------------------------------------
# Consulta 4: Preferencias de aprendizaje por estudiante
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("Preferencias de aprendizaje registradas por estudiante")

    sql4 = """
        SELECT e.nombre AS estudiante,
               pref.value AS preferencia_aprendizaje
        FROM estudiantes e, json_each(e.perfil, '$.preferencias_aprendizaje') AS pref
        ORDER BY e.nombre
    """
    df4 = run_query(sql4)

    vista = st.radio("Vista", ["Detallada (una fila por preferencia)", "Agrupada por estudiante"], horizontal=True)
    if vista.startswith("Detallada"):
        st.dataframe(df4, use_container_width=True, hide_index=True)
    else:
        agrupado = (
            df4.groupby("estudiante")["preferencia_aprendizaje"]
            .apply(lambda s: ", ".join(s))
            .reset_index()
            .rename(columns={"preferencia_aprendizaje": "preferencias_aprendizaje"})
        )
        st.dataframe(agrupado, use_container_width=True, hide_index=True)

    with st.expander("Ver consulta SQL"):
        st.code(sql4, language="sql")

# ---------------------------------------------------------------------------
# Vista de datos crudos
# ---------------------------------------------------------------------------
with tab5:
    st.subheader("Perfiles completos (JSON crudo)")
    df_raw = run_query("SELECT id, nombre, correo, perfil FROM estudiantes ORDER BY id")
    estudiante_sel = st.selectbox(
        "Selecciona un estudiante para ver su perfil JSON",
        df_raw["nombre"].tolist(),
    )
    fila = df_raw[df_raw["nombre"] == estudiante_sel].iloc[0]
    st.json(json.loads(fila["perfil"]))

    st.divider()
    st.markdown("**Tabla completa (id, nombre, correo):**")
    st.dataframe(df_raw[["id", "nombre", "correo"]], use_container_width=True, hide_index=True)

st.divider()
st.caption("Taller de Bases de Datos · Contexto 13: Plataforma de educación virtual · Streamlit + SQLite (JSON1)")
