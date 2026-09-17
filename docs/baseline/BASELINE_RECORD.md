# Existing Prototype Baseline Record

**Task:** 0.1 — Create a project baseline release
**Date recorded:** 2026-09-17
**Tag:** `v0.1-prototype`
**Tagged commit SHA:** `fd5cd91aa35470d7777c37982689230f196b233c`
**Source repository:** https://github.com/Subeeshan07/legal-metrology-compliance-checker

This record exists so another team member can reproduce and verify the original
prototype without relying on any one developer's machine state.

---

## 1. What was verified

| Check | Result |
|---|---|
| Fresh clone checks out the tag | ✅ Verified (`git checkout v0.1-prototype` from a clean clone) |
| Tag contains all current sample assets and dataset files | ✅ `static/samples/` and `legal_metrology_dataset.csv` are present and tracked at this commit |
| No generated uploads or secrets are tracked | ✅ `git ls-files` shows nothing under `uploads/`, no `.env`, no `*.db`, no credential files. `.gitignore` already excludes `uploads/`, `.env`, `venv/`, `__pycache__/`, `*.log`. |
| App boots from a clean environment | ✅ `python -c "import app"` succeeds; Flask app object constructs; 9 routes register correctly |
| Existing test suite runs | ⚠️ 8 of 9 tests pass (see below) |

## 2. Environment used for verification

| Component | Version |
|---|---|
| OS | Ubuntu 24.04 (Linux container) |
| Python | 3.12.3 |
| Flask | 3.0.x (per `requirements.txt` floor `>=3.0.0`) |
| Pillow | `>=10.0.0` |
| pandas | `>=2.0.0` |
| pytesseract | `>=0.3.10` |
| Werkzeug | `>=3.0.0` |
| Tesseract OCR binary | 5.3.4 (installed at `/usr/bin/tesseract` via apt, i.e. Linux path, not the Windows path the code assumes) |
| Browser | No specific browser version is pinned by the project; README makes no browser claim. Manual smoke testing should target current Chrome, Firefox, and Edge until a supported-browser statement is written (tracked under Task 0.3 / documentation tasks). |

`requirements.txt` at this commit pins only lower bounds (`>=`), not exact
versions, so exact minor/patch versions actually installed depend on what
PyPI resolves at install time. Pinning exact compatible ranges is explicitly
scoped to **Task 0.3**, not this baseline task.

## 3. Test suite result at baseline (`pytest test_app.py -v`)

```
8 passed, 1 failed
```

The one failure is **expected and already documented as a known gap** in the
implementation plan (Section 2, "Main gaps and risks": *"Existing tests
assume Tesseract is installed at a particular local path"*):

```
FAILED test_app.py::TestLegalMetrologyChecker::test_tesseract_ocr_path_and_execution
AssertionError: 'Local Tesseract OCR' not found in "OCR Error: C:\Program Files\Tesseract-OCR\tesseract.exe is not installed or it's not in your PATH..."
```

Root cause: `perform_ocr_on_image()` re-hardcodes
`pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`
before actually running OCR, even though `check_tesseract_available()` itself
has a broader PATH-based fallback that does find the Linux binary. This
confirms the gap description precisely and is left **unmodified** in this
baseline. It will be fixed under **Task 0.3 — Make the clean environment
reproducible**, not here, so the tag stays a true, untouched snapshot of the
current prototype.

## 4. Supported/assumed versions going forward

Recorded now as a reference point for later compatibility decisions (not
enforced yet):

- **Python:** 3.9+ per README; verified working on 3.12.3.
- **OS:** Originally developed against Windows (hardcoded Tesseract path);
  verified also runs on Linux once Tesseract path assumptions are worked
  around. macOS is mentioned in the README's Tesseract install instructions
  (Homebrew) but not otherwise verified here.
- **Tesseract:** README documents Windows/macOS install steps; no version
  floor specified. This baseline verified against 5.3.4.
- **Browsers:** Not specified by the project. To be formalized later.

## 5. "Existing Prototype Baseline" milestone/issue content

GitHub write access was not available in this session, so the
issue/milestone described by Task 0.1 could not be created directly on
GitHub. The text below is ready to paste into a new GitHub issue (and/or
milestone) named **`Existing Prototype Baseline`**:

> **Title:** Existing Prototype Baseline
>
> **Body:**
> This issue tracks the frozen, verified state of the prototype before any
> refactor work begins.
>
> - Tag: `v0.1-prototype` at commit `fd5cd91aa35470d7777c37982689230f196b233c`
> - Verified: fresh clone, app boot, dependency install, and existing test
>   suite (8/9 passing; the 1 known failure is the hardcoded Windows
>   Tesseract path, tracked separately under Task 0.3).
> - Full details: `docs/baseline/BASELINE_RECORD.md`
> - Purpose: gives every later task a stable, reproducible point to diff
>   against and to roll back to if a refactor regresses behaviour.
>
> Closes when Task 0.1's Definition of Done is satisfied (this record + tag).

---

**Done when (per plan):** another team member can reproduce the original
prototype without using the developer's machine state. Satisfied by: the
`v0.1-prototype` tag (pristine, no docs added to it) plus this record
explaining exactly how it was verified and on what environment.
