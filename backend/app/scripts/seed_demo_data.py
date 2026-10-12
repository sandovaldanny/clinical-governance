"""
Seed de demostración: datos maestros M01/M02, roles, usuarios, catálogos e indicadores
UCCA/JAWDA/OMH001 para pruebas locales.

Uso:
  python -m app.scripts.seed_demo_data

Idempotente: puede ejecutarse varias veces sin duplicar registros clave.
"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.domains.governance.corrective_actions.models import CorrectiveAction
from app.domains.governance.ucca.models import (
    AuditCriterion,
    AuditCycle,
    AuditResult,
    AuditTemplate,
    AuditTemplateVersion,
    ChartAudit,
    Finding,
)
from app.domains.governance.ucca.scoring import compute_score
from app.domains.identity.models import (
    AegisRole,
    CatalogValue,
    Facility,
    OrganizationalPosition,
    Permission,
    Profession,
    Professional,
    RolePermissionAssignment,
    User,
    UserFacilityAssignment,
    UserRoleAssignment,
)

DEMO_PASSWORD = "Demo123!Change"

FACILITIES = [
    {"name": "Al Bateen", "city": "Abu Dhabi", "country": "UAE"},
    {"name": "Al Falah", "city": "Abu Dhabi", "country": "UAE"},
]

PROFESSIONS = [
    "Physician",
    "Psychiatrist",
    "Psychologist",
    "Registered Nurse",
    "Clinical Pharmacist",
    "Social Worker",
    "Occupational Therapist",
    # Documento M01 (tabla Professions)
    "Psychiatry",
    "Psychology",
    "Occupational Therapy",
    "Speech & Language Therapy",
    "Nursing",
    "Administration",
]

ORGANIZATIONAL_POSITIONS = [
    "Medical Director",
    "Governance Lead",
    "Quality Manager",
    "Staff Clinician",
    "Chief Nursing Officer",
    "Clinical Auditor",
    # Documento M01 (tabla Organizational Positions)
    "Group Medical Director",
    "Clinical Director",
    "Consultant Psychiatrist",
    "Psychologist",
    "Occupational Therapist",
    "Speech & Language Therapist",
    "Administrator",
]

SPECIALTIES = [
    ("psychiatry", "Psychiatry"),
    ("general_practice", "General Practice"),
    ("clinical_psychology", "Clinical Psychology"),
    ("mental_health_nursing", "Mental Health Nursing"),
    ("clinical_pharmacy", "Clinical Pharmacy"),
]

ROLES = [
    ("system_administrator", "System Administrator", True),
    ("governance_lead", "Governance Lead", False),
    ("medical_director", "Medical Director", False),
    ("quality_manager", "Quality Manager", False),
    ("auditor", "Auditor", False),
    ("reviewer", "Reviewer", False),
    ("approver", "Approver", False),
    ("clinician", "Clinician", False),
    ("executive_viewer", "Executive Viewer", False),
]

PERMISSIONS = [
    ("users.manage", "Administrar usuarios y asignaciones"),
    ("users.view", "Consultar usuarios"),
    ("facilities.manage", "Administrar centros"),
    ("catalogs.manage", "Administrar catálogos"),
    ("ucca.create", "Crear y ejecutar auditorías UCCA"),
    ("ucca.approve", "Aprobar resultados UCCA"),
    ("ucca.view", "Consultar resultados UCCA"),
    ("medication.manage", "Gestionar monitoreo de medicación/JAWDA"),
    ("medication.view", "Consultar monitoreo de medicación"),
    ("corrective_actions.manage", "Gestionar acciones correctivas"),
    ("corrective_actions.view", "Consultar acciones correctivas"),
    ("reports.publish", "Publicar reportes"),
    ("reports.view", "Consultar reportes"),
    ("audit.read", "Consultar audit trail"),
    ("roles.manage", "Administrar roles y matriz de permisos"),
]

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "system_administrator": [p[0] for p in PERMISSIONS],
    "governance_lead": [
        "users.view",
        "ucca.create",
        "ucca.approve",
        "ucca.view",
        "medication.view",
        "corrective_actions.manage",
        "corrective_actions.view",
        "reports.publish",
        "reports.view",
        "audit.read",
    ],
    "medical_director": [
        "users.view",
        "ucca.create",
        "ucca.approve",
        "ucca.view",
        "medication.manage",
        "medication.view",
        "corrective_actions.manage",
        "corrective_actions.view",
        "reports.view",
    ],
    "quality_manager": [
        "users.view",
        "ucca.create",
        "ucca.approve",
        "ucca.view",
        "medication.view",
        "corrective_actions.manage",
        "corrective_actions.view",
        "reports.view",
        "audit.read",
    ],
    "auditor": ["users.view", "ucca.create", "ucca.view", "medication.view", "corrective_actions.view"],
    "reviewer": ["ucca.view", "corrective_actions.view", "reports.view"],
    "approver": ["ucca.approve", "corrective_actions.manage", "reports.publish"],
    "clinician": ["ucca.view", "corrective_actions.view"],
    "executive_viewer": ["ucca.view", "medication.view", "corrective_actions.view", "reports.view"],
}

CATALOG_ENTRIES: list[tuple[str, str, str]] = [
    # country / city (M01 doc: dropdowns en Facilities)
    ("country", "UAE", "United Arab Emirates"),
    ("city", "abu_dhabi", "Abu Dhabi"),
    ("city", "dubai", "Dubai"),
    # severity
    ("severity", "standard", "Estándar"),
    ("severity", "major", "Mayor"),
    ("severity", "critical", "Crítico"),
    # audit outcomes
    ("audit_outcome", "compliant", "Cumple"),
    ("audit_outcome", "non_compliant", "No cumple"),
    ("audit_outcome", "not_applicable", "No aplica"),
    # medication classes (M05)
    ("medication_class", "antipsychotic_omh001", "Antipsicótico calificador OMH001"),
    ("medication_class", "stimulant_adhd", "Estimulante / ADHD"),
    ("medication_class", "lithium", "Litio"),
    ("medication_class", "valproate", "Valproato"),
    ("medication_class", "carbamazepine", "Carbamazepina"),
    ("medication_class", "clozapine", "Clozapina"),
    ("medication_class", "antidepressant", "Antidepresivo"),
    ("medication_class", "other_psychotropic", "Otro psicotrópico"),
    # OMH001 investigations (M05 — 10 investigaciones)
    ("omh001_investigation", "ecg", "ECG"),
    ("omh001_investigation", "full_blood_count", "Full Blood Count"),
    ("omh001_investigation", "hba1c", "HbA1c"),
    ("omh001_investigation", "lipid_profile", "Lipid Profile"),
    ("omh001_investigation", "alt", "ALT"),
    ("omh001_investigation", "ast", "AST"),
    ("omh001_investigation", "urea", "Urea"),
    ("omh001_investigation", "sodium", "Sodium"),
    ("omh001_investigation", "potassium", "Potassium"),
    ("omh001_investigation", "creatinine", "Creatinine"),
    # qualifying antipsychotics (ejemplo — pendiente lista oficial)
    ("qualifying_antipsychotic", "risperidone", "Risperidone"),
    ("qualifying_antipsychotic", "olanzapine", "Olanzapine"),
    ("qualifying_antipsychotic", "quetiapine", "Quetiapine"),
    ("qualifying_antipsychotic", "clozapine", "Clozapine"),
    # psychometric scales
    ("psychometric_scale", "phq9", "PHQ-9"),
    ("psychometric_scale", "gad7", "GAD-7"),
    # corrective action / finding status
    ("corrective_action_status", "assigned", "Asignada"),
    ("corrective_action_status", "in_progress", "En progreso"),
    ("corrective_action_status", "closed", "Cerrada"),
    ("finding_status", "open", "Abierto"),
    ("finding_status", "closed", "Cerrado"),
]

# Criterios de evaluación (Código, Dominio, Pregunta universal, Interpretación por profesión,
# Ejemplos/Evidencia). Texto fuente en inglés tal como lo define el equipo clínico de Alkalma.
UCCA_CRITERIA = [
    (
        "CCA",
        "Clinical Assessment",
        "Was an appropriate assessment completed and documented according to scope?",
        "Psychiatric history, MSE, diagnosis/formulation and differential where relevant.",
        "Psychiatric history, MSE, diagnosis/formulation and differential where relevant.",
    ),
    (
        "CRS",
        "Clinical Risk & Safety",
        "Were relevant clinical, safeguarding and treatment risks identified and documented?",
        "Suicide, violence, safeguarding, capacity and medication risks; safety plan/escalation when indicated.",
        "Suicide, violence, safeguarding, capacity and medication risks; safety plan/escalation when indicated.",
    ),
    (
        "CTP",
        "Clinical Treatment Planning",
        "Was an evidence-based intervention or management plan selected and documented?",
        "Medication rationale, psychoeducation, psychotherapy/referral, investigations and follow-up aligned with diagnosis.",
        "Medication rationale, psychoeducation, psychotherapy/referral, investigations and follow-up aligned with diagnosis.",
    ),
    (
        "COM",
        "Clinical Outcome Monitoring",
        "Was response and safety monitoring completed and the plan adjusted when indicated?",
        "Response, adherence, side effects, physical monitoring and relevant outcome measures reviewed.",
        "Response, adherence, side effects, physical monitoring and relevant outcome measures reviewed.",
    ),
    (
        "CDC",
        "Clinical Documentation & Compliance",
        "Was the record complete, accurate, timely and compliant?",
        "History, MSE, risk, diagnosis code, medication dose, consent and follow-up plan complete and timely.",
        "History, MSE, risk, diagnosis code, medication dose, consent and follow-up plan complete and timely.",
    ),
    (
        "CEP",
        "Clinical Ethics & Professionalism",
        "Were consent, confidentiality, boundaries and professional standards maintained?",
        "Shared decision-making, confidentiality, capacity, boundaries and ethical prescribing maintained.",
        "Shared decision-making, confidentiality, capacity, boundaries and ethical prescribing maintained.",
    ),
    (
        "CMC",
        "Clinical Communication & MDT",
        "Was communication with patient, family and MDT appropriate and documented?",
        "Patient/family education, consented involvement, referrals, handover and MDT communication documented.",
        "Patient/family education, consented involvement, referrals, handover and MDT communication documented.",
    ),
]

DEMO_USERS = [
    {
        "email": "admin@alkalma.health",
        "full_name": "System Administrator",
        "employee_number": "EMP-001",
        "role_code": "system_administrator",
        "facility_names": ["Al Bateen", "Al Falah"],
        "corporate": True,
        "profession": None,
        "position": None,
        "use_settings_password": True,
    },
    {
        "email": "governance.lead@alkalma.health",
        "full_name": "Sara Al Mansoori",
        "employee_number": "EMP-010",
        "role_code": "governance_lead",
        "facility_names": ["Al Bateen", "Al Falah"],
        "corporate": True,
        "profession": None,
        "position": "Governance Lead",
    },
    {
        "email": "md.bateen@alkalma.health",
        "full_name": "Dr. Ahmed Al Bateen",
        "employee_number": "EMP-020",
        "role_code": "medical_director",
        "facility_names": ["Al Bateen"],
        "corporate": False,
        "profession": "Psychiatrist",
        "position": "Medical Director",
        "specialty": "Psychiatry",
    },
    {
        "email": "md.falah@alkalma.health",
        "full_name": "Dr. Fatima Al Falah",
        "employee_number": "EMP-021",
        "role_code": "medical_director",
        "facility_names": ["Al Falah"],
        "corporate": False,
        "profession": "Psychiatrist",
        "position": "Medical Director",
        "specialty": "Psychiatry",
    },
    {
        "email": "quality@alkalma.health",
        "full_name": "Layla Quality Manager",
        "employee_number": "EMP-030",
        "role_code": "quality_manager",
        "facility_names": ["Al Bateen", "Al Falah"],
        "corporate": True,
        "profession": None,
        "position": "Quality Manager",
    },
    {
        "email": "auditor@alkalma.health",
        "full_name": "Omar Clinical Auditor",
        "employee_number": "EMP-040",
        "role_code": "auditor",
        "facility_names": ["Al Bateen"],
        "corporate": False,
        "profession": None,
        "position": "Clinical Auditor",
    },
    {
        "email": "clinician@alkalma.health",
        "full_name": "Dr. Noor Clinician",
        "employee_number": "EMP-050",
        "role_code": "clinician",
        "facility_names": ["Al Bateen"],
        "corporate": False,
        "profession": "Physician",
        "position": "Staff Clinician",
        "specialty": "General Practice",
        "create_professional": True,
    },
]

DEMO_PROFESSIONALS = [
    {
        "employee_number": "PRO-100",
        "full_name": "Dr. Noor Clinician",
        "profession": "Physician",
        "specialty": "General Practice",
        "facility": "Al Bateen",
        "scope": ["adult_mental_health"],
        "user_email": "clinician@alkalma.health",
    },
    {
        "employee_number": "PRO-101",
        "full_name": "Dr. Ahmed Al Bateen",
        "profession": "Psychiatrist",
        "specialty": "Psychiatry",
        "facility": "Al Bateen",
        "scope": ["psychiatry", "omh001_monitoring"],
        "user_email": "md.bateen@alkalma.health",
    },
    {
        "employee_number": "PRO-102",
        "full_name": "Nurse Maryam Hassan",
        "profession": "Registered Nurse",
        "specialty": "Mental Health Nursing",
        "facility": "Al Falah",
        "scope": ["mental_health_nursing"],
        "user_email": None,
    },
]


def _get_or_create_facility(db: Session, name: str, city: str, country: str) -> Facility:
    row = db.scalar(select(Facility).where(Facility.name == name))
    if row:
        return row
    row = Facility(name=name, city=city, country=country, is_active=True)
    db.add(row)
    db.flush()
    return row


def _get_or_create_profession(db: Session, name: str) -> Profession:
    row = db.scalar(select(Profession).where(Profession.name == name))
    if row:
        return row
    row = Profession(name=name, is_active=True)
    db.add(row)
    db.flush()
    return row


def _get_or_create_position(db: Session, title: str) -> OrganizationalPosition:
    row = db.scalar(select(OrganizationalPosition).where(OrganizationalPosition.title == title))
    if row:
        return row
    row = OrganizationalPosition(title=title, is_active=True)
    db.add(row)
    db.flush()
    return row


def _get_or_create_role(db: Session, code: str, name: str, is_system: bool) -> AegisRole:
    row = db.scalar(select(AegisRole).where(AegisRole.code == code))
    if row:
        return row
    row = AegisRole(code=code, name=name, is_system_defined=is_system)
    db.add(row)
    db.flush()
    return row


def _get_or_create_permission(db: Session, code: str, description: str) -> Permission:
    row = db.scalar(select(Permission).where(Permission.code == code))
    if row:
        return row
    row = Permission(code=code, module=code.split(".")[0], name=code, description=description)
    db.add(row)
    db.flush()
    return row


def _ensure_role_permission(db: Session, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
    exists = db.scalar(
        select(RolePermissionAssignment).where(
            RolePermissionAssignment.role_id == role_id,
            RolePermissionAssignment.permission_id == permission_id,
        )
    )
    if not exists:
        db.add(RolePermissionAssignment(role_id=role_id, permission_id=permission_id))


def _get_or_create_catalog(
    db: Session, catalog_type: str, code: str, label: str
) -> CatalogValue:
    row = db.scalar(
        select(CatalogValue).where(
            CatalogValue.catalog_type == catalog_type, CatalogValue.code == code
        )
    )
    if row:
        return row
    row = CatalogValue(catalog_type=catalog_type, code=code, label=label, is_active=True)
    db.add(row)
    db.flush()
    return row


def _get_or_create_user(
    db: Session,
    *,
    email: str,
    full_name: str,
    employee_number: str | None,
    password: str,
    profession_id: uuid.UUID | None,
    position_id: uuid.UUID | None,
    must_change_password: bool = False,
) -> User:
    row = db.scalar(select(User).where(User.email == email))
    if row:
        return row
    row = User(
        email=email,
        full_name=full_name,
        employee_number=employee_number,
        hashed_password=hash_password(password),
        profession_id=profession_id,
        organizational_position_id=position_id,
        must_change_password=must_change_password,
        is_active=True,
    )
    db.add(row)
    db.flush()
    return row


def _ensure_user_facility(
    db: Session, user_id: uuid.UUID, facility_id: uuid.UUID, corporate: bool
) -> None:
    exists = db.scalar(
        select(UserFacilityAssignment).where(
            UserFacilityAssignment.user_id == user_id,
            UserFacilityAssignment.facility_id == facility_id,
        )
    )
    if not exists:
        db.add(
            UserFacilityAssignment(
                user_id=user_id, facility_id=facility_id, is_corporate_scope=corporate
            )
        )


def _ensure_user_role(db: Session, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
    exists = db.scalar(
        select(UserRoleAssignment).where(
            UserRoleAssignment.user_id == user_id, UserRoleAssignment.role_id == role_id
        )
    )
    if not exists:
        db.add(UserRoleAssignment(user_id=user_id, role_id=role_id))


def _seed_master_data(db: Session) -> dict[str, Facility]:
    facilities: dict[str, Facility] = {}
    for f in FACILITIES:
        facilities[f["name"]] = _get_or_create_facility(db, **f)

    for name in PROFESSIONS:
        _get_or_create_profession(db, name)

    for title in ORGANIZATIONAL_POSITIONS:
        _get_or_create_position(db, title)

    for code, label in SPECIALTIES:
        _get_or_create_catalog(db, "specialty", code, label)

    roles: dict[str, AegisRole] = {}
    for code, name, is_system in ROLES:
        roles[code] = _get_or_create_role(db, code, name, is_system)

    permissions: dict[str, Permission] = {}
    for code, description in PERMISSIONS:
        permissions[code] = _get_or_create_permission(db, code, description)

    for role_code, perm_codes in ROLE_PERMISSIONS.items():
        role = roles[role_code]
        for perm_code in perm_codes:
            _ensure_role_permission(db, role.id, permissions[perm_code].id)

    for catalog_type, code, label in CATALOG_ENTRIES:
        _get_or_create_catalog(db, catalog_type, code, label)

    return facilities


def _seed_users(db: Session, facilities: dict[str, Facility], settings) -> dict[str, User]:
    roles = {r.code: r for r in db.scalars(select(AegisRole)).all()}
    users: dict[str, User] = {}

    for spec in DEMO_USERS:
        profession_id = None
        if spec.get("profession"):
            profession_id = db.scalar(
                select(Profession.id).where(Profession.name == spec["profession"])
            )
        position_id = None
        if spec.get("position"):
            position_id = db.scalar(
                select(OrganizationalPosition.id).where(
                    OrganizationalPosition.title == spec["position"]
                )
            )

        password = (
            settings.seed_admin_temp_password
            if spec.get("use_settings_password")
            else DEMO_PASSWORD
        )
        must_change = bool(spec.get("use_settings_password"))

        user = _get_or_create_user(
            db,
            email=spec["email"],
            full_name=spec["full_name"],
            employee_number=spec["employee_number"],
            password=password,
            profession_id=profession_id,
            position_id=position_id,
            must_change_password=must_change,
        )
        users[spec["email"]] = user

        for facility_name in spec["facility_names"]:
            _ensure_user_facility(
                db, user.id, facilities[facility_name].id, spec.get("corporate", False)
            )
        _ensure_user_role(db, user.id, roles[spec["role_code"]].id)

    return users


def _seed_professionals(db: Session, facilities: dict[str, Facility], users: dict[str, User]) -> None:
    for spec in DEMO_PROFESSIONALS:
        exists = db.scalar(
            select(Professional).where(Professional.employee_number == spec["employee_number"])
        )
        if exists:
            continue
        profession_id = db.scalar(
            select(Profession.id).where(Profession.name == spec["profession"])
        )
        user_id = users[spec["user_email"]].id if spec.get("user_email") else None
        db.add(
            Professional(
                employee_number=spec["employee_number"],
                full_name=spec["full_name"],
                profession_id=profession_id,
                specialty=spec.get("specialty"),
                primary_facility_id=facilities[spec["facility"]].id,
                scope_of_practice=spec.get("scope", []),
                user_id=user_id,
                is_active=True,
            )
        )


def _seed_ucca_template(db: Session) -> AuditTemplateVersion:
    template = db.scalar(
        select(AuditTemplate).where(AuditTemplate.name == "UCCA — Gobierno Clínico Alkalma")
    )
    if not template:
        template = AuditTemplate(name="UCCA — Gobierno Clínico Alkalma", is_active=True)
        db.add(template)
        db.flush()

    version = db.scalar(
        select(AuditTemplateVersion).where(
            AuditTemplateVersion.template_id == template.id,
            AuditTemplateVersion.version_number == 1,
        )
    )
    if not version:
        version = AuditTemplateVersion(
            template_id=template.id, version_number=1, is_current=True
        )
        db.add(version)
        db.flush()

    for code, domain, question, interpretation, evidence in UCCA_CRITERIA:
        exists = db.scalar(
            select(AuditCriterion).where(
                AuditCriterion.template_version_id == version.id,
                AuditCriterion.code == code,
            )
        )
        if not exists:
            db.add(
                AuditCriterion(
                    template_version_id=version.id,
                    code=code,
                    domain=domain,
                    universal_question=question,
                    profession_interpretation=interpretation,
                    examples_evidence=evidence,
                    is_active=True,
                )
            )

    return version


# (MRN, respuestas por código en orden CCA,CRS,CTP,COM,CDC,CEP,CMC) — como la hoja Excel UCCA de
# referencia: 5 expedientes Compliant y uno con 2 "No" + 1 "N/A" que genera hallazgo y acción.
DEMO_CHART_AUDITS = [
    ("102453", ["compliant"] * 7),
    ("100598", ["compliant"] * 7),
    ("AKAD00132", ["compliant"] * 7),
    ("AKAD00264", ["compliant"] * 7),
    ("101460", ["compliant"] * 7),
    ("103877", ["compliant", "non_compliant", "compliant", "not_applicable", "compliant", "compliant", "non_compliant"]),
]
CRITERIA_CODES = ["CCA", "CRS", "CTP", "COM", "CDC", "CEP", "CMC"]


def _get_or_create_cycle(db: Session, facility: Facility, template_version: AuditTemplateVersion, year: int, quarter: str,
                         created_by: User) -> AuditCycle:
    cycle = db.scalar(
        select(AuditCycle).where(AuditCycle.facility_id == facility.id, AuditCycle.year == year, AuditCycle.quarter == quarter)
    )
    if cycle:
        return cycle
    cycle = AuditCycle(facility_id=facility.id, template_version_id=template_version.id, period_label=f"{quarter}-{year}",
                       year=year, quarter=quarter, status="draft", created_by_user_id=created_by.id)
    db.add(cycle)
    db.flush()
    return cycle


def _seed_sample_cycle(
    db: Session,
    facilities: dict[str, Facility],
    users: dict[str, User],
    template_version: AuditTemplateVersion,
) -> None:
    """Ciclo Q2-2026 (Al Bateen) con 6 expedientes auditados y aprobados del Dr. Ahmed Al Bateen
    (PRO-101), más el ciclo Q3-2026 vacío. Idempotente: no duplica ciclos ni expedientes."""
    admin = users["admin@alkalma.health"]
    auditor = users["governance.lead@alkalma.health"]
    facility = facilities["Al Bateen"]
    _get_or_create_cycle(db, facility, template_version, 2026, "Q3", admin)
    cycle = _get_or_create_cycle(db, facility, template_version, 2026, "Q2", auditor)

    professional = db.scalar(select(Professional).where(Professional.employee_number == "PRO-101"))
    criteria = {
        c.code: c
        for c in db.scalars(select(AuditCriterion).where(AuditCriterion.template_version_id == template_version.id)).all()
    }
    if not professional or any(code not in criteria for code in CRITERIA_CODES):
        return
    for case_ref, outcomes in DEMO_CHART_AUDITS:
        exists = db.scalar(
            select(ChartAudit).where(
                ChartAudit.cycle_id == cycle.id,
                ChartAudit.professional_id == professional.id,
                ChartAudit.case_reference == case_ref,
            )
        )
        if exists:
            continue
        score = compute_score(outcomes)
        audit = ChartAudit(
            cycle_id=cycle.id, facility_id=facility.id, professional_id=professional.id, auditor_user_id=auditor.id,
            case_reference=case_ref, audit_date=date(2026, 7, 20), status="approved",
            applicable_count=score.applicable_count, yes_count=score.yes_count, score=score.score,
            outcome=score.outcome, notes="",
        )
        db.add(audit)
        db.flush()
        for code, outcome in zip(CRITERIA_CODES, outcomes):
            db.add(
                AuditResult(
                    chart_audit_id=audit.id, facility_id=facility.id, cycle_id=cycle.id, criterion_id=criteria[code].id,
                    professional_id=professional.id, auditor_user_id=auditor.id, outcome=outcome,
                    not_applicable_reason="Outcome monitoring not yet due at audit date" if outcome == "not_applicable" else None,
                    status="approved",
                )
            )
        if score.outcome not in (None, "compliant"):
            finding = Finding(
                facility_id=facility.id, chart_audit_id=audit.id,
                description="Risk documentation and MDT communication incomplete in the audited chart.", status="open",
            )
            db.add(finding)
            db.flush()
            db.add(
                CorrectiveAction(
                    facility_id=facility.id, source_module="ucca", source_finding_id=finding.id,
                    responsible_user_id=users["md.bateen@alkalma.health"].id, due_date=date(2026, 8, 30),
                    status="assigned",
                    description="Refresher on risk assessment documentation; audit 5 further charts in Q3.",
                )
            )


def run() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        print("Sembrando datos maestros (centros, profesiones, roles, catálogos)...")
        facilities = _seed_master_data(db)

        print("Sembrando usuarios de demostración...")
        users = _seed_users(db, facilities, settings)

        print("Sembrando profesionales clínicos...")
        _seed_professionals(db, facilities, users)

        print("Sembrando plantilla UCCA e indicadores (JAWDA/OMH001)...")
        template_version = _seed_ucca_template(db)

        print("Sembrando ciclos UCCA de ejemplo (Q2-2026 con 6 expedientes, Q3-2026 vacío)...")
        _seed_sample_cycle(db, facilities, users, template_version)

        db.commit()

        criteria_count = len(
            db.scalars(
                select(AuditCriterion).where(
                    AuditCriterion.template_version_id == template_version.id
                )
            ).all()
        )
        catalog_count = len(db.scalars(select(CatalogValue)).all())

        print("\nSeed completado.")
        print(f"  Centros: {len(facilities)}")
        print(f"  Usuarios demo: {len(DEMO_USERS)}")
        print(f"  Profesionales: {len(DEMO_PROFESSIONALS)}")
        print(f"  Criterios de evaluación: {criteria_count}")
        print(f"  Auditorías de expediente demo: {db.scalar(select(func.count(ChartAudit.id)))}")
        print(f"  Valores de catálogo: {catalog_count}")
        print("\nCredenciales demo (excepto admin):")
        print(f"  Contraseña: {DEMO_PASSWORD}")
        print(f"  Admin: {settings.seed_admin_email} / {settings.seed_admin_temp_password}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
