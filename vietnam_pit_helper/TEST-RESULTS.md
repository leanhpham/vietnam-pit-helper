# Vietnam PIT Helper v1 — Test Results

Date: 2026-11-03. Environment: Python 3.12.3, Linux. No Odoo
installed in this environment (see "Odoo install" below).

## ⚠️ Law change found during verification (figures updated)

The spec quoted the pre-2026 law (7-bracket table, deductions
11,000,000 / 4,400,000 VND, BHXH/BHYT cap 46,800,000). Web
verification on 2026-11-03 showed the law has changed for **tax
year 2026**, so the module implements the **current law** instead:

| Item | Spec (pre-2026) | Current law used in v1 | Source |
|---|---|---|---|
| Personal deduction | 11,000,000 VND/mo | **15,500,000 VND/mo** | Resolution 110/2025/UBTVQH15 |
| Dependent deduction | 4,400,000 VND/mo | **6,200,000 VND/mo** | Resolution 110/2025/UBTVQH15 |
| PIT table | 7 brackets (5/10/15/20/25/30/35%, top above 80M) | **5 brackets: 5% ≤10M, 10% 10–30M, 20% 30–60M, 30% 60–100M, 35% >100M** | Law 109/2025/QH15, Art. 9 (from tax year 2026) |
| BHXH/BHYT cap | 46,800,000 (base salary 2,340,000) | **50,600,000** (base salary 2,530,000 from 01/07/2026) | Decree 161/2026/NĐ-CP |
| BHTN cap | 20 × Region I min. wage | **106,200,000** (Region I 5,310,000, Decree 293/2025) | vi.money / ketoanleanh.edu.vn |
| Insurance rates | BHXH 8%, BHYT 1.5%, BHTN 1% | **unchanged** | confirmed by the same sources |

The old 7-bracket figures are kept only as a comment in
`models/pit_tax.py` for reference.

## Verification checks

| Check | Result |
|---|---|
| `python3 -m compileall` on all Python files | ✅ PASS (no errors) |
| XML well-formedness (`xml.etree.ElementTree`) on all XML files (views + report) | ✅ PASS (2 files) |
| Manifest parses as a Python dict; name "Vietnam PIT Helper", version 17.0.1.0.0, price 69.00 EUR, license OPL-1, depends `hr` + `account` | ✅ PASS |
| Standalone computation test `python3 tests/test_pit_compute.py` (31 assertions, exit code 0) | ✅ PASS — see table below |
| Real install on a clean Odoo 17 database | ❌ NOT DONE — Odoo is **not installed** in this environment (`which odoo` empty, no `odoo` pip package). Odoo was **not** installed on purpose (no system changes per instructions). |

## Hand-check table — 3 sample employees

All amounts in VND. Every figure below was computed by hand from
the 2026 law and asserted against the module's output.

| | A — low | B — mid | C — high |
|---|---|---|---|
| Gross salary | 15,000,000 | 30,000,000 | 120,000,000 |
| Bonus | 0 | 5,000,000 | 10,000,000 |
| Dependents | 0 | 2 | 1 |
| BHXH (8%) | 1,200,000 | 2,400,000 | 4,048,000 (cap 50.6M) |
| BHYT (1.5%) | 225,000 | 450,000 | 759,000 (cap 50.6M) |
| BHTN (1%) | 150,000 | 300,000 | 1,062,000 (cap 106.2M) |
| Total insurance | 1,575,000 | 3,150,000 | 5,869,000 |
| Total income | 15,000,000 | 35,000,000 | 130,000,000 |
| Family deduction | 15,500,000 | 27,900,000 | 21,700,000 |
| Taxable income | 0 (negative → 0) | 3,950,000 | 102,431,000 |
| PIT | 0 | 197,500 (5% × 3,950,000) | 21,350,850 (all 5 brackets) |
| **Net salary** | **13,425,000** | **31,652,500** | **102,780,150** |

Employee C bracket detail (PIT 21,350,850):
10M×5% = 500,000; 20M×10% = 2,000,000; 30M×20% = 6,000,000;
40M×30% = 12,000,000; 2,431,000×35% = 850,850. Cross-checked with
the quick formula 35% × 102,431,000 − 14,500,000 = 21,350,850. ✅

Bracket-boundary checks also pass: taxable 10M → PIT 500,000;
30M → 2,500,000; 60M → 8,500,000; 100M → 20,500,000; 0 → 0.

Full test output: run `python3 tests/test_pit_compute.py` (exit 0,
"ALL CHECKS PASSED", 31 assertions).

## Still needs a real Odoo 17 instance to confirm

1. **Install on a clean Odoo 17 database** (with Employees +
   Accounting installed) — confirm no load errors in manifest,
   views, access rules, menu (`hr.menu_hr_root`) and report action.
2. **Create the 3 sample employees in Odoo** and check the computed
   fields on the form match the hand-check table above.
3. **Print the QWeb report to PDF** and visually check the layout
   (the report template was reviewed statically, not rendered).
4. **Access check**: log in as a plain internal user and confirm the
   payroll menu/model is not visible; log in as HR / Accounting and
   confirm the expected read/write rights.
5. **Screenshots** for the Apps Store listing (form, list, PDF
   report) — cannot be produced without an Odoo instance.
6. Apps Store submission itself (not done, per instructions).

---

## Live Odoo 17 test — 2026-11-03

Route: **direct install** (Docker route failed — see
`../test-env/SETUP-LOG.md`). Real Odoo 17.0 (source tarball from
github.com/odoo/odoo, branch 17.0) on Python 3.11.18, PostgreSQL 16
cluster `main` on 127.0.0.1:5432, wkhtmltopdf 0.12.6. Database
`pit_test`. Full setup in `../test-env/SETUP-LOG.md`.

### Install result

- `odoo-bin -d pit_test -i base,hr,account,vietnam_pit_helper
  --without-demo=all --stop-after-init` → **exit 0, clean install**.
  `ir_module_module` states: `account`, `hr`, `vietnam_pit_helper`
  all `installed`. Module loaded in 0.28 s (145 queries); access CSV,
  list/form/search views, menu, QWeb report all loaded.
- One benign line in the log: docutils `(ERROR/3) Unexpected
  indentation` while rendering a stock Odoo module description —
  not from this module, no effect.
- **First install attempt FAILED** (verbatim):
  `ValueError: Wrong value for ir.ui.view.type: 'list'` —
  `ParseError ... views/pit_payroll_views.xml:4`. Cause: the views
  used Odoo 18 conventions (`<list>`, `view_mode="list,form"`);
  Odoo 17 requires `<tree>` / `view_mode="tree,form"`. **Fixed in the
  module** (`<list>` → `<tree>`, `list,form` → `tree,form`) and the
  clean reinstall above succeeded. Without this fix the module could
  not be installed on Odoo 17 at all.
- Company currency set to VND for the test (VND is inactive by
  default in a fresh `--without-demo=all` DB; activated it first).

### 3-employee comparison (live Odoo vs hand-check table)

Created in Odoo via `odoo shell` (script
`../test-env/test-scripts/test_pit_live.py`, full output
`../test-env/test-output.log`): employees "Nguyen Van A (low)",
"Tran Thi B (mid)", "Le Van C (high)", one payroll line each for
2026-11. **Every figure matches exactly** (`FIGURE CHECK: ALL
MATCH`):

| | A — low | B — mid | C — high |
|---|---|---|---|
| Gross / bonus / dependents | 15,000,000 / 0 / 0 | 30,000,000 / 5,000,000 / 2 | 120,000,000 / 10,000,000 / 1 |
| BHXH / BHYT / BHTN | 1,200,000 / 225,000 / 150,000 | 2,400,000 / 450,000 / 300,000 | 4,048,000 / 759,000 / 1,062,000 |
| Total insurance | 1,575,000 | 3,150,000 | 5,869,000 |
| Total income | 15,000,000 | 35,000,000 | 130,000,000 |
| Family deduction | 15,500,000 | 27,900,000 | 21,700,000 |
| Taxable income | 0 | 3,950,000 | 102,431,000 |
| PIT | 0 | 197,500 | 21,350,850 |
| **Net salary** | **13,425,000** | **31,652,500** | **102,780,150** |

Workflow also verified on line A: Draft → Confirm → Done works.

### QWeb report (PDF)

Rendered for employee C via `ir.actions.report._render_qweb_pdf`
(`vietnam_pit_helper.report_pit_payroll`): **20,113 bytes, 1 page,
valid `%PDF-1.4`**. Text verified with `pdftotext` — all figures
above appear correctly, plus the 2026-law footnote.
Saved at: `../test-env/output/pit_report_C.pdf`.

### Access check (via `odoo shell`, `with_user(...)`)

- Plain internal user (only `base.group_user`): search →
  `AccessError`, create → `AccessError`. ✅ cannot see salaries.
- HR user (`hr.group_hr_user`): search OK, create OK. ✅
- Accounting user (`account.group_account_user`): search OK,
  create → `AccessError` (read-only). ✅
Result: **ACCESS CHECK: ALL AS EXPECTED** (matches
`security/ir.model.access.csv`).

### Still unverified

1. Visual check of the web UI (form/list/report screens) — no
   browser was available to this test run; the web UI responds
   (HTTP 200 at `http://127.0.0.1:8069/web/login`) but no
   screenshots were taken. The Apps Store listing still needs
   screenshots (form, list, PDF report).
2. Apps Store submission itself (not done, per instructions).
3. Behaviour with demo data / a company currency other than VND
   was not tested (currency defaults to company currency, as
   designed).

---

## Rebuilt after VM replacement — 2026-11-03 (second live test)

The VM was replaced mid-task: all system packages (PostgreSQL, Docker,
wkhtmltopdf, Playwright system libs, apt-sources fix) were gone; everything
under `~/workspace` survived (venv, Odoo 17.0 source, tarballs, scripts,
earlier screenshots + PDF).

### Rebuild steps
- Re-applied apt fix (`archive.ubuntu.com` + `Acquire::Languages "none"`),
  `apt-get update` (26.6 MB in 23 s), reinstalled `postgresql-16` and
  `wkhtmltopdf`; re-ran `playwright install-deps chromium` (Chromium binary
  survived in `~/.cache/ms-playwright`, so no browser re-download).
- PostgreSQL 16 cluster `main` recreated via the Debian package, started
  with `pg_ctlcluster 16 main start`; role `odoo` (superuser, password
  `odoo`) recreated. The `pgdata/` dir in test-env was NOT used (only a
  stray `postgresql.conf` from the abandoned first attempt).
- Clean install: `odoo-bin -d pit_test -i base,hr,account,vietnam_pit_helper
  --without-demo=all --stop-after-init` → **exit 0, no errors**. All four
  modules state `installed`. Log: `test-env/odoo-install-rebuild.log`.
  Module now includes the `currency_id` view fix (added after the first
  screenshots); no tax-logic changes.
- Fixtures recreated with `test-scripts/create_fixtures.py` (explicit
  `env.cr.commit()`).

### Fixture persistence check
Fresh `psql` session after the shell run: `SELECT count(*) FROM
pit_payroll_line` → **3 rows** (ids 1–3; employees A=2, B=3, C=4).
Action id for the list view is 317 (same as before); `screenshot_pit.py`
`LINE_C_ID` updated 8 → 3 (new id of Le Van C's line). Server started in
background, login page HTTP 200 at `http://127.0.0.1:8069`.

### Figure match (fresh psql read-back)
| | A — low | B — mid | C — high |
|---|---|---|---|
| Total insurance | 1,575,000 | 3,150,000 | 5,869,000 |
| Taxable income | 0 | 3,950,000 | 102,431,000 |
| PIT | 0 | 197,500 | 21,350,850 |
| **Net salary** | **13,425,000** | **31,652,500** | **102,780,150** |
**ALL MATCH** the hand-check table. Full log: `test-env/test-output-rebuild.log`.

### Footer totals + ₫ symbol verification (new screenshots inspected)
- `output/screenshot-list.png`: every monetary amount shows the **₫**
  symbol; footer shows summed totals — Gross 165,000,000 ₫, Bonus
  15,000,000 ₫, Total Insurance 10,594,000 ₫, Taxable 106,381,000 ₫,
  PIT 21,548,350 ₫, Net 147,857,650 ₫ (all cross-checked by hand).
  ✅ No "—" anywhere.
- `output/screenshot-form-c.png`: all amounts show **₫** (Gross
  120,000,000 ₫, PIT 21,350,850 ₫, Net 102,780,150 ₫, …). ✅
- `output/screenshot-report-c.png`: QWeb HTML render, all figures with ₫
  + 2026-law footnote. ✅
- One cosmetic note: the **Family Deduction** column footer is blank
  (not "—", just empty) because that field has no `sum=` attribute in the
  list view (`views/pit_payroll_views.xml:15` — all other monetary fields
  declare `sum="..."`). One-line view fix if a total is wanted there;
  not a rendering failure, left as-is.
