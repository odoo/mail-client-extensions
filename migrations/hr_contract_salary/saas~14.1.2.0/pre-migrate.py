# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "hr_contract_salary_advantage", "active", "boolean", default=True)
    util.create_column(cr, "generate_simulation_link", "contract_start_date", "date")
