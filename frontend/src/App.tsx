// JoyOrderDashboardTemplate.tsx
import * as React from "react";
import Box from "@mui/joy/Box";
import Breadcrumbs from "@mui/joy/Breadcrumbs";
import CssBaseline from "@mui/joy/CssBaseline";
import GlobalStyles from "@mui/joy/GlobalStyles";
import Link from "@mui/joy/Link";
import { CssVarsProvider, useColorScheme } from "@mui/joy/styles";
import Typography from "@mui/joy/Typography";
import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";
import HomeRoundedIcon from "@mui/icons-material/HomeRounded";
import Header from "components/joy/Header";
import Sidebar from "components/joy/Sidebar";
import { Outlet, useLocation } from "react-router";
import menu from "./config/menu";
import bgUrl from "assets/wave_green.svg?url";
import Footer from "components/joy/Footer.tsx";

const BRAND = {
    red: "#E0081F",
    blue: "#005A9B",
    dark: "#0F1720",
    dark2: "#0B1119",
} as const;

const MAIN_HEIGHT = "90dvh";

const Background = React.memo(function Background({ isDark }: { isDark: boolean }) {
    const bgImages = React.useMemo(
        () =>
            isDark
                ? [
                    `url(${bgUrl})`,
                    `radial-gradient(1100px 700px at 0% 0%, rgba(224,8,31,0.12) 0%, transparent 60%)`,
                    `radial-gradient(1100px 700px at 100% 100%, rgba(0,90,155,0.12) 0%, transparent 60%)`,
                    `linear-gradient(180deg, ${BRAND.dark} 0%, ${BRAND.dark2} 100%)`,
                ]
                : [`url(${bgUrl})`],
        [isDark]
    );

    const bgRepeat = isDark ? "no-repeat, no-repeat, no-repeat, no-repeat" : "no-repeat";
    const bgSize = isDark ? "cover, 1100px 700px, 1100px 700px, cover" : "cover";
    const bgPos = isDark ? "center, 0% 0%, 100% 100%, center" : "center";
    const bgBlend = isDark ? "overlay, screen, screen, normal" : "normal";

    return (
        <Box
            role="presentation"
            aria-hidden
            sx={{
                position: "fixed",
                inset: 0,
                zIndex: 0,
                pointerEvents: "none",
                backgroundImage: bgImages.join(", "),
                backgroundRepeat: bgRepeat,
                backgroundSize: bgSize,
                backgroundPosition: bgPos,
                backgroundBlendMode: bgBlend,
                "&::before": {
                    content: '""',
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    height: 3,
                    background: `linear-gradient(90deg, ${BRAND.red}, ${BRAND.blue})`,
                },
                "&::after": {
                    content: '""',
                    position: "absolute",
                    inset: 0,
                    pointerEvents: "none",
                    opacity: isDark ? 0.06 : 0.03,
                },
            }}
        />
    );
});


export default function JoyOrderDashboardTemplate() {
    return (
        <CssVarsProvider defaultMode="system" disableTransitionOnChange>
            <CssBaseline />
            <InnerApp />
        </CssVarsProvider>
    );
}

function InnerApp() {
    const { mode } = useColorScheme();
    const isDark = mode === "dark";

    const location = useLocation();
    const currentUrl = location.pathname || "";

    const currentMenuName = React.useMemo(() => {
        const item = menu.items.find((it) => it.link.includes(currentUrl));
        return item?.name ?? "";
    }, [currentUrl]);

    return (
        <>
            <GlobalStyles
                styles={{
                    "*": { WebkitTapHighlightColor: "transparent" },
                    "::selection": {
                        background: isDark ? "rgba(224,8,31,0.35)" : "rgba(0,90,155,0.2)",
                        color: "#fff",
                    },
                }}
            />

            <Background isDark={isDark} />

            <Box sx={{ display: "flex", height: MAIN_HEIGHT, px: 0, position: "relative", zIndex: 1 }}>
                <Header />
                <Sidebar />

                <Box
                    aria-hidden
                    sx={{
                        width: { xs: 0, md: "var(--app-sidebar-current)" },
                        flexShrink: 0,
                        transition: "width .25s ease",
                    }}
                />

                <Box
                    component="main"
                    className="MainContent"
                    sx={{
                        position: "relative",
                        flex: 1,
                        display: "flex",
                        flexDirection: "column",
                        minWidth: 0,
                        height: MAIN_HEIGHT,
                        pt: { xs: "calc(12px + var(--Header-height))", sm: "calc(12px + var(--Header-height))", md: 3 },
                        px: { xs: 2, md: 6 },
                        pb: { xs: 2, sm: 2, md: 0 },
                        background: "transparent",
                    }}
                >
                    <Box
                        sx={{
                            flex: 1,
                            display: "flex",
                            flexDirection: "column",
                            gap: 1,
                            borderRadius: 2,
                            border: "0px solid",
                            bgcolor: isDark ? "rgba(255 255 255 / 0.04)" : "transparent",
                            p: { xs: 1.5, md: 2 },
                        }}
                    >
                        <Box sx={{ display: "flex", alignItems: "center" }}>
                            <Breadcrumbs
                                size="sm"
                                aria-label="breadcrumbs"
                                separator={
                                    <ChevronRightRoundedIcon
                                        fontSize="small"
                                        sx={{ color: isDark ? "text.tertiary" : "rgba(0,0,0,0.5)" }}
                                    />
                                }
                                sx={{
                                    pl: 0,
                                    fontSize: 14,
                                    fontWeight: 500,
                                    mb: 1,
                                    color: "text.primary",
                                }}
                            >
                                <Link underline="none" sx={{ color: "inherit" }} href="/" aria-label="HOME">
                                    <HomeRoundedIcon sx={{ color: "inherit" }} />
                                </Link>
                                <Typography level="body-xs" sx={{ color: "text.secondary", fontWeight: 500 }}>
                                    {currentMenuName}
                                </Typography>
                            </Breadcrumbs>
                        </Box>

                        <Box sx={{ flex: 1, minHeight: 0 }}>
                            <Outlet />
                        </Box>
                    </Box>
                </Box>

            </Box>
        </>
    );
}
