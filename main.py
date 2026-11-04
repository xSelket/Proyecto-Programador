from fastapi import FastAPI, Depends, HTTPException
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
from schemas import CursoCrear, CursoRespuesta, AlumnoCrear, AlumnoRespuesta

app = FastAPI(title="Sistema de Asistencia CFP Nº1")

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
def crear_alumno(
    datos: AlumnoCrear,
    db: Session = Depends(obtener_db)
):
    nombre = datos.nombre.strip()
    apellido = datos.apellido.strip()
    dni = datos.dni.strip()

    if not nombre or not apellido or not dni:
        raise HTTPException(
            status_code=422,
            detail="Nombre, apellido y DNI son campos obligatorios"
        )

    alumno_existente = db.query(Alumno).filter(Alumno.dni == dni).first()
    if alumno_existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un alumno registrado con ese DNI"
        )

    nuevo_alumno = Alumno(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        telefono=datos.telefono.strip() if datos.telefono else None,
        fnac=datos.fnac,
        mail=datos.mail.strip() if datos.mail else None
    )

    db.add(nuevo_alumno)
    db.commit()
    db.refresh(nuevo_alumno)

    return nuevo_alumno
