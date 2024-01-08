# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "hr_payslip_line", "category_id")
    util.remove_column(cr, "hr_payslip_line", "partner_id")

    util.remove_column(cr, "hr_payroll_edit_payslip_line", "category_id")
