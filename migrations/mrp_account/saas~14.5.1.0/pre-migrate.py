# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mrp_production", "analytic_account_id", "int4")
    util.create_column(cr, "mrp_workorder", "mo_analytic_account_line_id", "int4")
    util.create_column(cr, "mrp_workorder", "wc_analytic_account_line_id", "int4")
