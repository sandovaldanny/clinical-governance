/**
 * Guías → Clinical Governance Framework (Keralty × Alkalma, "Key Elements for Mental Health Centres
 * in the UAE — Horizon & BrightMinds"). Mapa de sus 13 dominios contra lo que AEGIS ya cubre, lo
 * que está planificado en el requerimiento funcional (M01–M19) y lo que no tiene dueño todavía.
 * Fuente: docs/Clinical Governance Framework.docx. Texto bilingüe: se elige por idioma de la UI.
 */

export type FrameworkStatus = "compliant" | "partial" | "planned" | "gap";

export type Bilingual = { es: string; en: string };

export type FrameworkRow = {
  section: number;
  title: Bilingual;
  status: FrameworkStatus;
  /** Dónde AEGIS ya lo aplica (módulos, pantallas, criterios). */
  applied: Bilingual;
  /** Qué falta para cubrir el dominio. */
  pending: Bilingual;
};

export const FRAMEWORK_SOURCE = {
  es: "Clinical Governance Framework — Keralty × Alkalma (Horizon & BrightMinds, EAU). Evaluación de línea base al 2026-10-14.",
  en: "Clinical Governance Framework — Keralty × Alkalma (Horizon & BrightMinds, UAE). Baseline assessment as of 2026-10-14.",
};

export const FRAMEWORK_ROWS: FrameworkRow[] = [
  {
    section: 1,
    title: { es: "Fundamentos regulatorios y de licenciamiento", en: "Regulatory & Licensing Foundations" },
    status: "planned",
    applied: {
      es: "Catálogos JAWDA / OMH001 (investigaciones y clases de medicación) en Indicadores a evaluar (M05).",
      en: "JAWDA / OMH001 catalogs (investigations and medication classes) in Indicators (M05).",
    },
    pending: {
      es: "Mapa de regulador por emirato (DHA / DoH / MOHAP), licencias profesionales y alcance de práctica (M14, Fase 3), reporte regulatorio obligatorio.",
      en: "Regulator map by emirate (DHA / DoH / MOHAP), professional licensing and scope of practice (M14, Phase 3), mandatory regulatory reporting.",
    },
  },
  {
    section: 2,
    title: { es: "Estructura de gobierno y rendición de cuentas", en: "Governance Structure & Accountability" },
    status: "partial",
    applied: {
      es: "Roles y matriz de permisos (M01), director clínico por centro (M02), alcance corporativo vs. centro.",
      en: "Roles and permission matrix (M01), clinical director per facility (M02), corporate vs. facility scope.",
    },
    pending: {
      es: "Comités (Gobierno Clínico, Incidentes/Mortalidad, MDT, Medicamentos, Quejas) con términos de referencia, cadencia, actas y acuerdos; RACI y esquema de delegación. Encaja en M03 (Fase 2).",
      en: "Committees (Clinical Governance, Serious Incident/Mortality, MDT, Medicines, Complaints) with terms of reference, cadence, minutes and actions; RACI and scheme of delegation. Fits M03 (Phase 2).",
    },
  },
  {
    section: 3,
    title: { es: "Alcance de servicios y vías clínicas", en: "Scope of Services & Clinical Pathways" },
    status: "planned",
    applied: {
      es: "Criterio CTP (planificación del tratamiento) de UCCA audita que el plan sea basado en evidencia.",
      en: "UCCA criterion CTP (treatment planning) audits that the plan is evidence-based.",
    },
    pending: {
      es: "Auditoría de adherencia a guías de práctica clínica (M07, Fase 2). La definición de vías y poblaciones es política, no software.",
      en: "Clinical practice guideline adherence audit (M07, Phase 2). Defining pathways and populations is policy, not software.",
    },
  },
  {
    section: 4,
    title: { es: "Riesgo clínico, seguridad del paciente y crisis", en: "Clinical Risk, Patient Safety & Crisis Management" },
    status: "gap",
    applied: {
      es: "Criterio CRS (riesgo y seguridad) de UCCA: suicidio, violencia, safeguarding, capacidad, plan de seguridad.",
      en: "UCCA criterion CRS (risk & safety): suicide, violence, safeguarding, capacity, safety plan.",
    },
    pending: {
      es: "Registro de riesgos clínicos con umbrales de escalamiento; incidentes con clasificación, RCA, cierre y notificación regulatoria (M15, hoy en Fase 4: subir de prioridad); protocolo de inasistencia de pacientes de alto riesgo.",
      en: "Clinical risk register with escalation thresholds; incidents with classification, RCA, closure and regulatory notification (M15, currently Phase 4: raise priority); missed-appointment protocol for high-risk patients.",
    },
  },
  {
    section: 5,
    title: { es: "Gobierno de medicación", en: "Medication Governance" },
    status: "partial",
    applied: {
      es: "Catálogos OMH001 y clases de medicación (M05); esqueleto del reporte semanal de antipsicóticos; criterio COM de UCCA revisa monitoreo físico y efectos adversos.",
      en: "OMH001 catalogs and medication classes (M05); weekly antipsychotic report skeleton; UCCA criterion COM reviews physical monitoring and side effects.",
    },
    pending: {
      es: "Auditoría periódica de prescripción, reconciliación en transiciones, polifarmacia / off-label, reporte de ADR y errores de medicación, privilegios de prescripción.",
      en: "Periodic prescribing audits, reconciliation at care transitions, polypharmacy / off-label oversight, ADR and medication-error reporting, prescribing privileges.",
    },
  },
  {
    section: 6,
    title: { es: "Consentimiento, capacidad y derechos del paciente", en: "Consent, Capacity & Patient Rights" },
    status: "gap",
    applied: {
      es: "Solo implícito en los criterios CRS (capacidad) y CEP (ética y profesionalismo) de UCCA.",
      en: "Only implicit in UCCA criteria CRS (capacity) and CEP (ethics & professionalism).",
    },
    pending: {
      es: "Criterio UCCA explícito de consentimiento informado / capacidad / asentimiento de menores (configurable hoy desde Administración → Criterios); vía de escalamiento ético.",
      en: "Explicit UCCA criterion for informed consent / capacity / minors' assent (configurable today from Administration → Criteria); ethics escalation pathway.",
    },
  },
  {
    section: 7,
    title: { es: "Safeguarding", en: "Safeguarding" },
    status: "gap",
    applied: {
      es: "Mencionado dentro del criterio CRS de UCCA.",
      en: "Mentioned within UCCA criterion CRS.",
    },
    pending: {
      es: "Líder de safeguarding por centro, reporte obligatorio y vías de escalamiento, protocolo y estándar de documentación para abuso / negligencia / violencia doméstica; criterio UCCA propio.",
      en: "Named safeguarding lead per facility, mandatory reporting and escalation pathways, protocol and documentation standard for abuse / neglect / domestic violence; dedicated UCCA criterion.",
    },
  },
  {
    section: 8,
    title: { es: "Fuerza laboral y gobierno del equipo multidisciplinario", en: "Workforce & Multidisciplinary Team Governance" },
    status: "partial",
    applied: {
      es: "UCCA como evaluación de competencia por profesional y ciclo (M04); criterio CMC audita comunicación y MDT; profesiones, especialidades y cargos (M02).",
      en: "UCCA as per-practitioner competency evaluation by cycle (M04); criterion CMC audits communication and MDT; professions, specialties and positions (M02).",
    },
    pending: {
      es: "Credentialing y privileging (M14), OPPE / FPPE (M11 / M12), peer review (M13), CME y supervisión (M17): Fase 3. Estructura, quórum y frecuencia del MDT.",
      en: "Credentialing and privileging (M14), OPPE / FPPE (M11 / M12), peer review (M13), CME and supervision (M17): Phase 3. MDT structure, quorum and frequency.",
    },
  },
  {
    section: 9,
    title: { es: "Documentación clínica", en: "Clinical Documentation" },
    status: "compliant",
    applied: {
      es: "Auditoría de expediente por ciclo trimestral (UCCA): 7 criterios, score, outcome, hallazgo; criterio CDC cubre documentación y cumplimiento.",
      en: "Chart audit per quarterly cycle (UCCA): 7 criteria, score, outcome, finding; criterion CDC covers documentation and compliance.",
    },
    pending: {
      es: "Plantillas estándar y tiempos de cierre de nota viven en el EMR, fuera de AEGIS.",
      en: "Standard templates and record-completion timelines live in the EMR, outside AEGIS.",
    },
  },
  {
    section: 10,
    title: { es: "Resultados, auditoría, quejas y experiencia del paciente", en: "Outcomes, Audit, Complaints & Patient Experience" },
    status: "partial",
    applied: {
      es: "Plan de auditoría por ciclos, hallazgo → acción correctiva con responsable y fecha (M06) → re-auditoría; dashboard UCCA por criterio y profesional (M08 inicial).",
      en: "Audit plan by cycles, finding → corrective action with owner and due date (M06) → re-audit; UCCA dashboard by criterion and practitioner (initial M08).",
    },
    pending: {
      es: "Gestión de quejas y retroalimentación (M16, Fase 4); resultados clínicos con PHQ-9 / GAD-7 y PROMs / PREMs; auditorías de medicación, safeguarding y adherencia a vías.",
      en: "Complaints and feedback management (M16, Phase 4); clinical outcomes with PHQ-9 / GAD-7 and PROMs / PREMs; medication, safeguarding and pathway-adherence audits.",
    },
  },
  {
    section: 11,
    title: { es: "Telesalud mental y gobierno de la información", en: "Tele-Mental Health & Information Governance" },
    status: "partial",
    applied: {
      es: "Acceso por rol (RBAC), segregación por centro con Row-Level Security, audit trail inmutable (M10), sesión con JWT.",
      en: "Role-based access (RBAC), facility segregation with Row-Level Security, immutable audit trail (M10), JWT session.",
    },
    pending: {
      es: "Criterios de elegibilidad y verificación de identidad para atención virtual, prescripción remota, retención de datos y gestión de brechas, gobierno de herramientas digitales / IA (M19).",
      en: "Eligibility and identity-verification criteria for virtual care, remote prescribing, data retention and breach management, governance of digital / AI tools (M19).",
    },
  },
  {
    section: 12,
    title: { es: "Políticas, KPIs y aseguramiento del gobierno", en: "Policies, KPIs & Governance Assurance" },
    status: "partial",
    applied: {
      es: "Action tracker de acciones correctivas (M06); dashboard de KPIs UCCA por centro y trimestre.",
      en: "Corrective-action tracker (M06); UCCA KPI dashboard by facility and quarter.",
    },
    pending: {
      es: "Registro maestro de políticas (dueño, aprobador, vigencia, revisión, mapeo regulatorio); registro de riesgos; set de KPIs de seguridad, medicación, safeguarding, quejas, resultados y acceso; cadencia mensual centro → comité.",
      en: "Master policy register (owner, approver, effective / review dates, regulatory mapping); risk register; KPI set for safety, medication, safeguarding, complaints, outcomes and access; monthly facility → committee cadence.",
    },
  },
  {
    section: 13,
    title: { es: "Enfoque de implementación sugerido", en: "Suggested Implementation Approach" },
    status: "partial",
    applied: {
      es: "Esta página es la evaluación de línea base que pide el documento: qué existe, qué fortalecer, qué construir.",
      en: "This page is the baseline assessment the document asks for: what exists, what to strengthen, what to build.",
    },
    pending: {
      es: "Convertirla en plan priorizado con responsables y fechas, empezando por las áreas de alto riesgo: suicidio / autolesión, safeguarding, emergencias, medicación, consentimiento, credenciales e incidentes.",
      en: "Turn it into a prioritised plan with owners and dates, starting with high-risk areas: suicide / self-harm, safeguarding, emergencies, medication, consent, credentialing and incidents.",
    },
  },
];

export const RECOMMENDATIONS: Bilingual[] = [
  {
    es: "Hoy, sin código: añadir criterios UCCA explícitos de consentimiento / capacidad, safeguarding y plan de seguridad ante riesgo suicida desde Administración → Criterios. Cierra §4, §6 y §7 a nivel de auditoría.",
    en: "Today, no code: add explicit UCCA criteria for consent / capacity, safeguarding and suicide-risk safety plan from Administration → Criteria. Closes §4, §6 and §7 at audit level.",
  },
  {
    es: "Reordenar fases: subir M15 Incidentes / RCA y M16 Quejas de Fase 4 a Fase 2; el framework los pone entre los primeros.",
    en: "Re-sequence phases: move M15 Incidents / RCA and M16 Complaints from Phase 4 to Phase 2; the framework ranks them among the first.",
  },
  {
    es: "Dos entidades nuevas no previstas en M01–M19: registro de riesgos clínicos (§4, §12) y registro maestro de políticas (§12). Encajan en M03.",
    en: "Two new entities not foreseen in M01–M19: clinical risk register (§4, §12) and master policy register (§12). They fit M03.",
  },
  {
    es: "Comités (§2): M03 debe modelar comité, términos de referencia, cadencia, actas y acuerdos ligados a acciones correctivas.",
    en: "Committees (§2): M03 should model committee, terms of reference, cadence, minutes and actions linked to corrective actions.",
  },
  {
    es: "KPI set (§12): alinear el dashboard M08 con las categorías del documento, no solo UCCA.",
    en: "KPI set (§12): align the M08 dashboard with the document's categories, not only UCCA.",
  },
];
