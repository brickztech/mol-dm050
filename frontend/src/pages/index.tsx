import * as React from "react";
import { Box, Button, Divider, Grid, Typography, Sheet, List, ListItem, ListItemDecorator } from "@mui/joy";

import { motion } from "framer-motion";
import ArrowRightAltRoundedIcon from "@mui/icons-material/ArrowRightAltRounded";
import { useNavigate } from "react-router";
import ExampleQuestionCard from "components/ExampleQuestionCard";
import logo_red from "assets/mol_red.png";
import BulletItem from "components/BulletItem.tsx";
const CARD_HEIGHT = { xs: 120, sm: 128, lg: 128 };
import { useColorScheme } from "@mui/joy/styles";
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
        opacity: 1, y: 0,
        transition: { duration: 0.32, ease: "easeOut", when: "beforeChildren", staggerChildren: 0.05 },
    },
};
const item = {
    hidden: { opacity: 0, y: 4 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.22, ease: "easeOut" } },
};

export default function HomePage() {
    const navigate = useNavigate();
    const { mode } = useColorScheme();
    const logoSrc = mode === "dark" ? logo_red : logo_red;

    const sendExample = (q: string) => {
        navigate(`/dm050?q=${encodeURIComponent(q)}`, { state: { q } });
    };

    return (
        <motion.div initial="hidden" animate="visible" variants={container}>
            <Box
                component={motion.section}
                variants={item}
                sx={{
                    width: "100%",
                    p: { xs: 2, md: 3 },
                    borderRadius: 2,
                    background: "transparent",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 1.75,
                }}
            >
                <Box
                    component={motion.div}
                    variants={item}
                    sx={{
                        width: "100%",
                        maxWidth: 960,
                        display: "flex",
                        flexDirection: "row",
                        alignItems: "center",
                        gap: 1,
                        justifyContent: "flex-start",
                        mb: 1,
                    }}
                >
                    <Box
                        component="img"
                        src={logoSrc}
                        alt="DM050 Logo"
                        sx={{
                            height: 32,
                            width: "auto",
                            mb: 0.5,
                            userSelect: "none",

                        }}
                    />
                    <Typography
                        level="h1"
                        component={motion.h1}
                        variants={item}
                        sx={{
                            fontSize: { xs: 22, sm: 45 },
                            fontWeight: 700,
                            letterSpacing: 0.2,
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
                        maxWidth: 960,
                        textAlign: "left",
                        "--ListItem-minHeight": "28px",
                        gap: 1.5,
                    }}
                >
                    <BulletItem>
                        Use natural language to explore operational and analytical data across projects, users, and time.
                    </BulletItem>

                    <BulletItem>
                        Automatically translates your question into SQL, runs it against the selected datasets, and returns
                        results instantly — as interactive tables <strong>or charts</strong> for easier visual analysis.
                    </BulletItem>

                    <BulletItem>
                        Iterate quickly — refine the question, adjust filters, or export both tabular and graphical results without leaving the page.
                    </BulletItem>

                    <BulletItem secondary>
                        Designed for business users and analysts to uncover insights faster — no SQL required — while still
                        providing transparency, control, and clear visuals that make complex data easy to understand.
                    </BulletItem>
                </List>

                <Divider sx={{ my: 1, opacity: 0.12, width: "100%" }} />


                <Typography
                    level="h4"
                    component={motion.p}
                    variants={item}
                    sx={{ color: "text.primary", width: "100%", maxWidth: 960, mt: 5 }}
                >
                    Try an example to jump straight into DM050 with a prefilled question:
                </Typography>

                <Grid
                    container
                    spacing={1.25}
                    sx={{ width: "100%", maxWidth: 960 }}
                    component={motion.div}
                    variants={container}
                >
                    {EXAMPLES.map((q) => (
                        <Grid
                            xs={12}
                            sm={6}
                            lg={4}
                            key={q}
                            component={motion.div}
                            variants={item}
                            sx={{ display: "flex" }}
                        >
                            <ExampleQuestionCard
                                title={q}
                                onClick={() => sendExample(q)}
                                sx={{
                                    height: CARD_HEIGHT,
                                    width: "100%",
                                    flex: 1,
                                }}
                            />
                        </Grid>
                    ))}
                </Grid>

                <Box component={motion.div} variants={item} sx={{ display: "flex", gap: 1, width: "100%", maxWidth: 960 }}>
                    <Button
                        onClick={() => navigate("/dm050")}
                        size="md"
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
                            px: { xs: 1.25, sm: 1.75 },
                            minHeight: 40,
                            borderRadius: 5,
                            textTransform: "none",
                            fontWeight: 700,
                            letterSpacing: 0.2,
                            backgroundColor: "#000000",
                            "&:hover": { backgroundColor: "#E0081F" },
                            color: "#fff",
                            boxShadow: "3 3px 20px rgba(0,0,0,0.15)",
                            transition: "transform .06s ease, box-shadow .18s ease, opacity .18s ease, filter .18s ease",
                            "&:active": { transform: "translateY(1px)" },
                            "&:focus-visible": {
                                outline: "none",
                                boxShadow:
                                    "0 0 0 3px rgba(224,8,31,0.25), 0 0 0 6px rgba(0,90,155,0.15), 0 10px 24px rgba(0,0,0,0.12)",
                            },
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
