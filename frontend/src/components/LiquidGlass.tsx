import * as React from "react";
import { Box } from "@mui/joy";
import { useColorScheme } from "@mui/joy/styles";

type Props = {
    radius?: number;
    opacity?: number;
    sx?: any;
};

export default function LiquidGlass({
                                        radius = 48,
                                        opacity = 1,
                                        sx,
                                    }: Props) {
    const { mode } = useColorScheme();
    const isDark = mode === "dark";

    return (
        <Box
            aria-hidden
            sx={{
                position: "absolute",
                inset: 0,
                borderRadius: radius,
                overflow: "hidden",
                pointerEvents: "none",
                opacity,

                background: isDark
                    ? "linear-gradient(0deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.06) 100%), rgba(29,29,29,0.06)"
                    : "linear-gradient(0deg, rgba(0,0,0,0.08) 0%, rgba(0,0,0,0.08) 100%), rgba(255,255,255,0.65)",
                backgroundBlendMode: isDark ? "normal, color-burn" : "multiply, normal",

                backdropFilter: "blur(20px) saturate(220%)",
                WebkitBackdropFilter: "blur(20px) saturate(220%)",

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
                    opacity: 0.25,
                    mixBlendMode: "overlay",
                    pointerEvents: "none",
                },

                "@supports not ((-webkit-backdrop-filter: none) or (backdrop-filter: none))": {
                    background: isDark
                        ? "rgba(255,255,255,0.06)"
                        : "rgba(255,255,255,0.82)",
                    backgroundBlendMode: "normal",
                },

                ...sx,
            }}
        />
    );
}
