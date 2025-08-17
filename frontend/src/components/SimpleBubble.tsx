import * as React from "react";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { Box, IconButton, Sheet, Tooltip, Typography } from "@mui/joy";
import copy from "copy-to-clipboard";
import type { MessageSender } from "src/pages/chat";

type Props = {
    sender: MessageSender;
    message: string | React.ReactNode;
    hideCopy?: boolean;
    isHtml?: boolean;
};

const BRAND = {
    asstBg: "rgba(224,8,31,0.09)",
    asstBorder: "rgba(224,8,31,0.45)",
    userBg: "rgba(0,90,155,0.09)",
    userBorder: "rgba(0,90,155,0.45)",
};

const isHtmlLike = (s: string) => /<\/?[a-z][\s\S]*>/i.test(s);

export default function SimpleChatBubble({ sender, message, hideCopy, isHtml }: Props) {
    const isUser = String(sender).toLowerCase() === "user";
    const bg = isUser ? BRAND.userBg : BRAND.asstBg;
    const border = isUser ? BRAND.userBorder : BRAND.asstBorder;


    const handleCopy = React.useCallback(() => {
        let txt = "";
        if (typeof message === "string") txt = message;
        else if (React.isValidElement(message)) {
            const c = message.props?.children ?? "";
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
        <Box sx={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", my: 1.5 }}>
            <Sheet
                variant="soft"
                sx={{
                    position: "relative",
                    width: "100%",
                    maxWidth: { xs: "96%", sm: 900 },
                    px: { xs: 1.5, sm: 2 },
                    py: { xs: 1.25, sm: 1.5 },
                    borderRadius: 2,
                    backgroundColor: bg,
                    backdropFilter: "blur(5px)",
                    boxShadow: "0 2px 10px rgba(0,0,0,0.2)",

                    borderBottom: `2px solid ${border}`,
                    borderColor: `${border}40`,
                    boxSizing: "border-box",
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
