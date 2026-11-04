# Vietnam PIT Helper — Odoo 20 Community

Monthly payroll and Vietnamese personal income tax (PIT) for one
employee per month, computed under the law in force for **tax year
2026** (Law 109/2025/QH15).

## What it does

For each employee and month, enter gross salary, bonus and number of
dependents. The module automatically computes:

| Step | Rule (2026 law) |
|---|---|
| Insurance (employee) | BHXH 8%, BHYT 1.5%, BHTN 1% of gross salary, capped: BHXH/BHYT base max 50,600,000 VND/month (20 × base salary 2,530,000), BHTN base max 106,200,000 VND/month (20 × Region I minimum wage 5,310,000) |
| Family deduction | 15,500,000 VND/month (personal) + 6,200,000 VND/month per dependent |
| Taxable income | Gross + bonus − insurance − family deduction (floored at 0) |
| PIT | Progressive monthly table, 5 brackets: ≤10M 5%, 10–30M 10%, 30–60M 20%, 60–100M 30%, >100M 35% |
| Net salary | Gross + bonus − insurance − PIT |

Features:

- **Payroll lines** — one line per employee per month (unique
  constraint), with Draft → Confirmed → Done workflow.
- **List + form views** — filters by month/employee/status, group by
  period/employee; totals in the list footer.
- **QWeb report** — monthly payroll + PIT table per employee,
  printable / exportable to PDF from the list or form.
- **Access control** — salary figures are visible only to HR
  (`hr.group_hr_user` / `hr.group_hr_manager`) and Accounting
  (`account.group_account_user` read-only /
  `account.group_account_manager`). Other users cannot see the model
  at all.
- **No Enterprise dependency** — Odoo 20 Community only; depends on
  the standard `hr` and `account` apps.

## Law change note (important)

The original spec for this module quoted the pre-2026 law: a
7-bracket table (5% to 5M … 35% above 80M) with deductions of
11,000,000 / 4,400,000 VND. That law was superseded for tax year
2026 by **Law 109/2025/QH15** (5 brackets, deductions 15,500,000 /
6,200,000) and by **Decree 161/2026/NĐ-CP** (base salary 2,530,000
from 01/07/2026, so the BHXH/BHYT cap rose from 46,800,000 to
50,600,000). This module implements the **current (2026) law**; the
old figures are kept only as comments in `models/pit_tax.py`. See
`TEST-RESULTS.md` for the verification sources.

## Install

1. Copy the `vietnam_pit_helper` folder into your Odoo addons path.
2. In Odoo: Apps → Update Apps List → search "Vietnam PIT Helper" →
   Install. (Requires the Employees and Accounting apps.)
3. Menu: **Employees → Payroll & PIT**.

## Use

1. Open **Employees → Payroll & PIT** → Create.
2. Pick the employee, month and year; enter gross salary, bonus and
   number of dependents. Insurance, taxable income, PIT and net
   salary compute automatically.
3. **Confirm** when the figures are checked, **Mark as Done** after
   payment. Use **Print → Payroll & PIT Report** to export the PDF.

## Assumptions (v1, documented)

- Insurance is computed on the **gross salary only**. Bonus is
  taxable but is not part of the insurance base (the common case
  where the bonus is not contractual salary for insurance).
- BHTN cap uses the **Region I** minimum wage (5,310,000 VND/month).
  Companies in other regions should adjust `BHTN_CAP` in
  `models/pit_tax.py`.
- Amounts are rounded to whole VND, half-up.
- Out of scope for v1: year-end settlement, eTax filing, electronic
  declaration.

## Price

**$19.00 (USD), one-time, per database** (set in the manifest).
Odoo Apps Store takes ~20% commission. Support:
leanhpham2611@gmail.com — bug fixes within the first 30 days after
purchase.

## Files

- `__manifest__.py` — metadata, price, dependencies.
- `models/pit_tax.py` — pure-Python computation (no Odoo import), the
  single source of truth for all tax/insurance figures.
- `models/pit_payroll.py` — Odoo model `pit.payroll.line`.
- `views/pit_payroll_views.xml` — list, form, search views, action,
  menu.
- `reports/pit_payroll_report.xml` — QWeb payroll + PIT report (PDF).
- `security/ir.model.access.csv` — HR / Accounting access rules.
- `tests/test_pit_compute.py` — standalone test (plain `python3`,
  no Odoo needed); see `TEST-RESULTS.md`.

## Differences vs Odoo 17

This is the **Odoo 20** build of the same module. The tax logic
(`models/pit_tax.py`) is byte-identical to the Odoo 17 version;
only the framework-facing parts changed:

- **List view renamed**: `<tree>` → `<list>`, and the action's
  `view_mode` `tree,form` → `list,form` (same as the Odoo 18/19
  builds). Source: Odoo's migrator script
  `odoo/upgrade_code/17.5-01-tree-to-list.py`.
- **SQL constraint rewritten**: `_sql_constraints` →
  `_unique_employee_period = models.Constraint(...)` (same as the
  Odoo 19 build — the old attribute is ignored in 20 too).
  Source: `odoo/orm/model_classes.py`, migrator script
  `odoo/upgrade_code/18.1-00-sql-constraint.py`.
- **`report_file` removed from `ir.actions.report`**: Odoo 20
  dropped the `report_file` field (`odoo/addons/base/models/
  ir_actions_report.py` has no such field; it still exists in
  18/19). The field was a redundant duplicate of `report_name`
  in this module, so the line was simply deleted — the report
  action keeps `report_name` + `print_report_name`.
- **Search view Group By simplified**: the `<group expand="0"
  string="Group By">` wrapper is now a bare `<group>` (same as
  the Odoo 19 build — Odoo 20 also dropped the `expand` and
  `string` attributes from the `group` element).
- **Access rights moved to the new model**: `security/ir.model.access.csv`
  is replaced by `security/ir.access.csv`. Odoo 20 removed the
  `ir.model.access` model (and merged record rules into it); access
  is now `ir.access` records with a single `operation` column
  holding a subset of `crud` (`crud` = all, `cru` = no delete,
  `r` = read-only). The four rows carry the exact same rights as
  the Odoo 17 CSV. Source: migrator script
  `odoo/upgrade_code/19.4-00-ir-access.py` and
  `odoo/addons/base/models/ir_access.py`.
- **Manifest version**: `20.0.1.0.0`. Price stays $19.00 USD.
- **Python / database**: Odoo 20 requires Python ≥ 3.12
  (`MIN_PY_VERSION = (3, 12)` in `odoo/release.py`) and
  PostgreSQL 16+.

Everything else — QWeb report, `hr`/`account` dependencies,
group ids (`hr.group_hr_user`, `account.group_account_manager`,
…) — is unchanged from the Odoo 17 version and was verified
against the Odoo 20.0 source.

## License

Vietnam PIT Helper is licensed under the Odoo Proprietary License v1.0 (OPL-1).
See the LICENSE file. Copyright (C) 2026 LeePham.
