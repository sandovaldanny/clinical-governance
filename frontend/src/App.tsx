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
import { ChartAuditPage } from "./modules/ucca/ChartAuditPage";
import { UccaAnalyticsPage } from "./modules/ucca/UccaAnalyticsPage";
import { UccaCyclePage } from "./modules/ucca/UccaCyclePage";
import { UccaCyclesPage } from "./modules/ucca/UccaCyclesPage";

export function App() {
  const { session } = useAuth();

  if (!AUTH_DISABLED && !session) return <LoginPage />;

  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/admin/users" replace />} />
        <Route path="/ucca" element={<UccaCyclesPage />} />
        <Route path="/ucca/dashboard" element={<UccaAnalyticsPage />} />
        <Route path="/ucca/cycles/:cycleId" element={<UccaCyclePage />} />
        <Route path="/ucca/cycles/:cycleId/audits/new" element={<ChartAuditPage />} />
        <Route path="/ucca/audits/:auditId" element={<ChartAuditPage />} />
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
