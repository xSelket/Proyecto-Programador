from datetime import date

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import (
    FamiliaProf,
    Curso,
    Alumno,
    Inscripcion,
    Jornada,
    Asistencia
)

from schemas import (
    CursoCrear,
    CursoRespuesta,
    AlumnoCrear,
    AlumnoRespuesta,
    InscripcionCrear,
    InscripcionRespuesta
)

app = FastAPI(title="Sistema de Asistencia CFP Nº1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


# Abrir una sesión de base de datos por petición
def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def inicio():
    return {"mensaje": "API de asistencia funcionando"}


# Listar cursos almacenados en SQLite
@app.get("/cursos", response_model=list[CursoRespuesta])
def listar_cursos(db: Session = Depends(obtener_db)):
    return db.query(Curso).order_by(Curso.id_curso).all()


# Crear un curso nuevo
@app.post("/cursos", response_model=CursoRespuesta, status_code=201)
def crear_curso(
    datos: CursoCrear,
    db: Session = Depends(obtener_db)
):
    nombre = datos.nombre.strip()

    if not nombre:
        raise HTTPException(
            status_code=422,
            detail="El nombre del curso es obligatorio"
        )

    # Si se indicó una familia, verificar que exista
    if datos.id_familia is not None:
        familia = db.query(FamiliaProf).filter(
            FamiliaProf.id_familia == datos.id_familia
        ).first()

        if familia is None:
            raise HTTPException(
                status_code=404,
                detail="La familia profesional no existe"
            )

    nuevo_curso = Curso(
        nombre=nombre,
        turno=datos.turno,
        cantidad_clases=datos.cantidad_clases,
        inasistencias_posibles=datos.inasistencias_posibles,
        id_familia=datos.id_familia
    )

    db.add(nuevo_curso)
    db.commit()
    db.refresh(nuevo_curso)

    return nuevo_curso

@app.get("/alumnos", response_model=list[AlumnoRespuesta])
def listar_alumnos(db: Session = Depends(obtener_db)):
    return db.query(Alumno).order_by(Alumno.apellido, Alumno.nombre).all()


@app.post("/alumnos", response_model=AlumnoRespuesta, status_code=201)
def crear_alumno(datos: AlumnoCrear, db: Session = Depends(obtener_db)):
    nombre = datos.nombre.strip()
    apellido = datos.apellido.strip()
    dni = datos.dni.strip()

    if not nombre or not apellido or not dni:
        raise HTTPException(
            status_code=422,
            detail="Nombre, apellido y DNI son obligatorios"
        )

    alumno_existente = db.query(Alumno).filter(Alumno.dni == dni).first()

    if alumno_existente is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un alumno con ese DNI"
        )

    nuevo_alumno = Alumno(
        nombre=nombre,
        apellido=apellido,
        telefono=datos.telefono,
        fnac=datos.fnac,
        dni=dni,
        mail=datos.mail
    )

    db.add(nuevo_alumno)
    db.commit()
    db.refresh(nuevo_alumno)

    return nuevo_alumno
# -------------------------
# ENDPOINTS DE INSCRIPCIONES
# -------------------------


# Listar todas las inscripciones
@app.get("/inscripciones", response_model=list[InscripcionRespuesta])
def listar_inscripciones(db: Session = Depends(obtener_db)):

    inscripciones = db.query(Inscripcion).order_by(
        Inscripcion.id_inscripcion
    ).all()

    return inscripciones


# Crear una inscripción
@app.post("/inscripciones", response_model=InscripcionRespuesta, status_code=201)
def crear_inscripcion(
    datos: InscripcionCrear,
    db: Session = Depends(obtener_db)
):

    # Verificar que exista el alumno
    alumno = db.query(Alumno).filter(
        Alumno.id_alumno == datos.id_alumno
    ).first()

    if alumno is None:
        raise HTTPException(
            status_code=404,
            detail="El alumno no existe"
        )

    # Verificar que exista el curso
    curso = db.query(Curso).filter(
        Curso.id_curso == datos.id_curso
    ).first()

    if curso is None:
        raise HTTPException(
            status_code=404,
            detail="El curso no existe"
        )

    # Verificar que no exista una inscripción activa
    inscripcion_existente = db.query(Inscripcion).filter(
        Inscripcion.id_alumno == datos.id_alumno,
        Inscripcion.id_curso == datos.id_curso,
        Inscripcion.fecha_baja.is_(None)
    ).first()

    if inscripcion_existente is not None:
        raise HTTPException(
            status_code=409,
            detail="El alumno ya tiene una inscripción activa en este curso"
        )

    # Crear la inscripción
    nueva_inscripcion = Inscripcion(
        id_alumno=datos.id_alumno,
        id_curso=datos.id_curso,
        fecha_alta=datos.fecha_alta
    )

    db.add(nueva_inscripcion)
    db.commit()
    db.refresh(nueva_inscripcion)

    return nueva_inscripcion


# Listar alumnos activos de un curso
@app.get("/cursos/{id_curso}/alumnos", response_model=list[AlumnoRespuesta])
def listar_alumnos_de_curso(
    id_curso: int,
    db: Session = Depends(obtener_db)
):

    # Verificar que exista el curso
    curso = db.query(Curso).filter(
        Curso.id_curso == id_curso
    ).first()

    if curso is None:
        raise HTTPException(
            status_code=404,
            detail="El curso no existe"
        )

    # Buscar alumnos con inscripción activa
    alumnos = db.query(Alumno).join(
        Inscripcion,
        Alumno.id_alumno == Inscripcion.id_alumno
    ).filter(
        Inscripcion.id_curso == id_curso,
        Inscripcion.fecha_baja.is_(None)
    ).order_by(
        Alumno.apellido,
        Alumno.nombre
    ).all()

    return alumnos


# Listar cursos activos de un alumno
@app.get("/alumnos/{id_alumno}/cursos", response_model=list[CursoRespuesta])
def listar_cursos_de_alumno(
    id_alumno: int,
    db: Session = Depends(obtener_db)
):

    # Verificar que exista el alumno
    alumno = db.query(Alumno).filter(
        Alumno.id_alumno == id_alumno
    ).first()

    if alumno is None:
        raise HTTPException(
            status_code=404,
            detail="El alumno no existe"
        )

    # Buscar cursos con inscripción activa
    cursos = db.query(Curso).join(
        Inscripcion,
        Curso.id_curso == Inscripcion.id_curso
    ).filter(
        Inscripcion.id_alumno == id_alumno,
        Inscripcion.fecha_baja.is_(None)
    ).order_by(
        Curso.nombre
    ).all()

    return cursos