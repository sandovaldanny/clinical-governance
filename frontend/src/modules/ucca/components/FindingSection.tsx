import { useTranslation } from "react-i18next";

import { FormField } from "../../../components/FormField";
import { brandTokens } from "../../../theme/brand-tokens";
import type { ActionStatus } from "../types";

export type FindingState = {
  enabled: boolean; description: string; actionEnabled: boolean; actionDescription: string;
  ownerId: string; dueDate: string; actionStatus: ActionStatus; closureEvidence: string;
};

export const EMPTY_FINDING: FindingState = {
  enabled: false, description: "", actionEnabled: false, actionDescription: "", ownerId: "", dueDate: "",
  actionStatus: "assigned", closureEvidence: "",
};

type Owner = { id: string; full_name: string; status?: string };
const STATUSES: ActionStatus[] = ["assigned", "in_progress", "closed"];

/** Hallazgo principal (Key Finding) + acción correctiva (M06). Obligatorio cuando el outcome no es
 * Compliant y hay al menos un "No"; opcional en el resto de casos. */
export function FindingSection({ state, onChange, required, owners, readOnly }: {
  state: FindingState; onChange: (s: FindingState) => void; required: boolean; owners: Owner[]; readOnly: boolean;
}) {
  const { t } = useTranslation();
  const set = (patch: Partial<FindingState>) => onChange({ ...state, ...patch });
  return (
    <div data-testid="finding-section"
         style={{ background: brandTokens.colors.surface, border: `1px solid ${required ? brandTokens.colors.warning : brandTokens.colors.border}`,
                  borderRadius: brandTokens.radius.lg, padding: 20, marginTop: 24 }}>
      <h2 style={{ fontSize: 17, margin: "0 0 6px" }}>{t("ucca.form.findingSection")}</h2>
      <p style={{ fontSize: 13, color: required ? brandTokens.colors.textPrimary : brandTokens.colors.textSecondary, margin: "0 0 14px" }}>
        {required ? t("ucca.form.findingHint") : t("ucca.form.findingOptional")}
      </p>
      {!required && !readOnly && (
        <label style={{ fontSize: 13, display: "flex", gap: 8, alignItems: "center", marginBottom: 12 }}>
          <input type="checkbox" checked={state.enabled} onChange={(e) => set({ enabled: e.target.checked })} /> {t("ucca.form.keyFinding")}
        </label>
      )}
      {(required || state.enabled) && (
        <>
          <FormField label={t("ucca.form.keyFinding")} required>
            <textarea rows={2} value={state.description} disabled={readOnly} required onChange={(e) => set({ description: e.target.value })} />
          </FormField>
          <label style={{ fontSize: 13, display: "flex", gap: 8, alignItems: "center", marginBottom: 12 }}>
            <input type="checkbox" checked={state.actionEnabled} disabled={readOnly} onChange={(e) => set({ actionEnabled: e.target.checked })} /> {t("ucca.form.correctiveAction")}
          </label>
          {state.actionEnabled && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0 16px" }}>
              <div style={{ gridColumn: "1 / -1" }}>
                <FormField label={t("ucca.form.correctiveAction")} required>
                  <textarea rows={2} value={state.actionDescription} disabled={readOnly} required onChange={(e) => set({ actionDescription: e.target.value })} />
                </FormField>
              </div>
              <FormField label={t("ucca.form.owner")} required>
                <select value={state.ownerId} disabled={readOnly} required onChange={(e) => set({ ownerId: e.target.value })}>
                  <option value="">{t("ucca.form.ownerPlaceholder")}</option>
                  {owners.filter((o) => o.status === undefined || o.status === "active").map((o) => <option key={o.id} value={o.id}>{o.full_name}</option>)}
                </select>
              </FormField>
              <FormField label={t("ucca.form.dueDate")} required>
                <input type="date" value={state.dueDate} disabled={readOnly} required onChange={(e) => set({ dueDate: e.target.value })} />
              </FormField>
              <FormField label={t("ucca.form.actionStatus")}>
                <select value={state.actionStatus} disabled={readOnly} onChange={(e) => set({ actionStatus: e.target.value as ActionStatus })}>
                  {STATUSES.map((s) => <option key={s} value={s}>{t(`ucca.actionStatuses.${s}`)}</option>)}
                </select>
              </FormField>
              <FormField label={t("ucca.form.closureEvidence")}>
                <input value={state.closureEvidence} disabled={readOnly} onChange={(e) => set({ closureEvidence: e.target.value })} />
              </FormField>
            </div>
          )}
        </>
      )}
    </div>
  );
}
