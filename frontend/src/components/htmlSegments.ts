// utils/htmlSegments.ts
import type { GridColDef } from "@mui/x-data-grid";

export type Row = Record<string, any> & { id: string | number };
export type HtmlSegment =
    | { type: "text"; text: string }
    | { type: "table"; columns: GridColDef[]; rows: Row[] };

export const looksLikeHtmlTable = (s: string) => /<table[\s\S]*?<\/table>/i.test(s);

const toCamelSafe = (field: string) =>
    field
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-zA-Z0-9 ]/g, " ")
        .trim()
        .split(/\s+/)
        .map((w, i) => (i === 0 ? w.toLowerCase() : w[0].toUpperCase() + w.slice(1).toLowerCase()))
        .join("") || "field";

export function parseHtmlTable(htmlOrEl: string | HTMLElement): { columns: GridColDef[]; rows: Row[] } {
    const doc = typeof htmlOrEl === "string" ? new DOMParser().parseFromString(htmlOrEl, "text/html") : null;
    const table = typeof htmlOrEl === "string" ? doc?.querySelector("table") : htmlOrEl;
    if (!table) return { columns: [], rows: [] };

    let headerCells: Element[] = [];
    let headerFromFirstRow = false;

    const theadCells = Array.from(table.querySelectorAll("thead th"));
    if (theadCells.length > 0) {
        headerCells = theadCells;
    } else {
        const firstRow = table.querySelector("tr");
        if (firstRow) {
            headerCells = Array.from(firstRow.querySelectorAll("th, td"));
            headerFromFirstRow = true;
        }
    }

    const headers = headerCells.map((th, i) => th.textContent?.trim() || `col${i}`);

    const columns: GridColDef[] = headers.map((h) => ({
        field: toCamelSafe(h),
        headerName: h,
        flex: 1,
    }));

    let rowTrs = Array.from(table.querySelectorAll("tbody tr"));
    if (rowTrs.length === 0) {
        rowTrs = Array.from(table.querySelectorAll("tr"));
    }
    if (headerFromFirstRow && rowTrs.length > 0) {
        rowTrs = rowTrs.slice(1);
    }

    const rows: Row[] = rowTrs.map((tr, idx) => {
        const cells = Array.from(tr.querySelectorAll("td, th"));
        const row: Record<string, any> = {};
        cells.forEach((td, i) => {
            const h = headers[i] || `col${i}`;
            row[toCamelSafe(h)] = td.textContent?.trim() ?? "";
        });
        row.id ??= idx + 1;
        return row as Row;
    });

    return { columns, rows };
}

export function parseHtmlMessageToSegments(html: string): HtmlSegment[] {
    const doc = new DOMParser().parseFromString(html, "text/html");
    const segs: HtmlSegment[] = [];

    const walk = (node: Node) => {
        if (node.nodeType === Node.ELEMENT_NODE) {
            const el = node as HTMLElement;
            if (el.tagName === "TABLE") {
                segs.push({ type: "table", ...parseHtmlTable(el) });
            } else {
                el.childNodes.forEach(walk);
            }
        } else if (node.nodeType === Node.TEXT_NODE) {
            const t = node.textContent?.trim();
            if (t) segs.push({ type: "text", text: t });
        }
    };
    walk(doc.body);

    return segs.reduce<HtmlSegment[]>((acc, cur) => {
        if (cur.type === "text" && acc.at(-1)?.type === "text") {
            (acc.at(-1) as { type: "text"; text: string }).text += " " + cur.text;
        } else acc.push(cur);
        return acc;
    }, []);
}

export const generateId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
export const brandGradient = "linear-gradient(90deg, #E0081F 0%, #005A9B 100%)";
