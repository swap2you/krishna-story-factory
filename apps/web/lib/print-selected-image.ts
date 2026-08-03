/**
 * Isolated same-origin image print — never prints the application DOM.
 * Accepts only known story asset URLs from the current package (caller-validated).
 */

export type PrintSelectedImageOptions = {
  imageUrl: string;
  title?: string;
  /** Allowed same-origin or relative asset URLs for this story session. */
  allowedUrls: readonly string[];
};

export type PrintSelectedImageResult =
  | { ok: true }
  | { ok: false; reason: "blocked_url" | "window_blocked" | "image_error" };

function normalizeAssetUrl(url: string): string {
  try {
    if (typeof window !== "undefined") {
      return new URL(url, window.location.origin).href;
    }
  } catch {
    /* fall through */
  }
  return url.trim();
}

export function isAllowedPrintAssetUrl(imageUrl: string, allowedUrls: readonly string[]): boolean {
  const target = normalizeAssetUrl(imageUrl);
  return allowedUrls.some((candidate) => normalizeAssetUrl(candidate) === target);
}

function buildPrintDocumentHtml(imageUrl: string, title: string): string {
  const safeTitle = title.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const safeSrc = imageUrl.replace(/"/g, "&quot;");
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>${safeTitle}</title>
<style>
  @page { margin: 12mm; }
  html, body {
    margin: 0;
    padding: 0;
    background: #fff;
    height: 100%;
  }
  body {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
  }
  img {
    display: block;
    max-width: 100%;
    max-height: 100vh;
    width: auto;
    height: auto;
    object-fit: contain;
    page-break-inside: avoid;
  }
</style>
</head>
<body>
  <img id="print-target" src="${safeSrc}" alt="${safeTitle}" />
</body>
</html>`;
}

/**
 * Open a temporary same-origin iframe, load only the selected image, print when ready,
 * then tear down after `afterprint` (long fallback only if the event never fires).
 */
export async function printSelectedImage(
  options: PrintSelectedImageOptions,
): Promise<PrintSelectedImageResult> {
  const { imageUrl, title = "Print image", allowedUrls } = options;
  if (!isAllowedPrintAssetUrl(imageUrl, allowedUrls)) {
    return { ok: false, reason: "blocked_url" };
  }

  if (typeof document === "undefined" || typeof window === "undefined") {
    return { ok: false, reason: "window_blocked" };
  }

  const iframe = document.createElement("iframe");
  iframe.setAttribute("aria-hidden", "true");
  iframe.setAttribute("title", "Print selected image");
  iframe.style.cssText =
    "position:fixed;right:0;bottom:0;width:0;height:0;border:0;opacity:0;pointer-events:none;";
  document.body.appendChild(iframe);

  let fallbackTimer = 0;
  let settled = false;

  const cleanup = () => {
    window.clearTimeout(fallbackTimer);
    if (iframe.parentNode) iframe.parentNode.removeChild(iframe);
  };

  const finish = (result: PrintSelectedImageResult): PrintSelectedImageResult => {
    if (settled) return result;
    settled = true;
    cleanup();
    return result;
  };

  const doc = iframe.contentDocument;
  if (!doc) {
    return finish({ ok: false, reason: "window_blocked" });
  }

  return new Promise((resolve) => {
    try {
      doc.open();
      doc.write(buildPrintDocumentHtml(imageUrl, title));
      doc.close();
    } catch {
      resolve(finish({ ok: false, reason: "window_blocked" }));
      return;
    }

    const img = doc.getElementById("print-target") as HTMLImageElement | null;
    if (!img) {
      resolve(finish({ ok: false, reason: "image_error" }));
      return;
    }

    const runPrint = () => {
      try {
        const win = iframe.contentWindow;
        if (!win) {
          resolve(finish({ ok: false, reason: "window_blocked" }));
          return;
        }
        const onAfterPrint = () => {
          win.removeEventListener("afterprint", onAfterPrint);
          resolve(finish({ ok: true }));
        };
        win.addEventListener("afterprint", onAfterPrint);
        // Keep the iframe alive while the system print dialog is open.
        fallbackTimer = window.setTimeout(() => {
          win.removeEventListener("afterprint", onAfterPrint);
          resolve(finish({ ok: true }));
        }, 120_000);
        win.focus();
        // Playwright / automation can set this to avoid blocking on the system dialog.
        if ((window as unknown as { __BHAVA_SKIP_PRINT__?: boolean }).__BHAVA_SKIP_PRINT__) {
          win.dispatchEvent(new Event("afterprint"));
        } else {
          win.print();
        }
      } catch {
        resolve(finish({ ok: false, reason: "window_blocked" }));
      }
    };

    const whenReady = () => {
      if (typeof img.decode === "function") {
        void img
          .decode()
          .then(runPrint)
          .catch(() => {
            if (img.complete && img.naturalWidth > 0) runPrint();
            else resolve(finish({ ok: false, reason: "image_error" }));
          });
      } else if (img.complete && img.naturalWidth > 0) {
        runPrint();
      } else {
        img.onload = () => runPrint();
        img.onerror = () => resolve(finish({ ok: false, reason: "image_error" }));
      }
    };

    whenReady();
  });
}

/** DOM-contract helper for tests: printable markup contains only the target image. */
export function printableImageDocumentContract(html: string, imageUrl: string): {
  hasTargetImage: boolean;
  hasThumbnailText: boolean;
  hasSiteChrome: boolean;
} {
  return {
    hasTargetImage: html.includes(imageUrl),
    hasThumbnailText: /carousel-thumb|asset-tile/i.test(html),
    hasSiteChrome: /site-header|site-footer|mini-player|bhava-tabs|carousel-dialog/i.test(html),
  };
}

export function buildIsolatedPrintHtmlForTest(imageUrl: string, title = "Print image"): string {
  return buildPrintDocumentHtml(imageUrl, title);
}
