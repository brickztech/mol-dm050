import * as React from "react";
import { Box, ListItem, ListItemDecorator, Typography } from "@mui/joy";
import logoRed from "assets/mol_red.png";

type Props = {
    children: React.ReactNode;
    secondary?: boolean;
    iconSrc?: string;
    iconSize?: number;
    fontWeight?: number;
};

export default function BulletItem({
                                           children,
                                           secondary = false,
                                           iconSrc = logoRed,
                                           iconSize = 20,
                                           fontWeight = 500,
                                       }: Props) {
    return (
        <ListItem sx={{ alignItems: "flex-start",  py: 0.5 }}>
            <ListItemDecorator sx={{ mt: "1px" }}>
                <Box
                    component="img"
                    src={iconSrc}
                    alt="bullet"
                    sx={{ height: iconSize, width: "auto", userSelect: "none" }}
                />
            </ListItemDecorator>
            <Typography
                level="body-md"
                sx={{ color: secondary ? "text.secondary" : "text.primary", fontWeight }}
            >
                {children}
            </Typography>
        </ListItem>
    );
}
