# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "hr_contract_salary_advantage", "active", "boolean", default=True)
    util.create_column(cr, "hr_contract_salary_advantage", "activity_type_id", "int4")
    util.create_column(cr, "hr_contract_salary_advantage", "activity_creation", "varchar", default="countersigned")
    util.create_column(cr, "hr_contract_salary_advantage", "activity_creation_type", "varchar", default="always")
    util.create_column(cr, "hr_contract_salary_advantage", "activity_responsible_id", "int4")

    util.create_column(cr, "generate_simulation_link", "contract_start_date", "date")

    util.create_column(cr, 'hr_contract_salary_resume', 'active', 'boolean', default=True)
