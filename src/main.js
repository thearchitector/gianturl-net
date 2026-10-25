const [{ mount }, { default: App }] = await Promise.all([
  import("svelte"),
  import("./App.svelte"),
]);
mount(App, { target: document.getElementById("app"), intro: false });
