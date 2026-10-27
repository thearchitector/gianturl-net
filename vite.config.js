import { svelte } from "@sveltejs/vite-plugin-svelte";

export default {
  plugins: [svelte()],
  publicDir: "static",
  build: {
    outDir: "public",
    rolldownOptions: {
      input: {
        index: "index.html",
        "src/main": "src/main.js",
        gianturl: "static/gianturl.js",
      },
      output: { entryFileNames: "[name].js" },
    },
  },
};
