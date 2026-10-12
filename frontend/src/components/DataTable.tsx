import type { ReactNode } from "react";

import { brandTokens } from "../theme/brand-tokens";

type Column<T> = {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  /** Ancho fijo opcional (px o %). Sin él, el navegador reparte el espacio. */
  width?: number | string;
};

type DataTableProps<T> = {
  columns: Column<T>[];
  rows: T[];
  emptyMessage: string;
};

export function DataTable<T extends { id?: string }>({ columns, rows, emptyMessage }: DataTableProps<T>) {
  if (rows.length === 0) {
    return (
      <p
        style={{
          color: brandTokens.colors.textSecondary,
          background: brandTokens.colors.surface,
          border: `1px dashed ${brandTokens.colors.border}`,
          borderRadius: brandTokens.radius.lg,
          padding: "28px 24px",
          textAlign: "center",
        }}
      >
        {emptyMessage}
      </p>
    );
  }

  return (
    <div
      style={{
        background: brandTokens.colors.surface,
        borderRadius: brandTokens.radius.lg,
        boxShadow: brandTokens.shadow.card,
        border: `1px solid ${brandTokens.colors.border}`,
        overflow: "hidden",
      }}
    >
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: brandTokens.colors.surfaceSoft, textAlign: "left" }}>
            {columns.map((col) => (
              <th
                key={col.key}
                style={{
                  width: col.width,
                  padding: "14px 16px",
                  fontSize: 12,
                  fontWeight: 700,
                  letterSpacing: "0.04em",
                  textTransform: "uppercase",
                  color: brandTokens.colors.textSecondary,
                }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={row.id ?? idx} style={{ borderTop: `1px solid ${brandTokens.colors.border}` }}>
              {columns.map((col) => (
                <td key={col.key} style={{ padding: "14px 16px", fontSize: 14, verticalAlign: "top" }}>
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
