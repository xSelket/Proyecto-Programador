from datetime import date, time

from pydantic import BaseModel, ConfigDict


# -------------------------
# ESQUEMAS DE CURSOS
# -------------------------

class CursoCrear(BaseModel):
    nombre: str
    turno: str | None = None
    cantidad_clases: int | None = None
    inasistencias_posibles: int | None = None
    id_familia: int | None = None


class CursoRespuesta(CursoCrear):
    id_curso: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# ESQUEMAS DE ALUMNOS
# -------------------------

class AlumnoCrear(BaseModel):
    nombre: str
    apellido: str
    telefono: str | None = None
    fnac: date | None = None
    dni: str
    mail: str | None = None


class AlumnoRespuesta(AlumnoCrear):
    id_alumno: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# ESQUEMAS DE INSCRIPCIONES
# -------------------------

class InscripcionCrear(BaseModel):
    id_alumno: int
    id_curso: int
    fecha_alta: date


class InscripcionRespuesta(InscripcionCrear):
    id_inscripcion: int
    fecha_baja: date | None = None

    model_config = ConfigDict(from_attributes=True)

# JORNADAS

class JornadaCrear(BaseModel):
    id_curso: int
    fecha: date
    hora_inicio: time | None = None
    observaciones: str | None = None


class JornadaRespuesta(JornadaCrear):
    id_jornada: int
    model_config = ConfigDict(from_attributes=True)

# ASISTENCIAS

class AsistenciaCrear(BaseModel):
    id_jornada: int
    id_inscripcion: int
    estado: str
    justificada: bool = False
    observaciones: str | None = None


class AsistenciaRespuesta(AsistenciaCrear):
    id_asistencia: int
    model_config = ConfigDict(from_attributes=True)

# ALUMNOS DE UNA JORNADA

class AlumnoJornadaRespuesta(BaseModel):
    id_alumno: int
    nombre: str
    apellido: str
    dni: str
    id_inscripcion: int
    id_asistencia: int | None = None
    estado: str | None = None
    justificada: bool = False
    observaciones: str | None = None