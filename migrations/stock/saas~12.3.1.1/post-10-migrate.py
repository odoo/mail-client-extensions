# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    env["res.company"].create_missing_transit_location()
    env["res.company"].create_missing_warehouse()
    env["res.company"].create_missing_inventory_loss_location()
    env["res.company"].create_missing_production_location()
    env["res.company"].create_missing_scrap_location()
