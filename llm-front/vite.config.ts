import react from "@vitejs/plugin-react-swc";
import * as path from "path";
import { defineConfig } from "vite";
import svgr from "vite-plugin-svgr";

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    outDir: '../jidongkim/dist'
  },
  plugins: [
    react(),
    svgr({
      svgrOptions: {
        svgo: true,
        icon: true,
      },
      esbuildOptions: {},
      include: "**/*.svg?react",
      exclude: "",
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "./runtimeConfig": "./runtimeConfig.browser", // 모듈의 실제 위치를 브라우저 번들러에게 알려줌
    },
  },
});
