import type { ReactNode } from "react";

/** Fila de acciones sobre una tabla: contenido a la izquierda (filtros) y acciones a la derecha. */
export function Toolbar({ left, right }: { left?: ReactNode; right?: ReactNode }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16, marginBottom: 16 }}>
      <div>{left}</div>
      <div style={{ display: "flex", gap: 10 }}>{right}</div>
    </div>
  );
}
