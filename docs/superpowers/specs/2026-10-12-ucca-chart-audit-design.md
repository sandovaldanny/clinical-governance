# UCCA — Auditoría por expediente (chart audit), score, outcome y dashboard

**Fecha:** 2026-10-12 · **Estado:** aprobado en conversación, pendiente de revisión escrita
**Módulos:** M04 UCCA (gobierno clínico), M06 Acciones correctivas · **Fuente:** Excel
"Universal Clinical Competency Audit with JAWDA / OMH Regulatory Indicators" del equipo clínico.

## 1. Objetivo

Que el director médico audite expedientes clínicos de forma simple: elige profesional y
expediente, responde Yes / No / N/A a los 7 criterios de evaluación (CCA, CRS, CTP, COM, CDC, CEP,
CMC), ve score y outcome en vivo y, si el resultado no es *Compliant*, registra hallazgo y acción
correctiva en la misma pantalla. El ciclo muestra una tabla equivalente a la hoja Excel y un
dashboard consolida resultados por centro, profesional, criterio y trimestre.

Fuera de alcance en esta iteración: capa OMH / JAWDA del Excel (columnas regulatorias), OPPE/FPPE,
exportación a Excel, notificaciones.

## 2. Decisiones tomadas con el usuario

| Tema | Decisión |
|---|---|
| Unidad de auditoría | Un expediente (MRN / Case Ref) de un profesional dentro de un ciclo; 7 respuestas en una sola pantalla. |
| N/A | Razón corta **obligatoria** por cada N/A (regla global #5 del funcional). |
| Hallazgo y acción correctiva | Sección al pie de la misma auditoría, visible cuando outcome < Compliant. Se persiste como `Finding` + `CorrectiveAction` (M06), nunca como texto suelto. |
| CG_ID | Es el código del profesional auditado = `professionals.employee_number`. No se crea campo nuevo. |
| Profesionales auditables | Todos los profesionales activos del centro del ciclo (los 7 criterios son universales). |
| Año / trimestre | Se formalizan en el ciclo (`year`, `quarter`) para filtrar en dashboard; `period_label` se mantiene como etiqueta visible. |
| Capa OMH / JAWDA | Fase posterior. |

## 3. Modelo de datos (migración `0007_ucca_chart_audits`)

### 3.1 Tablas

**`ucca_chart_audits`** — cabecera, equivale a una fila del Excel.

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID PK | |
| `cycle_id` | FK `ucca_audit_cycles` | |
| `facility_id` | UUID | copiado del ciclo; RLS multi-centro |
| `professional_id` | FK `professionals` | CG_ID y profesión se leen del profesional |
| `auditor_user_id` | UUID | usuario que registra (por defecto el actual) |
| `case_reference` | String 80 | MRN / Case Ref |
| `audit_date` | Date | por defecto hoy |
| `status` | String 20 | `draft` → `submitted` → `approved` |
| `applicable_count` | Integer | calculado |
| `yes_count` | Integer | calculado |
| `score` | Numeric(5,2) nullable | % con 2 decimales; `NULL` si `applicable_count = 0` |
| `outcome` | String 40 nullable | `compliant` · `minor_improvement` · `improvement_required` · `priority_corrective_action`; `NULL` si score `NULL` |
| `notes` | String 1000 | comentario general opcional |
| `created_at`, `updated_at` | timestamptz | |

Restricción única `(cycle_id, professional_id, case_reference)` → 409 si se repite.

**`ucca_audit_results`** (existente) — una fila por criterio de la auditoría.

- Nueva columna `chart_audit_id` FK `ucca_chart_audits`, **NOT NULL**. La tabla está vacía en todos
  los entornos conocidos; la migración borra filas huérfanas antes de añadir la columna.
- `outcome` sigue siendo `compliant | non_compliant | not_applicable` (= Yes / No / N/A).
- `not_applicable_reason` obligatorio cuando `outcome = not_applicable` (ya validado en servicio).
- Nueva columna `comment` String 500 nullable.
- `cycle_id`, `facility_id`, `professional_id`, `auditor_user_id` se conservan (denormalizados
  desde la cabecera) para no romper RLS ni consultas por criterio.
- `status` de cada resultado se sincroniza con el de la cabecera.
- Única `(chart_audit_id, criterion_id)`.

**`ucca_findings`** (existente) — hallazgo a nivel expediente (*Key Finding*).

- Nueva columna `chart_audit_id` FK nullable; `result_id` pasa a nullable (hallazgo de expediente
  no apunta a un criterio concreto). Check: al menos uno de los dos no nulo.
- `description` = Key Finding.

**`corrective_actions`** (existente, M06).

- Nuevas columnas: `description` String 1000 (Corrective Action), `closure_evidence` String 1000
  nullable, `closed_at` timestamptz nullable.
- `status`: `assigned` · `in_progress` · `closed` (Action Status).
- `responsible_user_id` = Action Owner, `due_date` = Due Date.

**`ucca_audit_cycles`** (existente).

- Nuevas columnas `year` Integer, `quarter` String 2 (`Q1`…`Q4`), ambas NOT NULL con backfill
  desde `period_label` (`Q3-2026` → 2026 / Q3).

### 3.2 Cálculo (función pura en `ucca/scoring.py`)

```
applicable = respuestas con outcome != not_applicable
yes        = respuestas con outcome == compliant
score      = None si applicable == 0, si no round(yes / applicable * 100, 2)
outcome    = None            si score is None
             compliant       si score >= 90
             minor_improvement        si score >= 80
             improvement_required     si score >= 70
             priority_corrective_action en otro caso
```

Umbrales en una constante `OUTCOME_BANDS` del módulo (documentada); pasar a catálogo configurable
queda como mejora posterior. Se recalcula en cada guardado mientras `status = draft`. Una auditoría
`approved` es inmutable (regla global #1): cabecera, respuestas y hallazgo.

### 3.3 Permisos

Se reutilizan: `ucca.view` (leer), `ucca.create` (crear / editar borrador / enviar),
`ucca.approve` (aprobar), `corrective_actions.manage` (hallazgo + acción). Director médico y
Governance Lead ya los tienen en el seed.

## 4. API (`/ucca`)

| Método y ruta | Permiso | Descripción |
|---|---|---|
| `GET /cycles` | ucca.view | ya existe; añade `year`, `quarter`, `facility_name`, `audits_count`, `average_score` |
| `POST /cycles` | ucca.create | ya existe; body pasa a `{facility_id, year, quarter}`; `period_label` se deriva (`Q2-2026`); plantilla vigente se resuelve en servidor; 409 si ya existe ciclo centro+año+trimestre |
| `GET /cycles/{id}/audits` | ucca.view | filas Excel: cabecera + `answers: {CCA: "yes", …}` + `finding` resumida |
| `POST /cycles/{id}/audits` | ucca.create | crea cabecera + 7 respuestas + hallazgo/acción opcionales en un payload; devuelve calculados |
| `GET /audits/{id}` | ucca.view | detalle completo (para editar / ver) |
| `PATCH /audits/{id}` | ucca.create | solo `draft`; reemplaza respuestas y datos; recalcula; 409 si no es borrador |
| `POST /audits/{id}/submit` | ucca.create | `draft → submitted` |
| `POST /audits/{id}/approve` | ucca.approve | `submitted → approved`; marca resultados aprobados; inmutable después |
| `GET /cycles/{id}/summary` | ucca.view | agregados del ciclo (§6) |
| `GET /dashboard?facility_id&year&quarter` | ucca.view | agregados multi-ciclo (§6) |

Payload de creación / edición:

```json
{
  "professional_id": "…", "case_reference": "102453", "audit_date": "2026-07-20",
  "notes": "",
  "answers": [
    {"criterion_id": "…", "outcome": "compliant", "comment": null, "not_applicable_reason": null}
  ],
  "finding": {
    "description": "…",
    "corrective_action": {"description": "…", "responsible_user_id": "…", "due_date": "2026-08-30",
                          "status": "assigned", "closure_evidence": null}
  }
}
```

Reglas de validación (422): exactamente una respuesta por criterio activo de la plantilla del
ciclo; `not_applicable_reason` no vacío si N/A; `finding.description` obligatorio si outcome
calculado ≠ `compliant` **y** hay al menos un `non_compliant`; `corrective_action` requiere
`responsible_user_id` y `due_date`. Profesional debe estar activo y pertenecer al centro del ciclo.

Se eliminan `POST /results` y `GET /results` sueltos (sustituidos por las rutas de auditoría);
`POST /results/{id}/approve` se elimina (la aprobación es por expediente).

Toda escritura pasa por `record_event` (`module="ucca"`, entidades `ChartAudit`, `AuditResult`,
`Finding`; `module="corrective_actions"` para `CorrectiveAction`).

## 5. UI

Navegación: *Gobierno clínico* → **UCCA — Ciclos**, **UCCA — Dashboard**, Indicadores.

### 5.1 `/ucca` — Ciclos
Tabla existente + botón **Nuevo ciclo** (drawer: centro, año, trimestre). Clic en periodo → página
del ciclo. Columnas: Periodo · Centro · Expedientes · Score medio · Estado.

### 5.2 `/ucca/cycles/:cycleId` — Página del ciclo
- Cabecera: centro, periodo, estado, botón **Nueva auditoría**.
- 4 KPIs: expedientes auditados · score medio · % Compliant · acciones correctivas abiertas.
- Tabla tipo Excel (sin scroll horizontal; chips compactos): # · CG_ID · Profesional · Profesión ·
  MRN · Fecha · Auditor · CCA · CRS · CTP · COM · CDC · CEP · CMC · Aplic. · Yes · Score · Outcome ·
  Estado · Ver/Editar. Chips: ✓ turquesa (Yes), ✗ rojo (No), "N/A" gris. Outcome como badge:
  Compliant turquesa · Minor Improvement ámbar · Improvement Required ámbar oscuro · Priority
  Corrective Action rojo.

### 5.3 `/ucca/cycles/:cycleId/audits/new` y `/ucca/audits/:auditId` — Auditar expediente
Una sola pantalla, tres bloques:
1. **Datos**: profesional (select de activos del centro; al elegir muestra CG_ID y profesión),
   MRN / Case Ref, fecha (hoy), auditor (usuario actual, solo lectura).
2. **Criterios**: 7 tarjetas en orden de código. Cada una: `CCA · Clinical Assessment`, pregunta
   universal, "Ver interpretación y evidencia" desplegable, selector segmentado **Yes / No / N/A**
   (turquesa / rojo / gris), campo "Razón de N/A" obligatorio al marcar N/A, comentario opcional.
3. **Hallazgo y acción correctiva**: aparece cuando el outcome en vivo ≠ Compliant. Key finding,
   acción correctiva, responsable (usuarios activos), fecha límite, estado, evidencia de cierre.

Barra fija inferior: Aplicables · Yes · **Score %** · **Outcome** (badge) en vivo + botones
*Guardar borrador*, *Enviar*, *Aprobar* (según permiso y estado). Auditoría aprobada → todo en
solo lectura con aviso.

### 5.4 `/ucca/dashboard`
Filtros: centro, año, trimestre. KPIs globales; barras "% Yes por criterio"; tabla por profesional
(CG_ID, nombre, profesión, expedientes, score medio, outcome, % por criterio); tendencia de score
por trimestre; lista de acciones correctivas abiertas (hallazgo, responsable, vencimiento, estado).

## 6. Agregados (`summary` / `dashboard`)

Por ciclo o por filtro: `audits_count`, `average_score`, `outcome_distribution` (conteo por
banda), `criteria` (por criterio: aplicables, yes, `% yes`), `professionals` (por profesional:
CG_ID, nombre, profesión, expedientes, score medio, outcome del promedio con las mismas bandas,
`% yes` por criterio), `open_corrective_actions`. Solo se agregan auditorías `submitted` o
`approved` (los borradores no cuentan); se indica `draft_count` aparte.

## 7. Seed de demostración

Ciclo Q2-2026 Al Bateen con 5 expedientes (102453, 100598, AKAD00132, AKAD00264, 101460) del
profesional Dr. Ahmed Al Bateen auditados por governance.lead@, todos Yes (como el Excel), más
1 expediente con 2 No y hallazgo + acción correctiva asignada para que el dashboard muestre
variedad. Idempotente.

## 8. Pruebas

- Unitarias puras: `scoring.py` (bandas, N/A excluidos, 0 aplicables → `None`).
- Router con fakes: crear auditoría (respuestas incompletas 422; N/A sin razón 422; duplicado
  MRN 409; profesional de otro centro 422), editar solo en borrador (409 si aprobada), submit/
  approve con permisos, hallazgo obligatorio cuando corresponde, summary agrega solo no-borradores.
- Build TS sin errores; verificación UI con Playwright: crear ciclo, auditar 7 criterios con un
  N/A y un No, ver score/outcome en vivo, registrar hallazgo, tabla del ciclo, dashboard.

## 9. Fases (un commit por fase)

0. Migración 0007 + modelos + `scoring.py` + tests puros.
1. Servicio y API de auditorías, ciclos (año/trimestre) y summary + tests.
2. UI: ciclos (nuevo ciclo), página del ciclo, formulario de auditoría con barra en vivo.
3. UI + API: hallazgo y acción correctiva dentro de la auditoría.
4. Dashboard (`/ucca/dashboard`) + endpoint.
5. Seed demo, README, documento M04 en `docs/`, grafo.
