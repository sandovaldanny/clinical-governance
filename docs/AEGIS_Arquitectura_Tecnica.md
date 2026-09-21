# AEGIS — Arquitectura Técnica de la Plataforma de Gobierno Clínico

**Organización:** Alkalma Health
**Versión:** 1.0
**Fecha:** 8 de septiembre de 2026
**Estado:** Borrador técnico para validación
**Documento base:** AEGIS_Requerimiento_Funcional_Alkalma.md (v1.0)

---

## 1. Propósito y alcance de este documento

Este documento traduce el requerimiento funcional de AEGIS en una arquitectura técnica implementable. Cubre el modelo de componentes, el stack tecnológico propuesto, el modelo de datos, el enfoque de seguridad y control de acceso, el diseño del audit trail inmutable, las integraciones externas, la estrategia de despliegue y la hoja de ruta técnica alineada a las cuatro fases funcionales definidas por el negocio.

No sustituye las decisiones pendientes listadas en la sección 14 del requerimiento funcional (branding, SSO vs. credenciales locales, alcance JAWDA vigente, etc.); donde el requerimiento deja una decisión abierta, este documento propone una opción por defecto y la marca explícitamente como **supuesto a validar**.

## 2. Principios arquitectónicos

Los diez principios de diseño del requerimiento funcional (sección 3) se traducen en las siguientes decisiones técnicas:

| Principio funcional | Traducción arquitectónica |
|---|---|
| Una sola fuente de verdad | Base de datos relacional única con esquema compartido de entidades maestras (usuarios, profesionales, centros, catálogos); ningún módulo mantiene copias propias |
| Registrar una vez, usar en todas partes | Entidades maestras expuestas como servicios/dominios internos consumidos por todos los módulos vía la capa de aplicación, nunca duplicadas por tabla |
| Arquitectura modular | Monolito modular por dominios (module-per-bounded-context) dentro de un mismo repositorio y base de datos, no microservicios distribuidos, dado el tamaño de equipo y la necesidad de consistencia transaccional fuerte |
| Acceso basado en roles | RBAC con roles, permisos y asignación por centro, resuelto en un middleware de autorización centralizado, no en cada módulo |
| Trazabilidad completa | Tabla de eventos append-only (audit ledger) alimentada automáticamente por la capa de persistencia, no por lógica de cada módulo |
| Control de versiones | Versionado explícito de entidades configurables (plantillas, criterios, guías, reportes) mediante tablas `*_versions` con estado vigente/histórico |
| Multi-centro y escalable | Segregación de datos por `facility_id` en cada tabla operativa, con políticas de Row-Level Security a nivel de base de datos, no solo filtros de aplicación |
| Independencia del EMR | Capa de importación desacoplada (archivos + API) que normaliza datos externos a las entidades internas antes de que cualquier módulo los consuma |
| Configuración sobre código | Catálogos, roles, permisos, criterios y umbrales almacenados como datos configurables, administrables desde UI, no como constantes de código |
| Privacidad desde el diseño | Autorización a nivel de fila y de campo, con vistas agregadas para roles ejecutivos que no exponen identificadores individuales |

**Supuesto a validar:** se asume un equipo de desarrollo de tamaño moderado (no una organización con decenas de squads), lo que justifica el monolito modular frente a microservicios. Si Alkalma prevé escalar el equipo de ingeniería significativamente o distribuir el desarrollo entre proveedores independientes por módulo, la arquitectura de microservicios por dominio (M04, M05, M09, etc.) sería una alternativa a reconsiderar en el diseño detallado.

## 3. Vista de alto nivel

```
                         ┌─────────────────────────────────────┐
                         │           Usuarios (web/tablet)       │
                         └───────────────────┬───────────────────┘
                                              │ HTTPS
                         ┌───────────────────▼───────────────────┐
                         │        Frontend SPA (branding Alkalma) │
                         └───────────────────┬───────────────────┘
                                              │ REST/GraphQL (JWT)
                         ┌───────────────────▼───────────────────┐
                         │              API Gateway / BFF          │
                         │   (rate limiting, routing, logging)     │
                         └───────────────────┬───────────────────┘
                                              │
        ┌────────────────────┬───────────────┼───────────────┬────────────────────┐
        │                    │                │               │                    │
┌───────▼──────┐   ┌─────────▼────────┐ ┌─────▼──────┐ ┌──────▼───────┐  ┌─────────▼─────────┐
│ Auth &        │   │ Módulos de        │ │ Motor de   │ │ Publisher /  │  │ Notificaciones &   │
│ Autorización  │   │ Gobierno Clínico   │ │ Reglas &   │ │ Reportería   │  │ Jobs programados   │
│ (RBAC, SSO)   │   │ (UCCA, JAWDA, CPG, │ │ Cálculo    │ │ (branding,   │  │ (semanal lunes,    │
│               │   │ Acciones, OPPE...) │ │ (scoring,  │ │ versiones)   │  │ alertas 11 meses)  │
│               │   │                    │ │ elegibilidad)│              │                    │
└───────┬───────┘   └─────────┬──────────┘ └─────┬──────┘ └──────┬───────┘  └─────────┬──────────┘
        │                     │                    │              │                    │
        └─────────────────────┴────────────────────┴──────────────┴────────────────────┘
                                              │
                         ┌───────────────────▼───────────────────┐
                         │      Capa de datos maestros y de       │
                         │   dominio (PostgreSQL, RLS por centro) │
                         └───────────────────┬───────────────────┘
                                              │
                         ┌───────────────────▼───────────────────┐
                         │   Audit Ledger (append-only, inmutable) │
                         └─────────────────────────────────────────┘
                                              │
        ┌─────────────────────────────────────┴─────────────────────────────────────┐
        │                     Capa de integración e importación                      │
        │   Importador de archivos │ Conectores EMR │ Entra ID/AD │ Malaffi (futuro)  │
        └───────────────────────────────────────────────────────────────────────────┘
```

Las líneas de flujo relevantes: todo módulo pasa por el middleware de autorización antes de leer o escribir; todo `INSERT/UPDATE` sobre entidades gobernadas dispara un evento de auditoría; el Publisher Engine y el motor de notificaciones consumen datos ya aprobados, nunca escriben directamente sobre los registros operativos.

## 4. Stack tecnológico propuesto

| Capa | Propuesta | Justificación |
|---|---|---|
| Frontend | React + TypeScript, componentes con sistema de diseño propio (tokens de marca Alkalma configurables) | Ecosistema maduro, soporta la exigencia de tablero ejecutivo, formularios de auditoría complejos y responsividad tableta/escritorio |
| Backend | API REST modular en Python (FastAPI) organizada por dominios (bounded contexts) | Coherente con el stack que Alkalma ya usa en otros proyectos de gobierno de datos (FastAPI + ETL en el proyecto PHM Grafos); permite reutilizar patrones y conocimiento del equipo |
| Base de datos | PostgreSQL 16+, con Row-Level Security nativo por `facility_id` | Consistencia transaccional fuerte necesaria para auditorías, versionado y flujos de aprobación; RLS resuelve la segregación multi-centro a nivel de motor de base de datos, no solo de aplicación |
| Audit ledger | Tabla append-only en PostgreSQL con triggers, replicada a almacenamiento de solo-anexado (ej. blob storage con políticas de retención inmutable) | Cumple el requisito de que ni siquiera el System Administrator pueda alterar el historial vía interfaz funcional |
| Autenticación | Usuario/contraseña propio (fase 1) + OIDC/SAML contra Microsoft Entra ID (fase posterior), MFA vía Entra ID o proveedor TOTP | Cumple el requisito explícito de preparación para SSO corporativo y MFA sin bloquear el arranque del proyecto |
| Autorización | Middleware RBAC centralizado con resolución de permisos por rol + centro, cacheado por sesión | Evita que cada módulo implemente su propia lógica de permisos, reduciendo riesgo de fugas de datos entre centros |
| Cola de trabajos / jobs programados | Motor de tareas asíncronas (ej. Celery + Redis, o equivalente gestionado en la nube) | Necesario para el reporte semanal obligatorio de los lunes, alertas a los 11 meses, recordatorios de vencimiento y notificaciones |
| Almacenamiento de evidencia/documentos | Blob storage (Azure Blob o equivalente) con control de acceso heredado del registro de origen | Los documentos deben respetar los mismos permisos que el registro al que están vinculados; el storage de objetos separa el binario de los metadatos gobernados en PostgreSQL |
| Generación de reportes | Motor de plantillas (ej. HTML→PDF) parametrizado por branding Alkalma, con almacenamiento inmutable de versiones publicadas | Cumple el requisito de plantillas versionadas y no sobrescritura de documentos oficiales |
| Infraestructura / nube | Microsoft Azure, región con residencia de datos en EAU (o la más cercana con garantías equivalentes) | Alineado con el requisito de integración con Microsoft Entra ID/AD y con la infraestructura Azure ya utilizada por Alkalma en otro proyecto de gobierno de datos clínicos |
| Contenedores / despliegue | Contenedores (Docker) orquestados en Azure Container Apps o AKS, según el volumen esperado | Permite escalar horizontalmente los módulos con más carga (ej. UCCA en periodos de auditoría masiva) sin sobredimensionar el resto |
| Observabilidad | Logging centralizado, métricas y trazas (ej. Azure Monitor / OpenTelemetry) | Necesario para cumplir los requisitos no funcionales de rendimiento, disponibilidad y detección temprana de fallos en jobs críticos como el reporte semanal |

**Supuesto a validar:** la elección de Azure como nube principal asume que Alkalma prefiere consolidar su infraestructura en un solo proveedor (coherente con el uso de Entra ID y con el proyecto PHM Grafos existente). Si eHealth/IT tiene una política de nube distinta, el diseño de dominios y RLS se mantiene igual; solo cambian los servicios gestionados equivalentes.

## 5. Arquitectura de datos

### 5.1 Entidades maestras (fuente única de verdad)

Un núcleo de entidades maestras, propiedad de M01 y M02, es consumido por todos los módulos sin duplicación:

`Users`, `Organizational Positions`, `Facilities`, `Professions`, `AEGIS Roles`, `Permissions`, `User Role Assignment`, `Role Permission Assignment`, `Professionals`, `Catalog Values` (genérico para valores de catálogo activables/desactivables).

Cada módulo funcional (UCCA, CPG, medicación/JAWDA, acciones correctivas, incidentes, quejas, OPPE, FPPE, Peer Review, Credentialing, CME) define sus propias tablas de dominio, pero **referencia** estas entidades maestras por clave foránea; nunca las copia.

### 5.2 Segregación multi-centro

Toda tabla operativa incluye `facility_id`. Las políticas de Row-Level Security en PostgreSQL filtran automáticamente por los centros asignados al usuario autenticado, de modo que un `SELECT` mal construido en un módulo no pueda filtrar datos de otro centro por error de programación. Los roles corporativos (Governance Lead, Executive Viewer con alcance ampliado) reciben una política RLS que permite el alcance multi-centro explícitamente autorizado.

### 5.3 Versionado

Las entidades configurables versionadas (plantillas de auditoría UCCA, guías CPG, criterios, reportes, publicaciones) siguen un patrón de tabla `entity` + `entity_version`, donde cada versión queda vinculada a los registros que la usaron (ej. cada auditoría UCCA queda ligada a la versión exacta de plantilla con la que se ejecutó, aunque la plantilla evolucione después).

### 5.4 Inmutabilidad de resultados aprobados

Los registros aprobados o publicados no se sobrescriben (regla global de negocio #1). Técnicamente esto se implementa con un campo `status` (`draft` → `submitted` → `approved`/`published`) y una restricción a nivel de aplicación y de base de datos que bloquea `UPDATE`/`DELETE` sobre filas en estado `approved` o `published`; cualquier corrección genera una nueva versión con referencia a la anterior.

### 5.5 Modelo de datos por grupo de módulos (nivel conceptual)

- **Gobierno operativo (M03–M09):** `governance_items`, `audits`, `audit_templates`, `audit_criteria`, `audit_results`, `findings`, `corrective_actions`, `medication_reviews`, `investigations`, `cpg_guidelines`, `cpg_audits`.
- **Evaluación profesional (M11–M14):** `oppe_cycles`, `fppe_cases`, `peer_review_cases`, `credentials`, `privileges`, con acceso restringido reforzado (ver sección 6.4).
- **Registros de gobierno (M15–M17):** `incidents`, `complaints`, `cme_activities`.
- **Inteligencia (M08, M18):** vistas materializadas y agregaciones sobre los dominios anteriores; no almacenan datos primarios, se recalculan o refrescan periódicamente.

## 6. Autenticación, autorización y control de acceso

### 6.1 Autenticación

Fase 1: usuario y contraseña con políticas de complejidad y expiración configurables, hash con algoritmo moderno (ej. Argon2). Fase posterior: federación OIDC/SAML con Microsoft Entra ID, permitiendo convivencia de ambos mecanismos durante la transición. El diseño de la tabla `Users` desacopla la identidad interna del método de autenticación (`auth_provider`, `external_id`) para que activar SSO no requiera migrar datos de usuario.

### 6.2 Autorización (RBAC)

- Un middleware único resuelve, para cada request, el conjunto de permisos efectivos del usuario a partir de sus roles y centros asignados, y lo adjunta al contexto de la petición.
- Los permisos se definen como pares `(módulo, acción)` (ver, crear, editar, aprobar, publicar, exportar, configurar) y se agrupan en roles configurables desde UI, nunca hardcodeados en el backend.
- El rol **System Administrator** se implementa como un rol con todos los permisos otorgados por configuración, no como un `bypass` de código, de modo que sus acciones también queden sujetas al audit trail y a las mismas restricciones de inmutabilidad.

### 6.3 Cuenta administradora inicial

Se aprovisiona mediante un script de despliegue (seed) que crea el usuario, fuerza cambio de contraseña en el primer acceso y, cuando MFA esté habilitado, exige su configuración antes de conceder acceso completo. Las credenciales iniciales no se almacenan en el repositorio de código ni en documentación; se generan y comunican por un canal seguro fuera de banda.

### 6.4 Confidencialidad reforzada

Los módulos FPPE, Peer Review, incidentes y quejas requieren una capa adicional de restricción de campo (no solo de fila): ciertos campos (identidad del reportante, detalles del caso) son visibles únicamente para roles explícitamente autorizados, incluso dentro de un centro donde el usuario ya tiene acceso general. Esto se implementa con una segunda capa de autorización a nivel de campo en la capa de servicio, además del RLS de fila.

## 7. Audit trail y control de versiones (M10)

- Cada operación de creación, modificación, aprobación, publicación y exportación relevante genera un evento inmutable con: usuario, fecha/hora, módulo, entidad, acción, valores anteriores/nuevos, origen (IP/sesión) e indicador de si es una entrada retrospectiva o tardía.
- El evento se genera automáticamente desde la capa de persistencia (triggers o interceptores en el ORM), no depende de que cada módulo recuerde registrarlo, para evitar huecos de trazabilidad.
- La tabla de auditoría es de solo inserción; ningún rol, incluido System Administrator, tiene permiso de `UPDATE`/`DELETE` sobre ella a nivel de base de datos (revocado explícitamente, no solo oculto en la UI).
- Se recomienda replicar periódicamente el ledger a almacenamiento con política de inmutabilidad (WORM) como capa adicional de protección ante un compromiso a nivel de base de datos.

## 8. Motor de reglas y cálculo (UCCA, JAWDA/OMH001, CPG)

Dado que UCCA, el monitoreo de medicación/JAWDA y CPG comparten la necesidad de aplicar criterios configurables por profesión, diagnóstico o clase de medicamento, se propone un **motor de reglas desacoplado** en lugar de lógica embebida en cada módulo:

- Las reglas de aplicabilidad ("No aplica" por profesión/alcance), la ventana de cumplimiento de 12 meses para OMH001, la alerta a los 11 meses y la clasificación de medicamentos por ruta (antipsicóticos, litio, valproato, carbamazepina, clozapina, antidepresivos, estimulantes) se definen como configuración versionada, evaluada por un servicio común.
- Este motor expone una API interna (`evaluate(context, ruleset_version)`) que UCCA, JAWDA y CPG consumen de forma consistente, evitando que cada módulo reimplemente su propia lógica de elegibilidad y produciendo resultados auditable y reproducibles para una versión de reglas dada.
- Toda evaluación conserva la referencia a la versión del criterio/guía usada, cumpliendo el requisito de que los indicadores muestren definición, fuente, periodo y versión.

## 9. Flujo semanal de medicación y JAWDA (M05)

Este es el flujo con mayor exigencia de automatización y el más sensible a fallos silenciosos, por lo que se diseña como un **job programado con verificación explícita**, no como un proceso manual:

1. Job nocturno/semanal recibe o importa la población del EMR (archivo o API) sin alterar el conjunto de origen (se conserva copia cruda + versión normalizada).
2. El motor de reglas clasifica la medicación y determina elegibilidad OMH001, generando las vistas `Antipsychotic Population` y `Unique URNs` (deduplicadas).
3. Un job programado, ejecutado cada lunes en una ventana horaria fija, genera el reporte y lo distribuye a los Medical Directors y destinatarios de liderazgo configurados.
4. El sistema calcula automáticamente la ventana de 12 meses por investigación (ECG, hemograma, HbA1c, perfil lipídico, ALT, AST, urea, sodio, potasio, creatinina) y genera alerta interna a los 11 meses.
5. Toda ejecución del job queda registrada (éxito, fallo, cantidad de registros procesados) con alertas a IT si el job no corre o produce menos registros de los esperados, para que un fallo de integración no pase desapercibido antes del lunes.

**Supuesto a validar:** se asume que la carga inicial del EMR será por archivo estructurado (no API en tiempo real) dado que el requerimiento indica independencia del EMR con posibilidad de integración futura. El diseño del importador ya contempla ambos modos para no requerir rediseño cuando la integración directa esté disponible.

## 10. Reportería y Publisher Engine (M09)

- Los reportes se generan exclusivamente a partir de datos en estado `approved`, nunca de datos en borrador, evitando publicar cifras que luego cambien.
- El Publisher Engine mantiene un flujo de estados (`draft` → `in_review` → `approved` → `published` → `retired`) con autor, revisor, aprobador, versión, audiencia y periodo registrados en cada paso.
- Las plantillas de reporte (AEGIS-Q, Executive, OPPE, DOH) se versionan igual que las plantillas de auditoría, con el branding Alkalma aplicado mediante un sistema de tokens de marca centralizado (logo, colores, tipografías) para que el equipo de marketing/comunicación pueda actualizarlos sin tocar código.
- Las versiones publicadas se almacenan como artefactos inmutables (PDF generado + metadata), nunca regeneradas in situ sobre el mismo identificador de versión.

## 11. Integraciones (sección 9.4 del requerimiento)

| Integración | Enfoque técnico | Estado propuesto |
|---|---|---|
| Importación de archivos estructurados | Validación de encabezados, tipos, duplicados y campos obligatorios antes de confirmar; registro de origen, fecha y resultado de cada carga | Fase 1 |
| EMR | Adaptador desacoplado (archivo o API según disponibilidad) que normaliza a las entidades internas; AEGIS nunca escribe de vuelta al EMR en el alcance actual | Fase 1 (archivo), evolución a API |
| Microsoft Entra ID / Active Directory | OIDC/SAML para SSO + sincronización opcional de atributos de usuario (no de permisos AEGIS, que permanecen configurados dentro de la plataforma) | Fase 1 preparación, activación posterior |
| HR | Importación periódica de altas/bajas/cambios organizacionales para mantener sincronizados centros, cargos y estado de cuenta | Evolución posterior |
| Malaffi | Conector futuro, sujeto a autorización regulatoria; hasta entonces, el sistema distingue explícitamente evidencia interna, externa y "no verificable por ausencia de acceso a Malaffi" como estado de dato, no como ausencia silenciosa | Futuro, condicionado |

## 12. Notificaciones y trabajos programados (sección 9.2)

Motor de notificaciones desacoplado de cada módulo, que se suscribe a eventos del dominio (asignación, vencimiento próximo, vencido, alerta de 11 meses, expiración de credenciales, reporte programado) y resuelve canal y destinatarios desde configuración (no hardcodeado por módulo). Esto permite añadir nuevos tipos de alerta (ej. para módulos futuros de Fase 3–4) sin modificar el motor.

## 13. Seguridad y privacidad

- Cifrado en tránsito (TLS 1.2+) y en reposo (cifrado nativo de la base de datos y del almacenamiento de objetos).
- Gestión de sesión con expiración configurable, revocación inmediata al desactivar un usuario y registro de intentos fallidos.
- Principio de mínimo privilegio aplicado tanto a usuarios finales (RBAC) como a componentes técnicos (cada servicio interno usa credenciales de base de datos con permisos acotados a su dominio).
- Registro de accesos sensibles (no solo modificaciones): consultas a expedientes de FPPE, Peer Review, incidentes y quejas quedan auditadas como "consulta sensible", conforme al principio 5 del requerimiento.
- Exportaciones de información sensible quedan registradas con usuario, fecha, alcance y formato.

## 14. Requerimientos no funcionales — enfoque técnico

| Categoría | Enfoque propuesto | Parámetro pendiente de definir con IT |
|---|---|---|
| Disponibilidad | Despliegue con redundancia (múltiples instancias de aplicación, base de datos con réplica) | SLA objetivo (ej. 99.5% vs. 99.9%) |
| Rendimiento | Índices por `facility_id` + periodo en tablas de alto volumen (resultados UCCA, medicación); vistas materializadas para tableros | Tiempos de respuesta objetivo por tipo de consulta |
| Escalabilidad | Contenedores escalables horizontalmente por dominio de mayor carga (UCCA en periodos de auditoría masiva) | Volumen esperado de usuarios concurrentes y centros a 3 años |
| Recuperación | Backups automáticos con retención definida, pruebas periódicas de restauración, punto de recuperación (RPO) y tiempo de recuperación (RTO) objetivo | RPO/RTO acordados con IT y requisitos regulatorios de retención |
| Accesibilidad | Componentes de UI con contraste AA, navegación por teclado, etiquetas ARIA | Confirmar estándar objetivo (WCAG 2.1 AA sugerido) |

## 15. Hoja de ruta técnica alineada a las fases funcionales

**Fase 1 — Fundación y operación inicial:** implementar el núcleo de entidades maestras, RBAC, autenticación local, audit ledger, UCCA, monitoreo de medicación/JAWDA con el motor de reglas, acciones correctivas, Quality Dashboard inicial, Publisher Engine básico. Esta fase concentra el mayor riesgo técnico (motor de reglas, job semanal, RLS multi-centro) y debe validarse exhaustivamente antes de avanzar.

**Fase 2 — Gobierno clínico complementario:** extender el motor de reglas a CPG reutilizando la misma infraestructura de versionado de criterios; ampliar tableros y reportería regulatoria.

**Fase 3 — Desempeño y credenciales:** OPPE, FPPE, Peer Review, Credentialing, con la capa de confidencialidad reforzada de la sección 6.4.

**Fase 4 — Ecosistema e inteligencia:** incidentes, quejas, CME, inteligencia ejecutiva avanzada y, solo tras aprobar sus controles de gobierno, capacidades asistidas por IA (M19) implementadas como servicios auxiliares de solo lectura sobre datos ya aprobados, nunca con capacidad de aprobación o decisión autónoma.

## 16. Riesgos técnicos principales

1. **Motor de reglas OMH001/JAWDA mal calibrado:** un error en la clasificación de medicamentos o en el cálculo de la ventana de 12 meses tendría impacto regulatorio directo. Mitigación: suite de pruebas con casos reales anonimizados antes de producción, y periodo de validación en paralelo con el proceso manual actual.
2. **RLS multi-centro incompleto:** si alguna tabla nueva omite `facility_id` o su política RLS, se rompe la segregación de datos. Mitigación: plantilla de migración estándar que exige `facility_id` + política RLS como parte del checklist de revisión de código para toda tabla nueva.
3. **Job semanal silenciosamente fallido:** si el reporte de los lunes no se genera o se genera incompleto sin alerta, el impacto regulatorio es alto. Mitigación: monitoreo activo del job con alerta a IT ante fallo o volumen anómalo.
4. **Dependencia de integración EMR aún no definida:** el diseño de importación debe tolerar tanto carga manual como integración futura sin rediseño; validar con eHealth/IT la viabilidad real antes de comprometer fechas de Fase 1.
5. **Alcance de "inmutable" mal implementado:** si la restricción de no-sobrescritura vive solo en la aplicación y no en la base de datos, un acceso directo a la base de datos podría violarla. Mitigación: reforzar con permisos de base de datos, no solo lógica de aplicación.

## 17. Decisiones técnicas pendientes de confirmar con eHealth/IT

1. Proveedor de nube definitivo y región (se propone Azure/EAU como supuesto).
2. Mecanismo definitivo de autenticación de la primera versión (local, SSO, o ambos en paralelo).
3. Disponibilidad real de API del EMR y de Malaffi, y ventana de tiempo esperada para esa integración.
4. RPO/RTO y política de retención de backups y del audit ledger.
5. Volumen esperado de usuarios y centros a 3 años, para dimensionar la estrategia de escalado.
6. Estándar de accesibilidad objetivo a certificar.
7. Política de nomenclatura y flujo de firma para los paquetes de reporte AEGIS-Q/Executive/OPPE/DOH.

---

*Este documento debe leerse junto con AEGIS_Requerimiento_Funcional_Alkalma.md. Las secciones marcadas como "supuesto a validar" requieren confirmación de Clinical Governance, Quality, Medical Directors y eHealth/IT antes de congelar el diseño detallado.*
