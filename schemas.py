from datetime import date

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