import { useTranslation } from "react-i18next";

import type { AnswerValue } from "../types";

const VALUES: AnswerValue[] = ["compliant", "non_compliant", "not_applicable"];

export function AnswerSelector({ value, onChange, disabled, name }: {
  value: AnswerValue | null; onChange: (v: AnswerValue) => void; disabled?: boolean; name: string;
}) {
  const { t } = useTranslation();
  return (
    <div className="segmented" role="group" aria-label={name}>
      {VALUES.map((v) => (
        <button key={v} type="button" data-value={v} aria-pressed={value === v} disabled={disabled} onClick={() => onChange(v)}>
          {t(`ucca.answers.${v}`)}
        </button>
      ))}
    </div>
  );
}
