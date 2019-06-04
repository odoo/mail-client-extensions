# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, "account_invoice", "extract_status_code", "int4")
    util.create_column(cr, "res_company", "extract_single_line_per_tax", "boolean")
    cr.execute("UPDATE res_company set extract_single_line_per_tax=TRUE")
