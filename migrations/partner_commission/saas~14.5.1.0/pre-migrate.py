# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "commission_plan", "company_id", "integer")
    util.create_column(cr, "commission_plan", "active", "boolean", default=True)
    util.create_column(cr, "res_company", "commission_po_minimum", "numeric", default=0.0)
    util.remove_column(cr, "res_config_settings", "commission_automatic_po_frequency")
