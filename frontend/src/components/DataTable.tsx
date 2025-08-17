// /components/JoySortableFilterableTable.tsx
import * as React from "react";
import { Box, FormControl, FormLabel, Input, Option, Select, Sheet, Table } from "@mui/joy";

type SortDir = "asc" | "desc" | null;
export type JoyColumn = { field: string; headerName: string };
export type JoyRow = Record<string, any> & { id: string | number };

const smartCompare = (a: any, b: any) => {
    const norm = (v: any) => (v instanceof Date ? v.getTime() : typeof v === "boolean" ? (v ? 1 : 0) : v);
    const A = norm(a), B = norm(b);
    if (A == null && B == null) return 0;
    if (A == null) return -1;
    if (B == null) return 1;
    if (typeof A === "number" && typeof B === "number") return A - B;
    return String(A).localeCompare(String(B), "hu", { sensitivity: "base", numeric: true });
};

export default function DataTable({ columns, rows }: { columns: JoyColumn[]; rows: JoyRow[] }) {
    const [sortField, setSortField] = React.useState<string>(columns[0]?.field ?? "id");
    const [sortDir, setSortDir] = React.useState<SortDir>("asc");
    const [filterText, setFilterText] = React.useState("");
    const [filterField, setFilterField] = React.useState<string>("__all__");

    const filtered = React.useMemo(() => {
        if (!filterText.trim()) return rows;
        const q = filterText.trim().toLowerCase();
        if (filterField === "__all__") {
            return rows.filter((r) => columns.some((c) => String(r[c.field] ?? "").toLowerCase().includes(q)));
        }
        return rows.filter((r) => String(r[filterField] ?? "").toLowerCase().includes(q));
    }, [rows, columns, filterText, filterField]);

    const sorted = React.useMemo(() => {
        if (!sortField || !sortDir) return filtered;
        return [...filtered].sort((a, b) => {
            const cmp = smartCompare(a[sortField], b[sortField]);
            return sortDir === "asc" ? cmp : -cmp;
        });
    }, [filtered, sortField, sortDir]);

    const onHeaderClick = (field: string) => {
        if (sortField !== field) {
            setSortField(field);
            setSortDir("asc");
        } else {
            setSortDir((d) => (d === "asc" ? "desc" : d === "desc" ? null : "asc"));
        }
    };

    return (
        <Sheet variant="soft" sx={{ p: 1, borderRadius: 8 }}>
            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", alignItems: "center", mb: 1 }}>
                <FormControl size="sm">
                    <FormLabel>Szűrés</FormLabel>
                    <Input placeholder="Keresés…" value={filterText} onChange={(e) => setFilterText(e.target.value)} sx={{ minWidth: 220 }} />
                </FormControl>
                <FormControl size="sm">
                    <FormLabel>Mező</FormLabel>
                    <Select value={filterField} onChange={(_, v) => setFilterField(v ?? "__all__")} sx={{ minWidth: 180 }}>
                        <Option value="__all__">Mind</Option>
                        {columns.map((c) => (
                            <Option key={c.field} value={c.field}>{c.headerName}</Option>
                        ))}
                    </Select>
                </FormControl>
                <Box sx={{ ml: "auto", fontSize: 12, opacity: 0.8 }}>{sorted.length} találat</Box>
            </Box>

            <Sheet variant="outlined" sx={{ borderRadius: 8, overflow: "auto", maxHeight: 440 }}>
                <Table stickyHeader hoverRow size="sm" variant="soft" borderAxis="bothBetween">
                    <thead>
                    <tr>
                        {columns.map((c) => {
                            const active = sortField === c.field && sortDir;
                            const arrow = !active ? "↕" : sortDir === "asc" ? "▲" : sortDir === "desc" ? "▼" : "•";
                            return (
                                <th key={c.field} onClick={() => onHeaderClick(c.field)} style={{ cursor: "pointer", whiteSpace: "nowrap", fontWeight: 600, padding: "8px 12px" }}>
                                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                        <span>{c.headerName}</span>
                                        <span style={{ fontSize: 12, opacity: active ? 1 : 0.5 }}>{arrow}</span>
                                    </Box>
                                </th>
                            );
                        })}
                    </tr>
                    </thead>
                    <tbody>
                    {sorted.map((r) => (
                        <tr key={r.id}>
                            {columns.map((c) => {
                                const v = r[c.field];
                                const formatted = v instanceof Date ? v.toLocaleString("hu-HU") : typeof v === "boolean" ? (v ? "Igen" : "Nem") : v ?? "";
                                return <td key={c.field} style={{ padding: "8px 12px", verticalAlign: "top" }}>{String(formatted)}</td>;
                            })}
                        </tr>
                    ))}
                    </tbody>
                </Table>
            </Sheet>
        </Sheet>
    );
}
