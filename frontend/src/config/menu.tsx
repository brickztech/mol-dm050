import BarChartIcon from '@mui/icons-material/BarChart';
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import QueryStatsRoundedIcon from "@mui/icons-material/QueryStatsRounded";
import HomePage from "src/pages";
import Text2SqlPageMol from "src/pages/chat";
// import HistoryPage from "src/pages/historyPage.tsx";

export interface Menu {
  items: MenuItem[];
}
export interface MenuItem {
  name: string;
  link: string[];
  icon: React.ElementType<any>;
  component: React.ComponentType<{}> | null | undefined;
}

export default {
  items: [
    {
      name: "HOME",
      icon: DashboardRoundedIcon,
      link: ["", "/"],
      component: HomePage,
    },
    {
      name: "DM050",
      icon: BarChartIcon,
      link: ["/dm050"],
      component: Text2SqlPageMol,
    },
    // {
    //   name: "History",
    //   icon: QueryStatsRoundedIcon,
    //   link: ["/history"],
    //   component: HistoryPage,
    // },
  ] as MenuItem[],
} as Menu;
