# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    model = 'res.config.settings' if util.version_gte('10.saas~18') else 'sale.config.settings'
    util.env(cr)[model].create({'group_proforma_sales': True}).execute()
