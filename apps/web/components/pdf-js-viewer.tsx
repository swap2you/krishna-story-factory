"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@bhava/ui";
import type { PDFDocumentProxy, RenderTask } from "pdfjs-dist";

type Props = {
  url: string;
  title: string;
};

const ZOOM_STEPS = [0.75, 1, 1.25, 1.5, 2] as const;

export function PdfJsViewer({ url, title }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const shellRef = useRef<HTMLDivElement>(null);
  const pdfRef = useRef<PDFDocumentProxy | null>(null);
  const renderTaskRef = useRef<RenderTask | null>(null);
  const [page, setPage] = useState(1);
  const [pageCount, setPageCount] = useState(0);
  const [zoomIndex, setZoomIndex] = useState(1);
  const [fitWidth, setFitWidth] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  const zoom = ZOOM_STEPS[zoomIndex] ?? 1;

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setReady(false);
    setPage(1);
    setPageCount(0);

    void (async () => {
      try {
        const pdfjs = await import("pdfjs-dist");
        pdfjs.GlobalWorkerOptions.workerSrc = "/pdfjs/pdf.worker.min.mjs";
        const doc = await pdfjs.getDocument({ url, withCredentials: false }).promise;
        if (cancelled) {
          void doc.destroy();
          return;
        }
        if (pdfRef.current) {
          void pdfRef.current.destroy();
        }
        pdfRef.current = doc;
        setPageCount(doc.numPages);
        setReady(true);
        setLoading(false);
      } catch (err) {
        if (cancelled) return;
        setLoading(false);
        setError(err instanceof Error ? err.message : "Could not load the activity PDF.");
      }
    })();

    return () => {
      cancelled = true;
      renderTaskRef.current?.cancel();
      renderTaskRef.current = null;
      if (pdfRef.current) {
        void pdfRef.current.destroy();
        pdfRef.current = null;
      }
    };
  }, [url]);

  const renderPage = useCallback(async () => {
    const pdf = pdfRef.current;
    const canvas = canvasRef.current;
    if (!pdf || !canvas || !ready) return;

    try {
      renderTaskRef.current?.cancel();
      const pdfPage = await pdf.getPage(page);
      const baseViewport = pdfPage.getViewport({ scale: 1 });
      const containerWidth = containerRef.current?.clientWidth ?? baseViewport.width;
      const fitScale = Math.max(0.45, (containerWidth - 16) / baseViewport.width);
      const scale = (fitWidth ? fitScale : 1) * zoom;
      const viewport = pdfPage.getViewport({ scale });
      const ctx = canvas.getContext("2d", { alpha: false });
      if (!ctx) {
        setError("Canvas rendering is unavailable in this browser.");
        return;
      }
      canvas.height = Math.floor(viewport.height);
      canvas.width = Math.floor(viewport.width);
      canvas.style.width = `${Math.floor(viewport.width)}px`;
      canvas.style.height = `${Math.floor(viewport.height)}px`;

      const task = pdfPage.render({ canvasContext: ctx, viewport });
      renderTaskRef.current = task;
      await task.promise;
      setError(null);
    } catch (err) {
      if (err && typeof err === "object" && "name" in err && (err as { name: string }).name === "RenderingCancelledException") {
        return;
      }
      setError(err instanceof Error ? err.message : "Could not render this PDF page.");
    }
  }, [page, zoom, fitWidth, ready]);

  useEffect(() => {
    void renderPage();
  }, [renderPage]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(() => {
      if (fitWidth) void renderPage();
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [fitWidth, renderPage]);

  useEffect(() => {
    const shell = shellRef.current;
    if (!shell) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      event.stopPropagation();
      if (event.key === "ArrowLeft") {
        setPage((p) => Math.max(1, p - 1));
      } else {
        setPage((p) => Math.min(pageCount || p, p + 1));
      }
    };
    shell.addEventListener("keydown", onKey);
    return () => shell.removeEventListener("keydown", onKey);
  }, [pageCount]);

  const canPrev = page > 1;
  const canNext = page < pageCount;

  return (
    <div
      ref={shellRef}
      className="pdf-shell"
      data-pdf-viewer="pdfjs"
      tabIndex={0}
      role="region"
      aria-label={`${title} activity sheet viewer`}
    >
      <div className="pdf-toolbar" role="toolbar" aria-label="PDF controls">
        <Button
          variant="quiet"
          disabled={!canPrev || loading}
          aria-label="Previous page"
          onClick={() => setPage((p) => Math.max(1, p - 1))}
        >
          Previous
        </Button>
        <span className="pdf-page-label" aria-live="polite">
          {pageCount ? `Page ${page} of ${pageCount}` : "Page —"}
        </span>
        <Button
          variant="quiet"
          disabled={!canNext || loading}
          aria-label="Next page"
          onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
        >
          Next
        </Button>
        <Button
          variant={fitWidth ? "accent" : "quiet"}
          aria-pressed={fitWidth}
          onClick={() => setFitWidth((v) => !v)}
        >
          Fit width
        </Button>
        <Button
          variant="quiet"
          disabled={zoomIndex <= 0}
          aria-label="Zoom out"
          onClick={() => setZoomIndex((i) => Math.max(0, i - 1))}
        >
          −
        </Button>
        <span className="pdf-zoom-label">{Math.round(zoom * 100)}%</span>
        <Button
          variant="quiet"
          disabled={zoomIndex >= ZOOM_STEPS.length - 1}
          aria-label="Zoom in"
          onClick={() => setZoomIndex((i) => Math.min(ZOOM_STEPS.length - 1, i + 1))}
        >
          +
        </Button>
      </div>

      <div ref={containerRef} className="pdf-canvas-wrap">
        {loading ? (
          <p className="pdf-status hint" role="status">
            Loading activity sheet…
          </p>
        ) : null}
        {error ? (
          <div className="pdf-status pdf-status--error" role="alert">
            <p>Could not display the activity PDF here.</p>
            <p className="hint">{error}</p>
            <p className="hint">Use Open full tab or Download PDF above.</p>
          </div>
        ) : null}
        <canvas
          ref={canvasRef}
          className="pdf-canvas"
          data-testid="pdfjs-canvas"
          hidden={loading || !!error}
          aria-hidden={loading || !!error ? true : undefined}
          aria-label={`${title} activity sheet, page ${page}`}
        />
      </div>
      <p className="pdf-hint hint">Keyboard: focus this viewer, then ← / → to change pages.</p>
    </div>
  );
}
