import { produce } from 'immer';
import * as React from "react";
import * as ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router";
import { create } from 'zustand';
import menu, { type Menu } from "~/config/menu";
import JoyOrderDashboardTemplate from "./App";
import Layout from "./layouts/dashboard";
import LoginPage from "./pages/login";

export interface User {
  code: string;
  name: string;
  image?: string;
}
export interface AppState {
  loggedIn: boolean;
  user: User | null;
  setUser: (user: User) => void;
  clearUser: () => void;
  login: () => void;
  logout: () => void;
}

function loadUserFromLocalStore(): User | null {
  const userJson = localStorage.getItem("user_data");
  console.log("loadUserFromLocalStore", userJson);
  if (!userJson) return null;
  const user = JSON.parse(userJson);
  return user;
}
function storeUserToLocalStore(user: User) {
  localStorage.setItem("user_data", JSON.stringify(user));
}
function deleteUserFromLocalStore() {
  localStorage.removeItem("user_data");
}

export const useAppStore = create<AppState>((set) => ({
  loggedIn: false,
  user: null,
  setUser: (user: User) => {
    set(produce((state: AppState) => { state.user = user; state.loggedIn = true }));
    storeUserToLocalStore(user);
  },
  clearUser: () => {
    set(produce((state: AppState) => { state.user = null; state.loggedIn = false }));
    deleteUserFromLocalStore();
  },
  login: () => set(produce((state: AppState) => { state.loggedIn = true })),
  logout: () => set(produce((state: AppState) => { state.loggedIn = false })),
} as AppState));

const user = loadUserFromLocalStore();
if (user) {
  console.log("User loaded from local storage:", user);
  useAppStore.getState().setUser(user);
}

const router = createBrowserRouter([
  {
    Component: JoyOrderDashboardTemplate,
    children: [
      {
        path: "/",
        Component: Layout,
        children: (menu as Menu).items.map((item) => ({
          path: item.link[0],
          Component: item.component,
        })),
      },
    ],
  },
  {
    path: "/login",
    Component: LoginPage,
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
