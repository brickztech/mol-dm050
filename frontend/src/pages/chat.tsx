import React, { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import {
    Box,
    Button,
    LinearProgress,
    Textarea,
    Chip,
    Typography,
    Card,
    Sheet,
    Table,
    Input,
    Select,
    Option,
    FormControl,
    FormLabel,
    CircularProgress,
    linearProgressClasses,
    Tooltip,
    IconButton, Divider
} from "@mui/joy"; // +CircularProgress
import { AnimatePresence, motion } from "framer-motion";
import SimpleChatBubble from "src/components/SimpleBubble";
import { askQuestionStream } from "../api/api";
import MotionWrapper from "../components/MotionWrapper";
import { FullSizeCentered } from "../components/styled";
import "./style.css";
import SendRoundedIcon from "@mui/icons-material/SendRounded";
import StopRoundedIcon from "@mui/icons-material/StopRounded";
import DataTable from "src/components/DataTable.tsx";
import {
    brandGradient,
    generateId,
    looksLikeHtmlTable,
    parseHtmlMessageToSegments,
} from "src/components/htmlSegments";
import MolTriangleLoader from "components/MolTriangleLoader.tsx";
import {useLocation} from "react-router";
import ChatBubble from "src/components/ChatBubble.tsx";
export type MessageSender = "user" | "assistant";
export type TextFormat = "Text" | "Table" | "Json";
import EmojiObjectsRoundedIcon from "@mui/icons-material/EmojiObjectsRounded";
import TableChartRoundedIcon from "@mui/icons-material/TableChartRounded";
import AutoGraphRoundedIcon from "@mui/icons-material/AutoGraphRounded";
import QueryStatsRoundedIcon from "@mui/icons-material/QueryStatsRounded";
import HelpOutlineRoundedIcon from "@mui/icons-material/HelpOutlineRounded";

export interface Message {
    id: string;
    role: MessageSender;
    timestamp: number;
    content: string;
    format: TextFormat;
}

function useLiveRef<T>(value: T) {
    const ref = useRef(value);
    useEffect(() => { ref.current = value; }, [value]);
    return ref;
}

function useAutoScroll(dependsOn: unknown[]) {
    const endRef = useRef<HTMLDivElement | null>(null);
    const scrollToBottom = useCallback((smooth = true) => {
        endRef.current?.scrollIntoView({ behavior: smooth ? "smooth" : "auto" });
    }, []);
    useLayoutEffect(() => { scrollToBottom(true); }, dependsOn as any);
    return { endRef, scrollToBottom };
}

const MemoBubble = React.memo(function MemoBubble({ msg }: { msg: Message }) {
    const hasTable = msg.role === "assistant" && looksLikeHtmlTable(msg.content);
    const segments = React.useMemo(
        () => (hasTable ? parseHtmlMessageToSegments(msg.content) : []),
        [hasTable, msg.content]
    );
    if (hasTable) {
        return (
            <Card variant="soft" sx={{ p: 1.25, width: "100%" }}>
                {segments.map((seg, i) =>
                    seg.type === "text" ? (
                        <Typography key={`t-${i}`} level="body-sm" sx={{ mb: 1, whiteSpace: "pre-wrap" }}>
                            {seg.text}
                        </Typography>
                    ) : (
                        <Box key={`tbl-${i}`} sx={{ mb: 1 }}>
                            <Typography level="title-sm" sx={{ mb: 0.75 }}>Táblázatos eredmény</Typography>
                            <DataTable columns={seg.columns} rows={seg.rows} />
                        </Box>
                    )
                )}
            </Card>
        );
    }
    return (
        <Box sx={{ display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start", width: "100%" }}>
            <SimpleChatBubble sender={msg.role} message={msg.content} />
        </Box>
    );
});

function StreamingBubble({ role, content }: { role: MessageSender; content: string }) {
    return (
        <Box sx={{ display: "flex", justifyContent: role === "user" ? "flex-end" : "flex-start", width: "100%" }}>
            <SimpleChatBubble sender={role} message={content} />
        </Box>
    );
}

function FadingBlurLoader({
                              open,
                              size = 96,
                              blur = 14,
                              fadeMs = 260,
                          }: {
    open: boolean;
    size?: number;
    blur?: number;
    fadeMs?: number;
}) {

    return (
        <AnimatePresence>
            {open && (
                <motion.div
                    key="fullpage-blur-loader"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: fadeMs / 1000 }}
                    style={{
                        position: "fixed",
                        inset: 0,
                        zIndex: 9999,
                        display: "grid",
                        placeItems: "center",
                        backdropFilter: `blur(${blur}px)`,
                        WebkitBackdropFilter: `blur(${blur}px)`,
                        backgroundColor: "rgba(0,0,0,0.15)",
                    }}
                >
                        <Box
                            sx={{
                                position: "absolute",
                                inset: 0,
                                display: "grid",
                                placeItems: "center",
                            }}
                        >
                            <MolTriangleLoader
                                width={Math.round(size * 0.55)}
                                height={Math.round(size * 0.25)}
                                speed={1.8}
                            />
                        </Box>
                </motion.div>
            )}
        </AnimatePresence>
    );
}


function EmptyState({ onPick }: { onPick?: (text: string) => void }) {
    const example = (t: string) => () => onPick?.(t);

    return (
        <Box sx={{ display: "flex", justifyContent: "center", width: "100%", marginTop: 6 }}>
            <Sheet
                variant="outlined"
                sx={{
                    position: "relative",
                    width: "100%",

                    maxWidth: 920,
                    p: { xs: 1.5, sm: 2 },
                    borderRadius: 5,
                    borderColor: "neutral.outlinedBorder",
                    background:
                        "linear-gradient(180deg, rgba(0,90,155,0.06), rgba(0,90,155,0.03))",
                    boxShadow: "0 2px 10px rgba(0,0,0,0.04)",
                }}
            >
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Box
                        sx={{
                            width: 40,
                            height: 40,
                            borderRadius: "50%",
                            display: "grid",
                            placeItems: "center",
                            background:
                                "linear-gradient(135deg, rgba(0,90,155,.18), rgba(224,8,31,.18))",
                            border: "1px solid rgba(0,0,0,0.06)",
                        }}
                    >
                        <QueryStatsRoundedIcon sx={{height:22, width:22}}  />
                    </Box>
                    <Box sx={{ flex: 1 }}>
                        <Typography level="title-md" fontWeight="lg">
                            Text → SQL
                        </Typography>
                        <Typography level="body-sm" sx={{ opacity: 0.85 }}>
                            Ask in natural language — I’ll build SQL and provide the results.
                        </Typography>
                    </Box>
                </Box>

                {/* Examples */}
                <Box
                    sx={{
                        mt: 1.5,
                        display: "grid",
                        gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr 1fr" },
                        gap: 1,
                    }}
                >
                    <Sheet
                        variant="soft"
                        onClick={example(
                            "Top 10 customers by lifetime revenue this year, include total orders and last order date."
                        )}
                        sx={{
                            p: 1,
                            borderRadius: 10,
                            cursor: "pointer",
                            "&:hover": { boxShadow: "sm", transform: "translateY(-1px)" },
                            transition: "all .15s ease",
                        }}
                    >
                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
                            <AutoGraphRoundedIcon fontSize="small" />
                            <Typography level="body-sm" fontWeight="lg">
                                Top revenue customers
                            </Typography>
                        </Box>
                        <Typography level="body-xs" sx={{ mt: 0.5, opacity: 0.8 }}>
                            Includes total orders + last order date
                        </Typography>
                    </Sheet>

                    <Sheet
                        variant="soft"
                        onClick={example(
                            "Monthly sales by region for 2024, pivot as columns (regions) with totals."
                        )}
                        sx={{
                            p: 1,
                            borderRadius: 10,
                            cursor: "pointer",
                            "&:hover": { boxShadow: "sm", transform: "translateY(-1px)" },
                            transition: "all .15s ease",
                        }}
                    >
                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
                            <TableChartRoundedIcon fontSize="small" />
                            <Typography level="body-sm" fontWeight="lg">
                                Pivot by region
                            </Typography>
                        </Box>
                        <Typography level="body-xs" sx={{ mt: 0.5, opacity: 0.8 }}>
                            Month × Region with totals
                        </Typography>
                    </Sheet>

                    <Sheet
                        variant="soft"
                        onClick={example(
                            "Find orders delayed > 7 days between dispatch and delivery, show order id, customer, days delayed."
                        )}
                        sx={{
                            p: 1,
                            borderRadius: 10,
                            cursor: "pointer",
                            "&:hover": { boxShadow: "sm", transform: "translateY(-1px)" },
                            transition: "all .15s ease",
                        }}
                    >
                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
                            <EmojiObjectsRoundedIcon fontSize="small" />
                            <Typography level="body-sm" fontWeight="lg">
                                Delayed orders
                            </Typography>
                        </Box>
                        <Typography level="body-xs" sx={{ mt: 0.5, opacity: 0.8 }}>
                            Gap  7 days from dispatch to delivery
                        </Typography>
                    </Sheet>
                </Box>
                <Divider
                    sx={{
                        my: 2,
                        borderColor: "neutral.outlinedBorder",
                        width: "100%",
                        opacity: 0.6,
                    }}

                />
                <Box
                    sx={{
                        display: "grid",
                        gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
                        gap: 1,
                    }}
                >
                    <TipItem
                        icon={<HelpOutlineRoundedIcon fontSize="small" />}
                        title="Natural language"
                        text='Ask plainly: e.g. “Top 10 sales by region this quarter.”'
                    />
                    <TipItem
                        icon={<AutoGraphRoundedIcon fontSize="small" />}
                        title="Add constraints"
                        text='Use filters: “only electronics”, “after 2024-01-01”, “exclude test users”.'
                    />
                    <TipItem
                        icon={<TableChartRoundedIcon fontSize="small" />}
                        title="Shape the output"
                        text='Say “as a table”, “pivot by region”, or “grouped weekly with totals”.'
                    />
                    <TipItem
                        icon={<EmojiObjectsRoundedIcon fontSize="small" />}
                        title="Name fields"
                        text='Ask for columns: “customer, region, revenue, last_order_at”.'
                    />
                </Box>
            </Sheet>
        </Box>
    );
}

function TipItem({
                     icon,
                     title,
                     text,
                 }: {
    icon: React.ReactNode;
    title: string;
    text: string;
}) {
    return (
        <Box sx={{ display: "flex", gap: 0.75, alignItems: "flex-start" }}>
            <Box
                sx={{
                    width: 22,
                    height: 22,
                    borderRadius: "50%",
                    display: "grid",
                    placeItems: "center",
                    backgroundColor: "rgba(0,0,0,0.06)",
                    flex: "0 0 auto",
                }}
            >
                {icon}
            </Box>
            <Box sx={{ minWidth: 0 }}>
                <Typography level="body-sm" fontWeight="lg">
                    {title}
                </Typography>
                <Typography level="body-xs" sx={{ opacity: 0.8 }}>
                    {text}
                </Typography>
            </Box>
        </Box>
    );
}



export default function Text2SqlPageMol() {
    const [history, setHistory] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string>("");

    const [streamText, setStreamText] = useState<string>("");
    const isLoadingRef = useLiveRef(isLoading);
    const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array<any>> | null>(null);
    const { endRef, scrollToBottom } = useAutoScroll([history.length, streamText]);

    const location = useLocation();
    const textareaRef = React.useRef<HTMLTextAreaElement | null>(null);

    const hasStream = isLoading && streamText.length > 0;
    const streamHasTable = hasStream && looksLikeHtmlTable(streamText);
    const streamSegments = React.useMemo(
        () => (streamHasTable ? parseHtmlMessageToSegments(streamText) : []),
        [streamHasTable, streamText]
    );

    const addMessage = useCallback((msg: Message) => {
        setHistory((prev) => [...prev, msg]);
    }, []);

    const handleStop = useCallback(async () => {
        setIsLoading(false);
        try { await readerRef.current?.cancel?.(); } catch { /* noop */ }
        readerRef.current = null;
    }, []);

    useEffect(() => {
        const preset = (location.state as any)?.q as string | undefined;
        if (preset && typeof preset === "string") {
            setInput(preset);

            window.history.replaceState({}, "");
            textareaRef.current?.focus();
        }
    }, [location.state]);

    useEffect(() => () => { readerRef.current?.cancel?.().catch(() => {}); }, []);

    const handleSend = useCallback(async () => {
        if (!input.trim() || isLoadingRef.current) return;
        setError("");
        setIsLoading(true);

        const userMsg: Message = { id: generateId(), role: "user", content: input, timestamp: Date.now(), format: "Text" };
        setHistory((prev) => [...prev, userMsg]);

        const question = input;
        setInput("");
        const context = [...history, userMsg];

        try {
            const readerOrStream = await askQuestionStream(question, context);
            const reader: ReadableStreamDefaultReader<Uint8Array<any>> =
                typeof (readerOrStream as any)?.read === "function"
                    ? (readerOrStream as ReadableStreamDefaultReader<Uint8Array<any>>)
                    : (readerOrStream as ReadableStream<Uint8Array<any>>).getReader();

            readerRef.current = reader;
            setStreamText("");

            const decoder = new TextDecoder();
            let accum = "";

            while (true) {
                if (!isLoadingRef.current) break;
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                accum += chunk;
                setStreamText((prev) => prev + chunk);
            }

            if (accum.trim().length > 0) {
                addMessage({ id: generateId(), role: "assistant", content: accum, timestamp: Date.now(), format: "Text" });
                setStreamText("");
            }
        } catch (err: any) {
            setError(err?.message ?? "Unexpected error while streaming the answer.");
        } finally {
            setIsLoading(false);
            readerRef.current = null;
            scrollToBottom(true);
        }
    }, [addMessage, history, input, isLoadingRef, scrollToBottom]);

    const onKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey && !isLoading) {
            e.preventDefault();
            handleSend();
        }
    }, [handleSend, isLoading]);

    return (
        <MotionWrapper >
                    <Box
                        sx={{
                            display: "flex",
                            flex:1,
                            justifyContent: "center",
                            alignItems: "space-between",
                            width: "100%",
                            height: "85dvh",
                            p: "1rem",
                            position: "relative",
                            backgroundColor: "transparent",
                        }}
                    >
                        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, ease: "easeOut" }} style={{ width: "100%",  display: "flex", flexDirection: "column", gap: 2, flex:1 }}>
                                <Box
                                    className={isLoading ? "loading-border" : ""}
                                    sx={{
                                        position: "relative",
                                        flex: 1,
                                        display: "flex",
                                        flexDirection: "column",
                                        overflowY: "auto",
                                        p: 2,
                                        border: "none",

                                    }}
                                >
                                    {history.length === 0 && !isLoading && (
                                        <EmptyState onPick={(q) => setInput(q)} />
                                    )}
                                    <AnimatePresence initial={false} >
                                        {history.map((msg) => (
                                            <motion.div key={msg.id} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
                                                <MemoBubble msg={msg} />
                                            </motion.div>
                                        ))}
                                        {isLoading && (
                                            <motion.div key="streaming" initial={{ opacity: 0.6 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
                                                {streamText.length === 0 ? (
                                                    <>
                                                    <FadingBlurLoader open={isLoading} blur={10} fadeMs={1000} size={500}/>

                                                    </>

                                                ) : streamHasTable ? (
                                                    <Card variant="soft" sx={{ p: 1, width: "100%" }}>
                                                        {streamSegments.map((seg, i) =>
                                                            seg.type === "text" ? (
                                                                <Typography key={`ts-${i}`} level="body-sm" sx={{ mb: 1, whiteSpace: "pre-wrap" }}>
                                                                    {seg.text}
                                                                </Typography>
                                                            ) : (
                                                                <Box key={`tt-${i}`} sx={{ mb: 1 }}>
                                                                    <Typography level="title-sm" sx={{ mb: 0.75 }}>Táblázatos eredmény (stream)</Typography>
                                                                    <DataTable columns={seg.columns} rows={seg.rows} />
                                                                </Box>
                                                            )
                                                        )}
                                                    </Card>
                                                ) : (
                                                    <StreamingBubble role="assistant" content={streamText} />
                                                )}
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                    <div ref={endRef} style={{ height: 1 }} />
                                </Box>

                                {error && (
                                    <Box sx={{ border: "1px solid #990B1D", background: "rgba(224,8,31,0.08)", color: "#fff", borderRadius: 8, p: 1.25 }}>
                                        {error}
                                    </Box>
                                )}
                                <Sheet
                                    variant="outlined"
                                    sx={(theme) => ({
                                        bottom: 0,
                                        flexShrink: 0,
                                        borderRadius: 8,
                                        p: 0.75,
                                        backdropFilter: "blur(8px)",
                                        bgcolor: "background.surface",
                                        borderColor: "neutral.outlinedBorder",
                                        boxShadow: "md",
                                        [theme.getColorSchemeSelector("dark")]: {
                                            bgcolor: "rgba(255 255 255 / 0.05)",
                                        },
                                    })}
                                >
                                    <Box sx={{ position: "relative" }}>
                                        <Textarea
                                            ref={textareaRef}
                                            value={input}
                                            onChange={(e) => setInput(e.target.value)}
                                            onKeyDown={onKeyDown}
                                            disabled={isLoading}
                                            placeholder="Ask about your data…"
                                            aria-label="Ask about your data"
                                            variant="soft"
                                            color="neutral"
                                            minRows={1}
                                            maxRows={6}
                                            sx={(theme) => ({
                                                "--Textarea-radius": "8px",
                                                "--Textarea-paddingBlock": "10px",
                                                "--Textarea-paddingInline": "12px",
                                                "--Textarea-focusedInset": "0px",
                                                "--Textarea-focusedThickness": "2px",
                                                "--Textarea-placeholderColor": theme.vars.palette.text.tertiary,
                                                bgcolor: "background.level1",
                                                boxShadow: "sm",
                                                "& textarea": {
                                                    color: "text.primary",
                                                    fontFamily:
                                                        "Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif",
                                                    scrollbarWidth: "thin",
                                                },
                                            })}
                                        />
                                        <Tooltip title={isLoading ? "Stop" : "Send"} placement="top" variant="soft">
                                          <span>
                                            <IconButton
                                                size="sm"
                                                variant="solid"
                                                color={isLoading ? "danger" : "primary"}  // ✅ use Joy palette keys
                                                onClick={isLoading ? handleStop : handleSend}
                                                disabled={!input.trim() && !isLoading}
                                                sx={{
                                                    position: "absolute",
                                                    right: 6,
                                                    bottom: 6,
                                                    width: 32,
                                                    height: 32,
                                                    borderRadius: 8,
                                                    boxShadow: "sm",
                                                }}
                                            >
                                              {isLoading ? <StopRoundedIcon /> : <SendRoundedIcon />}
                                            </IconButton>
                                          </span>
                                        </Tooltip>
                                    </Box>
                                    <Typography level="body-xs" sx={{ mt: 0.5, opacity: 0.65, px: 0.5 }}>
                                        Press <kbd>Enter</kbd> to send • <kbd>Shift</kbd>+<kbd>Enter</kbd> for newline
                                    </Typography>
                                </Sheet>

                        </motion.div>
                    </Box>
        </MotionWrapper>

    );
}
