# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "uan", "varchar")
    util.create_column(cr, "hr_employee", "pan", "varchar")
    util.create_column(cr, "hr_employee", "esic_number", "varchar")

    util.force_noupdate(cr, "l10n_in_hr_payroll.hr_salary_rule_uniform_junior", True)
