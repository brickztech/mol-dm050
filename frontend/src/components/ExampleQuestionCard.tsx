// components/ExampleQuestionCard.tsx
import * as React from "react";
import { Card, Typography, Box } from "@mui/joy";
import { useTheme } from "@mui/joy/styles";
import ArrowRightAltRoundedIcon from "@mui/icons-material/ArrowRightAltRounded";

type Props = {
    title: string;
    onClick: () => void;
    sx?: React.ComponentProps<typeof Card>["sx"]; // 👈 allow custom sizing from parent
};

export default function ExampleQuestionCard({ title, onClick, sx }: Props) {
    const theme = useTheme();

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
            onClick={onClick}
            onKeyDown={onKeyDown}
            variant="outlined"
            sx={{
                cursor: "pointer",
                p: 1.5,
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                borderRadius: 2,
                overflow: "hidden",

                bgcolor: "background.surface",
                transition:
                    "transform .2s ease, box-shadow .2s ease, background-color .2s ease",
                "&:hover": {
                    bgcolor: "background.level1",
                    transform: "translateY(-3px) scale(1.02)",
                    boxShadow: "0 6px 16px rgba(0, 90, 155, 0.18)",
                },
                "&:active": {
                    transform: "translateY(-1px) scale(1.01)",
                    boxShadow: "0 4px 12px rgba(0, 90, 155, 0.12)",
                },
                [theme.getColorSchemeSelector("dark")]: {
                    bgcolor: "rgba(255 255 255 / 0.06)",
                    "&:hover": {
                        bgcolor: "rgba(255 255 255 / 0.10)",
                        boxShadow: "0 6px 16px rgba(0,0,0,0.45)",
                    },
                    "&:active": { boxShadow: "0 4px 12px rgba(0,0,0,0.4)" },
                },
                "&:focus-visible": {
                    outline: "none",
                    boxShadow:
                        "0 0 0 3px rgba(0,90,155,.35), 0 0 0 6px rgba(224,8,31,.2)",
                },
                ...sx,
            }}
            aria-label={`Example: ${title}`}
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
