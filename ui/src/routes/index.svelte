<script lang="ts">
    import { fly } from "svelte/transition";
    import { SvelteToast, toast } from "@zerodevx/svelte-toast";

    let showURL: boolean = false;
    let originalURL: string = "";
    let longerURL: string = "";
    let percentLarger: string = "";

    let hasError: boolean = false;
    let errorMsg: string = "";

    async function enlargeURL() {
        let original = (document.getElementById("shortURL") as HTMLInputElement)
            .value;
        let response = await fetch(`/api?url=${encodeURIComponent(original)}`);
        let json = await response.json();

        if (response.ok) {
            originalURL = json["original"];
            percentLarger = json["improvement"];
            longerURL = json["enlarged"];
            showURL = true;
        } else {
            hasError = true;
            errorMsg = json["detail"];
        }
    }

    function copyText() {
        toast.push("Copied to clipboard", {
            duration: 2000,
            theme: {
                "--toastBackground": "#48BB78",
                "--toastBarBackground": "#2F855A",
            },
        });

        let copyText = document.getElementById("longerURL")! as HTMLDivElement;
        navigator.clipboard.writeText(copyText.innerText);
    }
</script>

<svelte:head>
    <title>GiantURL.net - enlarge that short url into a giant url</title>
</svelte:head>

<SvelteToast />

<div class="container">
    <section>
        <h1>GiantURL</h1>
        <div class="row">
            <div class="four columns">
                <p>
                    GiantURL enlarges your pesky small URLs by three or four,
                    securely, uniquely, and forever.
                </p>
                <p>
                    Want programatic access? Our REST API is rate limited, but
                    public and free. Read <a href="/docs" rel="external">here</a
                    >.
                </p>
            </div>
            <div class="eight columns">
                {#if !showURL}
                    <form
                        on:submit|preventDefault={enlargeURL}
                        in:fly={{ y: -25 }}
                    >
                        <label for="shortURL">
                            Enter a short URL to make a GiantURL
                        </label>
                        <input
                            class="u-full-width"
                            type="text"
                            id="shortURL"
                            value=""
                            required
                        />
                        <label
                            for="submit"
                            class:error={hasError}
                            class:invisible={!hasError}
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
                            {originalURL}
                        </div>
                        <label for="longerURLWrap">
                            GiantURL ({percentLarger} larger)
                        </label>
                        <div class="u-full-width output" id="longerURLWrap">
                            <span id="longerURL">{longerURL}</span>
                            <button on:click={copyText}>Copy</button>
                        </div>

                        <a class="button" href={longerURL} rel="external">
                            Visit Link
                        </a>
                        &nbsp;
                        <a
                            class="button button-primary"
                            href="/"
                            sveltekit:reload
                        >
                            Enlarge another
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
        padding: 0 5px;
        float: right;
        margin-top: 1rem;
    }
</style>
