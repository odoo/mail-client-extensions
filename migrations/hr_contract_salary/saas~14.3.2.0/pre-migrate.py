# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # Allow salary package info/values ordering
    util.create_column(cr, "hr_contract_salary_personal_info", "sequence", "int4")
    util.create_column(cr, "hr_contract_salary_personal_info_value", "sequence", "int4")
    util.create_column(cr, "hr_contract_salary_advantage_value", "sequence", "int4")

    # Doesn't change anything as
    # _order = 'sequence'  => ORDER BY sequence ASC, id ASC
    # But it's more "explicit"
    cr.execute("UPDATE hr_contract_salary_personal_info SET sequence=id")
    cr.execute("UPDATE hr_contract_salary_personal_info_value SET sequence=id")
    cr.execute("UPDATE hr_contract_salary_advantage_value SET sequence=id")
