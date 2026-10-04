# Evaluación de calidad — ISO/IEC 25010

**Sistema:** FisioGest v1.0 · **Fecha:** 03/10/2026 · **Evaluadores:** L. S. Taco Batson, J. S. Erique Robayo

**Escala:** 1 a 5 por característica → **Alto** (4,0–5,0) · **Medio** (3,0–3,9) · **Bajo** (< 3,0).
Cada nota se basa en evidencia medible del repositorio (pruebas, pipeline, mediciones), no en
apreciación.

## Resultados por característica

| Característica | Subcaracterísticas evaluadas | Evidencia / métrica | Nota | Nivel |
|---|---|---|---|---|
| **Adecuación funcional** | Completitud, corrección, pertinencia | 10/10 RF del SRS implementados; 150 pruebas automatizadas pasan; cada RF tiene al menos una prueba que lo verifica | 5,0 | Alto |
| **Eficiencia de desempeño** | Comportamiento temporal, capacidad | Promedio < 2 ms por página con datos demo; búsqueda entre 5 000 pacientes: 3,2 ms; listado completo de 5 000: 76 ms (RNF-01 exige < 3 s) | 4,5 | Alto |
| **Compatibilidad** | Interoperabilidad, coexistencia | Web estándar (cualquier navegador); exporta reportes a CSV (Excel); no expone API para otros sistemas | 3,5 | Medio |
| **Usabilidad** | Aprendizaje, protección contra errores, estética | Menú según rol, validación por campo con mensajes claros, confirmación de acciones destructivas, diseño responsivo. No se hizo prueba formal con usuarios reales | 4,0 | Alto |
| **Fiabilidad** | Madurez, tolerancia a fallos, recuperabilidad | Transacciones con *rollback*, claves foráneas y restricciones `UNIQUE`/`CHECK`; baja lógica conserva el historial. Sin respaldos automáticos; SQLite en un solo servidor | 3,5 | Medio |
| **Seguridad** | Confidencialidad, integridad, autenticidad, responsabilidad | Hash de contraseñas, bloqueo tras 5 intentos, CSRF, cabeceras CSP, control por rol probado. Faltan HTTPS en despliegue, bitácora de auditoría y cifrado de la base | 4,0 | Alto |
| **Mantenibilidad** | Modularidad, reusabilidad, analizabilidad, capacidad de prueba | Arquitectura hexagonal + slices verificada por pruebas; cobertura 89 %; ruff sin errores; CI en cada push | 4,8 | Alto |
| **Portabilidad** | Adaptabilidad, instalabilidad | Funciona en Windows/macOS/Linux con Python 3.10–3.12 (probado en CI); imagen Docker; una sola dependencia de ejecución | 4,5 | Alto |
| **Promedio** | | | **4,2** | **Alto** |

## Fortalezas

1. **Adecuación funcional completa**: todos los requerimientos del SRS están implementados y
   trazados a pruebas (CP-01 a CP-06).
2. **Mantenibilidad**: el núcleo no depende de Flask ni SQLite, lo que permite probarlo en
   milisegundos y cambiar la base de datos modificando solo adaptadores.
3. **Seguridad por defecto**: contraseñas cifradas (mejora pendiente identificada en la Unidad 3),
   protección CSRF y permisos por rol.

## Mejoras priorizadas

| Prioridad | Mejora | Característica | Esfuerzo |
|---|---|---|---|
| Alta | Respaldo automático diario de `fisiogest.db` y procedimiento de restauración | Fiabilidad | Bajo |
| Alta | Desplegar detrás de HTTPS (proxy inverso) con `SESSION_COOKIE_SECURE` | Seguridad | Bajo |
| Media | Bitácora de auditoría (quién modificó un paciente o canceló una cita) | Seguridad | Medio |
| Media | Paginación del listado de pacientes cuando supere 1 000 registros | Eficiencia | Bajo |
| Media | Prueba de usabilidad con la recepcionista y un fisioterapeuta (SUS) | Usabilidad | Bajo |
| Baja | API REST para integrar con facturación o recordatorios por WhatsApp | Compatibilidad | Alto |

## Cómo reproducir las mediciones

```bash
pytest -q                 # adecuación funcional: 150 pruebas
pytest --cov              # mantenibilidad: cobertura
ruff check .              # analizabilidad
```
