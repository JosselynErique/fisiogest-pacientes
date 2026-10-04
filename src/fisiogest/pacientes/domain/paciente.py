from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from fisiogest.shared.domain.errors import DomainError, Errores
from fisiogest.shared.domain.validators import (
    es_cedula_valida,
    es_correo_valido,
    es_telefono_valido,
    limpiar,
    parsear_fecha,
)


@dataclass(frozen=True)
class DatosPaciente:
    """Datos de entrada tal como llegan del formulario (comando)."""

    cedula: str = ""
    nombres: str = ""
    apellidos: str = ""
    fecha_nacimiento: str = ""
    telefono: str = ""
    correo: str = ""
    direccion: str = ""
    contacto_emergencia: str = ""


@dataclass
class Paciente:
    cedula: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date | None = None
    telefono: str = ""
    correo: str = ""
    direccion: str = ""
    contacto_emergencia: str = ""
    activo: bool = True
    id: int | None = None
    creado_en: datetime = field(default_factory=datetime.now)
    actualizado_en: datetime | None = None

    @classmethod
    def crear(cls, datos: DatosPaciente, hoy: date | None = None) -> Paciente:
        return cls(**_validar(datos, hoy or date.today()))

    def actualizar(self, datos: DatosPaciente, hoy: date | None = None) -> None:
        if not self.activo:
            raise DomainError("No se puede modificar un paciente dado de baja. Reactívelo primero.")
        for campo, valor in _validar(datos, hoy or date.today()).items():
            setattr(self, campo, valor)
        self.actualizado_en = datetime.now()

    def dar_de_baja(self) -> None:
        if not self.activo:
            raise DomainError("El paciente ya se encuentra dado de baja.")
        self.activo = False
        self.actualizado_en = datetime.now()

    def reactivar(self) -> None:
        if self.activo:
            raise DomainError("El paciente ya está activo.")
        self.activo = True
        self.actualizado_en = datetime.now()

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"

    def edad(self, hoy: date | None = None) -> int | None:
        if self.fecha_nacimiento is None:
            return None
        hoy = hoy or date.today()
        n = self.fecha_nacimiento
        return hoy.year - n.year - ((hoy.month, hoy.day) < (n.month, n.day))


def _validar(datos: DatosPaciente, hoy: date) -> dict:
    errores = Errores()
    cedula = limpiar(datos.cedula)
    nombres = limpiar(datos.nombres)
    apellidos = limpiar(datos.apellidos)
    telefono = limpiar(datos.telefono).replace(" ", "")
    correo = limpiar(datos.correo).lower()

    if not cedula:
        errores.agregar("cedula", "La cédula es obligatoria.")
    elif not es_cedula_valida(cedula):
        errores.agregar("cedula", "La cédula ecuatoriana no es válida.")
    if len(nombres) < 2:
        errores.agregar("nombres", "Los nombres son obligatorios.")
    if len(apellidos) < 2:
        errores.agregar("apellidos", "Los apellidos son obligatorios.")

    fecha_nacimiento = None
    if datos.fecha_nacimiento:
        fecha_nacimiento = parsear_fecha(datos.fecha_nacimiento)
        if fecha_nacimiento is None:
            errores.agregar("fecha_nacimiento", "Fecha de nacimiento inválida.")
        elif fecha_nacimiento > hoy:
            errores.agregar("fecha_nacimiento", "La fecha de nacimiento no puede ser futura.")
        elif hoy.year - fecha_nacimiento.year > 120:
            errores.agregar("fecha_nacimiento", "La fecha de nacimiento no es razonable.")

    if telefono and not es_telefono_valido(telefono):
        errores.agregar(
            "telefono", "Teléfono inválido. Use 10 dígitos (09XXXXXXXX) o un fijo con código."
        )
    if correo and not es_correo_valido(correo):
        errores.agregar("correo", "El correo electrónico no es válido.")
    errores.lanzar_si_hay()

    return {
        "cedula": cedula,
        "nombres": nombres.title(),
        "apellidos": apellidos.title(),
        "fecha_nacimiento": fecha_nacimiento,
        "telefono": telefono,
        "correo": correo,
        "direccion": limpiar(datos.direccion),
        "contacto_emergencia": limpiar(datos.contacto_emergencia),
    }
