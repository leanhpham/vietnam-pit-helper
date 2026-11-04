# -*- coding: utf-8 -*-
"""Pure-Python Vietnam personal income tax (PIT) / payroll computation.

This module has NO Odoo dependency on purpose: the Odoo model
(``pit_payroll.py``) imports it, and the standalone test
(``tests/test_pit_compute.py``) runs the exact same code with plain
``python3``.  Any change to the law is a change to the constants below.

Law basis (verified 2026-11-03, current law for tax year 2026)
-------------------------------------------------------------
* Personal income tax: Law 109/2025/QH15, effective 01/07/2026,
  applicable from tax year 2026.
* Family deduction: personal 15,500,000 VND/month; each dependent
  6,200,000 VND/month (Resolution 110/2025/UBTVQH15).
* Monthly progressive table (5 brackets, resident individuals):

      Taxable income / month      Rate
      Up to      10,000,000        5%
      Over 10M to 30,000,000      10%
      Over 30M to 60,000,000      20%
      Over 60M to 100,000,000     30%
      Over       100,000,000      35%

  Quick formulas (equivalent): 5% x TNTT; 10% x TNTT - 500,000;
  20% x TNTT - 3,500,000; 30% x TNTT - 9,500,000;
  35% x TNTT - 14,500,000 (TNTT = taxable income).

* Employee compulsory insurance (unchanged rates):
  BHXH 8%, BHYT 1.5%, BHTN 1% (total 10.5% of the insurance salary).
* Insurance caps: BHXH/BHYT salary is capped at 20 x the base salary.
  Base salary is 2,530,000 VND/month from 01/07/2026
  (Decree 161/2026/ND-CP), so the BHXH/BHYT cap is 50,600,000
  VND/month.  BHTN salary is capped at 20 x the regional minimum
  wage; Region I is 5,310,000 VND/month (Decree 293/2025), so the
  BHTN cap is 106,200,000 VND/month.

NOTE — superseded figures (kept here for reference only):
The pre-2026 law (PIT Law 2007 as amended; Resolution
954/2020/UBTVQH14) used a 7-bracket table (5% to 5M, 10% 5-10M,
15% 10-18M, 20% 18-32M, 25% 32-52M, 30% 52-80M, 35% above 80M)
with deductions of 11,000,000 (personal) and 4,400,000 (per
dependent), and a BHXH/BHYT cap of 46,800,000 (base salary
2,340,000).  Those figures apply to tax year 2025 and earlier
only; they are NOT used by this module.

Simplification (documented, v1): insurance is computed on the gross
salary only.  Bonuses are included in taxable income but not in the
insurance base, which matches the common case where the bonus is not
part of the contractual salary used for insurance.
"""

# ---------------------------------------------------------------------------
# Law constants — update these when the law changes.
# ---------------------------------------------------------------------------

#: Family deduction for the taxpayer themselves (VND/month).
PERSONAL_DEDUCTION = 15_500_000
#: Family deduction per registered dependent (VND/month).
DEPENDENT_DEDUCTION = 6_200_000

#: Employee BHXH (social insurance) rate.
BHXH_RATE = 0.08
#: Employee BHYT (health insurance) rate.
BHYT_RATE = 0.015
#: Employee BHTN (unemployment insurance) rate.
BHTN_RATE = 0.01

#: Base salary from 01/07/2026 (Decree 161/2026/ND-CP).
BASE_SALARY = 2_530_000
#: BHXH/BHYT salary cap = 20 x base salary.
BHXH_BHYT_CAP = 20 * BASE_SALARY  # 50,600,000 VND/month
#: Region I minimum wage (Decree 293/2025).
REGION_I_MIN_WAGE = 5_310_000
#: BHTN salary cap = 20 x Region I minimum wage.
BHTN_CAP = 20 * REGION_I_MIN_WAGE  # 106,200,000 VND/month

#: Monthly progressive PIT table (tax year 2026): list of
#: (upper bound of the bracket in VND, rate).  ``None`` = no upper bound.
TAX_BRACKETS = [
    (10_000_000, 0.05),
    (30_000_000, 0.10),
    (60_000_000, 0.20),
    (100_000_000, 0.30),
    (None, 0.35),
]


def round_vnd(amount):
    """Round a positive amount to whole VND (half up).

    Python's built-in ``round()`` uses banker's rounding, which is not
    what Vietnamese payroll expects, so amounts are rounded half-up.
    """
    return int(amount + 0.5)


def compute_insurance(gross_salary):
    """Employee compulsory insurance on a gross salary.

    Returns a dict with the insurance bases and each contribution.
    Amounts are rounded to whole VND.
    """
    bhxh_bhyt_base = min(gross_salary, BHXH_BHYT_CAP)
    bhtn_base = min(gross_salary, BHTN_CAP)
    bhxh = round_vnd(bhxh_bhyt_base * BHXH_RATE)
    bhyt = round_vnd(bhxh_bhyt_base * BHYT_RATE)
    bhtn = round_vnd(bhtn_base * BHTN_RATE)
    return {
        "bhxh_bhyt_base": bhxh_bhyt_base,
        "bhtn_base": bhtn_base,
        "bhxh": bhxh,
        "bhyt": bhyt,
        "bhtn": bhtn,
        "total": bhxh + bhyt + bhtn,
    }


def compute_pit(taxable_income):
    """Progressive monthly PIT on a taxable income (VND).

    Applies each bracket's rate only to the part of the income that
    falls inside that bracket.  Zero or negative taxable income
    yields zero tax.
    """
    if taxable_income <= 0:
        return 0
    tax = 0.0
    lower = 0
    for upper, rate in TAX_BRACKETS:
        if taxable_income <= lower:
            break
        slice_top = taxable_income if upper is None else min(taxable_income, upper)
        tax += (slice_top - lower) * rate
        lower = upper
    return round_vnd(tax)


def compute_payroll(gross_salary, bonus=0.0, dependents=0):
    """Full monthly payroll computation for one employee.

    ``gross_salary``: contractual gross salary (VND).
    ``bonus``: bonus paid in the month (VND, taxable, not insured).
    ``dependents``: number of registered dependents.

    Returns a dict with every figure the Odoo model stores.
    """
    gross_salary = float(gross_salary or 0.0)
    bonus = float(bonus or 0.0)
    dependents = int(dependents or 0)
    if dependents < 0:
        dependents = 0

    insurance = compute_insurance(gross_salary)
    total_income = round_vnd(gross_salary + bonus)
    family_deduction = round_vnd(
        PERSONAL_DEDUCTION + dependents * DEPENDENT_DEDUCTION
    )
    taxable_income = max(
        0, round_vnd(total_income - insurance["total"] - family_deduction)
    )
    pit = compute_pit(taxable_income)
    net_salary = round_vnd(total_income - insurance["total"] - pit)

    return {
        "gross_salary": round_vnd(gross_salary),
        "bonus": round_vnd(bonus),
        "dependents": dependents,
        "bhxh_bhyt_base": insurance["bhxh_bhyt_base"],
        "bhtn_base": insurance["bhtn_base"],
        "bhxh": insurance["bhxh"],
        "bhyt": insurance["bhyt"],
        "bhtn": insurance["bhtn"],
        "total_insurance": insurance["total"],
        "total_income": total_income,
        "family_deduction": family_deduction,
        "taxable_income": taxable_income,
        "pit": pit,
        "net_salary": net_salary,
    }
