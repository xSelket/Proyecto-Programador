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
    InscripcionRespuesta,
    JornadaCrear,
    JornadaRespuesta,
    AsistenciaCrear,
    AsistenciaRespuesta,
    AlumnoJornadaRespuesta
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


@app.delete("/alumnos/{id_alumno}", status_code=204)
def eliminar_alumno(id_alumno: int, db: Session = Depends(obtener_db)):
    alumno = db.query(Alumno).filter(Alumno.id_alumno == id_alumno).first()

    if alumno is None:
        raise HTTPException(
            status_code=404,
            detail="El alumno no existe"
        )

    # Verificar si tiene inscripciones asociadas
    tiene_inscripciones = db.query(Inscripcion).filter(
        Inscripcion.id_alumno == id_alumno
    ).first()

    if tiene_inscripciones is not None:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el alumno porque tiene inscripciones asociadas"
        )

    db.delete(alumno)
    db.commit()

    return None

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

# JORNADAS

@app.get("/jornadas", response_model=list[JornadaRespuesta])
def listar_jornadas(db: Session = Depends(obtener_db)):
    jornadas = db.query(Jornada).order_by(
        Jornada.fecha.desc(),
        Jornada.id_jornada.desc()
    ).all()

    return jornadas


@app.post("/jornadas", response_model=JornadaRespuesta, status_code=201)
def crear_jornada(datos: JornadaCrear, db: Session = Depends(obtener_db)):
    curso = db.query(Curso).filter(
        Curso.id_curso == datos.id_curso
    ).first()

    if curso is None:
        raise HTTPException(
            status_code=404,
            detail="El curso no existe"
        )

    jornada_existente = db.query(Jornada).filter(
        Jornada.id_curso == datos.id_curso,
        Jornada.fecha == datos.fecha
    ).first()

    if jornada_existente is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una jornada para ese curso y fecha"
        )

    nueva_jornada = Jornada(
        id_curso=datos.id_curso,
        fecha=datos.fecha,
        hora_inicio=datos.hora_inicio,
        observaciones=datos.observaciones
    )

    db.add(nueva_jornada)
    db.commit()
    db.refresh(nueva_jornada)

    return nueva_jornada

# ASISTENCIAS

@app.get(
    "/jornadas/{id_jornada}/asistencias",
    response_model=list[AsistenciaRespuesta]
)
def listar_asistencias_de_jornada(
    id_jornada: int,
    db: Session = Depends(obtener_db)
):
    jornada = db.query(Jornada).filter(
        Jornada.id_jornada == id_jornada
    ).first()

    if jornada is None:
        raise HTTPException(
            status_code=404,
            detail="La jornada no existe"
        )

    asistencias = db.query(Asistencia).filter(
        Asistencia.id_jornada == id_jornada
    ).order_by(Asistencia.id_asistencia).all()

    return asistencias


@app.post(
    "/asistencias",
    response_model=AsistenciaRespuesta,
    status_code=201
)
def crear_asistencia(
    datos: AsistenciaCrear,
    db: Session = Depends(obtener_db)
):
    jornada = db.query(Jornada).filter(
        Jornada.id_jornada == datos.id_jornada
    ).first()

    if jornada is None:
        raise HTTPException(
            status_code=404,
            detail="La jornada no existe"
        )

    inscripcion = db.query(Inscripcion).filter(
        Inscripcion.id_inscripcion == datos.id_inscripcion
    ).first()

    if inscripcion is None:
        raise HTTPException(
            status_code=404,
            detail="La inscripción no existe"
        )

    if inscripcion.id_curso != jornada.id_curso:
        raise HTTPException(
            status_code=400,
            detail="La inscripción no corresponde al curso de esta jornada"
        )

    asistencia_existente = db.query(Asistencia).filter(
        Asistencia.id_jornada == datos.id_jornada,
        Asistencia.id_inscripcion == datos.id_inscripcion
    ).first()

    if asistencia_existente is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una asistencia para este alumno en la jornada"
        )

    if datos.estado not in ["Presente", "Tarde", "Ausente"]:
        raise HTTPException(
            status_code=422,
            detail="El estado debe ser Presente, Tarde o Ausente"
        )

    nueva_asistencia = Asistencia(
        id_jornada=datos.id_jornada,
        id_inscripcion=datos.id_inscripcion,
        estado=datos.estado,
        justificada=datos.justificada,
        observaciones=datos.observaciones
    )

    db.add(nueva_asistencia)
    db.commit()
    db.refresh(nueva_asistencia)

    return nueva_asistencia

@app.get(
    "/jornadas/{id_jornada}/alumnos",
    response_model=list[AlumnoJornadaRespuesta]
)
def listar_alumnos_de_jornada(
    id_jornada: int,
    db: Session = Depends(obtener_db)
):
    jornada = db.query(Jornada).filter(
        Jornada.id_jornada == id_jornada
    ).first()

    if jornada is None:
        raise HTTPException(
            status_code=404,
            detail="La jornada no existe"
        )

    inscripciones = db.query(Inscripcion).join(
        Alumno,
        Inscripcion.id_alumno == Alumno.id_alumno
    ).filter(
        Inscripcion.id_curso == jornada.id_curso,
        Inscripcion.fecha_alta <= jornada.fecha,
        (Inscripcion.fecha_baja.is_(None) |
         (Inscripcion.fecha_baja > jornada.fecha))
    ).order_by(
        Alumno.apellido,
        Alumno.nombre
    ).all()

    resultado = []

    for inscripcion in inscripciones:

        alumno = db.query(Alumno).filter(
            Alumno.id_alumno == inscripcion.id_alumno
        ).first()

        asistencia = db.query(Asistencia).filter(
            Asistencia.id_jornada == id_jornada,
            Asistencia.id_inscripcion == inscripcion.id_inscripcion
        ).first()

        resultado.append({
            "id_alumno": alumno.id_alumno,
            "nombre": alumno.nombre,
            "apellido": alumno.apellido,
            "dni": alumno.dni,
            "id_inscripcion": inscripcion.id_inscripcion,
            "id_asistencia": asistencia.id_asistencia if asistencia else None,
            "estado": asistencia.estado if asistencia else None,
            "justificada": asistencia.justificada if asistencia else False,
            "observaciones": asistencia.observaciones if asistencia else None
        })

    return resultado