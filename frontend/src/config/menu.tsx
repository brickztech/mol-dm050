import BarChartIcon from '@mui/icons-material/BarChart';
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import HomePage from "src/pages";
import Text2SqlPageMol from "src/pages/chat";

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
      name: "Home",
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
  ] as MenuItem[],
} as Menu;
