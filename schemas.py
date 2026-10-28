from pydantic import BaseModel, ConfigDict


class CursoCrear(BaseModel):
    nombre: str
    turno: str | None = None
    cantidad_clases: int | None = None
    inasistencias_posibles: int | None = None
    id_familia: int | None = None


class CursoRespuesta(CursoCrear):
    id_curso: int

    model_config = ConfigDict(from_attributes=True)