# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, 'report.mrp_cost_structure', 'report.mrp_account.mrp_cost_structure',
                      rename_table=False)
