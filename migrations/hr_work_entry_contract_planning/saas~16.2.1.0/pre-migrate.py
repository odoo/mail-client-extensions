# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_work_entry_contract_planning.hr_employee_view_form_inherit")
