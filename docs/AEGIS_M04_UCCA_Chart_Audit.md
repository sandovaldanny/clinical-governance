# AEGIS — M04 UCCA: Auditoría por expediente (chart audit)

## Objetivo

Permitir que el director médico (o auditor) evalúe un expediente clínico (MRN) de un profesional
respondiendo Yes / No / N/A a los 7 criterios universales de competencia clínica en una sola
pantalla, con score y outcome calculados al instante, hallazgo y acción correctiva registrados en el
mismo acto, y un dashboard consolidado por centro, profesional, criterio y trimestre. Reproduce la
hoja Excel "Universal Clinical Competency Audit" de referencia sin exigir la hoja de cálculo.

## Flujo del director médico

1. **Crear ciclo** (Gobierno clínico → UCCA → Nuevo ciclo): centro + año + trimestre. AEGIS sugiere el
   siguiente trimestre libre del centro; un ciclo es único por centro + año + trimestre.
2. **Nueva auditoría** desde la página del ciclo: seleccionar el profesional del centro (CG_ID y
   profesión se rellenan solos), indicar MRN / Case Ref y fecha.
3. **Responder los 7 criterios** CCA · CRS · CTP · COM · CDC · CEP · CMC (Yes / No / N/A; N/A exige
   razón). La barra inferior muestra aplicables, Yes, score y outcome en vivo.
4. **Hallazgo y acción correctiva**: si el outcome no es Compliant y hay al menos un No, el hallazgo
   principal es obligatorio; la acción correctiva (descripción, responsable, fecha límite, estado,
   evidencia de cierre) se guarda en M06 (`corrective_actions`).
5. **Guardar borrador → Enviar → Aprobar** (`ucca.create` / `ucca.approve`). Una auditoría aprobada es
   inmutable. El dashboard solo cuenta auditorías enviadas o aprobadas.

## Reglas de evaluación (fórmulas)

Implementadas en `backend/app/domains/governance/ucca/scoring.py` y replicadas en
`frontend/src/modules/ucca/scoring.ts`; visibles en la UI en el panel "Reglas de evaluación" del
formulario.

```
applicable = respuestas con outcome != not_applicable
yes        = respuestas con outcome == compliant
score      = None si applicable == 0, si no round(yes / applicable * 100, 2)
outcome    = None                        si score is None
             compliant                   si score >= 90
             minor_improvement           si score >= 80
             improvement_required        si score >= 70
             priority_corrective_action  en otro caso
```

Equivalencia con el Excel: `Score = IF(Applicable=0,"",YesCount/Applicable)` y
`Outcome = IF(Score="","",IF(Score>=90%,"Compliant",IF(Score>=80%,"Minor Improvement",
IF(Score>=70%,"Improvement Required","Priority Corrective Action"))))`.

Reglas adicionales:

- Cada N/A exige `not_applicable_reason` no vacío (regla global #5).
- Outcome ≠ Compliant con ≥ 1 No → hallazgo principal obligatorio (422 si falta).
- Todos los criterios activos de la plantilla deben responderse; criterio repetido o ajeno → 422.
- Expediente único por ciclo + profesional + MRN (409 si se repite).
- Auditoría aprobada: cualquier escritura → 409.
- Agregados (`summary.py`): solo `submitted`/`approved`; `draft_count` aparte. % por criterio =
  Yes ÷ (Yes + No), N/A excluidos. Score por profesional = media de sus expedientes; outcome del
  promedio con las mismas bandas. Tendencia = media por (año, trimestre).
- Orden de presentación de criterios: `CRITERIA_ORDER` (CCA, CRS, CTP, COM, CDC, CEP, CMC).

## Mapa Excel → AEGIS

| Columna Excel | AEGIS |
|---|---|
| Audit ID | `ucca_chart_audits.id` |
| Year / Quarter | `ucca_audit_cycles.year` / `quarter` (`period_label` = "Q2-2026") |
| CG_ID | `professionals.employee_number` |
| Practitioner / Profession | `professionals.full_name` / `professions.name` |
| Center | centro del ciclo (`ucca_audit_cycles.facility_id`) |
| MRN / Case Ref | `ucca_chart_audits.case_reference` |
| Audit Date | `ucca_chart_audits.audit_date` |
| Auditor | `ucca_chart_audits.auditor_user_id` |
| CCA … CMC | `ucca_audit_results.outcome` (una fila por criterio, `chart_audit_id`) |
| Applicable / Yes Count / Score / Outcome | `applicable_count` / `yes_count` / `score` / `outcome` (calculados en cada guardado) |
| Key Finding | `ucca_findings.description` (`chart_audit_id`) |
| Corrective Action / Owner / Due Date / Status / Closure Evidence | `corrective_actions.description` / `responsible_user_id` / `due_date` / `status` / `closure_evidence` |

## API

| Método y ruta | Permiso | Uso |
|---|---|---|
| `GET /ucca/cycles` · `POST /ucca/cycles` | `ucca.view` · `ucca.create` | Listar / crear ciclo (`{facility_id, year, quarter}`) |
| `GET /ucca/cycles/{id}/audits` | `ucca.view` | Filas tipo Excel del ciclo |
| `POST /ucca/cycles/{id}/audits` | `ucca.create` | Crear auditoría (cabecera + 7 respuestas + hallazgo opcional) |
| `GET /ucca/audits/{id}` · `PATCH /ucca/audits/{id}` | `ucca.view` · `ucca.create` | Detalle / editar borrador |
| `POST /ucca/audits/{id}/submit` · `POST …/approve` | `ucca.create` · `ucca.approve` | Transiciones draft → submitted → approved |
| `GET /ucca/cycles/{id}/summary` | `ucca.view` | Agregados del ciclo |
| `GET /ucca/dashboard?facility_id&year&quarter` | `ucca.view` | Agregados multi-ciclo |

## Estado de implementación

| Elemento | Estado |
|---|---|
| Modelo (`0007_ucca_chart_audits`), RLS por centro | ✅ |
| Score/outcome puro + tests (`test_ucca_scoring.py`) | ✅ |
| API auditorías, ciclos, summary, dashboard + tests | ✅ |
| UI: ciclos, página del ciclo, formulario, dashboard, panel de reglas | ✅ |
| Seed demo (Q2-2026, 6 expedientes, 1 hallazgo + acción) | ✅ |
| Capa OMH / JAWDA (indicadores regulatorios) | ⏳ pendiente |
| Exportación a Excel | ⏳ pendiente |
| Umbrales de outcome configurables por catálogo | ⏳ pendiente (constante `OUTCOME_BANDS`) |
