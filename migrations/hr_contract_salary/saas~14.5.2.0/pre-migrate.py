# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract_salary_advantage_value", "display_type", "varchar", default="line")
    cr.execute("ALTER TABLE hr_contract_salary_advantage_value ALTER COLUMN value TYPE float8 USING value::float8")
    cr.execute("ALTER TABLE hr_contract_salary_resume ALTER COLUMN fixed_value TYPE float8 USING fixed_value::float8")
