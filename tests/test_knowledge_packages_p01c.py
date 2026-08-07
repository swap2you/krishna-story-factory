"""P01C knowledge package schema, lifecycle, auth, and export tests."""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from bhava_api.knowledge.packages import (  # noqa: E402
    FIXTURE_MARKER,
    VENDORED_DEVA,
    VENDORED_LATIN,
    canonical_text_hash,
    get_package,
    is_loopback_host,
    list_packages,
    render_docx,
    render_pdf,
    resolve_vendored_fonts,
    validate_package,
)
from bhava_api.knowledge.routes import router as knowledge_router  # noqa: E402


@pytest.fixture()
def pkg():
    package = get_package("p01c-structural-fixture")
    assert package is not None
    return package


def test_fixture_package_valid_and_blocked(pkg):
    result = validate_package(pkg)
    assert result.ok, result.errors
    assert pkg["record"]["source_status"] == "SOURCE_BLOCKED"
    assert pkg["source_dossier"]["decision"] == "SOURCE_BLOCKED"
    assert pkg["record"]["visibility"] == "private"
    assert pkg["record"]["fixture"] is True
    assert FIXTURE_MARKER in pkg["record"]["fixture_label"]
    assert canonical_text_hash(pkg["content"]) == pkg["record"]["canonical_text_hash"]


def test_list_packages_includes_fixture():
    ids = {p["record"]["record_id"] for p in list_packages()}
    assert "KF-P01C-FIXTURE-001" in ids


def test_vendored_fonts_resolve_with_checksums():
    latin, deva, hashes = resolve_vendored_fonts()
    assert latin.name == VENDORED_LATIN
    assert deva.name == VENDORED_DEVA
    assert hashes[VENDORED_LATIN]
    assert hashes[VENDORED_DEVA]


@pytest.mark.parametrize("page_size", ["letter", "a4"])
def test_export_pdf_docx_letter_and_a4(pkg, page_size):
    pdf, pdf_manifest = render_pdf(pkg, page_size=page_size)
    docx, docx_manifest = render_docx(pkg, page_size=page_size)
    assert pdf.startswith(b"%PDF")
    assert docx[:2] == b"PK"
    assert pdf_manifest["page_sizes"] == [page_size]
    assert docx_manifest["page_sizes"] == [page_size]
    assert pdf_manifest["canonical_content_hash"] == pkg["record"]["canonical_text_hash"]
    assert docx_manifest["canonical_content_hash"] == pkg["record"]["canonical_text_hash"]
    assert pdf_manifest["embedded_font_hashes"][VENDORED_LATIN]
    assert pdf_manifest["embedded_font_hashes"][VENDORED_DEVA]
    assert docx_manifest["embedded_font_hashes"] == pdf_manifest["embedded_font_hashes"]
    assert pdf_manifest["validation"]["pdf_ua_claimed"] is False
    assert pdf_manifest["validation"]["study_neutral"] is True

    from pypdf import PdfReader
    from docx import Document

    pdf_text = "\n".join((page.extract_text() or "") for page in PdfReader(io.BytesIO(pdf)).pages)
    assert "TEST FIXTURE" in pdf_text
    assert pkg["record"]["title"] in pdf_text
    assert f"Page size: {page_size}" in pdf_text
    assert any("\u0900" <= ch <= "\u097F" for ch in pdf_text), pdf_text[:500]
    stanzas = [b for b in pkg["content"]["blocks"] if b.get("block_type") == "stanza"]
    assert stanzas[0]["iast"] in pdf_text
    assert stanzas[0]["translation_en"] in pdf_text

    document = Document(io.BytesIO(docx))
    text = "\n".join(p.text for p in document.paragraphs)
    assert "TEST FIXTURE" in text
    assert pkg["record"]["title"] in text
    assert f"Page size: {page_size}" in text
    assert any("\u0900" <= ch <= "\u097F" for ch in text)
    assert "lens_explanations" not in text
    assert "word_meanings" not in text
    section = document.sections[0]
    if page_size == "a4":
        assert abs(section.page_width.mm - 210) < 1
        assert abs(section.page_height.mm - 297) < 1
    else:
        assert abs(section.page_width.inches - 8.5) < 0.05
        assert abs(section.page_height.inches - 11) < 0.05


def test_canonical_hash_ignores_lens_copy(pkg):
    content = dict(pkg["content"])
    blocks = [dict(b) for b in content["blocks"]]
    for b in blocks:
        if b.get("block_type") == "stanza":
            b["lens_explanations"] = {"explorer": "CHANGED LENS COPY MUST NOT AFFECT HASH"}
    content["blocks"] = blocks
    assert canonical_text_hash(content) == pkg["record"]["canonical_text_hash"]


@pytest.mark.parametrize(
    "host,expected",
    [
        ("127.0.0.1", True),
        ("127.1.2.3", True),
        ("localhost", True),
        ("::1", True),
        ("[::1]", True),
        ("::ffff:127.0.0.1", True),
        ("testclient", True),
        ("8.8.8.8", False),
        ("example.com", False),
        ("::ffff:8.8.8.8", False),
        (None, False),
    ],
)
def test_is_loopback_host(host, expected):
    assert is_loopback_host(host) is expected


def test_private_search_rejects_forgeable_header_alone():
    app = FastAPI()
    app.include_router(knowledge_router)
    client = TestClient(app)
    res = client.get(
        "/api/v1/knowledge/search",
        params={"q": "Sanatana", "include_private": True},
        headers={"X-Bhava-Studio": "1"},
    )
    assert res.status_code == 403
    detail = res.json()["detail"].lower()
    assert "secret" in detail or "forgeable" in detail


def test_private_search_allows_loopback_with_secret(monkeypatch):
    monkeypatch.setenv("BHAVA_STUDIO_BOOTSTRAP_TOKEN", "test-studio-secret")
    app = FastAPI()
    app.include_router(knowledge_router)
    client = TestClient(app)
    res = client.get(
        "/api/v1/knowledge/search",
        params={"q": "Sanatana", "include_private": True},
        headers={"X-Bhava-Studio": "1", "X-Bhava-Studio-Secret": "test-studio-secret"},
    )
    assert res.status_code == 200
    assert res.json()["count"] >= 1


def test_packages_endpoint_requires_secret(monkeypatch):
    monkeypatch.setenv("BHAVA_STUDIO_BOOTSTRAP_TOKEN", "test-studio-secret")
    app = FastAPI()
    app.include_router(knowledge_router)
    client = TestClient(app)
    denied = client.get("/api/v1/knowledge/packages", headers={"X-Bhava-Studio": "1"})
    assert denied.status_code == 403
    ok = client.get(
        "/api/v1/knowledge/packages",
        headers={"X-Bhava-Studio-Secret": "test-studio-secret"},
    )
    assert ok.status_code == 200
    assert any(p["slug"] == "p01c-structural-fixture" for p in ok.json()["packages"])
