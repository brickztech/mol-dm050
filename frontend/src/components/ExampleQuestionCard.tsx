import * as React from "react";
import { Card, Typography, Box } from "@mui/joy";
import { useTheme, useColorScheme } from "@mui/joy/styles";
import ArrowRightAltRoundedIcon from "@mui/icons-material/ArrowRightAltRounded";

type Props = {
    title: string;
    onClick: () => void;
    sx?: React.ComponentProps<typeof Card>["sx"];
};

export default function ExampleQuestionCard({ title, onClick, sx }: Props) {
    const theme = useTheme();
    const { mode } = useColorScheme();
    const isDark = mode === "dark";

    const onKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onClick();
        }
    };

    return (
        <Card
            role="button"
            tabIndex={0}
            aria-label={`Example: ${title}`}
            onClick={onClick}
            onKeyDown={onKeyDown}
            variant="plain"
            sx={{
                cursor: "pointer",
                p: 1.5,
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                borderRadius: 15,
                overflow: "hidden",
                boxSizing: "border-box",
                position: "relative",

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

                    backgroundSize: "120px 120px",
                    opacity: 0.22,
                    mixBlendMode: "overlay",
                    pointerEvents: "none",
                },

                transition:
                    "transform .18s ease, box-shadow .18s ease, background-color .18s ease",
                "&:hover": {
                    transform: "translateY(-3px) scale(1.015)",
                    boxShadow: isDark
                        ? "0 10px 24px rgba(0,0,0,0.45)"
                        : "0 10px 24px rgba(0,0,0,0.15)",

                    "&::after": {
                        content: '""',
                        position: "absolute",
                        inset: 0,
                        background:
                            "linear-gradient(180deg, rgba(0,90,155,0.06), rgba(224,8,31,0.04))",
                        mixBlendMode: "soft-light",
                        pointerEvents: "none",
                    },
                },
                "&:active": {
                    transform: "translateY(-1px) scale(1.01)",
                    boxShadow: isDark
                        ? "0 6px 16px rgba(0,0,0,0.40)"
                        : "0 6px 16px rgba(0,0,0,0.12)",
                },


                "&:focus-visible": {
                    outline: "none",
                    boxShadow:
                        "0 0 0 3px rgba(0,90,155,.35), 0 0 0 6px rgba(224,8,31,.2)",
                },


                "@supports not ((-webkit-backdrop-filter: none) or (backdrop-filter: none))": {
                    background: isDark
                        ? "rgba(255,255,255,0.06)"
                        : "rgba(255,255,255,0.86)",
                    backgroundBlendMode: "normal",
                },

                ...sx,
            }}
        >
            <Typography
                level="title-sm"
                sx={{
                    mb: 0.75,
                    display: "-webkit-box",
                    overflow: "hidden",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                }}
            >
                {title}
            </Typography>

            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                <Typography level="body-xs" sx={{ color: "text.tertiary" }}>
                    Try this
                </Typography>
                <ArrowRightAltRoundedIcon fontSize="small" sx={{ opacity: 0.8 }} />
            </Box>
        </Card>
    );
}
