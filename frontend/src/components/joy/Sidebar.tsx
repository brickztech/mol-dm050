// components/Sidebar.tsx
import * as React from "react";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router";
import {
    Avatar,
    Box,
    Divider,
    GlobalStyles,
    IconButton,
    List,
    ListItem,
    ListItemButton,
    listItemButtonClasses,
    ListItemContent,
    Sheet,
    Tooltip,
    Typography,
} from "@mui/joy";
import { useColorScheme } from "@mui/joy/styles";
import MenuIcon from "@mui/icons-material/Menu";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import DarkModeRoundedIcon from "@mui/icons-material/DarkModeRounded";
import LightModeRoundedIcon from "@mui/icons-material/LightModeRounded";
import Logo from "~/assets/MOL_Group.png";
import menu from "~/config/menu";
import { closeSidebar } from "~/utils";
import LiquidGlass from "components/LiquidGlass.tsx";

function LiquidGlassBackground({
                                   radius = 12,
                                   opacity = 1,
                                   sx,
                               }: { radius?: number; opacity?: number; sx?: any }) {
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

                // Frosted panel base
                background:
                    "linear-gradient(0deg, rgba(255, 255, 255, 0.10) 0%, rgba(255, 255, 255, 0.10) 100%), rgba(29, 29, 29, 0.10)",
                backgroundBlendMode: "normal, color-burn",
                opacity,

                backdropFilter: "blur(12px) saturate(120%)",
                WebkitBackdropFilter: "blur(12px) saturate(120%)",

                // Subtle etched edges
                borderTop: `1px solid rgba(255, 255, 255, ${isDark ? 0.28 : 0.40})`,
                borderLeft: `1px solid rgba(255, 255, 255, ${isDark ? 0.28 : 0.40})`,

                // Inset glow/shading
                boxShadow:
                    "-2.5px -4.5px 1.5px -5.25px rgba(255, 255, 255, 0.50) inset, " +
                    "2.5px 2.5px 1.5px -3.25px rgba(255, 255, 255, 0.50) inset, " +
                    "3px 4.5px 1.5px -3px rgba(179, 179, 179, 0.20) inset, " +
                    "-3px -4.5px 1.5px -3px rgba(179, 179, 179, 0.20) inset, " +
                    "0 0 33px 0 rgba(242, 242, 242, 0.50) inset",

                "@supports not ((-webkit-backdrop-filter: none) or (backdrop-filter: none))": {
                    background: isDark ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.80)",
                    backgroundBlendMode: "normal",
                },

                ...sx,
            }}
        />
    );
}

const OPEN_WIDTH_MD = "220px";
const OPEN_WIDTH_LG = "240px";
const COLLAPSED_WIDTH = "70px";
const BRAND_BLUE = "#005A9B";
const BRAND_RED = "#E0081F";

const BRAND_BLUE_SUBTLE = "rgba(0,90,155,0.66)";
const BRAND_RED_SUBTLE = "rgba(224,8,31,0.66)";

interface SidebarProps {
    defaultExpanded?: boolean;
}

export default function Sidebar({ defaultExpanded = false }: SidebarProps) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);
    const navigate = useNavigate();
    const location = useLocation();
    const currentPath = location.pathname;
    const { mode, setMode } = useColorScheme();

    useEffect(() => {
        const width = isExpanded ? OPEN_WIDTH_MD : COLLAPSED_WIDTH;
        document.documentElement.style.setProperty("--app-sidebar-current", width);
    }, [isExpanded]);

    const toggleExpanded = () => setIsExpanded((v) => !v);

    return (
        <>
            <Sheet
                component="nav"
                aria-label="Primary"
                sx={{
                    position: { xs: "fixed", md: "fixed" },
                    inset: { xs: "0 auto 0 0", md: "0 auto 0 0" },
                    zIndex: 10000,
                    height: "100dvh",
                    width: "var(--Sidebar-width)",
                    flexShrink: 0,
                    display: "flex",
                    flexDirection: "column",
                    gap: 1.5,
                    p: 2,
                    bgcolor: "transparent",
                    border: 0,
                    overflow: "hidden",

                    boxShadow: mode === "dark"
                        ? "0 12px 12px rgba(0,0,0,0.45)"
                        : "0 16px 12px rgba(0,0,0,0.12)",

                    "&::before": {
                        content: '""',
                        position: "absolute",
                        top: 0,
                        left: 0,
                        right: 0,
                        height: 3,
                        zIndex: 1,
                        background: `linear-gradient(90deg, ${BRAND_RED}, ${BRAND_BLUE})`,
                        pointerEvents: "none",
                    },

                    transition: "transform .3s ease, width .25s ease",
                    transform: {
                        xs: "translateX(calc(100% * (var(--SideNavigation-slideIn, 0) - 1)))",
                        md: "none",
                    },
                }}
            >
                <LiquidGlass opacity={0.8} radius={0}  sx={{ zIndex: 0 }} />

                <GlobalStyles
                    styles={(theme) => ({
                        ":root": {
                            "--Sidebar-width": isExpanded ? OPEN_WIDTH_MD : COLLAPSED_WIDTH,
                            "--app-sidebar-current": isExpanded ? OPEN_WIDTH_MD : COLLAPSED_WIDTH,
                            [theme.breakpoints.up("lg")]: {
                                "--Sidebar-width": isExpanded ? OPEN_WIDTH_LG : COLLAPSED_WIDTH,
                            },
                        },
                    })}
                />

                <Box
                    className="Sidebar-overlay"
                    sx={{
                        position: "fixed",
                        zIndex: 9998,
                        top: 0,
                        left: 0,
                        width: "100vw",
                        height: "100vh",
                        opacity: "var(--SideNavigation-slideIn)",
                        backgroundColor: "var(--joy-palette-background-backdrop)",
                        transition: "opacity .3s",
                        transform: {
                            xs: "translateX(calc(100% * (var(--SideNavigation-slideIn, 0) - 1) + var(--SideNavigation-slideIn, 0) * var(--Sidebar-width, 0px)))",
                            lg: "translateX(-100%)",
                        },
                    }}
                    onClick={() => closeSidebar()}
                />

                <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 0.5, zIndex: 2 }}>
                    <Box sx={{ display: "flex", alignItems: "center", overflow: "hidden", gap: 1, }}>
                        <img src={Logo} alt="MOL logo" style={{ height: 32, display: "block" }} />
                    </Box>

                    <Box sx={{ display: "flex", gap: 0.5 }}>
                        <IconButton
                            onClick={toggleExpanded}
                            variant="outlined"
                            size="md"
                            aria-label={isExpanded ? "Collapse sidebar" : "Expand sidebar"}
                            aria-expanded={isExpanded}
                            sx={{
                                borderRadius: 10,
                                backgroundColor: mode === "dark" ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.8)",
                                backdropFilter: "blur(6px)",
                                "&:focus-visible": { outline: `2px solid ${BRAND_BLUE}66` },
                                left: -2,
                            }}
                        >
                            <MenuIcon sx={{ fontSize: 18 }} />
                        </IconButton>
                    </Box>
                </Box>

                <Box
                    sx={{
                        minHeight: 0,
                        overflow: "hidden auto",
                        flexGrow: 1,
                        display: "flex",
                        flexDirection: "column",
                        zIndex: 2,
                        [`& .${listItemButtonClasses.root}`]: {
                            gap: 1,
                            alignItems: "center",
                            minHeight: 40,
                            borderRadius: 10,
                            px: 1,
                            "&:hover": {
                                backgroundColor: mode === "dark" ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.04)",
                                transform: "translateX(1px)",
                            },
                            "&.Mui-selected": {
                                background: mode === "dark" ? BRAND_RED_SUBTLE : BRAND_BLUE_SUBTLE,
                                boxShadow: `inset 2px 0 0 ${BRAND_BLUE}`,
                                color:"#fff",


                            },
                        },
                        "& .nav-icon": {
                            display: "grid",
                            placeItems: "center",
                            width: 28,
                            height: 28,
                            flexShrink: 0,
                            opacity: 0.92,
                        },
                    }}
                >
                    <List
                        size="sm"
                        sx={{
                            gap: 0.5,
                            "--List-nestedInsetStart": "30px",
                            "--ListItem-radius": (theme) => theme.vars.radius.sm,
                        }}
                    >
                        {menu.items.map((item) => {
                            const selected = item.link.includes(currentPath);
                            const Icon = item.icon;

                            const button = (
                                <ListItemButton
                                    selected={selected}
                                    onClick={() => navigate(item.link[0])}
                                    sx={{ color: "inherit", backgroundColor: "transparent" }}
                                >
                                    <Box className="nav-icon">
                                        <Icon sx={{ fontSize: 20 }} />
                                    </Box>
                                    <ListItemContent sx={{ display: isExpanded ? "block" : "none" }}>
                                        <Typography level="title-sm" fontWeight={500} textColor={selected ? "#fff"  : "inherit"}>
                                            {item.name}
                                        </Typography>
                                    </ListItemContent>
                                </ListItemButton>
                            );

                            return (
                                <ListItem key={item.name} sx={{ px: 0.5 }}>
                                    {isExpanded ? (
                                        button
                                    ) : (
                                        <Tooltip title={item.name} placement="right" variant="soft">
                                            {button}
                                        </Tooltip>
                                    )}
                                </ListItem>
                            );
                        })}
                    </List>
                </Box>

                <Divider sx={{ my: 0.5, opacity: mode === "dark" ? 0.2 : 0.25, zIndex: 2 }} />

                <Box sx={{ zIndex: 2 }}>
                    <IconButton
                        size="sm"
                        variant="soft"
                        onClick={() => setMode(mode === "dark" ? "light" : "dark")}
                        aria-label="Toggle color scheme"
                        sx={{ borderRadius: 10 }}
                    >
                        {mode === "dark" ? <LightModeRoundedIcon fontSize="small" /> : <DarkModeRoundedIcon fontSize="small" />}
                    </IconButton>
                </Box>

                <Box sx={{ display: "flex", alignItems: "center", gap: 1, zIndex: 2 }}>
                    <Avatar
                        variant="outlined"
                        size="sm"
                        src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=286"
                    />
                    <Box sx={{ minWidth: 0, flex: 1, overflow: "hidden", display: isExpanded ? "block" : "none" }}>
                        <Typography level="title-sm">Mol Employee</Typography>
                        <Typography level="body-xs" sx={{ opacity: 0.8 }}>
                            employee@molgroup.com
                        </Typography>
                    </Box>
                    {isExpanded ? (
                        <IconButton size="sm" variant="plain" color="neutral" aria-label="Log out">
                            <LogoutRoundedIcon />
                        </IconButton>
                    ) : null}
                </Box>
            </Sheet>
        </>
    );
}
