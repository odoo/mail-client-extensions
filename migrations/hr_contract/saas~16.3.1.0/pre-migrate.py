# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.employee.public", "first_contract_date")

    util.remove_view(cr, "hr_contract.hr_employee_public_view_form")
