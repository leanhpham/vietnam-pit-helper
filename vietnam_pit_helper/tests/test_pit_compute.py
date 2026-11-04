#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Standalone test for the Vietnam PIT computation (no Odoo needed).

Run from anywhere with plain Python 3:

    python3 tests/test_pit_compute.py

It imports the exact same ``pit_tax`` module that the Odoo model
(``models/pit_payroll.py``) uses, runs 3 sample employees (low / mid /
high salary, different dependent counts) and asserts every figure
against hand-computed bracket math.  Exit code 0 = all checks pass.

Law applied: tax year 2026 (Law 109/2025/QH15) — personal deduction
15,500,000 VND/month, dependent 6,200,000 VND/month, 5-bracket
monthly table 5% / 10% / 20% / 30% / 35%; insurance BHXH 8%,
BHYT 1.5%, BHTN 1% with caps 50,600,000 (BHXH/BHYT) and
106,200,000 (BHTN).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "models"))

import pit_tax  # noqa: E402


def check(label, got, expected):
    """Assert one figure and print the comparison."""
    status = "OK  " if got == expected else "FAIL"
    print(f"  [{status}] {label:<28} got {got:>15,}  expected {expected:,}")
    assert got == expected, "%s: got %s, expected %s" % (label, got, expected)


def main():
    print("Vietnam PIT Helper — standalone computation test")
    print("Law: tax year 2026 (Law 109/2025/QH15)")
    print("=" * 72)

    # ------------------------------------------------------------------
    # Employee A — low salary, no dependents, no bonus.
    # Hand check:
    #   Insurance: 15,000,000 x 10.5% = 1,575,000
    #     (BHXH 1,200,000 + BHYT 225,000 + BHTN 150,000)
    #   Taxable: 15,000,000 - 1,575,000 - 15,500,000 = -2,075,000 -> 0
    #   PIT: 0.  Net: 15,000,000 - 1,575,000 = 13,425,000
    # ------------------------------------------------------------------
    print("\nEmployee A — low: gross 15,000,000, bonus 0, dependents 0")
    a = pit_tax.compute_payroll(15_000_000, 0, 0)
    check("BHXH", a["bhxh"], 1_200_000)
    check("BHYT", a["bhyt"], 225_000)
    check("BHTN", a["bhtn"], 150_000)
    check("total insurance", a["total_insurance"], 1_575_000)
    check("family deduction", a["family_deduction"], 15_500_000)
    check("taxable income", a["taxable_income"], 0)
    check("PIT", a["pit"], 0)
    check("net salary", a["net_salary"], 13_425_000)

    # ------------------------------------------------------------------
    # Employee B — mid salary, bonus, 2 dependents.
    # Hand check:
    #   Insurance: 30,000,000 x 10.5% = 3,150,000
    #     (BHXH 2,400,000 + BHYT 450,000 + BHTN 300,000)
    #   Total income: 30,000,000 + 5,000,000 = 35,000,000
    #   Deduction: 15,500,000 + 2 x 6,200,000 = 27,900,000
    #   Taxable: 35,000,000 - 3,150,000 - 27,900,000 = 3,950,000
    #   PIT (bracket 1 only): 3,950,000 x 5% = 197,500
    #   Net: 35,000,000 - 3,150,000 - 197,500 = 31,652,500
    # ------------------------------------------------------------------
    print("\nEmployee B — mid: gross 30,000,000, bonus 5,000,000, dependents 2")
    b = pit_tax.compute_payroll(30_000_000, 5_000_000, 2)
    check("BHXH", b["bhxh"], 2_400_000)
    check("BHYT", b["bhyt"], 450_000)
    check("BHTN", b["bhtn"], 300_000)
    check("total insurance", b["total_insurance"], 3_150_000)
    check("total income", b["total_income"], 35_000_000)
    check("family deduction", b["family_deduction"], 27_900_000)
    check("taxable income", b["taxable_income"], 3_950_000)
    check("PIT", b["pit"], 197_500)
    check("net salary", b["net_salary"], 31_652_500)

    # ------------------------------------------------------------------
    # Employee C — high salary, bonus, 1 dependent (exercises both
    # insurance caps and all 5 tax brackets).
    # Hand check:
    #   Insurance base BHXH/BHYT capped at 50,600,000:
    #     BHXH 50,600,000 x 8%   = 4,048,000
    #     BHYT 50,600,000 x 1.5% =   759,000
    #   Insurance base BHTN capped at 106,200,000:
    #     BHTN 106,200,000 x 1%  = 1,062,000
    #   Total insurance = 5,869,000
    #   Total income: 120,000,000 + 10,000,000 = 130,000,000
    #   Deduction: 15,500,000 + 6,200,000 = 21,700,000
    #   Taxable: 130,000,000 - 5,869,000 - 21,700,000 = 102,431,000
    #   PIT, bracket by bracket:
    #     10,000,000 x 5%  =    500,000
    #     20,000,000 x 10% =  2,000,000
    #     30,000,000 x 20% =  6,000,000
    #     40,000,000 x 30% = 12,000,000
    #      2,431,000 x 35% =    850,850
    #     Total = 21,350,850
    #   Cross-check (quick formula): 35% x 102,431,000 - 14,500,000
    #     = 35,850,850 - 14,500,000 = 21,350,850  ✓
    #   Net: 130,000,000 - 5,869,000 - 21,350,850 = 102,780,150
    # ------------------------------------------------------------------
    print("\nEmployee C — high: gross 120,000,000, bonus 10,000,000, dependents 1")
    c = pit_tax.compute_payroll(120_000_000, 10_000_000, 1)
    check("BHXH/BHYT base (cap)", c["bhxh_bhyt_base"], 50_600_000)
    check("BHTN base (cap)", c["bhtn_base"], 106_200_000)
    check("BHXH", c["bhxh"], 4_048_000)
    check("BHYT", c["bhyt"], 759_000)
    check("BHTN", c["bhtn"], 1_062_000)
    check("total insurance", c["total_insurance"], 5_869_000)
    check("total income", c["total_income"], 130_000_000)
    check("family deduction", c["family_deduction"], 21_700_000)
    check("taxable income", c["taxable_income"], 102_431_000)
    check("PIT", c["pit"], 21_350_850)
    check("net salary", c["net_salary"], 102_780_150)
    quick = round(0.35 * 102_431_000) - 14_500_000
    check("PIT quick-formula cross-check", quick, 21_350_850)

    # ------------------------------------------------------------------
    # Boundary checks on the bracket table itself.
    # ------------------------------------------------------------------
    print("\nBracket boundaries (compute_pit on taxable income directly)")
    check("taxable 0 -> PIT 0", pit_tax.compute_pit(0), 0)
    check("taxable 10,000,000 -> 500,000", pit_tax.compute_pit(10_000_000), 500_000)
    check("taxable 30,000,000 -> 2,500,000", pit_tax.compute_pit(30_000_000), 2_500_000)
    check("taxable 60,000,000 -> 8,500,000", pit_tax.compute_pit(60_000_000), 8_500_000)
    check("taxable 100,000,000 -> 20,500,000", pit_tax.compute_pit(100_000_000), 20_500_000)

    print("\n" + "=" * 72)
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
