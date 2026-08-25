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
st.title(" Plataforma de Educación Virtual")
st.caption(
    "Taller de Bases de Datos — Contexto 13 — Perfiles de estudiantes con "
    "información flexible en JSON (intereses, cursos, competencias, "
    "actividades y preferencias de aprendizaje)."
)

with st.expander("ℹ Acerca de esta base de datos", expanded=False):
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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1️ Competencia Python",
    "2️ Actividades por curso",
    "3️ Nivel intermedio",
    "4️ Preferencias de aprendizaje",
    "# Datos crudos (perfiles)",
    "° Diagrama de clases",
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

# ---------------------------------------------------------------------------
# Diagrama de clases (notación UML) generado con Graphviz
# ---------------------------------------------------------------------------
with tab6:
    st.subheader("Diagrama de clases del modelo de datos (notación UML)")
    st.markdown(
        "Aunque físicamente todo se almacena en una sola tabla `estudiantes`, "
        "el contenido de la columna `perfil` (JSON) representa lógicamente "
        "tres clases relacionadas por **composición**, con su respectiva "
        "**multiplicidad**:"
    )

    diagrama_uml = r"""
    digraph ClassDiagram {
        graph [rankdir=LR, splines=ortho, bgcolor=transparent, nodesep=0.9, ranksep=1.1];
        node [shape=none, fontname="Helvetica", fontsize=11];
        edge [fontname="Helvetica", fontsize=10, color="#555555", fontcolor="#333333"];

        Estudiante [label=<
            <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" COLOR="#2E5AAC" BGCOLOR="#E6F1FB">
                <TR><TD BGCOLOR="#2E5AAC"><FONT COLOR="white"><B>Estudiante</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT">+ id : int [PK]</TD></TR>
                <TR><TD ALIGN="LEFT">+ nombre : string</TD></TR>
                <TR><TD ALIGN="LEFT">+ correo : string</TD></TR>
                <TR><TD ALIGN="LEFT">+ perfil : Perfil</TD></TR>
            </TABLE>
        >];

        Perfil [label=<
            <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" COLOR="#0F6E56" BGCOLOR="#E1F5EE">
                <TR><TD BGCOLOR="#0F6E56"><FONT COLOR="white"><B>Perfil</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT">+ intereses : string[ ]</TD></TR>
                <TR><TD ALIGN="LEFT">+ competencias : string[ ]</TD></TR>
                <TR><TD ALIGN="LEFT">+ preferencias_aprendizaje : string[ ]</TD></TR>
                <TR><TD ALIGN="LEFT">+ cursos_inscritos : CursoInscrito[ ]</TD></TR>
            </TABLE>
        >];

        CursoInscrito [label=<
            <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" COLOR="#993C1D" BGCOLOR="#FAECE7">
                <TR><TD BGCOLOR="#993C1D"><FONT COLOR="white"><B>CursoInscrito</B></FONT></TD></TR>
                <TR><TD ALIGN="LEFT">+ curso : string</TD></TR>
                <TR><TD ALIGN="LEFT">+ nivel_experiencia : string</TD></TR>
                <TR><TD ALIGN="LEFT">+ actividades_completadas : int</TD></TR>
                <TR><TD ALIGN="LEFT">+ progreso_porcentaje : int</TD></TR>
            </TABLE>
        >];

        Estudiante -> Perfil [dir=both, arrowtail=diamond, arrowhead=none,
            penwidth=1.2, taillabel="1", headlabel="1", xlabel="contiene"];
        Perfil -> CursoInscrito [dir=both, arrowtail=diamond, arrowhead=none,
            penwidth=1.2, taillabel="1", headlabel="0..*", xlabel="cursos_inscritos"];
    }
    """

    st.graphviz_chart(diagrama_uml, use_container_width=True)

    with st.expander("Leer notación del diagrama"):
        st.markdown(
            """
- **Rombo relleno (◆)**: relación de **composición** — `CursoInscrito` no existe
  sin un `Perfil`, ni `Perfil` sin un `Estudiante`.
- **Multiplicidad `1` — `0..*`**: un `Perfil` puede tener **cero o muchos**
  cursos inscritos; un `Estudiante` tiene **exactamente un** `Perfil`.
- **`[PK]`**: llave primaria de la tabla física `estudiantes`.
- Físicamente, `Perfil` y `CursoInscrito` **no son tablas aparte**: viven
  serializadas dentro de la columna `perfil` (JSON) de `estudiantes`, y se
  consultan con `json_extract` / `json_each` (ver pestañas 1 a 4).
            """
        )

    st.download_button(
        "⬇️ Descargar definición del diagrama (.dot / Graphviz)",
        data=diagrama_uml,
        file_name="diagrama_clases_plataforma_educativa.dot",
        mime="text/plain",
    )

st.divider()
st.caption("Taller de Bases de Datos · Contexto 13: Plataforma de educación virtual · Streamlit + SQLite (JSON1)")
