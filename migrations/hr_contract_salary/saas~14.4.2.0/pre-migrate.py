# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "hr_contract_salary_advantage", "sign_template_id", "int4")
    util.create_column(cr, "hr_contract_salary_advantage", "sign_copy_partner_id", "int4")
    util.create_column(cr, "hr_contract_salary_advantage", "sign_frenquency", "varchar", default="onchange")
