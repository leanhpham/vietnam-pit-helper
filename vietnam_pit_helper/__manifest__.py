# -*- coding: utf-8 -*-
{
    "name": "Vietnam PIT Helper",
    "version": "20.0.1.0.0",
    "category": "Human Resources/Payroll",
    "summary": "Monthly payroll and personal income tax (PIT) for Vietnam, "
    "following the 2026 tax law (5-bracket progressive table).",
    "description": """
Vietnam PIT Helper — Monthly payroll & personal income tax for Vietnam
========================================================================

Compute monthly payroll and Vietnamese personal income tax (PIT) for
each employee, using the law in force for tax year 2026
(Law 109/2025/QH15):

* Gross salary + bonus, compulsory insurance (BHXH 8%, BHYT 1.5%,
  BHTN 1%) with the statutory caps (BHXH/BHYT capped at 20x the base
  salary = 50,600,000 VND/month; BHTN capped at 20x the Region I
  minimum wage = 106,200,000 VND/month).
* Family deduction: 15,500,000 VND/month for the taxpayer plus
  6,200,000 VND/month per registered dependent.
* PIT on the progressive monthly table (5 brackets: 5% / 10% / 20% /
  30% / 35%).
* Net salary, per-employee monthly payroll lines, and a printable
  monthly payroll + PIT report (PDF).

Features
---------
* One payroll line per employee per month (gross, bonus, dependents).
* Automatic computation of insurance, taxable income, PIT and net
  salary; amounts are stored and searchable.
* List and form views with filters by month and employee.
* QWeb report: monthly payroll and PIT table, exportable to PDF.
* Salary figures are visible only to HR and Accounting groups.

Compatibility
-------------
* Odoo 20 Community (no Enterprise dependency).
* Depends on the standard ``hr`` (Employees) and ``account``
  (Accounting) apps only.

Out of scope (v1)
-----------------
Year-end settlement, eTax filing and electronic declaration are NOT
included in this version.

Support
-------
Support email: leanhpham2611@gmail.com — bug fixes within the first
30 days after purchase.

Price: USD 19.00 (one-time, per database).

========================================================================
Vietnam PIT Helper — Bảng lương & thuế TNCN hàng tháng cho Việt Nam
========================================================================

Tính bảng lương và thuế thu nhập cá nhân (TNCN) hàng tháng cho từng
nhân viên theo luật hiện hành của kỳ tính thuế 2026
(Luật 109/2025/QH15):

* Lương gross + thưởng, bảo hiểm bắt buộc (BHXH 8%, BHYT 1,5%,
  BHTN 1%) theo trần luật định (BHXH/BHYT trần 20 lần lương cơ sở =
  50.600.000 đ/tháng; BHTN trần 20 lần lương tối thiểu vùng I =
  106.200.000 đ/tháng).
* Giảm trừ gia cảnh: 15.500.000 đ/tháng cho bản thân, 6.200.000
  đ/tháng cho mỗi người phụ thuộc.
* Thuế TNCN theo biểu lũy tiến từng phần 5 bậc hàng tháng:
  5% / 10% / 20% / 30% / 35%.
* Lương net, bảng lương theo từng nhân viên từng tháng, báo cáo
  bảng lương + thuế TNCN hàng tháng xuất được ra PDF.

Tương thích: Odoo 20 Community (không cần Enterprise).
Chưa có trong v1: quyết toán năm, khai báo điện tử, tích hợp eTax.
Hỗ trợ: leanhpham2611@gmail.com — sửa lỗi trong 30 ngày đầu.
Giá: 19,00 USD (một lần, cho một database).
""",
    "author": "LeePham",
    "website": "https://www.facebook.com/profile.php?id=61595231866235",
    "license": "OPL-1",
    "images": [
        "static/description/images/main_screenshot.png",
        "static/description/images/list_screenshot.png",
        "static/description/images/form_screenshot.png",
        "static/description/images/report_screenshot.png",
    ],
    "price": 19.00,
    "currency": "USD",
    "depends": ["hr", "account"],
    "data": [
        "security/ir.access.csv",
        "views/pit_payroll_views.xml",
        "reports/pit_payroll_report.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
