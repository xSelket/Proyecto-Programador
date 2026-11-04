from pydantic import BaseModel, ConfigDict
from datetime import date



class CursoCrear(BaseModel):
    nombre: str
    turno: str | None = None
    cantidad_clases: int | None = None
    inasistencias_posibles: int | None = None
    id_familia: int | None = None


class CursoRespuesta(CursoCrear):
    id_curso: int

    model_config = ConfigDict(from_attributes=True)


class AlumnoCrear(BaseModel):
    nombre: str
    apellido: str
    dni: str
    telefono: str | None = None
    fnac: date | None = None
    mail: str | None = None


class AlumnoRespuesta(AlumnoCrear):
    id_alumno: int

    model_config = ConfigDict(from_attributes=True)
