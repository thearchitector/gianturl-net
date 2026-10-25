window.giantURL = (() => {
  const MAX_BYTES = 500;
  const BAD_URL =
    "This URL doesn't look quite right. Did you type it correctly?";
  const INFINITE_LOOP =
    "Within this URL I see a possibility for infinite loops, where there be dragons.";
  const URL_TOO_LARGE =
    "Enlarging the provided URL would exceed the maximum URL length for browser compatability. Sorry!";

  const encoder = new TextEncoder();
  const decoder = new TextDecoder("utf-8", { fatal: true });

  function normalizeURL(input, origin) {
    let original = input.trim();
    if (!/^[a-z][a-z\d+.-]*:/i.test(original)) {
      original = `http://${original}`;
    }

    let parsed;
    try {
      parsed = new URL(original);
    } catch {
      throw new Error(BAD_URL);
    }

    if (
      !/^https?:\/\/[^/]/i.test(original) ||
      /\s/.test(original) ||
      (!parsed.hostname.startsWith("[") &&
        (!parsed.hostname.includes(".") ||
          !parsed.hostname
            .split(".")
            .every((label) =>
              /^[a-z\d](?:[a-z\d-]{0,61}[a-z\d])?$/i.test(label),
            )))
    ) {
      throw new Error(BAD_URL);
    }
    if (parsed.origin === origin) {
      throw new Error(INFINITE_LOOP);
    }
    if (encoder.encode(original).length > MAX_BYTES) {
      throw new Error(URL_TOO_LARGE);
    }
    return original;
  }

  function enlarge(input, origin) {
    const original = normalizeURL(input, origin);
    let candidate = original;
    do {
      candidate = encoder.encode(candidate).toBase64({ alphabet: "base64url" });
    } while (candidate.length <= MAX_BYTES);

    const enlarged = `${origin}/#${candidate}`;
    return {
      original,
      enlarged,
      improvement: Math.trunc((enlarged.length / [...original].length) * 100),
    };
  }

  function decode(token, origin) {
    try {
      if (token.length > MAX_BYTES * 2) {
        throw new Error(BAD_URL);
      }
      let original = token;
      do {
        original = decoder.decode(
          Uint8Array.fromBase64(original, { alphabet: "base64url" }),
        );
      } while (original && !/^https?:\/\//i.test(original));
      if (normalizeURL(original, origin) !== original) {
        throw new Error(BAD_URL);
      }
      return original;
    } catch {
      throw new Error(
        `'${token}' is not a valid URL token. Return to ${origin}.`,
      );
    }
  }

  return { enlarge, decode };
})();
try {
  const token = location.hash.slice(1);
  if (token) {
    location.replace(window.giantURL.decode(token, location.origin));
    document.documentElement.hidden = true;
  }
} catch {
  // Invalid links fall through to the existing error UI.
}
