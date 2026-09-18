import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";

export default defineConfig({
  resolve: {
    alias: {
      "@foxglove/common": fileURLToPath(new URL("./src/foxglove-common-shim.ts", import.meta.url)),
    },
  },
  server: {
    host: "localhost",
    port: 5173,
    strictPort: true,
    fs: {
      allow: [".."],
    },
  },
  preview: {
    host: "localhost",
    port: 5173,
    strictPort: true,
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
