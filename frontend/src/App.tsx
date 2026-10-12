import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "./layout/AppShell";
import { LoginPage } from "./auth/LoginPage";
import { useAuth } from "./auth/AuthContext";
import { AUTH_DISABLED } from "./api/client";
import { CriteriaPage } from "./modules/admin/CriteriaPage";
import { AegisPage } from "./modules/aegis/AegisPage";
import { FacilitiesPage } from "./modules/admin/FacilitiesPage";
import { PositionsPage } from "./modules/admin/PositionsPage";
import { ProfessionsPage } from "./modules/admin/ProfessionsPage";
import { RolesPage } from "./modules/admin/RolesPage";
import { SpecialtiesPage } from "./modules/admin/SpecialtiesPage";
import { UsersPage } from "./modules/admin/UsersPage";
import { IndicatorsPage } from "./modules/indicators/IndicatorsPage";
import { UccaDashboard } from "./modules/ucca/UccaDashboard";
import { UccaEvaluatePage } from "./modules/ucca/UccaEvaluatePage";

export function App() {
  const { session } = useAuth();

  if (!AUTH_DISABLED && !session) return <LoginPage />;

  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/admin/users" replace />} />
        <Route path="/ucca" element={<UccaDashboard />} />
        <Route path="/ucca/cycles/:cycleId/evaluate" element={<UccaEvaluatePage />} />
        <Route path="/indicators" element={<IndicatorsPage />} />
        <Route path="/aegis" element={<AegisPage />} />
        <Route path="/admin/users" element={<UsersPage />} />
        <Route path="/admin/positions" element={<PositionsPage />} />
        <Route path="/admin/facilities" element={<FacilitiesPage />} />
        <Route path="/admin/professions" element={<ProfessionsPage />} />
        <Route path="/admin/specialties" element={<SpecialtiesPage />} />
        <Route path="/admin/criteria" element={<CriteriaPage />} />
        <Route path="/admin/roles" element={<RolesPage />} />
      </Route>
    </Routes>
  );
}
