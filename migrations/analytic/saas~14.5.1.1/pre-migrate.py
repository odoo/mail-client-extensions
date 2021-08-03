# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_analytic_line", "category", "varchar", default="other")
    util.move_field_to_module(cr, "res.config.settings", "group_analytic_accounting", "account", "analytic")
