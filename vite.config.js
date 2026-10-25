import { svelte } from "@sveltejs/vite-plugin-svelte";

export default {
  plugins: [svelte()],
  publicDir: "static",
  build: {
    outDir: "public",
    rolldownOptions: {
      input: ["index.html", "src/main.js"],
      output: { entryFileNames: "src/[name].js" },
    },
  },
};
