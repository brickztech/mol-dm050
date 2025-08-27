import * as React from "react";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { Box, IconButton, Sheet, Tooltip, Typography } from "@mui/joy";
import { useColorScheme } from "@mui/joy/styles";
import copy from "copy-to-clipboard";
import type { MessageSender } from "src/pages/chat";

type Props = {
    sender: MessageSender;
    message: string | React.ReactNode;
    hideCopy?: boolean;
    isHtml?: boolean;
    compact?: boolean;
};

const TINT = {
    user: "rgba(0,90,155,0.10)",
    asst: "rgba(224,8,31,0.08)",
};

const isHtmlLike = (s: string) => /<\/?[a-z][\s\S]*>/i.test(s);

export default function SimpleChatBubble({
                                             sender,
                                             message,
                                             hideCopy,
                                             isHtml,
                                             compact,
                                         }: Props) {
    const { mode } = useColorScheme();
    const isDark = mode === "dark";
    const isUser = String(sender).toLowerCase() === "user";
    const tint = isUser ? TINT.user : TINT.asst;

    const handleCopy = React.useCallback(() => {
        let txt = "";
        if (typeof message === "string") txt = message;
        else if (React.isValidElement(message)) {
            const c = (message as any)?.props?.children ?? "";
            txt = typeof c === "string" ? c : String(c ?? "");
        } else txt = String(message ?? "");
        if (!txt.trim()) return;
        copy(txt);
    }, [message]);

    const body = React.useMemo(() => {
        if (typeof message === "string") {
            if (isHtml || isHtmlLike(message)) {
                return (
                    <Box
                        sx={{ color: "text.primary", whiteSpace: "pre-wrap", wordBreak: "break-word" }}
                        dangerouslySetInnerHTML={{ __html: message }}
                    />
                );
            }
            return (
                <Typography level="body-sm" sx={{ color: "text.primary", whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                    {message}
                </Typography>
            );
        }
        return <Box sx={{ color: "text.primary" }}>{message}</Box>;
    }, [message, isHtml]);

    return (
        <Box sx={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", my: 1.25 }}>
            <Sheet
                variant="plain"
                sx={{
                    position: "relative",
                    width: "100%",
                    maxWidth: { xs: "96%", sm: 900 },
                    px: compact ? 1.25 : { xs: 1.5, sm: 2 },
                    py: compact ? 1 : { xs: 1.1, sm: 1.35 },
                    borderRadius: compact ? 10 : 15,
                    overflow: "hidden",
                    boxSizing: "border-box",

                    background:
                        "linear-gradient(0deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.06) 100%), rgba(29,29,29,0.06)",
                    backgroundBlendMode: "normal, color-burn",
                    backdropFilter: "blur(8px) saturate(110%)",
                    WebkitBackdropFilter: "blur(8px) saturate(110%)",
                    borderTop: `1px solid rgba(255,255,255,${isDark ? 0.18 : 0.28})`,
                    borderLeft: `1px solid rgba(255,255,255,${isDark ? 0.18 : 0.28})`,

                    boxShadow:
                        "-2px -2px 1px -3px rgba(255,255,255,0.35) inset, " +
                        "2px 2px 1px -3px rgba(255,255,255,0.35) inset, " +
                        "2px 3px 1px -2px rgba(179,179,179,0.14) inset, " +
                        "-2px -3px 1px -2px rgba(179,179,179,0.14) inset",

                    "&::before": {
                        content: '""',
                        position: "absolute",
                        inset: 0,
                        backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(
                            `<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120' preserveAspectRatio='none'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2' stitchTiles='stitch'/></filter><rect width='120' height='120' filter='url(#n)' opacity='0.06'/></svg>`
                        )}")`,
                        backgroundSize: "120px 120px",
                        opacity: 0.25,
                        mixBlendMode: "overlay",
                        pointerEvents: "none",
                    },
                    "&::after": {
                        content: '""',
                        position: "absolute",
                        inset: 0,
                        background: tint,
                        mixBlendMode: "soft-light",
                        opacity: 0.9,
                        pointerEvents: "none",
                    },
                    "@supports not ((-webkit-backdrop-filter: none) or (backdrop-filter: none))": {
                        background: isDark ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.82)",
                        backgroundBlendMode: "normal",
                    },
                    "&:hover .copy-btn": { opacity: 1 },
                }}
            >
                {!hideCopy && (
                    <Tooltip title="Copy" variant="plain">
                        <IconButton
                            size="sm"
                            variant="plain"
                            className="copy-btn"
                            onClick={handleCopy}
                            sx={{
                                position: "absolute",
                                top: 6,
                                right: 6,
                                opacity: 0,
                                transition: "opacity .15s ease",
                                borderRadius: 8,
                                backdropFilter: "blur(3px)",
                            }}
                        >
                            <ContentCopyIcon fontSize="small" />
                        </IconButton>
                    </Tooltip>
                )}
                {body}
            </Sheet>
        </Box>
    );
}
