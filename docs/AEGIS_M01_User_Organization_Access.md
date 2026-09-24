# AEGIS Phase 1 — Module 1: User, Organization & Access Management

**Version:** 1.0 (Development Draft) · Recibido del negocio el 2026-09-24. Fuente de la implementación del módulo administrativo (`backend/app/domains/identity`, `frontend/src/modules/admin`).

## 1. Purpose

This module is responsible for controlling access to AEGIS and ensuring that every action performed within the platform can be linked to an authorized user. It provides the foundation for security, accountability, governance, and audit traceability. The objective is not simply to create usernames and passwords, but to ensure that every user only has access to the information and functions appropriate to their responsibilities within the organization. This module also establishes the organizational structure upon which the rest of AEGIS is built.

## 2. Business Process

Create User → Assign Organizational Position → Assign Facility → Assign Profession → Assign AEGIS Role(s) → Activate Account → User accesses AEGIS. Every action performed afterwards is linked to this account.

## 3. Database Tables

| # | Table | Purpose | Examples |
|---|---|---|---|
| 1 | Users | Personal identity of every system user | — |
| 2 | Organizational Positions | The user's organizational appointment | Group Medical Director, Clinical Director, Consultant Psychiatrist, Psychologist, Occupational Therapist, Speech & Language Therapist, Quality Manager, Administrator |
| 3 | Facilities | Every clinic within the organization | Al Bateen, Al Falah, Dubai |
| 4 | Professions | — | Psychiatry, Psychology, Occupational Therapy, Speech & Language Therapy, Nursing, Administration |
| 5 | AEGIS Roles | What the user is allowed to do; one person may have several | Governance Lead, Auditor, Reviewer, Approver, Clinician, Executive Viewer, System Administrator |
| 6 | Permissions | Every permission available inside AEGIS | View Audit, Create Audit, Edit Audit, Approve Audit, Publish Report, Manage Users, Export Data, View Dashboard |
| 7 | User Role Assignment | Links Users to one or more AEGIS Roles | — |
| 8 | Role Permission Assignment | Links Roles to Permissions; changing one role updates permissions for everyone assigned | — |
| 9 | Login History | Every login | — |
| 10 | Activity Log | Every action performed within AEGIS | — |

## 4. Field Definitions

**Users:** User ID (auto, PK) · Employee Number (text, required, links to HR) · First Name · Last Name · Full Name (calculated) · Email (unique) · Mobile (optional) · Username · Password (encrypted, system managed) · Status (Active / Inactive / Suspended) · Created Date · Created By · Last Login.

**Organizational Position:** Position ID · Position Name · Description · Active (Yes/No).

**Facilities:** Facility ID · Facility Name · Country (dropdown) · City (dropdown) · Clinical Director (user lookup) · Status (Active / Closed).

**Professions:** Profession ID · Profession Name · Active.

**AEGIS Roles:** Role ID · Role Name · Description · Active.

**Permissions:** Permission ID · Permission Name · Module · Description.

## 5. Relationships

User belongs to Facility, belongs to Profession, has Organizational Position, has many AEGIS Roles, performs Activities. AEGIS Role contains many Permissions. One user may have several AEGIS Roles; one AEGIS Role may belong to many users. This structure allows the platform to grow without redesigning permissions.

## 6. Business Rules

- Every user must have a unique account.
- Every user must belong to at least one facility.
- Every clinical user must have an assigned profession.
- Every user must have at least one AEGIS Role.
- Permissions should always be assigned through roles rather than directly to users.
- Users may have multiple roles.
- Organizational Position should not determine permissions.
- Deactivated users should remain in the database to preserve historical records.
- No approved governance record should lose its author because a user leaves the organization.

## 7. Workflow

- **New user:** Administrator creates user → Assign Position → Facility → Profession → AEGIS Roles → Activate → First Login → User begins work.
- **Change position:** position changes, user keeps the same account, permissions unchanged unless roles change.
- **Add responsibility:** e.g. Clinical Director becomes Auditor → only a new AEGIS Role is added.
- **Employee leaves:** deactivate account → retain history → transfer responsibilities → archive account.

## 8. System Calculations

Number of active users · Users by facility · Users by profession · Users by role · Last login · Inactive users · Failed login attempts · Multiple-role users.

## 9. Outputs

User Register · Role Register · Facility Register · Profession Register · Login History · Activity History · Permission Matrix · Security Reports. Every subsequent module references these master records rather than storing duplicate information.

## 10. Future Expansion

Additional countries, outpatient clinics, professions, positions and governance roles · SSO · MFA · HR integration · Active Directory / Microsoft Entra ID · Federated identity · External auditors with temporary access · AI-assisted governance functions requiring role-based permissions.

## Questions for the Development Team

1. Can users authenticate using the organization's existing Microsoft account or Active Directory?
2. Can permissions remain configurable through the database instead of being hard-coded?
3. Can a user hold multiple AEGIS roles simultaneously?
4. Can access be restricted by facility while still allowing Group Medical Directors to oversee all clinics?
5. Can all user activities be automatically captured in an immutable audit log?
6. Can role changes take effect immediately without affecting historical records?
7. Can temporary users (e.g., external auditors) be given access with automatic expiry?
8. Can the permission model support future modules without requiring redesign?

## Estado de implementación en el arquetipo (2026-09-24)

| Requisito | Estado | Dónde |
|---|---|---|
| Tablas 1–8 con los campos del §4 | ✅ | `backend/alembic/versions/0001`, `0005` |
| Flujo crear usuario (§2/§7) con contraseña gestionada por el sistema | ✅ | `POST /identity/users`, drawer en `frontend/src/modules/admin/UsersPage.tsx` |
| Estado Active / Inactive / Suspended; nunca borrar | ✅ | `PATCH /identity/users/{id}/status` |
| Reglas §6 (≥1 centro, ≥1 rol, clínico con profesión, permisos solo por rol) | ✅ | `identity/service.py::_validate_user_rules` |
| Cargos, Centros (director, país/ciudad), Profesiones, Especialidades: crear/editar/estado | ✅ | `MasterDataPage` + endpoints `POST/PATCH` |
| Matriz rol→permiso editable; cambio aplica a todos los usuarios del rol | ✅ | `PATCH /identity/roles/{id}` (`permission_ids`) |
| Login History (tabla 9) | ⚠️ tabla creada, sin registro en login ni UI | pendiente |
| Activity Log (tabla 10) | ✅ `audit_events` append-only | `core/audit.py` |
| Cálculos §8 y reportes §9 | ⏳ | siguiente iteración |
| Accesos temporales con expiración, SSO, MFA | ⏳ | roadmap |

Respuestas a las preguntas: 1 preparado (`auth_provider`/`external_id`), 2 sí (roles/permisos en BD, editables en UI), 3 sí, 4 sí (RLS por centro + alcance corporativo), 5 sí (`audit_events` con UPDATE/DELETE revocados), 6 sí (los permisos se resuelven al iniciar sesión; el histórico conserva autor), 7 pendiente, 8 sí (permisos `<módulo>.<acción>` sin cambios estructurales).
