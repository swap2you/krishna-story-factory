# ADR-006 — PDF/DOCX export strategy

## Status

Proposed (P01B) — D08 spike complete; OD-02/03/04 open for install/bar/policy

## Decision

1. **PDF primary:** reportlab platypus (already depended); HTML-print fallback only if shaping fails.  
2. **DOCX recommend:** `python-docx` (MIT) after owner install approval — do not install in P01B.  
3. **No paid PDF APIs** by default.  
4. **Do not claim PDF/UA** until capability proven (OD-03).  
5. **Study-neutral export** recommended (OD-04): canonical text only in PDF/DOCX hashes.  

## Consequences

Clear spike path; dependency gate explicit; hash agreement enforceable.
