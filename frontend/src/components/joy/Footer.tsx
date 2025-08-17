import * as React from "react";
import {
    Box,
    Sheet,
    Typography,
    IconButton,
    Input,
    Button,
    Divider,
    Select,
    Option,
} from "@mui/joy";

import LanguageRoundedIcon from "@mui/icons-material/LanguageRounded";
import ArrowUpwardRoundedIcon from "@mui/icons-material/ArrowUpwardRounded";
import MailRoundedIcon from "@mui/icons-material/MailRounded";

type Props = {
    logoSrc?: string; // optional brand logo
    onSubscribe?: (email: string) => void; // newsletter shown only if provided
    languages?: { code: string; label: string }[];
    bgWaveUrl?: string; // optional background SVG
    tagline?: string; // optional custom tagline
};

const BRAND = {
    red: "#E0081F",
    blue: "#005A9B",
    dark: "#0F1720",
    lightText: "rgba(255,255,255,0.88)",
    dimText: "rgba(255,255,255,0.65)",
};

export default function Footer({
                                   logoSrc,
                                   onSubscribe,
                                   languages = [
                                       { code: "en", label: "English" },
                                       { code: "hu", label: "Magyar" },
                                   ],
                                   bgWaveUrl,
                                   tagline = "Data, decisions, and energy at scale.",
                               }: Props) {
    const [email, setEmail] = React.useState("");
    const [lang, setLang] = React.useState(languages[0]?.code ?? "en");

    return (
        <Sheet
            component="footer"
            role="contentinfo"
            aria-label="Footer"
            variant="solid"
            color="neutral"
            sx={{
                position: "relative",
                mt: 4,
                bgcolor: BRAND.dark,
                color: BRAND.lightText,
                overflow: "hidden",
                // slim gradient accent bar
                "&::before": {
                    content: '""',
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    height: 2,
                    background: `linear-gradient(90deg, ${BRAND.red}, ${BRAND.blue})`,
                },
                // optional decorative wave
                ...(bgWaveUrl
                    ? {
                        backgroundImage: `url(${bgWaveUrl})`,
                        backgroundRepeat: "no-repeat",
                        backgroundSize: "cover",
                        backgroundPosition: "center",
                        "&::after": {
                            content: '""',
                            position: "absolute",
                            inset: 0,
                            background:
                                "radial-gradient(80% 60% at 20% -10%, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0) 60%)",
                            pointerEvents: "none",
                        },
                    }
                    : {}),
            }}
        >
            {/* Content container */}
            <Box
                sx={{
                    maxWidth: 1200,
                    mx: "auto",
                    px: { xs: 2, md: 3 },
                    py: { xs: 3, md: 4 },
                    display: "grid",
                    gap: 2,
                }}
            >
                {/* Brand + tagline */}
                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        flexWrap: "wrap",
                        mb: 0.5,
                    }}
                >
                    {logoSrc ? (
                        <img
                            src={logoSrc}
                            alt="MOL Group"
                            style={{
                                height: 22,
                                objectFit: "contain",
                                filter: "brightness(1) contrast(1.1)",
                            }}
                        />
                    ) : (
                        <Typography level="title-lg" sx={{ fontWeight: 800 }}>
                            MOL Group
                        </Typography>
                    )}
                    <Typography level="body-sm" sx={{ color: BRAND.dimText }}>
                        {tagline}
                    </Typography>
                </Box>

                {/* Newsletter (only if onSubscribe provided) */}
                {onSubscribe && (
                    <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                        <Input
                            size="sm"
                            variant="soft"
                            placeholder="Your email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            startDecorator={<MailRoundedIcon />}
                            endDecorator={
                                <Button
                                    size="sm"
                                    color="danger"
                                    sx={{
                                        bgcolor: BRAND.red,
                                        "&:hover": { bgcolor: "#c2071b" },
                                        borderRadius: 8,
                                    }}
                                    onClick={() => onSubscribe?.(email)}
                                >
                                    Subscribe
                                </Button>
                            }
                            sx={{
                                "--Input-radius": "10px",
                                maxWidth: 380,
                                bgcolor: "rgba(255,255,255,0.06)",
                                color: BRAND.lightText,
                            }}
                        />
                    </Box>
                )}
            </Box>

            <Divider sx={{ opacity: 0.12 }} />

            {/* Bottom bar (minimal) */}
            <Box
                sx={{
                    maxWidth: 1200,
                    mx: "auto",
                    px: { xs: 2, md: 3 },
                    py: 1.5,
                    display: "flex",
                    gap: 1,
                    alignItems: "center",
                    flexWrap: "wrap",
                }}
            >
                <Typography level="body-xs" sx={{ color: BRAND.dimText }}>
                    © {new Date().getFullYear()} MOL Group
                </Typography>

                <Box sx={{ flex: 1 }} />

                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Select
                        size="sm"
                        variant="soft"
                        value={lang}
                        startDecorator={<LanguageRoundedIcon />}
                        onChange={(_, v) => v && setLang(v)}
                        sx={{
                            minWidth: 140,
                            bgcolor: "rgba(255,255,255,0.06)",
                            color: BRAND.lightText,
                            "--Select-indicatorColor": BRAND.lightText,
                        }}
                    >
                        {languages.map((l) => (
                            <Option key={l.code} value={l.code}>
                                {l.label}
                            </Option>
                        ))}
                    </Select>

                    <IconButton
                        aria-label="Back to top"
                        variant="soft"
                        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                        sx={{
                            borderRadius: 12,
                            bgcolor: "rgba(255,255,255,0.06)",
                            color: BRAND.lightText,
                            "&:hover": { bgcolor: "rgba(255,255,255,0.12)" },
                        }}
                    >
                        <ArrowUpwardRoundedIcon />
                    </IconButton>
                </Box>
            </Box>
        </Sheet>
    );
}
