import type { AnswerValue, Outcome } from "./types";

/** Réplica exacta de backend/app/domains/governance/ucca/scoring.py para feedback en vivo. */
export type ScoreResult = { applicable: number; yes: number; score: number | null; outcome: Outcome | null };

export const OUTCOME_BANDS: [Outcome, number][] = [
  ["compliant", 90],
  ["minor_improvement", 80],
  ["improvement_required", 70],
];
export const PRIORITY_OUTCOME: Outcome = "priority_corrective_action";

export function outcomeFor(score: number | null): Outcome | null {
  if (score === null) return null;
  for (const [outcome, threshold] of OUTCOME_BANDS) if (score >= threshold) return outcome;
  return PRIORITY_OUTCOME;
}

export function computeScore(outcomes: AnswerValue[]): ScoreResult {
  const applicable = outcomes.filter((o) => o !== "not_applicable").length;
  const yes = outcomes.filter((o) => o === "compliant").length;
  const score = applicable === 0 ? null : Math.round((yes / applicable) * 10000) / 100;
  return { applicable, yes, score, outcome: outcomeFor(score) };
}

export function formatScore(score: number | null): string {
  return score === null ? "—" : `${score.toFixed(score % 1 === 0 ? 0 : 2)} %`;
}

/** Siguiente trimestre libre para un centro, a partir de sus ciclos existentes. Sin ciclos → trimestre
 * calendario actual. Se usa como valor por defecto del drawer "Nuevo ciclo"; siempre editable. */
export function nextQuarter(existing: { year: number; quarter: string }[], today = new Date()): { year: number; quarter: string } {
  if (existing.length === 0) {
    return { year: today.getFullYear(), quarter: `Q${Math.floor(today.getMonth() / 3) + 1}` };
  }
  const last = existing.reduce((best, c) => (c.year > best.year || (c.year === best.year && c.quarter > best.quarter) ? c : best));
  const q = Number(last.quarter.replace("Q", ""));
  return q >= 4 ? { year: last.year + 1, quarter: "Q1" } : { year: last.year, quarter: `Q${q + 1}` };
}
