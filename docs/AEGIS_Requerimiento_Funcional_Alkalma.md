# AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico

**Organización:** Alkalma Health  
**Versión:** 1.0  
**Fecha:** 8 de septiembre de 2026  
**Estado:** Borrador funcional para validación  
**Idioma de implementación:** Por definir  

---

## 1. Propósito del documento

Este documento consolida los requerimientos funcionales conocidos para el diseño y desarrollo de **AEGIS**, una plataforma modular de inteligencia para gobierno clínico. La solución deberá centralizar los procesos de auditoría, seguimiento de hallazgos, mejora de la calidad, evaluación profesional, reportería y preparación regulatoria en un único ecosistema digital.

La plataforma no deberá reproducir el funcionamiento de una hoja de cálculo. Deberá operar sobre una base de datos central, con trazabilidad, control de acceso, flujos configurables y capacidad de incorporar nuevos módulos sin rediseñar la estructura existente.

## 2. Visión funcional

AEGIS será la fuente única de información para las actividades de gobierno clínico de Alkalma Health. Los datos se registrarán una sola vez y podrán reutilizarse, según los permisos aplicables, en auditorías, acciones correctivas, indicadores, evaluaciones profesionales, tableros, publicaciones y reportes regulatorios.

La plataforma deberá apoyar:

- Seguridad del paciente.
- Calidad y consistencia de la documentación clínica.
- Desarrollo y desempeño de los profesionales.
- Mejora continua.
- Supervisión por centro y a nivel corporativo.
- Cumplimiento de requisitos de DOH, JAWDA y otros marcos regulatorios aplicables.
- Preparación permanente de evidencia para auditorías externas.
- Evolución futura hacia funciones de inteligencia asistida por IA.

## 3. Principios de diseño

1. **Una sola fuente de verdad:** todos los módulos consultarán los mismos registros maestros.
2. **Registrar una vez, utilizar en todas partes:** no se duplicarán datos de usuarios, profesionales, centros, auditorías, hallazgos o evidencias.
3. **Arquitectura modular:** cada proceso tendrá límites funcionales claros y podrá evolucionar sin afectar los demás.
4. **Acceso basado en roles:** los permisos se asignarán mediante roles y no directamente a cada usuario.
5. **Trazabilidad completa:** toda creación, consulta sensible, modificación, aprobación, publicación y exportación deberá quedar registrada.
6. **Control de versiones:** las plantillas, criterios, guías, reportes y publicaciones deberán conservar su historial.
7. **Multi-centro y escalable:** la solución deberá soportar Al Bateen, Al Falah y nuevos centros, ciudades o países.
8. **Independencia del EMR:** la plataforma deberá poder funcionar con carga manual o importación de archivos y estar preparada para integración con el EMR.
9. **Configuración sobre código:** roles, permisos, centros, profesiones, criterios y catálogos deberán ser configurables siempre que sea viable.
10. **Privacidad desde el diseño:** cada usuario visualizará únicamente la información necesaria para su responsabilidad.

## 4. Alcance funcional consolidado

| Grupo | Módulos o componentes | Estado propuesto |
|---|---|---|
| Base de la plataforma | Autenticación; Usuarios, Organización y Accesos; Registro de Profesionales; Centros, Profesiones y Catálogos; Registro de Gobierno; Auditoría y Versiones | Fundación obligatoria |
| Gobierno clínico operativo | UCCA; Monitoreo de Medicación Psicotrópica y JAWDA; Acciones Correctivas; Inteligencia de Calidad; Reportería y Publicación | Alcance inicial/prioritario |
| Gobierno clínico complementario | Auditoría de Cumplimiento de Guías Clínicas (CPG) | Desarrollo prioritario complementario, independiente de UCCA |
| Evaluación y supervisión profesional | OPPE; FPPE; Peer Review; Credentialing & Privileging | Evolución planificada |
| Registros de gobierno | Incidentes; Quejas; CME Tracking | Evolución planificada |
| Inteligencia ejecutiva | Executive Dashboard; Governance Analytics; Regulatory Reporting | Evolución sobre la base de los módulos operativos |
| Inteligencia futura | Soporte de decisiones e inteligencia de gobierno asistida por IA | Futuro, sujeto a gobierno de datos y validación clínica |

## 5. Branding y experiencia Alkalma

La solución deberá desarrollarse con la identidad visual de **Alkalma Health** y no con una apariencia genérica de software.

### 5.1 Requerimientos de marca

- Utilizar el logotipo oficial, paleta de colores, tipografías, iconografía y lineamientos gráficos de Alkalma.
- Mostrar la identidad Alkalma en la pantalla de acceso, encabezado, navegación, correos, alertas, reportes, exportaciones y publicaciones.
- Presentar el producto como **“AEGIS — Clinical Governance Platform by Alkalma Health”**, sujeto a aprobación final de marca.
- Mantener una interfaz limpia, profesional, clínica y ejecutiva.
- Utilizar componentes visuales consistentes para estados, riesgos, alertas, vencimientos, cumplimiento y acciones pendientes.
- Permitir que los elementos de marca se administren mediante configuración central, sin modificar la lógica de negocio.
- Diseñar una experiencia adaptable a computador y tableta; la visualización móvil deberá ser al menos responsiva.

### 5.2 Insumos pendientes de marca

Antes de cerrar el diseño visual deberán entregarse o confirmarse: logotipo en formato digital, colores oficiales, tipografías, reglas de uso, plantillas de correo y plantilla corporativa de reportes.

## 6. Usuarios, autenticación y control de acceso

### 6.1 Acceso a la plataforma

La plataforma será privada. Ningún módulo ni dato deberá ser accesible sin autenticación válida.

El flujo mínimo será:

1. El usuario abre la pantalla de acceso con branding Alkalma.
2. Ingresa sus credenciales o utiliza el mecanismo corporativo de inicio de sesión cuando esté disponible.
3. El sistema valida el estado de la cuenta, los centros asignados, los roles y los permisos.
4. El usuario accede únicamente a los módulos, acciones y datos autorizados.
5. El sistema registra el ingreso y las actividades ejecutadas durante la sesión.

La solución deberá admitir inicialmente autenticación mediante usuario y contraseña segura y quedar preparada para Single Sign-On con Microsoft Entra ID/Active Directory y autenticación multifactor.

### 6.2 Usuario administrador inicial

Durante la configuración inicial deberá crearse un usuario con el rol **System Administrator** y acceso completo a todos los centros, módulos y funciones.

| Atributo | Definición |
|---|---|
| Tipo de cuenta | Usuario administrador inicial |
| Rol | System Administrator |
| Centros | Todos los centros actuales y futuros |
| Módulos | Acceso completo a todos los módulos actuales y futuros |
| Permisos | Ver, crear, editar, asignar, aprobar, publicar, exportar, configurar catálogos, administrar usuarios, roles y permisos, y consultar registros de auditoría |
| Estado inicial | Activo |
| Credenciales | No deberán quedar escritas en código ni en este documento |
| Primer acceso | Deberá exigir creación o cambio de contraseña y, cuando esté habilitado, MFA |
| Trazabilidad | Todas sus acciones deberán registrarse; el acceso completo no autoriza alterar o eliminar el historial inmutable |

El nombre, correo corporativo y número de empleado del administrador inicial se definirán antes del despliegue. Los permisos completos deberán otorgarse mediante el rol **System Administrator**, no mediante excepciones asignadas directamente a la cuenta.

### 6.3 Roles funcionales iniciales

- System Administrator.
- Governance Lead.
- Medical Director.
- Quality Manager/Quality Reviewer.
- Auditor.
- Reviewer.
- Approver.
- Clinician.
- Executive Viewer.
- External Auditor temporal, como capacidad futura.

Una persona podrá tener varios roles. El cargo organizacional no deberá determinar automáticamente los permisos de la plataforma.

### 6.4 Matriz de acceso de referencia

| Rol | Alcance de datos | Capacidades principales |
|---|---|---|
| System Administrator | Todos los centros | Administración completa de plataforma y configuración |
| Governance Lead | Según asignación, con posible alcance corporativo | Supervisar auditorías, hallazgos, acciones, aprobaciones, indicadores y reportes |
| Medical Director | Centros bajo su responsabilidad | Revisar expedientes asignados, supervisar acciones, aprobar o escalar hallazgos y consultar desempeño |
| Quality Manager/Reviewer | Centros asignados o corporativo | Validar criterios, revisar cumplimiento, monitorear indicadores y recibir reportes |
| Auditor | Auditorías y centros asignados | Crear y ejecutar auditorías, registrar evidencia y hallazgos |
| Reviewer | Registros asignados | Revisar resultados y solicitar correcciones |
| Approver | Elementos asignados | Aprobar auditorías, acciones o publicaciones según el flujo |
| Clinician | Información propia y casos asignados | Consultar retroalimentación, completar acciones y aportar evidencia |
| Executive Viewer | Información agregada autorizada | Consultar tableros y reportes ejecutivos sin modificar información |
| External Auditor | Alcance temporal y limitado | Consulta controlada de evidencia expresamente autorizada |

## 7. Módulos funcionales

### M01. Gestión de Usuarios, Organización y Accesos

**Objetivo:** controlar el acceso, establecer la estructura organizacional y vincular cada acción con un usuario autorizado.

**Funciones principales:**

- Crear, editar, activar, suspender, desactivar y archivar usuarios.
- Asignar uno o varios centros, una profesión, un cargo organizacional y uno o varios roles AEGIS.
- Crear y mantener roles y permisos configurables.
- Restringir acceso por centro y permitir supervisión corporativa cuando corresponda.
- Registrar fecha de creación, creador, último acceso, intentos fallidos e historial de inicio de sesión.
- Mantener las cuentas desactivadas para preservar la autoría histórica.
- Transferir responsabilidades pendientes cuando una persona deja la organización.
- Permitir accesos temporales con fecha de expiración para auditores externos en una fase futura.

**Reglas principales:**

- Cada usuario tendrá una cuenta única y un correo único.
- Todo usuario deberá tener al menos un centro y un rol.
- Todo usuario clínico deberá tener una profesión asignada.
- Los permisos se otorgarán mediante roles.
- Los cambios de rol aplicarán inmediatamente y no modificarán registros históricos.
- Ningún registro aprobado perderá la identificación de su autor.

**Entidades mínimas:** Users, Organizational Positions, Facilities, Professions, AEGIS Roles, Permissions, User Role Assignment, Role Permission Assignment, Login History y Activity Log.

**Salidas:** registro de usuarios, registro de roles, matriz de permisos, usuarios por centro/profesión/rol, cuentas inactivas, historial de acceso y reporte de seguridad.

### M02. Registro de Profesionales y Datos Maestros

**Objetivo:** administrar las entidades compartidas por todos los módulos y evitar su duplicación.

**Funciones principales:**

- Mantener el registro único de profesionales clínicos.
- Relacionar cada profesional con su usuario cuando tenga acceso a AEGIS.
- Administrar centros, países, ciudades, profesiones, especialidades, cargos y estados.
- Registrar el alcance profesional y las disciplinas aplicables.
- Activar o desactivar valores de catálogo sin borrar su historial.
- Incorporar nuevos centros y profesiones sin cambios estructurales.

**Datos mínimos del profesional:** identificador, número de empleado, nombre completo, profesión, especialidad, cargo, centro o centros, director responsable, estado y fechas de vigencia.

**Regla crítica:** el sistema deberá utilizar la profesión y el alcance de práctica para determinar criterios aplicables en UCCA y preclasificar como “No aplica” los indicadores regulatorios que no correspondan, conservando la razón de dicha clasificación.

### M03. Registro de Gobierno Clínico

**Objetivo:** ofrecer un índice central de las actividades y obligaciones de gobierno clínico.

**Funciones principales:**

- Registrar iniciativas, auditorías, comités, revisiones, obligaciones, riesgos y evidencias de gobierno.
- Relacionar cada elemento con centro, responsable, periodo, módulo de origen, estado y fecha de vencimiento.
- Permitir búsqueda y filtros por centro, periodo, responsable, tipo y estado.
- Conectar cada registro con sus documentos, acciones correctivas, decisiones, aprobaciones y publicaciones.

**Salidas:** registro corporativo de gobierno, calendario de obligaciones, elementos pendientes y evidencia disponible para revisión regulatoria.

### M04. Universal Clinical Competency Audit (UCCA)

**Objetivo:** digitalizar la auditoría universal de competencia clínica enfocada en gobierno clínico, calidad documental, estándares profesionales, seguridad del paciente y documentación regulatoria.

**Funciones principales:**

- Configurar ciclos, periodos, centros, muestras, disciplinas, profesionales y auditores.
- Crear plantillas de auditoría versionadas.
- Incorporar indicadores JAWDA y otros criterios regulatorios vigentes.
- Aplicar interpretación específica según profesión y alcance de práctica.
- Registrar cumplimiento, incumplimiento, no aplica, observaciones, evidencia y nivel de severidad.
- Calcular resultados por expediente, profesional, profesión, centro, criterio y periodo.
- Generar hallazgos y acciones correctivas desde los resultados.
- Registrar revisión, retroalimentación individual, aprobación y cierre del ciclo.
- Conservar la relación entre la versión de la plantilla y cada auditoría realizada.

**Reglas principales:**

- UCCA no sustituye una auditoría clínica específica por diagnóstico.
- Un criterio “No aplica” deberá estar sustentado por profesión, alcance o regla aprobada.
- Los resultados aprobados no deberán sobrescribirse; toda corrección generará trazabilidad o una nueva versión.
- Los resultados podrán alimentar OPPE, FPPE y Peer Review, pero estos seguirán siendo procesos independientes.

**Salidas:** resultado individual, resumen por profesional, comparativo por centro/profesión, tendencias, hallazgos, plan de mejora, indicadores JAWDA aplicables y evidencia para reportes.

### M05. Monitoreo de Medicación Psicotrópica y JAWDA

**Objetivo:** validar de forma estructurada el denominador de pacientes, clasificar primero la medicación y dirigir cada caso al criterio de monitoreo aplicable, evitando evaluar poblaciones no elegibles bajo OMH001.

**Funciones principales:**

- Importar o recibir desde el EMR la población completa del periodo sin alterar el archivo o conjunto maestro de origen.
- Identificar encuentros con antipsicóticos calificadores para OMH001.
- Generar una vista de **Antipsychotic Population** y otra de **Unique URNs**, eliminando duplicados para seguimiento a nivel de paciente.
- Validar la metodología de extracción y el denominador antes de iniciar auditorías masivas.
- Clasificar medicamentos y dirigirlos a rutas diferenciadas: antipsicóticos OMH001, estimulantes/ADHD, litio, valproato, carbamazepina, clozapina, antidepresivos y otros psicotrópicos.
- Registrar y verificar PHQ-9 y GAD-7 cuando correspondan.
- Registrar la fuente de la evidencia y distinguir información interna, externa o no verificable por ausencia de acceso a Malaffi.
- Asignar expedientes para revisión, registrar correcciones, comentarios clínicos, escalamiento y cierre.
- Soportar una revisión retrospectiva inicial y un flujo prospectivo semanal sostenible.

**Criterios OMH001 para antipsicóticos calificadores:**

- ECG.
- Full Blood Count.
- HbA1c.
- Lipid Profile.
- ALT.
- AST.
- Urea.
- Sodium.
- Potassium.
- Creatinine.

**Reglas principales:**

- La ventana regulatoria de cumplimiento será de los 12 meses precedentes.
- El sistema deberá generar una alerta interna de renovación a los 11 meses.
- Si existe una fecha exacta, deberá registrarse. Si únicamente puede verificarse mes y año, se registrará con esa precisión sin crear una fecha artificial.
- Los pacientes sin antipsicótico calificador no se evaluarán contra OMH001, pero podrán permanecer en la ruta de seguridad de medicación correspondiente.
- Los expedientes con riesgo clínico, de seguridad de medicación, diagnóstico dudoso o incumplimiento recurrente deberán escalarse al Medical Director.
- Las correcciones retrospectivas o entradas tardías deberán cumplir las normas de documentación y quedar en el audit trail.
- El profesional tratante será responsable de completar o corregir su documentación; el Medical Director tendrá responsabilidad de supervisión.

**Reporte semanal obligatorio:** cada lunes el sistema deberá generar el reporte de las prescripciones de antipsicóticos emitidas durante la semana anterior y distribuirlo a los Medical Directors y a los destinatarios de liderazgo configurados. Cada Medical Director deberá poder auditar durante la semana el registro completo de resultados de laboratorio y ECG correspondientes.

**Datos mínimos:** URN, centro, encuentro, prescriptor, medicamento, clase, indicador de elegibilidad OMH001, fechas y estados de investigaciones, precisión de fecha, fuente de evidencia, PHQ-9, GAD-7, estado de cumplimiento, brecha, responsable, fecha límite, acción, escalamiento y comentarios.

**Salidas:** denominador validado, población antipsicótica, pacientes únicos, brechas por investigación, alertas a 11 meses, cumplimiento OMH001, seguimiento PHQ-9/GAD-7, trabajo pendiente semanal y reporte automático del lunes.

### M06. Gestión de Acciones Correctivas

**Objetivo:** convertir hallazgos de cualquier módulo en acciones de mejora verificables y cerradas oportunamente.

**Funciones principales:**

- Crear acciones desde UCCA, CPG, medicación/JAWDA, incidentes, quejas, OPPE, FPPE o Peer Review.
- Registrar hallazgo de origen, causa, acción, responsable, prioridad, fecha de compromiso y evidencia requerida.
- Gestionar estados: borrador, asignada, en progreso, pendiente de validación, cerrada, vencida y cancelada con justificación.
- Enviar recordatorios y alertas de vencimiento.
- Permitir adjuntar evidencia y comentarios.
- Requerir revisión o aprobación antes del cierre cuando corresponda.
- Reabrir una acción conservando el historial.

**Salidas:** plan de acciones, vencimientos, acciones por responsable/centro/origen, tasa de cierre, tiempo de resolución, recurrencia y evidencia de mejora.

### M07. Auditoría de Cumplimiento de Guías de Práctica Clínica (CPG)

**Objetivo:** evaluar, de forma independiente a UCCA, la adherencia a guías clínicas basadas en evidencia para diagnósticos prioritarios.

**Funciones principales:**

- Mantener un registro versionado de guías aprobadas y una Clinical Audit Policy.
- Seleccionar al menos cinco diagnósticos de alto riesgo o propensos a error, alineados con el alcance de servicios.
- Configurar criterios clínicos por diagnóstico y versión de guía.
- Definir población, muestra, periodo, centro, líder clínico y auditores.
- Integrarse con el EMR o recibir datos estructurados para automatizar el monitoreo cuando sea posible.
- Registrar cumplimiento, desviación, justificación clínica, evidencia, hallazgos y acciones.
- Ejecutar auditoría trimestral liderada por un médico.
- Facilitar revisión por el Medical Director, comunicación formal a Quality y presentación colectiva de aprendizajes a los profesionales.
- Consolidar resultados en el tablero unificado sin fusionar la metodología con UCCA.

**Reglas principales:**

- UCCA y CPG serán procesos complementarios, pero independientes.
- Toda evaluación deberá conservar la guía y versión utilizadas.
- Los accesos al tablero CPG deberán incluir, como mínimo, a Clinicians y Quality según su ámbito autorizado.
- La implementación podrá iniciar como piloto en Al Bateen y posteriormente estandarizarse en los demás centros.

**Salidas:** cumplimiento por guía/diagnóstico/profesional/centro, brechas, tendencias, acciones correctivas, reporte médico trimestral y evidencia para DOH Ranking Audit.

### M08. Inteligencia y Tableros de Calidad

**Objetivo:** transformar la información operativa en indicadores y tendencias útiles para la mejora continua.

**Funciones principales:**

- Presentar indicadores de UCCA, CPG, JAWDA, medicación, acciones correctivas y futuros módulos.
- Permitir filtros por periodo, centro, profesión, profesional, auditoría, diagnóstico, indicador y estado.
- Mostrar cumplimiento, tendencia, variación, brechas, vencimientos, recurrencia y comparación entre centros.
- Permitir navegación desde un indicador agregado hasta los registros autorizados que lo originan.
- Diferenciar visualmente cumplimiento, riesgo, alerta y vencimiento.
- Exportar vistas y datos de acuerdo con los permisos.

**Vistas mínimas:** Quality Dashboard, desempeño por centro, desempeño por profesional, tendencias por criterio, acciones correctivas, cumplimiento regulatorio y seguridad de medicación.

### M09. Reportería y Publicación

**Objetivo:** generar reportes consistentes a partir de la fuente única de datos y controlar su revisión, aprobación y publicación.

**Funciones principales:**

- Generar reportes trimestrales, ejecutivos, de calidad, UCCA, CPG, OPPE, DOH/JAWDA y paquetes de evidencia regulatoria.
- Utilizar plantillas con branding Alkalma.
- Permitir borrador, revisión, aprobación, publicación y retiro controlado.
- Generar salidas en formatos definidos, incluyendo PDF y exportaciones tabulares cuando correspondan.
- Registrar autor, revisor, aprobador, fecha, versión, audiencia y periodo.
- Conservar versiones publicadas y evitar sobrescritura de documentos oficiales.
- Programar reportes recurrentes y distribuirlos únicamente a destinatarios autorizados.

**Publisher Engine:** deberá soportar paquetes controlados AEGIS-Q, Executive, OPPE y DOH, sujetos a confirmación de nomenclatura y plantilla.

### M10. Audit Trail y Control de Versiones

**Objetivo:** garantizar responsabilidad, integridad y reconstrucción histórica de todas las actividades relevantes.

**Funciones principales:**

- Registrar usuario, fecha/hora, módulo, registro, acción, valores anteriores y nuevos, origen y sesión.
- Conservar historial de inicio de sesión, intentos fallidos, cambios de roles y cambios de estado.
- Versionar plantillas de auditoría, criterios, guías, reglas, reportes y publicaciones.
- Identificar entradas retrospectivas o tardías.
- Permitir consulta y exportación del historial a usuarios autorizados.
- Impedir la modificación o eliminación ordinaria de eventos del audit trail.

**Regla crítica:** ni siquiera el System Administrator podrá borrar o reescribir el historial inmutable mediante la interfaz funcional.

### M11. OPPE — Ongoing Professional Practice Evaluation

**Objetivo:** evaluar de manera continua el desempeño profesional mediante información consolidada y criterios definidos.

**Funciones previstas:**

- Configurar periodos, criterios, umbrales y fuentes.
- Reutilizar resultados autorizados de UCCA, CPG, Peer Review, incidentes, quejas, CME y acciones correctivas.
- Generar perfil longitudinal del profesional.
- Registrar revisión, comentarios, plan de desarrollo, aprobación y cierre.
- Publicar un resumen OPPE versionado.

### M12. FPPE — Focused Professional Practice Evaluation

**Objetivo:** administrar evaluaciones focalizadas cuando un privilegio es nuevo o existe una preocupación específica de desempeño.

**Funciones previstas:**

- Registrar motivo, alcance, criterios, periodo, supervisor y profesional evaluado.
- Definir casos o evidencia requeridos.
- Integrar hallazgos, acciones, revisión y decisión final.
- Mantener confidencialidad reforzada y acceso limitado.
- Relacionar el resultado con Credentialing & Privileging cuando corresponda.

### M13. Peer Review

**Objetivo:** estructurar la revisión profesional de casos clínicos con criterios consistentes y trazabilidad.

**Funciones previstas:**

- Crear casos, asignar revisores y controlar conflictos de interés.
- Registrar criterios, evidencia, conclusión, oportunidad de mejora y recomendación.
- Mantener acceso confidencial según el rol.
- Generar acciones correctivas o FPPE cuando proceda.
- Alimentar OPPE mediante resultados aprobados y permitidos.

### M14. Credentialing & Privileging

**Objetivo:** administrar credenciales, vigencias, requisitos y privilegios clínicos.

**Funciones previstas:**

- Registrar credenciales, licencias, certificaciones, documentos, fechas de emisión y vencimiento.
- Configurar privilegios solicitados, aprobados, restringidos, suspendidos o vencidos.
- Enviar alertas de renovación.
- Gestionar revisión, aprobación y evidencia.
- Vincular decisiones con OPPE y FPPE sin duplicar información.

### M15. Gestión de Incidentes

**Objetivo:** registrar, evaluar y dar seguimiento a incidentes relacionados con seguridad y calidad.

**Funciones previstas:**

- Registrar incidente, fecha, centro, categoría, severidad y descripción.
- Aplicar acceso restringido y confidencial.
- Asignar investigación, análisis de causa y acciones.
- Escalar eventos según severidad y reglas configurables.
- Monitorear cierre, recurrencia, aprendizaje e impacto.

### M16. Gestión de Quejas

**Objetivo:** administrar quejas con trazabilidad, oportunidad de respuesta y conexión con la mejora clínica.

**Funciones previstas:**

- Registrar origen, categoría, centro, fecha, responsable y nivel de prioridad.
- Gestionar investigación, respuesta, acciones y cierre.
- Controlar plazos y escalamiento.
- Identificar tendencias y recurrencia.
- Vincular hallazgos relevantes con profesionales, centros o procesos mediante permisos apropiados.

### M17. CME Tracking

**Objetivo:** hacer seguimiento a la educación médica continua y a los requisitos de desarrollo profesional.

**Funciones previstas:**

- Registrar actividades, proveedor, fecha, tema, horas o créditos y evidencia.
- Configurar requisitos por profesión, cargo o periodo.
- Alertar sobre brechas y vencimientos.
- Integrar resultados con Credentialing, OPPE y planes de desarrollo.

### M18. Inteligencia Ejecutiva y Reportería Regulatoria

**Objetivo:** brindar una vista corporativa del desempeño, riesgo, madurez de gobierno y preparación regulatoria.

**Funciones principales:**

- Presentar Executive Dashboard, Governance Analytics y Regulatory Reporting.
- Consolidar información entre centros sin duplicar datos.
- Mostrar tendencias, riesgos prioritarios, acciones vencidas, recurrencia, cumplimiento y preparación regulatoria.
- Permitir comparación entre centros con definiciones consistentes.
- Generar paquetes de evidencia para auditorías y comités.
- Restringir la visualización de datos identificables cuando un indicador agregado sea suficiente.

### M19. Inteligencia de Gobierno Asistida por IA — Futuro

**Objetivo:** incorporar capacidades de apoyo analítico sin reemplazar la responsabilidad clínica o de gobierno.

**Capacidades potenciales:**

- Resumir hallazgos y tendencias.
- Detectar patrones, recurrencias o posibles áreas de riesgo.
- Sugerir borradores de acciones o reportes.
- Facilitar búsquedas sobre políticas, guías y evidencia autorizada.

**Condiciones obligatorias:** validación humana, control de acceso, registro de uso, fuentes identificables, protección de datos, monitoreo de calidad y prohibición de aprobación o decisión clínica autónoma.

## 8. Flujos funcionales integrados

### 8.1 Flujo general de auditoría

1. Se configura el periodo, centro, población, plantilla y responsables.
2. El auditor ejecuta la revisión y registra evidencia.
3. El sistema calcula o consolida resultados.
4. Los hallazgos pasan a revisión.
5. Los hallazgos aprobados pueden generar acciones correctivas.
6. El responsable completa la acción y aporta evidencia.
7. El revisor valida el cierre.
8. Los resultados actualizan tableros y reportes.
9. La publicación oficial conserva versión y aprobaciones.

### 8.2 Flujo semanal de medicación y JAWDA

1. El sistema recibe la población de la semana anterior.
2. Clasifica la medicación y valida la elegibilidad OMH001.
3. Genera población antipsicótica y listado de URN únicos.
4. Cada lunes distribuye el reporte a los destinatarios configurados.
5. El Medical Director asigna o supervisa la revisión del expediente completo.
6. Se verifican laboratorio, ECG, PHQ-9/GAD-7 y documentación aplicable.
7. Las brechas generan corrección, acción o escalamiento.
8. El sistema actualiza cumplimiento, alertas y trazabilidad durante la misma semana.

### 8.3 Flujo de publicación

1. Se genera un reporte desde datos aprobados.
2. El autor revisa el borrador.
3. El revisor solicita cambios o recomienda aprobación.
4. El aprobador autoriza la publicación.
5. El sistema asigna versión, fecha y audiencia.
6. La versión publicada queda bloqueada y disponible según permisos.

## 9. Capacidades transversales

### 9.1 Búsqueda y filtros

Todos los módulos deberán ofrecer búsqueda y filtros coherentes por los atributos aplicables, incluyendo centro, periodo, profesional, responsable, estado, severidad, módulo de origen y fecha límite.

### 9.2 Notificaciones y tareas

El sistema deberá generar notificaciones para asignaciones, solicitudes de revisión, aprobaciones, acciones próximas a vencer, acciones vencidas, alertas de 11 meses, expiración de credenciales y reportes programados. Los canales y destinatarios deberán ser configurables.

### 9.3 Documentos y evidencia

- Los archivos deberán vincularse al registro correspondiente y no quedar aislados.
- Cada evidencia deberá registrar autor, fecha de carga, tipo, versión y estado.
- La plataforma deberá controlar formatos y tamaños permitidos.
- El acceso a documentos deberá respetar las mismas reglas del registro de origen.

### 9.4 Importación, integración y exportación

- Permitir carga inicial y periódica de archivos estructurados.
- Validar encabezados, tipos, duplicados, campos obligatorios y errores antes de confirmar una importación.
- Conservar el origen, fecha y resultado de cada carga.
- Preparar servicios de integración con EMR, HR, Microsoft Entra ID/Active Directory y, cuando exista autorización, fuentes externas como Malaffi.
- Permitir exportación controlada a formatos tabulares y PDF según rol.
- Registrar las exportaciones de información sensible.

### 9.5 Configuración

Los siguientes elementos deberán ser administrables por usuarios autorizados: centros, profesiones, cargos, roles, permisos, catálogos, estados, severidades, plantillas, criterios, reglas de aplicación, umbrales, destinatarios, calendarios y plantillas de reporte.

## 10. Requerimientos no funcionales mínimos

| Categoría | Requerimiento |
|---|---|
| Seguridad | Cifrado en tránsito y reposo, contraseñas seguras, gestión de sesión, principio de mínimo privilegio y preparación para MFA/SSO |
| Privacidad | Acceso por necesidad de conocer, segregación por centro, control de datos identificables y registro de accesos sensibles |
| Integridad | Validaciones, relaciones referenciales, historial inmutable y versionado de elementos aprobados |
| Disponibilidad | Disponibilidad y respaldo acordes con la criticidad del proceso; objetivos concretos por definir |
| Rendimiento | Tableros, búsquedas y reportes deberán responder dentro de tiempos aceptables definidos durante el diseño técnico |
| Escalabilidad | Incorporación de nuevos centros, países, profesiones, roles, criterios y módulos sin rediseño estructural |
| Usabilidad | Interfaz coherente, validaciones claras, navegación por rol, formularios eficientes y reducción de entrada repetitiva |
| Accesibilidad | Contraste, navegación mediante teclado y etiquetas comprensibles; estándar objetivo por confirmar |
| Interoperabilidad | Integración mediante mecanismos documentados y desacoplados del EMR específico |
| Recuperación | Copias de seguridad, restauración y continuidad operativa; parámetros por definir con IT |

## 11. Reglas globales de negocio

1. Un registro aprobado o publicado no se sobrescribirá.
2. Las acciones de usuarios desactivados conservarán autoría e historial.
3. El acceso corporativo a varios centros dependerá del rol y la asignación explícita.
4. Los indicadores deberán mostrar definición, fuente, periodo y versión del criterio.
5. “No aplica” requerirá una regla o justificación trazable.
6. Toda modificación retrospectiva deberá identificarse como tal.
7. Las publicaciones oficiales deberán tener autor, revisor, aprobador y versión.
8. Los datos agregados deberán permitir trazabilidad hasta el origen únicamente para usuarios autorizados.
9. Los módulos futuros deberán reutilizar usuarios, profesionales, centros, evidencias, acciones y registros existentes.
10. Las reglas regulatorias y clínicas deberán ser configurables y versionadas para reflejar cambios sin alterar resultados históricos.

## 12. Criterios de aceptación de la primera entrega

La primera entrega funcional se considerará aceptable cuando, como mínimo:

- La pantalla de acceso utilice branding Alkalma y no permita acceso anónimo.
- Exista un usuario **System Administrator** activo, con acceso completo mediante rol, obligado a establecer una contraseña segura en su primer acceso.
- El administrador pueda crear usuarios, centros, profesiones, cargos, roles y permisos.
- Un usuario pueda tener varios roles y uno o varios centros.
- Los permisos oculten o bloqueen módulos y acciones no autorizadas.
- Existan registros maestros únicos de usuarios, profesionales, centros y profesiones.
- Se pueda crear un ciclo UCCA, asignar muestra y auditor, completar criterios, registrar evidencia y producir resultados.
- Los criterios UCCA puedan variar por profesión y registrar “No aplica” de forma justificada.
- Un hallazgo pueda convertirse en una acción correctiva con responsable, fecha y evidencia.
- El módulo de medicación pueda separar la población OMH001 calificada, deduplicar URN y registrar las diez investigaciones requeridas.
- El sistema calcule la ventana de 12 meses y genere alerta interna a los 11 meses.
- Se pueda producir el reporte semanal de antipsicóticos de la semana anterior para su distribución cada lunes.
- Los resultados aprobados alimenten el Quality Dashboard.
- Se pueda generar un reporte con branding Alkalma y someterlo a revisión, aprobación y publicación versionada.
- Toda acción relevante quede registrada en el audit trail.
- Los datos de dos centros permanezcan segregados para usuarios locales y consolidados para roles corporativos autorizados.

## 13. Fases propuestas

### Fase 1 — Fundación y operación inicial

- Branding Alkalma y autenticación.
- M01 Gestión de Usuarios, Organización y Accesos.
- M02 Registro de Profesionales y Datos Maestros.
- M04 UCCA.
- M05 Monitoreo de Medicación Psicotrópica y JAWDA.
- M06 Acciones Correctivas.
- M08 Quality Dashboard inicial.
- M09 Reportería y Publicación inicial.
- M10 Audit Trail y Control de Versiones.

### Fase 2 — Gobierno clínico complementario

- M03 Registro de Gobierno Clínico.
- M07 Auditoría CPG, iniciando con la definición de la política y al menos cinco guías prioritarias.
- Ampliación del Quality Dashboard y reportes regulatorios.

### Fase 3 — Desempeño y credenciales

- M11 OPPE.
- M12 FPPE.
- M13 Peer Review.
- M14 Credentialing & Privileging.

### Fase 4 — Ecosistema e inteligencia

- M15 Incidentes.
- M16 Quejas.
- M17 CME Tracking.
- M18 Inteligencia Ejecutiva y Reportería Regulatoria avanzada.
- M19 Inteligencia asistida por IA, únicamente después de aprobar sus controles de gobierno.

La secuencia final deberá validarse con Clinical Governance, Quality, Medical Directors, eHealth/IT y liderazgo ejecutivo. La prioridad regulatoria podría requerir que CPG se ejecute en paralelo con la estabilización de UCCA.

## 14. Decisiones pendientes para diseño detallado

1. Confirmar el kit oficial de branding Alkalma.
2. Confirmar nombre, correo y número de empleado del administrador inicial.
3. Definir si la primera versión usará credenciales locales, Microsoft SSO o ambos mecanismos.
4. Aprobar la matriz definitiva de roles, permisos y alcance por centro.
5. Entregar la plantilla UCCA final, fórmula de puntuación, criterios y reglas por profesión.
6. Confirmar el perfil JAWDA/DOH vigente y la lista oficial de antipsicóticos calificadores.
7. Aprobar las rutas de monitoreo para las demás clases de psicotrópicos.
8. Definir las cinco guías CPG iniciales, su Clinical Audit Policy y el líder clínico.
9. Confirmar los datos disponibles en EMR, frecuencia de extracción y viabilidad de integración con Malaffi.
10. Definir destinatarios del reporte de cada lunes y canal de distribución.
11. Definir periodos de retención, ubicación de alojamiento, respaldo, recuperación y requisitos regulatorios de seguridad.
12. Aprobar los formatos de reporte, nomenclaturas AEGIS-Q/Executive/OPPE/DOH y flujo de firma.
13. Completar los diccionarios de datos de los módulos futuros antes de su desarrollo.

## 15. Trazabilidad con las fuentes revisadas

| Fuente | Aporte principal al requerimiento |
|---|---|
| Descripcion.txt | Visión, propósito, enfoque de plataforma y principio de fuente única |
| AEGIS Charter Part I | Objetivos, principios, gobierno, fases y criterios de éxito |
| AEGIS Charter Part II | Arquitectura modular, módulos, reportería y Publisher Engine |
| Phase 1 Module 01 | Usuarios, estructura organizacional, roles, permisos, reglas y tablas base |
| Correso.txt y Correos.docx | Separación UCCA/CPG, JAWDA, despliegue multi-centro y requisitos de auditoría clínica |
| Platform architecture.docx | Inventario de componentes actuales, futuros y ejecutivos |
| track_mails.docx | Denominador OMH001, monitoreo de psicotrópicos, investigaciones, alertas y flujo semanal |

## 16. Resultado esperado

Al finalizar la implementación progresiva, Alkalma Health dispondrá de una plataforma privada y con identidad corporativa que conecte las actividades de gobierno clínico desde el registro operativo hasta la inteligencia ejecutiva y la evidencia regulatoria. Cada usuario trabajará con permisos definidos, cada resultado tendrá trazabilidad y los módulos compartirán una única base de información, evitando duplicación y facilitando la expansión futura de AEGIS.
