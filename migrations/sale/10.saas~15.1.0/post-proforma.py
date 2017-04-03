# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.env(cr)['sale.config.settings'].create({'group_proforma_sales': True}).execute()
