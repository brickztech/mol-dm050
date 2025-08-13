import Box from "@mui/joy/Box";
import Breadcrumbs from "@mui/joy/Breadcrumbs";
import CssBaseline from "@mui/joy/CssBaseline";
import Link from "@mui/joy/Link";
import { CssVarsProvider, useTheme } from "@mui/joy/styles";
import Typography from "@mui/joy/Typography";

import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";
import HomeRoundedIcon from "@mui/icons-material/HomeRounded";

import Header from "components/joy/Header";
import Sidebar from "components/joy/Sidebar";
import { Outlet, useLocation, useNavigation, useRoutes } from "react-router";
import menu from "./config/menu";

export default function JoyOrderDashboardTemplate() {
  const theme = useTheme();
  const location = useLocation();

  const currentUrl = location.pathname || "";
  const currentMenu = menu.items.filter(item => item.link.includes(currentUrl));
  console.log("currentUrl: ", currentUrl, "currentMenu: ", currentMenu);
  return (
    <CssVarsProvider disableTransitionOnChange theme={theme}>
      <CssBaseline />
      <Box sx={{ display: "flex", minHeight: "100dvh" }}>
        <Header />
        <Sidebar />
        <Box
          component="main"
          className="MainContent"
          sx={{
            px: { xs: 2, md: 6 },
            pt: {
              xs: "calc(12px + var(--Header-height))",
              sm: "calc(12px + var(--Header-height))",
              md: 3,
            },
            pb: { xs: 2, sm: 2, md: 3 },
            flex: 1,
            display: "flex",
            flexDirection: "column",
            minWidth: 0,
            height: "100dvh",
            
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Breadcrumbs
              size="sm"
              aria-label="breadcrumbs"
              separator={<ChevronRightRoundedIcon fontSize="small" />}
              sx={{ pl: 0 }}
            >
              <Link
                underline="none"
                color="neutral"
                href="/"
                aria-label="Home"
              >
                <HomeRoundedIcon />
              </Link>
              <Typography
                color="primary"
                sx={{ fontWeight: 500, fontSize: 12 }}
              >
                {currentMenu.length > 0 ? currentMenu[0].name : ""}
              </Typography>
            </Breadcrumbs>
          </Box>
          <Outlet />
        </Box>
      </Box>
    </CssVarsProvider>
  );
}
