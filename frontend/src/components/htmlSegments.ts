// /utils/htmlSegments.ts
export type JoyColumn = { field: string; headerName: string };
export type JoyRow = Record<string, any> & { id: string | number };
export type HtmlSegment =
    | { type: "text"; text: string }
    | { type: "table"; columns: JoyColumn[]; rows: JoyRow[] };

const HUN_BOOLEAN: Record<string, boolean> = { Igen: true, Nem: false };
const NULL_LIKE = new Set(["–", "-", "", "null", "undefined"]);
const DATE_RE = /\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/;

const HEADER_ALIAS: Record<string, string> = {
    Azonosító: "id",
    "Bejelentkezési név": "login",
    Keresztnév: "firstName",
    "Admin jog": "isAdmin",
    Státusz: "status",
    "Utolsó bejelentkezés": "lastLogin",
    Nyelv: "lang",
    Létrehozva: "createdAt",
    Frissítve: "updatedAt",
    Típus: "type",
    "Email értesítés": "emailNotif",
    "Jelszó módosítása kötelező": "mustChangePwd",
};

export const looksLikeHtmlTable = (s: string) => /<table[\s\S]*?<\/table>/i.test(s);

const toCamelSafe = (field: string) => {
    const ascii = field
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-zA-Z0-9 ]/g, " ")
        .trim();
    return (
        ascii
            .split(/\s+/)
            .map((w, i) => (i === 0 ? w.toLowerCase() : w[0].toUpperCase() + w.slice(1).toLowerCase()))
            .join("") || "field"
    );
};

const coerceValue = (header: string, raw: string) => {
    const t = (raw ?? "").trim();
    if (NULL_LIKE.has(t)) return null;
    if (header.includes("Admin jog") || header.includes("Jelszó módosítása kötelező")) {
        if (t in HUN_BOOLEAN) return HUN_BOOLEAN[t];
    }
    if (header === "Azonosító" && /^\d+$/.test(t)) return Number(t);
    if (DATE_RE.test(t)) return new Date(t.replace(" ", "T"));
    return t;
};

export function parseHtmlTableToJoyData(htmlOrTableEl: string | HTMLTableElement): {
    columns: JoyColumn[];
    rows: JoyRow[];
} {
    let table: HTMLTableElement | null = null;

    if (typeof htmlOrTableEl === "string") {
        const doc = new DOMParser().parseFromString(htmlOrTableEl, "text/html");
        table = doc.querySelector("table");
    } else {
        table = htmlOrTableEl;
    }
    if (!table) return { columns: [], rows: [] };

    let headerCells = Array.from(table.querySelectorAll("thead th"));
    let headerFromFirstRow = false;
    if (headerCells.length === 0) {
        const firstTr = table.querySelector("tbody tr, tr");
        if (firstTr) {
            headerCells = Array.from(firstTr.querySelectorAll("th, td"));
            headerFromFirstRow = true;
        }
    }
    const headers = headerCells.map((th) => th.textContent?.trim() || "");

    const columns: JoyColumn[] = headers.map((h) => ({
        field: HEADER_ALIAS[h] || toCamelSafe(h),
        headerName: h || "Oszlop",
    }));

    let rowTrs = Array.from(table.querySelectorAll("tbody tr"));
    if (rowTrs.length === 0) rowTrs = Array.from(table.querySelectorAll("tr"));

    if (headerFromFirstRow && rowTrs.length > 0) {
        rowTrs = rowTrs.slice(1);
    }

    const rows: JoyRow[] = rowTrs.map((tr, idx) => {
        const cells = Array.from(tr.querySelectorAll("td, th"));
        const row: Record<string, any> = {};
        cells.forEach((td, i) => {
            const h = headers[i] || `col${i}`;
            const field = HEADER_ALIAS[h] || toCamelSafe(h);
            row[field] = coerceValue(h, td.textContent || "");
        });
        if (row.id == null) row.id = idx + 1;
        return row as JoyRow;
    });

    return { columns, rows };
}

export function parseHtmlMessageToSegments(html: string): HtmlSegment[] {
    const doc = new DOMParser().parseFromString(html, "text/html");
    const body = doc.body;
    const segs: HtmlSegment[] = [];

    const pushText = (t?: string | null) => {
        const s = (t ?? "").replace(/\s+/g, " ").trim();
        if (s) segs.push({ type: "text", text: s });
    };

    const walk = (node: Node) => {
        if (node.nodeType === Node.ELEMENT_NODE) {
            const el = node as HTMLElement;
            if (el.tagName === "TABLE") {
                const { columns, rows } = parseHtmlTableToJoyData(el);
                segs.push({ type: "table", columns, rows });
                return;
            }
            node.childNodes.forEach(walk);
            return;
        }
        if (node.nodeType === Node.TEXT_NODE) pushText(node.textContent);
    };

    walk(body);

    const merged: HtmlSegment[] = [];
    for (const s of segs) {
        const last = merged[merged.length - 1];
        if (s.type === "text" && last?.type === "text") {
            last.text = `${last.text} ${s.text}`.replace(/\s+/g, " ").trim();
        } else {
            merged.push(s);
        }
    }
    return merged;
}

export const generateId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
export const brandGradient = "linear-gradient(90deg, #E0081F 0%, #005A9B 100%)";
