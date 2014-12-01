# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'fleet.brand_lander rover', 'fleet.brand_land rover')
