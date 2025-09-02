import * as React from "react";
import { Box, Button, Divider, Grid, Typography, List } from "@mui/joy";
import { motion } from "framer-motion";
import ArrowRightAltRoundedIcon from "@mui/icons-material/ArrowRightAltRounded";
import { useNavigate } from "react-router";
import ExampleQuestionCard from "components/ExampleQuestionCard";
import logo_red from "assets/mol_red.png";
import BulletItem from "components/BulletItem.tsx";
import { useColorScheme } from "@mui/joy/styles";

const CARD_HEIGHT = { xs: 100, sm: 110, lg: 110 };

const BRAND = {
    red: "#E0081F",
    blue: "#005A9B",
    dark: "#62020c",
    dark2: "#012e4f",
} as const;
const EXAMPLES = [
    "Egy adott projekt(ek)re vagy felhasználóra vonatkozó ledolgozott órák összesítése/idősora.",
    "Kinek mennyi időt rögzítettek egy adott időszakban?",
    "Kik a tagjai egy adott projektnek?",
    "Milyen alprojekteket tartalmaz egy projekt?",
    "Hány aktív felhasználó, mennyi admin van a rendszerben?",
    "Projektek, felhasználók vagy csoportok szerinti statisztikák.",
];

const container = {
    hidden: { opacity: 0, y: 8 },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.32,
            ease: "easeOut",
            when: "beforeChildren",
            staggerChildren: 0.05,
        },
    },
};
const item = {
    hidden: { opacity: 0, y: 4 },
    visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.22, ease: "easeOut" },
    },
};

export default function HomePage() {
    const navigate = useNavigate();
    const { mode } = useColorScheme();
    const logoSrc = mode === "dark" ? logo_red : logo_red;
    const isDark = mode === "dark";

    const sendExample = (q: string) => {
        navigate(`/dm050?q=${encodeURIComponent(q)}`, { state: { q } });
    };

    return (
        <motion.div initial="hidden" animate="visible" >
            <Box
                component={motion.section}
                sx={{
                    width: "100%",
                    p: { xs: 1.5, md: 2 },
                    borderRadius: 2,
                    background: "transparent",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 1.25,
                }}
            >
                <Box
                    component={motion.div}
                    sx={{
                        width: "100%",
                        maxWidth: 1100,
                        display: "flex",
                        flexDirection: "row",
                        alignItems: "center",
                        gap: 0.75,
                        justifyContent: "flex-start",
                        mb: 0.75,
                    }}
                >
                    <Box
                        component="img"
                        src={logoSrc}
                        alt="DM050 Logo"
                        sx={{
                            height: 26,
                            width: "auto",
                            mb: 0.25,
                            userSelect: "none",
                        }}
                    />
                    <Typography
                        level="h2"
                        component={motion.h1}
                        sx={{
                            fontSize: { xs: 18, sm: 34 },
                            fontWeight: 600,
                            letterSpacing: 0.15,
                            color: "text.primary",
                            m: 0,
                            textAlign: "center",
                        }}
                    >
                        DM050 Text-to-SQL Console
                    </Typography>
                </Box>

                <List
                    size="sm"
                    sx={{
                        maxWidth: 1000,
                        textAlign: "left",
                        "--ListItem-minHeight": "24px",
                        gap: 1.25,
                    }}
                >
                    <BulletItem>
                        Use natural language to explore operational and analytical data across projects, users, and time.
                    </BulletItem>
                    <BulletItem>
                        Automatically translates your question into SQL, runs it against the selected datasets, and returns results
                        instantly — as interactive tables <strong>or charts</strong>.
                    </BulletItem>
                    <BulletItem>
                        Iterate quickly — refine the question, adjust filters, or export results without leaving the page.
                    </BulletItem>
                    <BulletItem secondary>
                        Designed for business users and analysts to uncover insights faster — no SQL required.
                    </BulletItem>
                </List>

                <Divider sx={{ my: 3, opacity: 1, width: "100%",  }} />

                <Typography
                    component={motion.p}
                    sx={{ color: "text.primary", width: "100%", maxWidth: 960, mt: 0.5 }}
                >
                    Try an example to jump straight into DM050 with a prefilled question:
                </Typography>

                <Grid
                    container
                    spacing={1}
                    sx={{ width: "100%", maxWidth: 960 }}
                    component={motion.div}
                >
                    {EXAMPLES.map((q) => (
                        <Grid
                            xs={12}
                            sm={6}
                            lg={4}
                            key={q}
                            component={motion.div}
                            sx={{ display: "flex" }}
                        >
                            <ExampleQuestionCard
                                title={q}
                                onClick={() => sendExample(q)}
                                sx={{
                                    height: CARD_HEIGHT,
                                    width: "100%",
                                    flex: 1,
                                    fontSize: "0.85rem",
                                }}
                            />
                        </Grid>
                    ))}
                </Grid>

                <Box
                    component={motion.div}
                    sx={{ display: "flex", gap: 1, width: "100%", maxWidth: 960, mt: 3, flex: 1}}
                >
                    <Button
                        onClick={() => navigate("/dm050")}
                        size="sm"
                        variant="solid"
                        endDecorator={
                            <ArrowRightAltRoundedIcon
                                sx={{
                                    transition: "transform .18s ease",
                                    ".open-console-btn:hover &": { transform: "translateX(2px)" },
                                }}
                            />
                        }
                        className="open-console-btn"
                        sx={{
                            ml: "auto",
                            px: { xs: 1, sm: 1.5 },
                            minHeight: 34,
                            borderRadius: 4,
                            textTransform: "none",
                            fontWeight: 600,
                            letterSpacing: 0.15,
                            backgroundColor: isDark ? BRAND.red : BRAND.blue,
                            "&:hover": {
                                backgroundColor: isDark ? BRAND.dark : BRAND.dark2
                            },
                            color: "#fff",
                            transition: "transform .06s ease, box-shadow .18s ease, opacity .18s ease, filter .18s ease",
                            "&:active": { transform: "translateY(1px)" },
                            width: { xs: "100%", sm: "auto" },
                        }}
                    >
                        Open DM050 Console
                    </Button>
                </Box>
            </Box>
        </motion.div>
    );
}
