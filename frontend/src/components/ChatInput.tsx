import React, { useCallback } from "react";
import { Box, IconButton, Sheet, Textarea, Tooltip, Typography } from "@mui/joy";
import SendRoundedIcon from "@mui/icons-material/SendRounded";
import StopRoundedIcon from "@mui/icons-material/StopRounded";

export default function ChatInput({
                                      input,
                                      setInput,
                                      isLoading,
                                      handleSend,
                                      handleStop,
                                      textareaRef,
                                  }: {
    input: string;
    setInput: (v: string) => void;
    isLoading: boolean;
    handleSend: () => void;
    handleStop: () => void;
    textareaRef: React.RefObject<HTMLDivElement>;
}) {
    const onKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
            if (e.key === "Enter" && !e.shiftKey && !isLoading) {
                e.preventDefault();
                handleSend();
            }
        },
        [handleSend, isLoading]
    );

    return (
        <Sheet variant="outlined" sx={{ bottom: 0, flexShrink: 0, borderRadius: 2, p: 2, bgcolor: "transparent", border: 0, boxShadow: 0 }}>
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
                    sx={{
                        "--Textarea-radius": "40px",
                        bgcolor: "transparent",
                        paddingRight: "48px",
                        "&::before": { display: "none" },
                    }}
                />

                <Tooltip title={isLoading ? "Stop" : "Send"} placement="top" variant="soft">
          <span>
            <IconButton
                size="sm"
                variant="plain"
                onClick={isLoading ? handleStop : handleSend}
                disabled={!input.trim() && !isLoading}
                sx={{
                    position: "absolute",
                    right: 6,
                    bottom: 6,
                    width: 32,
                    height: 32,
                    borderRadius: 2,
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
    );
}
