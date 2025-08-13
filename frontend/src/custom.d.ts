/// <reference types="vite-plugin-svgr/client" />   
declare module "*.css";
declare module "*.json" {
  const value: any;
  export default value;
}
declare module "*.png" {
  const value: string;
  export default value;
}