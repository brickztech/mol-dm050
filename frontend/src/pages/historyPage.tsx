// import * as React from "react";
// import {
//     Box,
//     Sheet,
//     Typography,
//     Input,
//     Select,
//     Option,
//     Chip,
//     IconButton,
//     Tooltip,
//     Card,
//     CardContent,
//     CardOverflow,
//     Button,
//     Divider,
//     Table,
//     Modal,
//     ModalDialog,
//     AspectRatio,
//     Skeleton,             // 👈 NEW
// } from "@mui/joy";
// import SearchRoundedIcon from "@mui/icons-material/SearchRounded";
// import ReplayRoundedIcon from "@mui/icons-material/ReplayRounded";
// import DeleteSweepRoundedIcon from "@mui/icons-material/DeleteSweepRounded";
// import OpenInNewRoundedIcon from "@mui/icons-material/OpenInNewRounded";
// import VisibilityRoundedIcon from "@mui/icons-material/VisibilityRounded";
// import CalendarMonthRoundedIcon from "@mui/icons-material/CalendarMonthRounded";
// import QueryStatsRoundedIcon from "@mui/icons-material/QueryStatsRounded";
// import DataObjectRoundedIcon from "@mui/icons-material/DataObjectRounded";
// import TableChartRoundedIcon from "@mui/icons-material/TableChartRounded";
// import { AnimatePresence, motion } from "framer-motion";
//
// import chartThumb from "src/assets/chart.png";
//
//
// type HistoryItem = {
//     id: string;
//     question: string;
//     createdAt: number;
//     durationMs: number;
//     status: "success" | "error" | "partial";
//     rowsReturned: number;
//     dbName: string;
//     tags: string[];
//     thumbUrl: string;
//     sql: string;
//     resultSample: { columns: string[]; rows: Array<Record<string, any>> } | null;
// };
//
// function seededRandom(seed: number) {
//     let x = Math.sin(seed) * 10000;
//     return () => {
//         x = Math.sin(x) * 10000;
//         return x - Math.floor(x);
//     };
// }
// function formatDateShort(ts: number) {
//     const d = new Date(ts);
//     return new Intl.DateTimeFormat(undefined, {
//         year: "numeric",
//         month: "short",
//         day: "2-digit",
//         hour: "2-digit",
//         minute: "2-digit",
//     }).format(d);
// }
// function humanMs(ms: number) {
//     if (ms < 1000) return `${ms} ms`;
//     const s = ms / 1000;
//     if (s < 60) return `${s.toFixed(1)} s`;
//     const m = Math.floor(s / 60);
//     const r = Math.round(s % 60);
//     return `${m}m ${r}s`;
// }
//
// const gridVariants = {
//     hidden: { opacity: 0 },
//     show: {
//         opacity: 1,
//         transition: { staggerChildren: 0.06, delayChildren: 0.02 },
//     },
// };
// const cardVariants = {
//     hidden: { opacity: 0, y: 12, scale: 0.98 },
//     show: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.24, ease: "easeOut" } },
//     exit: { opacity: 0, y: 8, scale: 0.98, transition: { duration: 0.16, ease: "easeIn" } },
// };
//
// function makeMockItem(i: number, thumbs?: string[]): HistoryItem {
//     const rnd = seededRandom(i + 42);
//     const statuses: HistoryItem["status"][] = ["success", "partial", "error"];
//     const status = statuses[Math.floor(rnd() * statuses.length)];
//     const createdAt = Date.now() - Math.floor(rnd() * 1000 * 60 * 60 * 24 * 14);
//     const durationMs = Math.floor(200 + rnd() * 6000);
//     const rowsReturned = Math.floor(rnd() * 5000);
//     const dbs = ["sales_prod", "analytics", "warehouse", "ops_reporting"];
//     const dbName = dbs[Math.floor(rnd() * dbs.length)];
//     const tagsPool = ["revenue", "pivot", "orders", "retention", "latency", "anomalies", "inventory"];
//     const pickTags = Array.from(
//         new Set(Array.from({ length: 1 + Math.floor(rnd() * 3) }, () => tagsPool[Math.floor(rnd() * tagsPool.length)]))
//     );
//     const questions = [
//         "Top 10 customers by lifetime revenue this year",
//         "Monthly sales by region for 2024 (pivot)",
//         "Orders delayed > 7 days: id, customer, days delayed",
//         "Weekly active users vs. churn (last 12 weeks)",
//         "Inventory low stock (threshold < 10 units)",
//         "Detect revenue anomalies for Q2",
//     ];
//     const question = questions[i % questions.length];
//
//     const columns = ["name", "region", "revenue"];
//     const rows = Array.from({ length: 4 }, (_, r) => [
//         `Row ${r + 1}`,
//         ["EU", "NA", "APAC"][Math.floor(rnd() * 3)],
//         `$${(1000 + rnd() * 9000).toFixed(0)}`,
//     ]);
//     const resultSample = {
//         columns,
//         rows: rows.map((r) => ({ name: r[0], region: r[1], revenue: r[2] })),
//     };
//
//     const thumbUrl = chartThumb;
//     const sql = `-- auto-generated SQL
// SELECT name, region, SUM(revenue) AS revenue
// FROM orders
// WHERE created_at >= '2024-01-01'
// GROUP BY 1,2
// ORDER BY revenue DESC
// LIMIT 10;`;
//
//     return {
//         id: `hist_${i}`,
//         question,
//         createdAt,
//         durationMs,
//         status,
//         rowsReturned,
//         dbName,
//         tags: pickTags,
//         thumbUrl,
//         sql,
//         resultSample,
//     };
// }
// function useMockHistory(count = 18, thumbs?: string[]) {
//     const [items] = React.useState(() => Array.from({ length: count }, (_, i) => makeMockItem(i + 1, thumbs)));
//     return items;
// }
//
//
// function HistorySkeletonCard() {
//     return (
//         <Card
//             variant="outlined"
//             sx={(theme) => ({
//                 borderRadius: 8,
//                 overflow: "hidden",
//                 display: "flex",
//                 flexDirection: "column",
//                 width: "100%",
//                 bgcolor: "background.level1",
//                 [theme.getColorSchemeSelector("dark")]: {
//                     bgcolor: "rgba(255 255 255 / 0.06)",
//                     borderColor: "neutral.outlinedBorder",
//                 },
//             })}
//         >
//             <CardOverflow>
//                 <AspectRatio ratio="16/9">
//                     <Skeleton variant="rectangular" />
//                 </AspectRatio>
//             </CardOverflow>
//             <CardContent sx={{ display: "grid", gap: 0.7 }}>
//                 <Skeleton variant="text" level="title-sm" />
//                 <Box sx={{ display: "flex", gap: 0.75, flexWrap: "wrap" }}>
//                     <Skeleton variant="rectangular" width={72} height={24} />
//                     <Skeleton variant="rectangular" width={90} height={24} />
//                     <Skeleton variant="rectangular" width={90} height={24} />
//                 </Box>
//                 <Skeleton variant="text" level="body-xs" />
//                 <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", mt: 0.5 }}>
//                     <Skeleton variant="rectangular" width={64} height={22} />
//                     <Skeleton variant="rectangular" width={72} height={22} />
//                 </Box>
//             </CardContent>
//             <CardOverflow sx={{ p: 1, pt: 0.5 }}>
//                 <Skeleton variant="rectangular" height={96} />
//             </CardOverflow>
//         </Card>
//     );
// }
// function HistorySkeletonGrid() {
//     return (
//         <Box
//             sx={{
//                 display: "grid",
//                 gap: 1.5,
//                 gridTemplateColumns: { xs: "1fr", lg: "1fr 1fr 1fr" },
//             }}
//         >
//             {Array.from({ length: 6 }).map((_, i) => (
//                 <Box key={i} sx={{ display: "flex" }}>
//                     <HistorySkeletonCard />
//                 </Box>
//             ))}
//         </Box>
//     );
// }
//
//
// export default function HistoryPage({ thumbs }: { thumbs?: string[] }) {
//     const allItems = useMockHistory(21, thumbs);
//
//     const [query, setQuery] = React.useState("");
//     const [status, setStatus] = React.useState<string | null>(null);
//     const [db, setDb] = React.useState<string | null>(null);
//
//     const [loading, setLoading] = React.useState(true);
//
//     const [selected, setSelected] = React.useState<HistoryItem | null>(null);
//     const [detailLoading, setDetailLoading] = React.useState(false);
//
//     React.useEffect(() => {
//
//         const t = setTimeout(() => setLoading(false), 400);
//         return () => clearTimeout(t);
//     }, []);
//
//     const filtered = React.useMemo(() => {
//         if (loading) return [];
//         return allItems.filter((it) => {
//             const q = query.trim().toLowerCase();
//             const matchesQuery =
//                 !q || it.question.toLowerCase().includes(q) || it.tags.some((t) => t.toLowerCase().includes(q));
//             const matchesStatus = !status || it.status === status;
//             const matchesDb = !db || it.dbName === db;
//             return matchesQuery && matchesStatus && matchesDb;
//         });
//     }, [allItems, query, status, db, loading]);
//
//     const openDetail = (it: HistoryItem) => {
//         setSelected(it);
//         setDetailLoading(true);
//         const t = setTimeout(() => setDetailLoading(false), 300);
//         return () => clearTimeout(t);
//     };
//
//     return (
//         <Box sx={{ p: { xs: 1, md: 2 }, display: "grid", gap: 1.5 }}>
//             <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
//                 <Typography level="h4" sx={{ display: "flex", alignItems: "center", gap: 1 }}>
//                     <QueryStatsRoundedIcon /> History
//                 </Typography>
//                 <Box sx={{ flex: 1 }} />
//                 <Tooltip title="Clear filters">
//                     <Button
//                         variant="plain"
//                         size="sm"
//                         onClick={() => {
//                             setQuery("");
//                             setStatus(null);
//                             setDb(null);
//                         }}
//                     >
//                         Reset
//                     </Button>
//                 </Tooltip>
//             </Box>
//
//             <Sheet
//                 variant="outlined"
//                 sx={(theme) => ({
//                     p: 1,
//                     borderRadius: 5,
//                     display: "grid",
//                     gap: 1,
//                     gridTemplateColumns: { xs: "1fr", md: "2fr 1fr 1fr" },
//                     bgcolor: "background.surface",
//                     [theme.getColorSchemeSelector("dark")]: {
//                         bgcolor: "rgba(255 255 255 / 0.04)",
//                         borderColor: "neutral.outlinedBorder",
//                     },
//                 })}
//             >
//                 <Input
//                     startDecorator={<SearchRoundedIcon />}
//                     placeholder="Search questions, tags…"
//                     value={query}
//                     onChange={(e) => setQuery(e.target.value)}
//                     sx={(theme) => ({
//                         bgcolor: "background.level1",
//                         [theme.getColorSchemeSelector("dark")]: {
//                             bgcolor: "rgba(255 255 255 / 0.06)",
//                         },
//                     })}
//                 />
//                 <Select
//                     value={status}
//                     placeholder="Status"
//                     onChange={(_, v) => setStatus(v)}
//                     sx={(theme) => ({
//                         bgcolor: "background.level1",
//                         [theme.getColorSchemeSelector("dark")]: {
//                             bgcolor: "rgba(255 255 255 / 0.06)",
//                         },
//                     })}
//                 >
//                     <Option value={null as any}>Any</Option>
//                     <Option value="success">Success</Option>
//                     <Option value="partial">Partial</Option>
//                     <Option value="error">Error</Option>
//                 </Select>
//                 <Select
//                     value={db}
//                     placeholder="Database"
//                     onChange={(_, v) => setDb(v)}
//                     sx={(theme) => ({
//                         bgcolor: "background.level1",
//                         [theme.getColorSchemeSelector("dark")]: {
//                             bgcolor: "rgba(255 255 255 / 0.06)",
//                         },
//                     })}
//                 >
//                     <Option value={null as any}>Any</Option>
//                     <Option value="sales_prod">sales_prod</Option>
//                     <Option value="analytics">analytics</Option>
//                     <Option value="warehouse">warehouse</Option>
//                     <Option value="ops_reporting">ops_reporting</Option>
//                 </Select>
//             </Sheet>
//
//             {loading ? (
//                 <HistorySkeletonGrid />
//             ) : (
//                 <motion.div
//                     key={`${query}-${status}-${db}`}
//                     variants={gridVariants}
//                     initial="hidden"
//                     animate="show"
//                     layout
//                     style={{ display: "grid", gap: 8 }}
//                 >
//                     <Box
//                         component={motion.div}
//                         layout
//                         sx={{
//                             display: "grid",
//                             gap: 1.5,
//                             gridTemplateColumns: { xs: "1fr", lg: "1fr 1fr 1fr" },
//                         }}
//                     >
//                         <AnimatePresence mode="popLayout">
//                             {filtered.map((it) => (
//                                 <motion.div
//                                     key={it.id}
//                                     layout
//                                     whileHover={{ y: -2 }}
//                                     whileTap={{ scale: 0.995 }}
//                                     style={{ display: "flex" }}
//                                 >
//                                     <Card
//                                         variant="outlined"
//                                         sx={(theme) => ({
//                                             borderRadius: 8,
//                                             overflow: "hidden",
//                                             display: "flex",
//                                             flexDirection: "column",
//                                             width: "100%",
//                                             bgcolor: "background.level1",
//                                             [theme.getColorSchemeSelector("dark")]: {
//                                                 bgcolor: "rgba(255 255 255 / 0.06)",
//                                                 borderColor: "neutral.outlinedBorder",
//                                             },
//                                         })}
//                                     >
//                                         <CardOverflow sx={{ position: "relative" }}>
//                                             <AspectRatio ratio="16/9" variant="plain">
//                                                 <img src={it.thumbUrl} alt="chart preview" loading="lazy" />
//                                             </AspectRatio>
//
//                                             <Sheet
//                                                 variant="soft"
//                                                 sx={{
//                                                     position: "absolute",
//                                                     top: 8,
//                                                     left: 8,
//                                                     borderRadius: 999,
//                                                     px: 0.75,
//                                                     py: 0.25,
//                                                     display: "flex",
//                                                     alignItems: "center",
//                                                     gap: 0.5,
//                                                     backdropFilter: "blur(6px)",
//                                                 }}
//                                             >
//                                                 <TableChartRoundedIcon fontSize="small" />
//                                                 <Typography level="body-xs">Chart</Typography>
//                                             </Sheet>
//                                         </CardOverflow>
//
//                                         <CardContent sx={{ display: "grid", gap: 0.7 }}>
//                                             <Typography level="title-sm" sx={{ lineClamp: 2 }}>
//                                                 {it.question}
//                                             </Typography>
//
//                                             <Box sx={{ display: "flex", alignItems: "center", gap: 0.75, rowGap: 1, flexWrap: "wrap" }}>
//                                                 <Chip
//                                                     size="sm"
//                                                     variant="soft"
//                                                     color={
//                                                         it.status === "success" ? "success" : it.status === "partial" ? "warning" : "danger"
//                                                     }
//                                                 >
//                                                     {it.status}
//                                                 </Chip>
//                                                 <Chip size="sm" startDecorator={<TableChartRoundedIcon />}>
//                                                     {it.rowsReturned} rows
//                                                 </Chip>
//                                                 <Chip size="sm" startDecorator={<DataObjectRoundedIcon />}>
//                                                     {it.dbName}
//                                                 </Chip>
//                                             </Box>
//
//                                             <Typography level="body-xs" startDecorator={<CalendarMonthRoundedIcon />} sx={{ opacity: 0.7 }}>
//                                                 {formatDateShort(it.createdAt)} • {humanMs(it.durationMs)}
//                                             </Typography>
//
//                                             <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", mt: 0.5 }}>
//                                                 {it.tags.map((t) => (
//                                                     <Chip key={t} size="sm" variant="outlined" onClick={() => setQuery(t)}>
//                                                         {t}
//                                                     </Chip>
//                                                 ))}
//                                             </Box>
//                                         </CardContent>
//
//                                         <CardOverflow sx={{ p: 1, pt: 0.5 }}>
//                                             {it.resultSample && (
//                                                 <Sheet
//                                                     variant="outlined"
//                                                     sx={(theme) => ({
//                                                         borderRadius: 10,
//                                                         overflow: "hidden",
//                                                         p: 0.5,
//                                                         "--TableCell-paddingY": "8px",
//                                                         "--TableCell-paddingX": "10px",
//                                                         bgcolor: "background.body",
//                                                         [theme.getColorSchemeSelector("dark")]: {
//                                                             bgcolor: "rgba(255 255 255 / 0.03)",
//                                                         },
//                                                     })}
//                                                     component={motion.div}
//                                                     initial={{ opacity: 0 }}
//                                                     whileInView={{ opacity: 1 }}
//                                                     viewport={{ once: true, amount: 0.4 }}
//                                                     transition={{ duration: 0.25 }}
//                                                 >
//                                                     <Table aria-label="mini preview" size="sm" stickyHeader stripe="even" hoverRow>
//                                                         <thead>
//                                                         <tr>
//                                                             {it.resultSample.columns.map((c) => (
//                                                                 <th key={c}>{c}</th>
//                                                             ))}
//                                                         </tr>
//                                                         </thead>
//                                                         <tbody>
//                                                         {it.resultSample.rows.slice(0, 3).map((r, idx) => (
//                                                             <tr key={idx}>
//                                                                 {it.resultSample.columns.map((c) => (
//                                                                     <td key={c}>{String(r[c])}</td>
//                                                                 ))}
//                                                             </tr>
//                                                         ))}
//                                                         </tbody>
//                                                     </Table>
//                                                 </Sheet>
//                                             )}
//                                         </CardOverflow>
//
//                                         <CardOverflow sx={{ p: 1, display: "flex", gap: 0.5, justifyContent: "flex-end", flexDirection: "row" }}>
//                                             <Tooltip title="Preview">
//                                                 <IconButton size="sm" variant="plain" onClick={() => openDetail(it)}>
//                                                     <VisibilityRoundedIcon />
//                                                 </IconButton>
//                                             </Tooltip>
//                                             <Tooltip title="Re-run (mock)">
//                                                 <IconButton size="sm" variant="plain">
//                                                     <ReplayRoundedIcon />
//                                                 </IconButton>
//                                             </Tooltip>
//                                             <Tooltip title="Delete (mock)">
//                                                 <IconButton size="sm" variant="plain">
//                                                     <DeleteSweepRoundedIcon />
//                                                 </IconButton>
//                                             </Tooltip>
//                                             <Tooltip title="Open in new tab (mock)">
//                                                 <IconButton size="sm" variant="plain">
//                                                     <OpenInNewRoundedIcon />
//                                                 </IconButton>
//                                             </Tooltip>
//                                         </CardOverflow>
//                                     </Card>
//                                 </motion.div>
//                             ))}
//                         </AnimatePresence>
//                     </Box>
//                 </motion.div>
//             )}
//
//             {!loading && filtered.length === 0 && (
//                 <Sheet variant="soft" sx={{ p: 3, borderRadius: 5, textAlign: "center" }}>
//                     <Typography level="title-md">No history matches your filters</Typography>
//                     <Typography level="body-sm" sx={{ mt: 0.5, opacity: 0.8 }}>
//                         Try clearing filters or searching different keywords.
//                     </Typography>
//                     <Button
//                         sx={{ mt: 1 }}
//                         variant="outlined"
//                         onClick={() => {
//                             setQuery("");
//                             setStatus(null);
//                             setDb(null);
//                         }}
//                     >
//                         Reset filters
//                     </Button>
//                 </Sheet>
//             )}
//             <Modal
//                 open={!!selected}
//                 onClose={() => setSelected(null)}
//                 sx={{
//                     zIndex: 1300,
//                     backdropFilter: "blur(6px)",
//                     display: "flex",
//                     alignItems: "center",
//                     justifyContent: "center",
//                 }}
//             >
//                 <ModalDialog
//                     layout="fullscreen"
//                     size="lg"
//                     component={motion.div}
//                     initial={{ opacity: 0, scale: 0.98, y: 8 }}
//                     animate={{ opacity: 1, scale: 1, y: 0 }}
//                     exit={{ opacity: 0, scale: 0.98, y: 8 }}
//                     transition={{ duration: 0.18, ease: "easeOut" }}
//                     sx={(theme) => ({
//                         p: 0,
//                         maxWidth: "55%",
//                         width: "100%",
//                         maxHeight: "90vh",
//                         height: "100%",
//                         overflow: "hidden",
//                         borderRadius: 5,
//                         boxShadow: "lg",
//                         margin: "auto",
//                         bgcolor: "rgba(255 255 255 / 0.98)",
//                         borderColor: "neutral.outlinedBorder",
//                         [theme.getColorSchemeSelector("dark")]: {
//                             bgcolor: "rgba(16 18 22 / 0.98)",
//                             borderColor: "neutral.outlinedBorder",
//                         },
//                     })}
//                 >
//                     <Box
//                         sx={(theme) => ({
//                             position: "sticky",
//                             top: 0,
//                             zIndex: 3,
//                             display: "flex",
//                             alignItems: "center",
//                             gap: 1,
//                             justifyContent: "space-between",
//                             px: { xs: 1, md: 2 },
//                             py: 1,
//                             borderBottom: "1px solid",
//                             borderColor: "neutral.outlinedBorder",
//                             bgcolor: "rgba(255 255 255 / 0.98)",
//                             [theme.getColorSchemeSelector("dark")]: {
//                                 bgcolor: "rgba(16 18 22 / 0.98)",
//                             },
//                         })}
//                     >
//                         <Typography
//                             level="title-lg"
//                             sx={{
//                                 pr: 1,
//                                 overflow: "hidden",
//                                 textOverflow: "ellipsis",
//                                 whiteSpace: "nowrap",
//                             }}
//                             title={selected?.question}
//                         >
//                             {selected ? selected.question : "Preview"}
//                         </Typography>
//
//                         <IconButton onClick={() => setSelected(null)} variant="plain" color="neutral" aria-label="Close">
//                             ✕
//                         </IconButton>
//                     </Box>
//
//                     {selected && !detailLoading && (
//                         <Box
//                             sx={(theme) => ({
//                                 zIndex: 2,
//                                 px: { xs: 1, md: 2 },
//                                 py: 0.75,
//                                 borderBottom: "1px solid",
//                                 borderColor: "neutral.outlinedBorder",
//                                 bgcolor: "rgba(255 255 255 / 0.98)",
//                                 [theme.getColorSchemeSelector("dark")]: {
//                                     bgcolor: "rgba(16 18 22 / 0.98)",
//                                 },
//                             })}
//                         >
//                             <Typography level="body-xs" sx={{ opacity: 0.7 }}>
//                                 {formatDateShort(selected.createdAt)} • {humanMs(selected.durationMs)} • {selected.dbName}
//                             </Typography>
//                         </Box>
//                     )}
//
//                     <Box
//                         sx={{
//                             overflowY: "auto",
//                             p: { xs: 1, md: 2 },
//                             height: "100%",
//                         }}
//                     >
//                         {!selected ? null : detailLoading ? (
//                             <Box sx={{ display: "grid", gap: 1 }}>
//                                 <Skeleton variant="text" level="body-sm" width="45%" />
//                                 <Divider sx={{ my: 1 }} />
//                                 <Skeleton variant="text" width="30%" />
//                                 <Skeleton variant="rectangular" height={180} sx={{ borderRadius: 12 }} />
//                                 <Skeleton variant="text" width="30%" />
//                                 <Skeleton variant="rectangular" height={140} sx={{ borderRadius: 10 }} />
//                             </Box>
//                         ) : (
//                             <Box
//                                 sx={{
//                                     display: "flex",
//                                     gap: 1,
//                                     flexDirection: { xs: "row", md: "column" },
//                                 }}
//                             >
//                                 <Box>
//                                     <Typography level="title-sm" sx={{ mb: 0.5 }}>
//                                         Result preview
//                                     </Typography>
//
//                                     {selected.resultSample ? (
//                                         <Sheet variant="outlined" sx={{ borderRadius: 12, overflow: "hidden" }}>
//                                             <Table hoverRow stickyHeader stripe="even">
//                                                 <thead>
//                                                 <tr>
//                                                     {selected.resultSample.columns.map((c) => (
//                                                         <th key={c}>{c}</th>
//                                                     ))}
//                                                 </tr>
//                                                 </thead>
//                                                 <tbody>
//                                                 {selected.resultSample.rows.map((r, idx) => (
//                                                     <tr key={idx}>
//                                                         {selected.resultSample!.columns.map((c) => (
//                                                             <td key={c}>{String(r[c])}</td>
//                                                         ))}
//                                                     </tr>
//                                                 ))}
//                                                 </tbody>
//                                             </Table>
//                                         </Sheet>
//                                     ) : (
//                                         <Typography level="body-sm">No table sample available.</Typography>
//                                     )}
//
//                                     <Typography level="title-sm" sx={{ mt: 1 }}>
//                                         Generated SQL
//                                     </Typography>
//                                     <Sheet variant="soft" sx={{ p: 1, borderRadius: 2, mt: 0.5, overflowX: "auto" }}>
//               <pre style={{ margin: 0 }}>
//                 <code>{selected.sql}</code>
//               </pre>
//                                     </Sheet>
//                                 </Box>
//
//                                 <Box>
//                                     <Sheet variant="outlined" sx={{ borderRadius: 2, overflow: "hidden" }}>
//                                         <AspectRatio ratio="16/9">
//                                             <img src={selected.thumbUrl} alt="full" />
//                                         </AspectRatio>
//                                     </Sheet>
//
//                                     <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap", mt: 1 }}>
//                                         {selected.tags.map((t) => (
//                                             <Chip key={t} variant="outlined" onClick={() => setQuery(t)}>
//                                                 {t}
//                                             </Chip>
//                                         ))}
//                                     </Box>
//
//                                     <Box sx={{ display: "flex", gap: 0.5, mt: 1, justifyContent: "flex-end" }}>
//                                         <Button variant="outlined" startDecorator={<ReplayRoundedIcon />}>
//                                             Re-run (mock)
//                                         </Button>
//                                         <Button color="danger" variant="outlined" startDecorator={<DeleteSweepRoundedIcon />}>
//                                             Delete (mock)
//                                         </Button>
//                                     </Box>
//                                 </Box>
//                             </Box>
//                         )}
//                     </Box>
//                 </ModalDialog>
//             </Modal>
//         </Box>
//     );
// }
