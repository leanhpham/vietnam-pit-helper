# -*- coding: utf-8 -*-
"""Odoo model: one monthly payroll line per employee.

Computation lives in ``pit_tax`` (pure Python, no Odoo dependency);
this model only maps its results onto Odoo fields so the same numbers
can be unit-tested without an Odoo instance.
"""

from odoo import api, fields, models

from . import pit_tax


class PitPayrollLine(models.Model):
    _name = "pit.payroll.line"
    _description = "Vietnam PIT Payroll Line"
    _order = "year desc, month desc, employee_id"

    _sql_constraints = [
        (
            "unique_employee_period",
            "UNIQUE(employee_id, year, month)",
            "A payroll line already exists for this employee and period.",
        ),
    ]

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------
    name = fields.Char(
        string="Reference",
        compute="_compute_name",
        store=True,
        readonly=True,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
        index=True,
    )
    year = fields.Integer(
        string="Year",
        required=True,
        default=lambda self: fields.Date.today().year,
    )
    month = fields.Selection(
        [
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        string="Month",
        required=True,
        default=lambda self: str(fields.Date.today().month),
    )
    period = fields.Char(
        string="Period",
        compute="_compute_period",
        store=True,
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
        ],
        string="Status",
        default="draft",
        required=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Inputs
    # ------------------------------------------------------------------
    gross_salary = fields.Monetary(
        string="Gross Salary",
        currency_field="currency_id",
        required=True,
        default=0.0,
        help="Contractual gross salary for the month. Insurance is "
        "computed on this amount (capped by law).",
    )
    bonus = fields.Monetary(
        string="Bonus",
        currency_field="currency_id",
        default=0.0,
        help="Bonus paid in the month. Taxable, but not part of the "
        "insurance base.",
    )
    dependents = fields.Integer(
        string="Dependents",
        default=0,
        help="Number of registered dependents. Each dependent reduces "
        "taxable income by 6,200,000 VND/month (2026 law).",
    )

    # ------------------------------------------------------------------
    # Computed results (all stored, recomputed on input change)
    # ------------------------------------------------------------------
    bhxh = fields.Monetary(
        string="BHXH (8%)", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    bhyt = fields.Monetary(
        string="BHYT (1.5%)", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    bhtn = fields.Monetary(
        string="BHTN (1%)", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    total_insurance = fields.Monetary(
        string="Total Insurance",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
    )
    total_income = fields.Monetary(
        string="Total Income (Gross + Bonus)",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
    )
    family_deduction = fields.Monetary(
        string="Family Deduction",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        help="Personal deduction 15,500,000 VND/month plus 6,200,000 "
        "VND/month per dependent (2026 law).",
    )
    taxable_income = fields.Monetary(
        string="Taxable Income",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
    )
    pit = fields.Monetary(
        string="PIT",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        help="Personal income tax, progressive monthly table (2026 law).",
    )
    net_salary = fields.Monetary(
        string="Net Salary",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
    )

    # ------------------------------------------------------------------
    # Computes
    # ------------------------------------------------------------------
    @api.depends("employee_id", "year", "month")
    def _compute_name(self):
        for line in self:
            employee = line.employee_id.name or "?"
            line.name = "PIT %s/%s - %s" % (
                line.month or "?",
                line.year or "?",
                employee,
            )

    @api.depends("year", "month")
    def _compute_period(self):
        for line in self:
            if line.year and line.month:
                line.period = "%02d/%s" % (int(line.month), line.year)
            else:
                line.period = False

    @api.depends("gross_salary", "bonus", "dependents")
    def _compute_amounts(self):
        for line in self:
            result = pit_tax.compute_payroll(
                line.gross_salary, line.bonus, line.dependents
            )
            line.bhxh = result["bhxh"]
            line.bhyt = result["bhyt"]
            line.bhtn = result["bhtn"]
            line.total_insurance = result["total_insurance"]
            line.total_income = result["total_income"]
            line.family_deduction = result["family_deduction"]
            line.taxable_income = result["taxable_income"]
            line.pit = result["pit"]
            line.net_salary = result["net_salary"]

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------
    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_done(self):
        self.write({"state": "done"})

    def action_draft(self):
        self.write({"state": "draft"})
