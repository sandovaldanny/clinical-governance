"""
Middleware/dependencia de autorización centralizada (sección 6.2 de la arquitectura técnica).

Regla de diseño: NINGÚN módulo decide por sí mismo si un usuario puede hacer algo. Todo router
declara el permiso que necesita con `require_permission("modulo.accion")`, y este archivo es el
ÚNICO lugar donde se resuelven roles -> permisos. El rol System Administrator no es un bypass de
código: es un rol al que, por configuración (seed/migración), se le otorgan todos los permisos —
así sus acciones también generan audit trail y respetan las mismas reglas de inmutabilidad.
"""
from fastapi import Depends, HTTPException, status

from app.core.config import get_settings
from app.core.deps import CurrentUser, get_current_user


def require_permission(permission_code: str):
    """
    permission_code sigue la convención "<modulo>.<accion>", ej. "ucca.approve",
    "corrective_actions.create", "users.manage_roles".
    """

    def dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if get_settings().auth_disabled:
            return current_user
        if permission_code not in current_user.effective_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"El usuario no tiene el permiso requerido: {permission_code}",
            )
        return current_user

    return dependency


def require_facility_access(facility_id: str, current_user: CurrentUser) -> None:
    """Chequeo defensivo a nivel de aplicación; la RLS de base de datos es la barrera real,
    pero fallar rápido aquí evita queries innecesarias y da mejores mensajes de error."""
    if current_user.is_corporate:
        return
    if facility_id not in current_user.facility_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene acceso a este centro.",
        )
