"""
Genera la base de datos SQLite 'plataforma_educativa.db' para el
Taller de Bases de Datos - Contexto 13: Plataforma de educación virtual.

Cada estudiante tiene un perfil flexible almacenado como JSON dentro de
una columna de texto (extensión típica de bases de datos relacionales
para soportar datos semiestructurados: NoSQL embebido / JSON columns).
"""

import sqlite3
import json
import random
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "plataforma_educativa.db")

# ---------------------------------------------------------------------------
# Datos base para generar perfiles variados y realistas
# ---------------------------------------------------------------------------
NOMBRES = [
    "Camila Rodríguez", "Andrés Gómez", "Valentina Torres", "Santiago Pérez",
    "Isabella Martínez", "Mateo Ramírez", "Sofía Castro", "Nicolás Herrera",
    "Daniela Suárez", "Juan Diego López", "María José Vargas", "Sebastián Rojas",
    "Laura Jiménez", "David Moreno", "Gabriela Ortiz", "Alejandro Cárdenas",
    "Natalia Peña", "Felipe Salazar", "Paula Restrepo", "Julián Mejía",
]

CURSOS = [
    "Fundamentos de Python", "Bases de Datos Relacionales", "Desarrollo Web con Django",
    "Ciencia de Datos", "Estructuras de Datos", "Machine Learning Básico",
    "SQL Avanzado", "Programación Orientada a Objetos",
]

COMPETENCIAS_POSIBLES = [
    "Python", "SQL", "JavaScript", "Análisis de datos", "Git",
    "Modelado de bases de datos", "Machine Learning", "APIs REST",
    "Docker", "Estructuras de datos",
]

INTERESES_POSIBLES = [
    "Inteligencia artificial", "Desarrollo web", "Ciberseguridad",
    "Análisis de datos", "Videojuegos", "Robótica", "Cloud computing",
    "Diseño UX/UI",
]

NIVELES = ["principiante", "intermedio", "avanzado"]

PREFERENCIAS_POSIBLES = [
    "visual", "auditivo", "lectura/escritura", "kinestésico",
    "aprendizaje autodirigido", "aprendizaje colaborativo",
]


def generar_perfil(seed_rnd: random.Random) -> dict:
    """Genera un perfil JSON flexible para un estudiante."""

    # Cursos inscritos, cada uno con su propio nivel y actividades completadas
    n_cursos = seed_rnd.randint(1, 4)
    cursos_elegidos = seed_rnd.sample(CURSOS, n_cursos)
    cursos_inscritos = []
    for curso in cursos_elegidos:
        cursos_inscritos.append({
            "curso": curso,
            "nivel_experiencia": seed_rnd.choice(NIVELES),
            "actividades_completadas": seed_rnd.randint(0, 8),
            "progreso_porcentaje": seed_rnd.randint(10, 100),
        })

    competencias = seed_rnd.sample(
        COMPETENCIAS_POSIBLES, seed_rnd.randint(2, 5)
    )
    intereses = seed_rnd.sample(
        INTERESES_POSIBLES, seed_rnd.randint(1, 3)
    )
    preferencias = seed_rnd.sample(
        PREFERENCIAS_POSIBLES, seed_rnd.randint(1, 2)
    )

    return {
        "intereses": intereses,
        "cursos_inscritos": cursos_inscritos,
        "competencias": competencias,
        "preferencias_aprendizaje": preferencias,
    }


def crear_base_datos():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            perfil TEXT NOT NULL  -- columna JSON: intereses, cursos, competencias, preferencias
        )
    """)

    rnd = random.Random(42)  # semilla fija -> datos reproducibles
    for i, nombre in enumerate(NOMBRES, start=1):
        correo = nombre.lower().replace(" ", ".").replace("é", "e").replace(
            "í", "i").replace("á", "a").replace("ó", "o") + "@estudiantes.edu.co"
        perfil = generar_perfil(rnd)
        cur.execute(
            "INSERT INTO estudiantes (nombre, correo, perfil) VALUES (?, ?, ?)",
            (nombre, correo, json.dumps(perfil, ensure_ascii=False)),
        )

    conn.commit()
    conn.close()
    print(f"Base de datos creada en: {DB_PATH}")


if __name__ == "__main__":
    crear_base_datos()
