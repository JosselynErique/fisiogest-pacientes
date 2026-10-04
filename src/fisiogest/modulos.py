"""Registro de las slices verticales. Cada slice expone su propio Blueprint."""

from fisiogest.citas.features.agendar_cita.endpoint import bp as agendar_cita
from fisiogest.citas.features.cancelar_cita.endpoint import bp as cancelar_cita
from fisiogest.citas.features.consultar_agenda.endpoint import bp as consultar_agenda
from fisiogest.historial.features.consultar_historial.endpoint import bp as consultar_historial
from fisiogest.pacientes.features.actualizar_paciente.endpoint import bp as actualizar_paciente
from fisiogest.pacientes.features.dar_de_baja_paciente.endpoint import bp as dar_de_baja_paciente
from fisiogest.pacientes.features.listar_pacientes.endpoint import bp as listar_pacientes
from fisiogest.pacientes.features.registrar_paciente.endpoint import bp as registrar_paciente
from fisiogest.panel.features.ver_panel.endpoint import bp as ver_panel
from fisiogest.reportes.features.exportar_reporte.endpoint import bp as exportar_reporte
from fisiogest.reportes.features.generar_reporte.endpoint import bp as generar_reporte
from fisiogest.terapias.features.registrar_terapia.endpoint import bp as registrar_terapia
from fisiogest.usuarios.features.cambiar_estado_usuario.endpoint import bp as cambiar_estado_usuario
from fisiogest.usuarios.features.iniciar_sesion.endpoint import bp as iniciar_sesion
from fisiogest.usuarios.features.listar_usuarios.endpoint import bp as listar_usuarios
from fisiogest.usuarios.features.registrar_usuario.endpoint import bp as registrar_usuario

SLICES = (
    # Usuarios y acceso (RF-09)
    iniciar_sesion,
    listar_usuarios,
    registrar_usuario,
    cambiar_estado_usuario,
    # Panel
    ver_panel,
    # Pacientes (RF-01, RF-02, RF-03)
    registrar_paciente,
    listar_pacientes,
    actualizar_paciente,
    dar_de_baja_paciente,
    # Citas (RF-04, RF-05, RF-10)
    agendar_cita,
    consultar_agenda,
    cancelar_cita,
    # Terapias (RF-06)
    registrar_terapia,
    # Historial clínico (RF-07)
    consultar_historial,
    # Reportes (RF-08)
    generar_reporte,
    exportar_reporte,
)
