import type { ReactNode } from "react";

import { brandTokens } from "../theme/brand-tokens";

type Column<T> = {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
};

type DataTableProps<T> = {
  columns: Column<T>[];
  rows: T[];
  emptyMessage: string;
};

export function DataTable<T extends { id?: string }>({
  columns,
  rows,
  emptyMessage,
}: DataTableProps<T>) {
  if (rows.length === 0) {
    return <p style={{ color: brandTokens.colors.textSecondary }}>{emptyMessage}</p>;
  }

  return (
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse",
        background: brandTokens.colors.surface,
        borderRadius: 8,
        overflow: "hidden",
        boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
      }}
    >
      <thead>
        <tr style={{ background: "#EEF4F6", textAlign: "left" }}>
          {columns.map((col) => (
            <th key={col.key} style={{ padding: "10px 14px", fontSize: 13, fontWeight: 600 }}>
              {col.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, idx) => (
          <tr key={row.id ?? idx} style={{ borderTop: "1px solid #E2E8EC" }}>
            {columns.map((col) => (
              <td key={col.key} style={{ padding: "10px 14px", fontSize: 14 }}>
                {col.render(row)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
