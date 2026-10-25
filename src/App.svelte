<script>
  import { onMount } from "svelte";
  import { fly } from "svelte/transition";
  import Icon from "svelte-awesome";
  import { undo, link, externalLink, copy, check } from "svelte-awesome/icons";

  const { decode, enlarge } = window.giantURL;

  let input = "";
  let result = null;
  let errorMsg = "";
  let hasCopied = false;

  function enlargeURL() {
    errorMsg = "";
    try {
      result = enlarge(input, window.location.origin);
    } catch (error) {
      errorMsg = error.message;
    }
  }

  function redirectURL() {
    const token = window.location.hash.slice(1);
    if (!token) return;
    try {
      window.location.replace(decode(token, window.location.origin));
    } catch (error) {
      result = null;
      errorMsg = error.message;
    }
  }

  onMount(redirectURL);

  function copyText() {
    navigator.clipboard.writeText(result.enlarged);
    hasCopied = true;

    setTimeout(() => (hasCopied = false), 1500);
  }
</script>

<svelte:window on:hashchange={redirectURL} />

<svelte:head>
  <link rel="icon" href="/favicon.png" />
  <title>GiantURL.net - enlarge that short url into a giant url</title>
</svelte:head>

<div class="container">
  <section>
    <h1>
      <Icon data={link} scale={3} /> GiantURL
    </h1>
    <div class="row">
      <div class="four columns">
        <p>
          GiantURL enlarges your pesky small URLs by three or four, uniquely,
          and forever.
        </p>
        <br />
        <p>&copy; 2022-{new Date().getUTCFullYear()} Elias Gabriel</p>
      </div>
      <div class="eight columns">
        {#if !result}
          <form on:submit|preventDefault={enlargeURL} in:fly={{ y: -25 }}>
            <label for="shortURL"> Enter a short URL to make a GiantURL </label>
            <input
              class="u-full-width"
              type="text"
              id="shortURL"
              bind:value={input}
              required
            />
            <label
              for="submit"
              class:error={errorMsg}
              class:invisible={!errorMsg}
            >
              * {errorMsg}
            </label>
            <input
              id="submit"
              class="button-primary"
              type="submit"
              value="Make GiantURL!"
            />
          </form>
        {:else}
          <div in:fly={{ y: -25 }}>
            <label for="original">Your Short URL</label>
            <div class="u-full-width output" id="original">
              {result.original}
            </div>
            <label for="longerURLWrap">
              GiantURL ({result.improvement}% larger)
            </label>
            <div class="u-full-width output" id="longerURLWrap">
              <span id="longerURL">{result.enlarged}</span>
              <button disabled={hasCopied} class:hasCopied on:click={copyText}>
                <Icon data={hasCopied ? check : copy} />
              </button>
            </div>

            <a
              class="button"
              href={result.enlarged}
              rel="external"
              target="_blank"
            >
              <Icon data={externalLink} /> Visit Link
            </a>
            &nbsp;
            <a class="button button-primary" href="/">
              Enlarge another <Icon data={undo} />
            </a>
          </div>
        {/if}
      </div>
    </div>
  </section>
</div>

<style>
  @import "normalize-css";
  @import "skeleton-css/css/skeleton.css";

  section {
    padding-top: 6rem;
  }

  .error {
    color: red;
    font-weight: normal;
  }

  .invisible {
    display: none;
  }

  .output {
    padding: 6px 10px;
    background-color: #fff;
    border: 1px solid #d1d1d1;
    border-radius: 4px;
    box-shadow: none;
    box-sizing: border-box;
    margin-bottom: 1.5rem;
    word-wrap: anywhere;
    display: flow-root;
  }

  #longerURLWrap > button {
    padding: 0px;
    float: right;
    margin-top: 1rem;
    width: 3rem;
    transition: 0.25s;
  }

  #longerURLWrap > button.hasCopied {
    border-color: #35b950;
    color: #35b950;
  }

  :global(svg.fa-icon) {
    vertical-align: text-bottom;
    overflow: visible;
  }
</style>
