from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Time,
    Boolean,
    Text,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint
)

from database import Base


class FamiliaProf(Base):
    __tablename__ = "familias_prof"

    id_familia = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)


class Curso(Base):
    __tablename__ = "cursos"

    id_curso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)

    turno = Column(String(30), nullable=True)

    cantidad_clases = Column(Integer, nullable=True)
    inasistencias_posibles = Column(Integer, nullable=True)

    id_familia = Column(
        Integer,
        ForeignKey("familias_prof.id_familia"),
        nullable=True
    )


class Alumno(Base):
    __tablename__ = "alumnos"

    id_alumno = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)

    telefono = Column(String(30), nullable=True)
    fnac = Column(Date, nullable=True)

    dni = Column(String(20), nullable=False, unique=True)
    mail = Column(String(150), nullable=True)


class Inscripcion(Base):
    __tablename__ = "inscripciones"

    id_inscripcion = Column(Integer, primary_key=True, index=True)

    id_alumno = Column(
        Integer,
        ForeignKey("alumnos.id_alumno"),
        nullable=False
    )

    id_curso = Column(
        Integer,
        ForeignKey("cursos.id_curso"),
        nullable=False
    )

    fecha_alta = Column(Date, nullable=False)
    fecha_baja = Column(Date, nullable=True)


class Jornada(Base):
    __tablename__ = "jornadas"

    id_jornada = Column(Integer, primary_key=True, index=True)

    id_curso = Column(
        Integer,
        ForeignKey("cursos.id_curso"),
        nullable=False
    )

    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=True)
    observaciones = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "id_curso",
            "fecha",
            name="uq_jornada_curso_fecha"
        ),
    )


class Asistencia(Base):
    __tablename__ = "asistencias"

    id_asistencia = Column(Integer, primary_key=True, index=True)

    id_jornada = Column(
        Integer,
        ForeignKey("jornadas.id_jornada"),
        nullable=False
    )

    id_inscripcion = Column(
        Integer,
        ForeignKey("inscripciones.id_inscripcion"),
        nullable=False
    )

    estado = Column(String(10), nullable=False)

    justificada = Column(Boolean, nullable=False, default=False)
    observaciones = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "id_jornada",
            "id_inscripcion",
            name="uq_asistencia_jornada_inscripcion"
        ),
        CheckConstraint(
            "estado IN ('Presente', 'Tarde', 'Ausente')",
            name="ck_asistencia_estado"
        ),
    )