# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    env = util.env(cr)
    for company in env['res.company'].search([]):
        company._create_production_location()
        company._create_scrap_location()
        company._create_inventory_loss_location()
