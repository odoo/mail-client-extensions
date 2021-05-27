# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract_salary_advantage", "display_type", "varchar", default="line")
